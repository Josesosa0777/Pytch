import numpy as np

def selectScaleTime(ScaleTimes, maxDensity=True):
  """ Selects the most/least dense scale time.
  """
  Times = {}
  for Time in ScaleTimes:
    dTime = np.diff(Time)
    aTime = dTime.mean()
    Times[aTime] = Time
  aTimes = Times.keys()
  aTimes.sort() # increasing order
  index = 0 if maxDensity else -1
  selectedTime = aTimes[index]
  ScaleTime = Times[selectedTime]
  return ScaleTime
  