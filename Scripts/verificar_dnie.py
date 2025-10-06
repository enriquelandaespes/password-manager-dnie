from pkcs11 import lib
import manejo_datos as md
from tkinter import messagebox

def verificar_dnie(pin):
    """
    Verifica el PIN del DNIe usando la librería PKCS#11 definida en manejo_datos.py.
    Si el PIN es correcto:
      - Inicializa la clave cifrada (si no existe)
      - Guarda el PIN en manejo_datos para las operaciones posteriores
    Devuelve True si la verificación fue exitosa, False si falló.
    """

    # 1️⃣ Cargar la librería PKCS#11 desde manejo_datos.py
    try:
        pkcs11 = lib(md.PKCS11_LIB)
    except Exception as e:
        messagebox.showerror(
            "Error de Librería",
            f"No se pudo cargar la librería PKCS#11.\n"
            f"Revisa la ruta en manejo_datos.py.\n\nError: {e}"
        )
        return False

    # 2️⃣ Buscar tokens (DNIe conectados)
    try:
        slots = pkcs11.get_slots(token_present=True)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo acceder a los slots PKCS#11.\n{e}")
        return False

    if not slots:
        messagebox.showerror("Error", "No se detectó ningún DNIe.\nAsegúrate de que esté insertado correctamente.")
        return False

    # 3️⃣ Intentar verificar el PIN en cada token disponible
    for slot in slots:
        try:
            token = slot.get_token()
            with token.open(user_pin=pin):
                # Si no lanza excepción → el PIN es correcto
                md.inicializar_clave_encriptada(token)
                md.guardar_pin(pin)
                return True
        except Exception:
            continue

    # 4️⃣ Si ninguno permitió abrir sesión, el PIN o el DNIe son incorrectos
    messagebox.showerror("Error de PIN", "PIN incorrecto o el DNIe no responde.")
    return False
