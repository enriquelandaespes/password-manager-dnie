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

    # --- Colores, Fuentes y Clase Button (sin cambios) ---
    COLOR_BG = (34, 38, 41)
    COLOR_TEXT = (239, 239, 239)
    COLOR_SUCCESS = (25, 135, 84)
    COLOR_DANGER = (220, 53, 69)
    COLOR_INACTIVE = (108, 117, 125)
    COLOR_ACTIVE = (0, 123, 255)

    title_font = pygame.font.Font(None, 50)
    subtitle_font = pygame.font.Font(None, 24)
    input_font = pygame.font.Font(None, 32)
    status_font = pygame.font.Font(None, 22)

    class Button:
        def __init__(self, x, y, width, height, text, color):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color

        def draw(self, surface):
            pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
            text_surf = subtitle_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

        def is_clicked(self, event):
            return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    # --- Elementos de la UI ---
    title_surf = title_font.render("Verificación del DNIe", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))
    subtitle_surf = subtitle_font.render("Por favor, introduce el PIN de tu DNIe:", True, COLOR_TEXT)
    subtitle_rect = subtitle_surf.get_rect(center=(WIDTH // 2, 100))
    input_rect = pygame.Rect(WIDTH // 2 - 150, 130, 300, 40)
    pin_text = ""
    input_active = False
    verify_button = Button(WIDTH // 2 - 75, 190, 150, 40, 'Verificar', COLOR_SUCCESS)
    status_message = ""
    status_color = COLOR_TEXT
    success_time = None
    dnie_instance = None

    # --- Bucle Principal ---
    running = True
    while running:
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
        
        if success_time and (time.time() - success_time) > 2:
            running = False

        screen.fill(COLOR_BG)
        screen.blit(title_surf, title_rect)
        screen.blit(subtitle_surf, subtitle_rect)
        border_color = COLOR_ACTIVE if input_active else COLOR_INACTIVE
        pygame.draw.rect(screen, border_color, input_rect, 2, 5)
        asterisks_surf = input_font.render("*" * len(pin_text), True, COLOR_TEXT)
        screen.blit(asterisks_surf, (input_rect.x + 10, input_rect.y + 10))
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
