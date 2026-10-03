from dataclasses import dataclass

@dataclass(frozen=True)
class Difficulty:
    name: str
    max_depth: int
    time_limit: float

DIFFICULTIES = {
    "Easy": Difficulty("Easy", 2, 1.0),
    "Medium": Difficulty("Medium", 3, 2.5),
    "Hard": Difficulty("Hard", 4, 6.0),
}

WINDOW_W = 1040
WINDOW_H = 760
BOARD_SIZE = 700
SQUARE_SIZE = BOARD_SIZE // 8
PANEL_W = WINDOW_W - BOARD_SIZE

FPS = 60

# UI palette
BG = (24, 27, 32)
PANEL = (31, 35, 42)
PANEL_2 = (39, 44, 52)
TEXT = (236, 239, 244)
MUTED = (158, 166, 178)
ACCENT = (89, 166, 255)
SUCCESS = (82, 196, 125)
WARNING = (240, 180, 80)
DANGER = (228, 90, 90)

BOARD_LIGHT = (235, 220, 194)
BOARD_DARK = (112, 145, 110)
BOARD_HIGHLIGHT = (246, 211, 91)
BOARD_LAST = (193, 173, 83)
BOARD_CHECK = (207, 80, 80)
MOVE_DOT = (52, 58, 65)

PIECE_LIGHT = (248, 248, 248)
PIECE_DARK = (32, 35, 40)
PIECE_OUTLINE = (80, 84, 90)
