import pygame
import sys
# Suponiendo que este archivo sigue existiendo para ser llamado
import detectar_dnie_gui as detdniegui 

# --- Inicialización de Pygame ---
pygame.init()

# --- Configuración de la Ventana ---
WIDTH, HEIGHT = 600, 250
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gestor de Contraseñas")

# --- Colores (estilo "superhero") ---
COLOR_BG = (34, 38, 41)         # Fondo oscuro
COLOR_TEXT = (239, 239, 239)    # Texto principal (casi blanco)
COLOR_GRAY = (173, 181, 189)    # Texto secundario (gris)
COLOR_SUCCESS = (25, 135, 84)   # Botón Acceder (verde)
COLOR_DANGER = (220, 53, 69)    # Botón Salir (rojo)
COLOR_SUCCESS_HOVER = (21, 115, 71) # Verde más oscuro al pasar el ratón

# --- Fuentes ---
try:
    # Intenta usar una fuente moderna si está disponible
    title_font = pygame.font.SysFont('Segoe UI Bold', 40)
    button_font = pygame.font.SysFont('Segoe UI', 20)
    subtitle_font = pygame.font.SysFont('Segoe UI', 12)
except pygame.error:
    # Usa la fuente por defecto si la otra no se encuentra
    title_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 30)
    subtitle_font = pygame.font.Font(None, 18)

# --- Clase para los Botones ---
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
        
        # Dibuja el texto centrado en el botón
        text_surf = button_font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

# --- Creación de Elementos de la UI ---
# Título y subtítulo
title_surf = title_font.render("Gestor de Contraseñas", True, COLOR_TEXT)
title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3))

subtitle_surf = subtitle_font.render("by Enrique Landa y Ruben Sanz", True, COLOR_GRAY)
subtitle_rect = subtitle_surf.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))

# Botones
button_width, button_height = 120, 50
button_y = HEIGHT // 2 + 20
spacing = 30

exit_button = Button(
    WIDTH // 2 - button_width - spacing // 2, 
    button_y, 
    button_width, 
    button_height, 
    'Salir', 
    COLOR_DANGER
)

access_button = Button(
    WIDTH // 2 + spacing // 2, 
    button_y, 
    button_width, 
    button_height, 
    'Acceder', 
    COLOR_SUCCESS, 
    COLOR_SUCCESS_HOVER
)

buttons = [exit_button, access_button]

# --- Bucle Principal del "Juego" ---
running = True
while running:
    # --- Manejo de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Comprobar si un botón ha sido pulsado
        if exit_button.is_clicked(event):
            running = False # Salir del bucle
        
        if access_button.is_clicked(event):
            # Cierra la ventana de Pygame y lanza la siguiente GUI de ttkbootstrap
            pygame.quit() 
            detdniegui.detectar_dnie() 
            # Como la siguiente ventana no es Pygame, salimos del script
            sys.exit()

    # --- Lógica de Actualización ---
    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.check_hover(mouse_pos)

    # --- Dibujado en Pantalla ---
    screen.fill(COLOR_BG) # Limpia la pantalla con el color de fondo

    # Dibuja el texto
    screen.blit(title_surf, title_rect)
    screen.blit(subtitle_surf, subtitle_rect)

    # Dibuja los botones
    for button in buttons:
        button.draw(screen)

    # Actualiza la pantalla para mostrar lo que se ha dibujado
    pygame.display.flip()

# --- Salida Limpia ---
pygame.quit()
sys.exit()
