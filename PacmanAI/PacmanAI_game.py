from PacmanAI import PacmanAI_pygame  # Pacman, Ghost, Board, PygameDrawer, PyGameController, GameMaster
from PacmanAI import PacmanAI_Interface


class GameMaster:
    _Pacman_obj = None
    _Ghosts_obj_list = None

    _Output_impl = None
    _Input_impl = None
    _Board_impl = None

    _running = False

    def __init__(self, output_impl: PacmanAI_Interface.Drawer, input_impl: PacmanAI_Interface.Controller,
                 pacman_impl: PacmanAI_Interface.Entity,
                 ghost_impl: list[PacmanAI_Interface.Entity], board_impl: PacmanAI_Interface.BoardIface):
        self._Output_impl = output_impl
        self._Input_impl = input_impl
        self._Board_impl = board_impl
        self._Pacman_obj = pacman_impl
        self._Ghosts_obj_list = ghost_impl
        self._running = True

    def _drawing(self) -> None:  # ent color change in movement/collision !
        self._Output_impl.draw_board(self._Board_impl)
        self._Output_impl.draw_entity(self._Pacman_obj)
        [self._Output_impl.draw_entity(cur_ghost_obj) for cur_ghost_obj in self._Ghosts_obj_list]
        self._Output_impl.draw_ui(self._Pacman_obj.get_stats())

    def _get_input(self) -> str:
        return self._Input_impl.get_event()

    def _check_collision(self) -> bool:
        ppt = self._Pacman_obj.get_pp_time()
        if ppt > 0:
            self._Pacman_obj.set_pp_time(ppt - 1)
            if ppt == 1:
                [ghost.set_color(ghost.get_def_color()) for ghost in self._Ghosts_obj_list]
        GRID_HEIGHT, GRID_WIDTH = self._Board_impl.get_params()
        tmp_stats = self._Pacman_obj.get_stats()
        for ghost in self._Ghosts_obj_list:
            pacman_x, pacman_y = self._Pacman_obj.get_position()
            ghost_x, ghost_y = ghost.get_position()
            if pacman_x == ghost_x and pacman_y == ghost_y:
                if self._Pacman_obj.get_pp_time() > 0:
                    ghost_x, ghost_y = GRID_WIDTH - 2, GRID_HEIGHT - 2
                    ghost.set_position(ghost_x, ghost_y)
                    tmp_stats["SCORE"] += 200
                else:
                    tmp_stats["HP"] -= 1
                    self._Pacman_obj.set_stats(tmp_stats)
                    if tmp_stats["HP"] > 0:
                        return True
                    else:
                        return False
            self._Pacman_obj.set_stats(tmp_stats)
        return True

    def _next_level(self) -> None:
        tmp_stats = self._Pacman_obj.get_stats()
        tmp_stats["LEVEL"] += 1
        self._Pacman_obj.set_stats(tmp_stats)
        level = 2
        GRID_HEIGHT, GRID_WIDTH = self._Board_impl.get_params()
        self._Pacman_obj.set_position(1, 1)
        for ghost in self._Ghosts_obj_list:
            ghost.set_position(GRID_WIDTH - 2, GRID_HEIGHT - 2)
        if level % 2 == 0 and len(self._Ghosts_obj_list) < 4:
            ghost_class = type(self._Ghosts_obj_list[0])
            new_ghost = ghost_class()
            new_ghost.set_position(GRID_WIDTH // 2, GRID_HEIGHT // 2)
            new_ghost.set_def_color("ORANGE")
            new_ghost.set_color("ORANGE")
            self._Ghosts_obj_list.append(new_ghost)
        self._Board_impl.reset()

    def game_cycle(self) -> None:
        ghost_move_counter = 0
        while self._running:

            self._drawing()
            event = self._get_input()

            match event:
                case "QUIT":
                    self._running = False
                case "AI_STATE":
                    temp_stats = self._Pacman_obj.get_stats()
                    temp_stats["AI_STATE"] = False if temp_stats["AI_STATE"] else True
                    self._Pacman_obj.set_stats(temp_stats)
                case "UP":
                    self._Pacman_obj.movement(self._Board_impl, 0, -1, ghosts_list=self._Ghosts_obj_list)
                case "DOWN":
                    self._Pacman_obj.movement(self._Board_impl, 0, 1, ghosts_list=self._Ghosts_obj_list)
                case "LEFT":
                    self._Pacman_obj.movement(self._Board_impl, -1, 0, ghosts_list=self._Ghosts_obj_list)
                case "RIGHT":
                    self._Pacman_obj.movement(self._Board_impl, 1, 0, ghosts_list=self._Ghosts_obj_list)
                case _:
                    if self._Pacman_obj.get_stats()["AI_STATE"]:
                        self._Pacman_obj.movement(self._Board_impl, 0, 0, ghosts_list=self._Ghosts_obj_list)

            ghost_move_counter += 1

            if ghost_move_counter % 2 == 0:
                [ghost.movement(self._Board_impl, pacman_obj=self._Pacman_obj) for ghost in self._Ghosts_obj_list]
                ghost_move_counter = 0

            if not self._check_collision():
                print("Game Over! You ran out of lifes!")
                self._running = False

            if self._Board_impl.is_empty():
                print("EMPTY BOARD!")
                self._next_level()

        self._Input_impl.game_quit()


class Game:
    _platform = None

    def __init__(self, platform: str = "pygame"):
        self._platform = platform

    def _run_config_pygame(self) -> GameMaster:
        WIDTH = 600
        HEIGHT = 400
        CELL_SIZE = 20
        grid_w = WIDTH // CELL_SIZE
        grid_h = HEIGHT // CELL_SIZE

        out = PacmanAI_pygame.PygameDrawer(WIDTH, HEIGHT, CELL_SIZE)
        inp = PacmanAI_pygame.PyGameController()
        pcm = PacmanAI_pygame.Pacman()
        gh = [PacmanAI_pygame.Ghost(grid_w - 2, grid_h - 2, "RED"),
              PacmanAI_pygame.Ghost(1, grid_h - 2, "PINK"),
              PacmanAI_pygame.Ghost(grid_w - 2, 1, "CYAN")]
        br = PacmanAI_pygame.Board(grid_h, grid_w)

        GM = GameMaster(out, inp, pcm, gh, br)
        return GM

    def run(self) -> None:
        handler = None
        match self._platform:
            case "pygame":
                handler = self._run_config_pygame()
            case _:
                print("Error")
                exit(-1)
        handler.game_cycle()
