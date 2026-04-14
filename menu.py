import sys
import math
import pygame as pg
import cv2

from settings import RES, WIDTH, HEIGHT, resource_path


class Menu:
    def __init__(self, game):
        # Guarda referencias principais do jogo para desenhar e controlar tempo.
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        # Carrega a imagem de fundo do menu principal.
        self.background = pg.transform.scale(
            pg.image.load(resource_path('resources', 'menu', 'menu.png')).convert(), RES
        )
        # Carrega a imagem do botao de iniciar e define sua posicao inicial.
        self.button_image = pg.image.load(resource_path('resources', 'hub', 'iniciar.png')).convert_alpha()
        self.button_center = (WIDTH // 2, HEIGHT - 140)
        self.button_rect = self.button_image.get_rect(center=self.button_center)
        # Carrega o fundo e as opcoes do menu de escolhas.
        self.selection_background = pg.transform.scale(
            pg.image.load(resource_path('resources', 'hub', 'menu-jhoon.png')).convert(), RES
        )
        # Escala base do menu de escolhas.
        # Altere estes valores se quiser ajustar visualmente depois.
        self.selection_button_width = 360
        self.selection_button_centers = {
            'new_game': (WIDTH // 2, HEIGHT // 2 - 70),
            'load_game': (WIDTH // 2, HEIGHT // 2 + 105),
            'quit': (WIDTH // 2, HEIGHT // 2 + 320),
        }
        self.selection_buttons = [
            {
                'id': 'new_game',
                'image': self.scale_menu_button_image(
                    pg.image.load(resource_path('resources', 'hub', 'new-game.png')).convert_alpha()
                ),
                'center': self.selection_button_centers['new_game'],
            },
            {
                'id': 'load_game',
                'image': self.scale_menu_button_image(
                    pg.image.load(resource_path('resources', 'hub', 'load-game.png')).convert_alpha()
                ),
                'center': self.selection_button_centers['load_game'],
            },
            {
                'id': 'quit',
                'image': self.scale_menu_button_image(
                    pg.image.load(resource_path('resources', 'hub', 'Quit.png')).convert_alpha()
                ),
                'center': self.selection_button_centers['quit'],
            },
        ]
        # Define caminhos dos arquivos de audio e video usados na introducao.
        self.sound_path = resource_path('resources', 'menu', 'sound_menu.mp3')
        self.intro_video_path = resource_path('resources', 'sound', 'inicio.mp4')
        # Inicializa as fontes usadas nas telas do menu.
        self.story_title_font = pg.font.SysFont('georgia', 42, bold=True)
        self.story_font = pg.font.SysFont('georgia', 28)
        self.story_hint_font = pg.font.SysFont('couriernew', 24, bold=True)
        self.pause_title_font = pg.font.SysFont('couriernew', 42, bold=True)
        self.pause_font = pg.font.SysFont('couriernew', 28, bold=True)
        self.selection_hint_font = pg.font.SysFont('couriernew', 24, bold=True)
        self.selection_feedback_until = 0
        self.selection_feedback = ''
        self.pause_feedback_until = 0
        self.pause_feedback = ''
        # Texto exibido na tela de prologo.
        self.story_lines = [
            'Ao cair da tarde, um jovem viajante chegava a Braganca em um onibus quase vazio,',
            'cansado da estrada e sem imaginar que aquela seria a ultima noite de sua vida comum.',
            '',
            'Assim que desceu na parada, uma neblina escura tomou a rua em silencio,',
            'engolindo luzes, sons e qualquer sinal de saida.',
            '',
            'Quando a neblina finalmente se desfez, ele ja nao estava mais na cidade.',
            'Despertou sozinho dentro de um labirinto sombrio, cercado por criaturas',
            'que se moviam nas sombras como se sempre tivessem esperado por sua chegada.',
        ]
        # Define um painel quadrado e os botoes internos do menu de pausa.
        self.pause_panel_rect = pg.Rect(0, 0, 470, 470)
        self.pause_panel_rect.center = (WIDTH // 2, HEIGHT // 2)
        button_width = 300
        button_height = 68
        center_x = self.pause_panel_rect.centerx - button_width // 2
        first_button_y = self.pause_panel_rect.y + 150
        button_gap = 90
        self.resume_rect = pg.Rect(center_x, first_button_y, button_width, button_height)
        self.save_game_rect = pg.Rect(center_x, first_button_y + button_gap, button_width, button_height)
        self.quit_rect = pg.Rect(center_x, first_button_y + button_gap * 2, button_width, button_height)

    def scale_menu_button_image(self, image):
        # Normaliza os botoes do menu secundario pela mesma largura visual.
        target_width = self.selection_button_width
        scale = target_width / image.get_width()
        target_height = max(1, int(image.get_height() * scale))
        return pg.transform.smoothscale(image, (target_width, target_height))

    def draw(self):
        # Desenha o fundo do menu principal.
        self.screen.blit(self.background, (0, 0))

        # Verifica se o mouse esta sobre o botao e aplica um pequeno efeito de destaque.
        mouse_pos = pg.mouse.get_pos()
        hovered = self.button_rect.collidepoint(mouse_pos)
        animation_time = pg.time.get_ticks() * 0.01
        hover_scale = 1.08 + 0.03 * math.sin(animation_time) if hovered else 1

        # Redimensiona o botao para criar a animacao de hover.
        button_width = int(self.button_image.get_width() * hover_scale)
        button_height = int(self.button_image.get_height() * hover_scale)
        button_surface = pg.transform.smoothscale(self.button_image, (button_width, button_height))
        self.button_rect = button_surface.get_rect(center=self.button_center)

        self.screen.blit(button_surface, self.button_rect)

        # Atualiza a tela com o menu desenhado.
        pg.display.flip()

    def draw_menu_image_button(self, image, center, hovered):
        # Aplica um leve efeito de profundidade quando o mouse passa sobre o botao.
        animation_time = pg.time.get_ticks() * 0.01
        scale = 1.08 + 0.03 * math.sin(animation_time) if hovered else 1.0
        offset_y = -8 if hovered else 0
        width = int(image.get_width() * scale)
        height = int(image.get_height() * scale)
        button_surface = pg.transform.smoothscale(image, (width, height))
        button_rect = button_surface.get_rect(center=(center[0], center[1] + offset_y))

        shadow_surface = button_surface.copy()
        shadow_surface.fill((0, 0, 0, 110), special_flags=pg.BLEND_RGBA_MULT)
        self.screen.blit(shadow_surface, button_rect.move(0, 12))
        self.screen.blit(button_surface, button_rect)
        return button_rect

    def draw_selection_menu(self):
        # Desenha a segunda tela de menu com as opcoes principais.
        self.screen.blit(self.selection_background, (0, 0))
        mouse_pos = pg.mouse.get_pos()

        for button in self.selection_buttons:
            hovered = pg.Rect(button['center'][0] - 1, button['center'][1] - 1, 2, 2).collidepoint(mouse_pos)
            if 'rect' in button:
                hovered = button['rect'].collidepoint(mouse_pos)
            button['rect'] = self.draw_menu_image_button(button['image'], button['center'], hovered)

        if self.selection_feedback and pg.time.get_ticks() < self.selection_feedback_until:
            label = self.selection_hint_font.render(self.selection_feedback, True, (255, 241, 198))
            box = label.get_rect(center=(WIDTH // 2, HEIGHT - 90)).inflate(30, 16)
            pg.draw.rect(self.screen, (18, 18, 22), box, border_radius=12)
            pg.draw.rect(self.screen, (255, 215, 128), box, 2, border_radius=12)
            self.screen.blit(label, label.get_rect(center=box.center))

        pg.display.flip()

    def run_selection_menu(self):
        # Loop do menu de escolhas entre a tela inicial e o inicio da partida.
        while True:
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.selection_buttons:
                        if button.get('rect') and button['rect'].collidepoint(event.pos):
                            if button['id'] == 'new_game':
                                return 'new_game'
                            if button['id'] == 'load_game':
                                if self.game.has_save_game():
                                    return 'load_game'
                                self.selection_feedback = 'Nenhum save encontrado'
                                self.selection_feedback_until = pg.time.get_ticks() + 1600
                            if button['id'] == 'quit':
                                pg.quit()
                                sys.exit()

            self.draw_selection_menu()
            self.clock.tick(60)

    def start_game(self):
        # Encerra a musica do menu e prepara o jogo para capturar mouse e teclado.
        pg.mixer.music.stop()
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def handle_common_event(self, event):
        # Trata eventos comuns de saida usados nas telas do menu.
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()

    def draw_story(self):
        # Desenha a tela do prologo sobre o fundo do menu.
        self.screen.blit(self.background, (0, 0))

        # Aplica uma camada escura para melhorar a leitura do texto.
        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((6, 8, 12, 215))
        self.screen.blit(overlay, (0, 0))

        # Desenha o titulo do prologo.
        title_surface = self.story_title_font.render('Prologo', True, (245, 237, 214))
        title_pos = (WIDTH // 2 - title_surface.get_width() // 2, 110)
        self.screen.blit(title_surface, title_pos)

        # Escreve cada linha da historia centralizada na tela.
        y = 210
        for line in self.story_lines:
            if line:
                line_surface = self.story_font.render(line, True, (232, 232, 232))
                line_pos = (WIDTH // 2 - line_surface.get_width() // 2, y)
                self.screen.blit(line_surface, line_pos)
            y += 42

        # Mostra a instrucao para o usuario continuar.
        hint_surface = self.story_hint_font.render('Clique ou pressione ENTER para continuar', True, (255, 255, 255))
        hint_pos = (WIDTH // 2 - hint_surface.get_width() // 2, HEIGHT - 110)
        self.screen.blit(hint_surface, hint_pos)
        pg.display.flip()

    def draw_intro_transition(self):
        # Faz uma transicao de fade para preto antes de iniciar o jogo.
        start_time = pg.time.get_ticks()
        duration = 3000
        while True:
            elapsed = pg.time.get_ticks() - start_time
            progress = min(1.0, elapsed / duration)

            # Escurece gradualmente a tela conforme o tempo passa.
            self.screen.fill((0, 0, 0))
            fade_surface = pg.Surface(RES, pg.SRCALPHA)
            fade_surface.fill((0, 0, 0, int(progress * 255)))
            self.screen.blit(fade_surface, (0, 0))
            pg.display.flip()

            # Continua tratando eventos para permitir fechamento correto durante a transicao.
            for event in pg.event.get():
                self.handle_common_event(event)

            if progress >= 1.0:
                return
            self.clock.tick(60)

    def run_intro_video(self):
        # Reproduz o video de introducao usando OpenCV.
        pg.mixer.music.stop()
        capture = cv2.VideoCapture(self.intro_video_path)
        fps = capture.get(cv2.CAP_PROP_FPS) or 30
        frame_delay = max(1, int(1000 / fps))
        skip_video = False

        while capture.isOpened():
            # Permite sair ou pular o video.
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    skip_video = True
                    break

            if skip_video:
                break

            # Le um frame do video e interrompe se acabar.
            ok, frame = capture.read()
            if not ok:
                break

            # Converte o frame para o formato esperado pelo pygame e o desenha na tela.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, RES, interpolation=cv2.INTER_AREA)
            frame = cv2.transpose(frame)
            frame_surface = pg.surfarray.make_surface(frame)
            self.screen.blit(frame_surface, (0, 0))
            pg.display.flip()
            self.clock.tick(max(1, int(round(fps))))
            pg.time.delay(frame_delay // 3)

        # Libera o video, faz a transicao e inicia a partida.
        capture.release()
        self.draw_intro_transition()
        self.start_game()

    def run_story(self):
        # Loop da tela de prologo ate o usuario decidir continuar.
        while True:
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.run_intro_video()
                        return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.run_intro_video()
                    return

            self.draw_story()
            self.clock.tick(60)

    def run(self):
        # Configura o menu inicial com mouse visivel e musica em loop.
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        pg.mixer.music.load(self.sound_path)
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(-1)

        # Loop principal do menu inicial.
        while True:
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        action = self.run_selection_menu()
                        if action == 'new_game':
                            self.run_story()
                            return 'new_game'
                        if action == 'load_game':
                            self.start_game()
                            return 'load_game'
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        action = self.run_selection_menu()
                        if action == 'new_game':
                            self.run_story()
                            return 'new_game'
                        if action == 'load_game':
                            self.start_game()
                            return 'load_game'

            self.draw()
            self.clock.tick(60)

    def draw_pause_button(self, rect, text):
        # Desenha um botao do menu de pausa com destaque visual ao passar o mouse.
        mouse_pos = pg.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        fill = (44, 38, 32)
        border = (220, 196, 148)
        y_offset = 0
        if hovered:
            fill = (84, 70, 50)
            border = (255, 224, 140)
            y_offset = -4
        draw_rect = rect.move(0, y_offset)
        shadow_rect = draw_rect.move(0, 10)
        pg.draw.rect(self.screen, (0, 0, 0, 90), shadow_rect, border_radius=16)
        pg.draw.rect(self.screen, fill, draw_rect, border_radius=16)
        pg.draw.rect(self.screen, border, draw_rect, 3, border_radius=16)
        label = self.pause_font.render(text, True, (245, 240, 224))
        self.screen.blit(label, label.get_rect(center=draw_rect.center))

    def draw_pause_menu(self):
        # Desenha uma camada escura sobre o jogo e a janela do menu de pausa.
        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))

        panel_shadow = self.pause_panel_rect.move(0, 14)
        pg.draw.rect(self.screen, (8, 8, 10), panel_shadow, border_radius=28)
        pg.draw.rect(self.screen, (24, 22, 22), self.pause_panel_rect, border_radius=28)
        pg.draw.rect(self.screen, (232, 214, 176), self.pause_panel_rect, 3, border_radius=28)
        inner_rect = self.pause_panel_rect.inflate(-26, -26)
        pg.draw.rect(self.screen, (36, 32, 30), inner_rect, 2, border_radius=22)

        title = self.pause_title_font.render('PAUSE', True, (255, 236, 194))
        self.screen.blit(title, title.get_rect(center=(self.pause_panel_rect.centerx, self.pause_panel_rect.y + 72)))

        subtitle = self.selection_hint_font.render('Escolha uma opcao', True, (220, 220, 220))
        self.screen.blit(subtitle, subtitle.get_rect(center=(self.pause_panel_rect.centerx, self.pause_panel_rect.y + 116)))

        # Desenha os botoes de acao do menu de pausa.
        self.draw_pause_button(self.resume_rect, 'Continuar')
        self.draw_pause_button(self.save_game_rect, 'Save game')
        self.draw_pause_button(self.quit_rect, 'Quit')

        if self.pause_feedback and pg.time.get_ticks() < self.pause_feedback_until:
            feedback = self.selection_hint_font.render(self.pause_feedback, True, (255, 241, 198))
            self.screen.blit(feedback, feedback.get_rect(center=(self.pause_panel_rect.centerx, self.pause_panel_rect.bottom - 46)))

        # Exibe a dica de controle rapido.
        hint = self.story_hint_font.render('ESC fecha o menu', True, (255, 255, 255))
        self.screen.blit(hint, hint.get_rect(center=(self.pause_panel_rect.centerx, self.pause_panel_rect.bottom - 18)))
        pg.display.flip()

    def run_pause_menu(self):
        # Loop do menu de pausa durante a partida.
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.pause_feedback = ''
        self.pause_feedback_until = 0

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    # ESC e ENTER fecham o menu e devolvem o controle ao jogo.
                    if event.key == pg.K_ESCAPE:
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        return
                    if event.key == pg.K_RETURN:
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Permite clicar nos botoes do menu de pausa.
                    if self.resume_rect.collidepoint(event.pos):
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        return
                    if self.save_game_rect.collidepoint(event.pos):
                        if self.game.save_game():
                            self.game.show_top_message('Jogo salvo')
                            pg.mouse.set_visible(False)
                            pg.event.set_grab(True)
                            return
                        else:
                            self.pause_feedback = 'Falha ao salvar'
                        self.pause_feedback_until = pg.time.get_ticks() + 1800
                    if self.quit_rect.collidepoint(event.pos):
                        pg.quit()
                        sys.exit()

            # Mantem o jogo desenhado ao fundo enquanto o menu fica aberto.
            self.game.draw()
            self.draw_pause_menu()
            self.clock.tick(60)
