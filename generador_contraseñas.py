import random
import string

def crear_contraseña(longitud):
    # Definimos los carácteres que usaremos
    caracteres = string.ascii_letters + string.digits + string.punctuation

    # Generamos la contraseña con los carácteres que hemos seleccionado anteriormente
    contraseña_generada = ''.join(random.choice(caracteres) for i in range(longitud))
    
    return contraseña_generada

# Generamos una contraseña aleatoria que tenga una longitud segura(Entre 15 y 25 carácteres)
def generar_contraseña():
    # Elegimos una longitud aleatoria entre 15 y 25
        longitud_deseada = random.randint(15, 25)
        
        # Generamos la contraseña llamando a la función
        contraseña_final = crear_contraseña(longitud_deseada)

        return contraseña_final


