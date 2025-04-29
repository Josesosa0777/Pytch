import interface
import viewTCLength_CVR3

DefParam = interface.NullParam

class cView(viewTCLength_CVR3.cView):
  SignalGroups = [{"rmp.D2lLocationData_TC.tAbsMeasTimeStamp": ("ECU", "rmp.D2lLocationData_TC.tAbsMeasTimeStamp"), }, ]
  SignalRequest = "rmp.D2lLocationData_TC.tAbsMeasTimeStamp"
  SensorType = 'LRR3'

