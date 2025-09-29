import json

# Nombre del archivo JSON
ARCHIVO = "Database.json"

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
    db["Contrasenas"].append({"nombre": nombre, "contrasena": contraseña})
    guardar_bd(db)

# Listar usuarios
def listar_usuarios():
    db = cargar_bd()
    for u in db["Contrasenas"]:
        print(f"👤 {u['nombre']} - 🔑 {u['contrasena']}")

# Buscar un usuario por nombre
def buscar_usuario(nombre):
    db = cargar_bd()
    for u in db["Contrasenas"]:
        if u["nombre"] == nombre:
            return u
    return None
def eliminar_usuario(nombre):
    db = cargar_bd()
    db["Contrasenas"] = [u for u in db["Contrasenas"] if u["nombre"] != nombre]
    guardar_bd(db)
