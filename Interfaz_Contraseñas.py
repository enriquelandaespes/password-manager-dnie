import pygame
import sys
import pyperclip
import threading
import time
import Nombre_Contraseña
import generador_contraseñas as gc

def copy_password_temporal(password, duration=30):
    # Copia la contraseña temporalmente en el portapaples durante una duración pequeña(30 segundos)
    # Eso si, no es del todo eficaz en windows al menos ya que se puede revisar el historial del portapaples
    pyperclip.copy(password)
    def clear_clipboard():
        time.sleep(duration)
        if pyperclip.paste() == password:
            pyperclip.copy("")
    threading.Thread(target=clear_clipboard, daemon=True).start()

# -------------------- Botón --------------------
class Button:
    def __init__(self, rect, text, color, hover_color=None, text_color=(255,255,255), font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.text_color = text_color
        self.font = font if font else pygame.font.Font(None,22)
        self.is_hovered = False

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos, surface_offset=(0,0)):
        mouse_pos_relative = (mouse_pos[0]-surface_offset[0], mouse_pos[1]-surface_offset[1])
        self.is_hovered = self.rect.collidepoint(mouse_pos_relative)

    def is_clicked(self, event, surface_offset=(0,0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos_relative = (event.pos[0]-surface_offset[0], event.pos[1]-surface_offset[1])
            return self.rect.collidepoint(mouse_pos_relative)
        return False

# -------------------- Diálogo no bloqueante --------------------
class ConfirmDialog:
    def __init__(self, text, font, screen):
        self.text = text
        self.screen = screen
        self.font = font
        self.result = None
        self.active = True

        self.box_rect = pygame.Rect(0,0,450,150)
        self.box_rect.center = screen.get_rect().center
        self.yes_button = Button((self.box_rect.centerx - 110, self.box_rect.bottom - 45,100,35),"Sí",(25,135,84))
        self.no_button = Button((self.box_rect.centerx + 10, self.box_rect.bottom - 45,100,35),"No",(220,53,69))

    def handle_event(self,event):
        if self.active:
            if self.yes_button.is_clicked(event):
                self.result = True
                self.active = False
            if self.no_button.is_clicked(event):
                self.result = False
                self.active = False

    def draw(self):
        if self.active:
            pygame.draw.rect(self.screen,(43,48,53),self.box_rect,border_radius=10)
            pygame.draw.rect(self.screen,(0,123,255),self.box_rect,2,10)
            text_surf = self.font.render(self.text, True,(255,255,255))
            self.screen.blit(text_surf,(self.box_rect.x+20, self.box_rect.y+30))
            mouse_pos = pygame.mouse.get_pos()
            for btn in [self.yes_button,self.no_button]:
                btn.check_hover(mouse_pos)
                btn.draw(self.screen)

# -------------------- Ventana de edición --------------------
def edit_entry_screen(screen, ini, entry, notify_callback):
    from Nombre_Contraseña import InputBox
    edit_running = True
    WIDTH, HEIGHT = 500, 250
    gui_rect = pygame.Rect(0,0,WIDTH,HEIGHT)
    gui_rect.center = screen.get_rect().center

    input_nombre = InputBox((gui_rect.x+150, gui_rect.y+20,250,40), pygame.font.Font(None,28), text=entry['nombre'])
    input_pass = InputBox((gui_rect.x+150, gui_rect.y+70,250,40), pygame.font.Font(None,28), text=entry['contrasena'])
    btn_aceptar = Button((gui_rect.x+150, gui_rect.y+130,120,40),"Aceptar",(25,135,84))
    btn_cancelar = Button((gui_rect.x+280, gui_rect.y+130,120,40),"Cancelar",(108,117,125))

    notif_text = ""
    notif_color = (25,135,84)
    notif_end_time = 0
    notif_font = pygame.font.Font(None,22)

    def show_local_notification(text,duration=2000,error=False):
        nonlocal notif_text, notif_end_time, notif_color
        notif_text = text
        notif_end_time = pygame.time.get_ticks() + duration
        notif_color = (220,53,69) if error else (25,135,84)

    while edit_running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: edit_running=False
            input_nombre.handle_event(event)
            input_pass.handle_event(event)
            if btn_cancelar.is_clicked(event): edit_running=False
            if btn_aceptar.is_clicked(event):
                new_name = input_nombre.text.strip()
                new_pass = input_pass.text.strip()
                
                # --- Validaciones ---
                if new_name == "":
                    show_local_notification("El nombre no puede estar vacío", error=True)
                    continue
                if len(new_pass) < 15:
                    show_local_notification("La contraseña debe tener al menos 15 caracteres", error=True)
                    continue

                # --- Lógica de Actualización Corregida ---
                nombre_ha_cambiado = (new_name != entry['nombre'])
                actualizacion_exitosa = True # Suponemos que todo irá bien

                if nombre_ha_cambiado:
                    # Si el nombre cambia, intentamos actualizarlo PRIMERO
                    if not ini.editar_nombre(entry['nombre'], new_name):
                        # Si editar_nombre devuelve False (porque ya existe), mostramos error
                        show_local_notification("Ese nombre ya existe. No se ha actualizado.", error=True)
                        actualizacion_exitosa = False
                    else:
                        # Si el cambio de nombre tuvo éxito, actualizamos la contraseña en la entrada con el NUEVO nombre
                        ini.editar_contraseña(new_name, new_pass)
                else:
                    # Si el nombre no ha cambiado, solo actualizamos la contraseña
                    ini.editar_contraseña(entry['nombre'], new_pass)

                if actualizacion_exitosa:
                    # Solo si todo fue bien, mostramos el mensaje de éxito y cerramos
                    show_local_notification("Entrada actualizada correctamente")
                    notify_callback("Entrada actualizada correctamente")
                    edit_running = False

        # Fondo de edición semitransparente
        screen.fill((34,38,41))
        font = pygame.font.Font(None,28)
        screen.blit(font.render("Nombre:",True,(255,255,255)),(gui_rect.x+20,gui_rect.y+30))
        screen.blit(font.render("Contraseña:",True,(255,255,255)),(gui_rect.x+20,gui_rect.y+80))
        input_nombre.draw(screen)
        input_pass.draw(screen)
        for btn in [btn_aceptar, btn_cancelar]:
            btn.check_hover(mouse_pos)
            btn.draw(screen)

        if pygame.time.get_ticks() < notif_end_time:
            text_surf = notif_font.render(notif_text, True,(255,255,255))
            rect = text_surf.get_rect(center=(screen.get_width()//2, gui_rect.y+HEIGHT-20))
            bg_rect = rect.inflate(20,10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((*notif_color,200))
            screen.blit(bg_surf,bg_rect)
            screen.blit(text_surf,rect)

        pygame.display.flip()

# -------------------- Interfaz principal --------------------
def interfaz_contrasenas(ini):
    pygame.init()
    WIDTH, HEIGHT = 1400,750
    screen = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Gestor de Contraseñas")

    COLOR_BG = (34,38,41)
    COLOR_HEADER = (0,123,255)
    COLOR_TEXT = (239,239,239)
    COLOR_ROW_BG = (43,48,53)
    header_font = pygame.font.Font(None,32)
    row_font = pygame.font.Font(None,24)
    button_font = pygame.font.Font(None,18)
    notification_font = pygame.font.Font(None,22)

    lista_entries = []
    scroll_y = 0
    notification_text = ""
    notification_end_time = 0
    notification_color = (25,135,84)
    dialogs = []

    def notify(text,duration=2000,error=False):
        nonlocal notification_text, notification_end_time, notification_color
        notification_text = text
        notification_end_time = pygame.time.get_ticks()+duration
        notification_color = (220,53,69) if error else (25,135,84)

    def reload_data():
        nonlocal lista_entries
        lista_entries = []
        raw_list = ini.cargar_bd().get("Contrasenas",[])
        for item in raw_list:
            lista_entries.append({
                "nombre": item["nombre"],
                "contrasena": item["contrasena"],
                "is_shown": False,
                "buttons": {}
            })

    reload_data()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running=False
            if event.type == pygame.MOUSEWHEEL: scroll_y += event.y*-20
            for dialog in dialogs:
                dialog.handle_event(event)

        screen.fill(COLOR_BG)

        # Header
        header_surf = pygame.Surface((WIDTH,40))
        header_surf.fill(COLOR_BG)
        header_surf.blit(header_font.render("Nombre", True,COLOR_HEADER),(20,10))
        header_surf.blit(header_font.render("Contraseña", True,COLOR_HEADER),(200,10))
        screen.blit(header_surf,(0,0))

        list_area_height = HEIGHT-90
        list_total_height = len(lista_entries)*45
        list_surf = pygame.Surface((WIDTH,list_total_height))
        list_surf.fill(COLOR_BG)
        list_offset = (0,50)

        for i, entry in enumerate(lista_entries):
            y_pos = i*45
            pygame.draw.rect(list_surf, COLOR_ROW_BG, (10,y_pos,WIDTH-40,40), border_radius=5)
            if list_offset[1]-scroll_y <= mouse_pos[1] <= list_offset[1]-scroll_y+40:
                if 10 <= mouse_pos[0] <= WIDTH-30:
                    pygame.draw.rect(list_surf, (60,65,70), (10,y_pos,WIDTH-40,40), border_radius=5)
            list_surf.blit(row_font.render(entry["nombre"], True, COLOR_TEXT),(20,y_pos+10))
            pass_text = entry["contrasena"] if entry["is_shown"] else "*"*12
            list_surf.blit(row_font.render(pass_text, True, COLOR_TEXT),(200,y_pos+10))

            btn_x = 650
            if not entry["buttons"]:
                entry["buttons"]["show"] = Button((btn_x,y_pos+5,70,30),"Ocultar" if entry["is_shown"] else "Mostrar",(0,123,255),font=button_font)
                entry["buttons"]["copy"] = Button((btn_x+90,y_pos+5,70,30),"Copiar",(108,117,125),font=button_font)
                entry["buttons"]["edit"] = Button((btn_x+180,y_pos+5,70,30),"Editar",(255,193,7),font=button_font)
                entry["buttons"]["gen"] = Button((btn_x+270,y_pos+5,70,30),"Generar",(50,150,255),font=button_font)
                entry["buttons"]["del"] = Button((btn_x+360,y_pos+5,70,30),"Borrar",(220,53,69),font=button_font)

            list_scroll_offset = (list_offset[0], list_offset[1]-scroll_y)
            for event in events:
                if entry["buttons"]["show"].is_clicked(event,list_scroll_offset):
                    entry["is_shown"] = not entry["is_shown"]
                    entry["buttons"]["show"].text = "Ocultar" if entry["is_shown"] else "Mostrar"
                if entry["buttons"]["copy"].is_clicked(event,list_scroll_offset):
                    copy_password_temporal(entry["contrasena"], duration=30)
                    notify("Contraseña copiada al portapapeles (30s)")
                if entry["buttons"]["del"].is_clicked(event,list_scroll_offset):
                    dialogs.append(ConfirmDialog(f"¿Seguro que quieres borrar '{entry['nombre']}'?", row_font, screen))
                if entry["buttons"]["gen"].is_clicked(event,list_scroll_offset):
                    dialogs.append(ConfirmDialog(f"¿Generar nueva contraseña para '{entry['nombre']}'?", row_font, screen))
                if entry["buttons"]["edit"].is_clicked(event,list_scroll_offset):
                    edit_entry_screen(screen, ini, entry, notify)
                    reload_data()
                    break

            for btn in entry["buttons"].values():
                btn.check_hover(mouse_pos, list_scroll_offset)
                btn.draw(list_surf)

        scroll_y = max(0,min(scroll_y,max(list_total_height-list_area_height,0)))
        screen.blit(list_surf,list_offset,(0,scroll_y,WIDTH,list_area_height))

        # Footer
        footer_offset = (0,HEIGHT-50)
        footer_surf = pygame.Surface((WIDTH,50))
        footer_surf.fill(COLOR_BG)
        salir_btn = Button((20,10,150,30),"Salir",(220,53,69))
        nueva_btn = Button((WIDTH-170,10,150,30),"Nueva Contraseña",(25,135,84))
        for event in events:
            if salir_btn.is_clicked(event, footer_offset): running=False
            if nueva_btn.is_clicked(event, footer_offset):
                Nombre_Contraseña.Nombre_Contraseña(ini,screen)
                reload_data()
        for btn in [salir_btn,nueva_btn]:
            btn.check_hover(mouse_pos, footer_offset)
            btn.draw(footer_surf)
        screen.blit(footer_surf, footer_offset)

        # Notificación global
        if pygame.time.get_ticks() < notification_end_time:
            text_surf = notification_font.render(notification_text, True,(255,255,255))
            rect = text_surf.get_rect(center=(WIDTH//2,HEIGHT-25))
            bg_rect = rect.inflate(20,10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((*notification_color,200))
            screen.blit(bg_surf,bg_rect)
            screen.blit(text_surf,rect)

        # Dibujar diálogos activos
        for dialog in dialogs:
            dialog.draw()
        # Manejar resultados de diálogos
        for dialog in dialogs[:]:
            if dialog.result is not None:
                if "borrar" in dialog.text.lower():
                    if dialog.result:
                        target_name = dialog.text.split("'")[1]
                        ini.eliminar_contraseña(target_name)
                        reload_data()
                        notify(f"Entrada '{target_name}' eliminada")
                if "generar" in dialog.text.lower():
                    if dialog.result:
                        target_name = dialog.text.split("'")[1]
                        nueva = gc.generar_contraseña()
                        ini.editar_contraseña(target_name,nueva)
                        reload_data()
                        notify(f"Nueva contraseña para '{target_name}' generada")
                dialogs.remove(dialog)

        pygame.display.flip()
    pygame.quit()
    sys.exit()

