import tkinter as tk
from tkinter import font
import detectar_dnie_gui as detdniegui

# Create the main window
window = tk.Tk()
window.title('Simple GUI')
window.geometry('600x250')  # Set a window size for a better look

# Define a font for the title
title_font = font.Font(family="Any", size=30, weight="bold")
subtitle_font = font.Font(family="Any", size=10, weight="bold")

# Create a frame for the main content to help with centering
main_frame = tk.Frame(window)
main_frame.pack(expand=True, fill='both', padx=10, pady=10)

# Title Label
title_label = tk.Label(main_frame, text="Gestor de Contraseñas", font=title_font)
title_label.pack(pady=10)

# Frame for buttons to center them
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=20)

# Buttons
exit_button = tk.Button(button_frame, text='Salir', width=10, height=3, command=window.destroy)
exit_button.pack(side=tk.LEFT, padx=10)

access_button = tk.Button(button_frame, text='Acceder', width=10, height=3, command=lambda:[window.destroy(), detdniegui.detectar_dnie()])
access_button.pack(side=tk.LEFT, padx=10)

# Empty label for spacing, similar to sg.Text("", size=(1,2))
spacer = tk.Label(main_frame, text="", height=2)
spacer.pack()

# Subtitle Label
subtitle_label = tk.Label(main_frame, text="by Enrique Landa y Ruben Sanz", font=subtitle_font, fg="gray")
subtitle_label.pack(side=tk.BOTTOM, anchor='e') # Anchors to the bottom and east (right)

# Start the main event loop
window.mainloop()


