"""
Track-to-track fusion algorithms

References:
[1] Stephan Matzka and Richard Altendorfer - A Comparison of Track-to-Track Fusion Algorithms for Automotive Sensor Fusion
[2] Nico Kampchen - Feature-Level Fusion of Laser Scanner and Video Data for Advanced Driver Assistance Systems
[3] Chee-Yee Chong et al. - Architectures and Algorithms for Track Association and Fusion
[4] Angelos Amditis et al. - Multiple Sensor Collision avoidance system for automotive applications using an IMM approach for obstacle tracking
[5] Shozo Mori et al. - Track Association and Track Fusion with Non-Deterministic Target Dynamics
"""

import numpy as np
from numpy.core.umath_tests import matrix_multiply

from fusutils import matrixop

def weightedAverage(xi, xj, Pi, Pj, isDiag=False):
  """ Calculates fused state estimates and covariance matrices of 2 tracks (aligned in time), 
  under the assumption that the cross-covariance matrices between the tracks can be ignored.
  See e.g. [3], section 4.1.1 Basic Convex Combination
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
  :ReturnType: tuple
    ( xfus<ndarray, shape (N,M)>, Pfus<ndarray, shape (N,M,M)> )
    The tuple of fused state estimates and covariance matrices (with the same dimensions as the inputs).
  :Exceptions:
    AssertionError
      in case of shape mismatch
    numpy.linalg.LinAlgError
      if any of the covariance matrices is singular
  """
  assert     xi.shape == xj.shape\
         and Pi.shape == Pj.shape\
         and xi.shape[0] == Pi.shape[0]\
         and xi.shape[1] == Pi.shape[1] == Pi.shape[2]
  M = Pi.shape[1]
  if M == 2:
    inv = matrixop.inv2x2
  elif isDiag:
    inv = matrixop.invDiag
  else:
    inv = matrixop.invStepByStep
  PiInv = inv(Pi)
  PjInv = inv(Pj)
  Pfus  = inv(PiInv + PjInv)
  Ti = matrix_multiply(PiInv, xi[...,np.newaxis])
  Tj = matrix_multiply(PjInv, xj[...,np.newaxis])
  xfus = matrix_multiply(Pfus, Ti+Tj)[...,0]
  return xfus, Pfus
  
  
  
  