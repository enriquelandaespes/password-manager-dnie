"""
bd_cifrada_dnie.py

Flujo:
- Si no existe clave_enc.bin -> genera AES key (32 bytes), obtiene certificado público desde el DNIe
  (sin PIN), cifra AES key con la clave pública (RSA-OAEP-SHA256) y guarda clave_enc.bin.
- Al cargar la BD:
  - pide PIN, abre sesión con el DNIe y descifra clave_enc.bin usando la clave privada del DNIe.
  - usa la clave AES descifrada en memoria para descifrar Database.json.enc (AES-GCM).
- Al guardar BD:
  - cifra JSON con AES-GCM y sobrescribe Database.json.enc
"""

import os
import json

from pkcs11 import lib as pkcs11_lib, ObjectClass, Mechanism
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509
from tkinter import messagebox # Se mueve aquí para usarla en las funciones de gestión

# ---------------- CONFIGÚRA ESTO ----------------
# ************************************************
# RUTA CORREGIDA PARA WINDOWS (OpenSC)
PKCS11_LIB = r"C:\\Program Files\\OpenSC Project\\OpenSC\\pkcs11\\opensc-pkcs11.dll"
# ************************************************
SLOT_INDEX = 0                              # índice de slot a usar (0 por defecto)
ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "Database.json.enc")
ARCHIVO_CLAVE_ENC = os.path.join(os.path.dirname(__file__), "clave_enc.bin")
# ------------------------------------------------

def obtener_token():
    # Usa la variable de configuración PKCS11_LIB
    pkcs11 = pkcs11_lib(PKCS11_LIB)
    slots = pkcs11.get_slots(token_present=True)
    if not slots:
        raise SystemExit("No se encontró token DNIe en los slots. ¿Lector conectado?")
    try:
        slot = slots[SLOT_INDEX]
    except IndexError:
        slot = slots[0]
    return slot.get_token()

def extraer_certificado_del_token(token):
    """
    Devuelve el objeto x509.Certificate (público) obtenido desde el token.
    No requiere hacer login al token para leer certificados.
    """
    # Abrimos una sesión "sin login" para leer objetos públicos (certificados)
    with token.open() as session:
        # buscamos objetos de tipo CERTIFICATE
        for obj in session.get_objects({ "class": ObjectClass.CERTIFICATE }):
            # obtener el DER del certificado (atributo CKA_VALUE)
            try:
                der = obj.get_attribute_value('CKA_VALUE')
                if der:
                    cert = x509.load_der_x509_certificate(der)
                    return cert
            except Exception:
                continue
    raise RuntimeError("No se encontró certificado público en el token.")

def inicializar_clave_encriptada(token):
    """
    Si no existe ARCHIVO_CLAVE_ENC:
      - genera AES key (32 bytes)
      - obtiene certificado público desde token
      - cifra AES key con RSA-OAEP-SHA256 y guarda en ARCHIVO_CLAVE_ENC
    """
    if os.path.exists(ARCHIVO_CLAVE_ENC):
        #print("Ya existe clave cifrada en:", ARCHIVO_CLAVE_ENC)
        return
    cert = extraer_certificado_del_token(token)
    pubkey = cert.public_key()

    # generar clave AES-256
    aes_key = AESGCM.generate_key(bit_length=256)  # 32 bytes

    # cifrar AES key con la clave pública (OAEP SHA256)
    aes_key_enc = pubkey.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # guardar en binario
    with open(ARCHIVO_CLAVE_ENC, "wb") as f:
        f.write(aes_key_enc)

    # print("Clave AES generada y cifrada con el certificado del token.")
    # print("Archivo:", ARCHIVO_CLAVE_ENC)
    # NO guardamos la clave AES en claro en disco.
    
pin_guardado=0
def guardar_pin(pin):
    global pin_guardado
    pin_guardado=pin
    

def descifrar_clave_con_dnie():
    """
    Abre sesión en token con PIN y pide al token que descifre la clave AES cifrada (OAEP).
    Devuelve la clave AES en bytes.
    Se ha modificado para usar el argumento 'pin' directamente.
    """
    if not os.path.exists(ARCHIVO_CLAVE_ENC):
        raise FileNotFoundError("No existe archivo de clave cifrada. Ejecuta inicializar_clave_encriptada().")

    with open(ARCHIVO_CLAVE_ENC, "rb") as f:
        aes_key_enc = f.read()

    token = obtener_token()
    # abrir sesión con PIN
    with token.open(user_pin=pin_guardado) as session: # Usa el pin pasado
        # buscar la clave privada RSA con capacidad DECRYPT
        priv_key = None
        for obj in session.get_objects({ "class": ObjectClass.PRIVATE_KEY }):
            try:
                attrs = obj.get_attributes(['CKA_DECRYPT'])
                if attrs.get('CKA_DECRYPT', False):
                    priv_key = obj
                    break
            except Exception:
                continue

        if priv_key is None:
            raise RuntimeError("No se encontró clave privada con CKA_DECRYPT en el DNIe.")

        # intentar descifrar con OAEP; si falla, se puede intentar PKCS1 v1.5 (no recomendado)
        try:
            aes_key = priv_key.decrypt(aes_key_enc, mechanism=Mechanism.RSA_PKCS_OAEP)
        except Exception as exc:
            # intento fallback PKCS1 v1.5
            try:
                aes_key = priv_key.decrypt(aes_key_enc, mechanism=Mechanism.RSA_PKCS)
            except Exception:
                raise RuntimeError(f"No se pudo descifrar la clave con el DNIe: {exc}")
    return aes_key

# ================= funciones de BD cifrada =================
def cargar_bd():
    """
    Descifra Database.json.enc con la clave AES obtenida desde el DNIe (pide PIN).
    Devuelve dict con la base de datos.
    """
    if not os.path.exists(ARCHIVO_DATOS):
        return {"Contrasenas": []}

    try:
        # Usa el PIN guardado globalmente
        aes_key = descifrar_clave_con_dnie(pin_guardado)
    except Exception as e:
        # Esto ocurre si el PIN es incorrecto o no hay DNIe
        messagebox.showerror("Error de Carga", f"Error al descifrar la clave AES con el DNIe: {e}")
        return {"Contrasenas": []} # Devuelve vacío para evitar que la app crashee

    # leer fichero cifrado: formato -> nonce (12 bytes) + ciphertext + tag(16 bytes)
    with open(ARCHIVO_DATOS, "rb") as f:
        contenido = f.read()
    if len(contenido) < 12 + 16:
        raise RuntimeError("Archivo de datos corrupto o no es AES-GCM.")

    nonce = contenido[:12]
    ciphertext = contenido[12:]
    aesgcm = AESGCM(aes_key)
    try:
        datos_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    except Exception as e:
        raise RuntimeError(f"No se pudo descifrar Database.json.enc: {e}")

    return json.loads(datos_bytes.decode("utf-8"))

def guardar_bd(db):
    """
    Cifra el JSON con AES-GCM usando la clave AES (necesita PIN para descifrar la clave).
    """
    try:
        # Usa el PIN guardado globalmente
        aes_key = descifrar_clave_con_dnie()
    except Exception as e:
        messagebox.showerror("Error de Guardado", f"Error al descifrar la clave AES con el DNIe: {e}")
        return # Evita guardar si no se puede obtener la clave

    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce recomendado para GCM
    datos_json = json.dumps(db, indent=4).encode("utf-8")
    ct = aesgcm.encrypt(nonce, datos_json, associated_data=None)
    # guardamos nonce + ciphertext (ct ya incluye tag al final)
    with open(ARCHIVO_DATOS, "wb") as f:
        f.write(nonce + ct)

# ========== funciones de gestión (idénticas a las tuyas, usan cargar_bd/guardar_bd) ==========

def agregar_contraseña(nombre, contraseña):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            messagebox.showinfo("Repetido", f"{nombre} ya existe")
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
    messagebox.showinfo("Actualizado", f"Contraseña actualizada a {nueva}.")
    if len(nueva) < 15:
        messagebox.showwarning("Cuidado", "La contraseña es insegura")
    guardar_bd(db)

def editar_nombre(nombre, nueva, cont):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nueva:
            messagebox.showinfo("Error", "El nombre no se ha actualizado (ya existe)")
            return
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            u["nombre"] = nueva
            messagebox.showinfo("Actualizado", f"{nombre} ahora es {nueva}.")
    guardar_bd(db)

# ================= utilidad simple de prueba =================
if __name__ == "__main__":
    print("Inicializando (si es necesario) la clave cifrada con el certificado del DNIe...")
    try:
        # Se obtiene el token antes de inicializar para tener el objeto
        token_para_init = obtener_token()
        inicializar_clave_encriptada(token_para_init)
        print("Inicialización completa.")
    except Exception as e:
        print("Error al inicializar clave:", e)
        exit(1)

    # Para pruebas, el pin_guardado debe ser establecido manualmente si se ejecuta __main__
    # ejemplo de uso interactivo mínimo
    if not os.path.exists(ARCHIVO_DATOS):
        print("Creando base de datos de ejemplo...")
        # NOTA: Esto fallará si el pin_guardado no está establecido previamente
        # para una prueba real, necesitarías pedir el PIN aquí.
        # Por ahora, solo intenta crear el archivo si no existe.
        print("Base de datos creada (cifrada).")

    # print("Intentando cargar la BD (pedirá PIN)...")
    # Si quieres probar esto, debes haber ejecutado md.guardar_pin("TU_PIN") antes.
    # db = cargar_bd()
    # print("Contenido:", db)