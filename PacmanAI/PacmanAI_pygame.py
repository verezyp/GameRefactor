from PacmanAI.PacmanAI_Interface import BoardIface, Entity, Drawer, Controller
from queue import PriorityQueue
import pygame
from typing import Dict, Tuple


class Board(BoardIface):
    _board = None
    _board_height = None
    _board_width = None

    def __init__(self, grid_height: int, grid_width: int) -> None:
        self._board = []
        power_pellets = [(5, 5), (grid_width - 6, 5), (5, grid_height - 6), (grid_width - 6, grid_height - 6)]
        for y in range(grid_height):
            row = []
            for x in range(grid_width):
                if x == 0 or x == grid_width - 1 or y == 0 or y == grid_height - 1:
                    row.append('#')
                elif (x, y) in power_pellets:
                    row.append('O')
                else:
                    row.append('.')
            self._board.append(row)
        self._board_height = grid_height
        self._board_width = grid_width

    def reset(self) -> None:
        self.__init__(self._board_height, self._board_width)

    def get_ceil(self, x, y) -> str:
        match self._board[x][y]:
            case '#':
                return "BORDER"
            case 'O':
                return "POWER_P"
            case '.':
                return "DEFAULT_P"
            case "EMPTY":
                return "EMPTY"

    def get_params(self) -> Tuple[int, int]:
        return self._board_height, self._board_width

    def set_ceil(self, x_pos: int, y_pos: int, subj: str) -> None:
        self._board[x_pos][y_pos] = subj

    def is_empty(self) -> bool:
        if all(all(x == "EMPTY" or x == "#" for x in row) for row in self._board):
            return True
        return False


class Pacman(Entity):
    _x_pos = None
    _y_pos = None
    _score = None
    _color = None
    _power_pellet_timer = 0
    _stats = {"HP": 3, "SCORE": 0, "LEVEL": 1, "AI_STATE": False}
    _default_color = None

    def __init__(self) -> None:
        self._x_pos = 1
        self._y_pos = 1
        self._color = self._default_color = "YELLOW"
        self._score = 0

    def movement(self, field: BoardIface, dx: int = 0, dy: int = 0, pacman_obj=None, ghosts_list=None) -> None:
        old_x, old_y = self.get_position()
        if not (self.get_stats()["AI_STATE"]):
            new_x, new_y = old_x, old_y
            new_x += dx
            new_y += dy
            ceil = field.get_ceil(new_y, new_x)
            if ceil != "BORDER":
                self.set_position(new_x, new_y)
                field.set_ceil(old_y, old_x, "EMPTY")
                if ceil == "DEFAULT_P":
                    self._stats["SCORE"] += 10
                elif ceil == "POWER_P":
                    self._stats["SCORE"] += 50
                    [ghost.set_color("BLUE") for ghost in ghosts_list]
                    self._power_pellet_timer = 100  # 10 seconds at 10 FPS
        else:
            pacman_x, pacman_y = old_x, old_y
            moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            best_move = None
            best_score = float('-inf')
            cur_score = 0
            for idx, idy in moves:
                new_x = pacman_x + idx
                new_y = pacman_y + idy
                ceil = field.get_ceil(new_y, new_x)
                if ceil != "BORDER":
                    cur_score = 0
                    if ceil == "DEFAULT_P":
                        cur_score += 10
                    elif ceil == "POWER_P":
                        cur_score += 50
                    min_ghost_dist = 1111111111
                    for g in ghosts_list:
                        g_x, g_y = g.get_position()
                        cur = abs(new_x - g_x) + abs(new_y - g_y)
                        if cur < min_ghost_dist:
                            min_ghost_dist = cur
                    cur_score += min_ghost_dist * 5

                    if cur_score > best_score:
                        best_score = cur_score
                        best_move = (idx, idy)

            if best_move:
                new_pos_x, new_pos_y = pacman_x + best_move[0], pacman_y + best_move[1]
                self.set_position(new_pos_x, new_pos_y)
                ceil = field.get_ceil(new_pos_y, new_pos_x)
                if ceil != "BORDER":
                    field.set_ceil(old_y, old_x, "EMPTY")
                    if ceil == "DEFAULT_P":
                        self._stats["SCORE"] += 10
                    elif ceil == "POWER_P":
                        self._stats["SCORE"] += 50
                        [ghost.set_color("BLUE") for ghost in ghosts_list]
                        self._power_pellet_timer = 100  # 10 seconds at 10 FPS

    def get_pp_time(self) -> int:
        return self._power_pellet_timer

    def set_pp_time(self, val: int) -> None:
        self._power_pellet_timer = val

    def get_position(self) -> Tuple[int, int]:
        return self._x_pos, self._y_pos

    def set_position(self, x: int, y: int) -> None:
        self._x_pos = x
        self._y_pos = y

    def get_stats(self) -> Dict:
        return self._stats

    def set_stats(self, new_stats: Dict) -> None:
        self._stats = new_stats

    def set_color(self, val: str) -> None:
        self._color = val

    def get_color(self) -> str:
        return self._color

    def get_def_color(self) -> str:
        return self._default_color

    def set_def_color(self, val: str) -> None:
        self._default_color = val


class Ghost(Pacman):

    def __init__(self, spawn_x_pos: int = 0, spawn_y_pos: int = 0, spawn_color: str = "WHITE") -> None:
        super().__init__()
        self._x_pos = spawn_x_pos
        self._y_pos = spawn_y_pos
        self._color = spawn_color
        self._default_color = spawn_color

    def movement(self, field: BoardIface, dx=0, dy=0, pacman_obj=None, ghosts_list=None):

        # global power_pellet_timer
        GRID_HEIGHT, GRID_WIDTH = field.get_params()
        ppt = pacman_obj.get_pp_time()  # REPAIR!!!
        start = self.get_position()
        pacman_x, pacman_y = pacman_obj.get_position()
        if ppt > 0:
            # Run away from Pacman
            goal = (GRID_WIDTH - 1 - pacman_x, GRID_HEIGHT - 1 - pacman_y)
        else:
            # Chase Pacman
            goal = (pacman_x, pacman_y)

        path = self.__a_star(start, goal, field)

        if path and len(path) > 1:
            new_x, new_y = path[1]
            self.set_position(new_x, new_y)

    def __heuristic(self, a, b) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def __a_star(self, start, goal, board):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: self.__heuristic(start, goal)}
        oheap = PriorityQueue()
        oheap.put((fscore[start], start))

        while oheap:
            current = oheap.get()[1]

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            close_set.add(current)

            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + 1
                len1, len2 = board.get_params()

                if 0 <= neighbor[1] < len1 and 0 <= neighbor[0] < len2:
                    ceil = board.get_ceil(neighbor[1], neighbor[0])
                    if ceil == "BORDER":
                        continue
                else:
                    continue

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap.queue]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = gscore[neighbor] + self.__heuristic(neighbor, goal)
                    oheap.put((fscore[neighbor], neighbor))

        return None

    def get_stats(self):
        pass

    def get_pp_time(self):
        pass

    def set_pp_time(self, val):
        pass


class PygameDrawer(Drawer):
    screen = None
    clock = None
    _WIDTH = None
    _HEIGHT = None
    _CELL_SIZE = None

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    PINK = (255, 192, 203)
    CYAN = (0, 255, 255)

    def __init__(self, width: int, height: int, cell_size: int) -> None:
        pygame.init()
        self._WIDTH = width
        self._HEIGHT = height
        self._CELL_SIZE = cell_size
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(self.BLACK)
        pygame.display.set_caption("Pygame Pacman with AI")
        self.clock = pygame.time.Clock()

    def draw_entity(self, ent: Entity):
        x_pos, y_pos = ent.get_position()
        pygame.draw.circle(self.screen, ent.get_color(),
                           (x_pos * self._CELL_SIZE + self._CELL_SIZE // 2,
                            y_pos * self._CELL_SIZE + self._CELL_SIZE // 2),
                           self._CELL_SIZE // 2)

    def draw_board(self, obj: BoardIface):
        self.screen.fill(self.BLACK)
        GRID_HEIGHT, GRID_WIDTH = obj.get_params()

        for x in range(GRID_HEIGHT):
            for y in range(GRID_WIDTH):
                ceil = obj.get_ceil(x, y)
                if ceil == "BORDER":
                    pygame.draw.rect(self.screen, self.BLUE,
                                     (y * self._CELL_SIZE, x * self._CELL_SIZE, self._CELL_SIZE, self._CELL_SIZE))
                elif ceil == "DEFAULT_P":
                    pygame.draw.circle(self.screen, self.WHITE,
                                       (y * self._CELL_SIZE + self._CELL_SIZE // 2,
                                        x * self._CELL_SIZE + self._CELL_SIZE // 2),
                                       2)
                elif ceil == "POWER_P":
                    pygame.draw.circle(self.screen, self.WHITE,
                                       (y * self._CELL_SIZE + self._CELL_SIZE // 2,
                                        x * self._CELL_SIZE + self._CELL_SIZE // 2),
                                       5)
                elif ceil == "EMPTY":
                    pygame.draw.rect(self.screen, self.BLACK,
                                     (y * self._CELL_SIZE, x * self._CELL_SIZE, self._CELL_SIZE, self._CELL_SIZE))

    def draw_ui(self, stat_set):
        score = stat_set["SCORE"]
        hp = stat_set["HP"]
        level = stat_set["LEVEL"]
        ai_text = "ON" if stat_set["AI_STATE"] else "OFF"
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, self.WHITE)
        hp_text = font.render(f"HP: {hp}", True, self.WHITE)
        level_text = font.render(f"Level: {level}", True, self.WHITE)
        ai_text = font.render("AI:" + ai_text, True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(hp_text, (self._WIDTH - 100, 10))
        self.screen.blit(level_text, (self._WIDTH // 2 - 40, 10))
        self.screen.blit(ai_text, (self._WIDTH // 2 - 40, self._HEIGHT - 30))
        pygame.display.flip()
        self.clock.tick(15)


class PyGameController(Controller):
    ai_state = None  # ???

    def get_event(self):
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return "AI_STATE"
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                return "UP"
            if keys[pygame.K_s]:
                return "DOWN"
            if keys[pygame.K_a]:
                return "LEFT"
            if keys[pygame.K_d]:
                return "RIGHT"
        except IndexError:
            pass

    def game_quit(self):
        pygame.quit()
