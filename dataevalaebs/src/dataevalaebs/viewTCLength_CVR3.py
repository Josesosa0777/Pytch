import datavis
import interface
import measproc
import numpy
import matplotlib.pyplot as mplt

DefParam = interface.NullParam

class cView(interface.iView):
  SignalGroups = [{"dsp.LocationData_TC.tAbsMeasTimeStamp": ("MRR1plus", "dsp.LocationData_TC.tAbsMeasTimeStamp"), }, ]
  SignalRequest = "dsp.LocationData_TC.tAbsMeasTimeStamp"
  SensorType = 'CVR3'

  def check(self):
    Group = interface.Source.selectSignalGroup(self.SignalGroups)
    return Group

  def fill(self, Group):
    return Group

  def view(self, Param, Group):
    ListNav = datavis.cListNavigator(title="Cycle time length of %s" % self.SensorType)
    interface.Sync.addClient(ListNav)

    Time, TCValue = interface.Source.getSignalFromSignalGroup(Group, self.SignalRequest)
    Diff = numpy.zeros_like(TCValue)
    Diff[:-1] = numpy.diff(TCValue)
    Mask = Diff > 0
    TCValueIncr = interface.Source.compare(Time, Mask, measproc.not_equal, 0)

    RestartTimes = []
    TC_Min = []
    TC_Max = []
    TC_Mean = []
    TC_All = []
    for Int_Lower, Int_Upper in TCValueIncr:
      RestartTimes.append(TCValue[Int_Upper - 1])
      TC_Min.append(numpy.min(numpy.diff(TCValue[Int_Lower:Int_Upper])))
      TC_Max.append(numpy.max(numpy.diff(TCValue[Int_Lower:Int_Upper])))
      TC_Mean.append(numpy.mean(numpy.diff(TCValue[Int_Lower:Int_Upper])))
      TC_All.extend(numpy.diff(TCValue[Int_Lower:Int_Upper]))
    RestartTimes = numpy.array(RestartTimes)
    TC_Min = numpy.array(TC_Min)
    TC_Max = numpy.array(TC_Max)
    TC_Mean = numpy.array(TC_Mean)
    TC_All = numpy.array(TC_All)

    ListNav.addsignal("Number of time counter restarts [-]", (numpy.array([Time.min()]), numpy.array([len(TCValueIncr) if len(TCValueIncr) > 1 else 0])))
    ListNav.addsignal("Minimum time at which the time counter restarts [s]", (numpy.array([Time.min()]), numpy.array([RestartTimes.min() if len(TCValueIncr) > 1 else 0])))
    ListNav.addsignal("Maximum time at which the time counter restarts [s]", (numpy.array([Time.min()]), numpy.array([RestartTimes.max() if len(TCValueIncr) > 1 else 0])))
    ListNav.addsignal("Average time at which the time counter restarts [s]", (numpy.array([Time.min()]), numpy.array([RestartTimes.mean() if len(TCValueIncr) > 1 else 0])))
    ListNav.addsignal("Minimum cycle time length [ms]", (numpy.array([Time.min()]), numpy.array([numpy.min(TC_Min) * 1000])))
    ListNav.addsignal("Maximum cycle time length [ms]", (numpy.array([Time.min()]), numpy.array([numpy.max(TC_Max) * 1000])))
    ListNav.addsignal("Average cycle time length [ms]", (numpy.array([Time.min()]), numpy.array([numpy.mean(TC_Mean) * 1000])))
    ListNav.addsignal("Percentage of values above 300 ms [%]", (numpy.array([Time.min()]), numpy.array([(numpy.count_nonzero(TC_All > 0.3) / float(len(TC_All))) * 100])))
    
    Client = datavis.cPlotNavigator(title='Histogram of cycle time lengths (%s)' % self.SensorType, figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(hide_legend=True, xlabel='Cycle times [ms]')
    Axis.hist(TC_All * 1000, bins=20, histtype='bar', align = 'mid')
    
    Client = datavis.cPlotNavigator(title='Histogram of counter restarts (%s)' % self.SensorType, figureNr=None)
    interface.Sync.addClient(Client)
    Axis = Client.addAxis(hide_legend=True, xlabel='Times at which restarts occur [s]')
    Axis.hist(RestartTimes, bins=50, histtype='bar', align = 'mid')
    
    