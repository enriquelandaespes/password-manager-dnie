import pygame
import sys
import time
import math
import Interfaz_Contraseñas as ic
import manejo_datos as md
import threading

# Global para almacenar el resultado de la verificación
verification_result = {}

def verify_dnie_thread_func(pin):
    
    #Esta función se ejecuta en un hilo separado para no bloquear la GUI.
    global verification_result
    try:
        ini = md.manejo_datos(pin)
        if ini.verificar_dnie(pin):
            verification_result = {'status': 'success', 'instance': ini}
        else:
            verification_result = {'status': 'fail'}
    except Exception as e:
        print(f"Error en el hilo de verificación: {e}")
        verification_result = {'status': 'error'}


def iniciar_verificacion():
    # --- Inicialización de Pygame ---
    pygame.init()

    # --- Configuración de la Ventana ---
    WIDTH, HEIGHT = 600, 300
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Verificación del DNIe")

    # --- Colores ---
    COLOR_BG = (34, 38, 41)
    COLOR_TEXT = (239, 239, 239)
    COLOR_SUCCESS = (25, 135, 84)
    COLOR_SUCCESS_HOVER = (21, 115, 71)
    COLOR_DANGER = (220, 53, 69)
    COLOR_INACTIVE = (108, 117, 125)
    COLOR_ACTIVE = (0, 123, 255)

    # --- Fuentes ---
    title_font = pygame.font.Font(None, 50)
    subtitle_font = pygame.font.Font(None, 24)
    input_font = pygame.font.Font(None, 32)
    status_font = pygame.font.Font(None, 22)

    # --- Función para dibujar el spinner de carga ---
    def draw_loading_spinner(surface, center_pos, num_dots=8, radius=25, dot_radius=5, angle_offset=0):
        for i in range(num_dots):
            angle = 2 * math.pi * i / num_dots + math.radians(angle_offset)
            x = center_pos[0] + int(radius * math.cos(angle))
            y = center_pos[1] + int(radius * math.sin(angle))
            
            brightness = (math.sin(math.radians(angle_offset) + 2 * math.pi * i / num_dots) + 1) / 2
            color_val = 100 + int(155 * brightness)
            color = (color_val, color_val, color_val)
            
            pygame.draw.circle(surface, color, (x, y), dot_radius)

    # --- Clase para la creacion de botones ---
    class Button:
        def __init__(self, x, y, width, height, text, color, hover_color=None):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.color = color
            self.hover_color = hover_color if hover_color else color
            self.is_hovered = False
        def draw(self, surface):
            current_color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
            text_surf = subtitle_font.render(self.text, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
        def check_hover(self, mouse_pos):
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        def is_clicked(self, event):
            return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

    # --- Creación de Elementos de la GUI ---
    title_surf = title_font.render("Verificación del DNIe", True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 50))
    subtitle_surf = subtitle_font.render("Por favor, introduce el PIN de tu DNIe:", True, COLOR_TEXT)
    subtitle_rect = subtitle_surf.get_rect(center=(WIDTH // 2, 100))
    input_rect = pygame.Rect(WIDTH // 2 - 150, 130, 300, 40)
    pin_text = ""
    input_active = False
    verify_button = Button(WIDTH // 2 - 75, 190, 150, 40, 'Verificar', COLOR_SUCCESS, COLOR_SUCCESS_HOVER)
    
    status_message = ""
    status_color = COLOR_TEXT
    transition_time = None
    dnie_instance = None
    is_verifying = False
    spinner_angle = 0
    verification_thread = None

    # --- Bucle Principal ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not is_verifying and not transition_time:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    input_active = input_rect.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_BACKSPACE:
                        pin_text = pin_text[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if pin_text:
                            is_verifying = True
                            verification_result.clear()
                            verification_thread = threading.Thread(target=verify_dnie_thread_func, args=(pin_text,))
                            verification_thread.start()
                    else:
                        pin_text += event.unicode
                
                if verify_button.is_clicked(event) and pin_text:
                    is_verifying = True
                    verification_result.clear()
                    verification_thread = threading.Thread(target=verify_dnie_thread_func, args=(pin_text,))
                    verification_thread.start()
        
        mouse_pos = pygame.mouse.get_pos()
        if not is_verifying:
            verify_button.check_hover(mouse_pos)
        
        
        if transition_time and (time.time() - transition_time) > 2:
            running = False 

        spinner_angle = (spinner_angle - 2) % 360

        screen.fill(COLOR_BG)
        screen.blit(title_surf, title_rect)

        # --- Lógica de dibujado y estado ---
        if is_verifying:
            draw_loading_spinner(screen, (WIDTH // 2, 165), angle_offset=spinner_angle)
            status_surf = status_font.render("Verificando...", True, COLOR_TEXT)
            status_rect = status_surf.get_rect(center=(WIDTH // 2, 220))
            screen.blit(status_surf, status_rect)
            
            # Comprobar si el hilo ha terminado
            if not verification_thread.is_alive():
                is_verifying = False
                result = verification_result.get('status')
                
                if result == 'success':
                    status_message = "DNIe verificado correctamente."
                    status_color = COLOR_SUCCESS
                    transition_time = time.time() # Iniciar el temporizador para la transición
                    dnie_instance = verification_result.get('instance')
                else: # Si falla
                    status_message = "PIN incorrecto o DNIe no válido."
                    status_color = COLOR_DANGER
                    pin_text = "" # Borrar el PIN para el siguiente intento
        
        elif transition_time: # Si la verificación fue exitosa, mostrar solo el mensaje
            status_surf = status_font.render(status_message, True, status_color)
            status_rect = status_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(status_surf, status_rect)
        
        else: # Pantalla de introducción de PIN 
            screen.blit(subtitle_surf, subtitle_rect)
            border_color = COLOR_ACTIVE if input_active else COLOR_INACTIVE
            pygame.draw.rect(screen, border_color, input_rect, 2, 5)
            asterisks_surf = input_font.render("*" * len(pin_text), True, COLOR_TEXT)
            screen.blit(asterisks_surf, (input_rect.x + 10, input_rect.y + 10))
            verify_button.draw(screen)
            if status_message: # Mostrar mensaje de error si existe
                status_surf = status_font.render(status_message, True, status_color)
                status_rect = status_surf.get_rect(center=(WIDTH // 2, 250))
                screen.blit(status_surf, status_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    if dnie_instance:
        ic.interfaz_contrasenas(dnie_instance)
    sys.exit()

if __name__ == "__main__":
    iniciar_verificacion()

