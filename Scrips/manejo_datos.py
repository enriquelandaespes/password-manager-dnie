import json
# Falta cifrarlo y descifrarlo
# Nombre del archivo JSON
import os
from tkinter import messagebox

ARCHIVO = os.path.join(os.path.dirname(__file__), "Database.json")

    

# Cargar la base de datos (si existe) o crear nueva
def cargar_bd():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"Contrasenas": []}  # si no existe, empieza vacío

# Guardar la base de datos
def guardar_bd(db):
    with open(ARCHIVO, "w") as f:
        json.dump(db, f, indent=4)

# Agregar una contraseña
def agregar_contraseña(nombre, contraseña):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            messagebox.showinfo("Repetido", f"{nombre} ya existe")
            return False
    else :    
        db["Contrasenas"].append({"nombre": nombre, "contrasena": contraseña})
        guardar_bd(db)
        return True
    
# Buscar un usuario por nombre
def buscar_contraseña(nombre):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            return u
    return None
def eliminar_contraseña(nombre):
    db = cargar_bd()
    db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
    guardar_bd(db)
def editar_contraseña(nombre,nueva):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            u["contrasena"]=nueva
    messagebox.showinfo("Actualizado", f"Contraseña actualizada a {nueva}.")
    if len(nueva) < 15:
        messagebox.showwarning("Cuidado", "La contraseña es insegura")
    guardar_bd(db)

def editar_nombre(nombre,nueva,cont):
    db = cargar_bd()
    a=True
    for u in db["Contrasenas"]:
        if u["nombre"] == nueva:
            messagebox.showinfo("Error","El nombre no se ha acualizado(ya existe)")
            a=False
    if(a):
        for u in db["Contrasenas"]:
            if u["nombre"]==nombre:
                u["nombre"]=nueva
                messagebox.showinfo("Actualizado", f"{nombre} ahora es {nueva}.")
    guardar_bd(db)




   
   


    