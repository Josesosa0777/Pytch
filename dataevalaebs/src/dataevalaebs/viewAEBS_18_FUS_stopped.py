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

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i0.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i1.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i1.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i10.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i10.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i11.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i11.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i12.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i12.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i13.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i13.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i14.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i14.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i15.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i15.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i16.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i16.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i17.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i17.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i18.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i18.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i19.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i19.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i2.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i2.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i20.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i20.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i21.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i21.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i22.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i22.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i23.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i23.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i24.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i24.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i25.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i25.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i26.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i26.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i27.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i27.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i28.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i28.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i29.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i29.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i3.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i3.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i30.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i30.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i31.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i31.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i32.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i32.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i4.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i4.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i5.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i5.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i6.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i6.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i7.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i7.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i8.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i8.b.b.Stopped_b"),
                 "fus.ObjData_TC.FusObj.i9.b.b.Stopped_b": ("ECU", "fus.ObjData_TC.FusObj.i9.b.b.Stopped_b"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ############################ 
      #FUS Objects - stopped flag#
      ############################
      Client = datavis.cPlotNavigator(title="FUS_objects_stopped_flag", figureNr=306)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("FUS_flag stopped%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.b.b.Stopped_b"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste
      return []

