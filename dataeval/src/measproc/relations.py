"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

not_equal = lambda a, b: a != b
"""
Not Equal relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""
    
equal = lambda a, b: a == b
"""
Equality relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""

greater = lambda a, b: a > b
"""
Greater relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""

greater_equal = lambda a, b: a >= b
"""
Greater-or-equal relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""

less = lambda a, b: a < b
"""
Less relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""

less_equal = lambda a, b: a <= b
"""
Less-or-equal relation. The parameters have to have same size.

:Parameters:
  a : `ndarray`
  b : `ndarray` or float
    `ndarray` with the same dmension like `a` or scalar.
:ReturnType: bool `ndarray`
"""
