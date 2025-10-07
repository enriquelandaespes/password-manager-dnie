import sys
import subprocess
import importlib

# --- FUNCIÓN PARA COMPROBAR E INSTALAR DEPENDENCIAS ---

def verificar_dependencias():
    """
    Comprueba si las librerías necesarias están instaladas.
    Si falta alguna, pregunta al usuario si desea instalarlas.
    """
    # Lista de paquetes necesarios y el nombre con el que se importan
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
            # Intenta importar la librería
            importlib.import_module(nombre_import)
            print(f"✅ {paquete_pip} ya está instalado.")
        except ImportError:
            # Si falla, la añade a la lista de faltantes
            print(f"❌ {paquete_pip} no está instalado.")
            paquetes_faltantes.append(paquete_pip)

    if not paquetes_faltantes:
        print("\n¡Todas las dependencias están instaladas! Iniciando aplicación...")
        return True

    # Si faltan paquetes, pregunta al usuario si quiere instalarlos
    print("\nFaltan algunas librerías necesarias para ejecutar la aplicación.")
    respuesta = input("¿Te gustaría instalarlas ahora? (s/n): ").lower()

    if respuesta == 's':
        print("\nInstalando paquetes faltantes con pip...")
        for paquete in paquetes_faltantes:
            try:
                # Llama a pip para instalar el paquete
                # sys.executable se asegura de que se use el pip del python correcto
                subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
            except subprocess.CalledProcessError:
                print(f"\nHubo un error instalando '{paquete}'.")
                print("Por favor, instálalo manualmente ejecutando: pip install " + paquete)
                return False
        
        print("\n¡Instalación completada! Por favor, vuelve a ejecutar el programa.")
        # Es necesario salir para que los nuevos módulos se carguen correctamente
        sys.exit()
        
    else:
        print("\nInstalación cancelada. La aplicación no puede continuar.")
        return False

# --- CÓMO USARLO EN Inicio_Gestor.py ---

# Pon esto al principio del todo en Inicio_Gestor.py

if __name__ == "__main__":
    # Primero, verifica las dependencias
    if verificar_dependencias():
        # Si todo está OK, importa el resto y ejecuta tu código de Pygame
        import pygame
        # ... (el resto de tu código de Inicio_Gestor.py iría aquí)
        # Por ejemplo:
        # pygame.init()
        # screen = pygame.display.set_mode(...)
        # etc.