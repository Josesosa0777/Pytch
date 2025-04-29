import numpy

import interface
from measparser.signalgroup import SignalGroupList
from measparser.signalproc import selectTimeScale
from measproc.IntervalList import cIntervalList
from measproc.report2 import Report

DefParam = interface.NullParam

NAN = float('nan')

N_OHY_OBJ = 40
N_FUS_OBJ = 32
N_POS_OBJ = 6
FUS_INVALID_HANDLE = 0

cvr3SignalGroups = []
posSignalGroups = []
fusSignalGroups = []
ohySignalGroups = []
for device in 'MRR1plus', 'RadarFC':
  posSignalGroups.append([
    {'handle': (device,
                "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d" %i),}
    for i in xrange(N_POS_OBJ)])
  fusSignalGroups.append([
    {'handle': (device, "fus.ObjData_TC.FusObj.i%d.Handle" %i),
     'objidx': (device, "fus_asso_mat.LrrObjIdx.i%d"       %i),}
    for i in xrange(N_FUS_OBJ)])
  ohySignalGroups.append([
    {"dx":       (device, "ohy.ObjData_TC.OhlObj.i%d.dx"                   %i),
     "dy":       (device, "ohy.ObjData_TC.OhlObj.i%d.dy"                   %i),
     "power":    (device, "ohy.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt" %i),
     "cntAlive": (device, "ohy.ObjData_TC.OhlObj.i%d.internal.CntAlive"    %i),
     "measured": (device, "ohy.SensorInfo_TC.OhlObjInd.i%d.b.b.Measured_b" %i),
     "new":      (device,
                  "ohy.ObjData_TC.OhlObj.i%d.internal.stat.stat.NEW_occurred_b"
                  %i),}
    for i in xrange(N_OHY_OBJ)])
  cvr3SignalGroups.append({
    "absMeasTimeStamp":    (device, "dsp.LocationData_TC.tAbsMeasTimeStamp"),
    # T10 signal
    "absMeasTimeStampVid": (device, "fus.SVidBasicInput_T20.tAbsMeasTimeStamp"),
    "egoSpeed":            (device, "evi.General_T20.vxvRef"),
    "egoYawRate":          (device, "evi.General_TC.psiDtOptRaw"),
  })

canSignalGroups = [
  {
    "egoOdoMeter": ("Veh_Dist_high_Res", "tot_veh_dist"),
  },
]

QUANTITY_INFO =                 ("Unit", "Description", )
QUANTITIES = {
  "absTimeDer_max":             ("1",    "Maximum of the time derivative of tAbsMeasTimeStamp signal.", ),
  "absTimeDer_mean":            ("1",    "Mean value of the time derivative of tAbsMeasTimeStamp signal.", ),
  "absTimeDer_min":             ("1",    "Minimum of the time derivative of tAbsMeasTimeStamp signal.", ),
  "absTime_max":                ("s",    "Maximum value of the measurement timestamp.", ),
  "absTime_min":                ("s",    "Minimum value of the measurement timestamp.", ),
  "cntAlive_max":               ("-",    "Maximum lifetime (in terms of TC cycles) of OHY objects.", ),
  "cntAlive_mean":              ("-",    "Mean value of the lifetimes (in terms of TC cycles) of OHY objects.", ),
  "egoDrivenDistance":          ("km",   "Driven distance.", ),
  "egoSpeed_mean":              ("km/h", "Mean speed value.", ),
  "egoYawRate_max":             ("1/s",  "Maximum of the absolute yaw rate.", ),
  "egoYawRate_mean":            ("1/s",  "Mean value of the yaw rate.", ),
  "fov_dx_max":                 ("m",    "Maximum value of the detected distances of the objects in x direction.", ),
  "fov_dx_mean":                ("m",    "Mean value of the detected distances of the objects in x direction.", ),
  "fov_dy_max":                 ("m",    "Maximum value of the detected distances of the objects in y direction.", ),
  "fov_dy_mean":                ("m",    "Mean value of the detected distances of the objects in y direction.", ),
  "fusMeasErrors":              ("-",    "Est. number of measurement errors in FUS, based on signal inconsistencies.", ),
  "fusMissedVidUpdates":        ("-",    "Number of missed/ignored camera cycles in FUS.", ),
  "invalidTimeCount":           ("-",    "Number of time channels violating sign and monotonity requirements.", ),
  "objCreationRate_mean":       ("1/s",  "Number of new OHY objects per sec.", ),
  "posObjectCount":             ("-",    "Number of objects in the position matrix during the whole measurement.", ),
  "receivedPower_mean":         ("dB",   "Mean value of the received power.", ),
  "tcCycleCount":               ("-",    "Number of TC cycles in the measurement.", ),
  "tcCycleTime_max":            ("s",    "Maximum value of the TC cycle time.", ),
  "tcCycleTime_mean":           ("s",    "Mean value of the TC cycle time.", ),
  "tcCycleTime_std":            ("s",    "Standard deviation of the TC cycle time.", ),
}


class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    cvr3Group = source.selectSignalGroup(cvr3SignalGroups)
    canGroup  = source.selectSignalGroup(canSignalGroups)
    fusGroups = SignalGroupList.from_first_allvalid(fusSignalGroups, source)
    posGroups = SignalGroupList.from_first_allvalid(posSignalGroups, source)
    ohyGroups = SignalGroupList.from_first_allvalid(ohySignalGroups, source)
    return cvr3Group, canGroup, fusGroups, posGroups, ohyGroups
    
  def fill(self, cvr3Group, canGroup, fusGroups, posGroups,
           ohyGroups):
    source = self.get_source('main')
    
    # Time channels
    nInvalidTimeChannels = 0
    validTimes = []
    parser = source.loadParser()
    for timeKey in parser.iterTimeKeys():  # check in the measurement itself
      time = source.getTime(timeKey)  # use backup and/or memory parser if possible
      if time.size < 2: continue

      if numpy.all(time >= 0.0) and numpy.all(numpy.diff(time) > 0.0):
        validTimes.append(time)
      else:
        nInvalidTimeChannels += 1
    source.save()  # save backup, close parser
    
    tcTime, absMeasTimeStamp = cvr3Group.get_signal('absMeasTimeStamp')
    tcCycleTime = numpy.diff(tcTime)
    dtdt = numpy.diff(absMeasTimeStamp) / tcCycleTime
    nTcCycles = tcTime.size - 1
    tcTimeDuration = tcTime[-1] - tcTime[0] if tcTime.size > 1 else 0.0
    
    absMeasTimeStampVid = cvr3Group.get_value('absMeasTimeStampVid')
    allVidUpdateCycleTime = numpy.diff(absMeasTimeStampVid)
    vidUpdateCycleTime = allVidUpdateCycleTime[allVidUpdateCycleTime.nonzero()]
    
    # Ego data
    t, egoSpeed = cvr3Group.get_signal('egoSpeed')  # m/s
    egoYawRate = cvr3Group.get_value('egoYawRate', ScaleTime=t)
    egoOdoMeter = canGroup.get_value('egoOdoMeter', ScaleTime=t)  # km
    
    # OHY related quantities
    nOhyObjects = 0
    allValidPowers = []
    allValidDxs = []
    allValidDys = []
    allFinalCntAlives = []
    values = 'new', 'power', 'measured', 'dx', 'dy', 'cntAlive'
    for data in ohyGroups.get_values(values):
      nOhyObjects += numpy.count_nonzero(data['new'])

      power = data['power']
      validPower= power[power.nonzero()]
      allValidPowers.append(validPower)

      measured_nonzero = data['measured'].nonzero()
      allValidDxs.append(data['dx'][measured_nonzero])
      allValidDys.append(data['dy'][measured_nonzero])
      
      cntAlive  = data['cntAlive']
      cntAliveInt = cntAlive.astype(int)  # cast from unsigned integer
      finalCntAliveIndices = numpy.nonzero(numpy.diff(cntAliveInt) < 0)
      if cntAlive.size > 0:
        finalCntAliveIndices = numpy.append(finalCntAliveIndices, -1)
      if finalCntAliveIndices.size:
        finalCntAlive = cntAlive[finalCntAliveIndices]
      else:
        finalCntAlive =  numpy.empty(0)
      allFinalCntAlives.append(finalCntAlive)
    # normalization correction (result in dB)
    allValidPowers = numpy.concatenate(allValidPowers) / 2.0  
    allValidDxs = numpy.concatenate(allValidDxs)
    allValidDys = numpy.concatenate(allValidDys)
    allFinalCntAlives = numpy.concatenate(allFinalCntAlives)
    
    # FUS related quantities
    nFusIncons = 0  
    "number of timestamps where inconsistency detected (rough guess only)"
    for data in fusGroups.get_values(['handle', 'objidx'], ScaleTime=t):
      validHandle = data['handle'] != FUS_INVALID_HANDLE
      lrrAssociated = data['objidx'] < N_OHY_OBJ
      incons = (lrrAssociated & validHandle) != lrrAssociated
      nFusIncons += numpy.count_nonzero(incons)
    
    # Position matrix data
    nPosObjects = 0
    for handle in posGroups.get_value('handle', ScaleTime=t):
      validHandle = handle[handle.nonzero()]
      if validHandle.size > 0:
        nPosObjects += numpy.count_nonzero(numpy.diff(validHandle)) + 1
    
    # Adding values
    dic = {}
    
    value = absMeasTimeStamp.min() if absMeasTimeStamp.size > 0 else NAN
    isValid = value >= 0.0
    dic['absTime_min'] = (value, isValid)
    
    value = absMeasTimeStamp.max() if absMeasTimeStamp.size > 0 else NAN
    isValid = value > dic['absTime_min'][0]
    dic['absTime_max'] = (value, isValid)
    
    value = dtdt.min() if dtdt.size > 0 else NAN
    isValid = value > 0.5
    dic['absTimeDer_min'] = (value, isValid)
    
    value = dtdt.max() if dtdt.size > 0 else NAN
    isValid = value < 2.0
    dic['absTimeDer_max'] = (value, isValid)
    
    if tcTimeDuration > 0.0:
      value = (absMeasTimeStamp[-1] - absMeasTimeStamp[0])/tcTimeDuration
    else:
      value = NAN
    isValid = 0.85 < value < 1.15
    dic['absTimeDer_mean'] = (value, isValid)
    
    value = tcCycleTime.max() if nTcCycles > 0 else NAN
    isValid = 0.0 < value < 0.15
    dic['tcCycleTime_max'] = (value, isValid)
    
    value = tcTimeDuration / nTcCycles if nTcCycles > 0 else NAN
    isValid = 0.0 < value < 0.1
    dic['tcCycleTime_mean'] = (value, isValid)
    
    value = tcCycleTime.std() if nTcCycles > 0 else NAN
    isValid = 0.0 <= value < 0.07
    dic['tcCycleTime_std'] = (value, isValid)
    
    value = nOhyObjects / tcTimeDuration if tcTimeDuration > 0.0 else NAN
    isValid = 1.0 < value < 80.0
    dic['objCreationRate_mean'] = (value, isValid)
    
    value = nPosObjects
    isValid = value > 0
    dic['posObjectCount'] = (value, isValid)
    
    value = nTcCycles
    isValid = value > 100
    dic['tcCycleCount'] = (value, isValid)
    
    value = allValidPowers.mean() if allValidPowers.size > 0 else NAN
    isValid = 100.0 < value < 160.0
    dic['receivedPower_mean'] = (value, isValid)
    
    value = allValidDxs.max() if allValidDxs.size > 0 else NAN
    isValid = 100.0 < value < 300.0
    dic['fov_dx_max'] = (value, isValid)
    
    value = allValidDxs.mean() if allValidDxs.size > 0 else NAN
    isValid = 10.0 < value < 100.0
    dic['fov_dx_mean'] = (value, isValid)
    
    value = numpy.abs(allValidDys).max() if allValidDys.size > 0 else NAN
    isValid = 5.0 < value < 50.0
    dic['fov_dy_max'] = (value, isValid)
    
    value = allValidDys.mean() if allValidDys.size > 0 else NAN
    isValid = abs(value) < 10.0
    dic['fov_dy_mean'] = (value, isValid)
    
    value = allFinalCntAlives.max() if allFinalCntAlives.size > 0 else NAN
    isValid = value > 20
    dic['cntAlive_max'] = (value, isValid)
    
    value = allFinalCntAlives.mean() if allFinalCntAlives.size > 0 else NAN
    isValid = value > 2.0
    dic['cntAlive_mean'] = (value, isValid)
    
    value = egoSpeed.mean() if egoSpeed.size > 0 else NAN
    isValid = 5.0/3.6 < value < 130.0/3.6
    dic['egoSpeed_mean'] = (value, isValid)
    
    value = numpy.abs(egoYawRate).max() if egoYawRate.size > 0 else NAN
    isValid = value < 0.7
    dic['egoYawRate_max'] = (value, isValid)
    
    value = egoYawRate.mean() if egoYawRate.size > 0 else NAN
    isValid = abs(value) < 0.2
    dic['egoYawRate_mean'] = (value, isValid)
    
    value = egoOdoMeter[-1] - egoOdoMeter[0]
    isValid = value > 0.1 and value < 1000.0
    dic['egoDrivenDistance'] = (value, isValid)
    
    value = nInvalidTimeChannels
    isValid = value == 0
    dic['invalidTimeCount'] = (value, isValid)
    
    if vidUpdateCycleTime.size:
      value = numpy.count_nonzero(vidUpdateCycleTime > 0.15)
    else:
      value = NAN
    isValid = value == 0
    dic['fusMissedVidUpdates'] = (value, isValid)
    
    value = nFusIncons
    isValid = value == 0
    dic['fusMeasErrors'] = (value, isValid)
    
    # Static checks
    _dickeys = dic.keys()
    assert set(_dickeys).issubset(set(QUANTITIES.keys())),\
           "Missing description for one or more quantities"
    assert len(_dickeys) == len(set(_dickeys)),\
           "Attempt to add the same quantity multiple times"
    return t, dic
  
  def search(self, param, time, dic):
    batch = self.get_batch()
    check_votes = 'sensor check'
    check_quas = 'CVR3 sensor check'
    votes = batch.get_labelgroups(check_votes)
    names = batch.get_quanamegroups(check_quas)
    intervals = cIntervalList(time)
    report = Report(intervals, 'SensorCheck', names=names, votes=votes)

    set_sensorcheck(dic, report, check_quas, check_votes, (0, time.size))
    batch.add_entry(report, tags=['CVR3'])
    return


def set_sensorcheck(checks, report, check_quas, check_votes, interval):
  ids = []
  for name, (value, valid) in checks.iteritems():
    idx = report.addInterval(interval)
    report.set(idx, check_quas, name, value)
    vote = 'valid' if valid else 'invalid'
    report.vote(idx, check_votes, vote)
    ids.append(idx)
  return ids

