from PacmanAI import PacmanAI_pygame
from PacmanAI.PacmanAI_game import GameMaster
import keyboard
import unittest


class TestPacmanGame(unittest.TestCase):

    def setUp(self):
        WIDTH = 600
        HEIGHT = 400
        CELL_SIZE = 20
        grid_w = WIDTH // CELL_SIZE
        grid_h = HEIGHT // CELL_SIZE

        self.out = PacmanAI_pygame.PygameDrawer(WIDTH, HEIGHT, CELL_SIZE)
        self.inp = PacmanAI_pygame.PyGameController()
        self.pcm = PacmanAI_pygame.Pacman()
        self.gh = [PacmanAI_pygame.Ghost(grid_w - 2, grid_h - 2, "RED"),
                   PacmanAI_pygame.Ghost(1, grid_h - 2, "PINK"),
                   PacmanAI_pygame.Ghost(grid_w - 2, 1, "CYAN")]
        self.br = PacmanAI_pygame.Board(grid_h, grid_w)

        self.GM = GameMaster(self.out, self.inp, self.pcm, self.gh, self.br)

    def test_output(self):
        res = -1
        try:
            self.GM._drawing()
            res = 1
        except Exception:
            res = 0
        self.assertEqual(res, 1)

    def test_input(self):
        keyboard.press('s')
        self.assertEqual(self.GM._get_input(), "DOWN")

    def test_pacman_movement(self):
        start_pos = self.pcm.get_position()
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.assertNotEqual(self.pcm.get_position(), start_pos)

    def test_pacman_state(self):
        pacman = self.pcm
        self.assertEqual(pacman.get_color(), "YELLOW")
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.assertEqual(pacman.get_position(), (4, 1))

    def test_score_increase(self):
        start_score = self.pcm.get_stats()["SCORE"]
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.assertGreater(self.pcm.get_stats()["SCORE"], start_score)

    def test_board_state(self):
        self.assertFalse(self.br.is_empty())
        self.assertEqual(self.br.get_ceil(1, 1), "DEFAULT_P")
        self.pcm.movement(self.br, 1, 0, ghosts_list=self.gh)  # MOVE TO RIGHT
        self.assertEqual(self.br.get_ceil(1, 1), "EMPTY")
        self.br.set_ceil(7, 7, "#")
        self.assertEqual(self.br.get_ceil(7, 7), "BORDER")

    def test_ghost_afk(self):
        self.GM.game_cycle()
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
