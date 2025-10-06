from pkcs11 import lib
import getpass
import manejo_datos as md
def verificar_dnie(pin):
    # Ruta a la librería PKCS#11 para Windows
    libpath = r"C:\\Program Files\\OpenSC Project\\OpenSC\\pkcs11\\opensc-pkcs11.dll"
    pkcs11 = lib(libpath)
    slots = pkcs11.get_slots(token_present=True)
    for slot in slots:
        token = slot.get_token()
        md.inicializar_clave_encriptada()
        
        try:
            # Intentar abrir sesión con el PIN
            with token.open(user_pin=pin):
                return True
        except Exception as e:
            return False