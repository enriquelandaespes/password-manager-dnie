"""
bd_cifrada_pin.py

Flujo:
- Inicialización:
  - Si no existe clave_enc.bin -> genera AES key (32 bytes)
  - Cifra la clave AES usando derivación del PIN (PBKDF2-HMAC-SHA256) y guarda clave_enc.bin
- Al cargar la BD:
  - pide PIN
  - descifra la clave AES usando la derivación del PIN
  - usa la clave AES para descifrar Database.json.enc (AES-GCM)
- Al guardar BD:
  - cifra JSON con AES-GCM usando la clave AES
"""

import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ---------------- CONFIG ----------------
ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "Database.json.enc")
ARCHIVO_CLAVE_ENC = os.path.join(os.path.dirname(__file__), "clave_enc.bin")
PBKDF2_ITERATIONS = 100_000
PBKDF2_SALT_SIZE = 16
AES_KEY_SIZE = 32  # bytes
# ---------------------------------------

# Variable global para guardar PIN
pin_guardado = None

def guardar_pin(pin):
    global pin_guardado
    pin_guardado = pin

def limpiar_pin():
    global pin_guardado
    pin_guardado = None

# ---------------- Clave AES derivada del PIN ----------------
def inicializar_clave_encriptada():
    """
    Si no existe ARCHIVO_CLAVE_ENC:
        - genera clave AES-256
        - cifra AES con derivación de PIN
        - guarda clave cifrada + salt
    """
    if os.path.exists(ARCHIVO_CLAVE_ENC):
        return
    if pin_guardado is None:
        raise ValueError("Necesitas establecer el PIN antes de inicializar la clave AES.")

    # generar clave AES
    aes_key = os.urandom(AES_KEY_SIZE)
    salt = os.urandom(PBKDF2_SALT_SIZE)
    key_enc = _cifrar_aes_key(aes_key, pin_guardado, salt)

    # guardar salt + key_enc
    with open(ARCHIVO_CLAVE_ENC, "wb") as f:
        f.write(salt + key_enc)
    print("Clave AES generada y cifrada usando PIN.")

def _cifrar_aes_key(aes_key: bytes, pin: str, salt: bytes) -> bytes:
    """Cifra la clave AES usando derivación PBKDF2 del PIN"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key_pin = kdf.derive(pin.encode())
    aesgcm = AESGCM(key_pin)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, aes_key, associated_data=None)
    return nonce + ct  # nonce + ciphertext

def _descifrar_aes_key(pin: str) -> bytes:
    """Descifra la clave AES usando derivación PBKDF2 del PIN"""
    if not os.path.exists(ARCHIVO_CLAVE_ENC):
        raise FileNotFoundError("No existe archivo de clave cifrada. Inicializa primero.")

    with open(ARCHIVO_CLAVE_ENC, "rb") as f:
        contenido = f.read()
    salt = contenido[:PBKDF2_SALT_SIZE]
    nonce_ct = contenido[PBKDF2_SALT_SIZE:]
    nonce = nonce_ct[:12]
    ct = nonce_ct[12:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key_pin = kdf.derive(pin.encode())
    aesgcm = AESGCM(key_pin)
    return aesgcm.decrypt(nonce, ct, associated_data=None)

def obtener_clave_aes():
    if pin_guardado is None:
        raise ValueError("PIN no establecido. Usa guardar_pin().")
    return _descifrar_aes_key(pin_guardado)

# ---------------- Base de datos cifrada ----------------
def cargar_bd():
    if not os.path.exists(ARCHIVO_DATOS):
        return {"Contrasenas": []}
    aes_key = obtener_clave_aes()
    with open(ARCHIVO_DATOS, "rb") as f:
        contenido = f.read()
    if len(contenido) < 12 + 16:
        raise RuntimeError("Archivo corrupto o no AES-GCM.")
    nonce = contenido[:12]
    ct = contenido[12:]
    aesgcm = AESGCM(aes_key)
    datos_bytes = aesgcm.decrypt(nonce, ct, associated_data=None)
    return json.loads(datos_bytes.decode("utf-8"))

def guardar_bd(db):
    aes_key = obtener_clave_aes()
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, json.dumps(db, indent=4).encode("utf-8"), associated_data=None)
    with open(ARCHIVO_DATOS, "wb") as f:
        f.write(nonce + ct)

# ---------------- Funciones CRUD ----------------
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
    """
    Cambia el 'nombre' de una entrada en la base de datos.
    - Evita duplicados.
    - Guarda los cambios en el archivo cifrado.
    """
    db = cargar_bd()
    
    # Verificar si el nuevo nombre ya existe
    if any(u["nombre"] == nuevo_nombre for u in db["Contrasenas"]):
        print(f"Error: ya existe una entrada con el nombre '{nuevo_nombre}'.")
        return False
    
    # Buscar la entrada a modificar
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre_actual:
            u["nombre"] = nuevo_nombre
            guardar_bd(db)
            print(f"Nombre cambiado de '{nombre_actual}' a '{nuevo_nombre}'.")
            return True
    
    print(f"No se encontró la entrada con el nombre '{nombre_actual}'.")
    return False


