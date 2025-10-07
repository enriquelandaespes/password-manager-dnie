import pygame
import sys
import time
import detectar_dnie as det
import verificar_dnie_gui as vdnie

# Se mantiene el nombre original de la función para compatibilidad
def detectar_dnie():
    # --- Inicialización de Pygame ---
    pygame.init()

    # --- Configuración de la Ventana ---
    WIDTH, HEIGHT = 600, 250
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Detectando DNIe")

    # --- Colores ---
    COLOR_BG = (34, 38, 41)
    COLOR_TEXT = (239, 239, 239)
    COLOR_SUCCESS = (25, 135, 84)
    COLOR_DANGER = (220, 53, 69)
    COLOR_INACTIVE = (108, 117, 125) 

    # --- Fuentes ---
    title_font = pygame.font.Font(None, 50)
    subtitle_font = pygame.font.Font(None, 24)

    # --- Configuración de la Barra de Carga ---
    BAR_WIDTH, BAR_HEIGHT = 300, 15
    bar_x = (WIDTH - BAR_WIDTH) // 2
    bar_y = HEIGHT // 2 + 40
    bar_bg_rect = pygame.Rect(bar_x, bar_y, BAR_WIDTH, BAR_HEIGHT)

    # --- MODIFICADO: Constante para el tiempo de espera ---
    WAIT_SECONDS = 1.0 # Reducido de 2.0 a 1.0

    # --- Variables de estado ---
    start_time = time.time()
    detection_result = None
    status_message = "Detectando DNIe..."
    status_color = COLOR_TEXT
    transition_time = None

    # --- Bucle Principal ---
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        # MODIFICADO: Fase 1 ahora usa WAIT_SECONDS
        if detection_result is None and (current_time - start_time) > WAIT_SECONDS:
            if det.detectar_dnie():
                detection_result = True
                status_message = "DNIe detectado correctamente."
                status_color = COLOR_SUCCESS
                transition_time = current_time
            else:
                detection_result = False
                status_message = "No se ha detectado el DNIe."
                status_color = COLOR_DANGER

        # MODIFICADO: Fase 2 ahora usa WAIT_SECONDS
        if transition_time and (current_time - transition_time) > WAIT_SECONDS:
            running = False

        screen.fill(COLOR_BG)
        text_surf = title_font.render(status_message, True, status_color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        screen.blit(text_surf, text_rect)

        pygame.draw.rect(screen, COLOR_INACTIVE, bar_bg_rect, 2, border_radius=5)

        if detection_result is None:
            # MODIFICADO: La animación ahora dura WAIT_SECONDS
            elapsed = current_time - start_time
            progress = min(elapsed / WAIT_SECONDS, 1.0)
            
            current_bar_width = int(BAR_WIDTH * progress)
            bar_fill_rect = pygame.Rect(bar_x, bar_y, current_bar_width, BAR_HEIGHT)
            pygame.draw.rect(screen, COLOR_SUCCESS, bar_fill_rect, border_radius=5)
        else:
            final_bar_color = COLOR_SUCCESS if detection_result else COLOR_DANGER
            pygame.draw.rect(screen, final_bar_color, bar_bg_rect, border_radius=5)
        
        pygame.display.flip()

    pygame.quit()

    if detection_result:
        vdnie.iniciar_verificacion() 
    
    sys.exit()

if __name__ == "__main__":
    detectar_dnie()
