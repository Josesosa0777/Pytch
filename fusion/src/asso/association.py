"""
2D track-to-track association algorithms

Requirements
------------
* `Python 2.5 or 2.6 <http://www.python.org>`

Assumptions
----------
* Tracks contain information only from common field of view
* Tracks are aligned in time and coordinate system

References:
[1] Blackman, Popoli - Design and Analysis of Modern Tracking Systems
"""

import numpy as np
from numpy.core.umath_tests import matrix_multiply
# DEBUG imports
# from scipy.linalg import cholesky, LinAlgError

from fusutils import matrixop

CORR_COEFF_EST = 0.4 # estimated value of correlation coefficient (see [1])

def _calcResidCovarMatrices(Pi,Pj):
  """ Calculates association residual covariance matrices (in time) from state 
  covariance matrices of 2 tracks.
  Note for array shapes: N time length, M state dimension
  
  :Parameters:
      Pi : ndarray; shape (N,M,M)
        state covariance matrices of the 1st sensor's i-th track, aligned in time
      Pj : ndarray; shape (N,M,M)
        state covariance matrices of the 2nd sensor's j-th track, aligned in time
  :ReturnType: ndarray; shape (N,M,M)
  """
  # cross covariance estimation (elementwise operations)
  # PiPj = np.multiply(Pi,Pj)
  # with np.errstate(invalid='ignore'):
    # Pij = CORR_COEFF_EST * np.where( PiPj > 0.,
                                       # np.sqrt( PiPj),
                                       # np.sqrt(-PiPj))
  # Pij_T = np.transpose(Pij, axes=(0,2,1))
  # calc residual covariance matrix
  S = Pi + Pj # - Pij - Pij_T
  return S

def calcCostMatrixElements(xi, xj, Pi, Pj, isDiag=False):
  """ Calculates cost matrix elements from state estimates and covariance matrices of 2 tracks.
  Note for array shapes: N time length, M state dimension
  
  :Parameters:
      xi : ndarray; shape (N,M)
        state estimates of the 1st sensor's i-th track, aligned in time
      xj : ndarray; shape (N,M)
        state estimates of the 2nd sensor's j-th track, aligned in time
      Pi : ndarray; shape (N,M,M)
        state covariance matrices of the 1st sensor's i-th track, aligned in time
      Pj : ndarray; shape (N,M,M)
        state covariance matrices of the 2nd sensor's j-th track, aligned in time
      isDiag : bool
        Indicates if the covariance matrices are diagonal (i.e. only variances are given).
        Default is False.
  :ReturnType: ndarray; shape (N,)
  """
  assert     xi.shape == xj.shape\
         and Pi.shape == Pj.shape\
         and xi.shape[0] == Pi.shape[0]\
         and xi.shape[1] == Pi.shape[1] == Pi.shape[2]
  S     = _calcResidCovarMatrices(Pi,Pj)
  N     = S.shape[0]
  M     = S.shape[1]
  if M == 2:
    Sinv = matrixop.inv2x2(S)
  elif isDiag:
    Sinv = matrixop.invDiag(S)
  else:
    Sinv  = matrixop.invStepByStep(S)
    # Snorm = np.zeros(shape=(N,), dtype=S.dtype)
    # for k, Sk in enumerate(S):
      # try:
        # cholesky(Sk) # DEBUG: check positive definiteness
      # except LinAlgError, error:
        # print error.message, Sk
      # Snorm[k] = np.linalg.norm(Sk) # 2-norm
  xij   = xi[...,np.newaxis] - xj[...,np.newaxis] # expand dimension
  xij_T = np.transpose(xij, axes=(0,2,1))
  # calc statistical distance
  tmp  = matrix_multiply(xij_T, Sinv)
  d2ij = matrix_multiply(tmp, xij)
  d2ij.shape = N # flatten array
  # # calc penalty for uncertain tracks (can be negative!)
  # penalty = 2*np.log( np.sqrt(Snorm) )
  # calc cost
  costij = d2ij # + penalty
  return costij

def calcGate(signifLevel, dist, *args, **kwargs):
  """ Calculates gate size according to the given significance level and distribution.
    
    :Parameters:
      signifLevel : float
        significance level of hypothesis test, in (0,1) range
      dist : scipy.stats.rv_continuous
        supposed distribution of the sample dataset
      optional arguments and keyword arguments are given to the distribution's quantile function.
  :ReturnType: float
  """
  gate = dist.ppf(signifLevel, *args, **kwargs)
  return gate

def shrinkCostMatrix(C, maskInvalid):
  """ Shrinks cost matrix by removing rows and columns that contain invalid association costs only.
  
  :Parameters:
      C : ndarray; shape (K,L)
        cost matrix
      maskInvalid : ndarray; shape (K,L)
        bool mask indicating invalid association costs
  :ReturnType: ndarray, list, list
  :Return: Ccut, validRows, validCols
    Ccut : ndarray
      reduced cost matrix, does not share memory with input
    validRows : list
      valid row numbers of input cost matrix
    validCols : list
      valid column numbers of input cost matrix
  """
  assert     C.ndim == maskInvalid.ndim == 2 \
         and C.shape == maskInvalid.shape
  K,L = C.shape
  # mark invalid rows
  rowMask = np.ones(K, dtype=np.bool)
  validRows = []
  for i in xrange(K):
    if np.all(maskInvalid[i]):
      rowMask[i] = False
    else:
      validRows.append(i)
  # mark invalid columns
  columnMask = np.ones(L, dtype=np.bool)
  validCols = []
  for j in xrange(L):
    if np.all(maskInvalid[:,j]):
      columnMask[j] = False
    else:
      validCols.append(j)
  # cut matrix dimensions
  Ccut = C[rowMask][:,columnMask] # advanced indexing creates copy (orig. matrix is safe)
  return Ccut, validRows, validCols
