# Jhoon

Jhoon é um jogo em primeira pessoa feito em Python com Pygame, inspirado em clássicos como DOOM. O projeto utiliza raycasting para simular um ambiente 3D, com combate, inimigos, itens coletáveis, armas especiais e uma batalha contra chefe final.

## Visão Geral

O jogo usa uma estrutura de mapa 2D com projeção em pseudo-3D por meio de raycasting. O jogador explora o cenário, enfrenta inimigos, coleta power-ups, desbloqueia armas mais fortes e avança até o confronto final.

## Funcionalidades

- Renderização pseudo-3D com raycasting
- Movimentação em primeira pessoa com controle por mouse
- Sistema de armas com animações
- Shotgun, modo especial e minigun
- Inimigos com lógica de movimentação e ataque
- Itens coletáveis e objetos interagíveis
- Chefe final com segunda fase
- HUD com vida, minimapa, mensagens de interação e barra do chefe
- Menu inicial, tela de história, transição de introdução e menu de desenvolvedor
- Sons e troca dinâmica de música conforme o momento do jogo

## Controles

- `W`, `A`, `S`, `D`: movimentação
- `Mouse`: mover a câmera/visão
- `Botão esquerdo do mouse`: atirar
- `E`: interagir
- `Enter`: avançar nas telas de menu e história
- `Escape`: abrir o menu de desenvolvedor durante o jogo
- `D`: ativar ou desativar o modo desenvolvedor dentro do menu dev

## Fluxo do Jogo

1. Inicie o jogo pelo menu principal.
2. Explore o mapa e elimine os inimigos comuns.
3. Colete a shotgun e os itens de boost especial.
4. Limpe a horda para liberar a minigun.
5. Pegue a minigun para iniciar a luta contra o chefe final.
6. Derrote o chefe para chegar à tela de vitória.

## Estrutura do Projeto

- [`main.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/main.py): loop principal e controle geral do jogo
- [`player.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/player.py): movimentação, tiro, vida e controle do jogador
- [`weapon.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/weapon.py): estados das armas, animações, recoil e habilidades especiais
- [`raycasting.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/raycasting.py): lógica de projeção das paredes e renderização pseudo-3D
- [`map.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/map.py): definição do mapa e colisões
- [`sprite_object.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/sprite_object.py): sprites base, sprites animados, pickups e interações
- [`npc.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/npc.py): inteligência dos inimigos, movimentação, ataques e comportamento do chefe
- [`object_handler.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/object_handler.py): criação e atualização de entidades, progressão e condição de vitória
- [`object_renderer.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/object_renderer.py): HUD, plano de fundo, minimapa, barra do chefe e desenho dos objetos
- [`sound.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/sound.py): efeitos sonoros e controle das músicas
- [`menu.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/menu.py): telas de menu, introdução, história e menu dev
- [`settings.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/settings.py): constantes e configurações gerais
- [`pathfinding.py`](/abs/path/c:/Users/jubit/OneDrive/Desktop/Jhoon/pathfinding.py): apoio à navegação dos inimigos

## Requisitos

- Python 3.10 ou superior
- Pygame

Atualmente, o projeto lista:

```txt
pygame
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Recursos Utilizados

O jogo utiliza arquivos locais da pasta `resources/`, incluindo:

- texturas de parede
- elementos de HUD
- imagens do menu
- sprites de inimigos
- sprites de armas
- efeitos sonoros e músicas
