import chess


def test_start_position_has_20_legal_moves():
    board = chess.Board()
    assert board.legal_moves.count() == 20


def test_castling_is_supported():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert chess.Move.from_uci("e1g1") in board.legal_moves
    assert chess.Move.from_uci("e1c1") in board.legal_moves


def test_promotion_move_is_legal():
    board = chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    move = chess.Move.from_uci("a7a8q")
    assert move in board.legal_moves
