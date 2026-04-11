import pygame as pg
import math
from settings import *


class RayCasting:
    def __init__(self, game):
        # Guarda a referencia do jogo e inicializa estruturas usadas no ray casting.
        self.game = game
        # Armazena o resultado bruto dos raios disparados na cena.
        self.ray_casting_result = []
        # Lista final de colunas/objetos que serao desenhados na tela.
        self.objects_to_render = []
        # Referencia rapida para as texturas de parede carregadas no renderer.
        self.textures = self.game.object_renderer.wall_textures

    def get_objects_to_render(self):
        # Converte o resultado dos raios em colunas de parede prontas para desenhar.
        self.objects_to_render = []
        for ray, values in enumerate(self.ray_casting_result):
            depth, proj_height, texture, offset = values

            # Se a parede projetada cabe na tela, usa a textura inteira e ajusta a altura.
            if proj_height < HEIGHT:
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), 0, SCALE, TEXTURE_SIZE
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, proj_height))
                wall_pos = (ray * SCALE, HALF_HEIGHT - proj_height // 2)
            else:
                # Se a parede ficaria maior que a tela, recorta a parte central da textura.
                texture_height = TEXTURE_SIZE * HEIGHT / proj_height
                wall_column = self.textures[texture].subsurface(
                    offset * (TEXTURE_SIZE - SCALE), HALF_TEXTURE_SIZE - texture_height // 2,
                    SCALE, texture_height
                )
                wall_column = pg.transform.scale(wall_column, (SCALE, HEIGHT))
                wall_pos = (ray * SCALE, 0)

            # Salva a coluna de parede com sua profundidade para renderizacao posterior.
            self.objects_to_render.append((depth, wall_column, wall_pos))

    def ray_cast(self):
        # Dispara varios raios a partir da posicao do jogador para descobrir paredes visiveis.
        self.ray_casting_result = []
        texture_vert, texture_hor = 1, 1
        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        # Inicia o primeiro raio no limite esquerdo do campo de visao.
        ray_angle = self.game.player.angle - HALF_FOV + 0.0001
        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # Procura a primeira intersecao horizontal entre o raio e uma parede.
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(MAX_DEPTH):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.game.map.world_map:
                    texture_hor = self.game.map.world_map[tile_hor]
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # Procura a primeira intersecao vertical entre o raio e uma parede.
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(MAX_DEPTH):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.game.map.world_map:
                    texture_vert = self.game.map.world_map[tile_vert]
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # Escolhe a intersecao mais proxima e calcula o deslocamento da textura.
            if depth_vert < depth_hor:
                depth, texture = depth_vert, texture_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth, texture = depth_hor, texture_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            # Corrige a distorcao visual causada pela diferenca angular entre os raios.
            depth *= math.cos(self.game.player.angle - ray_angle)

            # Calcula a altura projetada da parede na tela.
            proj_height = SCREEN_DIST / (depth + 0.0001)

            # Salva o resultado do raio para ser convertido em uma coluna renderizavel.
            self.ray_casting_result.append((depth, proj_height, texture, offset))

            # Avanca para o proximo raio dentro do campo de visao.
            ray_angle += DELTA_ANGLE

    def update(self):
        # Atualiza o ray casting completo a cada frame.
        self.ray_cast()
        self.get_objects_to_render()
