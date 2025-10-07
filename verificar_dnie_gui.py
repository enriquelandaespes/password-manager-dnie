import pygame
import sys
import time
import Interfaz_Contraseñas as ic
import manejo_datos as md

# AHORA TODO EL CÓDIGO ESTÁ DENTRO DE ESTA FUNCIÓN
def iniciar_verificacion():
    # --- Inicialización de Pygame ---
    pygame.init()

    # --- Configuración de la Ventana ---
    WIDTH, HEIGHT = 600, 300
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Verificación del DNIe")

    # --- Colores, Fuentes ---
    COLOR_BG = (34, 38, 41)
    COLOR_TEXT = (239, 239, 239)
    COLOR_SUCCESS = (25, 135, 84)
    # NUEVO: Color para el hover del botón
    COLOR_SUCCESS_HOVER = (21, 115, 71)
    COLOR_DANGER = (220, 53, 69)
    COLOR_INACTIVE = (108, 117, 125)
    COLOR_ACTIVE = (0, 123, 255)

    title_font = pygame.font.Font(None, 50)
    subtitle_font = pygame.font.Font(None, 24)
    input_font = pygame.font.Font(None, 32)
    status_font = pygame.font.Font(None, 22)

    # --- MODIFICADO: Clase Button mejorada ---
    class Button:
        def __init__(self, x, y, width, height, text, color, hover_color=None):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.hover_color = hover_color if hover_color else color
            self.is_hovered = False

        def draw(self, surface):
            # Elige el color basado en si el ratón está encima
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
            
            text_surf = subtitle_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

        def check_hover(self, mouse_pos):
            # Comprueba si el ratón está sobre el botón
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        def is_clicked(self, event):
            # Comprueba si se ha hecho clic mientras el ratón estaba encima
            return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

    # --- Elementos de la UI ---
    title_surf = title_font.render("Verificación del DNIe", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))
    subtitle_surf = subtitle_font.render("Por favor, introduce el PIN de tu DNIe:", True, COLOR_TEXT)
    subtitle_rect = subtitle_surf.get_rect(center=(WIDTH // 2, 100))
    input_rect = pygame.Rect(WIDTH // 2 - 150, 130, 300, 40)
    pin_text = ""
    input_active = False
    
    # MODIFICADO: Se añade el color de hover al botón
    verify_button = Button(
        WIDTH // 2 - 75, 190, 150, 40, 'Verificar', COLOR_SUCCESS, COLOR_SUCCESS_HOVER
    )
    
    status_message = ""
    status_color = COLOR_TEXT
    success_time = None
    dnie_instance = None

    # --- Bucle Principal ---
    running = True
    while running:
        # --- Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_active = input_rect.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    pin_text = pin_text[:-1]
                else:
                    pin_text += event.unicode
            
            # La lógica de clic ahora usa el método mejorado
            if verify_button.is_clicked(event) and not success_time:
                ini = md.manejo_datos(pin_text)
                if ini.verificar_dnie(pin_text):
                    status_message = "DNIe verificado correctamente."
                    status_color = COLOR_SUCCESS
                    success_time = time.time()
                    dnie_instance = ini
                else:
                    status_message = "No se ha podido verificar el DNIe."
                    status_color = COLOR_DANGER
        
        # --- Lógica de Actualización ---
        # NUEVO: Comprueba la posición del ratón en cada fotograma
        mouse_pos = pygame.mouse.get_pos()
        verify_button.check_hover(mouse_pos)

        if success_time and (time.time() - success_time) > 2:
            running = False

        # --- Dibujado en Pantalla ---
        screen.fill(COLOR_BG)
        screen.blit(title_surf, title_rect)
        screen.blit(subtitle_surf, subtitle_rect)
        border_color = COLOR_ACTIVE if input_active else COLOR_INACTIVE
        pygame.draw.rect(screen, border_color, input_rect, 2, 5)
        asterisks_surf = input_font.render("*" * len(pin_text), True, COLOR_TEXT)
        screen.blit(asterisks_surf, (input_rect.x + 10, input_rect.y + 10))
        
        # El botón ahora se dibuja con el color correcto automáticamente
        verify_button.draw(screen)
        
        if status_message:
            status_surf = status_font.render(status_message, True, status_color)
            status_rect = status_surf.get_rect(center=(WIDTH // 2, 250))
            screen.blit(status_surf, status_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    if dnie_instance:
        ic.interfaz_contrasenas(dnie_instance)
    sys.exit()

# Esta línea asegura que el código solo se ejecute si abres este archivo directamente
if __name__ == "__main__":
    iniciar_verificacion()
