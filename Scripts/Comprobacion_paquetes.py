import sys
import subprocess
import importlib

def verificar_dependencias():
    # Esta función comprueba dentro de los paqutes requeridos para el funcionamiento del programa cuales estan istalados y cuales no
    paquetes_requeridos = {
        'pygame': 'pygame',
        'pyscard': 'smartcard', # El paquete se llama pyscard pero se importa como smartcard
        'cryptography': 'cryptography',
        'python-pkcs11': 'pkcs11',
        'pyperclip': 'pyperclip',
        'ttkbootstrap': 'ttkbootstrap'
    }

    paquetes_faltantes = []
    for paquete_pip, nombre_import in paquetes_requeridos.items():
        try:
            # Intenta importar la librería, en caso que no exista saltara la excepción
            importlib.import_module(nombre_import)
            print(f"{paquete_pip} ya está instalado.")
        except ImportError:
            # Si falla, la añade a la lista de faltantes
            print(f"{paquete_pip} no está instalado.")
            paquetes_faltantes.append(paquete_pip)

    if not paquetes_faltantes:
        return True

    # Si faltan paquetes, pregunta al usuario si quiere instalarlos por consola
    print("\nFaltan algunas librerías necesarias para ejecutar la aplicación.")
    respuesta = input("¿Te gustaría instalarlas ahora? (s/n): ").lower()

    if respuesta == 's':
        print("\nInstalando paquetes faltantes con pip...")
        for paquete in paquetes_faltantes:
            try:
                # Llama a pip para instalar el paquete y sys.executable se asegura de que se use el pip del python correcto
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
            except subprocess.CalledProcessError:
                # Salta la excepción si al instalar el paquete ocurre un error
                print(f"\nHubo un error instalando '{paquete}'.")
                print("Por favor, instálalo manualmente ejecutando: pip install " + paquete)
                return False
        
        print("\n¡Instalación completada! Por favor, vuelve a ejecutar el programa.")
        # Es necesario salir para que los nuevos módulos se carguen correctamente
        sys.exit()
        
    else:
        print("\nInstalación cancelada. La aplicación no puede continuar.")
        return False

# Pon esto al principio del todo en Inicio_Gestor.py

if __name__ == "__main__":
    # Primero, verifica las dependencias
    if verificar_dependencias():
        # Si todo está OK, importa el resto y ejecuta tu código de Pygame
        import pygame
