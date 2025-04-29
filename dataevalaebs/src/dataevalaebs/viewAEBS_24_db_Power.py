"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{"ohl.ObjData_TC.OhlObj.i0.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i0.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i1.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i1.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i10.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i10.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i11.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i11.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i12.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i12.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i13.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i13.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i14.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i14.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i15.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i15.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i16.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i16.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i17.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i17.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i18.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i18.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i19.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i19.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i2.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i2.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i20.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i20.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i21.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i21.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i22.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i22.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i23.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i23.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i24.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i24.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i25.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i25.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i26.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i26.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i27.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i27.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i28.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i28.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i29.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i29.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i3.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i3.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i30.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i30.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i31.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i31.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i32.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i32.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i33.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i33.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i34.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i34.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i35.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i35.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i36.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i36.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i37.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i37.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i38.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i38.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i39.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i39.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i4.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i4.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i5.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i5.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i6.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i6.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i7.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i7.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i8.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i8.internal.maxDbPowerFilt"),
                 "ohl.ObjData_TC.OhlObj.i9.internal.maxDbPowerFilt": ("ECU", "ohl.ObjData_TC.OhlObj.i9.internal.maxDbPowerFilt"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ###################################
      #dbPower - for radom investigation#
      ###################################
      Client = datavis.cPlotNavigator(title="dbPower", figureNr=501)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,40,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("dbPowerFilt_i%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "ohl.ObjData_TC.OhlObj.i%d.internal.maxDbPowerFilt"%i)) 
      Client.addsignal(*signals)  
      return []

