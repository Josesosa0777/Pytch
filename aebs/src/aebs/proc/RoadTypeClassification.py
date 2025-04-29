from __future__ import with_statement

import numpy

def calcRoadTypes(vx_ego, yr_ego, totDist, time, classificationPeriod=20.0):
  """
  Classify road type based on the host velocity and yaw rate of intervals
  with the given duration.
  
  :Parameters:
    vx_ego : numpy.ndarray
      Ego vehicle speed. [m/s]
    yr_ego : numpy.ndarray
      Ego vehicle yaw rate. [1/s]
    totDist : numpy.ndarray
      Total distance travelled.  [km]
    time : numpy.ndarray
      Time vector. [s]
    classificationPeriod : float
      Duration of a classification interval. [s]
  
  :ReturnType: tuple
  :Return:
    Tuple with the following contents:
      road curvature  : numpy.ndarray
      city mask       : numpy.ndarray
      rural road mask : numpy.ndarray
      highway mask    : numpy.ndarray
      travelled distance in city       : float
      travelled distance on rural road : float
      travelled distance on highway    : float
  """
  city      = numpy.zeros_like(time, dtype=bool)
  ruralRoad = numpy.zeros_like(time, dtype=bool)
  highway   = numpy.zeros_like(time, dtype=bool)
  with numpy.errstate(divide='ignore', invalid='ignore'):
    curvature = numpy.where(vx_ego > 1.0, yr_ego / vx_ego * 1000.0, 0.0) #[1/km]
  curvature = numpy.absolute(curvature)
  i1 = 0
  cityKm = 0.0 
  ruralRoadKm = 0.0 
  highwayKm = 0.0
  while i1 < vx_ego.size:
    i2 = time.searchsorted(time[i1] + classificationPeriod)
    i2b = min(i2, vx_ego.size-1)
    typicalSpeedinKph = numpy.mean(vx_ego[i1:i2]) * 3.6 
    maxCurvature = numpy.max(curvature[i1:i2])
    minSpeedinKph = numpy.min(vx_ego[i1:i2]) * 3.6
    if (minSpeedinKph > 65.0) and maxCurvature < 10.0:
      highway[i1:i2] = True
      highwayKm += totDist[i2b] - totDist[i1]
    elif typicalSpeedinKph > 50.0:
      ruralRoad[i1:i2] = True
      ruralRoadKm += totDist[i2b] - totDist[i1]
    else:
      city[i1:i2] = True
      cityKm += totDist[i2b] - totDist[i1]
    i1 = i2
  return curvature, city, ruralRoad, highway, cityKm, ruralRoadKm, highwayKm

def calcRoadTypes2(vx_ego, yr_ego, time, classificationPeriod=20.0):
  """
  Classify road type based on the host velocity and yaw rate of intervals
  with the given duration, into the following clusters:
    * ego vehicle stopped (no relevant road type detection)
    * city
    * rural road
    * highway
  
  :Parameters:
    vx_ego : numpy.ndarray
      Ego vehicle speed. [m/s]
    yr_ego : numpy.ndarray
      Ego vehicle yaw rate. [1/s]
    time : numpy.ndarray
      Time vector. [s]
    classificationPeriod : float
      Duration of a classification interval. [s]
  
  :ReturnType: tuple
  :Return:
    Tuple with the following contents:
      stopped mask    : numpy.ndarray
      city mask       : numpy.ndarray
      rural road mask : numpy.ndarray
      highway mask    : numpy.ndarray
  """
  # TODO: check if np.ma works well
  stopped   = numpy.zeros_like(time, dtype=bool)
  city      = numpy.zeros_like(time, dtype=bool)
  ruralRoad = numpy.zeros_like(time, dtype=bool)
  highway   = numpy.zeros_like(time, dtype=bool)
  with numpy.errstate(divide='ignore', invalid='ignore'):
    curvature = numpy.where(vx_ego > 1.0, yr_ego / vx_ego * 1000.0, 0.0) #[1/km]
  curvature = numpy.absolute(curvature)
  i1 = 0
  while i1 < vx_ego.size:
    i2 = time.searchsorted(time[i1] + classificationPeriod)
    typicalSpeedInKph = numpy.mean(vx_ego[i1:i2]) * 3.6 
    maxCurvature = numpy.max(curvature[i1:i2])
    minSpeedInKph = numpy.min(vx_ego[i1:i2]) * 3.6
    if (minSpeedInKph > 65.0) and maxCurvature < 10.0:
      highway[i1:i2] = True
    elif typicalSpeedInKph > 50.0:
      ruralRoad[i1:i2] = True
    elif typicalSpeedInKph > 1.0:
      city[i1:i2] = True
    else:
      stopped[i1:i2] = True
    i1 = i2
  return stopped, city, ruralRoad, highway
