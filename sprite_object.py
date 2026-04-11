import pygame as pg
from settings import *
import os
from collections import deque


class SpriteObject:
    def __init__(self, game, path='resources/sprites/static_sprites/candlebra.png',
                 pos=(10.5, 3.5), scale=0.7, shift=0.27):
        # Classe base para qualquer sprite projetado na cena 3D.
        self.game = game
        self.player = game.player
        self.x, self.y = pos
        # Carrega a imagem do sprite e suas propriedades basicas.
        self.image = pg.image.load(resource_path(*path.split('/'))).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        # Variaveis auxiliares usadas no calculo da projecao do sprite.
        self.dx, self.dy, self.theta, self.screen_x, self.dist, self.norm_dist = 0, 0, 0, 0, 1, 1
        self.sprite_half_width = 0
        self.sprite_top = 0
        self.sprite_bottom = 0
        # Escala geral do sprite e deslocamento vertical na projecao.
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift

    def get_sprite_projection(self):
        # Calcula o tamanho com que o sprite deve aparecer na tela.
        proj = SCREEN_DIST / self.norm_dist * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj
        # Limita a projecao maxima para evitar sprites enormes e perda de desempenho.
        proj_width = max(1, min(int(proj_width), MAX_SPRITE_PROJ_WIDTH))
        proj_height = max(1, min(int(proj_height), MAX_SPRITE_PROJ_HEIGHT))

        # Redimensiona a imagem para o tamanho projetado.
        image = pg.transform.scale(self.image, (proj_width, proj_height))

        # Calcula a posicao final do sprite na tela.
        self.sprite_half_width = proj_width // 2
        height_shift = int(proj_height * self.SPRITE_HEIGHT_SHIFT)
        pos = (
            int(self.screen_x - self.sprite_half_width),
            int(HALF_HEIGHT - proj_height // 2 + height_shift)
        )
        self.sprite_top = pos[1]
        self.sprite_bottom = pos[1] + proj_height

        # Envia o sprite para a lista de renderizacao junto com sua profundidade.
        self.game.raycasting.objects_to_render.append((self.norm_dist, image, pos))

    def get_sprite(self):
        # Calcula posicao relativa do sprite em relacao ao jogador.
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        # Ajusta o angulo para descobrir em que coluna da tela o sprite deve aparecer.
        delta = self.theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (HALF_NUM_RAYS + delta_rays) * SCALE

        # Calcula distancia real e distancia corrigida para projecao.
        self.dist = math.hypot(dx, dy)
        self.norm_dist = self.dist * math.cos(delta)
        # So projeta o sprite se ele estiver visivel e a frente do jogador.
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and self.norm_dist > 0.5:
            self.get_sprite_projection()

    def update(self):
        # Atualizacao padrao de um sprite simples.
        self.get_sprite()


class FrameSprite(SpriteObject):
    def __init__(self, game, path='resources/sprites/static_sprites/candlebra.png',
                 pos=(11.5, 3.5), scale=0.8, shift=0.16, animation_time=120):
        # Sprite animado que alterna entre varias imagens ao longo do tempo.
        super().__init__(game, path, pos, scale, shift)
        self.animation_time = animation_time
        self.path = path.rsplit('/', 1)[0]
        self.images = self.get_images(self.path)
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

    def update(self):
        # Atualiza a projecao e a animacao do sprite.
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        # Avanca para o proximo frame da animacao quando o tempo permitir.
        if self.animation_trigger:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self):
        # Verifica se chegou o momento de trocar para o proximo frame.
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def get_images(self, path):
        # Carrega todos os arquivos de imagem de uma pasta para montar a animacao.
        images = deque()
        resolved_path = resource_path(*path.split('/'))
        for file_name in sorted(os.listdir(resolved_path)):
            if os.path.isfile(os.path.join(resolved_path, file_name)):
                img = pg.image.load(os.path.join(resolved_path, file_name)).convert_alpha()
                images.append(img)
        return images


class PickupSprite(SpriteObject):
    def __init__(self, game, path, pos, on_pickup=None, scale=0.45, shift=0.1, pickup_distance=0.75):
        # Sprite coletavel simples que executa uma acao quando o jogador chega perto.
        super().__init__(game, path, pos, scale, shift)
        self.on_pickup = on_pickup
        self.pickup_distance = pickup_distance
        self.picked = False

    def check_pickup(self):
        # Verifica se o jogador esta perto o bastante para coletar o item.
        if self.picked:
            return
        if math.hypot(self.x - self.player.x, self.y - self.player.y) <= self.pickup_distance:
            self.picked = True
            if self.on_pickup:
                self.on_pickup()

    def update(self):
        # Atualiza a coleta e desenha o item apenas se ele ainda nao foi pego.
        self.check_pickup()
        if not self.picked:
            self.get_sprite()


class AnimatedPickupSprite(FrameSprite):
    def __init__(self, game, path, pos, on_pickup=None, scale=0.45, shift=0.1,
                 pickup_distance=0.75, animation_time=120):
        # Pickup animado que combina animacao com coleta por proximidade.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.on_pickup = on_pickup
        self.pickup_distance = pickup_distance
        self.picked = False

    def check_pickup(self):
        # Verifica a coleta do item animado.
        if self.picked:
            return
        if math.hypot(self.x - self.player.x, self.y - self.player.y) <= self.pickup_distance:
            self.picked = True
            if self.on_pickup:
                self.on_pickup()

    def update(self):
        # Atualiza coleta e animacao apenas enquanto o item existir no mapa.
        self.check_pickup()
        if not self.picked:
            super().update()


class SequenceAnimatedPickupSprite(SpriteObject):
    def __init__(self, game, image_paths, pos, on_pickup=None, scale=0.45, shift=0.1,
                 pickup_distance=0.75, animation_time=120):
        # Pickup com animacao feita por uma sequencia manual de imagens.
        super().__init__(game, image_paths[0], pos, scale, shift)
        self.images = deque([pg.image.load(resource_path(*path.split('/'))).convert_alpha() for path in image_paths])
        self.image = self.images[0]
        self.on_pickup = on_pickup
        self.pickup_distance = pickup_distance
        self.picked = False
        self.animation_time = animation_time
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

    def check_pickup(self):
        # Verifica se o jogador pegou o item.
        if self.picked:
            return
        if math.hypot(self.x - self.player.x, self.y - self.player.y) <= self.pickup_distance:
            self.picked = True
            if self.on_pickup:
                self.on_pickup()

    def check_animation_time(self):
        # Controla o tempo entre os quadros da animacao sequencial.
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def update(self):
        # Atualiza coleta, animacao e projecao do pickup sequencial.
        self.check_pickup()
        if self.picked:
            return
        self.check_animation_time()
        if self.animation_trigger:
            self.images.rotate(-1)
            self.image = self.images[0]
        self.get_sprite()


class InteractableSprite(SpriteObject):
    def __init__(self, game, path, pos, on_interact=None, scale=0.45, shift=0.1, interact_distance=1.5):
        # Sprite que pode ser usado/interagido pelo jogador quando estiver proximo.
        super().__init__(game, path, pos, scale, shift)
        self.on_interact = on_interact
        self.interact_distance = interact_distance
        self.used = False

    def can_interact(self):
        # Retorna True se o objeto ainda nao foi usado e esta perto do jogador.
        return (not self.used) and math.hypot(self.x - self.player.x, self.y - self.player.y) <= self.interact_distance

    def interact(self):
        # Executa a interacao e impede que ela aconteca novamente.
        if not self.can_interact():
            return False
        self.used = True
        if self.on_interact:
            self.on_interact()
        return True

    def update(self):
        # Desenha o objeto somente enquanto ele ainda estiver disponivel.
        if not self.used:
            self.get_sprite()
