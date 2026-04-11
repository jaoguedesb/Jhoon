import pygame as pg
import math
from settings import *


class ObjectRenderer:
    def __init__(self, game):
        # Guarda referencias principais do jogo e da tela.
        self.game = game
        self.screen = game.screen
        # Carrega as texturas usadas nas paredes do mapa.
        self.wall_textures = self.load_wall_textures()
        # Carrega os ceus da fase normal e da fase 2 do boss.
        self.default_sky_image = self.get_texture(resource_path('resources', 'textures', 'sky.png'), (WIDTH, HALF_HEIGHT))
        self.phase_two_sky_image = self.get_texture(resource_path('resources', 'textures', 'sky-2.jpg'), (WIDTH, HALF_HEIGHT))
        self.sky_image = self.default_sky_image
        self.sky_offset = 0
        # Tela vermelha exibida quando o jogador recebe dano.
        self.blood_screen = self.get_texture(resource_path('resources', 'textures', 'blood_screen.png'), RES)
        # Carrega os digitos usados para mostrar a vida no HUD.
        self.digit_size = 42
        self.digit_images = [self.get_texture(resource_path('resources', 'textures', 'digits', f'{i}.png'), [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        # Carrega as telas finais de derrota e vitoria.
        self.game_over_image = self.get_texture(resource_path('resources', 'textures', 'game_over.png'), RES)
        self.win_image = self.get_texture(resource_path('resources', 'textures', 'win.png'), RES)
        # Carrega elementos graficos do HUD principal.
        self.hub_background_size = (640, 310)
        self.hub_background = self.get_texture(resource_path('resources', 'hub', 'fundo.png'), self.hub_background_size)
        self.hub_face_size = (122, 122)
        self.hub_faces = [
            self.get_texture(resource_path('resources', 'hub', f'{i}.png'), self.hub_face_size)
            for i in range(1, 4)
        ]
        # Icone mostrado quando o bonus especial esta ativo.
        self.buff_icon_size = self.hub_face_size
        self.buff_icon = self.get_texture(resource_path('resources', 'hub', '4.png'), self.buff_icon_size)
        # Posicoes base dos elementos do HUD.
        self.hub_background_pos = (
            HALF_WIDTH - self.hub_background_size[0] // 2,
            HEIGHT - self.hub_background_size[1] + 110
        )
        self.hub_face_pos = (
            HALF_WIDTH - self.hub_face_size[0] // 2,
            HEIGHT - self.hub_face_size[1] + 6
        )
        self.minimap_center = (WIDTH - 140, 140)
        self.minimap_radius = 105
        self.minimap_scale = 12
        # Fontes usadas em textos do HUD.
        self.hud_label_font = pg.font.SysFont('couriernew', 24, bold=True)
        self.interact_font = pg.font.SysFont('couriernew', 30, bold=True)

    def draw(self):
        # Desenha os elementos de fundo e depois todos os objetos 3D/sprites da cena.
        self.draw_background()
        self.render_game_objects()
 
    def draw_hud(self):
        # Desenha todos os elementos da interface sobre a cena principal.
        self.draw_minimap()
        self.draw_hub_background()
        self.draw_player_health()
        self.draw_player_face()
        self.draw_final_boss_bar()
        self.draw_interaction_prompt()
        self.draw_mecha_status()

    def win(self):
        # Exibe a tela de vitoria.
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        # Exibe a tela de derrota.
        self.screen.blit(self.game_over_image, (0, 0))

    def draw_player_health(self):
        # Desenha a vida do jogador usando imagens numericas no HUD.
        health = str(self.game.player.health)
        total_width = (len(health) + 1) * self.digit_size
        start_x = self.hub_face_pos[0] - total_width - 26
        start_y = self.hub_face_pos[1] + 54
        label_surface = self.hud_label_font.render('VIDA', False, (255, 255, 255))
        label_x = start_x + max(0, (total_width - label_surface.get_width()) // 2)
        label_y = start_y - label_surface.get_height() - 2
        self.screen.blit(label_surface, (label_x, label_y))
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char], (start_x + i * self.digit_size, start_y))
        self.screen.blit(self.digits['10'], (start_x + len(health) * self.digit_size, start_y))

    def draw_hub_background(self):
        # Desenha a base grafica do HUD na parte inferior da tela.
        self.screen.blit(self.hub_background, self.hub_background_pos)

    def draw_player_face(self):
        # Mostra o rosto do jogador ou o icone de buff quando o especial esta ativo.
        if self.game.weapon.special_active:
            self.screen.blit(self.buff_icon, self.hub_face_pos)
            return
        face_index = (pg.time.get_ticks() // 4000) % len(self.hub_faces)
        self.screen.blit(self.hub_faces[face_index], self.hub_face_pos)

    def draw_minimap(self):
        # Cria e desenha o minimapa circular com paredes, grade e direcao do jogador.
        minimap_size = self.minimap_radius * 2
        minimap_surface = pg.Surface((minimap_size, minimap_size), pg.SRCALPHA)
        center = (self.minimap_radius, self.minimap_radius)

        # Desenha os circulos de fundo do minimapa.
        for radius, color in (
            (self.minimap_radius, (10, 14, 18, 235)),
            (self.minimap_radius - 10, (18, 24, 30, 240)),
            (self.minimap_radius - 22, (24, 32, 40, 245)),
        ):
            pg.draw.circle(minimap_surface, color, center, radius)

        # Adiciona aneis concentricos e linhas de grade para referencia visual.
        for radius in range(24, self.minimap_radius - 14, 24):
            pg.draw.circle(minimap_surface, (60, 86, 94, 70), center, radius, 1)

        for offset in range(-72, 73, 24):
            pg.draw.line(
                minimap_surface,
                (60, 86, 94, 45),
                (center[0] + offset, 16),
                (center[0] + offset, minimap_size - 16),
                1
            )
            pg.draw.line(
                minimap_surface,
                (60, 86, 94, 45),
                (16, center[1] + offset),
                (minimap_size - 16, center[1] + offset),
                1
            )

        # Desenha as paredes do mapa no minimapa relativas a posicao do jogador.
        player_x, player_y = self.game.player.pos
        for map_x, map_y in self.game.map.world_map:
            rel_x = (map_x + 0.5 - player_x) * self.minimap_scale
            rel_y = (map_y + 0.5 - player_y) * self.minimap_scale
            rect = pg.Rect(
                int(rel_x + self.minimap_radius - self.minimap_scale / 2),
                int(rel_y + self.minimap_radius - self.minimap_scale / 2),
                self.minimap_scale,
                self.minimap_scale
            )
            if rect.centerx < 0 or rect.centery < 0 or rect.centerx > minimap_size or rect.centery > minimap_size:
                continue
            pg.draw.rect(minimap_surface, (124, 222, 180, 215), rect, border_radius=3)
            pg.draw.rect(minimap_surface, (220, 255, 240, 150), rect, 1, border_radius=3)

        # Desenha o cone de visao do jogador.
        cone_length = 44
        left_angle = self.game.player.angle - 0.35
        right_angle = self.game.player.angle + 0.35
        vision_points = [center]
        for angle in (left_angle, self.game.player.angle, right_angle):
            vision_points.append(
                (
                    center[0] + int(math.cos(angle) * cone_length),
                    center[1] + int(math.sin(angle) * cone_length)
                )
            )
        pg.draw.polygon(minimap_surface, (255, 120, 80, 55), vision_points)

        # Desenha o marcador de direcao e o ponto central do jogador.
        direction_end = (
            center[0] + int(math.cos(self.game.player.angle) * 36),
            center[1] + int(math.sin(self.game.player.angle) * 36)
        )
        pg.draw.line(minimap_surface, (255, 132, 92, 255), center, direction_end, 4)
        pg.draw.circle(minimap_surface, (255, 214, 102, 255), center, 8)
        pg.draw.circle(minimap_surface, (255, 246, 196, 255), center, 4)

        # Aplica uma mascara circular para manter o minimapa recortado corretamente.
        mask_surface = pg.Surface((minimap_size, minimap_size), pg.SRCALPHA)
        pg.draw.circle(
            mask_surface,
            (255, 255, 255, 255),
            (self.minimap_radius, self.minimap_radius),
            self.minimap_radius - 5
        )
        minimap_surface.blit(mask_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # Desenha os contornos finais do minimapa.
        pg.draw.circle(minimap_surface, (255, 240, 200, 255), center, self.minimap_radius - 2, 3)
        pg.draw.circle(minimap_surface, (74, 49, 32, 255), center, self.minimap_radius, 6)

        # Posiciona o minimapa no canto superior direito da tela.
        self.screen.blit(
            minimap_surface,
            (self.minimap_center[0] - self.minimap_radius, self.minimap_center[1] - self.minimap_radius)
        )

    def player_damage(self):
        # Sobrepoe a tela vermelha de dano.
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_final_boss_bar(self):
        # Desenha a barra de vida do boss final quando ele estiver vivo.
        boss = self.game.object_handler.final_boss
        if not boss or not boss.alive:
            return

        bar_width = 560
        bar_height = 26
        x = HALF_WIDTH - bar_width // 2
        y = 28
        health_ratio = max(0.0, min(1.0, boss.health / boss.max_health))

        title_font = pg.font.SysFont('couriernew', 32, bold=True)
        title_surface = title_font.render(boss.name, True, (250, 238, 210))
        title_pos = (HALF_WIDTH - title_surface.get_width() // 2, y - 34)
        self.screen.blit(title_surface, title_pos)

        shadow_rect = pg.Rect(x - 6, y - 6, bar_width + 12, bar_height + 12)
        pg.draw.rect(self.screen, (20, 8, 8), shadow_rect, border_radius=10)
        bg_rect = pg.Rect(x, y, bar_width, bar_height)
        pg.draw.rect(self.screen, (68, 18, 18), bg_rect, border_radius=8)
        fill_rect = pg.Rect(x, y, int(bar_width * health_ratio), bar_height)
        if fill_rect.width > 0:
            pg.draw.rect(self.screen, (210, 32, 32), fill_rect, border_radius=8)
        pg.draw.rect(self.screen, (255, 220, 180), bg_rect, 3, border_radius=8)

    def draw_interaction_prompt(self):
        # Exibe uma mensagem de interacao na tela quando houver algo para pegar/interagir.
        message = self.game.object_handler.interaction_message
        if not message:
            return
        prompt_surface = self.interact_font.render(message, True, (255, 244, 188))
        prompt_bg = prompt_surface.get_rect(center=(HALF_WIDTH, HEIGHT - 170)).inflate(32, 20)
        pg.draw.rect(self.screen, (14, 14, 18), prompt_bg, border_radius=12)
        pg.draw.rect(self.screen, (255, 212, 122), prompt_bg, 2, border_radius=12)
        self.screen.blit(prompt_surface, prompt_surface.get_rect(center=prompt_bg.center))

    def draw_mecha_status(self):
        # Mostra um aviso visual quando a minigun estiver equipada.
        if self.game.weapon.weapon_type != 'minigun':
            return
        status_text = 'MINIGUN EQUIPADA'
        status_surface = self.interact_font.render(status_text, True, (255, 220, 120))
        self.screen.blit(status_surface, (32, 26))

    def draw_background(self):
        # Desenha o ceu com movimento lateral baseado na rotacao do jogador.
        self.sky_offset = (self.sky_offset + 4.5 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # Desenha o chao como um retangulo preenchendo a metade inferior da tela.
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))

    def set_default_sky(self):
        # Restaura o ceu padrao do jogo.
        self.sky_image = self.default_sky_image

    def set_boss_phase_two_sky(self):
        # Troca o ceu para a versao especial da fase 2 do boss.
        self.sky_image = self.phase_two_sky_image

    def render_game_objects(self):
        # Ordena os objetos por profundidade e desenha do mais distante para o mais proximo.
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        # Carrega uma textura da imagem e redimensiona para a resolucao desejada.
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        # Carrega e organiza as texturas de parede por identificador numerico.
        return {
            1: self.get_texture(resource_path('resources', 'textures', '1.png')),
            2: self.get_texture(resource_path('resources', 'textures', '2.png')),
            3: self.get_texture(resource_path('resources', 'textures', '3.png')),
            4: self.get_texture(resource_path('resources', 'textures', '4.png')),
            5: self.get_texture(resource_path('resources', 'textures', '5.png')),
        }
