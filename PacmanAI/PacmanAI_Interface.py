from abc import ABC, abstractmethod
from typing import NoReturn, Dict, Tuple, Self


class BoardIface(ABC):

    @abstractmethod
    def get_ceil(self, x: int, y: int) -> str:  # "BORDER"/ "POWER_P" / "DEFAULT_P"
        pass

    @abstractmethod
    def get_params(self) -> (int, int):
        pass

    @abstractmethod
    def set_ceil(self, x_pos: int, y_pos: int, subj: str) -> None:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def reset(self) -> NoReturn:
        pass


class Entity(ABC):

    @abstractmethod
    def movement(self, field: BoardIface, dx: int = None, dy: int = None, pacman_obj: Self = None,
                 ghosts_list=list[Self]) -> None:
        pass

    @abstractmethod
    def get_position(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_color(self) -> str:
        pass

    @abstractmethod
    def set_position(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def get_stats(self) -> Dict:
        pass

    @abstractmethod
    def set_color(self, val: str) -> None:
        pass

    @abstractmethod
    def set_stats(self, new_stats: Dict) -> None:
        pass

    @abstractmethod
    def get_pp_time(self) -> int:
        pass

    @abstractmethod
    def set_pp_time(self, val: int) -> None:
        pass

    @abstractmethod
    def set_def_color(self, val: str) -> None:
        pass

    @abstractmethod
    def get_def_color(self) -> str:
        pass


class Drawer(ABC):

    @abstractmethod
    def draw_entity(self, ent: Entity) -> None:
        pass

    @abstractmethod
    def draw_board(self, obj: BoardIface) -> None:
        pass

    @abstractmethod
    def draw_ui(self, stat_set: Dict) -> None:
        pass


class Controller(ABC):

    @abstractmethod
    def get_event(self) -> str:
        pass

    @abstractmethod
    def game_quit(self) -> NoReturn:
        pass
