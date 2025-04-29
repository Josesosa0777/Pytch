import copy
import sys

import numpy

import interface
import aebs.proc
import measproc

DefParam = interface.NullParam

SignalGroups = [
  {
   'Curv':    ("MRR1plus", "evi.MovementData_T20.kapCurvTraj"),
   'OneLane': ("MRR1plus", "evi.General_T20.qOneLaneHist"),
   'v_ego':   ("MRR1plus", "evi.General_T20.vxvRef"),
   'sc':      ("MRR1plus", "evi.MovementData_T20.kapCurvTraj"),
  },
  {
   'Curv':    ("ECU", "evi.MovementData_T20.kapCurvTraj"),
   'OneLane': ("ECU", "evi.General_T20.qOneLaneHist"),
   'v_ego':   ("ECU", "evi.General_T20.vxvRef"),
   'sc':      ("ECU", "evi.MovementData_T20.kapCurvTraj"),
  },
]

class cEnvironment(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    """
    Estimates environment base on ego_vehicle speed, yaw-rate and OneLaneHist Signal.
    """
    Source = self.get_source('main')
    scaletime, Curv = Source.getSignalFromSignalGroup(Group, "Curv")
    scaletime, OneLane = Source.getSignalFromSignalGroup(Group, "OneLane", ScaleTime=scaletime)
    scaletime, v_ego = Source.getSignalFromSignalGroup(Group, "v_ego",ScaleTime=scaletime)
    
    Curv_scaled = abs(Curv/0.05)
    v_ego_scaled = v_ego/25
    v_ego_scaled = numpy.repeat(numpy.array([1]),len(scaletime))-v_ego_scaled
    numpy.clip(v_ego_scaled,0,1,out=v_ego_scaled)
    
    Curv_diff = copy.deepcopy(Curv_scaled)
    for x in xrange(1,len(scaletime)):
      Curv_diff[x] = abs(Curv_scaled[x]-Curv_scaled[x-1])
    
    Curv_filt = aebs.proc.filters.pt1overSteps(Curv_diff)
    
    Curv_filt=Curv_filt/0.002
    
    result = (Curv_filt*OneLane*v_ego_scaled)**(1/3.)
    result = result.real
    result[numpy.isnan(result)] = -1
    
    result_filt = aebs.proc.filters.pt1overSteps(result)
    
    result_filt+=1
    result_filt[v_ego<1] = 0
    
    #slider around value with border
    Interval_top_border=copy.deepcopy(result_filt)
    Interval_bottom_border=copy.deepcopy(result_filt)
    Interval_len=0.6 # between 0.55 and 0.75 depending on border hits
    hitted_last_timestamp=False
    hitted_b_t=0
    Interval=[result_filt[0]-Interval_len/2,result_filt[0]+Interval_len/2]
    classification=numpy.repeat(numpy.array([0.]),len(scaletime))
    for x in xrange(len(scaletime)):
      if result_filt[x]>Interval[1]:
        if not hitted_last_timestamp:
          Interval_len=min(Interval_len+0.1,0.75)
        Interval[1]=result_filt[x]
        Interval[0]=Interval[1]-Interval_len
        hitted_b_t=1
        hitted_last_timestamp=True
      elif result_filt[x]<Interval[0]:
        if not hitted_last_timestamp:
          Interval_len=min(Interval_len+0.1,0.75)
        Interval[0]=result_filt[x]
        Interval[1]=Interval[0]+Interval_len
        hitted_b_t=0
        hitted_last_timestamp=True
      else:
        Interval_len=max(Interval_len-0.002,0.15)
        hitted_last_timestamp=False
        if hitted_b_t==1:
          Interval[0]=Interval[1]-Interval_len
        else:
          Interval[1]=Interval[0]+Interval_len
        hitted_last_timestep=False
      classification[x]=round(Interval[0]+Interval_len/2)
      Interval_top_border[x]=Interval[1]
      Interval_bottom_border[x]=Interval[0]
      
    
    classification_filt = copy.deepcopy(classification)
    starttime=0.
    endtime=0.
    laststartindex=1
    startindex=0
    endindex=0
    lastvalue=0
    actualvalue=0
    stepdistance=1
    for i in xrange(7):
      for x in xrange(1,len(scaletime)):
          endtime=scaletime[x]
          if classification_filt[x]!=classification_filt[x-1]:
            endindex=x
            if lastvalue==classification_filt[x] and endtime-starttime<stepdistance+stepdistance*i:
              if 0 in classification_filt[startindex:endindex]:
                classification_filt[startindex:endindex]=0
              else:
                classification_filt[startindex:endindex]=lastvalue
              lastvalue=classification_filt[x]
            elif lastvalue!=classification_filt[x] and endtime-starttime<stepdistance+stepdistance*i:
              if lastvalue==0:
                classification_filt[startindex:endindex]=classification_filt[laststartindex-1]
              elif classification_filt[x]==0:
                classification_filt[startindex:endindex]=lastvalue
              else:
                pass
              lastvalue=classification_filt[x-1]
            else:
              lastvalue=classification_filt[x-1]
            starttime=scaletime[x]
            laststartindex=startindex
            startindex=endindex

    reliances = {}
    reliances["Standing"] = calc_reliances(result_filt, -1,1)
    reliances["Highway"] = calc_reliances(result_filt, 0,2)
    reliances["FastRoad"] = calc_reliances(result_filt, 1,3)
    reliances["Road"] = calc_reliances(result_filt, 2,4)
    reliances["RoadTown"] = calc_reliances(result_filt, 3,5)
    reliances["Town"] = calc_reliances(result_filt, 4,6)
    reliances["LameTown"] = calc_reliances(result_filt, 5,7)
    reliances["Maneuver"] = calc_reliances(result_filt, 6,8)
    reliances["Maneuver"][result_filt>8] = 1.
    
    sc_DeviceName, sc_SignalName = Group['sc']
    for key, value in reliances.iteritems():
      try:
        Source.addSignal('searchEnvironment.py', "reliance_Report%s" %key,
                         Source.getTimeKey(sc_DeviceName, sc_SignalName), value)
      except ValueError:
        print >> sys.stderr, 'signal reliance_Report%s already exists' %key
    return scaletime, classification_filt, reliances

  def search(self, Param, scaletime, classification_filt, reliances):
    Batch = self.get_batch()

    Classifications = {0:"Standing", 1:"Highway", 2:"FastRoad", 3:"Road",
                       4:"RoadTown", 5:"Town",    6:"LameTown", 7:"Maneuver"}
    IntervalDict = dict([(Title,
                          measproc.cEventFinder.compExtSigScal(scaletime, 
                                                               classification_filt, 
                                                               measproc.equal, 
                                                               Limit))
                         for Limit, Title in Classifications.iteritems()])
    dropNmerge(IntervalDict)
    for Title, IntervalList in IntervalDict.iteritems():
      Report = measproc.cIntervalListReport(IntervalList, Title="Report%s" %Title)
      interface.Batch.add_entry(Report, self.NONE)
    return
    
def dropNmerge(IntervalDict, dropdist=1, mergedist=3):
  for value in IntervalDict.itervalues():
    value.drop(dropdist)
    value.merge(mergedist)
  return
          
def calc_reliances(value, lower, upper):
  """
  :Parameters:
    value: ndarray
    lower: float
    upper: float
  """
  reliance = copy.deepcopy(value)
  halfdistance=(upper-lower)/2
  mask = numpy.logical_and(value<upper,value>lower)
  reliance[mask] = 1-abs(lower+halfdistance-reliance[mask])/halfdistance
  mask = mask == False
  reliance[mask] = 0.
  return reliance
    
