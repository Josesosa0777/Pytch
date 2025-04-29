""" Takes in all measurement files from the measurement directory provided as a 
command line parameter and analyzes CVR3 and AC100 sensor signals for which
sensor detects objects earlier. It is based on the association list. The results
are output in text files: the raw results and their statistics. Histograms are 
also drawn and saved in png format. The first command line parameter should be the
location of the measurement files and the second parameter should be the location
where the results, statistics and histograms are to be saved.
"""

from aebs.sdf.asso_cvr3_ac100 import AssoCvr3Ac100
import measparser
import measproc
import math
import fnmatch
import os
import sys
import numpy
import matplotlib.pyplot

# Thresholds for interval merging
# AC100 object discrimination: 2.5 [m] and angular accuracy: 0.5[deg] (tan(0.5[deg]) = 0.00873)
DX_CHK_THRESHOLD = 2.5
AZIMUTH_CHK_THRESHOLD = 0.00873
TIME_DIFF_THRESHOLD = 0.3

# Thresholds for filtering results (max. azimuth values were determined from track navigator)
DX_RANGEMAX = 100.0
TIMEDIFF_MAX = 1.0
CVR3_AZIMUTHMAX = 0.61080427292467898
AC100_AZIMUTHMAX = 0.2443527830646362
RELIABILITYLIMIT = 0.4

# request intermediate result evaluation
MAKEINTERIMRES = True

try:
  measdir = sys.argv[1]
  evaldir = sys.argv[2]
except IndexError:
  print 'Please provide a measurement and evaluation results directory as command line parameter.'
  print 'First parameter should be the measurement directory and the second should be the evaluation directory'
  exit()

measPaths = []
for root, dirs, filenames in os.walk(measdir):
  for filename in filenames:
    if fnmatch.fnmatch(filename, '*.mdf'):
      measPaths.append(os.path.join(root, filename))
      
if len(measPaths) == 0:
  print 'No valid measurement files have been found in the given directory.'
  print 'Please provide measurement files in mdf format'
  exit()

CVR3OverallData = {'delta_t':[], 'dx':[], 'delta_s':[], 'azimuth':[]}
AC100OverallData = {'delta_t':[], 'dx':[], 'delta_s':[], 'azimuth':[]}

for measPath in measPaths:
  source = measparser.cSignalSource(measPath)
  try:
    assoObj = AssoCvr3Ac100(source, reliabilityLimit=RELIABILITYLIMIT)
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
    
    # determine the intervals of object detection (and existence) in the case of CVR3
    for CVR3ID in xrange(40):
      Time = assoObj.scaleTime
      try:
        CVR3Reliability = assoObj.reliability['CVR3'][CVR3ID]
      except KeyError:
        pass
      CVR3ReliabilityN0 = measproc.EventFinder.cEventFinder.compare(Time, CVR3Reliability, measproc.not_equal, 0)
      CVR3Intervals.append(CVR3ReliabilityN0)
      
    # determine the intervals of object detection (and existence) in the case of AC100
    for AC100ID in xrange(20):
      Time = assoObj.scaleTime
      try:
        AC100Reliability = assoObj.reliability['AC100'][AC100ID]
        AC100dxs = assoObj.posTracks['AC100'][AC100ID][0][:, 0]
        AC100dys = assoObj.posTracks['AC100'][AC100ID][0][:, 1]
      except KeyError:
        pass   
      AC100ReliabilityN0 = measproc.EventFinder.cEventFinder.compare(Time, AC100Reliability, measproc.not_equal, 0)
      
      # merge intervals that are close enough to each other
      AC100NewIntervals = measproc.cIntervalList(Time)
      counter = 0
      for index in xrange(len(AC100ReliabilityN0)):
        AC100NewIntervals.add(AC100ReliabilityN0[index][0], AC100ReliabilityN0[index][1])
        if index != 0:
          dx_check = math.fabs(AC100dxs[AC100ReliabilityN0[index][0]] - AC100dxs[AC100NewIntervals[counter][1] - 1])
          azimuth_check = math.fabs(math.fabs(AC100dys[AC100ReliabilityN0[index][0]] / AC100dxs[AC100ReliabilityN0[index][0]]) - math.fabs(AC100dys[AC100NewIntervals[counter][1] - 1] / AC100dxs[AC100NewIntervals[counter][1] - 1]))
          time_diff = Time[AC100ReliabilityN0[index][0]] - Time[AC100NewIntervals[counter][1] - 1]
          if dx_check < DX_CHK_THRESHOLD and azimuth_check < AZIMUTH_CHK_THRESHOLD and time_diff < TIME_DIFF_THRESHOLD:
            AC100NewIntervals.add(AC100NewIntervals[counter][0], AC100ReliabilityN0[index][1])
            AC100NewIntervals.remove(AC100NewIntervals[counter][0], AC100NewIntervals[counter][1])
            AC100NewIntervals.remove(AC100ReliabilityN0[index][0], AC100ReliabilityN0[index][1])
          else:
            counter = counter + 1
      AC100Intervals.append(AC100NewIntervals)
      
    # select the relevant interval (the one in which association happened) from the object detection (and existence) intervals
    DetectTimeIndexIntervals = []
    for change in changes:
      try:
        CVR3ObjExistInterval = CVR3Intervals[change[1][CVR3radar]].findInterval(change[0])
        AC100ObjExistInterval = AC100Intervals[change[1][AC100radar]].findInterval(change[0])
      except ValueError:
        pass
      else:
        DetectTimeIndexIntervals.append((change[1], (CVR3ObjExistInterval, AC100ObjExistInterval)))
        
    DetectTimeIndexIntervals = list(set(DetectTimeIndexIntervals))  # remove duplicate values
    
    # calculate and gather physical data; evaluate which sensor was quicker; filter and store the results 
    Results = []
    CVR3Data = {'delta_t':[], 'dx':[], 'delta_s':[], 'azimuth':[]}
    AC100Data = {'delta_t':[], 'dx':[], 'delta_s':[], 'azimuth':[]}
    for interval in DetectTimeIndexIntervals:
      ti0_AC100 = interval[1][AC100radar][0]
      ti0_CVR3 = interval[1][CVR3radar][0]
      id_AC100 = interval[0][AC100radar]
      id_CVR3 = interval[0][CVR3radar]
      
      delta_t = assoObj.scaleTime[ti0_AC100] - assoObj.scaleTime[ti0_CVR3]
      dx_CVR3 = assoObj.posTracks['CVR3'][id_CVR3][0][ti0_CVR3, 0]
      dx_AC100 = assoObj.posTracks['AC100'][id_AC100][0][ti0_AC100, 0]
      dy_CVR3 = assoObj.posTracks['CVR3'][id_CVR3][0][ti0_CVR3, 1]
      dy_AC100 = assoObj.posTracks['AC100'][id_AC100][0][ti0_AC100, 1]
      azimuth_CVR3 = math.atan(dy_CVR3 / dx_CVR3)
      azimuth_AC100 = math.atan(dy_AC100 / dx_AC100)
      
      if delta_t < 0:
        selected = 'AC100'
        objectID = id_AC100
        time = assoObj.scaleTime[ti0_AC100]
        dx = dx_AC100
        dy = dy_AC100
        delta_s = math.sqrt(dx ** 2 + dy ** 2)
        azimuth = azimuth_AC100
      elif delta_t >= 0:
        selected = 'CVR3'
        objectID = id_CVR3
        time = assoObj.scaleTime[ti0_CVR3]
        dx = dx_CVR3
        dy = dy_CVR3
        delta_s = math.sqrt(dx ** 2 + dy ** 2)
        azimuth = azimuth_CVR3
        
      if math.fabs(delta_t) < TIMEDIFF_MAX and math.fabs(delta_t) > 0.1:
        if (math.fabs(dx_CVR3) < DX_RANGEMAX and math.fabs(dx_AC100) < DX_RANGEMAX) and (math.fabs(azimuth_AC100) < AC100_AZIMUTHMAX or math.fabs(azimuth_CVR3) < CVR3_AZIMUTHMAX):
          Results.append({'selected':selected, 'objectID':objectID, 'time': time, 'delta_t':delta_t, 'dx':dx, 'dy':dy, 'delta_s':delta_s, 'azimuth':azimuth})
          # store additional info needed for statistics and histograms
          if selected == 'AC100':
            AC100Data['delta_t'].append(delta_t)
            AC100Data['dx'].append(dx)
            AC100Data['delta_s'].append(delta_s)
            AC100Data['azimuth'].append(azimuth)
            AC100OverallData['delta_t'].append(delta_t)
            AC100OverallData['dx'].append(dx)
            AC100OverallData['delta_s'].append(delta_s)
            AC100OverallData['azimuth'].append(azimuth)
          elif selected == 'CVR3':
            CVR3Data['delta_t'].append(delta_t)       
            CVR3Data['dx'].append(dx)                 
            CVR3Data['delta_s'].append(delta_s)       
            CVR3Data['azimuth'].append(azimuth)       
            CVR3OverallData['delta_t'].append(delta_t)
            CVR3OverallData['dx'].append(dx)          
            CVR3OverallData['delta_s'].append(delta_s)
            CVR3OverallData['azimuth'].append(azimuth)
          
    directory, filename = os.path.split(measPath)
    
    # save the results to separate files
    resulttxtfilename = filename + '-Results.txt'
    try:
      resulttxtoutput = open(evaldir + '\\' + resulttxtfilename, 'w')
      try:
        resulttxtoutput.writelines('No.\tSelected radar\tObject ID\tTime [s]\tdx coordinate [m]\tdy coordinate [m]\tDetection distance (delta_s) [m]\tAzimuth angle [deg]\tTime advantage (delta_t) [s]\n')
        for index, result in enumerate(Results):
          resulttxtoutput.writelines('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (index + 1, result['selected'], result['objectID'], result['time'], result['dx'], result['dy'], result['delta_s'], result['azimuth'] * 180 / math.pi, result['delta_t']))
      finally:
        resulttxtoutput.close()
    except IOError:
      pass
    
    # make intermediate result evaluation if requested
    if MAKEINTERIMRES:
      # make the statistics and plot the histograms
      
      if len(CVR3Data['delta_t']) != 0 and len(AC100Data['delta_t']) != 0:
        CVR3_dt_average = numpy.mean(CVR3Data['delta_t'])
        AC100_dt_average = numpy.mean(AC100Data['delta_t'])
        CVR3_dx_average = numpy.mean(CVR3Data['dx'])
        AC100_dx_average = numpy.mean(AC100Data['dx'])
        CVR3_ds_average = numpy.mean(CVR3Data['delta_s'])
        AC100_ds_average = numpy.mean(AC100Data['delta_s'])
        CVR3azimuth = numpy.array(CVR3Data['azimuth'])
        AC100azimuth = numpy.array(AC100Data['azimuth'])
        CVR3_azimuth_average_L = numpy.ma.average(CVR3azimuth, weights=CVR3azimuth < 0)
        CVR3_azimuth_average_R = numpy.ma.average(CVR3azimuth, weights=CVR3azimuth > 0)
        AC100_azimuth_average_L = numpy.ma.average(AC100azimuth, weights=AC100azimuth < 0)
        AC100_azimuth_average_R = numpy.ma.average(AC100azimuth, weights=AC100azimuth > 0)
        AC100Delta_t = numpy.abs(AC100Data['delta_t'])
        CVR3Delta_t = CVR3Data['delta_t']
        CVR3_detect_percentage = (len(CVR3Data['delta_t']) / float(len(CVR3Data['delta_t']) + len(AC100Data['delta_t']))) * 100
        AC100_detect_percentage = (len(AC100Data['delta_t']) / float(len(CVR3Data['delta_t']) + len(AC100Data['delta_t']))) * 100
      elif len(CVR3Data['delta_t']) == 0:
        CVR3_dt_average = numpy.NAN
        AC100_dt_average = numpy.mean(AC100Data['delta_t'])
        CVR3_dx_average = numpy.NAN
        AC100_dx_average = numpy.mean(AC100Data['dx'])
        CVR3_ds_average = numpy.NAN
        AC100_ds_average = numpy.mean(AC100Data['delta_s'])
        AC100azimuth = numpy.array(AC100Data['azimuth'])
        CVR3_azimuth_average_L = numpy.NAN
        CVR3_azimuth_average_R = numpy.NAN
        AC100_azimuth_average_L = numpy.ma.average(AC100azimuth, weights=AC100azimuth < 0)
        AC100_azimuth_average_R = numpy.ma.average(AC100azimuth, weights=AC100azimuth > 0)
        AC100Delta_t = numpy.abs(AC100Data['delta_t'])
        AC100_detect_percentage = (len(AC100Data['delta_t']) / float(len(CVR3Data['delta_t']) + len(AC100Data['delta_t']))) * 100
        CVR3_detect_percentage = 0
        CVR3Delta_t = [0]
      elif len(AC100Data['delta_t']) == 0:
        CVR3_dt_average = numpy.mean(CVR3Data['delta_t'])
        AC100_dt_average = numpy.NAN
        CVR3_dx_average = numpy.mean(CVR3Data['dx'])
        AC100_dx_average = numpy.NAN
        CVR3_ds_average = numpy.mean(CVR3Data['delta_s'])
        AC100_ds_average = numpy.NAN
        CVR3azimuth = numpy.array(CVR3Data['azimuth'])
        CVR3_azimuth_average_L = numpy.ma.average(CVR3azimuth, weights=CVR3azimuth < 0)
        CVR3_azimuth_average_R = numpy.ma.average(CVR3azimuth, weights=CVR3azimuth > 0)
        AC100_azimuth_average_L = numpy.NAN
        AC100_azimuth_average_R = numpy.NAN
        CVR3Delta_t = CVR3Data['delta_t']
        CVR3_detect_percentage = (len(CVR3Data['delta_t']) / float(len(CVR3Data['delta_t']) + len(AC100Data['delta_t']))) * 100
        AC100_detect_percentage = 0
        AC100Delta_t = [0]
        
      # create plot
      fig1 = matplotlib.pyplot.figure()
      fig1.canvas.set_window_title(filename)
      fig1.suptitle('Histogram of delta_t values (%s)' % filename)
      subplt = fig1.add_subplot(1, 1, 1)
      subplt.set_xlabel('Detection time advantage (delta_t) [s]')
      subplt.set_ylabel('No. of occurrence [-]')
      (hist, bin_edges, patches) = subplt.hist([AC100Delta_t, CVR3Delta_t], bins=10, histtype='bar', align='mid', color=['green', 'blue'], label=['AC100', 'CVR3'])
      subplt.legend()
      # save plot
      matplotlib.pyplot.savefig(evaldir + '\\' + filename + '-DetectTimeHistogram.png')
      # save statistics to separate files
      statisticsfilename = filename + '-Statistics.txt'
      try:
        statstxtoutput = open(evaldir + '\\' + statisticsfilename, 'w')
        try:
          statstxtoutput.writelines('Percentage of earlier CVR3 detection [%%]:\t%s\nPercentage of earlier AC100 detection [%%]:\t%s\n\n' % (CVR3_detect_percentage, AC100_detect_percentage))
          statstxtoutput.writelines('Average time advantage (delta_t) of CVR3 [s]:\t%s\nAverage time advantage (delta_t) of AC100 [s]:\t%s\n' % (CVR3_dt_average, numpy.abs(AC100_dt_average)))
          statstxtoutput.writelines('Average dx coordinate (CVR3) [m]:\t%s\nAverage dx coordinate (AC100) [m]:\t%s\n' % (CVR3_dx_average, AC100_dx_average))
          statstxtoutput.writelines('Average detection distance (delta_s) (CVR3) [m]:\t%s\nAverage detection distance (delta_s) (AC100) [m]:\t%s\n' % (CVR3_ds_average, AC100_ds_average))
          statstxtoutput.writelines('Average azimuth angle (CVR3) [deg]:\t%s\t%s\nAverage azimuth angle (AC100) [deg]:\t%s\t%s' % (CVR3_azimuth_average_L * 180 / math.pi, CVR3_azimuth_average_R * 180 / math.pi, AC100_azimuth_average_L * 180 / math.pi, CVR3_azimuth_average_R * 180 / math.pi))
        finally:
          statstxtoutput.close()
      except IOError:
        pass
      
# make a histogram and statistics with all evaluation data (overall evaluation results)
# create plot
fig2 = matplotlib.pyplot.figure()
fig2.canvas.set_window_title(filename)
fig2.suptitle('Histogram of delta_t values (Overall)')
subplt = fig2.add_subplot(1, 1, 1)
subplt.set_xlabel('Detection time advantage (delta_t) [s]')
subplt.set_ylabel('No. of occurrence [-]')
(hist, bin_edges, patches) = subplt.hist([numpy.abs(AC100OverallData['delta_t']), CVR3OverallData['delta_t']], bins=10, histtype='bar', align='mid', color=['green', 'blue'], label=['AC100', 'CVR3'])
subplt.legend()
# save plot
matplotlib.pyplot.savefig(evaldir + '\\' + 'Overall-DetectTimeHistogram.png')

# make statistics
CVR3_dt_average = numpy.mean(CVR3OverallData['delta_t'])
AC100_dt_average = numpy.mean(AC100OverallData['delta_t'])
CVR3_dx_average = numpy.mean(CVR3OverallData['dx'])
AC100_dx_average = numpy.mean(AC100OverallData['dx'])
CVR3_ds_average = numpy.mean(CVR3OverallData['delta_s'])
AC100_ds_average = numpy.mean(AC100OverallData['delta_s'])
CVR3azimuth = numpy.array(CVR3OverallData['azimuth'])  
AC100azimuth = numpy.array(AC100OverallData['azimuth'])
CVR3_azimuth_average_L = numpy.average(CVR3azimuth, weights=CVR3azimuth < 0)   
CVR3_azimuth_average_R = numpy.average(CVR3azimuth, weights=CVR3azimuth > 0)   
AC100_azimuth_average_L = numpy.average(AC100azimuth, weights=AC100azimuth < 0)
AC100_azimuth_average_R = numpy.average(AC100azimuth, weights=AC100azimuth > 0)
if len(CVR3OverallData['delta_t']) != 0 and len(AC100OverallData['delta_t']) != 0:
  CVR3_detect_percentage = (len(CVR3OverallData['delta_t']) / float(len(CVR3OverallData['delta_t']) + len(AC100OverallData['delta_t']))) * 100
  AC100_detect_percentage = (len(AC100OverallData['delta_t']) / float(len(CVR3OverallData['delta_t']) + len(AC100OverallData['delta_t']))) * 100
else:
  CVR3_detect_percentage = 0
  AC100_detect_percentage = 0

# save statistics to file
try:
  oastatstxtoutput = open(evaldir + '\\' + 'Overall-Statistics.txt', 'w')
  try:
    oastatstxtoutput.writelines('Percentage of earlier CVR3 detection [%%]:\t%s\nPercentage of earlier AC100 detection [%%]:\t%s\n\n' % (CVR3_detect_percentage, AC100_detect_percentage))                                                                                              
    oastatstxtoutput.writelines('Average time advantage (delta_t) of CVR3 [s]:\t%s\nAverage time advantage (delta_t) of AC100 [s]:\t%s\n' % (CVR3_dt_average, numpy.abs(AC100_dt_average)))                                                                                                     
    oastatstxtoutput.writelines('Average dx coordinate (CVR3) [m]:\t%s\nAverage dx coordinate (AC100) [m]:\t%s\n' % (CVR3_dx_average, AC100_dx_average))                                                                                                                                        
    oastatstxtoutput.writelines('Average detection distance (delta_s) (CVR3) [m]:\t%s\nAverage detection distance (delta_s) (AC100) [m]:\t%s\n' % (CVR3_ds_average, AC100_ds_average))                                                                                                          
    oastatstxtoutput.writelines('Average azimuth angle (CVR3) [deg]:\t%s\t%s\nAverage azimuth angle (AC100) [deg]:\t%s\t%s' % (CVR3_azimuth_average_L * 180 / math.pi, CVR3_azimuth_average_R * 180 / math.pi, AC100_azimuth_average_L * 180 / math.pi, CVR3_azimuth_average_R * 180 / math.pi))
  finally:
    oastatstxtoutput.close()
except IOError:
  pass
    
    
