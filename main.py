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
        # Define se o modo desenvolvedor esta ativo.
        self.dev_mode = False
        # global_trigger e um pulso periodico usado por animacoes e eventos temporizados.
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        # Abre o menu inicial antes de comecar a partida.
        self.menu = Menu(self)
        self.menu.run()
        # Depois do menu, cria todos os sistemas da partida.
        self.new_game()

    def new_game(self):
        # Reinicia o estado principal do jogo e recria todos os modulos da fase.
        self.map = Map(self)
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
        # Abre o menu de desenvolvedor durante a partida.
        self.menu.run_dev_menu()

    def update(self):
        # Atualiza a logica principal do jogo a cada frame.
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
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                # ESC abre o menu de desenvolvedor durante a partida.
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
