import pygame
import generador_contraseñas as gc

class InputBox:
    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect)
        self.color_inactive = (108,117,125)
        self.color_active = (0,123,255)
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.active = False
    # Manejo de eventos
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    #Dibuja la pantalla principal
    def draw(self, screen):
        pygame.draw.rect(screen,self.color,self.rect,2,5)
        text_surface = self.font.render(self.text, True, (239,239,239))
        screen.blit(text_surface,(self.rect.x+10,self.rect.y+10))
# Crea los botones, como en el resto de interfaces
class Button:
    def __init__(self, rect, text, color, hover_color=None, font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color or color
        self.font = font or pygame.font.Font(None, 24)
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface,color,self.rect,border_radius=5)
        text_surf = self.font.render(self.text, True, (255,255,255))
        rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            return self.rect.collidepoint(event.pos)
        return False
# Mensajes
def draw_message_box(screen, text):
    box = pygame.Rect(0,0,400,150)
    box.center = screen.get_rect().center
    font = pygame.font.Font(None,24)
    pygame.draw.rect(screen,(43,48,53),box,border_radius=10)
    pygame.draw.rect(screen,(0,123,255),box,2,10)
    surf = font.render(text,True,(255,255,255))
    rect = surf.get_rect(center=(box.centerx, box.centery-20))
    screen.blit(surf, rect)
    return Button((box.centerx-50, box.bottom-45, 100, 35),"Aceptar",(0,123,255))
# Pantalla de generación de nueva contraseña
def Nombre_Contraseña(ini, screen):
   
    WIDTH, HEIGHT = screen.get_size()
    COLOR_BG = (34,38,41)
    COLOR_TEXT = (239,239,239)
    main_font = pygame.font.Font(None,28)

    input_nombre = InputBox((WIDTH//2-125, HEIGHT//2-60,250,40), main_font)
    input_pass = InputBox((WIDTH//2-125, HEIGHT//2-10,250,40), main_font)
    input_boxes = [input_nombre,input_pass]
    btn_generar = Button((WIDTH//2+150, HEIGHT//2-10,120,40),"Generar",(0,123,255))
    btn_add = Button((WIDTH//2-125, HEIGHT//2+50,120,40),"Añadir",(25,135,84))
    btn_cancel = Button((WIDTH//2+5, HEIGHT//2+50,120,40),"Cancelar",(108,117,125))
    buttons = [btn_generar, btn_add, btn_cancel]

    dialog_active = False
    dialog_text = ""
    close_on_success = False

    running = True
    # Maneja los diferentes eventos mientras está activo
    while running:
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: return
            if dialog_active:
                ok_rect = pygame.Rect(0,0,100,35)
                ok_rect.center = (WIDTH//2, HEIGHT//2 + 47)
                if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                    if ok_rect.collidepoint(event.pos):
                        dialog_active=False
                        if close_on_success:
                            return
            else:
                for box in input_boxes:
                    box.handle_event(event)
                if btn_cancel.is_clicked(event): return
                if btn_generar.is_clicked(event):
                    input_pass.text = gc.generar_contraseña()
                if btn_add.is_clicked(event):
                    nombre = input_nombre.text.strip()
                    password = input_pass.text
                    if not nombre:
                        dialog_active = True
                        dialog_text = "Error: Nombre vacío"
                    elif len(password)<15:
                        dialog_active = True
                        dialog_text = "Error: Contraseña < 15 caracteres"
                    else:
                        if ini.agregar_contraseña(nombre,password):
                            dialog_active=True
                            dialog_text="Éxito: Contraseña guardada"
                            close_on_success=True
                        else:
                            dialog_active=True
                            dialog_text=f"Error: Entrada '{nombre}' ya existe"

        screen.fill(COLOR_BG)
        screen.blit(main_font.render("Nombre:",True,COLOR_TEXT),(WIDTH//2-250, HEIGHT//2-50))
        screen.blit(main_font.render("Contraseña:",True,COLOR_TEXT),(WIDTH//2-250, HEIGHT//2))
        for box in input_boxes: box.draw(screen)
        for btn in buttons:
            btn.check_hover(mouse_pos)
            btn.draw(screen)
        if dialog_active:
            ok_button = draw_message_box(screen, dialog_text)
            ok_button.check_hover(mouse_pos)
            ok_button.draw(screen)
        pygame.display.flip()
