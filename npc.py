from sprite_object import *
from random import randint, random


class BossProjectile(SpriteObject):
    def __init__(self, game, pos, angle, speed=0.085, damage=35,
                 path='resources/sprites/npc/boss_final/boladefogo.png', scale=0.55, shift=0.0):
        # Cria um projetil usado pelo boss final e, em alguns casos, pelo reflexo da fase 2.
        super().__init__(game, path, pos, scale, shift)
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.destroyed = False

    def update(self):
        # Ignora processamento se o projetil ja foi destruido.
        if self.destroyed:
            return

        # Move o projetil na direcao do angulo configurado.
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Destroi o projetil ao colidir com uma parede.
        if (int(self.x), int(self.y)) in self.game.map.world_map:
            self.destroyed = True
            return

        # Aplica dano ao jogador se o projetil atingir uma distancia de contato.
        if math.hypot(self.x - self.player.x, self.y - self.player.y) <= 0.45:
            self.player.get_damage(self.damage)
            self.destroyed = True
            return

        # Remove o projetil quando ele fica longe demais para nao gastar processamento.
        if math.hypot(self.x - self.player.x, self.y - self.player.y) > MAX_DEPTH + 4:
            self.destroyed = True
            return

        # Atualiza a projecao visual do projetil na tela.
        self.get_sprite()


class NPC(FrameSprite):
    def __init__(self, game, path='resources/sprites/npc/davy/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        # Inicializa um inimigo generico com animacoes e atributos base.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.load_animation_images('attack', self.images)
        self.death_images = self.load_animation_images('death', self.images)
        self.idle_images = self.load_animation_images('idle', self.images)
        self.pain_images = self.load_animation_images('pain', self.images)
        self.walk_images = self.load_animation_images('walk', self.images)

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100
        self.max_health = self.health
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False
        self.name = 'Enemy'
        self.overlay_render = False

    def load_single_scaled_image(self, path):
        # Carrega uma imagem unica e redimensiona conforme a escala do sprite.
        image = pg.image.load(resource_path(*path.split('/'))).convert_alpha()
        width = max(1, int(image.get_width() * self.SPRITE_SCALE))
        height = max(1, int(image.get_height() * self.SPRITE_SCALE))
        return pg.transform.smoothscale(image, (width, height))

    def load_animation_images(self, folder_name, fallback_images):
        # Tenta carregar imagens de uma pasta especifica da animacao.
        # Se a pasta nao existir, reutiliza as imagens de fallback.
        animation_path = self.path + f'/{folder_name}'
        if os.path.isdir(resource_path(*animation_path.split('/'))):
            return self.get_images(animation_path)
        return deque(fallback_images)

    def update(self):
        # Atualiza tempo de animacao, projecao visual e logica de IA do NPC.
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()
        # self.draw_ray_cast()

    def check_wall(self, x, y):
        # Retorna True se a celula nao for parede.
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        # Move o NPC apenas se nao houver parede no eixo correspondente.
        if self.check_wall(int(self.x + dx * self.size), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * self.size)):
            self.y += dy

    def movement(self):
        # Usa o pathfinding para perseguir o jogador pelo mapa.
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        # pg.draw.rect(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
        # Evita que dois NPCs tentem ocupar o mesmo tile de destino.
        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.y, next_x + 0.5 - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)

    def attack(self):
        # Executa o ataque apenas no frame correto da animacao.
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        # Reproduz a sequencia de morte quando o NPC ja nao esta vivo.
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        # Toca a animacao de dano e depois libera o NPC para voltar ao estado normal.
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        # Verifica se o disparo do jogador acertou o NPC atualmente alinhado no centro da tela.
        shot_active = self.game.player.shot or self.game.weapon.pending_damage
        if self.ray_cast_value and shot_active:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.weapon.consume_shot_hit()
                if self.should_react_to_hit():
                    self.pain = True
                self.health -= self.get_received_damage()
                self.check_health()

    def get_received_damage(self):
        # Define quanto dano esse NPC recebe ao ser atingido.
        return self.game.weapon.damage

    def should_react_to_hit(self):
        # Define se o NPC entra no estado de dor ao ser atingido.
        return True

    def check_health(self):
        # Marca o NPC como morto quando a vida chega a zero.
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self):
        # Controla a IA principal do NPC: detectar jogador, andar, atacar, sofrer dano ou morrer.
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()

            elif self.ray_cast_value:
                self.player_search_trigger = True

                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()

            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()

            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self):
        # Retorna a posicao do NPC em coordenadas inteiras do mapa.
        return int(self.x), int(self.y)

    def ray_cast_player_npc(self):
        # Faz um teste de linha de visao entre jogador e NPC usando ray casting.
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_v, wall_dist_h = 0, 0
        player_dist_v, player_dist_h = 0, 0

        ox, oy = self.game.player.pos
        x_map, y_map = self.game.player.map_pos

        ray_angle = self.theta

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # horizontals
        y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

        depth_hor = (y_hor - oy) / sin_a
        x_hor = ox + depth_hor * cos_a

        delta_depth = dy / sin_a
        dx = delta_depth * cos_a

        for i in range(MAX_DEPTH):
            tile_hor = int(x_hor), int(y_hor)
            if tile_hor == self.map_pos:
                player_dist_h = depth_hor
                break
            if tile_hor in self.game.map.world_map:
                wall_dist_h = depth_hor
                break
            x_hor += dx
            y_hor += dy
            depth_hor += delta_depth

        # verticals
        x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

        depth_vert = (x_vert - ox) / cos_a
        y_vert = oy + depth_vert * sin_a

        delta_depth = dx / cos_a
        dy = delta_depth * sin_a

        for i in range(MAX_DEPTH):
            tile_vert = int(x_vert), int(y_vert)
            if tile_vert == self.map_pos:
                player_dist_v = depth_vert
                break
            if tile_vert in self.game.map.world_map:
                wall_dist_v = depth_vert
                break
            x_vert += dx
            y_vert += dy
            depth_vert += delta_depth

        player_dist = max(player_dist_v, player_dist_h)
        wall_dist = max(wall_dist_v, wall_dist_h)

        if 0 < player_dist < wall_dist or not wall_dist:
            return True
        return False

    def draw_ray_cast(self):
        # Funcao auxiliar de depuracao para visualizar a linha entre NPC e jogador.
        pg.draw.circle(self.game.screen, 'red', (100 * self.x, 100 * self.y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(self.game.screen, 'orange', (100 * self.game.player.x, 100 * self.game.player.y),
                         (100 * self.x, 100 * self.y), 2)


class DavyNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/davy/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        # Inimigo basico que usa os atributos padrao da classe NPC.
        super().__init__(game, path, pos, scale, shift, animation_time)

class EsqueletoNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/esqueleto/0.png', pos=(10.5, 6.5),
                 scale=0.7, shift=0.27, animation_time=250):
        # Variante mais agressiva e rapida do inimigo base.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.max_health = self.health
        self.attack_damage = 25
        self.speed = 0.05
        self.accuracy = 0.35
        self.name = 'Esqueleto'

class AraraNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/arara/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        # Inimigo pesado com mais vida, maior alcance e dano consideravel.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.max_health = self.health
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25
        self.name = 'Arara'

    def attack(self):
        # A arara usa um dos dois sons principais de forma randomizada quando ataca.
        if self.animation_trigger:
            self.game.sound.play_arara_attack()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def check_health(self):
        # A morte da arara usa o terceiro audio dedicado.
        if self.health < 1:
            self.alive = False
            self.game.sound.play_arara_death()


class FinalBossNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/boss_final/boss.png', pos=(11.5, 16.5),
                 scale=5.4, shift=-0.28, animation_time=150):
        # Inicializa o boss final com sprites proprios, muita vida e logicas especiais de fase 2.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.idle_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss.png')])
        self.walk_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss-andando.png')])
        self.attack_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss-ataque.png')])
        self.pain_images = deque(self.idle_images)
        self.death_images = deque(self.idle_images)
        self.images = deque(self.idle_images)
        self.image = self.idle_images[0]
        self.attack_dist = 9
        self.health = 3200
        self.max_health = self.health
        self.attack_damage = 35
        self.speed = 0.02
        self.base_speed = 0.02
        self.phase_two_speed = 0.034
        self.accuracy = 0.45
        self.size = 28
        self.name = 'ENAD INHO'
        self.overlay_render = False
        self.projectile_damage = 35
        self.phase_two_triggered = False
        self.projectile_speed = 0.085
        self.phase_two_projectile_speed = 0.14
        self.phase_two_reflection = None
        self.phase_two_reflection_center = None
        self.phase_two_reflection_offset = (3.6, 0.0)
        self.last_real_attack_time = -1

    def set_phase_two_sprites(self):
        # Troca os sprites do boss para a aparencia exclusiva da fase 2.
        self.idle_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss-2fase.png')])
        self.walk_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss-andando-2fase.png')])
        self.attack_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_final/boss-atacando-2fase.png')])
        self.pain_images = deque(self.idle_images)
        self.images = deque(self.idle_images)
        self.image = self.idle_images[0]

    def can_spawn_boss_projectile(self, damage):
        # Limita quantos projeteis do boss podem existir ao mesmo tempo para evitar excesso.
        active_projectiles = [
            sprite for sprite in self.game.object_handler.sprite_list
            if isinstance(sprite, BossProjectile) and not sprite.destroyed
        ]
        if damage > 0:
            damaging_projectiles = [sprite for sprite in active_projectiles if sprite.damage > 0]
            return len(damaging_projectiles) < MAX_BOSS_PROJECTILES
        clone_projectiles = [sprite for sprite in active_projectiles if sprite.damage == 0]
        return len(clone_projectiles) < MAX_CLONE_PROJECTILES

    def get_received_damage(self):
        # Reduz o dano recebido do minigun para equilibrar a luta contra o boss.
        damage = self.game.weapon.damage
        if self.game.weapon.weapon_type == 'minigun':
            return max(1, int(damage * 0.22))
        return damage

    def should_react_to_hit(self):
        # O boss nao entra em animacao de dor a cada disparo recebido.
        return False

    def activate_phase_two(self):
        # Ativa a fase 2, aumenta velocidade/ataque e cria o reflexo do boss.
        self.phase_two_triggered = True
        self.speed = self.phase_two_speed
        self.projectile_speed = self.phase_two_projectile_speed
        self.set_phase_two_sprites()
        self.spawn_phase_two_reflection()

    def movement(self):
        # Na fase 2 o boss persegue diretamente o jogador sem usar pathfinding.
        if self.phase_two_triggered:
            angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.check_wall_collision(dx, dy)
            return
        super().movement()

    def check_wall_collision(self, dx, dy):
        # Na fase 2 o boss atravessa paredes; fora dela usa colisao normal.
        if self.phase_two_triggered:
            self.x += dx
            self.y += dy
            return
        super().check_wall_collision(dx, dy)

    def spawn_phase_two_reflection(self):
        # Cria o boss-reflexo na fase 2 apenas uma vez.
        if self.phase_two_reflection:
            return

        offset_x, offset_y = self.phase_two_reflection_offset
        self.phase_two_reflection_center = (
            self.x + offset_x / 2,
            self.y + offset_y / 2,
        )
        reflection = FinalBossReflection(
            self.game,
            original=self,
            mirror_center=self.phase_two_reflection_center,
            initial_pos=(self.x + offset_x, self.y + offset_y),
        )
        self.phase_two_reflection = reflection
        self.game.object_handler.add_npc(reflection)

    def clear_phase_two_reflection(self):
        # Remove o reflexo quando o boss morre ou a fase precisa ser encerrada.
        if self.phase_two_reflection:
            self.phase_two_reflection.destroyed = True
            self.phase_two_reflection.alive = False
            self.phase_two_reflection = None
        self.phase_two_reflection_center = None

    def check_health(self):
        # Reaproveita a checagem normal de vida e limpa o reflexo ao morrer.
        super().check_health()
        if not self.alive:
            self.clear_phase_two_reflection()

    def attack(self):
        # Dispara a bola de fogo do boss quando a animacao permite e o limite de projeteis nao foi excedido.
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy and self.can_spawn_boss_projectile(self.projectile_damage):
                self.last_real_attack_time = pg.time.get_ticks()
                projectile_angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
                projectile = BossProjectile(
                    self.game,
                    pos=(self.x, self.y),
                    angle=projectile_angle,
                    speed=self.projectile_speed,
                    damage=self.projectile_damage,
                )
                self.game.object_handler.add_sprite(projectile)


<<<<<<< HEAD
=======
class SecretBossNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/boss_secreto/boss-parado.png', pos=(11.5, 16.5),
                 scale=5.1, shift=-0.24, animation_time=110):
        # Boss secreto invocado por comando, com rajadas pesadas de bolas de fogo em varios angulos.
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.idle_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_secreto/boss-parado.png')])
        self.walk_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_secreto/boss-andando.png')])
        self.attack_images = deque([self.load_single_scaled_image('resources/sprites/npc/boss_secreto/boss-atack.png')])
        self.pain_images = deque(self.idle_images)
        self.death_images = deque(self.idle_images)
        self.images = deque(self.idle_images)
        self.image = self.idle_images[0]
        self.attack_dist = 12
        self.health = 4800
        self.max_health = self.health
        self.attack_damage = 40
        self.speed = 0.026
        self.accuracy = 1.0
        self.size = 30
        self.name = 'PEGADINHA'
        self.overlay_render = False
        self.projectile_damage = 35
        self.projectile_speed = 0.085
        self.last_attack_time = -1

    def can_spawn_secret_projectiles(self):
        # Reaproveita um limite mais alto de projeteis por existirem varios bosses ao mesmo tempo.
        active_projectiles = [
            sprite for sprite in self.game.object_handler.sprite_list
            if isinstance(sprite, BossProjectile) and not sprite.destroyed
        ]
        return len(active_projectiles) < max(MAX_BOSS_PROJECTILES * 4, 40)

    def should_react_to_hit(self):
        # O boss secreto nao pausa para animacao de dor.
        return False

    def attack(self):
        # Dispara uma bola de fogo na mesma logica do boss final.
        if not self.animation_trigger:
            return

        if self.animation_time_prev == self.last_attack_time:
            return

        if not self.can_spawn_secret_projectiles():
            return

        self.last_attack_time = self.animation_time_prev
        self.game.sound.npc_shot.play()
        projectile_angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
        projectile = BossProjectile(
            self.game,
            pos=(self.x, self.y),
            angle=projectile_angle,
            speed=self.projectile_speed,
            damage=self.projectile_damage,
        )
        self.game.object_handler.add_sprite(projectile)


>>>>>>> 51e6147 (Initial project import and gameplay updates)
class FinalBossReflection(SpriteObject):
    def __init__(self, game, original, mirror_center, initial_pos):
        # Cria o reflexo do boss final que espelha posicao e acoes na fase 2.
        super().__init__(
            game,
            path='resources/sprites/npc/boss_final/boss.png',
            pos=initial_pos,
            scale=original.SPRITE_SCALE,
            shift=original.SPRITE_HEIGHT_SHIFT,
        )
        self.original = original
        self.mirror_center = mirror_center
        self.alive = True
        self.destroyed = False
        self.projectile_speed = original.phase_two_projectile_speed
        self.projectile_damage = original.projectile_damage
        self.name = original.name
        self.attack_dist = original.attack_dist
        self.accuracy = original.accuracy
        self.last_attack_time = -1

    @property
    def map_pos(self):
        # Retorna a posicao do reflexo em coordenadas inteiras do mapa.
        return int(self.x), int(self.y)

    def sync_with_original(self):
        # Mantem o reflexo sincronizado com o boss real, espelhando sua posicao e sprite atual.
        if not self.original.alive:
            self.destroyed = True
            self.alive = False
            return

        if self.mirror_center is None:
            self.mirror_center = (self.original.x, self.original.y)

        center_x, center_y = self.mirror_center
        target_x = center_x * 2 - self.original.x
        target_y = center_y * 2 - self.original.y

        self.x = target_x
        self.y = target_y
        self.image = self.original.image
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()

    def attack(self):
        # Faz o reflexo disparar projeteis em sincronia com o boss, respeitando os limites globais.
        if self.original.animation_time_prev == self.last_attack_time:
            return

        if not self.original.animation_trigger:
            return

        if not self.original.can_spawn_boss_projectile(self.projectile_damage):
            return

        if self.original.ray_cast_value and self.original.dist < self.attack_dist and random() < self.accuracy:
            self.last_attack_time = self.original.animation_time_prev
            projectile_angle = math.atan2(self.game.player.y - self.y, self.game.player.x - self.x)
            projectile = BossProjectile(
                self.game,
                pos=(self.x, self.y),
                angle=projectile_angle,
                speed=self.projectile_speed,
                damage=self.projectile_damage,
            )
            self.game.object_handler.add_sprite(projectile)

    def update(self):
        # Atualiza posicao, projecao visual e ataque do reflexo.
        self.sync_with_original()
        if self.destroyed:
            return
        self.get_sprite()
        self.attack()
