from sprite_object import *


class Weapon(FrameSprite):
    def __init__(self, game):
        # Configuracoes de cada tipo de arma disponivel no jogo.
        self.config = {
            'hand': {
                'path': 'resources/hub/hand.png',
                'animated': False,
                'scale': 0.55,
                'animation_time': 120,
                'damage': 0,
                'can_shoot': False,
                'y_offset': 60,
            },
            'shotgun': {
                'path': 'resources/sprites/weapon/shotgun/0.png',
                'animated': True,
                'scale': 0.4,
                'animation_time': 90,
                'damage': 50,
                'can_shoot': True,
                'y_offset': 0,
            },
            'special': {
                'path': 'resources/sprites/special/special-1.png',
                'animated': False,
                'scale': 0.4,
                'animation_time': 45,
                'damage': 50,
                'can_shoot': True,
                'y_offset': 0,
                'shot_path': 'resources/sprites/special/special-2.png',
                'shot_duration': 65,
                'cooldown': 65,
            },
            'minigun': {
                'path': 'resources/sprites/minigun/minigun-0.png',
                'animated': False,
                'scale': 1.0,
                'animation_time': 55,
                'damage': 34,
                'can_shoot': True,
                'y_offset': 220,
                'idle_paths': [
                    'resources/sprites/minigun/minigun-0.png',
                    'resources/sprites/minigun/minigun-1.png',
                ],
                'cooldown': 55,
            },
        }
        # Usa a configuracao da shotgun para inicializar a classe base FrameSprite.
        shotgun_config = self.config['shotgun']
        super().__init__(
            game=game,
            path=shotgun_config['path'],
            scale=shotgun_config['scale'],
            animation_time=shotgun_config['animation_time']
        )
        # Estado atual da arma equipada e seus controles internos.
        self.weapon_type = 'hand'
        self.reloading = False
        self.damage = 0
        self.can_shoot = False
        self.frame_counter = 0
        self.num_images = 0
        self.base_weapon_pos = (0, 0)
        self.weapon_pos = (0, 0)
        self.bob_phase = 0
        self.special_active = False
        self.special_end_time = 0
        self.special_cooldown_until = 0
        self.special_shot_until = 0
        self.special_idle_image = None
        self.special_shot_image = None
        self.minigun_images = []
        self.minigun_frame_index = 0
        self.minigun_recoil = 0.0
        self.minigun_recoil_side = 1
        self.pending_damage = False
        # Equipa a arma inicial do jogador.
        self.set_weapon(self.weapon_type)

    def load_weapon_images(self, weapon_type):
        # Carrega e redimensiona as imagens da arma, animadas ou estaticas.
        config = self.config[weapon_type]
        path = config['path']
        scale = config['scale']
        if config['animated']:
            source_images = self.get_images(path.rsplit('/', 1)[0])
        else:
            source_images = deque([pg.image.load(resource_path(*path.split('/'))).convert_alpha()])

        scaled_images = deque()
        for img in source_images:
            width = max(1, int(img.get_width() * scale))
            height = max(1, int(img.get_height() * scale))
            scaled_images.append(pg.transform.smoothscale(img, (width, height)))
        return scaled_images

    def load_scaled_image(self, path, scale):
        # Carrega uma unica imagem e redimensiona conforme a escala informada.
        image = pg.image.load(resource_path(*path.split('/'))).convert_alpha()
        width = max(1, int(image.get_width() * scale))
        height = max(1, int(image.get_height() * scale))
        return pg.transform.smoothscale(image, (width, height))

    def set_weapon(self, weapon_type):
        # Aplica toda a configuracao visual e funcional da arma escolhida.
        self.weapon_type = weapon_type
        config = self.config[weapon_type]
        self.animation_time = config['animation_time']
        self.images = self.load_weapon_images(weapon_type)
        self.image = self.images[0]
        self.special_idle_image = None
        self.special_shot_image = None
        self.minigun_images = []
        self.minigun_frame_index = 0
        self.minigun_recoil = 0.0

        # Configura recursos visuais exclusivos da arma especial e da minigun.
        if weapon_type == 'special':
            self.special_idle_image = self.images[0]
            self.special_shot_image = self.load_scaled_image(config['shot_path'], config['scale'])
        elif weapon_type == 'minigun':
            self.minigun_images = [
                self.load_scaled_image(path, config['scale'])
                for path in config['idle_paths']
            ]
            self.image = self.minigun_images[0]

        # Posiciona a arma na tela e atualiza atributos de dano e disparo.
        y_offset = config.get('y_offset', 0)
        self.base_weapon_pos = (HALF_WIDTH - self.image.get_width() // 2, HEIGHT - self.image.get_height() + y_offset)
        self.weapon_pos = self.base_weapon_pos
        self.damage = config['damage']
        self.can_shoot = config['can_shoot']
        self.reloading = False
        self.frame_counter = 0
        self.num_images = len(self.images)

    def equip_shotgun(self):
        # Equipa a shotgun se o jogador ainda nao estiver com uma arma mais avancada.
        if not self.special_active and self.weapon_type not in ('shotgun', 'minigun'):
            self.set_weapon('shotgun')

    def equip_minigun(self):
        # Equipa a minigun e cancela qualquer estado especial anterior.
        self.special_active = False
        self.special_end_time = 0
        self.special_cooldown_until = 0
        self.special_shot_until = 0
        self.pending_damage = False
        self.game.player.speed_multiplier = 1.0
        self.set_weapon('minigun')

    def activate_racao_boost(self):
        # Ativa o modo especial temporario, aumentando mobilidade e trocando a arma.
        if self.weapon_type == 'minigun':
            return
        self.special_active = True
        self.special_end_time = pg.time.get_ticks() + 7000
        self.special_cooldown_until = 0
        self.special_shot_until = 0
        self.pending_damage = False
        self.game.player.speed_multiplier = 1.8
        self.set_weapon('special')
        self.game.sound.play_boost_theme()

    def deactivate_racao_boost(self):
        # Encerra o modo especial e restaura a arma e a musica adequadas.
        if not self.special_active:
            return
        self.special_active = False
        self.special_end_time = 0
        self.special_cooldown_until = 0
        self.special_shot_until = 0
        self.pending_damage = False
        self.game.player.speed_multiplier = 1.0
        if self.weapon_type != 'minigun':
            self.set_weapon('shotgun')
        final_boss = getattr(self.game.object_handler, 'final_boss', None)
        if final_boss and final_boss.alive:
            self.game.sound.play_boss_theme()
        else:
            self.game.sound.play_main_theme()

    def can_fire(self):
        # Verifica se a arma atual pode disparar neste instante.
        if not self.can_shoot:
            return False
        if self.weapon_type == 'minigun':
            return pg.time.get_ticks() >= self.special_cooldown_until
        if self.special_active:
            return pg.time.get_ticks() >= self.special_cooldown_until
        return not self.game.player.shot and not self.reloading

    def start_shot(self):
        # Inicia o disparo de acordo com a arma equipada.
        if self.weapon_type == 'minigun':
            time_now = pg.time.get_ticks()
            self.pending_damage = True
            self.reloading = False
            self.special_cooldown_until = time_now + self.config['minigun']['cooldown']
            # Aplica recuo e alterna o frame visual da minigun.
            self.minigun_recoil = 18
            self.minigun_recoil_side *= -1
            if self.minigun_images:
                self.minigun_frame_index = (self.minigun_frame_index + 1) % len(self.minigun_images)
                self.image = self.minigun_images[self.minigun_frame_index]
            return

        if self.special_active:
            # A arma especial troca temporariamente para a imagem de disparo e usa cooldown curto.
            time_now = pg.time.get_ticks()
            config = self.config['special']
            self.pending_damage = True
            self.reloading = False
            self.image = self.special_shot_image
            self.special_shot_until = time_now + config['shot_duration']
            self.special_cooldown_until = time_now + config['cooldown']
            return

        # A shotgun usa a animacao completa de recarga/disparo.
        self.reloading = True

    def consume_shot_hit(self):
        # Marca que o disparo ja acertou um alvo e nao deve aplicar dano novamente.
        self.game.player.shot = False
        self.pending_damage = False

    def clear_pending_damage(self):
        # Limpa dano pendente se nenhum inimigo foi acertado naquele frame/processo.
        if self.pending_damage:
            self.pending_damage = False
            self.game.player.shot = False

    def animate_shot(self):
        # Reproduz a animacao da shotgun enquanto ela esta recarregando/disparando.
        if self.reloading and self.can_shoot:
            self.game.player.shot = False
            if self.animation_trigger:
                self.images.rotate(-1)
                self.image = self.images[0]
                self.frame_counter += 1
                if self.frame_counter == self.num_images:
                    self.reloading = False
                    self.frame_counter = 0

    def update_special_state(self):
        # Atualiza a duracao e o estado visual da arma especial.
        if not self.special_active:
            return

        # No modo desenvolvedor, mantem o especial ativo sem encerrar o buff.
        if self.game.dev_mode:
            if self.special_idle_image is not None and pg.time.get_ticks() >= self.special_shot_until:
                self.image = self.special_idle_image
            return

        # Fora do modo dev, encerra o especial ao fim do tempo.
        time_now = pg.time.get_ticks()
        if time_now >= self.special_end_time:
            self.deactivate_racao_boost()
            return

        # Restaura a imagem ociosa quando o disparo especial termina.
        if time_now >= self.special_shot_until and self.special_idle_image is not None:
            self.image = self.special_idle_image

    def update_minigun_animation(self):
        # Se o jogador parar de atirar, volta a minigun para o frame base.
        if self.weapon_type != 'minigun' or not self.minigun_images:
            return
        if not pg.mouse.get_pressed()[0]:
            self.image = self.minigun_images[0]
            self.minigun_frame_index = 0

    def animate_movement(self):
        # Cria a animacao de balanco da arma e o recuo visual da minigun.
        base_x, base_y = self.base_weapon_pos
        recoil_x = 0
        recoil_y = 0
        if self.weapon_type == 'minigun' and self.minigun_recoil > 0:
            recoil_x = int(self.minigun_recoil_side * self.minigun_recoil * 0.35)
            recoil_y = int(self.minigun_recoil)
            self.minigun_recoil = max(0.0, self.minigun_recoil - self.game.delta_time * 0.045)
        if self.game.player.is_moving:
            # Ajusta velocidade e amplitude do balanco conforme a arma equipada.
            speed = 0.015 if self.weapon_type == 'hand' else 0.02
            amplitude_x = 18 if self.weapon_type == 'hand' else 12
            amplitude_y = 14 if self.weapon_type == 'hand' else 10
            if self.weapon_type == 'special':
                speed = 0.03
                amplitude_x = 16
                amplitude_y = 12
            elif self.weapon_type == 'minigun':
                speed = 0.012
                amplitude_x = 9
                amplitude_y = 6
            self.bob_phase += self.game.delta_time * speed
            offset_x = int(math.sin(self.bob_phase) * amplitude_x)
            offset_y = int(abs(math.cos(self.bob_phase)) * amplitude_y)
            self.weapon_pos = (base_x + offset_x + recoil_x, base_y + offset_y + recoil_y)
        else:
            self.bob_phase = 0
            self.weapon_pos = (base_x + recoil_x, base_y + recoil_y)

    def draw(self):
        # Desenha a arma equipada na tela do jogador.
        self.game.screen.blit(self.image, self.weapon_pos)

    def update(self):
        # Atualiza todos os estados visuais e funcionais da arma a cada frame.
        self.check_animation_time()
        self.update_special_state()
        self.update_minigun_animation()
        self.animate_shot()
        self.animate_movement()
