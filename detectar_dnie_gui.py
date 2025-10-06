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

    # --- Fuentes ---
    title_font = pygame.font.Font(None, 50)
    subtitle_font = pygame.font.Font(None, 24)

    # --- Variables de estado ---
    start_time = time.time()
    detection_result = None # None: detectando, True: éxito, False: fallo
    status_message = "Detectando DNIe..."
    status_color = COLOR_TEXT
    transition_time = None

    # --- Bucle Principal ---
    running = True
    while running:
        # --- Manejo de Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Lógica de Detección y Tiempos ---
        current_time = time.time()

        # Fase 1: Esperar 2 segundos antes de detectar
        if detection_result is None and (current_time - start_time) > 2:
            if det.detectar_dnie():
                detection_result = True
                status_message = "DNIe detectado correctamente."
                status_color = COLOR_SUCCESS
                transition_time = current_time # Iniciar temporizador para la transición
            else:
                detection_result = False
                status_message = "No se ha detectado el DNIe."
                status_color = COLOR_DANGER

        # Fase 2: Si la detección fue exitosa, esperar otros 2 segundos antes de cambiar de ventana
        if transition_time and (current_time - transition_time) > 2:
            running = False # Salir del bucle

        # --- Dibujado en Pantalla ---
        screen.fill(COLOR_BG)

        # Renderizar y centrar el texto de estado
        if detection_result is None: # Si aún estamos detectando
            text_surf = title_font.render(status_message, True, status_color)
        else: # Si ya tenemos un resultado
            text_surf = subtitle_font.render(status_message, True, status_color)
        
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text_surf, text_rect)

        # Actualizar la pantalla
        pygame.display.flip()

    # --- Salida Limpia y Transición ---
    pygame.quit()

    # Si la detección fue exitosa, llama a la siguiente ventana de verificación
    if detection_result:
        # Asumiendo que el otro script tiene la función 'iniciar_verificacion'
        vdnie.iniciar_verificacion() 
    
    sys.exit()

# Esta línea permite ejecutar el script directamente para probarlo
if __name__ == "__main__":
    detectar_dnie()
