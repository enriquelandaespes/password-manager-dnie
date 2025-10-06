import tkinter as tk
from tkinter import font
import detectar_dnie_gui as detdniegui

def iniciar_gestor():
    window = tk.Tk()
    window.title('Gestor de Contraseñas')
    window.geometry('600x250')

    title_font = font.Font(family="Any", size=30, weight="bold")
    subtitle_font = font.Font(family="Any", size=10, weight="bold")

    main_frame = tk.Frame(window)
    main_frame.pack(expand=True, fill='both', padx=10, pady=10)

    title_label = tk.Label(main_frame, text="Gestor de Contraseñas", font=title_font)
    title_label.pack(pady=10)

    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=20)

    exit_button = tk.Button(button_frame, text='Salir', width=10, height=3, command=window.destroy)
    exit_button.pack(side=tk.LEFT, padx=10)

    access_button = tk.Button(
        button_frame, text='Acceder', width=10, height=3,
        command=lambda: detdniegui.detectar_dnie(parent=window)
    )
    access_button.pack(side=tk.LEFT, padx=10)

    spacer = tk.Label(main_frame, text="", height=2)
    spacer.pack()

    subtitle_label = tk.Label(main_frame, text="by Enrique Landa y Ruben Sanz", font=subtitle_font, fg="gray")
    subtitle_label.pack(side=tk.BOTTOM, anchor='e')

    window.mainloop()

if __name__ == "__main__":
    iniciar_gestor()
