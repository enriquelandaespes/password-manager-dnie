import os # Sirve para poder obtener la ruta a la biblioteca pkcs11 en el sistema operativo
import json # Sirve para entender la base de datos con el lenguaje JSON
from hashlib import sha256 # Sirve para obetener el hash de algunas claves con el algoritmo sha256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509 # Sirve para leer y entender los certificados digitales del dni
from pkcs11 import lib as pkcs11_lib, ObjectClass, Attribute # Sirve para poder interactuar con el dni
from pkcs11 import Mechanism # Sirve para implementar el mecanismo de firma del dni (Sirve para más cosas pero en este caso lo utilizamos para firmar)
# Implementamos manejo_datos como una clase para que al correr este programa se inicialice como una instancia y todas las 
# variables críticas como pueden ser el pin o las claves no se queden registradas como variables globales.
class manejo_datos:
    
    PKCS11_LIB = r"C:\Program Files\OpenSC Project\OpenSC\pkcs11\opensc-pkcs11.dll" # Donde se encuentra la librería pcks11(¡PUEDE DAR FALLO!)
    SLOT_INDEX = 0

    AES_KEY_SIZE = 32  # 256 bits
    C_FILENAME = "C_value.bin"
    # Constructor de manejo de datos, solo necesita el pin, self representa al propio objeto que crea el constructor
    def __init__(self, pin: str):
        self.pin = pin # Obtiene el valor del pin(En verificar dnie)
        self.token = self.obtener_token() # Obtiene el token del dni, el token es el "Pase de acceso" del dni, verifica la identidad y permite acceder sin mostrar la clave privada
        self.cert = self.obtener_certificado_autenticacion() # Obtiene el certificado de autenticacion del dni
        self.nombre = self.obtener_nombre()  # Obtenemos el nombre del certificado
        self.serial_hash = self.obtener_hash_serial()  # hash del número de serie del dni
        # archivos:
        self.archivo_kdb = os.path.join(os.path.dirname(__file__), f"kdb_enc_{self.serial_hash}.bin") # Archivo que guarda la clave de acceso a la base de datos
        self.archivo_bd = os.path.join(os.path.dirname(__file__), f"Database_{self.serial_hash}.json.enc") # Archivo(json) que guarda la base de datos del dni. Se identifica por el hash del numero de serie del dni
        self.archivo_C = os.path.join(os.path.dirname(__file__), self.C_FILENAME) # Archivo que guarda el número C, es el único que no va cifrado.
        self.k_db_cache = None # Guarda la k_db cuando es necesario para no tener que firmar constantemente con el dni, acelera los procesos, de primeras no se inicializa.

        self.inicializar_C() # Crea C si no existía anteriormente
        self.inicializar_kdb() # Crea kdb si no existia anteriormente para ese usuario.

    # Funcion de verificacion del pin del DNIe
    def verificar_dnie(self, pin):
        try:
            token = obtener_token()
            with token.open(user_pin=pin): # Verifica que el pin es el correcto pasandole al token el pin que introduce el usuario.
                return True
        except Exception:
            return False
            
    # Funcion para obtener el token del DNIe
    def obtener_token(self):
        pkcs11 = pkcs11_lib(self.PKCS11_LIB)
        slots = pkcs11.get_slots(token_present=True)
        if not slots:
            raise RuntimeError("No se encontró token DNIe.")
        return slots[self.SLOT_INDEX].get_token()
        
    # Funcion para obtener el certificado de autenticacion del DNIe
    def obtener_certificado_autenticacion(self):
        with self.token.open(rw=True) as session:
            certificados = list(session.get_objects({Attribute.CLASS: ObjectClass.CERTIFICATE}))
            if not certificados:
                raise RuntimeError("No se encontró certificado en el DNIe.")
            der = certificados[0][Attribute.VALUE]
            return x509.load_der_x509_certificate(der)

    # Funcion para obtener el NIF
    def obtener_nif(self):
        subject = self.cert.subject
        for attr in subject:
            if attr.oid.dotted_string == "2.5.4.5":
                return attr.value
        raise RuntimeError("No se encontró NIF en certificado.")
        
    # Funcion para obtener el nombre del DNIe
    def obtener_nombre(self):
        subject = self.cert.subject
        for attr in subject:
            if attr.oid.dotted_string == "2.5.4.3":
                return attr.value
        return f"usuario_{self.nif}"

    # Funcion para calcular el hash del numero de serie del DNIe
    def obtener_hash_serial(self) -> str:
        serial = str(self.cert.serial_number).encode('utf-8')
        h = sha256(serial).hexdigest()[:16]
        return h

    # Gestión de C (64 bits): Es un numero aleatorio usado para ser firmado y con ello cifrar la K_db (Clave de cifrado de la base de datos. Cada "cliente" tiene una K_db distinta)
    # Funcion para inicializar C si no existe.
    def inicializar_C(self):
        if os.path.exists(self.archivo_C):
            return
        C = os.urandom(8)  # 64 bits
        with open(self.archivo_C, "wb") as f:
            f.write(C)

    # Funcion para leer C si ya existe
    def leer_C(self) -> bytes:
        with open(self.archivo_C, "rb") as f:
            data = f.read()
        if len(data) != 8:
            raise RuntimeError("Valor C inválido (longitud incorrecta).")
        return data

    # Firma con el DNI (S = firma_de(C))
    def firmar_con_dni(self, data: bytes) -> bytes:
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

    # k_db (clave de la Base de Datos). Cada DNI tiene su propia Clave
    def inicializar_kdb(self):
        if os.path.exists(self.archivo_kdb):
            return
        k_db = os.urandom(self.AES_KEY_SIZE)
        C = self.leer_C()
        S = self.firmar_con_dni(C)
        K = sha256(S).digest()
        aesgcm = AESGCM(K)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, k_db, associated_data=None)
        with open(self.archivo_kdb, "wb") as f:
            f.write(nonce + ct)
        self.k_db_cache = k_db

    # Funcion para descifrar la Clave K_db
    def descifrar_kdb(self) -> bytes:
        if self.k_db_cache is not None:
            return self.k_db_cache
        if not os.path.exists(self.archivo_kdb):
            raise RuntimeError("No existe la clave k_db cifrada para este DNI.")
        with open(self.archivo_kdb, "rb") as f:
            contenido = f.read()
        nonce = contenido[:12]
        ct = contenido[12:]
        C = self.leer_C()
        S = self.firmar_con_dni(C)
        K = sha256(S).digest()
        aesgcm = AESGCM(K)
        k_db = aesgcm.decrypt(nonce, ct, associated_data=None)
        self.k_db_cache = k_db
        return k_db

    # Funciones de manejo de la Base de datos
    # Funcion para cargar la base de datos
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

    # Funcion para guardar la Base de Datos
    def guardar_bd(self, db):
        k_db = self._descifrar_kdb()
        aesgcm = AESGCM(k_db)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, json.dumps(db, indent=4).encode("utf-8"), associated_data=None)
        with open(self.archivo_bd, "wb") as f:
            f.write(nonce + ct)

    # Funcion para agregar nuevas contraseñas
    def agregar_contraseña(self, nombre, contraseña):
        db = self.cargar_bd()
        if any(u["nombre"] == nombre for u in db["Contrasenas"]):
            return False
        db["Contrasenas"].append({"nombre": nombre, "contrasena": contraseña})
        self.guardar_bd(db)
        return True

    # Funcion para editar contraseñas ya existentes
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

    # Funcion para eliminar contraseñas
    def eliminar_contraseña(self, nombre):
        db = self.cargar_bd()
        original_len = len(db["Contrasenas"])
        db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
        if len(db["Contrasenas"]) < original_len:
            self.guardar_bd(db)
            return True
        else:
            return False

    # Funcion para editar el nombre
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





