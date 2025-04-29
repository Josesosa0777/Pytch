import datavis
import measparser
import interface
import aebs
import numpy

DefParam = interface.NullParam

SignalGroups = [{},]

class cView(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      Client = datavis.cPlotNavigator(title="AC100", figureNr=None)
      interface.Sync.addClient(Client)

      Time, ObjectsIn = aebs.fill.fillAC100_POS.cAC100_POS.fill(aebs.fill.fillAC100_POS.DefParam)
      Objects = {}
      for o in ObjectsIn:
        Objects[o['label']] = o
        pass
      Detect = numpy.zeros_like(Objects['ACC']['type'])
      for Name in 'ACC', 'NIV_L', 'IIV', 'NIV_R':
        Axis = Client.addAxis()
        Value = Objects[Name]['type']
        Client.addSignal2Axis(Axis, Name, Time, Value)
        Detect[Value!=aebs.par.grouptypes.NONE_TYPE] = 1
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, 'Detected object', Time, Detect)
      

      Client = datavis.cPlotNavigator(title="CVR3", figureNr=None)
      interface.Sync.addClient(Client)

      Time, ObjectsIn = aebs.fill.fillCVR3_POS.cCVR3_POS.fill(aebs.fill.fillCVR3_POS.DefParam)
      Objects = {}
      for o in ObjectsIn:
        Objects[o['label']] = o
        pass
      Detect = numpy.zeros_like(Objects['LeftLane_near']['type'])
      for Name in 'LeftLane_near', 'SameLane_near', 'RightLane_near', 'LeftLane_far', 'SameLane_far', 'RightLane_far':
        Axis = Client.addAxis()
        Value = numpy.ones_like(Objects[Name]['type']) * aebs.par.grouptypes.NONE_TYPE
        Mask = Objects[Name]['dx'] > 0.0
        Value[Mask] = Objects[Name]['type'][Mask] 
        Client.addSignal2Axis(Axis, Name, Time, Value)
        Detect[Value!=aebs.par.grouptypes.NONE_TYPE] = 1
      Axis = Client.addAxis()
      Client.addSignal2Axis(Axis, 'Detected object', Time, Detect)
      pass
    pass



