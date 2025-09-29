import random
import string

def crear_contraseña(longitud):
    """
    Esta función genera una contraseña aleatoria con la longitud especificada.
    """
    # 1. Definimos los caracteres que usaremos
    #    - string.ascii_letters (letras mayúsculas y minúsculas)
    #    - string.digits (números del 0 al 9)
    #    - string.punctuation (símbolos como !, @, #, $, etc.)
    caracteres = string.ascii_letters + string.digits + string.punctuation

    # 2. Generamos la contraseña
    #    - random.choice() selecciona un carácter al azar del grupo anterior.
    #    - Hacemos esto 'longitud' veces.
    #    - ''.join() une todos los caracteres seleccionados en un solo texto.
    contraseña_generada = ''.join(random.choice(caracteres) for i in range(longitud))
    
    return contraseña_generada

# --- Programa Principal ---

# Pedimos al usuario que elija la longitud. Se recomienda 12 o más.
def generar_contraseña():
    # Elegimos una longitud aleatoria entre 15 y 25
    longitud_deseada = random.randint(15, 25)
    
    # Generamos la contraseña llamando a la función
    contraseña_final = crear_contraseña(longitud_deseada)
    return contraseña_final
