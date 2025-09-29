import PySimpleGUI as sg
import string
import sys
import os
ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Añade esa ruta a la lista de lugares donde Python busca módulos
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
# --- FIN DEL CÓDIGO DE IMPORTACIÓN ---
# 3. Ahora puedes importar de forma 'absoluta' desde la raíz del proyecto
from Scripts.generador_contraseñas import generar_contraseña
# --- FIN DEL CÓDIGO DE IMPORTACIÓN ---

layout = [  [sg.Text("Nombre"), sg.InputText()],
            [sg.Text("Contraseña"), sg.InputText(), sg.Button('Generar Contraseña')],
            [sg.Button('Añadir'), sg.Button('Cancelar')] ]

window = sg.Window('Simple GUI', layout)

event,values = window.read()
while (event != sg.WIN_CLOSED or event != 'Cancelar'):
    if values[0] == "" and event == 'Añadir':
        sg.popup("El nombre no puede estar vacío")
    elif event == 'Añadir' and len(values[1]) < 15:
        sg.popup("La contraseña debe tener al menos 15 caracteres")
    elif event == 'Añadir' and len(values[1]) >= 15:
        with open("Contraseñas.txt", "a") as f:
            f.write(f"{values[0]}: {values[1]}\n")
        sg.popup("Contraseña guardada correctamente")
        window.close()
        exit()
    elif event == 'Generar Contraseña':
        generar_contraseña()
    event,values = window.read()

window.close()
exit()