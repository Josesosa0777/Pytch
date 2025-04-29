from aebs.sdf.asso_cvr3_ac100 import AssoCvr3Ac100

import interface
import measparser
import measproc
import numpy
import math

# module parameter class creation
class cParameter(interface.iParameter):
  def __init__(self, dx_chk_threshold, azimuth_chk_threshold, time_diff_threshold, dx_rangemax, time_rangemax, cvr3_azimuthmax, ac100_azimuthmax):
    self.dx_chk_threshold = dx_chk_threshold
    """:type: float
    Check threshold for dx to be used in AC100 object detection interval merging.
    """
    self.azimuth_chk_threshold = azimuth_chk_threshold
    """:type: float
    Check threshold for azimuth to be used in AC100 object detection interval merging.
    It should be viewed as an azimuth angle difference between two objects.
    """
    self.time_diff_threshold = time_diff_threshold
    """:type: float
    Check threshold for time difference to be used in AC100 object detection interval merging.
    """
    self.dx_rangemax = dx_rangemax
    """:type: float
    Max. absolute value for result filtering based on dx.
    """
    self.time_rangemax = time_rangemax
    """:type: float
    Max. absolute value for result filtering based on time.
    """
    self.cvr3_azimuthmax = cvr3_azimuthmax
    """:type: float
    Max. azimuth angle of the FOV of CVR3.
    """
    self.ac100_azimuthmax = ac100_azimuthmax
    """:type: float
    Max. azimuth angle of the FOV of AC100.
    """
    self.genKeys()
    
# instantiation of module parameters
searchObjDetectIntervals = cParameter(2.5, 0.00873, 0.3, 100, 1.0, 0.61080427292467898, 0.2443527830646362)

class cSearchCVR3EnduranceTestResult(interface.iSearch):
  def search(self, Param):
    TitlePattern = '%s - CVR3 and AC100 object detection intervals %s'
    
    Source = self.get_source('main')
    try:
      assoObj = AssoCvr3Ac100(Source, reliabilityLimit=0.4)
    except ValueError, error:
      print error.message
    else:
      assoObj.calc()
    
      # acquire the elements of the association list where at least one change of some sort has happened
      changes = []
      for index, aobjs in enumerate(assoObj.objectPairs):
        if index != 0:
          if aobjs != assoObj.objectPairs[index - 1]:
            for aobj in aobjs:
              changes.append([index, aobj])
            
      CVR3radar = 0  # the first member of association pair located in the association list is for CVR3
      AC100radar = 1 # the second member of association pair located in the association list is for AC100
      
      CVR3Intervals = []
      AC100Intervals = []
      
      for CVR3ID in xrange(40):
        Time = assoObj.scaleTime
        try:
          CVR3Reliability = assoObj.reliability['CVR3'][CVR3ID]
        except KeyError:
          pass
        CVR3ReliabilityN0 = Source.compare(Time, CVR3Reliability, measproc.not_equal, 0)
        CVR3Intervals.append(CVR3ReliabilityN0)
      
      for AC100ID in xrange(20):
        Time = assoObj.scaleTime
        try:
          AC100Reliability = assoObj.reliability['AC100'][AC100ID]
          AC100dxs = assoObj.posTracks['AC100'][AC100ID][0][:, 0]
          AC100dys = assoObj.posTracks['AC100'][AC100ID][0][:, 1]
        except KeyError:
          pass   
        AC100ReliabilityN0 = Source.compare(Time, AC100Reliability, measproc.not_equal, 0)
        AC100NewIntervals = measproc.cIntervalList(Time)
        counter = 0
        for index in xrange(len(AC100ReliabilityN0)):
          AC100NewIntervals.add(AC100ReliabilityN0[index][0], AC100ReliabilityN0[index][1])
          if index != 0:
            dx_check = math.fabs(AC100dxs[AC100ReliabilityN0[index][0]] - AC100dxs[AC100NewIntervals[counter][1] - 1])
            azimuth_check = math.fabs(math.fabs(AC100dys[AC100ReliabilityN0[index][0]] / AC100dxs[AC100ReliabilityN0[index][0]]) - math.fabs(AC100dys[AC100NewIntervals[counter][1] - 1] / AC100dxs[AC100NewIntervals[counter][1] - 1]))
            time_diff = Time[AC100ReliabilityN0[index][0]] - Time[AC100NewIntervals[counter][1] - 1]
            if dx_check < Param.dx_chk_threshold and azimuth_check < Param.azimuth_chk_threshold and time_diff < Param.time_diff_threshold:
              AC100NewIntervals.add(AC100NewIntervals[counter][0], AC100ReliabilityN0[index][1])
              AC100NewIntervals.remove(AC100NewIntervals[counter][0], AC100NewIntervals[counter][1])
              AC100NewIntervals.remove(AC100ReliabilityN0[index][0], AC100ReliabilityN0[index][1])
            else:
              counter = counter + 1
        AC100Intervals.append(AC100NewIntervals)
      
      DetectTimeIndexIntervals = []
      for change in changes:
        try:
          CVR3ObjExistInterval = CVR3Intervals[change[1][CVR3radar]].findInterval(change[0])
          AC100ObjExistInterval = AC100Intervals[change[1][AC100radar]].findInterval(change[0])
        except ValueError:
          pass
        else:
          DetectTimeIndexIntervals.append((change[1], (CVR3ObjExistInterval, AC100ObjExistInterval)))
        
      DetectTimeIndexIntervals = list(set(DetectTimeIndexIntervals))
    
      if len(DetectTimeIndexIntervals) != 0:
        Result = self.PASSED
        Title = TitlePattern % (Source.BackupParser.Measurement, 'found')
        FinalResultIntervals = measproc.cIntervalList(Time)
        FinalResultIDs = []
        
        for interval in DetectTimeIndexIntervals:
          ti0_AC100 = interval[1][AC100radar][0]
          ti0_CVR3 = interval[1][CVR3radar][0]
          ti1_AC100 = interval[1][AC100radar][1]
          ti1_CVR3 = interval[1][CVR3radar][1]
          id_AC100 = interval[0][AC100radar]
          id_CVR3 = interval[0][CVR3radar]
          
          delta_t = assoObj.scaleTime[ti0_AC100] - assoObj.scaleTime[ti0_CVR3]
          dx_CVR3 = assoObj.posTracks['CVR3'][id_CVR3][0][ti0_CVR3, 0]
          dx_AC100 = assoObj.posTracks['AC100'][id_AC100][0][ti0_AC100, 0]
          azimuth_CVR3 = math.atan(assoObj.posTracks['CVR3'][id_CVR3][0][ti0_CVR3, 1] / dx_CVR3)
          azimuth_AC100 = math.atan(assoObj.posTracks['AC100'][id_AC100][0][ti0_AC100, 1] / dx_AC100)
          
          if math.fabs(delta_t) < Param.time_rangemax and math.fabs(delta_t) > 0.1:
            if (dx_CVR3 < Param.dx_rangemax and dx_AC100 < Param.dx_rangemax) and (azimuth_CVR3 < Param.cvr3_azimuthmax or azimuth_AC100 < Param.ac100_azimuthmax):
              FinalResultIntervals.add(ti0_AC100, ti1_AC100)
              FinalResultIDs.append(('AC100', id_AC100))
              FinalResultIntervals.add(ti0_CVR3, ti1_CVR3)
              FinalResultIDs.append(('CVR3', id_CVR3))

        Report = measproc.cIntervalListReport(FinalResultIntervals, Title)
        
        for index in xrange(len(FinalResultIntervals)):
          Report.setComment(FinalResultIntervals[index], '%s: %s' % (FinalResultIDs[index][0], FinalResultIDs[index][1]))
      else:
        Result = self.FAILED
        Title = TitlePattern % (Source.BackupParser.Measurement, 'not found')
        Report = measproc.cEmptyReport(Title)
      
      # register report in batch
      Batch = self.get_batch()
      Batch.add_entry(Report, Result)
    
      
    
    
