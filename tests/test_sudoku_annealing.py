import random

import numpy as np
import pytest

from sudoku_annealing import (
    SOLVED_ENERGY,
    block_indices,
    energy_of,
    is_solution,
    parse_grid,
    random_initial_state,
    solve,
)

EASY = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
SOLVED = "483921657967345821251876493548132976729564138136798245372689514814253769695417382"


def test_parse_grid():
    grid = parse_grid("." * 80 + "9")
    assert grid.shape == (81,) and grid[-1] == 9 and grid[:-1].sum() == 0
    with pytest.raises(ValueError):
        parse_grid("123")


def test_block_indices():
    assert block_indices(0) == [0, 1, 2, 9, 10, 11, 18, 19, 20]
    assert block_indices(8)[-1] == 80


def test_energy_is_minimal_only_for_a_solution():
    assert energy_of(parse_grid(SOLVED)) == SOLVED_ENERGY
    broken = parse_grid(SOLVED)
    broken[[0, 1]] = broken[[1, 0]]
    assert energy_of(broken) > SOLVED_ENERGY


def test_initial_state_keeps_givens_and_fills_blocks():
    problem = parse_grid(EASY)
    state = random_initial_state(problem, random.Random(0))
    assert np.all(state[problem > 0] == problem[problem > 0])
    assert all(sorted(state[block_indices(b)]) == list(range(1, 10)) for b in range(9))


def test_is_solution_detects_changed_givens():
    problem, solution = parse_grid(EASY), parse_grid(SOLVED)
    assert is_solution(solution, problem)
    other = problem.copy()
    other[0] = 9  # a given that the solution does not respect
    assert not is_solution(solution, other)


def test_solves_an_easy_puzzle():
    problem = parse_grid(EASY)
    grid, _ = solve(problem, seed=1)
    assert is_solution(grid, problem)
    assert "".join(map(str, grid)) == SOLVED
