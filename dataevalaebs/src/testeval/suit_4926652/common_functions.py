import numpy as np
from measproc.IntervalList import maskToIntervals

def findDetectionIntervals(condition):
	detectionIntervals = maskToIntervals(condition)
	return detectionIntervals

def isAnyDetection(condition):
		detections = np.where(condition)
		isDetectionAvailable = np.any(detections)
		return isDetectionAvailable
#