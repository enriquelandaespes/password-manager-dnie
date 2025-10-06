import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from pkcs11 import lib as pkcs11_lib, ObjectClass, Attribute, Mechanism

class manejo_datos:
    PKCS11_LIB = r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll"
    SLOT_INDEX = 0
    AES_KEY_SIZE = 32  # AES-256

    def __init__(self, pin: str):
        self.pin = pin
        self.token = self._obtener_token()
        self.cert = self._obtener_certificado_autenticacion()
        self.nif = self._obtener_nif()
        # Archivos diferenciados por NIF
        self.archivo_clave = os.path.join(os.path.dirname(__file__), f"clave_enc_{self.nif}.bin")
        self.archivo_bd = os.path.join(os.path.dirname(__file__), f"Database_{self.nif}.json.enc")
        self.aes_key = None

    # ---------- DNIe ----------
    def _obtener_token(self):
        pkcs11 = pkcs11_lib(self.PKCS11_LIB)
        slots = pkcs11.get_slots(token_present=True)
        if not slots:
            raise RuntimeError("No se encontró token DNIe.")
        return slots[self.SLOT_INDEX].get_token()

    def _obtener_certificado_autenticacion(self):
        # Abrir sesión de solo lectura para obtener certificado público
        with self.token.open(rw=False) as session:
            certificados = list(session.get_objects({Attribute.CLASS: ObjectClass.CERTIFICATE}))
            if not certificados:
                raise RuntimeError("No se encontró certificado en el DNIe.")
            der = certificados[0][Attribute.VALUE]
            return x509.load_der_x509_certificate(der)

    def _obtener_nif(self):
        # Se busca el NIF en el campo SerialNumber del certificado
        subject = self.cert.subject
        for attr in subject:
            if attr.oid.dotted_string == "2.5.4.5":  # SerialNumber OID
                return attr.value
        raise RuntimeError("No se encontró NIF en certificado.")

    # ---------- Inicialización de clave AES ----------
    def inicializar_clave(self):
        if os.path.exists(self.archivo_clave):
            return
        # Genera AES-256
        aes_key = os.urandom(self.AES_KEY_SIZE)
        pubkey = self.cert.public_key()
        # Cifrar AES con clave pública del DNIe
        aes_key_enc = pubkey.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        with open(self.archivo_clave, "wb") as f:
            f.write(aes_key_enc)
        print(f"Clave AES cifrada generada para NIF {self.nif}.")

    def _descifrar_aes_key(self):
        if self.aes_key is not None:
            return self.aes_key
        if not os.path.exists(self.archivo_clave):
            raise FileNotFoundError("No existe clave cifrada. Ejecuta inicializar_clave().")
        with open(self.archivo_clave, "rb") as f:
            aes_key_enc = f.read()
        # Abrir sesión con PIN para descifrar
        with self.token.open(user_pin=self.pin) as session:
            priv_key = None
            # Buscar clave privada con capacidad DECRYPT
            for obj in session.get_objects({Attribute.CLASS: ObjectClass.PRIVATE_KEY}):
                attrs = obj.get_attributes([Attribute.DECRYPT, Attribute.LABEL])
                if attrs.get(Attribute.DECRYPT, False):
                    priv_key = obj
                    break
            if priv_key is None:
                raise RuntimeError("No se encontró clave privada con capacidad DECRYPT en el DNIe.")
            try:
                aes_key = priv_key.decrypt(aes_key_enc, mechanism=Mechanism.RSA_PKCS_OAEP)
            except Exception as e:
                raise RuntimeError(f"No se pudo descifrar la clave AES con el DNIe: {e}")
        self.aes_key = aes_key
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
                return True
        return False

    def eliminar_contraseña(self, nombre):
        db = self.cargar_bd()
        original_len = len(db["Contrasenas"])
        db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
        if len(db["Contrasenas"]) < original_len:
            self.guardar_bd(db)
            return True
        return False

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






