import pygame as pg
import sys
from settings import *
from mapas import Map
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from menu import Menu
from save_system import SaveSystem


class Game:
    def __init__(self):
        # Inicializa o pygame e garante que o mixer de audio esteja pronto.
        pg.init()
        if not pg.mixer.get_init():
            pg.mixer.init()
        # Cria a janela principal e o relogio que controla o tempo entre frames.
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        # delta_time armazena a duracao do ultimo frame para manter movimentos suaves.
        self.delta_time = 1
        self.save_system = SaveSystem()
        self.top_message = ''
        self.top_message_until = 0
        self.top_message_duration = 0
        # Define se o modo desenvolvedor esta ativo.
        self.dev_mode = False
        # Estado do terminal interno aberto pelo Enter.
        self.console_active = False
        self.console_input = ''
        self.console_message = ''
        self.console_message_until = 0
        # global_trigger e um pulso periodico usado por animacoes e eventos temporizados.
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        # Abre o menu inicial antes de comecar a partida.
        self.menu = Menu(self)
        menu_action = self.menu.run()
        if menu_action == 'load_game' and self.load_game():
            return
        # Depois do menu, cria todos os sistemas da partida.
        self.new_game()

    def new_game(self, map_id=None, show_intro_message=True):
        # Reinicia o estado principal do jogo e recria todos os modulos da fase.
        self.map = Map(self, map_id=map_id)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.weapon = Weapon(self)
        self.object_handler = ObjectHandler(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        # Se o modo dev estiver ligado, reaplica os beneficios no novo jogo.
        if self.dev_mode:
            self.set_dev_mode(True)
        if show_intro_message:
            self.show_top_message('Pegue o gato', duration=4000)

    def set_dev_mode(self, enabled):
        # Liga ou desliga o modo desenvolvedor e ajusta vantagens do jogador.
        self.dev_mode = enabled
        self.player.infinite_health = enabled
        if enabled:
            # Ao ativar, restaura a vida e equipa o bonus especial se necessario.
            self.player.health = PLAYER_MAX_HEALTH
            if self.weapon.weapon_type != 'minigun':
                self.weapon.activate_racao_boost()
        else:
            # Ao desativar, remove bonus especiais e normaliza a movimentacao.
            if self.weapon.special_active:
                self.weapon.deactivate_racao_boost()
            else:
                self.player.speed_multiplier = 1.0

    def open_dev_menu(self):
        # Abre o menu de pausa durante a partida.
        self.menu.run_pause_menu()

    def toggle_console(self):
        # Alterna a visibilidade do terminal interno e limpa a linha atual ao fechar.
        self.console_active = not self.console_active
        if self.console_active:
            self.console_input = ''
        else:
            self.console_input = ''

    def show_console_message(self, message, duration=2200):
        # Exibe uma resposta curta do terminal por alguns instantes.
        self.console_message = message
        self.console_message_until = pg.time.get_ticks() + duration

    def execute_console_command(self):
        # Processa os comandos digitados no terminal interno.
        command = self.console_input.strip().lower()
        self.console_input = ''

        if not command:
            self.console_active = False
            return

        if command == 'devmode':
            self.set_dev_mode(True)
            self.show_console_message('devmode ativado')
        elif command == 'disabledevmode':
            self.set_dev_mode(False)
            self.show_console_message('devmode desativado')
        elif command == 'pegadinha':
            self.object_handler.spawn_secret_boss()
            self.show_console_message('boss secreto spawnado')
        else:
            self.show_console_message(f'comando invalido: {command}')

        self.console_active = False

    def handle_console_event(self, event):
        # Captura entrada de texto enquanto o terminal estiver aberto.
        if event.type != pg.KEYDOWN:
            return

        if event.key == pg.K_ESCAPE:
            self.console_active = False
            self.console_input = ''
            return

        if event.key == pg.K_RETURN:
            self.execute_console_command()
            return

        if event.key == pg.K_BACKSPACE:
            self.console_input = self.console_input[:-1]
            return

        if event.unicode and event.unicode.isprintable():
            self.console_input += event.unicode
    def has_save_game(self):
        # Informa ao menu inicial se existe um save pronto para carregar.
        return self.save_system.has_save()

    def save_game(self):
        # Serializa o estado atual da partida em arquivo para retomar depois.
        payload = {
            'dev_mode': self.dev_mode,
            'map': self.map.serialize_state(),
            'player': self.player.serialize_state(),
            'weapon': self.weapon.serialize_state(),
            'objects': self.object_handler.serialize_state(),
        }
        try:
            self.save_system.save(payload)
            return True
        except (OSError, TypeError, ValueError):
            return False

    def show_top_message(self, message, duration=1800):
        # Exibe um aviso grande no topo da tela com fade-out automatico.
        self.top_message = message
        self.top_message_duration = duration
        self.top_message_until = pg.time.get_ticks() + duration

    def load_game(self):
        # Carrega o save existente e recompõe a partida exatamente no estado salvo.
        try:
            save_data = self.save_system.load()
        except (OSError, ValueError):
            return False
        if not save_data:
            return False

        map_state = save_data.get('map', {})
        self.new_game(map_id=map_state.get('map_id'), show_intro_message=False)
        self.dev_mode = save_data.get('dev_mode', False)
        self.map.apply_saved_state(map_state)
        self.player.apply_saved_state(save_data.get('player', {}))
        self.weapon.apply_saved_state(save_data.get('weapon', {}))
        self.object_handler.apply_saved_state(save_data.get('objects', {}))
        self.pathfinding.rebuild()
        self.sync_loaded_state()
        return True

    def sync_loaded_state(self):
        # Reaplica musica, ceu e mensagens corretas depois de carregar um save.
        self.player.infinite_health = self.dev_mode or self.player.infinite_health
        if self.dev_mode:
            self.player.health = PLAYER_MAX_HEALTH

        final_boss = self.object_handler.final_boss
        if final_boss and final_boss.alive:
            if final_boss.phase_two_triggered:
                self.object_renderer.set_boss_phase_two_sky()
                self.sound.play_boss_phase_two_theme()
            else:
                self.object_renderer.set_default_sky()
                self.sound.play_boss_theme()
        elif self.weapon.special_active:
            self.object_renderer.set_default_sky()
            self.sound.play_boost_theme()
        else:
            self.object_renderer.set_default_sky()
            self.sound.play_main_theme()
        self.object_handler.update_interaction_message()

    def update(self):
        # Atualiza a logica principal do jogo a cada frame.
        if self.console_active:
            # Congela a simulacao enquanto o jogador digita no terminal.
            pg.display.flip()
            self.delta_time = self.clock.tick(FPS)
            pg.display.set_caption(f'{self.clock.get_fps() :.1f}')
            return
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        # Envia o frame pronto para a tela.
        pg.display.flip()
        # Calcula o tempo do frame e atualiza o FPS exibido na janela.
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        # Desenha o cenario, objetos, arma e HUD.
        self.object_renderer.draw()
        self.weapon.draw()
        self.object_renderer.draw_hud()
        # Linhas abaixo podem ser ativadas para depuracao visual.
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        # Processa todos os eventos de entrada do usuario e do sistema.
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                # Fecha o jogo ao clicar no X da janela.
                pg.quit()
                sys.exit()
            elif self.console_active:
                self.handle_console_event(event)
                continue
            elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                # ENTER abre o terminal interno.
                self.toggle_console()
                continue
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                # ESC abre o menu de pausa durante a partida.
                self.open_dev_menu()
            elif event.type == self.global_event:
                # Marca o disparo do evento global temporizado.
                self.global_trigger = True
            # Repassa o evento para a logica de tiro do jogador.
            self.player.single_fire_event(event)

    def run(self):
        # Loop principal do jogo: ler eventos, atualizar logica e desenhar.
        while True:
            self.check_events()
            self.update()
            self.draw()


if __name__ == '__main__':
    # Cria a instancia principal do jogo e inicia o loop.
    game = Game()
    game.run()
