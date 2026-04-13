import math
import os
import sys

# Configuracoes gerais da janela do jogo.
RES = WIDTH, HEIGHT = 1600, 900
# RES = WIDTH, HEIGHT = 1920, 1080
# Metade da largura e da altura, usadas com frequencia em varios calculos.
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
# FPS = 0 deixa o jogo rodar sem limite fixo imposto pelo clock.
FPS = 0

# Mapa ativo carregado pela pasta mapas/.
# Opcoes iniciais: map_01_llm, map_02_classic, map_03_arena
ACTIVE_MAP = 'map_01_llm'

# Configuracoes iniciais do jogador.
PLAYER_POS = 1.5, 5  # mini_map
PLAYER_ANGLE = 0
PLAYER_SPEED = 0.004
PLAYER_ROT_SPEED = 0.002
PLAYER_SIZE_SCALE = 60
PLAYER_MAX_HEALTH = 100

# Configuracoes do controle por mouse.
MOUSE_SENSITIVITY = 0.0003
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

# Cor usada para desenhar o chao.
FLOOR_COLOR = (30, 30, 30)

# Configuracoes do campo de visao e do sistema de ray casting.
FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20

# Distancia da tela de projecao e escala horizontal de cada coluna renderizada.
SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# Tamanho base das texturas de parede.
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# Limites de projecao dos sprites para evitar escalas exageradas e perda de desempenho.
MAX_SPRITE_PROJ_HEIGHT = int(HEIGHT * 1.35)
MAX_SPRITE_PROJ_WIDTH = int(WIDTH * 1.2)

# Limites e distancias usadas na fase 2 do boss/reflexo.
MAX_BOSS_PROJECTILES = 18
MAX_CLONE_PROJECTILES = 8
CLONE_RENDER_DISTANCE = 16
CLONE_UPDATE_DISTANCE = 22


def resource_path(*parts):
    # Resolve caminhos de arquivos tanto no ambiente normal quanto em build empacotada.
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, *parts)
