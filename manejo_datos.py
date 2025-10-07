import os
import json
from hashlib import sha256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509

# pkcs11
from pkcs11 import lib as pkcs11_lib, ObjectClass, Attribute
from pkcs11 import Mechanism  # mecanismo de firma

class manejo_datos:
    PKCS11_LIB = r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll"
    SLOT_INDEX = 0

    AES_KEY_SIZE = 32  # 256 bits
    C_FILENAME = "C_value.bin"

    def __init__(self, pin: str):
        """
        Inicializa el handler con el PIN (usado para abrir el token y firmar).
        """
        self.pin = pin
        self.token = self._obtener_token()
        self.cert = self._obtener_certificado_autenticacion()
        self.nif = self._obtener_nif()
        self.nombre = self._obtener_nombre()  # CN del certificado
        self.serial_hash = self._obtener_hash_serial()  # hash del número de serie
        # archivos:
        self.archivo_kdb = os.path.join(os.path.dirname(__file__), f"kdb_enc_{self.serial_hash}.bin")
        self.archivo_bd = os.path.join(os.path.dirname(__file__), f"Database_{self.serial_hash}.json.enc")
        self.archivo_C = os.path.join(os.path.dirname(__file__), self.C_FILENAME)
        self._k_db_cache = None

        self._inicializar_C()
        self._inicializar_kdb()

    # ---------- DNIe, token y certificados ----------
    def verificar_dnie(self, pin):
        try:
            pkcs11 = pkcs11_lib(self.PKCS11_LIB)
            slots = pkcs11.get_slots(token_present=True)
            if not slots:
                return False
            token = slots[self.SLOT_INDEX].get_token()
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
            if attr.oid.dotted_string == "2.5.4.5":
                return attr.value
        raise RuntimeError("No se encontró NIF en certificado.")

    def _obtener_nombre(self):
        subject = self.cert.subject
        for attr in subject:
            if attr.oid.dotted_string == "2.5.4.3":
                return attr.value
        return f"usuario_{self.nif}"

    def _obtener_hash_serial(self) -> str:
        serial = str(self.cert.serial_number).encode('utf-8')
        h = sha256(serial).hexdigest()[:16]
        return h

    # ---------- Gestión de C (64-bit común) ----------
    def _inicializar_C(self):
        if os.path.exists(self.archivo_C):
            return
        C = os.urandom(8)  # 64 bits
        with open(self.archivo_C, "wb") as f:
            f.write(C)

    def _leer_C(self) -> bytes:
        with open(self.archivo_C, "rb") as f:
            data = f.read()
        if len(data) != 8:
            raise RuntimeError("Valor C inválido (longitud incorrecta).")
        return data

    # ---------- Firma con el DNI (S = firma_de(C)) ----------
    def _firmar_con_dni(self, data: bytes) -> bytes:
        with self.token.open(user_pin=self.pin) as session:
            keys = list(session.get_objects({Attribute.CLASS: ObjectClass.PRIVATE_KEY}))
            if not keys:
                raise RuntimeError("No se encontró clave privada para firmar en el token.")
            priv = keys[0]
            try:
                signature = priv.sign(data, mechanism=Mechanism.SHA256_RSA_PKCS)
            except Exception as e:
                try:
                    signature = priv.sign(data)
                except Exception as e2:
                    raise RuntimeError(f"Error al firmar con DNIe: {e2}") from e
            return signature

    # ---------- k_db (clave de la BD) por DNI ----------
    def _inicializar_kdb(self):
        if os.path.exists(self.archivo_kdb):
            return
        k_db = os.urandom(self.AES_KEY_SIZE)
        C = self._leer_C()
        S = self._firmar_con_dni(C)
        K = sha256(S).digest()
        aesgcm = AESGCM(K)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, k_db, associated_data=None)
        with open(self.archivo_kdb, "wb") as f:
            f.write(nonce + ct)
        self._k_db_cache = k_db

    def _descifrar_kdb(self) -> bytes:
        if self._k_db_cache is not None:
            return self._k_db_cache
        if not os.path.exists(self.archivo_kdb):
            raise RuntimeError("No existe la clave k_db cifrada para este DNI.")
        with open(self.archivo_kdb, "rb") as f:
            contenido = f.read()
        nonce = contenido[:12]
        ct = contenido[12:]
        C = self._leer_C()
        S = self._firmar_con_dni(C)
        K = sha256(S).digest()
        aesgcm = AESGCM(K)
        k_db = aesgcm.decrypt(nonce, ct, associated_data=None)
        self._k_db_cache = k_db
        return k_db

    # ---------- Base de datos ----------
    def cargar_bd(self):
        k_db = self._descifrar_kdb()
        if not os.path.exists(self.archivo_bd):
            return {"Contrasenas": []}
        with open(self.archivo_bd, "rb") as f:
            contenido = f.read()
        nonce = contenido[:12]
        ct = contenido[12:]
        aesgcm = AESGCM(k_db)
        datos_bytes = aesgcm.decrypt(nonce, ct, associated_data=None)
        return json.loads(datos_bytes.decode("utf-8"))

    def guardar_bd(self, db):
        k_db = self._descifrar_kdb()
        aesgcm = AESGCM(k_db)
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
        if not nueva_contraseña or len(nueva_contraseña) < 15:
            return False
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
        else:
            return False

    def editar_nombre(self, nombre_actual, nuevo_nombre):
        if not nuevo_nombre or not nuevo_nombre.strip():
            return False
        db = self.cargar_bd()
        if any(u["nombre"] == nuevo_nombre for u in db["Contrasenas"]):
            return False
        for u in db["Contrasenas"]:
            if u["nombre"] == nombre_actual:
                u["nombre"] = nuevo_nombre
                self.guardar_bd(db)
                return True
        return False
