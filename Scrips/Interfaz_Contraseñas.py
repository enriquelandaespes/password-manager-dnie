import tkinter as tk
from tkinter import messagebox, simpledialog
import manejo_datos as md
import Nombre_Contraseña

def interfaz_contrasenas():
    root = tk.Tk()
    root.title("Gestor de Contraseñas")

    # Encabezados con grid
    tk.Label(root, text="Nombre", width=15, font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5, pady=5)
    tk.Label(root, text="Contraseña", width=20, font=("Arial", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(root, text="", width=40).grid(row=0, column=2, columnspan=3)

    lista = md.cargar_bd().get("Contrasenas", [])

    for idx, entrada in enumerate(lista, start=1):
        nombre = entrada["nombre"]
        contrasena = entrada["contrasena"]

        tk.Label(root, text=nombre, width=15).grid(row=idx, column=0, padx=5, pady=2)

        a=tk.Label(root, text="*************", width=20, anchor="center").grid(row=idx, column=1, padx=5, pady=2)

        def mostrar(pw=contrasena):
            a=tk.Label(root,text=contrasena,width=30).grid(row=idx, column=1, padx=5, pady=2)
           


        tk.Button(root, text="Mostrar", width=10, command=mostrar).grid(row=idx, column=3, padx=2)

        def editar(nm=nombre, actual=contrasena):
            nueva = simpledialog.askstring("Editar", f"Editar contraseña de {nm}:", initialvalue=actual)
            if nueva:
                md.editar_contraseña(nm, nueva)
                messagebox.showinfo("Actualizado", f"Contraseña de {nm} actualizada.")
                root.destroy()
                interfaz_contrasenas()

        tk.Button(root, text="Editar", width=10, command=editar).grid(row=idx, column=4, padx=2)

        def borrar(nm=nombre):
            if messagebox.askyesno("Borrar", f"¿Seguro que deseas borrar la contraseña de {nm}?"):
                md.eliminar_contraseña(nm)
                messagebox.showinfo("Eliminado", f"Contraseña de {nm} eliminada.")
                root.destroy()
                interfaz_contrasenas()

        tk.Button(root, text="Borrar", width=10, command=borrar).grid(row=idx, column=5, padx=2)
        def copiar():
            root.clipboard_clear()
            root.clipboard_append(contrasena)
            root.update()
            messagebox.showinfo("Copiado","Contraseña en el portapapeles")
        tk.Button(root, text="Copiar", width=10, command=copiar).grid(row=idx, column=2, padx=2)

    bottom_row = len(lista) + 1

    def nueva_accion():
        root.destroy()
        Nombre_Contraseña.Nombre_Contraseña()
        interfaz_contrasenas()

    tk.Button(root, text="Salir", width=15, command=root.destroy).grid(row=bottom_row, column=0, pady=10)
    tk.Button(root, text="Nueva Contraseña", width=15, command=nueva_accion).grid(row=bottom_row, column=1, pady=10)

    root.mainloop()

if __name__ == "__main__":
    interfaz_contrasenas()
