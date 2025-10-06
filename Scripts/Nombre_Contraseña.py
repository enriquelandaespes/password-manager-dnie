import tkinter as tk
from tkinter import messagebox
import generador_contraseñas as gc
import manejo_datos as md

def Nombre_Contraseña():
    def on_add():
        nombre = entry_nombre.get()
        password = entry_pass.get()
        if nombre.strip() == "":
            messagebox.showwarning("Error", "El nombre no puede estar vacío")
        elif len(password) < 15:
            messagebox.showwarning("Error", "La contraseña debe tener al menos 15 caracteres")
        else:
            a=md.agregar_contraseña(nombre, password)
            if a:
                messagebox.showinfo("Éxito", "Contraseña guardada correctamente")
            window.destroy()

    def on_generate():
        nueva_pass = gc.generar_contraseña()
        entry_pass.delete(0, tk.END)
        entry_pass.insert(0, nueva_pass)

    def on_cancel():
        window.destroy()

    # Ventana principal
    window = tk.Tk()
    window.title("Contraseña")

    # Nombre
    tk.Label(window, text="Nombre").grid(row=0, column=0, padx=10, pady=5)
    entry_nombre = tk.Entry(window, width=30)
    entry_nombre.grid(row=0, column=1, padx=10, pady=5)

    # Contraseña
    tk.Label(window, text="Contraseña").grid(row=1, column=0, padx=10, pady=5)
    entry_pass = tk.Entry(window, width=30)
    entry_pass.grid(row=1, column=1, padx=10, pady=5)

    # Botón Generar Contraseña
    btn_generar = tk.Button(window, text="Generar Contraseña", command=on_generate)
    btn_generar.grid(row=1, column=2, padx=10, pady=5)

    # Botones Añadir y Cancelar
    btn_add = tk.Button(window, text="Añadir", command=on_add)
    btn_add.grid(row=2, column=0, padx=10, pady=10)

    btn_cancel = tk.Button(window, text="Cancelar", command=on_cancel)
    btn_cancel.grid(row=2, column=1, padx=10, pady=10)

    window.mainloop()