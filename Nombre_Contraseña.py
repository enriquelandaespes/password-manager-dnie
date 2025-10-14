import pygame
import sys
import time 
import detectar_dnie_gui as detdniegui 

# Inicialización de Pygame, para la interfaz del programa
pygame.init()

# Configuración de la Ventana
WIDTH, HEIGHT = 600, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gestor de Contraseñas")

# Colores de la ventana y botones tal y como especifica la libreria 
COLOR_BG = (34, 38, 41)
COLOR_TEXT = (239, 239, 239)
COLOR_GRAY = (173, 181, 189)
COLOR_SUCCESS = (25, 135, 84)
COLOR_DANGER = (220, 53, 69)
COLOR_SUCCESS_HOVER = (21, 115, 71)
COLOR_DANGER_HOVER = (187, 45, 59) 
COLOR_BORDER = (52, 58, 64)    

# Fuentes que aparecen en la ventana
try:
    title_font = pygame.font.SysFont('Segoe UI Bold', 40)
    button_font = pygame.font.SysFont('Segoe UI', 20)
    subtitle_font = pygame.font.SysFont('Segoe UI Light', 12) 
except pygame.error:
    # En el caso en el que las fuentes no esten instaladas en el sistema utiliza fuentes por defecto
    title_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 30)
    subtitle_font = pygame.font.Font(None, 18)

# Función para dibujar el icono del candado que aparece al inicio
def draw_lock_icon(surface, position):
    """Dibuja un icono simple de candado."""
    x, y = position
    # Cuerpo del candado (rectángulo redondeado)
    pygame.draw.rect(surface, COLOR_GRAY, (x - 20, y, 40, 30), border_radius=5)
    # Arco del candado
    pygame.draw.arc(surface, COLOR_BORDER, (x - 15, y - 20, 30, 30), 0, 3.14, 5)

# Clase para la creacion de botones de la interfaz
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color if hover_color else color
        self.is_hovered = False
        self.border_width = 2 

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Dibuja el borde del botón
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, border_radius=8)
        
        # Dibuja el relleno interior del botón
        inner_rect = self.rect.inflate(-self.border_width * 2, -self.border_width * 2)
        pygame.draw.rect(surface, current_color, inner_rect, border_radius=6)
        
        text_surf = button_font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    # Comprueba si el raton esta encima del boton
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    # Comprueba si el boton ha sido clicado
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered

# Creación de elementos de la GUI con la posicion y tamaño de los botones y del texto
icon_pos = (WIDTH // 2, 60)
title_surf = title_font.render("Gestor de Contraseñas", True, COLOR_TEXT)
title_rect = title_surf.get_rect(center=(WIDTH // 2, 110))

subtitle_surf = subtitle_font.render("by Enrique Landa y Ruben Sanz", True, COLOR_GRAY)
subtitle_rect = subtitle_surf.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))

button_width, button_height = 120, 50
button_y = 170
spacing = 30

exit_button = Button(
    WIDTH // 2 - button_width - spacing // 2, button_y, button_width, button_height, 
    'Salir', COLOR_DANGER, COLOR_DANGER_HOVER
)
access_button = Button(
    WIDTH // 2 + spacing // 2, button_y, button_width, button_height, 
    'Acceder', COLOR_SUCCESS, COLOR_SUCCESS_HOVER
)
buttons = [exit_button, access_button]

# Variables para la animación de la aparicion de 1 segundo (Para que sea más estético)
start_time = time.time()
fade_duration = 1.0 

# Bucle principal que genera la ventana
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if exit_button.is_clicked(event):
            running = False
        if access_button.is_clicked(event):
            pygame.quit() 
            detdniegui.detectar_dnie() 
            sys.exit()

    mouse_pos = pygame.mouse.get_pos()
    for button in buttons:
        button.check_hover(mouse_pos)

    # Relleno de la pantalla con el color que hemos elegido
    screen.fill(COLOR_BG)
    
    # Código que genera la animacion de aparición
    elapsed_time = time.time() - start_time
    alpha = min(255, int(255 * (elapsed_time / fade_duration)))

    # Crea una superficie temporal para aplicar la transparencia
    ui_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ui_surface.fill((0, 0, 0, 0)) 

    # Dibuja todos los elementos en la superficie temporal
    draw_lock_icon(ui_surface, icon_pos)
    ui_surface.blit(title_surf, title_rect)
    ui_surface.blit(subtitle_surf, subtitle_rect)
    for button in buttons:
        button.draw(ui_surface)
        
    # Aplica la transparencia y dibuja en la pantalla principal
    ui_surface.set_alpha(alpha)
    screen.blit(ui_surface, (0, 0))

    pygame.display.flip()

# Finalizar
pygame.quit()
sys.exit()

