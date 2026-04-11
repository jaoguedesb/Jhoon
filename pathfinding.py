from collections import deque
from functools import lru_cache


class PathFinding:
    def __init__(self, game):
        # Guarda a referencia do jogo e o mapa base usado para navegacao.
        self.game = game
        self.map = game.map.mini_map
        # Define as direcoes permitidas para movimentacao no grafo, incluindo diagonais.
        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, -1], [1, 1], [-1, 1]
        # graph armazenara, para cada tile livre, quais tiles vizinhos podem ser acessados.
        self.graph = {}
        # Monta o grafo de navegacao a partir do mapa.
        self.get_graph()

    @lru_cache
    def get_path(self, start, goal):
        # Retorna o proximo passo que leva do ponto inicial ate o alvo.
        # O resultado fica em cache para evitar recalculos repetidos.
        if start not in self.graph or goal not in self.graph:
            # Se um dos pontos nao existir no grafo, mantem a posicao atual.
            return start
        self.visited = self.bfs(start, goal, self.graph)
        path = [goal]
        step = self.visited.get(goal, start)

        # Reconstrui o caminho voltando do objetivo ate o inicio.
        while step and step != start:
            path.append(step)
            step = self.visited[step]
        # Retorna apenas o primeiro passo necessario para seguir o caminho.
        return path[-1]

    def bfs(self, start, goal, graph):
        # Executa busca em largura para encontrar um caminho entre inicio e objetivo.
        queue = deque([start])
        visited = {start: None}

        while queue:
            cur_node = queue.popleft()
            if cur_node == goal:
                break
            # Recupera os vizinhos acessiveis do no atual.
            next_nodes = graph.get(cur_node, [])

            for next_node in next_nodes:
                # Evita revisitar nos e tambem evita tiles ocupados por outros NPCs.
                if next_node not in visited and next_node not in self.game.object_handler.npc_positions:
                    queue.append(next_node)
                    visited[next_node] = cur_node
        return visited

    def get_next_nodes(self, x, y):
        # Retorna os vizinhos livres ao redor de uma celula.
        return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]

    def get_graph(self):
        # Percorre o mapa e cria o grafo apenas para os tiles vazios.
        for y, row in enumerate(self.map):
            for x, col in enumerate(row):
                if not col:
                    self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)
