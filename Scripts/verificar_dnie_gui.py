import tkinter as tk
from tkinter import font, messagebox
import verificar_dnie as vdnie
import Interfaz_Contraseñas as ic

def verificar_dnie(parent):
    window = tk.Toplevel(parent)
    window.title("Verificación del DNIe")
    window.geometry("600x200")

    main_frame = tk.Frame(window, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    title_font = font.Font(family="Any", size=30, weight="bold")
    subtitle_font = font.Font(family="Any", size=10, weight="bold")

    title_label = tk.Label(main_frame, text="Verificación del DNIe", font=title_font)
    title_label.pack(pady=10)

    tk.Label(main_frame, text="Introduce el PIN de tu DNIe:", font=subtitle_font).pack(pady=5)
    entry_pin = tk.Entry(main_frame, show="*", width=30)
    entry_pin.pack(pady=5)
    tk.Button(main_frame, text="Verificar", command=lambda: check_dnie(entry_pin, window, main_frame, subtitle_font, parent)).pack(pady=10)

def check_dnie(entry_pin, window, main_frame, subtitle_font, parent):
    pin = entry_pin.get().strip()
    if not pin:
        messagebox.showwarning("PIN vacío", "Por favor introduce tu PIN.")
        return

    if vdnie.verificar_dnie(pin):
        status_label = tk.Label(main_frame, text="DNIe verificado correctamente.", font=subtitle_font, fg="green")
        status_label.pack(pady=10)
        window.after(1000, lambda: abrir_gestor(window, parent))
    else:
        status_label = tk.Label(main_frame, text="PIN incorrecto o DNIe no responde.", font=subtitle_font, fg="red")
        status_label.pack(pady=10)

def abrir_gestor(window, parent):
    try:
        ic.interfaz_contrasenas()
        window.destroy()
        parent.deiconify()  # Muestra de nuevo la ventana principal al cerrar el gestor
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el gestor de contraseñas.\n{e}")
