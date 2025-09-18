# ps2.py
# Layout a Circuit Board using a CSP
# Starter Code by David Kopec
# Completed by: Chase Mackey
from __future__ import annotations
from csp import CSP, Constraint
from typing import NamedTuple


Grid = list[list[str]]  # type alias for grids


class GridLocation(NamedTuple):
    row: int
    column: int


class Chip(NamedTuple):
    width: int
    height: int
    symbol: str


def generate_grid(rows: int, columns: int) -> Grid:
    # initialize grid with "-"
    return [["-" for c in range(columns)] for r in range(rows)]


def display_grid(grid: Grid) -> None:
    for row in grid:
        print("".join(row))


# ---------------------------
# CSP Implementation
# ---------------------------

def generate_domain(chip: Chip, rows: int, columns: int) -> list[tuple[int,int,int,int]]:
    """Generate all possible placements (row, col, width, height) for a chip."""
    placements = []
    # consider both orientations (rotated or not)
    for (w, h) in [(chip.width, chip.height), (chip.height, chip.width)]:
        for r in range(rows - h + 1):
            for c in range(columns - w + 1):
                placements.append((r, c, w, h))
    return placements


class NonOverlappingConstraint(Constraint[Chip, tuple[int,int,int,int]]):
    """Constraint ensuring that no two chips overlap on the grid."""
    def __init__(self, chips: list[Chip]) -> None:
        super().__init__(chips)
    
    def satisfied(self, assignment: dict[Chip, tuple[int,int,int,int]]) -> bool:
        placements = list(assignment.values())
        for i in range(len(placements)):
            r1, c1, w1, h1 = placements[i]
            for j in range(i + 1, len(placements)):
                r2, c2, w2, h2 = placements[j]
                # overlap occurs if rectangles intersect
                if not (r1 + h1 <= r2 or   # A above B
                        r2 + h2 <= r1 or   # B above A
                        c1 + w1 <= c2 or   # A left of B
                        c2 + w2 <= c1):    # B left of A
                    return False
        return True


def solution(chips: list[Chip], grid: Grid) -> Grid | None:
    """
    Find a way to fit all of the chips onto the board and return 
    a filled-in grid. If the chips can't fit, return None.
    """
    rows, cols = len(grid), len(grid[0])

    # Build domains for each chip
    domains: dict[Chip, list[tuple[int,int,int,int]]] = {
        chip: generate_domain(chip, rows, cols) for chip in chips
    }

    # Set up CSP
    csp: CSP[Chip, tuple[int,int,int,int]] = CSP(chips, domains)
    csp.add_constraint(NonOverlappingConstraint(chips))

    # Run backtracking search
    assignment = csp.backtracking_search()
    if assignment is None:
        return None

    # Build new grid with assignments
    new_grid = [row[:] for row in grid]
    for chip, (r, c, w, h) in assignment.items():
        for dr in range(h):
            for dc in range(w):
                new_grid[r + dr][c + dc] = chip.symbol
    return new_grid


# ---------------------------
# Manual Test Run
# ---------------------------
if __name__ == "__main__":
    easy_grid = generate_grid(10, 10)
    easy_chips = [Chip(5, 5, "*"), Chip(4, 4, "#"), Chip(2, 2, "@")]
    sol = solution(easy_chips, easy_grid)
    if sol is None:
        print("No solution found!")
    else:
        display_grid(sol)
