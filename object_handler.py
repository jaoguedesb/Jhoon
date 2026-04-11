from sprite_object import *
from npc import *
from random import choices, randrange
import math


class ObjectHandler:
    def __init__(self, game):
        # Guarda a referencia do jogo e inicializa listas de sprites e NPCs.
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        # Caminhos base usados para recursos graficos.
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        add_sprite = self.add_sprite
        # Armazena tiles ocupados por NPCs vivos para evitar sobreposicao.
        self.npc_positions = {}
        # Controla estado do boss final e da progressao da fase.
        self.final_boss = None
        self.final_boss_spawned = False
        self.horde_cleared = False
        self.minigun_pickup = None
        self.interaction_message = ''

        # Define quantidade e distribuicao inicial de inimigos comuns.
        self.enemies = 20
        self.npc_types = [DavyNPC, EsqueletoNPC, AraraNPC]
        self.weights = [70, 20, 10]
        # Area reservada para nao gerar inimigos perto demais da regiao inicial.
        self.restricted_area = {(i, j) for i in range(10) for j in range(10)}
        self.spawn_npc()

        # Adiciona sprites decorativos e luzes do cenario.
        add_sprite(SpriteObject(game))
        add_sprite(SpriteObject(game, pos=(1.5, 1.5)))
        add_sprite(SpriteObject(game, pos=(1.5, 7.5)))
        add_sprite(SpriteObject(game, pos=(5.5, 3.25)))
        add_sprite(SpriteObject(game, pos=(5.5, 4.75)))
        add_sprite(SpriteObject(game, pos=(7.5, 2.5)))
        add_sprite(SpriteObject(game, pos=(7.5, 5.5)))
        add_sprite(SpriteObject(game, pos=(14.5, 1.5)))
        add_sprite(SpriteObject(game, pos=(14.5, 4.5)))
        add_sprite(SpriteObject(game, pos=(14.5, 24.5)))
        add_sprite(SpriteObject(game, pos=(14.5, 30.5)))
        add_sprite(SpriteObject(game, pos=(1.5, 30.5)))
        add_sprite(SpriteObject(game, pos=(1.5, 24.5)))
        add_sprite(PickupSprite(
            game,
            path='resources/hub/cat.png',
            pos=(5.2, 4.0),
            scale=0.22,
            shift=0.9,
            pickup_distance=0.9,
            on_pickup=self.game.weapon.equip_shotgun,
        ))
        # Espalha pickups do bonus especial pelo mapa.
        self.spawn_racao()

    def spawn_npc(self):
        # Gera a horda inicial de inimigos em posicoes livres do mapa.
        for _ in range(self.enemies):
            npc = choices(self.npc_types, self.weights)[0]
            x, y = self.get_random_free_tile(self.restricted_area)
            self.add_npc(npc(self.game, pos=(x + 0.5, y + 0.5)))

    def get_random_free_tile(self, blocked_tiles=None):
        # Procura aleatoriamente um tile que nao seja parede nem bloqueado.
        blocked_tiles = set(blocked_tiles or ())
        pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
        while pos in self.game.map.world_map or pos in blocked_tiles:
            pos = x, y = randrange(self.game.map.cols), randrange(self.game.map.rows)
        return x, y

    def get_tile_in_front_of_player(self, distance=2.2):
        # Tenta encontrar uma posicao livre a frente do jogador.
        px, py = self.game.player.pos
        angle = self.game.player.angle
        target_x = px + math.cos(angle) * distance
        target_y = py + math.sin(angle) * distance
        tile = (int(target_x), int(target_y))
        if tile not in self.game.map.world_map:
            return target_x, target_y

        for step in (1.8, 1.4, 1.0, 2.8):
            target_x = px + math.cos(angle) * step
            target_y = py + math.sin(angle) * step
            tile = (int(target_x), int(target_y))
            if tile not in self.game.map.world_map:
                return target_x, target_y
        x, y = self.get_random_free_tile(self.restricted_area)
        return x + 0.5, y + 0.5

    def spawn_racao(self, amount=5):
        # Gera pickups de racao em tiles livres e nao ocupados.
        racao_path = 'resources/sprites/racao/racao-0.png'
        occupied_tiles = {(int(sprite.x), int(sprite.y)) for sprite in self.sprite_list}
        occupied_tiles.update({(int(npc.x), int(npc.y)) for npc in self.npc_list})
        occupied_tiles.add(self.game.player.map_pos)
        occupied_tiles.add((5, 4))

        for _ in range(amount):
            x, y = self.get_random_free_tile(occupied_tiles | self.restricted_area)
            occupied_tiles.add((x, y))
            self.add_sprite(AnimatedPickupSprite(
                self.game,
                path=racao_path,
                pos=(x + 0.5, y + 0.5),
                on_pickup=self.game.weapon.activate_racao_boost,
                scale=0.35,
                shift=0.55,
                pickup_distance=0.75,
                animation_time=140,
            ))

    def spawn_final_boss(self):
        # Cria o boss final em um tile livre quando ele for liberado.
        occupied_tiles = {(int(sprite.x), int(sprite.y)) for sprite in self.sprite_list}
        occupied_tiles.update({(int(npc.x), int(npc.y)) for npc in self.npc_list if npc.alive})
        occupied_tiles.add(self.game.player.map_pos)
        x, y = self.get_random_free_tile(occupied_tiles | self.restricted_area)
        self.final_boss = FinalBossNPC(self.game, pos=(x + 0.5, y + 0.5))
        self.final_boss_spawned = True
        self.add_npc(self.final_boss)
        # Troca musica e ceu para o contexto do boss.
        self.game.sound.play_boss_theme()
        self.game.object_renderer.set_default_sky()

    def spawn_minigun_pickup(self):
        # Cria o pickup da minigun perto do jogador depois que a horda e derrotada.
        x, y = self.get_tile_in_front_of_player()
        self.minigun_pickup = SequenceAnimatedPickupSprite(
            self.game,
            image_paths=[
                'resources/sprites/minigun/minigun-lado-0-Photoroom.png',
                'resources/sprites/minigun/minigun-lado-1-Photoroom.png',
                'resources/sprites/minigun/minigun-lado-2-Photoroom.png',
                'resources/sprites/minigun/minigun-lado-3-Photoroom.png',
            ],
            pos=(x, y),
            on_pickup=self.pick_minigun,
            scale=0.95,
            shift=0.2,
            pickup_distance=0.95,
            animation_time=100,
        )
        self.add_sprite(self.minigun_pickup)

    def pick_minigun(self):
        # Equipa a minigun e, se necessario, libera a luta com o boss final.
        self.game.weapon.equip_minigun()
        self.minigun_pickup = None
        self.interaction_message = ''
        if not self.final_boss_spawned:
            self.spawn_final_boss()

    def try_interact(self):
        # Espaco reservado para futuras interacoes do jogador com objetos do mapa.
        return

    def check_win(self):
        # Verifica se todos os inimigos comuns foram derrotados para liberar a proxima etapa.
        alive_enemies = [npc for npc in self.npc_list if npc.alive and npc is not self.final_boss]
        if not alive_enemies and not self.horde_cleared:
            self.horde_cleared = True
            self.spawn_minigun_pickup()

        # Quando o boss final morre, exibe a tela de vitoria e reinicia o jogo.
        if self.horde_cleared and self.final_boss_spawned and (not self.final_boss or not self.final_boss.alive):
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def update(self):
        # Atualiza o conjunto de tiles ocupados por NPCs vivos.
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        # Atualiza todos os sprites do mapa, pickups e projeteis.
        [sprite.update() for sprite in self.sprite_list]
        # Remove da lista os sprites que ja foram coletados ou destruidos.
        self.sprite_list = [
            sprite for sprite in self.sprite_list
            if not getattr(sprite, 'picked', False) and not getattr(sprite, 'destroyed', False)
        ]
        # Atualiza todos os NPCs.
        [npc.update() for npc in self.npc_list]
        # Detecta automaticamente a transicao para a fase 2 do boss.
        if self.final_boss and self.final_boss.alive:
            if (not self.final_boss.phase_two_triggered
                    and self.final_boss.health <= self.final_boss.max_health * 0.5):
                self.final_boss.activate_phase_two()
                self.game.sound.play_boss_phase_two_theme()
                self.game.object_renderer.set_boss_phase_two_sky()
        # Quando o boss morre, restaura o ceu e a musica apropriada.
        if self.final_boss and not self.final_boss.alive:
            self.final_boss = None
            self.game.object_renderer.set_default_sky()
            if self.game.weapon.special_active:
                self.game.sound.play_boost_theme()
            else:
                self.game.sound.play_main_theme()
        # Exibe mensagem de interacao quando a minigun esta disponivel.
        if self.minigun_pickup:
            self.interaction_message = 'Pegue a minigun'
        else:
            self.interaction_message = ''
        # Limpa marcadores de dano pendente e verifica condicao de vitoria.
        self.game.weapon.clear_pending_damage()
        self.check_win()

    def add_npc(self, npc):
        # Adiciona um novo NPC ao gerenciador.
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        # Adiciona um novo sprite ao gerenciador.
        self.sprite_list.append(sprite)
