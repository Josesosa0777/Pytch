def round2(x, base=1.0):
  """
  Round values to the given base.
  
  Example:
  >>> a=[10,11,12,13,14,15,16,17,18,19,20]
  >>> for b in a:
  ...     round2(x, 5.0)
  ... 
  10
  10
  10
  15
  15
  15
  15
  15
  20
  20
  20
  
  Idea taken from:
  http://stackoverflow.com/questions/2272149/round-to-5-or-other-number-in-python
  """
  return base * round(float(x)/base)

def mps2kph(v):
  """
  Convert speed in m/s to km/h.
  """
  return v * 3.6

def kph2mps(v):
  """
  Convert speed in km/h to m/s.
  """
  return v / 3.6

def mph2kph(v):
  """
  Convert speed in mph to km/h.
  """
  return v * 1.6

def kph2mph(v):
  """
  Convert speed in km/h to mph.
  """
  return v / 1.6

def decdeg2degminsec(angle):
  """
  Convert angle from decimal degrees to degrees minutes seconds.
  
  Idea taken from:
  http://stackoverflow.com/questions/2579535/how-to-convert-dd-to-dms-in-python
  """
  negative = angle < 0.0
  angle = abs(angle)
  minutes, seconds = divmod(angle*3600.0, 60)
  degrees, minutes = divmod(minutes, 60)
  if negative:
    if degrees > 0.0:
      degrees = -degrees
    elif minutes > 0.0:
      minutes = -minutes
    else:
      seconds = -seconds
  return (degrees, minutes, seconds)

def degminsec2decdeg(degrees, minutes, seconds):
  """
  Convert angle from degrees minutes seconds to decimal degrees.
  """
  return degrees + minutes * 100.0/60.0 + seconds * 100.0/60.0
