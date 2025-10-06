import tkinter as tk
from tkinter import font
import Interfaz_Contraseñas as ic
import manejo_datos as md


def verificar_dnie():
    # Create the main window
    window = tk.Tk()
    window.title("Verificación del DNIe")
    window.geometry("600x200")
    
    # Create a frame for better layout
    main_frame = tk.Frame(window, padx=20, pady=20)
    main_frame.pack(expand=True, fill=tk.BOTH)
    
    # Define fonts
    title_font = font.Font(family="Any", size=30, weight="bold")
    subtitle_font = font.Font(family="Any", size=10, weight="bold")
    
    # Title label
    title_label = tk.Label(main_frame, text="Verificación del DNIe", font=title_font)
    title_label.pack(pady=10)
    
    tk.Label(main_frame, text="Por favor, introduce el PIN de tu DNIe en la consola.", font=subtitle_font)
    entry_pin=tk.Entry(main_frame, show="*", width=30)
    entry_pin.pack(pady=5)
    tk.Button(main_frame, text="Verificar", command=lambda:check_dnie(entry_pin,window,main_frame,subtitle_font)).pack(pady=10)
    
    window.mainloop()

def check_dnie(entry_pin,window,main_frame,subtitle_font):
    pin=entry_pin.get()
    ini=md.manejo_datos(pin)
    # Check if DNIe is verified
    if(ini.verificar_dnie(pin)):
        status_label = tk.Label(main_frame, text="DNIe verificado correctamente.", font=subtitle_font, fg="green")
        status_label.pack(pady=10)
        window.after(2000, lambda: [window.destroy(), ic.interfaz_contrasenas(ini)])
    else:
        status_label = tk.Label(main_frame, text="No se ha podido verificar el DNIe.", font=subtitle_font, fg="red")
        status_label.pack(pady=10)
    

    
