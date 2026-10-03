from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import chess
import chess.pgn
from datetime import datetime


@dataclass
class GameSettings:
    human_color: chess.Color = chess.WHITE
    difficulty: str = "Medium"


class Game:
    def __init__(self, settings: GameSettings | None = None):
        self.settings = settings or GameSettings()
        self.board = chess.Board()
        self.last_move = None

    def reset(self):
        self.board.reset()
        self.last_move = None

    def push(self, move: chess.Move):
        self.board.push(move)
        self.last_move = move

    def undo(self):
        if not self.board.move_stack:
            return False
        self.board.pop()
        self.last_move = self.board.peek() if self.board.move_stack else None
        return True

    def legal_moves_from(self, square):
        return [m for m in self.board.legal_moves if m.from_square == square]

    def game_status(self) -> str:
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            return f"Checkmate — {winner} wins"
        if self.board.is_stalemate():
            return "Stalemate — Draw"
        if self.board.is_insufficient_material():
            return "Draw — insufficient material"
        if self.board.is_fivefold_repetition():
            return "Draw — fivefold repetition"
        if self.board.is_seventyfive_moves():
            return "Draw — 75-move rule"
        if self.board.is_check():
            return f"{'White' if self.board.turn else 'Black'} is in check"
        return f"{'White' if self.board.turn else 'Black'} to move"

    def export_pgn(self, folder: str = "games") -> Path:
        target = Path(folder)
        target.mkdir(parents=True, exist_ok=True)

        game = chess.pgn.Game()
        game.headers["Event"] = "Python Chess"
        game.headers["Site"] = "Local"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["Round"] = "-"
        game.headers["White"] = "Human" if self.settings.human_color == chess.WHITE else "Computer"
        game.headers["Black"] = "Human" if self.settings.human_color == chess.BLACK else "Computer"

        temp = chess.Board()
        node = game
        for move in self.board.move_stack:
            node = node.add_variation(move)
            temp.push(move)

        path = target / f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        path.write_text(str(game), encoding="utf-8")
        return path
