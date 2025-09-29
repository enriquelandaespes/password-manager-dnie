import PySimpleGUI as sg
import string

def generar_contraseña():
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
            with open("Contraseñas.json", "a") as f:
                f.write(f"{values[0]}: {values[1]}\n")
                # Añadir aqui lo de introducir a la base de datos
            sg.popup("Contraseña guardada correctamente")
            window.close()
            exit()
        event,values = window.read()

    window.close()
    exit()

