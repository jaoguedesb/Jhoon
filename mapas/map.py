import pygame as pg
from copy import deepcopy
from random import choice

from settings import ACTIVE_MAP
from .catalog import MAP_LAYOUTS


class Map:
    def __init__(self, game, map_id=None):
        # Guarda a referencia do jogo para acessar a tela e outros sistemas.
        self.game = game
        selected_map_id = map_id if map_id in MAP_LAYOUTS else ACTIVE_MAP
        selected_map = MAP_LAYOUTS.get(selected_map_id, MAP_LAYOUTS['map_01_llm'])
        self.map_id = selected_map_id if selected_map_id in MAP_LAYOUTS else 'map_01_llm'
        self.map_title = selected_map['title']
        # Copia a matriz base para permitir reconstruir o layout ao carregar um save.
        self.base_mini_map = [row[:] for row in selected_map['mini_map']]
        self.mini_map = [row[:] for row in self.base_mini_map]
        self.door_definitions = deepcopy(selected_map.get('doors', []))
        self.doors = {}
        # world_map sera um dicionario com apenas as celulas ocupadas por parede.
        self.world_map = {}
        self.non_blocking_tiles = set()
        # Calcula quantidade de linhas e colunas do mapa.
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.initialize_doors()
        # Converte a matriz em um formato mais pratico para colisao e raycasting.
        self.get_map()

    def reset_layout(self):
        # Restaura a matriz original antes de reaplicar portas e alavancas.
        self.mini_map = [row[:] for row in self.base_mini_map]
        self.doors = {}
        self.world_map = {}
        self.non_blocking_tiles = set()

    def initialize_doors(self, saved_doors=None):
        # Registra todas as portas dinamicas do mapa e aplica o estado inicial fechado.
        saved_doors = saved_doors or {}
        for door_data in self.door_definitions:
            door_id = door_data['id']
            self.doors[door_id] = deepcopy(door_data)
            saved_door = saved_doors.get(door_id, {})
            self.doors[door_id]['is_open'] = False
            button_tiles = self.doors[door_id].get('button_tiles')
            selected_button_tile = saved_door.get('selected_button_tile')
            if selected_button_tile:
                self.doors[door_id]['selected_button_tile'] = tuple(selected_button_tile)
            elif button_tiles:
                self.doors[door_id]['selected_button_tile'] = choice(button_tiles)
            self.apply_closed_door(door_id)
            self.apply_switch_state(door_id, opened=False)
            if saved_door.get('is_open'):
                self.open_door(door_id)

    def get_map(self):
        # Percorre toda a matriz e salva no dicionario apenas as posicoes com parede.
        self.world_map = {}
        for j, row in enumerate(self.mini_map):
            for i, value in enumerate(row):
                if value and (i, j) not in self.non_blocking_tiles:
                    self.world_map[(i, j)] = value

    def set_tile(self, x, y, value):
        # Atualiza uma celula da matriz e do dicionario de colisao ao mesmo tempo.
        self.mini_map[y][x] = value
        if value and (x, y) not in self.non_blocking_tiles:
            self.world_map[(x, y)] = value
        else:
            self.world_map.pop((x, y), None)

    def set_passable_tile(self, x, y, value):
        # Marca um tile visual como atravessavel, sem colisao.
        self.non_blocking_tiles.add((x, y))
        self.set_tile(x, y, value)

    def set_blocking_tile(self, x, y, value):
        # Marca um tile como solido para colisao e raycasting.
        self.non_blocking_tiles.discard((x, y))
        self.set_tile(x, y, value)

    def is_blocking(self, x, y):
        # Retorna True quando o tile bloqueia movimento.
        return (x, y) in self.world_map

    def apply_closed_door(self, door_id):
        # Fecha a porta com madeira nas laterais e a folha da porta no centro.
        door = self.doors[door_id]
        for (x, y), texture_id in door['open_frame_tiles'].items():
            self.set_blocking_tile(x, y, texture_id)
        for x, y in door['open_passages']:
            self.set_blocking_tile(x, y, 6)

    def open_door(self, door_id):
        # Abre uma porta, liberando o centro para passagem e mantendo a folha visivel.
        door = self.doors.get(door_id)
        if not door or door['is_open']:
            return False

        for (x, y), texture_id in door['open_frame_tiles'].items():
            self.set_blocking_tile(x, y, texture_id)
        for x, y in door['open_passages']:
            self.set_passable_tile(x, y, 6)

        door['is_open'] = True
        self.apply_switch_state(door_id, opened=True)
        if hasattr(self.game, 'pathfinding'):
            self.game.pathfinding.rebuild()
        return True

    def apply_switch_state(self, door_id, opened):
        # Atualiza o tile da alavanca como parede interativa fechada ou aberta.
        door = self.doors[door_id]
        button_tile = door.get('selected_button_tile')
        if not button_tile:
            return
        texture_id = 9 if opened else 8
        self.set_blocking_tile(button_tile[0], button_tile[1], texture_id)

    def get_switches(self):
        # Retorna os botoes que controlam as portas do mapa atual.
        return list(self.doors.values())

    def serialize_state(self):
        # Exporta o estado das portas e alavancas para que a fase volte do mesmo ponto.
        return {
            'map_id': self.map_id,
            'doors': {
                door_id: {
                    'is_open': door_data.get('is_open', False),
                    'selected_button_tile': list(door_data['selected_button_tile'])
                    if door_data.get('selected_button_tile') else None,
                }
                for door_id, door_data in self.doors.items()
            },
        }

    def apply_saved_state(self, state):
        # Reconstrui o layout dinamico do mapa com base no save carregado.
        self.reset_layout()
        self.initialize_doors(state.get('doors', {}))
        self.get_map()

    def draw(self):
        # Desenha um contorno das paredes na tela.
        # Essa funcao serve como apoio visual para depuracao do mapa.
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.world_map]
