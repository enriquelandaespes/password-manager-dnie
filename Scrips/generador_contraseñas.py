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
    try:

        longitud_deseada = random.randint(15, 25)
        
        # Generamos la contraseña llamando a la función
        contraseña_final = crear_contraseña(longitud_deseada)
        
        # Mostramos el resultado
        print(f"\n✅ ¡Contraseña generada con éxito!")
        print(f"Tu contraseña segura es: {contraseña_final} y tiene {longitud_deseada} caracteres.\n")

    except ValueError:
        print("\n❌ Error: Por favor, introduce un número válido.")