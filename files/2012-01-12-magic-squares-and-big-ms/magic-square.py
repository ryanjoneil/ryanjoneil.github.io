#!/usr/bin/env python3

# This script solves the Magic Square problem using SCIP.
# https://en.wikipedia.org/wiki/Magic_square
#
# This is a constraint satisfaction problem. For a square matrix of size n, we
# seek n*n integers such that the following constraints are satisfied:
#
#   1. All variables are integers >= 1
#   2. All rows, all columns, and the diagonal sum to the same value
#   3. All variables are different
#
# The first argument to the script is required. This specifies the size of the
# matrix. The second, the maximum value of any variable, is optional, and may
# speed up solution time significantly.

from itertools import chain
from pyscipopt import Model
import sys

if __name__ == '__main__':
    m = Model()

    try:
        # Matrix size is required and should be >= 2.
        size = int(sys.argv[1])
        assert size > 1

        # Big-M is optional. If provided it must be a positive integer. If not,
        # we ask the optimizer to determine M for us.
        try:
            M = int(sys.argv[2])
        except IndexError:
            M = m.addVar(vtype="M", lb=size * size)
        else:
            assert M >= size * size

    except:
        print('usage: %s matrix-size [big-M]' % sys.argv[0])
        sys.exit()

    # Construct a matrix of decision variables.
    matrix = []
    for i in range(size):
        row = [m.addVar(vtype="I", lb=1) for _ in range(size)]
        for x in row:
            m.addCons(x <= M)
        matrix.append(row)

    # The rows and columns must all sum to the same value.
    sum_val = m.addVar(vtype="M")
    for i in range(size):
        # Row i sum
        m.addCons(sum(matrix[i]) == sum_val)

        # Column i sum
        m.addCons(sum(matrix[j][i] for j in range(size)) == sum_val)

    # Diagonal sum must be the same too.
    m.addCons(sum(matrix[i][i] for i in range(size)) == sum_val)

    # No two variables can have the same value.
    all_vars = list(chain(*matrix))
    for i, x in enumerate(all_vars):
        for y in all_vars[i+1:]:
            # x and y must be different integers. To enforce this, we require a
            # big-M (whether it is a variable or a constant and an additional
            # binary variable. The binary variable turns on exactly one of the
            # two constraints below, so either:
            #     x >= y + 1
            # or:
            #     x <= y - 1
            z = m.addVar(vtype="B")
            m.addCons(x >= y + 1 - M*z)
            m.addCons(x <= y - 1 + M*(1-z))

    m.optimize()
    assert m.getStatus() in ("feasible", "optimal")

    solution = m.getBestSol()
    print('sum = %d' % solution[sum_val])
    print('magic square:')
    for row in matrix:
        for x in row:
            print('% 6d' % solution[x], end=' ')
        print()
