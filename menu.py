import sys
import math
import os
import importlib
import random
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
                'home_center': self.selection_button_centers['new_game'],
            },
            {
                'id': 'load_game',
                'image': self.scale_menu_button_image(
                    pg.image.load(resource_path('resources', 'hub', 'load-game.png')).convert_alpha()
                ),
                'center': self.selection_button_centers['load_game'],
                'home_center': self.selection_button_centers['load_game'],
            },
            {
                'id': 'quit',
                'image': self.scale_menu_button_image(
                    pg.image.load(resource_path('resources', 'hub', 'Quit.png')).convert_alpha()
                ),
                'center': self.selection_button_centers['quit'],
                'home_center': self.selection_button_centers['quit'],
            },
        ]
        # Define caminhos dos arquivos de audio e video usados na introducao.
        self.sound_path = resource_path('resources', 'menu', 'sound_menu.mp3')
        self.intro_video_path = resource_path('resources', 'sound', 'Video Project 7.mp4')
        self.menu_theme_path = resource_path('resources', 'sound', 'menu.mp3')
        self.pydew_main_path = resource_path('pydew-valley-main', 'code', 'main.py')
        self.pydew_root_path = resource_path('pydew-valley-main')
        self.pydew_code_path = resource_path('pydew-valley-main', 'code')
        self.jhoon_theme_path = resource_path('resources', 'sound', 'theme.mp3')
        self.boss_sprite_path = resource_path('resources', 'sprites', 'npc', 'boss_final', 'boss.png')
        self.keep_transition_music = False
        self.opening_sequence_done = False
        self.boss_transition_sprite = None
        if os.path.exists(self.boss_sprite_path):
            self.boss_transition_sprite = pg.image.load(self.boss_sprite_path).convert_alpha()
        self.transition_rain_drops = []
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
        self.update_selection_menu_buttons(mouse_pos)

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

    def move_quit_button(self, button, mouse_pos):
        # Faz o botao de quit fugir do cursor e voltar devagar quando o mouse se afasta.
        current_x, current_y = button['center']
        home_x, home_y = button['home_center']
        dx = current_x - mouse_pos[0]
        dy = current_y - mouse_pos[1]
        distance = math.hypot(dx, dy)
        threat_radius = 240

        if distance < threat_radius:
            if distance < 1:
                dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
                distance = max(1.0, math.hypot(dx, dy))
            escape_step = 28
            current_x += (dx / distance) * escape_step
            current_y += (dy / distance) * escape_step
        else:
            current_x += (home_x - current_x) * 0.08
            current_y += (home_y - current_y) * 0.08

        margin_x = 220
        min_y = HEIGHT // 2 + 150
        max_y = HEIGHT - 80
        current_x = max(margin_x, min(WIDTH - margin_x, current_x))
        current_y = max(min_y, min(max_y, current_y))
        button['center'] = (current_x, current_y)

    def update_selection_menu_buttons(self, mouse_pos):
        # Atualiza a posicao do botao de quit para a brincadeira de fuga.
        for button in self.selection_buttons:
            if button['id'] == 'quit':
                self.move_quit_button(button, mouse_pos)
            else:
                button['center'] = button['home_center']

    def run_selection_menu(self):
        # Loop do menu de escolhas entre a tela inicial e o inicio da partida.
        while True:
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.selection_buttons:
                        if button.get('rect') and button['rect'].collidepoint(event.pos):
                            if button['id'] == 'new_game':
                                self.keep_transition_music = False
                                return 'new_game'
                            if button['id'] == 'load_game':
                                if self.game.has_save_game():
                                    self.keep_transition_music = False
                                    return 'load_game'
                                self.selection_feedback = 'Nenhum save encontrado'
                                self.selection_feedback_until = pg.time.get_ticks() + 1600
                            if button['id'] == 'quit':
                                self.move_quit_button(button, pg.mouse.get_pos())
                                self.selection_feedback = 'Nao da pra clicar em Quit'
                                self.selection_feedback_until = pg.time.get_ticks() + 900

            self.draw_selection_menu()
            self.clock.tick(60)

    def start_game(self):
        # Encerra a musica do menu e prepara o jogo para capturar mouse e teclado.
        self.game.transition_music_active = self.keep_transition_music
        if not self.keep_transition_music:
            pg.mixer.music.stop()
        self.keep_transition_music = False
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

    def play_menu_theme(self):
        # Toca a trilha do menu usada depois da abertura no Pydew.
        pg.mixer.music.load(self.menu_theme_path)
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(-1)

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

    def draw_pydew_red_warning(self, surface, width, height):
        # Adiciona uma camada vermelha transparente sobre o Pydew no fim da transicao.
        red_overlay = pg.Surface((width, height), pg.SRCALPHA)
        red_overlay.fill((200, 0, 0, 120))
        surface.blit(red_overlay, (0, 0))

    def reset_transition_rain(self, width, height, drop_count=90):
        # Prepara as gotas usadas na chuva da fase vermelha.
        self.transition_rain_drops = []
        for _ in range(drop_count):
            self.transition_rain_drops.append({
                'x': random.uniform(0, width),
                'y': random.uniform(-height, height),
                'length': random.randint(10, 22),
                'speed': random.uniform(520, 880),
            })

    def draw_transition_rain(self, surface, width, height, dt):
        # Desenha uma chuva inclinada sobre o mapa durante a fase vermelha.
        if not self.transition_rain_drops:
            self.reset_transition_rain(width, height)

        rain_surface = pg.Surface((width, height), pg.SRCALPHA)
        for drop in self.transition_rain_drops:
            start_pos = (int(drop['x']), int(drop['y']))
            end_pos = (int(drop['x'] - 8), int(drop['y'] + drop['length']))
            pg.draw.line(rain_surface, (210, 230, 255, 130), start_pos, end_pos, 2)

            drop['x'] -= 140 * dt
            drop['y'] += drop['speed'] * dt
            if drop['y'] - drop['length'] > height or drop['x'] < -20:
                drop['x'] = random.uniform(0, width + 60)
                drop['y'] = random.uniform(-120, -20)
                drop['length'] = random.randint(10, 22)
                drop['speed'] = random.uniform(520, 880)

        surface.blit(rain_surface, (0, 0))

    def draw_transition_boss(self, surface, width, height, red_elapsed_ms):
        # Faz o boss descer pelo mapa depois de 2 segundos da tela vermelha.
        if not self.boss_transition_sprite or red_elapsed_ms < 2000:
            return

        progress = min(1.0, (red_elapsed_ms - 2000) / 3500)
        target_height = int(height * 0.5)
        scale = target_height / self.boss_transition_sprite.get_height()
        target_width = max(1, int(self.boss_transition_sprite.get_width() * scale))
        boss_surface = pg.transform.smoothscale(
            self.boss_transition_sprite,
            (target_width, target_height),
        )
        x = (width - target_width) // 2
        start_y = -target_height
        end_y = height - target_height - 40
        y = int(start_y + (end_y - start_y) * progress)
        surface.blit(boss_surface, (x, y))

    def apply_transition_shake(self, surface, width, height, red_elapsed_ms):
        # Faz a tela tremer enquanto o boss desce durante a fase vermelha.
        if red_elapsed_ms < 2000:
            return

        shake_progress = min(1.0, (red_elapsed_ms - 2000) / 3500)
        amplitude = max(2, int(16 * (1.0 - shake_progress * 0.35)))
        offset_x = random.randint(-amplitude, amplitude)
        offset_y = random.randint(-amplitude, amplitude)

        frame = surface.copy()
        surface.fill((8, 0, 0))
        surface.blit(frame, (offset_x, offset_y))

    def load_pydew_level(self):
        # Carrega os modulos do Pydew temporariamente sem poluir os imports do Jhoon.
        if not os.path.exists(self.pydew_code_path):
            return None, None

        stashed_modules = {}
        conflicting_names = (
            'settings', 'menu', 'player', 'support', 'timer', 'level',
            'overlay', 'sprites', 'transition', 'soil', 'sky'
        )
        for name in conflicting_names:
            stashed_modules[name] = sys.modules.get(name)
            sys.modules.pop(name, None)

        inserted_path = False
        if self.pydew_code_path not in sys.path:
            sys.path.insert(0, self.pydew_code_path)
            inserted_path = True

        try:
            pydew_settings = importlib.import_module('settings')
            pydew_level = importlib.import_module('level')
            runtime_state = {
                'stashed_modules': stashed_modules,
                'inserted_path': inserted_path,
            }
            return (pydew_level.Level, pydew_settings), runtime_state
        except Exception:
            self.restore_pydew_imports({
                'stashed_modules': stashed_modules,
                'inserted_path': inserted_path,
            })
            return None, None

    def restore_pydew_imports(self, runtime_state):
        # Remove os modulos temporarios do Pydew e restaura os modulos originais.
        pydew_root = os.path.abspath(self.pydew_root_path)
        for name, module in list(sys.modules.items()):
            module_path = getattr(module, '__file__', None)
            if module_path and os.path.abspath(module_path).startswith(pydew_root):
                sys.modules.pop(name, None)

        if runtime_state.get('inserted_path') and self.pydew_code_path in sys.path:
            sys.path.remove(self.pydew_code_path)

        for name, module in runtime_state.get('stashed_modules', {}).items():
            if module is not None:
                sys.modules[name] = module

    def run_pydew_preview(self, duration_ms=20000, warning_duration_ms=8000):
        # Executa o Pydew na mesma janela, depois entra em alerta vermelho e troca para o Jhoon.
        pydew_runtime, runtime_state = self.load_pydew_level()
        if not pydew_runtime:
            return

        pg.mixer.music.stop()
        previous_caption = pg.display.get_caption()[0]
        previous_mouse_visible = pg.mouse.get_visible()

        try:
            PydewLevel, pydew_settings = pydew_runtime
            pydew_size = (pydew_settings.SCREEN_WIDTH, pydew_settings.SCREEN_HEIGHT)
            self.screen = pg.display.set_mode(pydew_size)
            pg.display.set_caption('Jhoon')
            pg.mouse.set_visible(False)
            pg.event.set_grab(False)
            pg.event.clear()

            level = PydewLevel()
            start_time = pg.time.get_ticks()
            total_duration_ms = duration_ms + warning_duration_ms
            audio_stopped = False
            self.reset_transition_rain(pydew_size[0], pydew_size[1])

            while True:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                        return

                elapsed = pg.time.get_ticks() - start_time
                if elapsed >= total_duration_ms:
                    break

                dt = self.clock.tick(60) / 1000
                level.run(dt)
                if elapsed >= duration_ms:
                    if not audio_stopped:
                        pg.mixer.stop()
                        pg.mixer.music.load(self.menu_theme_path)
                        pg.mixer.music.set_volume(0.3)
                        pg.mixer.music.play(-1)
                        self.keep_transition_music = True
                        audio_stopped = True
                    red_elapsed_ms = elapsed - duration_ms
                    self.draw_transition_rain(self.screen, pydew_size[0], pydew_size[1], dt)
                    self.draw_pydew_red_warning(self.screen, pydew_size[0], pydew_size[1])
                    self.draw_transition_boss(self.screen, pydew_size[0], pydew_size[1], red_elapsed_ms)
                    self.apply_transition_shake(self.screen, pydew_size[0], pydew_size[1], red_elapsed_ms)
                pg.display.update()
        except Exception:
            pass
        finally:
            if not self.keep_transition_music:
                pg.mixer.stop()
            self.transition_rain_drops = []
            self.restore_pydew_imports(runtime_state)
            self.screen = pg.display.set_mode(RES)
            pg.display.set_caption(previous_caption or 'Jhoon')
            pg.mouse.set_visible(previous_mouse_visible)
            pg.event.set_grab(False)
            pg.event.clear()

    def run_opening_sequence(self):
        # Mostra a abertura automatica com Pydew antes dos menus do Jhoon.
        if self.opening_sequence_done:
            return
        self.run_pydew_preview()
        self.screen = pg.display.set_mode(RES)
        pg.display.set_caption('Jhoon')
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        if not pg.mixer.music.get_busy():
            self.play_menu_theme()
        self.opening_sequence_done = True

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
        # Configura o menu inicial e executa a abertura automatica.
        pg.mouse.set_visible(True)
        pg.event.set_grab(False)
        self.run_opening_sequence()

        # Loop principal do menu inicial.
        while True:
            for event in pg.event.get():
                self.handle_common_event(event)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        action = self.run_selection_menu()
                        if action == 'new_game':
                            self.run_intro_video()
                            return 'new_game'
                        if action == 'load_game':
                            self.start_game()
                            return 'load_game'
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.button_rect.collidepoint(event.pos):
                        action = self.run_selection_menu()
                        if action == 'new_game':
                            self.run_intro_video()
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
