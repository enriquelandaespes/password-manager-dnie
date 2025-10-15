import secrets
import string

def crear_contraseña(longitud):
    # Definimos los carácteres que usaremos
    caracteres = string.ascii_letters + string.digits + string.punctuation

    # Generamos la contraseña con los carácteres que hemos seleccionado anteriormente. Secrets es como un random pero mas seguro.
    contraseña_generada = ''.join(secrets.choice(caracteres) for i in range(longitud))
    
    return contraseña_generada

# Generamos una contraseña aleatoria que tenga una longitud segura(Entre 15 y 25 carácteres)
def generar_contraseña():
    # Elegimos una longitud aleatoria entre 15 y 25
    longitud_deseada = secrets.randbelow(11) + 15
    
    # Generamos la contraseña llamando a la función
    contraseña_final = crear_contraseña(longitud_deseada)

    return contraseña_final


