import tkinter as tk
from tkinter import font
import detectar_dnie as det
import verificar_dnie_gui as vdnie

def detectar_dnie(parent):
    # Ocultar la ventana principal mientras se detecta el DNIe
    parent.withdraw()

    window = tk.Toplevel(parent)
    window.title('Detección del DNIe')
    window.geometry('600x250')

    title_font = font.Font(family="Any", size=30, weight="bold")
    subtitle_font = font.Font(family="Any", size=10, weight="bold")

    main_frame = tk.Frame(window)
    main_frame.pack(expand=True, fill='both', padx=30, pady=10)

    title_label = tk.Label(main_frame, text="Detectando DNIe...", font=title_font)
    title_label.pack(pady=10)

    window.after(2000, lambda: mostrar_resultado(window, main_frame, subtitle_font, parent))
    window.mainloop()

def mostrar_resultado(window, main_frame, subtitle_font, parent):
    if det.detectar_dnie():
        status_label = tk.Label(main_frame, text="DNIe detectado correctamente.", font=subtitle_font, fg="green")
        status_label.pack(pady=10)
        window.after(2000, lambda: [window.destroy(), vdnie.verificar_dnie(parent)])
    else:
        status_label = tk.Label(main_frame, text="No se ha detectado el DNIe.", font=subtitle_font, fg="red")
        status_label.pack(pady=10)

