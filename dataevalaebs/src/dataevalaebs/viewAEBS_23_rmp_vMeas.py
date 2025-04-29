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

SignalGroups = [{"rmp.D2lLocationData_TC.Location.i0.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i0.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i1.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i1.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i10.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i10.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i11.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i11.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i12.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i12.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i13.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i13.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i14.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i14.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i15.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i15.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i16.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i16.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i17.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i17.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i18.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i18.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i19.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i19.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i2.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i2.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i20.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i20.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i21.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i21.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i22.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i22.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i23.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i23.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i24.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i24.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i25.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i25.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i26.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i26.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i27.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i27.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i28.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i28.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i29.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i29.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i3.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i3.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i30.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i30.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i31.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i31.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i32.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i32.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i33.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i33.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i34.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i34.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i35.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i35.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i36.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i36.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i37.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i37.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i38.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i38.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i39.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i39.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i4.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i4.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i40.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i40.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i41.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i41.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i42.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i42.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i43.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i43.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i44.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i44.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i45.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i45.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i46.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i46.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i47.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i47.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i5.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i5.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i6.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i6.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i7.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i7.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i8.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i8.vMeas"),
                 "rmp.D2lLocationData_TC.Location.i9.vMeas": ("ECU", "rmp.D2lLocationData_TC.Location.i9.vMeas"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ###########################          
      #RMP radar locations vMeas# 
      ###########################
      Client = datavis.cPlotNavigator(title="RMP radar locations_vMeas", figureNr=411)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("v_Meas%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "rmp.D2lLocationData_TC.Location.i%d.vMeas"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste         
      return []

