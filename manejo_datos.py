import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pkcs11 import lib as pkcs11_lib, ObjectClass, Attribute
from cryptography import x509

class manejo_datos:
    PKCS11_LIB = r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll"
    SLOT_INDEX = 0
    PBKDF2_ITERATIONS = 100_000
    PBKDF2_SALT_SIZE = 16
    AES_KEY_SIZE = 32
    

    def __init__(self, pin: str):
        self.pin = pin
        self.token = self._obtener_token()
        self.cert = self._obtener_certificado_autenticacion()
        self.nif = self._obtener_nif()
        self.archivo_clave = os.path.join(os.path.dirname(__file__), f"clave_enc_{self.nif}.bin")
        self.archivo_bd = os.path.join(os.path.dirname(__file__), f"Database_{self.nif}.json.enc")
        self.aes_key = None

    # ---------- DNIe ----------
    def verificar_dnie(self, pin):
        self.inicializar_clave()
        pkcs11 = pkcs11_lib(self.PKCS11_LIB)
        slots = pkcs11.get_slots(token_present=True)
        for slot in slots:
            token = slot.get_token()
        try:
            with token.open(user_pin=pin):
                return True
        except Exception:
            return False

    
    def _obtener_token(self):
        pkcs11 = pkcs11_lib(self.PKCS11_LIB)
        slots = pkcs11.get_slots(token_present=True)
        if not slots:
            raise RuntimeError("No se encontró token DNIe.")
        return slots[self.SLOT_INDEX].get_token()

    def _obtener_certificado_autenticacion(self):
        with self.token.open(rw=True) as session:
            certificados = list(session.get_objects({Attribute.CLASS: ObjectClass.CERTIFICATE}))
            if not certificados:
                raise RuntimeError("No se encontró certificado en el DNIe.")
            der = certificados[0][Attribute.VALUE]
            return x509.load_der_x509_certificate(der)

    def _obtener_nif(self):
        subject = self.cert.subject
        for attr in subject:
            if attr.oid.dotted_string == "2.5.4.5":  # SerialNumber OID
                return attr.value
        raise RuntimeError("No se encontró NIF en certificado.")

    # ---------- AES Key ----------
    def inicializar_clave(self):
        if os.path.exists(self.archivo_clave):
            return
        aes_key = os.urandom(self.AES_KEY_SIZE)
        salt = os.urandom(self.PBKDF2_SALT_SIZE)
        key_enc = self._cifrar_aes_key(aes_key, self.pin, salt)
        with open(self.archivo_clave, "wb") as f:
            f.write(salt + key_enc)

    def _cifrar_aes_key(self, aes_key, pin, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=self.AES_KEY_SIZE,
                         salt=salt,
                         iterations=self.PBKDF2_ITERATIONS)
        key_pin = kdf.derive(pin.encode())
        aesgcm = AESGCM(key_pin)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, aes_key, associated_data=None)
        return nonce + ct

    def _descifrar_aes_key(self):
        if self.aes_key is not None:
            return self.aes_key
        with open(self.archivo_clave, "rb") as f:
            contenido = f.read()
        salt = contenido[:self.PBKDF2_SALT_SIZE]
        nonce_ct = contenido[self.PBKDF2_SALT_SIZE:]
        nonce = nonce_ct[:12]
        ct = nonce_ct[12:]
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                         length=self.AES_KEY_SIZE,
                         salt=salt,
                         iterations=self.PBKDF2_ITERATIONS)
        key_pin = kdf.derive(self.pin.encode())
        aesgcm = AESGCM(key_pin)
        self.aes_key = aesgcm.decrypt(nonce, ct, associated_data=None)
        return self.aes_key

    # ---------- Base de datos ----------
    def cargar_bd(self):
        aes_key = self._descifrar_aes_key()
        if not os.path.exists(self.archivo_bd):
            return {"Contrasenas": []}
        with open(self.archivo_bd, "rb") as f:
            contenido = f.read()
        nonce = contenido[:12]
        ct = contenido[12:]
        aesgcm = AESGCM(aes_key)
        datos_bytes = aesgcm.decrypt(nonce, ct, associated_data=None)
        return json.loads(datos_bytes.decode("utf-8"))

    def guardar_bd(self, db):
        aes_key = self._descifrar_aes_key()
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, json.dumps(db, indent=4).encode("utf-8"), associated_data=None)
        with open(self.archivo_bd, "wb") as f:
            f.write(nonce + ct)

    # ---------- CRUD ----------
    def agregar_contraseña(self, nombre, contraseña):
        db = self.cargar_bd()
        if any(u["nombre"] == nombre for u in db["Contrasenas"]):
            return False
        db["Contrasenas"].append({"nombre": nombre, "contrasena": contraseña})
        self.guardar_bd(db)
        return True
    def editar_contraseña(self, nombre_actual, nueva_contraseña):

        db = self.cargar_bd()
    
        for u in db["Contrasenas"]:
            if u["nombre"] == nombre_actual:
                u["contrasena"] = nueva_contraseña
                self.guardar_bd(db)
                return True  # Modificación exitosa
        return False  # No se encontró la entrada

    def eliminar_contraseña(self, nombre):
        db = self.cargar_bd()
        original_len = len(db["Contrasenas"])
    
        # Filtrar todas las entradas que NO coincidan con el nombre
        db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
    
        if len(db["Contrasenas"]) < original_len:
            self.guardar_bd(db)
            return True  # Se eliminó al menos una entrada
        else:
            return False  # No se encontró la entrada

    def editar_nombre(self, nombre_actual, nuevo_nombre):
        db = self.cargar_bd()
        if any(u["nombre"] == nuevo_nombre for u in db["Contrasenas"]):
            return False
        for u in db["Contrasenas"]:
            if u["nombre"] == nombre_actual:
                u["nombre"] = nuevo_nombre
                self.guardar_bd(db)
                return True
        return False
