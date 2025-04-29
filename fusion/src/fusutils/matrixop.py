"""
Vectorized linear algebra operations.
"""

import numpy as np
from numpy.core.umath_tests import matrix_multiply
from scipy.stats import chi2

EPS = 1e-6

def inv2x2(m):
  """ Calculates inverse of 2x2 matrices (aligned in time).
  Note: returns zero inverse matrices in place of any singular matrices
  
  :Parameters:
      m : ndarray; shape (N,2,2)
        Matrices to be inverted.
  :ReturnType: ndarray; shape (N,2,2)
    Returns the inverse matrices of (regular) matrices
  :Exceptions:
    AssertionError
      in case of shape mismatch
    numpy.linalg.LinAlgError
      if any of the matrices is singular
  """
  assert m.ndim == 3 and m.shape[1] == m.shape[2] == 2
  a = m[:,0,0]
  b = m[:,0,1]
  c = m[:,1,0]
  d = m[:,1,1]
  denom = a*d - b*c
  if np.any( np.abs(denom) < (EPS**2) ):
    raise np.linalg.LinAlgError('Matrix close to singular')
  np.reciprocal(denom, denom) # in-place reciprocal
  mInv = np.empty_like(m)
  mInv[:,0,0] =  denom * d
  mInv[:,0,1] = -denom * b
  mInv[:,1,0] = -denom * c
  mInv[:,1,1] =  denom * a
  return mInv

def invDiag(m):
  """ Calculates inverse of diagonal matrices (aligned in time).
  
  :Parameters:
      m : ndarray; shape (N,M,M)
        Diagonal matrices to be inverted.
  :ReturnType: ndarray; shape (N,M,M)
    Returns the inverse matrices (aligned in time).
  :Exceptions:
    AssertionError
      in case of shape mismatch
    numpy.linalg.LinAlgError
      if any of the matrices is singular
  """
  assert m.ndim == 3 and m.shape[1] == m.shape[2]
  mDiag = m.diagonal(axis1=1, axis2=2) # As of NumPy 1.7, 'diagonal' always returns a view into the array
  if np.any( np.abs(mDiag) < EPS ):
    raise np.linalg.LinAlgError('Matrix close to singular')
  mInv = np.copy(m)
  M = mInv.shape[1]
  # loop on diagonals ~M
  for i in xrange(M):
    diag = mInv[:,i,i]
    np.reciprocal(diag, diag) # in-place reciprocal
  return mInv
  
def invStepByStep(m):
  """ Calculates inverse of square matrices (aligned in time) 
  step by step.
  
  :Parameters:
      m : ndarray; shape (N,M,M)
        Matrices to be inverted.
  :ReturnType: ndarray; shape (N,M,M)
    Returns the inverse matrices (aligned in time).
  :Exceptions:
    AssertionError
      in case of shape mismatch
    numpy.linalg.LinAlgError
      if any of the matrices is singular
  """
  assert m.ndim == 3 and m.shape[1] == m.shape[2]
  mInv  = np.zeros_like(m)
  # loop on each time step ~N
  for i in xrange( m.shape[0] ):
    mInv[i] = np.linalg.inv( m[i] )
  return mInv
  
def errorEllipseDiag2x2(diagC, conf=0.95, offset=None, scale=None, numPoints=50):
  """ Calculates the error ellipse points of diagonal 2x2 covariance matrices (aligned in time)
  for a given confidence level.
  Remark: The general error ellipse computations can be simlified and vectorized based upon 
  the diagonal matrix criterion, therefore the diagonal property is NOT negligible.
  
  :Parameters:
      diagC : ndarray; shape (N,2,2)
        Diagonal 2x2 covariance matrices, aligned in time.
  :KeyWords:
      conf : float
        Required confidence level from (0,1) interval. Default value is 0.95.
      offset : ndarray; shape (N,2)
        Ellipse optional x-y offset (usually the state estimates). There is no offset by default. 
      scale : float
        Ellipse optional scaling. There is no scaling by default.
      numPoints : int
        Number of points controlling ellipse resolution. Default value is 50.
  :ReturnType: ndarray; shape (N,numPoints,2)
    The error ellipse points, where the last dimension corresponds to the x and y coordinates, 
    respectively.
  :Exceptions:
    AssertionError
      in case of invalid input parameter
  """
  assert diagC.ndim == 3 and diagC.shape[1] == diagC.shape[2] == 2
  diag = diagC[:,(0,1),(0,1)]
  offDiag = diagC[:,(0,1),(1,0)]
  assert np.all( diag > 0. ) # check positive definiteness
  assert np.all( (offDiag >= 0.) & (offDiag < EPS) ) # check diagonality
  assert conf > 0. and conf < 1.
  # quantile of chi square distribution for given confidence level and degree of freedom
  chi2dof = diagC.shape[1]
  quant = chi2.ppf(conf, chi2dof)
  # calculate ellipse points
  phi = np.linspace(0., 2*np.pi, numPoints)
  phi2 = phi[:,np.newaxis]
  proj = np.concatenate( (np.cos(phi2),np.sin(phi2)), axis=1 )
  pts = matrix_multiply(proj, np.sqrt(quant*diagC))
  # scaling and translating ellipse
  if scale is not None:
    pts *= scale
  if offset is not None:
    pts += offset[:,np.newaxis,:]
  return pts

if __name__ == '__main__':
  import matplotlib.pyplot as plt
  
  # check 2x2 matrix inverse
  m = np.array(
    [
      [[1.1 , 0.61],
       [0.13, 0.5 ]],
       
      [[0.2 , 0.34],
       [0.15, 0.9 ]],
       
      [[2.4 , 0.33],
       [0.71, 0.45]],
    ]
  ) # shape (N,M,M)
  mInv = inv2x2(m)
  N,M,_ = m.shape
  eye     = np.eye(M)
  eyeRef  = np.array((eye,eye,eye))
  eyeCalc = matrix_multiply(m, mInv)
  assert np.all( np.abs(eyeRef-eyeCalc) < EPS )

  # check error ellipse
  diagC = np.copy(m)
  try:
    errorEllipseDiag2x2(diagC)
  except AssertionError:
    diagC[:,(0,1),(1,0)] = 0. # clear off-diagonals
    pts1 = errorEllipseDiag2x2(diagC)
    pts2 = errorEllipseDiag2x2(diagC, offset=np.zeros(shape=(N,M)))
    pts3 = errorEllipseDiag2x2(diagC, scale=1.0)
    assert np.all( (np.abs(pts1-pts2) < EPS) & (np.abs(pts1-pts3) < EPS) )
    # plot ellipses
    for pts in pts1:
      plt.plot(pts[:,0], pts[:,1])
  else:
    raise ValueError('Error: non diagonal matrix passed!')
  
  # check MxM diagonal matrix inverse
  M = 15
  N = 1000
  mDiag = np.random.rand(M)
  mDiag += EPS
  m = np.diag(mDiag)
  m = np.resize(m, (N,M,M))
  mInv = invDiag(m)
  eye     = np.eye(M)
  eyeRef  = np.resize(eye, (N,M,M))
  eyeCalc = matrix_multiply(m, mInv)
  assert np.all( np.abs(eyeRef-eyeCalc) < EPS )
  
  # check MxM matrix inverse
  m = np.random.rand(M*M)
  m = np.resize(m, (N,M,M))
  try:
    mInv = invStepByStep(m)
  except np.linalg.LinAlgError, error:
    print error.message
  else:
    eyeCalc = matrix_multiply(m, mInv)
    assert np.all( np.abs(eyeRef-eyeCalc) < EPS )

  # show ellipses
  plt.show()