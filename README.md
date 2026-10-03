# ♟️ Python Chess Engine

A professional desktop chess application built with **Python**, **Pygame**, and **python-chess**.

The project combines a graphical chess interface with a custom chess engine using **Negamax search, Alpha-Beta pruning, Iterative Deepening, Quiescence Search, Transposition Tables, Move Ordering, and positional evaluation**.

---

## 🚀 Features

### 🎮 Gameplay

- Human vs Computer
- Play as White or Black
- Full legal chess move validation
- Check detection
- Checkmate detection
- Stalemate detection
- Draw detection
- Castling
- En passant
- Pawn promotion
- Move history
- Last-move highlighting
- Legal move indicators
- Undo moves
- New game option

### 🤖 Chess Engine

The built-in engine uses several classic chess-engine techniques:

- Negamax search
- Alpha-Beta pruning
- Iterative deepening
- Quiescence search
- Transposition table
- Move ordering
- Killer-move heuristic
- Material evaluation
- Piece-square tables
- Mobility evaluation
- Bishop-pair bonus
- Time-limited search

### ⚙️ Difficulty Levels

| Difficulty | Search Depth | Time Limit |
|------------|--------------|------------|
| Easy | 2 | ~1 sec |
| Medium | 3 | ~2.5 sec |
| Hard | 4 | ~6 sec |

The exact search depth can vary depending on the position and available search time.

### 💾 Game Management

- Export games to PGN
- Save complete move history
- Reset the game
- Undo the previous turn
- Switch player side

---

# 🧠 How the Chess Engine Works

The engine follows a simplified professional chess-engine architecture:

```text
                    Chess Position
                          │
                          ▼
                Generate Legal Moves
                          │
                          ▼
                    Move Ordering
                          │
                          ▼
                Iterative Deepening
                          │
                          ▼
                    Negamax Search
                          │
                          ▼
                  Alpha-Beta Pruning
                          │
                          ▼
                  Quiescence Search
                          │
                          ▼
               Position Evaluation
                          │
                          ▼
                    Best Move
