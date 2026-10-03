# ♟ Python Chess — Professional Edition

A polished chess application in Python with a graphical interface and a built-in chess engine.

## Features

- Human vs Computer
- Legal chess rules powered by `python-chess`
- Minimax-style **Negamax + Alpha-Beta pruning**
- Iterative deepening
- Quiescence search
- Transposition table
- Move ordering and killer-move heuristic
- Piece-square evaluation
- Easy / Medium / Hard engine settings
- Play as White or Black
- Move history
- Legal move hints
- Last-move highlighting
- Check, checkmate and draw detection
- Promotion dialog
- Undo full turn
- PGN export
- Modular, GitHub-friendly project structure

## Project structure

```text
pro_chess/
├── main.py
├── requirements.txt
├── pyproject.toml
├── README.md
├── .gitignore
├── chess_app/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── engine.py
│   ├── game.py
│   └── ui.py
├── tests/
│   └── test_rules.py
└── games/
```

## Run in PyCharm

### 1. Open the project

Open the `pro_chess` folder in PyCharm.

### 2. Create/select a virtual environment

Use PyCharm's recommended virtual environment, then open its Terminal.

### 3. Install packages

```bash
pip install -r requirements.txt
```

### 4. Start the game

```bash
python main.py
```

## Controls

| Key | Action |
|---|---|
| `N` | New game |
| `U` | Undo last full turn |
| `S` | Switch human side |
| `D` | Change difficulty |
| `P` | Save PGN |
| `ESC` | Quit |

Mouse: click a piece, then click its destination.

## Engine design

The engine uses:

```text
Position
   ↓
Generate legal moves
   ↓
Move ordering
   ↓
Iterative deepening
   ↓
Negamax
   ↓
Alpha-Beta pruning
   ↓
Quiescence search
   ↓
Evaluation function
   ↓
Best move
```

The evaluation combines material values, piece-square tables, bishop-pair bonus and mobility.

## Test

```bash
pytest
```

## GitHub

```bash
git init
git add .
git commit -m "Build professional Python chess"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/python-chess.git
git push -u origin main
```

## Future upgrades

- Opening book
- Better endgame evaluation
- Stockfish integration
- Adjustable board themes
- Sound effects
- PGN import
- Online multiplayer
- ELO-style rating
