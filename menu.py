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
        # Define caminhos dos arquivos de audio e video usados na introducao.
        self.sound_path = resource_path('resources', 'menu', 'sound_menu.mp3')
        self.intro_video_path = resource_path('resources', 'sound', 'inicio.mp4')
        # Inicializa as fontes usadas nas telas do menu.
        self.story_title_font = pg.font.SysFont('georgia', 42, bold=True)
        self.story_font = pg.font.SysFont('georgia', 28)
        self.story_hint_font = pg.font.SysFont('couriernew', 24, bold=True)
        self.dev_title_font = pg.font.SysFont('couriernew', 42, bold=True)
        self.dev_font = pg.font.SysFont('couriernew', 28, bold=True)
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
        # Define as areas clicaveis do menu de desenvolvedor.
        self.resume_rect = pg.Rect(WIDTH // 2 - 180, HEIGHT // 2 - 10, 360, 56)
        self.dev_mode_rect = pg.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 70, 360, 56)
        self.quit_rect = pg.Rect(WIDTH // 2 - 180, HEIGHT // 2 + 150, 360, 56)

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
                        self.run_story()
                        return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        self.run_story()
                        return

            self.draw()
            self.clock.tick(60)

    def draw_dev_button(self, rect, text, active=False):
        # Desenha um botao do menu dev com destaque visual ao passar o mouse.
        mouse_pos = pg.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)
        fill = (58, 48, 36) if not active else (84, 102, 40)
        if hovered:
            fill = (92, 78, 56) if not active else (112, 130, 58)
        pg.draw.rect(self.screen, fill, rect, border_radius=12)
        pg.draw.rect(self.screen, (232, 214, 176), rect, 3, border_radius=12)
        label = self.dev_font.render(text, True, (245, 240, 224))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_dev_menu(self):
        # Desenha uma camada escura sobre o jogo e a janela do menu de desenvolvedor.
        overlay = pg.Surface(RES, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))

        panel = pg.Rect(WIDTH // 2 - 260, HEIGHT // 2 - 130, 520, 330)
        pg.draw.rect(self.screen, (22, 20, 20), panel, border_radius=18)
        pg.draw.rect(self.screen, (232, 214, 176), panel, 3, border_radius=18)

        title = self.dev_title_font.render('DEV MODE', True, (255, 236, 194))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))

        # Mostra o estado atual do modo desenvolvedor.
        status = 'ATIVO' if self.game.dev_mode else 'DESLIGADO'
        status_surface = self.dev_font.render(f'Status: {status}', True, (220, 220, 220))
        self.screen.blit(status_surface, status_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25)))

        # Desenha os botoes de acao do menu dev.
        self.draw_dev_button(self.resume_rect, 'Continuar')
        self.draw_dev_button(self.dev_mode_rect, f'Dev Mode: {status}', active=self.game.dev_mode)
        self.draw_dev_button(self.quit_rect, 'Sair do jogo')

        # Exibe a dica de controle rapido.
        hint = self.story_hint_font.render('ESC fecha o menu', True, (255, 255, 255))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 225)))
        pg.display.flip()

    def run_dev_menu(self):
        # Loop do menu de desenvolvedor durante a partida.
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)

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
                    if event.key == pg.K_d:
                        # Alterna o estado do modo desenvolvedor.
                        self.game.set_dev_mode(not self.game.dev_mode)
                    if event.key == pg.K_RETURN:
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        return
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    # Permite clicar nos botoes do menu dev.
                    if self.resume_rect.collidepoint(event.pos):
                        pg.mouse.set_visible(False)
                        pg.event.set_grab(True)
                        return
                    if self.dev_mode_rect.collidepoint(event.pos):
                        self.game.set_dev_mode(not self.game.dev_mode)
                    if self.quit_rect.collidepoint(event.pos):
                        pg.quit()
                        sys.exit()

            # Mantem o jogo desenhado ao fundo enquanto o menu fica aberto.
            self.game.draw()
            self.draw_dev_menu()
            self.clock.tick(60)
