import tkinter as tk
from tkinter import font
import detectar_dnie as det
import verificar_dnie_gui as vdnie

def detectar_dnie():
    # Create the main window
    window = tk.Tk()
    window.title('Simple GUI')
    window.geometry('600x250')  # Set a window size for a better look

    title_font = font.Font(family="Any", size=30, weight="bold")
    subtitle_font = font.Font(family="Any", size=10, weight="bold")

    # Create a frame for the main content to help with centering
    main_frame = tk.Frame(window)
    main_frame.pack(expand=True, fill='both', padx=30, pady=10)

    # Title Label
    title_label = tk.Label(main_frame, text="Detectando DNIe...", font=title_font)
    title_label.pack(pady=10)

    # Añadir un tiempo de espera antes de mostrar el resultado
    window.after(2000, lambda: mostrar_resultado(window,main_frame,subtitle_font))
    
    spacer = tk.Label(main_frame, text="", height=2)
    spacer.pack()

    # Start the main event loop
    window.mainloop()

def mostrar_resultado(window,main_frame, subtitle_font):
    if(det.detectar_dnie()):
        status_label = tk.Label(main_frame, text="DNIe detectado correctamente.", font=subtitle_font, fg="green")
        status_label.pack(pady=10)
        window.after(2000, lambda: [window.destroy(), vdnie.verificar_dnie()])
    else:
        status_label = tk.Label(main_frame, text="No se ha detectado el DNIe.", font=subtitle_font, fg="red")
        status_label.pack(pady=10)
    spacer = tk.Label(main_frame, text="", height=2)
    spacer.pack()
