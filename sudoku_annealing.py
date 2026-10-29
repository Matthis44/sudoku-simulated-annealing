"""Sudoku solver based on simulated annealing.

Standalone version of the solver I integrated into the group's C# benchmark
(see ``csharp/``). The model follows the Sudoku example of the `simanneal`
library (https://github.com/perrygeo/simanneal):

* state: every 3x3 block is filled with a permutation of its missing digits,
  so the block constraint always holds;
* move: swap two non-given cells inside one block;
* energy: minus the number of distinct digits over all rows and columns, which
  reaches -162 exactly when the grid is solved.

Annealing can get stuck in a local minimum, so ``solve`` restarts from a new
random state until it finds a solution or runs out of restarts.
"""

from __future__ import annotations

import argparse
import random
import time

import numpy as np
from simanneal import Annealer

SOLVED_ENERGY = -162  # 9 rows + 9 columns, 9 distinct digits each


def parse_grid(line: str) -> np.ndarray:
    """81-character puzzle string ('.' or '0' for empty cells) -> flat array."""
    line = line.strip()
    if len(line) != 81:
        raise ValueError(f"Expected 81 characters, got {len(line)}")
    return np.array([0 if c in ".0" else int(c) for c in line], dtype=int)


def block_indices(block: int) -> list[int]:
    """Flat indices of a 3x3 block, numbered 0-8 in row-major order."""
    first_row, first_col = (block // 3) * 3, (block % 3) * 3
    return [(first_row + i) * 9 + first_col + j for i in range(3) for j in range(3)]


def random_initial_state(problem: np.ndarray, rng: random.Random) -> np.ndarray:
    """Fill each block with its missing digits in random order."""
    state = problem.copy()
    for block in range(9):
        indices = block_indices(block)
        empty = [i for i in indices if problem[i] == 0]
        missing = [d for d in range(1, 10) if d not in problem[indices]]
        rng.shuffle(missing)
        state[empty] = missing
    return state


def energy_of(state: np.ndarray) -> int:
    grid = state.reshape(9, 9)
    return -sum(len(set(grid[i])) + len(set(grid[:, i])) for i in range(9))


class SudokuAnnealer(Annealer):
    def __init__(self, problem: np.ndarray, rng: random.Random):
        self.problem = problem
        self.rng = rng
        self.free = [[i for i in block_indices(b) if problem[i] == 0] for b in range(9)]
        self.free = [cells for cells in self.free if len(cells) >= 2]
        super().__init__(random_initial_state(problem, rng))
        self.copy_strategy = "method"

    def move(self):
        m, n = self.rng.sample(self.rng.choice(self.free), 2)
        self.state[m], self.state[n] = self.state[n], self.state[m]

    def energy(self):
        e = energy_of(self.state)
        if e == SOLVED_ENERGY:
            self.user_exit = True  # stop as soon as a solution is found
        return e


def is_solution(grid: np.ndarray, problem: np.ndarray) -> bool:
    """Check every constraint and that the givens are unchanged."""
    g = grid.reshape(9, 9)
    full = set(range(1, 10))
    rows_ok = all(set(g[i]) == full for i in range(9))
    cols_ok = all(set(g[:, i]) == full for i in range(9))
    blocks_ok = all(set(grid[block_indices(b)]) == full for b in range(9))
    givens_ok = np.all((problem == 0) | (grid == problem))
    return bool(rows_ok and cols_ok and blocks_ok and givens_ok)


def solve(problem: np.ndarray, steps: int = 100_000, t_max: float = 0.5, t_min: float = 0.05,
          max_restarts: int = 10, seed: int | None = None) -> tuple[np.ndarray, int]:
    """Return (best grid found, number of attempts used)."""
    rng = random.Random(seed)
    best, best_energy = None, 0
    for attempt in range(1, max_restarts + 1):
        annealer = SudokuAnnealer(problem, rng)
        annealer.Tmax, annealer.Tmin, annealer.steps = t_max, t_min, steps
        annealer.updates = 0  # silence progress output
        state, energy = annealer.anneal()
        if energy < best_energy:
            best, best_energy = state, energy
        if energy == SOLVED_ENERGY:
            break
    return best, attempt


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve the Sudokus of a file by simulated annealing.")
    parser.add_argument("puzzles", help="file with one 81-character puzzle per line")
    parser.add_argument("--limit", type=int, help="only solve the first N puzzles")
    parser.add_argument("--steps", type=int, default=100_000)
    parser.add_argument("--restarts", type=int, default=10)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    with open(args.puzzles) as f:
        puzzles = [parse_grid(line) for line in f if line.strip()][: args.limit]

    solved, total_time = 0, 0.0
    for k, problem in enumerate(puzzles, 1):
        start = time.perf_counter()
        grid, attempts = solve(problem, steps=args.steps, max_restarts=args.restarts, seed=args.seed + k)
        elapsed = time.perf_counter() - start
        total_time += elapsed
        ok = is_solution(grid, problem)
        solved += ok
        givens = int((problem > 0).sum())
        print(f"#{k:3d}  givens={givens:2d}  {'solved ' if ok else 'FAILED '}  "
              f"attempts={attempts:2d}  {elapsed:6.2f}s")
    print(f"\n{solved}/{len(puzzles)} solved, {total_time / len(puzzles):.2f}s per puzzle on average")


if __name__ == "__main__":
    main()
