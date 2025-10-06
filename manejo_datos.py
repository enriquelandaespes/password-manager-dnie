"""
bd_cifrada_pin_por_nif_auto.py

Flujo:
- Inicialización:
  - Si no existe clave_enc_{NIF}.bin -> genera AES key (32 bytes)
  - Cifra la clave AES usando derivación del PIN (PBKDF2-HMAC-SHA256)
  - Guarda clave cifrada + salt
- Al cargar la BD:
  - pide PIN
  - descifra la clave AES usando la derivación del PIN
  - usa la clave AES para descifrar Database_{NIF}.json.enc (AES-GCM)
- Al guardar BD:
  - cifra JSON con AES-GCM usando la clave AES
- Bases de datos independientes según NIF del DNIe
- Detecta automáticamente el primer certificado disponible en el DNIe
"""

import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pkcs11 import lib as pkcs11_lib, ObjectClass, Attribute
from cryptography import x509

# ---------------- CONFIG ----------------
PKCS11_LIB = r"C:\\Program Files\\OpenSC Project\\OpenSC\\pkcs11\\opensc-pkcs11.dll"
PBKDF2_ITERATIONS = 100_000
PBKDF2_SALT_SIZE = 16
AES_KEY_SIZE = 32  # bytes
SLOT_INDEX = 0
# ---------------------------------------

# ---------------- Variables globales ----------------
pin_guardado = None

def guardar_pin(pin):
    global pin_guardado
    pin_guardado = pin

def limpiar_pin():
    global pin_guardado
    pin_guardado = None

# ---------------- DNIe y NIF ----------------
def obtener_token():
    pkcs11 = pkcs11_lib(PKCS11_LIB)
    slots = pkcs11.get_slots(token_present=True)
    if not slots:
        raise RuntimeError("No se encontró ningún token DNIe conectado.")
    return slots[SLOT_INDEX].get_token()

def obtener_certificado_autenticacion():
    """
    Detecta automáticamente el primer certificado disponible en el DNIe.
    """
    token = obtener_token()
    with token.open(rw=True) as session:
        certificados = list(session.get_objects({Attribute.CLASS: ObjectClass.CERTIFICATE}))
        if not certificados:
            raise RuntimeError("No se encontró ningún certificado en el DNIe.")
        cert_obj = certificados[0]
        der = cert_obj[Attribute.VALUE]
        return x509.load_der_x509_certificate(der)

def obtener_nif():
    """
    Extrae el NIF del certificado de autenticación del DNIe.
    """
    cert = obtener_certificado_autenticacion()
    subject = cert.subject
    for attr in subject:
        if attr.oid.dotted_string == "2.5.4.5":  # SerialNumber OID
            return attr.value
    raise RuntimeError("No se encontró el NIF en el certificado de autenticación.")

# ---------------- Rutas dinámicas por NIF ----------------
def _ruta_archivo_clave(nif: str):
    return os.path.join(os.path.dirname(__file__), f"clave_enc_{nif}.bin")

def _ruta_archivo_bd(nif: str):
    return os.path.join(os.path.dirname(__file__), f"Database_{nif}.json.enc")

# ---------------- Clave AES derivada del PIN ----------------
def inicializar_clave_encriptada():
    if pin_guardado is None:
        raise ValueError("Debes establecer el PIN primero.")
    nif = obtener_nif()
    archivo_clave = _ruta_archivo_clave(nif)
    if os.path.exists(archivo_clave):
        return
    aes_key = os.urandom(AES_KEY_SIZE)
    salt = os.urandom(PBKDF2_SALT_SIZE)
    key_enc = _cifrar_aes_key(aes_key, pin_guardado, salt)
    with open(archivo_clave, "wb") as f:
        f.write(salt + key_enc)
    print(f"Clave AES inicializada para NIF {nif}.")

def _cifrar_aes_key(aes_key: bytes, pin: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=AES_KEY_SIZE, salt=salt, iterations=PBKDF2_ITERATIONS)
    key_pin = kdf.derive(pin.encode())
    aesgcm = AESGCM(key_pin)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, aes_key, associated_data=None)
    return nonce + ct

def _descifrar_aes_key(pin: str, nif: str) -> bytes:
    archivo_clave = _ruta_archivo_clave(nif)
    if not os.path.exists(archivo_clave):
        raise FileNotFoundError(f"No existe clave AES para NIF {nif}.")
    with open(archivo_clave, "rb") as f:
        contenido = f.read()
    salt = contenido[:PBKDF2_SALT_SIZE]
    nonce_ct = contenido[PBKDF2_SALT_SIZE:]
    nonce = nonce_ct[:12]
    ct = nonce_ct[12:]
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=AES_KEY_SIZE, salt=salt, iterations=PBKDF2_ITERATIONS)
    key_pin = kdf.derive(pin.encode())
    aesgcm = AESGCM(key_pin)
    return aesgcm.decrypt(nonce, ct, associated_data=None)

def obtener_clave_aes():
    if pin_guardado is None:
        raise ValueError("Debes establecer el PIN primero.")
    nif = obtener_nif()
    return _descifrar_aes_key(pin_guardado, nif), nif

# ---------------- Base de datos cifrada ----------------
def cargar_bd():
    aes_key, nif = obtener_clave_aes()
    archivo_bd = _ruta_archivo_bd(nif)
    if not os.path.exists(archivo_bd):
        return {"Contrasenas": []}
    with open(archivo_bd, "rb") as f:
        contenido = f.read()
    nonce = contenido[:12]
    ct = contenido[12:]
    aesgcm = AESGCM(aes_key)
    datos_bytes = aesgcm.decrypt(nonce, ct, associated_data=None)
    return json.loads(datos_bytes.decode("utf-8"))

def guardar_bd(db):
    aes_key, nif = obtener_clave_aes()
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, json.dumps(db, indent=4).encode("utf-8"), associated_data=None)
    archivo_bd = _ruta_archivo_bd(nif)
    with open(archivo_bd, "wb") as f:
        f.write(nonce + ct)

# ---------------- CRUD ----------------
def agregar_contraseña(nombre, contraseña):
    db = cargar_bd()
    if any(u["nombre"] == nombre for u in db["Contrasenas"]):
        return False
    db["Contrasenas"].append({"nombre": nombre, "contrasena": contraseña})
    guardar_bd(db)
    return True

def buscar_contraseña(nombre):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            return u
    return None

def eliminar_contraseña(nombre):
    db = cargar_bd()
    db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
    guardar_bd(db)

def editar_contraseña(nombre, nueva):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            u["contrasena"] = nueva
            break
    guardar_bd(db)

def editar_nombre(nombre_actual, nuevo_nombre):
    db = cargar_bd()
    if any(u["nombre"] == nuevo_nombre for u in db["Contrasenas"]):
        print(f"Error: ya existe '{nuevo_nombre}'")
        return False
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre_actual:
            u["nombre"] = nuevo_nombre
            guardar_bd(db)
            print(f"Nombre cambiado de '{nombre_actual}' a '{nuevo_nombre}'")
            return True
    print(f"No se encontró '{nombre_actual}'")
    return False





