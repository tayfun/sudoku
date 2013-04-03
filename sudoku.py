from __future__ import print_function
from time import time
from functools import partial
import copy

print = partial(print, end="")


class SudokuContradiction(Exception):
    """
    Used for detecting if the sudoku cannot be solved with the current
    assumptions. When caught, go back and try another possible value.
    """
    pass


class Sudoku(object):
    def __init__(self, sudoku_repr):
        """
        Created a sudoku puzzle. Each puzzle is represented as a 9 x 9
        square with empty cells having an underscore character. For example:

                    1 _ 7  6 8 5  4 _ 2
                    _ _ _  9 1 _  6 3 _
                    _ _ _  2 _ _  1 _ _

                    _ _ _  4 6 9  _ 2 _
                    _ 5 _  _ _ _  _ 6 _
                    _ 6 _  3 5 8  _ _ _

                    _ _ 9  _ _ 6  _ _ _
                    _ 8 3  _ 9 1  _ _ _
                    6 _ 1  5 2 3  9 _ 4

        Also initializes the digits which will be used in solving the puzzle.
        """
        self.puzzle = []
        self.digits = set([str(i) for i in xrange(1, 10)])
        lines = sudoku_repr.splitlines()
        for line in lines:
            if not line.strip():
                continue
            self.puzzle.append(line.split())

    def pprint(self):
        """
        Pretty print sudoku puzzle.
        """
        print("\n\n")
        for lineno, line in enumerate(self.puzzle):
            for cellno, cell in enumerate(line):
                if cellno == 2 or cellno == 5:
                    print("%s    " % cell)
                else:
                    print("%s " % cell)
            if lineno == 2 or lineno == 5:
                print("\n")
            print("\n")
        print("\n\n")

    def check(self, row, column):
        cell = self.puzzle[row][column]
        if cell == "_":
            cell = self.digits
        elif not isinstance(cell, set):
            # this cell already has its value.
            return
        impossible_set = set()
        # add numbers in the row to impossible set.
        for a in xrange(9):
            if not isinstance(self.puzzle[a][column], set):
                impossible_set.add(self.puzzle[a][column])
            if not isinstance(self.puzzle[row][a], set):
                impossible_set.add(self.puzzle[row][a])

        row_start = row if row % 3 == 0 else row - row % 3
        column_start = column if column % 3 == 0 else column - column % 3
        for a in xrange(3):
            for b in xrange(3):
                square_cell = self.puzzle[row_start + a][column_start + b]
                if not isinstance(square_cell, set):
                    impossible_set.add(square_cell)
        impossible_set.discard("_")
        possible_set = cell.difference(impossible_set)
        if len(possible_set) == 1:
            self.puzzle[row][column] = possible_set.pop()
            # Constraints changed. Calculate them again. Not that this isn't
            # a smart recalculation. It would be better to check only those
            # cells in a unit, not the whole puzzle.
            self.solve()
        elif not possible_set:
            raise SudokuContradiction()
        else:
            self.puzzle[row][column] = possible_set

    def constraint_prop(self):
        for a, row in enumerate(self.puzzle):
            for b, column in enumerate(row):
                if isinstance(column, set):
                    # let's assign a value to this column from possible values
                    # and carry on.
                    for value in column:
                        # Note that we do deepcopy which is a bad idea but
                        # sets and list data structures I'm using necessitate
                        # using deepcopy.
                        # Norvig uses dictionary and plain strings as data
                        # structure so he can simply get away with shallow
                        # copy. Oh well.
                        new_sudoku = copy.deepcopy(self)
                        new_sudoku.puzzle[a][b] = value
                        try:
                            solved_sudoku = new_sudoku.solve()
                            return solved_sudoku
                        except SudokuContradiction:
                            continue
                    else:
                        # we couldn't find a non contradicting solution
                        raise SudokuContradiction()
        # if there were no empty cells, return sudoku directly.
        return self

    def calculate_sets(self):
        """
        Calculate possible values set for each cell.
        """
        for a in xrange(9):
            for b in xrange(9):
                self.check(a, b)

    def solve(self):
        """
        Calculates possible values and then tries guessing when there are
        multiple choices.
        """
        self.calculate_sets()
        # constraint propagation means we can solve this puzzle brute force in
        # a reasonable amount of time.
        return self.constraint_prop()

    def validate(self):
        """
        Validates that the solution is correct.
        """
        # row validation
        for i in xrange(9):
            if len(set(self.puzzle[i])) != 9:
                print("ERROR: Did not validate!! Row %d \n" % i)
        # column validation
        for i in xrange(9):
            if len(set([self.puzzle[row][i]
                        for row in xrange(9)])) != 9:
                print("ERROR: Did not validate!! Column %s \n" % i)
        # square validation
        for row_start in xrange(0, 9, 3):
            for column_start in xrange(0, 9, 3):
                square_set = set([
                    self.puzzle[row_start + a][column_start + b] for a in
                    xrange(3) for b in xrange(3)
                ])
                if len(square_set) != 9:
                    print("ERROR: Did not validate!! Square %s %s \n"
                          % row_start, column_start)


if __name__ == "__main__":
    sudoku_repr = """
        1 _ 7  6 8 5  4 _ 2
        _ _ _  9 1 _  6 3 _
        _ _ _  2 _ _  1 _ _

        _ _ _  4 6 9  _ 2 _
        _ 5 _  _ _ _  _ 6 _
        _ 6 _  3 5 8  _ _ _

        _ _ 9  _ _ 6  _ _ _
        _ 8 3  _ 9 1  _ _ _
        6 _ 1  5 2 3  9 _ 4
    """
    sudoku = Sudoku(sudoku_repr)
    sudoku.pprint()
    start = time()
    solved_sudoku = sudoku.solve()
    solved_sudoku.pprint()
    solved_sudoku.validate()
    elapsed = time() - start
    print("Took %d seconds to finish this one.\n" % elapsed)
    sudoku_hard = """
        4 _ _  _ _ _  8 _ 5
        _ 3 _  _ _ _  _ _ _
        _ _ _  7 _ _  _ _ _

        _ 2 _  _ _ _  _ 6 _
        _ _ _  _ 8 _  4 _ _
        _ _ _  _ 1 _  _ _ _

        _ _ _  6 _ 3  _ 7 _
        5 _ _  2 _ _  _ _ _
        1 _ 4  _ _ _  _ _ _
        """
    sudoku = Sudoku(sudoku_hard)
    sudoku.pprint()
    start = time()
    solved_sudoku = sudoku.solve()
    solved_sudoku.pprint()
    solved_sudoku.validate()
    elapsed = time() - start
    print("Took %d seconds to finish this one.\n" % elapsed)
    sudoku_evil = """
        8 _ _  2 _ _  _ 4 _
        3 _ _  _ _ _  _ 1 _
        _ _ 1  _ _ 3  5 _ _

        _ _ 3  5 _ _  _ 2 _
        _ _ 2  3 _ 6  1 _ _
        _ 9 _  _ _ 4  6 _ _

        _ _ 4  6 _ _  9 _ _
        _ 7 _  _ _ _  _ _ 6
        _ 1 _  _ _ 5  _ _ 3
    """
    sudoku = Sudoku(sudoku_evil)
    sudoku.pprint()
    start = time()
    solved_sudoku = sudoku.solve()
    solved_sudoku.pprint()
    solved_sudoku.validate()
    elapsed = time() - start
    print("Took %d seconds to finish this one.\n" % elapsed)
