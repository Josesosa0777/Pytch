"""
Solve the unique lowest-cost assignment problem using the
Hungarian algorithm (also known as Munkres algorithm).

References
==========

1. http://www.public.iastate.edu/~ddoty/HungarianAlgorithm.html

2. Harold W. Kuhn. The Hungarian Method for the assignment problem.
   *Naval Research Logistics Quarterly*, 2:83-97, 1955.

3. Harold W. Kuhn. Variants of the Hungarian method for assignment
   problems. *Naval Research Logistics Quarterly*, 3: 253-258, 1956.

4. Munkres, J. Algorithms for the Assignment and Transportation Problems.
   *Journal of the Society of Industrial and Applied Mathematics*,
   5(1):32-38, March, 1957.

5. http://en.wikipedia.org/wiki/Hungarian_algorithm

"""
# Based on original code by Brain Clapper, adapted to numpy to scikits
# learn coding standards by G. Varoquaux

# Copyright (c) 2008 Brian M. Clapper <bmc@clapper.org>, G Varoquaux
# Author: Brian M. Clapper, G Varoquaux
# LICENSE: BSD

import numpy as np

################################################################################
# Object-oriented form of the algorithm
class _Hungarian(object):
    """
    Calculate the Munkres solution to the classical assignment problem.
    See the module documentation for usage.
    """

    def compute(self, cost_matrix):
        """
        Compute the indexes for the lowest-cost pairings between rows and
        columns in the database. Returns a list of (row, column) tuples
        that can be used to traverse the matrix.

        Parameters
        ===========
        cost_matrix: 2D square matrix
                The cost matrix. 

        Returns
        ========
        indices: 2D array of indices
            The pairs of (col, row) indices in the original array giving
            the original ordering.
        """
        self.C = cost_matrix.copy()
        self.n = n = self.C.shape[0]
        self.m = m = self.C.shape[1]
        self.row_uncovered = np.ones(n, dtype=np.bool)
        self.col_uncovered = np.ones(m, dtype=np.bool)
        self.Z0_r = 0
        self.Z0_c = 0
        self.path = np.zeros((n+m, 2), dtype=int)
        self.marked = np.zeros((n, m), dtype=int)

        done = False
        step = 1

        steps = { 1 : self._step1,
                  3 : self._step3,
                  4 : self._step4,
                  5 : self._step5,
                  6 : self._step6 }

        if m == 0 or n == 0 :
            # No need to bother with assignments if one of the dimensions
            # of the cost matrix is zero-length.
            done = True

        while not done:
            try:
                func = steps[step]
                step = func()
            except KeyError:
                done = True

        # Look for the starred columns
        results = np.array(np.where(self.marked == 1)).T

        return results.tolist()

    def _step1(self):
        """ Steps 1 and 2 in the wikipedia page.
        """
        # Step1: For each row of the matrix, find the smallest element and
        # subtract it from every element in its row.
        self.C -= self.C.min(axis=1)[:, np.newaxis]
        # Step2: Find a zero (Z) in the resulting matrix. If there is no 
        # starred zero in its row or column, star Z. Repeat for each element 
        # in the matrix.
        for i, j in zip(*np.where(self.C == 0)):
            if self.col_uncovered[j] and self.row_uncovered[i]:
                self.marked[i, j] = 1
                self.col_uncovered[j] = False
                self.row_uncovered[i] = False

        self._clear_covers()
        return 3

    def _step3(self):
        """
        Cover each column containing a starred zero. If n columns are
        covered, the starred zeros describe a complete set of unique
        assignments. In this case, Go to DONE, otherwise, Go to Step 4.
        """
        marked = (self.marked == 1)
        self.col_uncovered[np.any(marked, axis=0)] = False

        if marked.sum() >= min(self.m, self.n) :
            return 7 # done
        else:
            return 4

    def _step4(self):
        """
        Find a noncovered zero and prime it. If there is no starred zero
        in the row containing this primed zero, Go to Step 5. Otherwise,
        cover this row and uncover the column containing the starred
        zero. Continue in this manner until there are no uncovered zeros
        left. Save the smallest uncovered value and Go to Step 6.
        """
        # We convert to int as numpy operations are faster on int
        C = (self.C == 0).astype(np.int)
        covered_C = C*self.row_uncovered[:, np.newaxis]
        covered_C *= self.col_uncovered.astype(np.int)
        n = self.n
        m = self.m
        while True:
            # Find an uncovered zero
            row, col = np.unravel_index(np.argmax(covered_C), (n, m))
            if covered_C[row, col] == 0:
                return 6
            else:
                self.marked[row, col] = 2
                # Find the first starred element in the row
                star_col = np.argmax(self.marked[row] == 1)
                if not self.marked[row, star_col] == 1:
                    # Could not find one
                    self.Z0_r = row
                    self.Z0_c = col
                    return 5
                else:
                    col = star_col
                    self.row_uncovered[row] = False
                    self.col_uncovered[col] = True
                    covered_C[:, col] = C[:, col]*(
                                self.row_uncovered.astype(np.int))
                    covered_C[row] = 0


    def _step5(self):
        """
        Construct a series of alternating primed and starred zeros as
        follows. Let Z0 represent the uncovered primed zero found in Step 4.
        Let Z1 denote the starred zero in the column of Z0 (if any).
        Let Z2 denote the primed zero in the row of Z1 (there will always
        be one). Continue until the series terminates at a primed zero
        that has no starred zero in its column. Unstar each starred zero
        of the series, star each primed zero of the series, erase all
        primes and uncover every line in the matrix. Return to Step 3
        """
        count = 0
        path = self.path
        path[count, 0] = self.Z0_r
        path[count, 1] = self.Z0_c
        done = False
        while not done:
            # Find the first starred element in the col defined by
            # the path.
            row = np.argmax(self.marked[:, path[count, 1]] == 1)
            if not self.marked[row, path[count, 1]] == 1:
                # Could not find one
                done = True
            else:
                count += 1
                path[count, 0] = row
                path[count, 1] = path[count-1, 1]

            if not done:
                # Find the first prime element in the row defined by the
                # first path step
                col = np.argmax(self.marked[path[count, 0]] == 2)
                if self.marked[row, col] != 2:
                    col = -1
                count += 1
                path[count, 0] = path[count-1, 0]
                path[count, 1] = col

        # Convert paths
        for i in range(count+1):
            if self.marked[path[i, 0], path[i, 1]] == 1:
                self.marked[path[i, 0], path[i, 1]] = 0
            else:
                self.marked[path[i, 0], path[i, 1]] = 1

        self._clear_covers()
        # Erase all prime markings
        self.marked[self.marked == 2] = 0
        return 3

    def _step6(self):
        """
        Add the value found in Step 4 to every element of each covered
        row, and subtract it from every element of each uncovered column.
        Return to Step 4 without altering any stars, primes, or covered
        lines.
        """
        # the smallest uncovered value in the matrix
        if np.any(self.row_uncovered) and np.any(self.col_uncovered):
            minval = np.min(self.C[self.row_uncovered], axis=0)
            minval = np.min(minval[self.col_uncovered])
            self.C[np.logical_not(self.row_uncovered)] += minval
            self.C[:, self.col_uncovered] -= minval
        return 4

    def _find_prime_in_row(self, row):
        """
        Find the first prime element in the specified row. Returns
        the column index, or -1 if no starred element was found.
        """
        col = np.argmax(self.marked[row] == 2)
        if self.marked[row, col] != 2:
            col = -1
        return col

    def _clear_covers(self):
        """Clear all covered matrix cells"""
        self.row_uncovered[:] = True
        self.col_uncovered[:] = True



################################################################################
# Functional form for easier use
def hungarian(cost_matrix):
    """ Return the indices to permute the columns of the matrix
        to minimize its trace.
    """
    H = _Hungarian()
    indices = H.compute(cost_matrix)
    indices.sort()
    # Re-force dtype to ints in case of empty list
    indices = np.array(indices, dtype=int)
    # Make sure the array is 2D with 2 columns.
    # This is needed when dealing with an empty list
    indices.shape = (-1, 2)
    return indices.T[1]


def find_permutation(vectors, reference):
    """ Returns the permutation indices of the vectors to maximize the
        correlation to the reference
    """
    # Compute a correlation matrix
    reference = reference/(reference**2).sum(axis=-1)[:, np.newaxis]
    vectors = vectors/(vectors**2).sum(axis=-1)[:, np.newaxis]
    K = np.abs(np.dot(reference, vectors.T))
    K -= 1 + K.max()
    K *= -1
    return hungarian(K)

################################################################################
# test_hungarian.py is merged here for easier use
# Author: Brian M. Clapper, G Varoquaux
# LICENSE: BSD

def test_hungarian():
    matrices = [
                # Square
                ([[400, 150, 400],
                  [400, 450, 600],
                  [300, 225, 300]],
                 850 # expected cost
                ),

                ## Rectangular variant
                ([[400, 150, 400, 1],
                  [400, 450, 600, 2],
                  [300, 225, 300, 3]],
                 452 # expected cost
                ),

                # Square
                ([[10, 10,  8],
                  [ 9,  8,  1],
                  [ 9,  7,  4]],
                 18
                ),

                ## Rectangular variant
                ([[10, 10,  8, 11],
                  [ 9,  8,  1, 1],
                  [ 9,  7,  4, 10]],
                 15
                ),

                ## n == 1, m == 0 matrix
                ([[]],
                 0
                ),
                
                ## 2x2
                ([[1.3, 12.0],
                  [4.5, 11.2]],
                 12.5
                ),
               ]

    m = _Hungarian()
    for cost_matrix, expected_total in matrices:
        print np.array(cost_matrix)
        cost_matrix = np.array(cost_matrix)
        indexes = m.compute(cost_matrix)
        total_cost = 0
        for r, c in indexes:
            x = cost_matrix[r, c]
            total_cost += x
        assert expected_total == total_cost
        print indexes, total_cost


def test_find_permutation():
    A = np.random.random((10, 100))
    B = A[::-1]
    np.testing.assert_array_equal(find_permutation(B, A),
                                  np.arange(10)[::-1])


if __name__ == '__main__' :
    print "find_permutations test..."
    test_find_permutation()
    print "Hungarian test..."
    test_hungarian()
