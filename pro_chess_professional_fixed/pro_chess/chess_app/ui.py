from __future__ import annotations

import pygame
import chess

from .config import *


UNICODE = {
    chess.PAWN:   ("♙", "♟"),
    chess.KNIGHT: ("♘", "♞"),
    chess.BISHOP: ("♗", "♝"),
    chess.ROOK:   ("♖", "♜"),
    chess.QUEEN:  ("♕", "♛"),
    chess.KING:   ("♔", "♚"),
}


class UI:
    def __init__(self):
        # Windows: Segoe UI Symbol contains the Unicode chess pieces.
        # Fall back to DejaVu/Arial if the Windows font is unavailable.
        chess_font = r"C:\Windows\Fonts\seguisym.ttf"
        try:
            self.font = pygame.font.Font(chess_font, 58)
        except (FileNotFoundError, OSError):
            self.font = self._font(["dejavusans", "segoeuisymbol", "arial"], 58)

        self.title = self._font(["arial", "dejavusans"], 30, True)
        self.text = self._font(["arial", "dejavusans"], 20)
        self.small = self._font(["arial", "dejavusans"], 16)
        self.tiny = self._font(["arial", "dejavusans"], 14)

    @staticmethod
    def _font(names, size, bold=False):
        for name in names:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        return pygame.font.Font(None, size)

    def board_rect(self):
        return pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE)

    def square_at(self, mouse_pos):
        x, y = mouse_pos
        if not self.board_rect().collidepoint(mouse_pos):
            return None
        file_ = x // SQUARE_SIZE
        row = y // SQUARE_SIZE
        return chess.square(file_, 7 - row)

    def draw(self, screen, board, selected, last_move, status, thinking, difficulty, human_color):
        screen.fill(BG)
        self.draw_board(screen, board, selected, last_move)
        self.draw_panel(screen, board, status, thinking, difficulty, human_color)
        pygame.display.flip()

    def draw_board(self, screen, board, selected, last_move):
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)
                color = BOARD_LIGHT if (row + col) % 2 == 0 else BOARD_DARK

                if last_move and square in (last_move.from_square, last_move.to_square):
                    color = BOARD_LAST
                if selected == square:
                    color = BOARD_HIGHLIGHT
                if board.is_check() and square == board.king(board.turn):
                    color = BOARD_CHECK

                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        if selected is not None:
            for move in board.legal_moves:
                if move.from_square != selected:
                    continue
                self._draw_move_hint(screen, board, move)

        self._draw_coordinates(screen)

        # Pieces with a subtle shadow/outline.
        for square, piece in board.piece_map().items():
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)

            symbol = UNICODE[piece.piece_type][0 if piece.color else 1]
            shadow = self.font.render(symbol, True, (0, 0, 0))
            text = self.font.render(symbol, True, PIECE_LIGHT if piece.color else PIECE_DARK)

            screen.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 3)))
            screen.blit(text, text.get_rect(center=center))

    def _draw_move_hint(self, screen, board, move):
        col = chess.square_file(move.to_square)
        row = 7 - chess.square_rank(move.to_square)
        center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)

        if board.piece_at(move.to_square):
            pygame.draw.circle(screen, MOVE_DOT, center, SQUARE_SIZE // 2 - 8, 5)
        else:
            pygame.draw.circle(screen, MOVE_DOT, center, 8)

    def _draw_coordinates(self, screen):
        coord_font = self.tiny
        for col in range(8):
            label = coord_font.render(chr(ord("a") + col), True, (70, 70, 70))
            screen.blit(label, (col * SQUARE_SIZE + 5, BOARD_SIZE - 20))
        for row in range(8):
            label = coord_font.render(str(8 - row), True, (70, 70, 70))
            screen.blit(label, (4, row * SQUARE_SIZE + 4))

    def draw_panel(self, screen, board, status, thinking, difficulty, human_color):
        panel = pygame.Rect(BOARD_SIZE, 0, PANEL_W, WINDOW_H)
        pygame.draw.rect(screen, PANEL, panel)

        x = BOARD_SIZE + 22
        y = 22
        screen.blit(self.title.render("PYTHON CHESS", True, TEXT), (x, y))
        y += 48

        status_color = WARNING if "check" in status.lower() else SUCCESS if "to move" in status.lower() else DANGER
        screen.blit(self.text.render(status, True, status_color), (x, y))
        y += 38

        side = "White" if human_color == chess.WHITE else "Black"
        screen.blit(self.small.render(f"You: {side}", True, MUTED), (x, y))
        y += 25
        screen.blit(self.small.render(f"Engine: {difficulty}", True, MUTED), (x, y))
        y += 35

        if thinking:
            screen.blit(self.text.render("Computer thinking…", True, ACCENT), (x, y))
            y += 35

        # Move history
        screen.blit(self.text.render("Moves", True, TEXT), (x, y))
        y += 34

        moves = list(board.mainline_moves()) if hasattr(board, "mainline_moves") else board.move_stack
        history = []
        temp = chess.Board()
        for move in board.move_stack:
            san = temp.san(move)
            history.append(san)
            temp.push(move)

        start = max(0, len(history) - 18)
        visible = history[start:]
        for i in range(0, len(visible), 2):
            move_no = start // 2 + i // 2 + 1
            white = visible[i]
            black = visible[i + 1] if i + 1 < len(visible) else ""
            line = f"{move_no:>2}. {white:<8} {black}"
            screen.blit(self.small.render(line, True, TEXT), (x, y))
            y += 23

        # Controls
        controls_y = WINDOW_H - 155
        pygame.draw.rect(screen, PANEL_2, (BOARD_SIZE + 15, controls_y, PANEL_W - 30, 140), border_radius=12)
        controls = [
            "N  New game",
            "U  Undo last turn",
            "S  Switch side",
            "D  Change difficulty",
            "P  Save PGN",
            "ESC  Quit",
        ]
        for idx, line in enumerate(controls):
            screen.blit(self.small.render(line, True, MUTED), (x, controls_y + 12 + idx * 20))

    def promotion_dialog(self, screen, board, color):
        overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(155, 250, 390, 170)
        pygame.draw.rect(screen, PANEL, box, border_radius=14)
        pygame.draw.rect(screen, PANEL_2, box, 2, border_radius=14)

        label = self.text.render("Choose promotion", True, TEXT)
        screen.blit(label, label.get_rect(center=(box.centerx, box.y + 28)))

        pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        buttons = []
        for i, piece_type in enumerate(pieces):
            r = pygame.Rect(box.x + 20 + i * 88, box.y + 70, 70, 75)
            pygame.draw.rect(screen, PANEL_2, r, border_radius=10)
            symbol = UNICODE[piece_type][0 if color else 1]
            piece = self.font.render(symbol, True, PIECE_LIGHT if color else PIECE_DARK)
            screen.blit(piece, piece.get_rect(center=r.center))
            buttons.append((r, piece_type))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return chess.QUEEN
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return chess.QUEEN
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for r, piece_type in buttons:
                        if r.collidepoint(event.pos):
                            return piece_type
