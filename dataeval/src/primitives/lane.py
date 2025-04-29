import copy

import numpy as np

from .bases import Primitive
from measparser.signalproc import isSameTime
from primitives.trajectory import Path, SlicedPath


class LaneData(Primitive):
  """
  Container of a three-lane road's lane information.
  """
  def __init__(self, left_line, right_line,
               left_left_line=None, right_right_line=None):
    # check time equality and call parent
    line_times = [right_line.time]
    if left_left_line is not None:
      line_times.append(left_left_line.time)
    if right_right_line is not None:
      line_times.append(right_right_line.time)
    for line_time in line_times:
      assert isSameTime(left_line.time, line_time), "ambiguous line time"
    Primitive.__init__(self, left_line.time)
    # store lines
    self.left_line = left_line
    self.right_line = right_line
    self.left_left_line = left_left_line
    self.right_right_line = right_right_line
    return
  
  def get_ego_lane(self):
    return Lane(self.left_line, self.right_line)
  
  def get_left_lane(self):
    return Lane(self.left_left_line, self.left_line)
  
  def get_right_lane(self):
    return Lane(self.right_line, self.right_right_line)

class Lane(Primitive):
  """
  Container of a lane with two bounding lines.
  """
  def __init__(self, left_line, right_line):
    assert isSameTime(left_line.time, right_line.time), "ambiguous lane time"
    Primitive.__init__(self, left_line.time)
    self.left_line = left_line
    self.right_line = right_line
    return
  
  def get_width(self):
    return self.left_line.offset - self.right_line.offset
  width = property(get_width)

class LineProp(Primitive):
  """
  Base class for a lane boundary property container.
  Properties might include line width, line color, line style etc.
  """
  pass

class FiniteLineProp(LineProp):
  """
  Property container for lines with finite length (view range).
  """
  def __init__(self, time, view_range):
    LineProp.__init__(self, time)
    self.view_range = view_range
    return
  
  def translate(self, dx, dy):
    newobj = copy.copy(self)
    newobj.view_range = self.view_range + dx
    return newobj

class VideoLineProp(FiniteLineProp):
  """
  Common container for the video-specific line properties.
  """
  def __init__(self, time, view_range, style, width):
    FiniteLineProp.__init__(self, time, view_range)
    self.style = style
    self.width = width
    return

class LineCurve(Primitive):
  """
  Base class for a single lane boundary, represented by a line (curve).
  """
  def eval_at(self, x, i):
    """
    Get the lateral coordinates for the given longitudinal coordinates at
    the given time index.
    
    :Parameters:
      x : array_like
        Longitudinal coordinates (scalar or 1-D array_like).
      i : int
        Time index.
    :ReturnType: numpy.ndarray
    :Return:
      y : Lateral coordinates as a 1-D array.
    """
    raise NotImplementedError
  
  def eval(self, x):
    """
    Get the lateral coordinates for the given longitudinal coordinates for
    all time instances.
    
    :Parameters:
      x : array_like
        Longitudinal coordinates (scalar or 1-D array_like or 2-D array_like).
    :ReturnType: numpy.ndarray
    :Return:
      y : Lateral coordinates as a 2-D array, where the first dimension
      represents the time.
    """
    x = self._process_dist_input(x)
    y = np.empty_like(x)
    for i in xrange(self.time.size):
      y[i,:] = self.eval_at(x[i,:], i)
    return y
  
  def get_slicedpath(self, x=None):
    """
    Return the evaluated curves as a SlicedPath object.
    
    :Parameters:
      x : array_like, optional
        Longitudinal coordinates (scalar or 1-D array_like or 2-D array_like).
        Default is [0, 10, ..., 90, 100].
    :ReturnType: primitives.trajectory.SlicedPath
    :Return:
      sl_path : The evaluated curves as a SlicedPath object.
    """
    if x is None:
      x = np.tile(np.arange(0.0, 100.1, 10.0), (self.time.size, 1))
    else:
      x = self._process_dist_input(x)
    y = self.eval(x)
    paths = []
    for i in xrange(self.time.size):
      path_time = np.zeros_like(x[i,:]) + self.time[i]
      path_time[1:] = np.NaN  # only the actual position's time is known
      path = Path(path_time, x[i,:], y[i,:])
      paths.append(path)
    sl_path = SlicedPath(self.time, paths)
    return sl_path
  
  def _process_dist_input(self, x):
    """
    Validate and convert the input, containing distance information.
    
    :Parameters:
      x : array_like
        Coordinates (scalar or 1-D array_like or 2-D array_like).
    :ReturnType: numpy.ndarray
    :Return:
      x : Same coordinates as a 2-D array, where the first dimension
      represents the time.
    """
    assert np.ndim(x) <= 2
    if np.ndim(x) < 1:
      x = np.array((x,))
    if np.ndim(x) < 2:
      x = np.tile(x, (self.time.size, 1))
    if not isinstance(x, np.ndarray):
      x = np.array(x)
    assert x.shape[0] == self.time.size, "x.shape[0] must equal time.size"
    return x
  
  def get_offset(self):
    """
    Get the lateral offset of the curve.
    """
    raise NotImplementedError
  offset = property(get_offset)

class PolyClothoid(LineCurve):
  """
  Third-order polynomial approximation of a clothoid curve.
  """
  def __init__(self, time, c0, c1, c2, c3):
    """
    :Parameters:
      time : numpy.ndarray
        Time stamps of the values
      c0 : numpy.ndarray
        Zero-order coefficients (offsets)
      c1 : numpy.ndarray
        First-order coefficients
      c2 : numpy.ndarray
        Second-order coefficients
      c3 : numpy.ndarray
        Third-order coefficients
    """
    LineCurve.__init__(self, time)
    self.c0 = c0
    self.c1 = c1
    self.c2 = c2
    self.c3 = c3
    return
  
  @classmethod
  def from_physical_coeffs(cls, time, a0, a1, a2, a3, *args, **kwargs):
    """
    :Parameters:
      time : numpy.ndarray
        Time stamps of the values
      a0 : numpy.ndarray
        Offsets
      a1 : numpy.ndarray
        Heading angles
      a2 : numpy.ndarray
        Curvatures
      a3 : numpy.ndarray
        Curvature rates
    """
    c0 = cls.a0_to_c0(a0)
    c1 = cls.a1_to_c1(a1)
    c2 = cls.a2_to_c2(a2)
    c3 = cls.a3_to_c3(a3)
    return cls(time, c0, c1, c2, c3, *args, **kwargs)
  
  def get_offset(self):
    return self.c0
  offset = property(get_offset)
  
  @staticmethod
  def a0_to_c0(a0):
    return a0
  @staticmethod
  def a1_to_c1(a1):
    return np.tan(a1)
  @staticmethod
  def a2_to_c2(a2):
    return a2 / 2.0
  @staticmethod
  def a3_to_c3(a3):
    return a3 / 6.0
  
  @staticmethod
  def c0_to_a0(c0):
    return c0
  @staticmethod
  def c1_to_a1(c1):
    return np.arctan(c1)
  @staticmethod
  def c2_to_a2(c2):
    return c2 * 2.0
  @staticmethod
  def c3_to_a3(c3):
    return c3 * 6.0
  
  def get_a0(self):
    return self.c0_to_a0(self.c0)
  def set_a0(self, value):
    self.c0 = self.a0_to_c0(value)
  a0 = property(get_a0, set_a0)
  
  def get_a1(self):
    return self.c1_to_a1(self.c1)
  def set_a1(self, value):
    self.c1 = self.a1_to_c1(value)
  a1 = property(get_a1, set_a1)
  
  def get_a2(self):
    return self.c2_to_a2(self.c2)
  def set_a2(self, value):
    self.c2 = self.a2_to_c2(value)
  a2 = property(get_a2, set_a2)
  
  def get_a3(self):
    return self.c3_to_a3(self.c3)
  def set_a3(self, value):
    self.c3 = self.a3_to_c3(value)
  a3 = property(get_a3, set_a3)
  
  def get_coeffs(self):
    return (self.c0, self.c1, self.c2, self.c3)
  def set_coeffs(self, value):
    self.c0, self.c1, self.c2, self.c3 = value
  coeffs = property(get_coeffs, set_coeffs)
  
  def get_physical_coeffs(self):
    return (self.a0, self.a1, self.a2, self.a3)
  def set_physical_coeffs(self, value):
    self.a0, self.a1, self.a2, self.a3 = value
  physical_coeffs = property(get_physical_coeffs, set_physical_coeffs)
  
  def eval_at(self, x, i):
    with np.errstate(invalid='ignore'):  # 0*inf for {x=0, radius=0 (curv=inf)}
      y = np.where(x == 0.0, self.c0[i],
        np.polyval([self.c3[i], self.c2[i], self.c1[i], self.c0[i]], x))
    if np.isscalar(x):
      y = y.flatten()  # convert shape: () --> (1,)
    return y
  
  def translate(self, dx, dy):
    """
    Translate with dx and dy.
    
    :Parameters:
      dx : scalar or numpy.ndarray
        Longitudinal offset.
        If ndarray, the shape must equal to the shape of time array.
      dy : scalar or numpy.ndarray
        Lateral offset.
        If ndarray, the shape must equal to the shape of time array.
    :ReturnType: type(self)
    :Return: A new, translated instance.
    """
    newobj = copy.copy(self)
    newobj.c0 = dy + \
                self.c0 - self.c1 * dx + self.c2 * dx**2.0 - self.c3 * dx**3.0
    newobj.c1 = self.c1 - 2.0 * self.c2 * dx + 3.0 * self.c3 * dx**2.0
    newobj.c2 = self.c2 - 3.0 * self.c3 * dx
    newobj.c3 = self.c3
    return newobj

class Circle(PolyClothoid):
  """
  Constant-radius lane boundary representation.
  """
  def __init__(self, time, curvature, x_offset=None, y_offset=None):
    c0 = y_offset if y_offset is not None else np.zeros_like(time)
    c1 = -2.0*x_offset if x_offset is not None else np.zeros_like(time)
    c2 = self.a2_to_c2(curvature)
    c3 = np.zeros_like(time)
    PolyClothoid.__init__(self, time, c0, c1, c2, c3)
    return
  
  @classmethod
  def from_radius(cls, time, radius, offset=None, *args, **kwargs):
    with np.errstate(divide='ignore'):
      c = 1.0 / radius
    return cls(time, c, offset, *args, **kwargs)
  
  get_curvature = PolyClothoid.get_a2
  set_curvature = PolyClothoid.set_a2
  curvature = property(get_curvature, set_curvature)
  
  def get_radius(self):
    with np.errstate(divide='ignore'):
      r = 1.0 / self.curvature
    return r
  def set_radius(self, value):
    with np.errstate(divide='ignore'):
      c = 1.0 / value
    self.curvature = c
  radius = property(get_radius, set_radius)
  
  def get_x_offset(self):
    return -self.c1/2.0
  def set_x_offset(self, value):
    self.c1 = -2.0 * value
  x_offset = property(get_x_offset, set_x_offset)
  
  def get_y_offset(self):
    return self.c0
  def set_y_offset(self, value):
    self.c0 = value
  y_offset = property(get_y_offset, set_y_offset)
  
  offset = property(get_y_offset)
  
