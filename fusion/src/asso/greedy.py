""" Greedy solution of the 2D assignment problem """

import numpy as np

def greedy(m, inf=None):
  """
  Compute the indexes of lowest-cost pairings (in greedy sense)
  between rows and columns of the input cost matrix.
  
  :Parameters:
      m : numpy.ndarray
        2-dimensional cost matrix, rectangular (non-square) matrix allowed.
      inf : float, optional
        Finite value that represents invalid association ("infinite") cost.
        Any cost greater or equal to this value will be discarded from solution (!)
  :Exceptions:
    AssertionError : if input parameters are incorrect
  :ReturnType: list
  :Return:
    List of row-column pairings [ (rowNum<int>,colNum<int>), ... ]
  """
  assert m.ndim == 2
  results = []
  N,M = m.shape
  rows = range(N)
  cols = range(M)
  k = 0
  # loop while cost matrix is not shrunk totally
  while m.size > 0:
    # get indices of actual minimum value (note: memory order param is skipped, since argmin() iterates on flat C-cont. array by default)
    i,j = np.unravel_index(m.argmin(), m.shape)
    if inf is not None and m[i,j] >= inf:
      # quit loop (invalid cost has been reached)
      break
    else:
      # register current minimal cost pairing
      results.append( (rows[i],cols[j]) )
      rows.pop(i)
      cols.pop(j)
      maski = np.ones(N-k, dtype=np.bool)
      maskj = np.ones(M-k, dtype=np.bool)
      maski[i] = False
      maskj[j] = False
      m = m[maski][:,maskj]
    k += 1
  return results

class Greedy(object):
  def compute(self, m, inf=None):
    return greedy(m, inf=inf)
