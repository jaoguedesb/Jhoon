from settings import *
import pygame as pg
import math


class Player:
    def __init__(self, game):
        # Guarda a referencia do jogo e inicializa o estado do jogador.
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        # shot indica se houve um disparo recente do jogador.
        self.shot = False
        # Vida atual do jogador.
        self.health = PLAYER_MAX_HEALTH
        # rel armazena o deslocamento recente do mouse no eixo X.
        self.rel = 0
        # Indica se o jogador esta se movendo no frame atual.
        self.is_moving = False
        # Quando ativo, impede a perda de vida.
        self.infinite_health = False
        # Controla o tempo entre recuperacoes automaticas de vida.
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        # Multiplicador de velocidade usado por buffs e modos especiais.
        self.speed_multiplier = 1.0
        # Corrige a velocidade em movimento diagonal para nao ficar mais rapido.
        self.diag_move_corr = 1 / math.sqrt(2)

    def recover_health(self):
        # Recupera 1 ponto de vida depois de um certo intervalo, ate o maximo.
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        # Verifica se ja passou o tempo necessario para recuperar vida novamente.
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        # Mostra a tela de derrota e reinicia o jogo quando a vida acaba.
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        # Aplica dano ao jogador, a menos que o modo de vida infinita esteja ativo.
        if self.infinite_health:
            self.health = PLAYER_MAX_HEALTH
            return
        self.health -= damage
        # Exibe efeito visual e sonoro de dano.
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        # Trata eventos unicos do jogador, como clique para atirar e tecla de interacao.
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.try_shoot()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_e:
                self.game.object_handler.try_interact()

    def try_shoot(self):
        # Tenta atirar com a arma atual se ela puder disparar naquele momento.
        if self.game.weapon.can_fire():
            if self.game.weapon.weapon_type == 'minigun':
                self.game.sound.meca_shot.play()
            else:
                self.game.sound.shotgun.play()
            self.shot = True
            self.game.weapon.start_shot()

    def movement(self):
        # Calcula o deslocamento do jogador com base nas teclas pressionadas e no angulo atual.
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        self.is_moving = False
        speed = PLAYER_SPEED * self.game.delta_time * self.speed_multiplier
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        # Lê o teclado e monta o vetor de movimento.
        keys = pg.key.get_pressed()
        num_key_pressed = 0
        if keys[pg.K_w]:
            num_key_pressed += 1
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            num_key_pressed += 1
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            num_key_pressed += 1
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            num_key_pressed += 1
            dx += -speed_sin
            dy += speed_cos

        # Corrige o deslocamento para que diagonais nao fiquem mais rapidas.
        if num_key_pressed > 1:
            dx *= self.diag_move_corr
            dy *= self.diag_move_corr
        if num_key_pressed > 0:
            self.is_moving = True

        # Aplica o movimento respeitando colisao com paredes.
        self.check_wall_collision(dx, dy)

        # Mantem o angulo sempre dentro do intervalo de uma volta completa.
        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau

    def check_wall(self, x, y):
        # Retorna True se a celula nao for uma parede do mapa.
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        # Move o jogador apenas se nao houver parede no caminho.
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def draw(self):
        # Funcao de depuracao para desenhar o jogador e sua direcao no mapa 2D.
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100),
                    (self.x * 100 + WIDTH * math.cos(self.angle),
                     self.y * 100 + WIDTH * math. sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        # Controla a rotacao da camera/jogador pelo movimento horizontal do mouse.
        mx, _ = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            # Reposiciona o mouse para manter o controle continuo de rotacao.
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        rel_x, _ = pg.mouse.get_rel()
        rel_x = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, rel_x))
        self.rel = rel_x
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        # Atualiza todas as funcoes principais do jogador a cada frame.
        if self.infinite_health:
            self.health = PLAYER_MAX_HEALTH
        self.movement()
        self.mouse_control()
        # Mantem armas automaticas disparando enquanto o botao do mouse estiver pressionado.
        if (self.game.weapon.special_active or self.game.weapon.weapon_type == 'minigun') and pg.mouse.get_pressed()[0]:
            self.try_shoot()
        self.recover_health()

    @property
    def pos(self):
        # Retorna a posicao atual do jogador em coordenadas continuas.
        return self.x, self.y

    @property
    def map_pos(self):
        # Retorna a posicao atual do jogador em coordenadas inteiras do mapa.
        return int(self.x), int(self.y)
