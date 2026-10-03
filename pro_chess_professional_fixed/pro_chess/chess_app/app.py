from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import pygame
import chess

from .config import *
from .config import DIFFICULTIES
from .engine import ChessEngine
from .game import Game, GameSettings
from .ui import UI


class ChessApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Python Chess — Professional Edition")
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()

        self.ui = UI()
        self.settings = GameSettings()
        self.game = Game(self.settings)
        self.selected = None
        self.thinking = False
        self.future = None
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.engine = None
        self.message = ""

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event) and running
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            self._poll_engine()

            self.ui.draw(
                self.screen,
                self.game.board,
                self.selected,
                self.game.last_move,
                self.game.game_status(),
                self.thinking,
                self.settings.difficulty,
                self.settings.human_color,
            )
            self.clock.tick(FPS)

        self.executor.shutdown(wait=False, cancel_futures=True)
        pygame.quit()

    def _handle_key(self, event):
        key = event.key
        if key == pygame.K_ESCAPE:
            return False
        if key == pygame.K_n:
            self._new_game()
        elif key == pygame.K_u:
            self._undo_turn()
        elif key == pygame.K_s:
            self.settings.human_color = not self.settings.human_color
            self._new_game()
        elif key == pygame.K_d:
            self._cycle_difficulty()
        elif key == pygame.K_p:
            path = self.game.export_pgn()
            self.message = f"Saved: {path}"
        return True

    def _handle_click(self, pos):
        if self.thinking or self.game.board.is_game_over():
            return

        square = self.ui.square_at(pos)
        if square is None:
            return

        board = self.game.board
        if board.turn != self.settings.human_color:
            return

        piece = board.piece_at(square)

        if self.selected is None:
            if piece and piece.color == board.turn:
                self.selected = square
            return

        # Re-select own piece.
        if piece and piece.color == board.turn:
            self.selected = square
            return

        candidates = [
            move for move in board.legal_moves
            if move.from_square == self.selected and move.to_square == square
        ]

        if not candidates:
            self.selected = None
            return

        move = candidates[0]
        if move.promotion:
            promotion = self.ui.promotion_dialog(self.screen, board, board.turn)
            move = chess.Move(move.from_square, move.to_square, promotion=promotion)

        self.game.push(move)
        self.selected = None
        self._maybe_start_engine()

    def _maybe_start_engine(self):
        if self.game.board.is_game_over():
            return
        if self.game.board.turn == self.settings.human_color:
            return

        diff = DIFFICULTIES[self.settings.difficulty]
        self.engine = ChessEngine(diff.max_depth, diff.time_limit)
        board_copy = self.game.board.copy(stack=True)
        self.thinking = True
        self.future = self.executor.submit(self.engine.choose_move, board_copy)

    def _poll_engine(self):
        if not self.thinking or self.future is None:
            return
        if not self.future.done():
            return

        try:
            move = self.future.result()
            if move and move in self.game.board.legal_moves:
                self.game.push(move)
        finally:
            self.future = None
            self.thinking = False

    def _new_game(self):
        self.game.reset()
        self.selected = None
        self.thinking = False
        if self.future and not self.future.done():
            self.future.cancel()
        self.future = None
        self._maybe_start_engine()

    def _undo_turn(self):
        if self.thinking:
            return

        # In human-vs-engine mode undo a full turn where possible.
        if len(self.game.board.move_stack) >= 2:
            self.game.undo()
            self.game.undo()
        elif self.game.board.move_stack:
            self.game.undo()

        self.selected = None

    def _cycle_difficulty(self):
        names = list(DIFFICULTIES.keys())
        idx = names.index(self.settings.difficulty)
        self.settings.difficulty = names[(idx + 1) % len(names)]
