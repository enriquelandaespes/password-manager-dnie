import pygame
import sys
import pyperclip
import Nombre_Contraseña
import generador_contraseñas as gc

# --- Clases y funciones de diálogo (sin cambios) ---
# (Button, show_confirm_dialog, edit_entry_screen...)
class Button:
    def __init__(self, rect, text, color, hover_color=None, text_color=(255, 255, 255), font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.text_color = text_color
        self.font = font if font else pygame.font.Font(None, 22)
        self.is_hovered = False
    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def check_hover(self, mouse_pos, surface_offset=(0, 0)):
        mouse_pos_relative = (mouse_pos[0] - surface_offset[0], mouse_pos[1] - surface_offset[1])
        self.is_hovered = self.rect.collidepoint(mouse_pos_relative)
    def is_clicked(self, event, surface_offset=(0, 0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos_relative = (event.pos[0] - surface_offset[0], event.pos[1] - surface_offset[1])
            return self.rect.collidepoint(mouse_pos_relative)
        return False
def show_confirm_dialog(screen, text):
    box_rect = pygame.Rect(0, 0, 450, 150)
    box_rect.center = screen.get_rect().center
    font = pygame.font.Font(None, 24)
    yes_button = Button((box_rect.centerx - 110, box_rect.bottom - 45, 100, 35), "Sí", (25, 135, 84))
    no_button = Button((box_rect.centerx + 10, box_rect.bottom - 45, 100, 35), "No", (220, 53, 69))
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if yes_button.is_clicked(event): return True
            if no_button.is_clicked(event): return False
        pygame.draw.rect(screen, (43, 48, 53), box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 123, 255), box_rect, 2, 10)
        line_surf = font.render(text, True, (255, 255, 255))
        screen.blit(line_surf, (box_rect.x + 20, box_rect.y + 30))
        for btn in [yes_button, no_button]:
            btn.check_hover(mouse_pos); btn.draw(screen)
        pygame.display.flip()
def edit_entry_screen(screen, ini, entry):
    from Nombre_Contraseña import InputBox
    edit_running = True
    input_nombre = InputBox((150, 20, 250, 40), pygame.font.Font(None, 28), text=entry['nombre'])
    input_pass = InputBox((150, 70, 250, 40), pygame.font.Font(None, 28), text=entry['contrasena'])
    btn_aceptar = Button((150, 130, 120, 40), "Aceptar", (25, 135, 84))
    btn_cancelar = Button((280, 130, 120, 40), "Cancelar", (108, 117, 125))
    while edit_running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: edit_running = False
            input_nombre.handle_event(event); input_pass.handle_event(event)
            if btn_cancelar.is_clicked(event): edit_running = False
            if btn_aceptar.is_clicked(event):
                new_name = input_nombre.text; new_pass = input_pass.text
                ini.editar_contraseña(entry['nombre'], new_pass)
                if new_name != entry['nombre']: ini.editar_nombre(entry['nombre'], new_name)
                edit_running = False
        screen.fill((34, 38, 41))
        font = pygame.font.Font(None, 28)
        screen.blit(font.render("Nombre:", True, (255,255,255)), (20, 30))
        screen.blit(font.render("Contraseña:", True, (255,255,255)), (20, 80))
        input_nombre.draw(screen); input_pass.draw(screen)
        for btn in [btn_aceptar, btn_cancelar]:
            btn.check_hover(mouse_pos); btn.draw(screen)
        pygame.display.flip()

def interfaz_contrasenas(ini):
    pygame.init()
    WIDTH, HEIGHT = 950, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gestor de Contraseñas")

    COLOR_BG = (34, 38, 41); COLOR_HEADER = (0, 123, 255); COLOR_TEXT = (239, 239, 239); COLOR_ROW_BG = (43, 48, 53)
    header_font = pygame.font.Font(None, 32); row_font = pygame.font.Font(None, 24); button_font = pygame.font.Font(None, 18); notification_font = pygame.font.Font(None, 22)
    
    lista_entries = []; scroll_y = 0

    # --- 1. Variables para la notificación ---
    notification_text = ""
    notification_end_time = 0

    def reload_data():
        nonlocal lista_entries; lista_entries = []
        raw_list = ini.cargar_bd().get("Contrasenas", [])
        for item in raw_list:
            lista_entries.append({"nombre": item["nombre"], "contrasena": item["contrasena"], "is_shown": False})
    reload_data()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEWHEEL: scroll_y += event.y * -20

        screen.fill(COLOR_BG)
        
        # --- Dibujado de la lista ---
        # ... (código de dibujado de header y lista sin cambios)
        header_surf = pygame.Surface((WIDTH, 40)); header_surf.fill(COLOR_BG)
        header_surf.blit(header_font.render("Nombre", True, COLOR_HEADER), (20, 10))
        header_surf.blit(header_font.render("Contraseña", True, COLOR_HEADER), (200, 10))
        screen.blit(header_surf, (0, 0))
        list_area_height = HEIGHT - 90
        list_total_height = len(lista_entries) * 45
        list_surf = pygame.Surface((WIDTH, list_total_height)); list_surf.fill(COLOR_BG)
        list_offset = (0, 50)
        for i, entry in enumerate(lista_entries):
            y_pos = i * 45
            pygame.draw.rect(list_surf, COLOR_ROW_BG, (10, y_pos, WIDTH - 40, 40), border_radius=5)
            list_surf.blit(row_font.render(entry["nombre"], True, COLOR_TEXT), (20, y_pos + 10))
            pass_text = entry["contrasena"] if entry["is_shown"] else "************"
            list_surf.blit(row_font.render(pass_text, True, COLOR_TEXT), (200, y_pos + 10))
            btn_x = 400
            show_text = "Ocultar" if entry["is_shown"] else "Mostrar"
            show_btn = Button((btn_x, y_pos + 5, 70, 30), show_text, (0,123,255), font=button_font)
            copy_btn = Button((btn_x + 80, y_pos + 5, 70, 30), "Copiar", (108,117,125), font=button_font)
            edit_btn = Button((btn_x + 160, y_pos + 5, 70, 30), "Editar", (255,193,7), font=button_font)
            gen_btn = Button((btn_x + 240, y_pos + 5, 70, 30), "Generar", (50,150,255), font=button_font)
            del_btn = Button((btn_x + 320, y_pos + 5, 70, 30), "Borrar", (220,53,69), font=button_font)
            row_buttons = [show_btn, copy_btn, edit_btn, gen_btn, del_btn]
            list_scroll_offset = (list_offset[0], list_offset[1] - scroll_y)
            for event in events:
                if show_btn.is_clicked(event, list_scroll_offset): entry["is_shown"] = not entry["is_shown"]
                
                # --- 2. Lógica para activar la notificación ---
                if copy_btn.is_clicked(event, list_scroll_offset): 
                    pyperclip.copy(entry["contrasena"])
                    notification_text = "Contraseña copiada al portapapeles"
                    notification_end_time = pygame.time.get_ticks() + 2000 # 2 segundos
                
                if del_btn.is_clicked(event, list_scroll_offset):
                    if show_confirm_dialog(screen, f"¿Seguro que quieres borrar la entrada '{entry['nombre']}'?"):
                        ini.eliminar_contraseña(entry["nombre"]); reload_data(); break
                if gen_btn.is_clicked(event, list_scroll_offset):
                    if show_confirm_dialog(screen, f"¿Generar nueva contraseña para '{entry['nombre']}'?"):
                        nueva = gc.generar_contraseña(); ini.editar_contraseña(entry['nombre'], nueva); reload_data(); break
                if edit_btn.is_clicked(event, list_scroll_offset):
                    edit_entry_screen(screen, ini, entry)
                    screen = pygame.display.set_mode((WIDTH, HEIGHT)); pygame.display.set_caption("Gestor de Contraseñas")
                    reload_data(); break
            
            for btn in row_buttons:
                btn.check_hover(mouse_pos, list_scroll_offset); btn.draw(list_surf)

        if list_total_height > list_area_height: scroll_y = max(0, min(scroll_y, list_total_height - list_area_height))
        else: scroll_y = 0
        screen.blit(list_surf, list_offset, (0, scroll_y, WIDTH, list_area_height))

        # --- Botones inferiores (sin cambios) ---
        footer_offset = (0, HEIGHT - 50); footer_surf = pygame.Surface((WIDTH, 50)); footer_surf.fill(COLOR_BG)
        salir_btn = Button((20, 10, 150, 30), "Salir", (220, 53, 69))
        nueva_btn = Button((WIDTH - 170, 10, 150, 30), "Nueva Contraseña", (25, 135, 84))
        for event in events:
            if salir_btn.is_clicked(event, footer_offset): running = False
            if nueva_btn.is_clicked(event, footer_offset):
                Nombre_Contraseña.Nombre_Contraseña(ini)
                screen = pygame.display.set_mode((WIDTH, HEIGHT)); pygame.display.set_caption("Gestor de Contraseñas")
                reload_data()
        for btn in [salir_btn, nueva_btn]:
            btn.check_hover(mouse_pos, footer_offset); btn.draw(footer_surf)
        screen.blit(footer_surf, footer_offset)

        # --- 3. Bloque para dibujar la notificación ---
        if pygame.time.get_ticks() < notification_end_time:
            text_surf = notification_font.render(notification_text, True, COLOR_TEXT)
            rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT - 25))
            # Fondo semi-transparente para la notificación
            bg_rect = rect.inflate(20, 10)
            bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg_surf.fill((25, 135, 84, 200)) # Verde semi-transparente
            screen.blit(bg_surf, bg_rect)
            screen.blit(text_surf, rect)

        pygame.display.flip()
    pygame.quit()
    sys.exit()
