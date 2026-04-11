import pygame as pg
from settings import resource_path


class Sound:
    def __init__(self, game):
        # Guarda a referencia do jogo.
        self.game = game
        # Garante que o mixer de audio do pygame esteja inicializado.
        if not pg.mixer.get_init():
            pg.mixer.init()
        # Caminho base dos arquivos de som do projeto.
        self.path = resource_path('resources', 'sound')
        # Carrega os efeitos sonoros usados durante o jogo.
        self.shotgun = pg.mixer.Sound(resource_path('resources', 'sound', 'shotgun.wav'))
        self.npc_pain = pg.mixer.Sound(resource_path('resources', 'sound', 'npc_pain.wav'))
        self.npc_death = pg.mixer.Sound(resource_path('resources', 'sound', 'npc_death.wav'))
        self.npc_shot = pg.mixer.Sound(resource_path('resources', 'sound', 'npc_attack.wav'))
        # Ajusta o volume do tiro dos NPCs para nao ficar alto demais.
        self.npc_shot.set_volume(0.2)
        self.player_pain = pg.mixer.Sound(resource_path('resources', 'sound', 'player_pain.wav'))
        self.meca_shot = pg.mixer.Sound(resource_path('resources', 'sound', 'meca-som.ogg'))
        # Ajusta o volume do disparo da minigun.
        self.meca_shot.set_volume(0.35)
        # Volume padrao das musicas de fundo.
        self.music_volume = 0.3
        # Caminhos das trilhas sonoras usadas em cada estado importante do jogo.
        self.main_theme_path = resource_path('resources', 'sound', 'theme.mp3')
        self.boost_theme_path = resource_path('resources', 'sound', 'hhh.mp3')
        self.boss_theme_path = resource_path('resources', 'sound', 'boss-final.mp3')
        self.boss_phase_two_theme_path = resource_path('resources', 'sound', 'boss-final-2.mp3')
        # Guarda qual musica esta tocando para evitar recarregar a mesma faixa sem necessidade.
        self.current_theme_path = None
        pg.mixer.music.set_volume(self.music_volume)
        # Inicia a musica principal do jogo.
        self.play_main_theme()

    def play_theme(self, theme_path):
        # Troca a musica atual apenas se a faixa desejada ainda nao estiver tocando.
        if self.current_theme_path == theme_path:
            return
        self.current_theme_path = theme_path
        pg.mixer.music.load(theme_path)
        pg.mixer.music.set_volume(self.music_volume)
        pg.mixer.music.play(-1)

    def play_main_theme(self):
        # Toca a trilha principal do jogo.
        self.play_theme(self.main_theme_path)

    def play_boost_theme(self):
        # Toca a trilha especial durante o modo de boost.
        self.play_theme(self.boost_theme_path)

    def play_boss_theme(self):
        # Toca a trilha da luta contra o boss final.
        self.play_theme(self.boss_theme_path)

    def play_boss_phase_two_theme(self):
        # Toca a trilha especifica da segunda fase do boss.
        self.play_theme(self.boss_phase_two_theme_path)
