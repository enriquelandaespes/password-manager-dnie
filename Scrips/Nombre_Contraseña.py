import PySimpleGUI as sg
import string
import sys
import os
from Scripts.generador_contraseñas import generar_contraseña


def Nombre_Contraseña():
    layout = [
        [sg.Text("Nombre"), sg.InputText(key="-NOMBRE-")],
        [sg.Text("Contraseña"), sg.InputText(key="-PASS-"), sg.Button('Generar Contraseña')],
        [sg.Button('Añadir'), sg.Button('Cancelar')]
    ]

    window = sg.Window('Simple GUI', layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancelar'):
            break
        if event == 'Añadir':
            if values['-NOMBRE-'] == "":
                sg.popup("El nombre no puede estar vacío")
            elif len(values['-PASS-']) < 15:
                sg.popup("La contraseña debe tener al menos 15 caracteres")
            else:
                # Cambiar aquí para generar el documento JSON en lugar de txt
                md.agregar_contraseña(values['-NOMBRE-'], values['-PASS-'])
                sg.popup("Contraseña guardada correctamente")
        elif event == 'Generar Contraseña':
            # Generar contraseña y mostrarla en el campo
            nueva_pass = gc.generar_contraseña()
            window['-PASS-'].update(nueva_pass)

    window.close()
exit()

