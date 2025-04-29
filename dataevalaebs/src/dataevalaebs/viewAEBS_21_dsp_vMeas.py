"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 (BU2) Budapest Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis
import interface
import measparser

DefParam = interface.NullParam

SignalGroups = [{"dsp.LocationData_TC.Location.i0.vMeas": ("ECU", "dsp.LocationData_TC.Location.i0.vMeas"),
                 "dsp.LocationData_TC.Location.i1.vMeas": ("ECU", "dsp.LocationData_TC.Location.i1.vMeas"),
                 "dsp.LocationData_TC.Location.i10.vMeas": ("ECU", "dsp.LocationData_TC.Location.i10.vMeas"),
                 "dsp.LocationData_TC.Location.i11.vMeas": ("ECU", "dsp.LocationData_TC.Location.i11.vMeas"),
                 "dsp.LocationData_TC.Location.i12.vMeas": ("ECU", "dsp.LocationData_TC.Location.i12.vMeas"),
                 "dsp.LocationData_TC.Location.i13.vMeas": ("ECU", "dsp.LocationData_TC.Location.i13.vMeas"),
                 "dsp.LocationData_TC.Location.i14.vMeas": ("ECU", "dsp.LocationData_TC.Location.i14.vMeas"),
                 "dsp.LocationData_TC.Location.i15.vMeas": ("ECU", "dsp.LocationData_TC.Location.i15.vMeas"),
                 "dsp.LocationData_TC.Location.i16.vMeas": ("ECU", "dsp.LocationData_TC.Location.i16.vMeas"),
                 "dsp.LocationData_TC.Location.i17.vMeas": ("ECU", "dsp.LocationData_TC.Location.i17.vMeas"),
                 "dsp.LocationData_TC.Location.i18.vMeas": ("ECU", "dsp.LocationData_TC.Location.i18.vMeas"),
                 "dsp.LocationData_TC.Location.i19.vMeas": ("ECU", "dsp.LocationData_TC.Location.i19.vMeas"),
                 "dsp.LocationData_TC.Location.i2.vMeas": ("ECU", "dsp.LocationData_TC.Location.i2.vMeas"),
                 "dsp.LocationData_TC.Location.i20.vMeas": ("ECU", "dsp.LocationData_TC.Location.i20.vMeas"),
                 "dsp.LocationData_TC.Location.i21.vMeas": ("ECU", "dsp.LocationData_TC.Location.i21.vMeas"),
                 "dsp.LocationData_TC.Location.i22.vMeas": ("ECU", "dsp.LocationData_TC.Location.i22.vMeas"),
                 "dsp.LocationData_TC.Location.i23.vMeas": ("ECU", "dsp.LocationData_TC.Location.i23.vMeas"),
                 "dsp.LocationData_TC.Location.i24.vMeas": ("ECU", "dsp.LocationData_TC.Location.i24.vMeas"),
                 "dsp.LocationData_TC.Location.i25.vMeas": ("ECU", "dsp.LocationData_TC.Location.i25.vMeas"),
                 "dsp.LocationData_TC.Location.i26.vMeas": ("ECU", "dsp.LocationData_TC.Location.i26.vMeas"),
                 "dsp.LocationData_TC.Location.i27.vMeas": ("ECU", "dsp.LocationData_TC.Location.i27.vMeas"),
                 "dsp.LocationData_TC.Location.i28.vMeas": ("ECU", "dsp.LocationData_TC.Location.i28.vMeas"),
                 "dsp.LocationData_TC.Location.i29.vMeas": ("ECU", "dsp.LocationData_TC.Location.i29.vMeas"),
                 "dsp.LocationData_TC.Location.i3.vMeas": ("ECU", "dsp.LocationData_TC.Location.i3.vMeas"),
                 "dsp.LocationData_TC.Location.i30.vMeas": ("ECU", "dsp.LocationData_TC.Location.i30.vMeas"),
                 "dsp.LocationData_TC.Location.i31.vMeas": ("ECU", "dsp.LocationData_TC.Location.i31.vMeas"),
                 "dsp.LocationData_TC.Location.i32.vMeas": ("ECU", "dsp.LocationData_TC.Location.i32.vMeas"),
                 "dsp.LocationData_TC.Location.i33.vMeas": ("ECU", "dsp.LocationData_TC.Location.i33.vMeas"),
                 "dsp.LocationData_TC.Location.i34.vMeas": ("ECU", "dsp.LocationData_TC.Location.i34.vMeas"),
                 "dsp.LocationData_TC.Location.i35.vMeas": ("ECU", "dsp.LocationData_TC.Location.i35.vMeas"),
                 "dsp.LocationData_TC.Location.i36.vMeas": ("ECU", "dsp.LocationData_TC.Location.i36.vMeas"),
                 "dsp.LocationData_TC.Location.i37.vMeas": ("ECU", "dsp.LocationData_TC.Location.i37.vMeas"),
                 "dsp.LocationData_TC.Location.i38.vMeas": ("ECU", "dsp.LocationData_TC.Location.i38.vMeas"),
                 "dsp.LocationData_TC.Location.i39.vMeas": ("ECU", "dsp.LocationData_TC.Location.i39.vMeas"),
                 "dsp.LocationData_TC.Location.i4.vMeas": ("ECU", "dsp.LocationData_TC.Location.i4.vMeas"),
                 "dsp.LocationData_TC.Location.i40.vMeas": ("ECU", "dsp.LocationData_TC.Location.i40.vMeas"),
                 "dsp.LocationData_TC.Location.i41.vMeas": ("ECU", "dsp.LocationData_TC.Location.i41.vMeas"),
                 "dsp.LocationData_TC.Location.i42.vMeas": ("ECU", "dsp.LocationData_TC.Location.i42.vMeas"),
                 "dsp.LocationData_TC.Location.i43.vMeas": ("ECU", "dsp.LocationData_TC.Location.i43.vMeas"),
                 "dsp.LocationData_TC.Location.i44.vMeas": ("ECU", "dsp.LocationData_TC.Location.i44.vMeas"),
                 "dsp.LocationData_TC.Location.i45.vMeas": ("ECU", "dsp.LocationData_TC.Location.i45.vMeas"),
                 "dsp.LocationData_TC.Location.i46.vMeas": ("ECU", "dsp.LocationData_TC.Location.i46.vMeas"),
                 "dsp.LocationData_TC.Location.i47.vMeas": ("ECU", "dsp.LocationData_TC.Location.i47.vMeas"),
                 "dsp.LocationData_TC.Location.i5.vMeas": ("ECU", "dsp.LocationData_TC.Location.i5.vMeas"),
                 "dsp.LocationData_TC.Location.i6.vMeas": ("ECU", "dsp.LocationData_TC.Location.i6.vMeas"),
                 "dsp.LocationData_TC.Location.i7.vMeas": ("ECU", "dsp.LocationData_TC.Location.i7.vMeas"),
                 "dsp.LocationData_TC.Location.i8.vMeas": ("ECU", "dsp.LocationData_TC.Location.i8.vMeas"),
                 "dsp.LocationData_TC.Location.i9.vMeas": ("ECU", "dsp.LocationData_TC.Location.i9.vMeas"),},]

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
      #DSP radar locations vMeas# 
      ###########################
      Client = datavis.cPlotNavigator(title="DSP radar locations_vMeas", figureNr=402)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("v_Meas%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "dsp.LocationData_TC.Location.i%d.vMeas"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste
      return []

