# Sudoku solver by simulated annealing

[![tests](https://github.com/Matthis44/sudoku-simulated-annealing/actions/workflows/tests.yml/badge.svg)](https://github.com/Matthis44/sudoku-simulated-annealing/actions/workflows/tests.yml)

Solving Sudoku as an optimisation problem: instead of searching the tree of possible grids,
simulated annealing starts from a random grid and swaps cells to reduce the number of
constraint violations, accepting some bad moves early on to escape local minima.

## Origin

This solver was my part of a group project at ECE Paris (Ing4 Finance, 2023), where each
team member added a solving method to a shared C# benchmark. I integrated a Python
simulated-annealing solver into the C# application through Python.NET: that code is in
[`csharp/`](csharp/) with its original commit history. The annealing model itself adapts the
Sudoku example of the [`simanneal`](https://github.com/perrygeo/simanneal) library.

[`sudoku_annealing.py`](sudoku_annealing.py) is a standalone, tested Python version of the
same solver, so it can run without the course's Visual Studio solution, with random restarts
and a benchmark command added.

## Model

| | |
|---|---|
| **State** | each 3x3 block holds a permutation of its missing digits, so block constraints always hold |
| **Move** | swap two non-given cells inside a random block |
| **Energy** | minus the number of distinct digits in every row and column: −162 means solved |
| **Schedule** | exponential cooling from T = 0.5 to 0.05 over 100,000 steps, restart if stuck |

## Results

```
python sudoku_annealing.py puzzles/easy51.txt
python sudoku_annealing.py puzzles/hardest.txt --limit 4 --restarts 5
```

| Puzzle set | Solved | Average time |
|---|---|---|
| 51 easy puzzles | 48 / 51 (94%) | 5.8 s |
| 4 of the "hardest" puzzles | 1 / 4 | 13.5 s |

Annealing works well when many cells are given but struggles on puzzles with few givens: the
energy landscape has many near-solutions (one or two violations) far apart from each other,
and restarts are not enough to reach the true minimum. A backtracking solver with constraint
propagation solves these in milliseconds, which is why such exact methods are preferred for
Sudoku; annealing shines on problems that are too large to search exhaustively.

## Run it

```bash
pip install -r requirements.txt
pytest
python sudoku_annealing.py puzzles/easy51.txt --limit 10
```

Puzzle files come from the course repository (one 81-character grid per line, `.` or `0`
for empty cells).
