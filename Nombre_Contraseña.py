import pygame
import sys
import generador_contraseñas as gc

# --- Clases de UI (InputBox, Button - sin cambios) ---
class InputBox:
    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect); self.color_inactive = (108, 117, 125); self.color_active = (0, 123, 255); self.color = self.color_inactive
        self.text = text; self.font = font; self.active = False
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
            else: self.text += event.unicode
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2, 5); text_surface = self.font.render(self.text, True, (239, 239, 239))
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
class Button:
    def __init__(self, rect, text, color, hover_color=None, font=None):
        self.rect = pygame.Rect(rect); self.text = text; self.color = color; self.hover_color = hover_color or color
        self.font = font or pygame.font.Font(None, 24); self.is_hovered = False
    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        text_surf = self.font.render(self.text, True, (255, 255, 255)); text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def check_hover(self, mouse_pos): self.is_hovered = self.rect.collidepoint(mouse_pos)
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: return self.rect.collidepoint(event.pos)
        return False

# --- FUNCIÓN DE DIBUJADO DE DIÁLOGO (YA NO TIENE SU PROPIO BUCLE) ---
def draw_message_box(screen, text):
    box_rect = pygame.Rect(0, 0, 400, 150)
    box_rect.center = screen.get_rect().center
    font = pygame.font.Font(None, 24)
    
    # Dibujado del diálogo
    pygame.draw.rect(screen, (43, 48, 53), box_rect, border_radius=10)
    pygame.draw.rect(screen, (0, 123, 255), box_rect, 2, 10)
    
    # Texto del mensaje
    line_surf = font.render(text, True, (255, 255, 255))
    text_rect = line_surf.get_rect(center=(box_rect.centerx, box_rect.centery - 20))
    screen.blit(line_surf, text_rect)
    
    # Devuelve el botón para que el bucle principal pueda manejar su clic
    return Button((box_rect.centerx - 50, box_rect.bottom - 45, 100, 35), "Aceptar", (0, 123, 255))

def Nombre_Contraseña(ini):
    pygame.init()
    WIDTH, HEIGHT = 550, 200
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Añadir Nueva Contraseña")
    
    COLOR_BG = (34, 38, 41); COLOR_TEXT = (239, 239, 239); main_font = pygame.font.Font(None, 28)

    input_nombre = InputBox((150, 20, 250, 40), main_font)
    input_pass = InputBox((150, 70, 250, 40), main_font)
    input_boxes = [input_nombre, input_pass]
    btn_generar = Button((410, 70, 120, 40), "Generar", (0, 123, 255))
    btn_add = Button((150, 130, 120, 40), "Añadir", (25, 135, 84))
    btn_cancel = Button((280, 130, 120, 40), "Cancelar", (108, 117, 125))
    buttons = [btn_generar, btn_add, btn_cancel]

    # --- Variables de estado para el diálogo ---
    dialog_active = False
    dialog_text = ""
    close_on_success = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # --- Lógica de eventos separada por estado ---
            if dialog_active:
                # Si el diálogo está activo, solo nos importa el clic en su botón "Aceptar"
                ok_button_rect = pygame.Rect(0,0,100,35)
                ok_button_rect.center = (screen.get_rect().centerx, screen.get_rect().centery + 47)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ok_button_rect.collidepoint(event.pos):
                        dialog_active = False # Cierra el diálogo
                        if close_on_success:
                            running = False # Cierra la ventana principal si la operación fue exitosa
            else:
                # Si el diálogo no está activo, manejamos los eventos del formulario principal
                for box in input_boxes: box.handle_event(event)
                if btn_cancel.is_clicked(event): running = False
                if btn_generar.is_clicked(event): input_pass.text = gc.generar_contraseña()
                if btn_add.is_clicked(event):
                    nombre = input_nombre.text; password = input_pass.text
                    if not nombre.strip():
                        dialog_active = True; dialog_text = "Error: El nombre no puede estar vacío."
                    elif len(password) < 15:
                        dialog_active = True; dialog_text = "Error: La contraseña debe tener al menos 15 caracteres."
                    else:
                        if ini.agregar_contraseña(nombre, password):
                            dialog_active = True; dialog_text = "Éxito: Contraseña guardada correctamente."
                            close_on_success = True # Marcar para cerrar después de hacer clic en OK
                        else:
                            dialog_active = True; dialog_text = f"Error: Ya existe una entrada con el nombre '{nombre}'."

        # --- Dibujado ---
        screen.fill(COLOR_BG)
        
        # Dibujar el formulario principal
        screen.blit(main_font.render("Nombre:", True, COLOR_TEXT), (20, 30))
        screen.blit(main_font.render("Contraseña:", True, COLOR_TEXT), (20, 80))
        for box in input_boxes: box.draw(screen)
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        # Si el diálogo está activo, dibujarlo encima de todo
        if dialog_active:
            ok_button = draw_message_box(screen, dialog_text)
            ok_button.check_hover(mouse_pos)
            ok_button.draw(screen)

        pygame.display.flip()
