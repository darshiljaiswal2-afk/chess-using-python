from __future__ import annotations

from dataclasses import dataclass
import time
import chess


MATE_SCORE = 100_000
INF = 1_000_000

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20_000,
}

# Simple piece-square tables, from White's perspective.
PST = {
    chess.PAWN: [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0,
    ],
    chess.KNIGHT: [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ],
    chess.BISHOP: [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ],
    chess.ROOK: [
         0,  0,  0,  0,  0,  0,  0,  0,
         5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         0,  0,  0,  5,  5,  0,  0,  0,
    ],
    chess.QUEEN: [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0, -10,
        -10,  0,  5,  5,  5,  5,  0, -10,
         -5,  0,  5,  5,  5,  5,  0,  -5,
          0,  0,  5,  5,  5,  5,  0,  -5,
        -10,  5,  5,  5,  5,  5,  0, -10,
        -10,  0,  5,  0,  0,  0,  0, -10,
        -20,-10,-10, -5, -5,-10,-10,-20,
    ],
    chess.KING: [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20,  20,  0,  0,  0,  0, 20, 20,
         20,  30, 10,  0,  0, 10, 30, 20,
    ],
}


@dataclass
class TTEntry:
    depth: int
    score: int
    flag: str
    move: chess.Move | None


class SearchTimeout(Exception):
    pass


class ChessEngine:
    def __init__(self, max_depth: int = 3, time_limit: float = 2.5):
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = 0.0
        self.nodes = 0
        self.tt: dict[str, TTEntry] = {}
        self.killers: dict[int, list[chess.Move]] = {}

    def choose_move(self, board: chess.Board) -> chess.Move | None:
        if board.is_game_over():
            return None

        self.start_time = time.perf_counter()
        self.nodes = 0

        best_move = next(iter(board.legal_moves), None)

        # Iterative deepening gives a safe best move even if the time limit is hit.
        for depth in range(1, self.max_depth + 1):
            try:
                score, move = self._root_search(board, depth)
                if move is not None:
                    best_move = move
                self.tt[board.fen()] = TTEntry(depth, score, "EXACT", move)
            except SearchTimeout:
                break

        return best_move

    def _check_time(self):
        if time.perf_counter() - self.start_time >= self.time_limit:
            raise SearchTimeout

    def _root_search(self, board: chess.Board, depth: int):
        alpha, beta = -INF, INF
        best_score = -INF
        best_move = None

        moves = list(board.legal_moves)
        self._order_moves(board, moves, None, 0)

        for move in moves:
            self._check_time()
            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha, 1)
            board.pop()

            if score > best_score:
                best_score = score
                best_move = move
            if score > alpha:
                alpha = score

        return best_score, best_move

    def _negamax(self, board: chess.Board, depth: int, alpha: int, beta: int, ply: int):
        self._check_time()
        self.nodes += 1

        outcome = board.outcome()
        if outcome is not None:
            if outcome.winner is None:
                return 0
            return -MATE_SCORE + ply

        if depth <= 0:
            return self._quiescence(board, alpha, beta, ply)

        key = board.fen()
        entry = self.tt.get(key)
        original_alpha = alpha
        if entry and entry.depth >= depth:
            if entry.flag == "EXACT":
                return entry.score
            if entry.flag == "LOWER":
                alpha = max(alpha, entry.score)
            elif entry.flag == "UPPER":
                beta = min(beta, entry.score)
            if alpha >= beta:
                return entry.score

        best = -INF
        best_move = None
        moves = list(board.legal_moves)
        self._order_moves(board, moves, entry.move if entry else None, ply)

        for move in moves:
            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha, ply + 1)
            board.pop()

            if score > best:
                best = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                # Killer heuristic: quiet move that caused a cutoff.
                if not board.is_capture(move):
                    killers = self.killers.setdefault(ply, [])
                    if move not in killers:
                        killers.insert(0, move)
                        del killers[2:]
                break

        if best <= original_alpha:
            flag = "UPPER"
        elif best >= beta:
            flag = "LOWER"
        else:
            flag = "EXACT"

        self.tt[key] = TTEntry(depth, best, flag, best_move)
        return best

    def _quiescence(self, board: chess.Board, alpha: int, beta: int, ply: int):
        self._check_time()
        stand_pat = self._evaluate_for_side_to_move(board)

        if stand_pat >= beta:
            return beta
        alpha = max(alpha, stand_pat)

        captures = [m for m in board.legal_moves if board.is_capture(m) or m.promotion]
        self._order_moves(board, captures, None, ply)

        for move in captures:
            board.push(move)
            score = -self._quiescence(board, -beta, -alpha, ply + 1)
            board.pop()

            if score >= beta:
                return beta
            alpha = max(alpha, score)

        return alpha

    def _order_moves(self, board, moves, tt_move, ply):
        killers = self.killers.get(ply, [])

        def score(move):
            s = 0
            if tt_move is not None and move == tt_move:
                s += 1_000_000
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                if victim:
                    s += 10_000 + 10 * PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
                else:
                    s += 9_000  # en passant
            if move.promotion:
                s += 8_000 + PIECE_VALUES[move.promotion]
            if move in killers:
                s += 5_000
            return s

        moves.sort(key=score, reverse=True)

    def _evaluate_for_side_to_move(self, board: chess.Board) -> int:
        white_score = self._evaluate(board)
        return white_score if board.turn == chess.WHITE else -white_score

    def _evaluate(self, board: chess.Board) -> int:
        score = 0
        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            table = PST[piece.piece_type]
            idx = square if piece.color == chess.WHITE else chess.square_mirror(square)
            value += table[idx]

            # Small bishop-pair bonus.
            if piece.piece_type == chess.BISHOP:
                same_color_bishops = len(board.pieces(chess.BISHOP, piece.color))
                if same_color_bishops >= 2:
                    value += 20

            score += value if piece.color == chess.WHITE else -value

        # Mobility is a useful lightweight positional signal.
        current_turn = board.turn
        own_moves = board.legal_moves.count()
        board.turn = not current_turn
        opp_moves = board.legal_moves.count()
        board.turn = current_turn
        score += 2 * (own_moves - opp_moves) if current_turn == chess.WHITE else -2 * (own_moves - opp_moves)

        return score
