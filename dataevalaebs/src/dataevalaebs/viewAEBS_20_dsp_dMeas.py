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

SignalGroups = [{"dsp.LocationData_TC.Location.i0.dMeas": ("ECU", "dsp.LocationData_TC.Location.i0.dMeas"),
                 "dsp.LocationData_TC.Location.i1.dMeas": ("ECU", "dsp.LocationData_TC.Location.i1.dMeas"),
                 "dsp.LocationData_TC.Location.i10.dMeas": ("ECU", "dsp.LocationData_TC.Location.i10.dMeas"),
                 "dsp.LocationData_TC.Location.i11.dMeas": ("ECU", "dsp.LocationData_TC.Location.i11.dMeas"),
                 "dsp.LocationData_TC.Location.i12.dMeas": ("ECU", "dsp.LocationData_TC.Location.i12.dMeas"),
                 "dsp.LocationData_TC.Location.i13.dMeas": ("ECU", "dsp.LocationData_TC.Location.i13.dMeas"),
                 "dsp.LocationData_TC.Location.i14.dMeas": ("ECU", "dsp.LocationData_TC.Location.i14.dMeas"),
                 "dsp.LocationData_TC.Location.i15.dMeas": ("ECU", "dsp.LocationData_TC.Location.i15.dMeas"),
                 "dsp.LocationData_TC.Location.i16.dMeas": ("ECU", "dsp.LocationData_TC.Location.i16.dMeas"),
                 "dsp.LocationData_TC.Location.i17.dMeas": ("ECU", "dsp.LocationData_TC.Location.i17.dMeas"),
                 "dsp.LocationData_TC.Location.i18.dMeas": ("ECU", "dsp.LocationData_TC.Location.i18.dMeas"),
                 "dsp.LocationData_TC.Location.i19.dMeas": ("ECU", "dsp.LocationData_TC.Location.i19.dMeas"),
                 "dsp.LocationData_TC.Location.i2.dMeas": ("ECU", "dsp.LocationData_TC.Location.i2.dMeas"),
                 "dsp.LocationData_TC.Location.i20.dMeas": ("ECU", "dsp.LocationData_TC.Location.i20.dMeas"),
                 "dsp.LocationData_TC.Location.i21.dMeas": ("ECU", "dsp.LocationData_TC.Location.i21.dMeas"),
                 "dsp.LocationData_TC.Location.i22.dMeas": ("ECU", "dsp.LocationData_TC.Location.i22.dMeas"),
                 "dsp.LocationData_TC.Location.i23.dMeas": ("ECU", "dsp.LocationData_TC.Location.i23.dMeas"),
                 "dsp.LocationData_TC.Location.i24.dMeas": ("ECU", "dsp.LocationData_TC.Location.i24.dMeas"),
                 "dsp.LocationData_TC.Location.i25.dMeas": ("ECU", "dsp.LocationData_TC.Location.i25.dMeas"),
                 "dsp.LocationData_TC.Location.i26.dMeas": ("ECU", "dsp.LocationData_TC.Location.i26.dMeas"),
                 "dsp.LocationData_TC.Location.i27.dMeas": ("ECU", "dsp.LocationData_TC.Location.i27.dMeas"),
                 "dsp.LocationData_TC.Location.i28.dMeas": ("ECU", "dsp.LocationData_TC.Location.i28.dMeas"),
                 "dsp.LocationData_TC.Location.i29.dMeas": ("ECU", "dsp.LocationData_TC.Location.i29.dMeas"),
                 "dsp.LocationData_TC.Location.i3.dMeas": ("ECU", "dsp.LocationData_TC.Location.i3.dMeas"),
                 "dsp.LocationData_TC.Location.i30.dMeas": ("ECU", "dsp.LocationData_TC.Location.i30.dMeas"),
                 "dsp.LocationData_TC.Location.i31.dMeas": ("ECU", "dsp.LocationData_TC.Location.i31.dMeas"),
                 "dsp.LocationData_TC.Location.i32.dMeas": ("ECU", "dsp.LocationData_TC.Location.i32.dMeas"),
                 "dsp.LocationData_TC.Location.i33.dMeas": ("ECU", "dsp.LocationData_TC.Location.i33.dMeas"),
                 "dsp.LocationData_TC.Location.i34.dMeas": ("ECU", "dsp.LocationData_TC.Location.i34.dMeas"),
                 "dsp.LocationData_TC.Location.i35.dMeas": ("ECU", "dsp.LocationData_TC.Location.i35.dMeas"),
                 "dsp.LocationData_TC.Location.i36.dMeas": ("ECU", "dsp.LocationData_TC.Location.i36.dMeas"),
                 "dsp.LocationData_TC.Location.i37.dMeas": ("ECU", "dsp.LocationData_TC.Location.i37.dMeas"),
                 "dsp.LocationData_TC.Location.i38.dMeas": ("ECU", "dsp.LocationData_TC.Location.i38.dMeas"),
                 "dsp.LocationData_TC.Location.i39.dMeas": ("ECU", "dsp.LocationData_TC.Location.i39.dMeas"),
                 "dsp.LocationData_TC.Location.i4.dMeas": ("ECU", "dsp.LocationData_TC.Location.i4.dMeas"),
                 "dsp.LocationData_TC.Location.i40.dMeas": ("ECU", "dsp.LocationData_TC.Location.i40.dMeas"),
                 "dsp.LocationData_TC.Location.i41.dMeas": ("ECU", "dsp.LocationData_TC.Location.i41.dMeas"),
                 "dsp.LocationData_TC.Location.i42.dMeas": ("ECU", "dsp.LocationData_TC.Location.i42.dMeas"),
                 "dsp.LocationData_TC.Location.i43.dMeas": ("ECU", "dsp.LocationData_TC.Location.i43.dMeas"),
                 "dsp.LocationData_TC.Location.i44.dMeas": ("ECU", "dsp.LocationData_TC.Location.i44.dMeas"),
                 "dsp.LocationData_TC.Location.i45.dMeas": ("ECU", "dsp.LocationData_TC.Location.i45.dMeas"),
                 "dsp.LocationData_TC.Location.i46.dMeas": ("ECU", "dsp.LocationData_TC.Location.i46.dMeas"),
                 "dsp.LocationData_TC.Location.i47.dMeas": ("ECU", "dsp.LocationData_TC.Location.i47.dMeas"),
                 "dsp.LocationData_TC.Location.i5.dMeas": ("ECU", "dsp.LocationData_TC.Location.i5.dMeas"),
                 "dsp.LocationData_TC.Location.i6.dMeas": ("ECU", "dsp.LocationData_TC.Location.i6.dMeas"),
                 "dsp.LocationData_TC.Location.i7.dMeas": ("ECU", "dsp.LocationData_TC.Location.i7.dMeas"),
                 "dsp.LocationData_TC.Location.i8.dMeas": ("ECU", "dsp.LocationData_TC.Location.i8.dMeas"),
                 "dsp.LocationData_TC.Location.i9.dMeas": ("ECU", "dsp.LocationData_TC.Location.i9.dMeas"),},]

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
      #DSP radar locations dMeas# 
      ###########################
      Client = datavis.cPlotNavigator(title="DSP radar locations_dMeas", figureNr=401)
      interface.Sync.addClient(Client)
      signals=[] #Erstellen einer leeren Liste
      for i in xrange(0,48,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        signals.append("d_Meas%d"%i) #Name der Signalbezeichnung
        signals.append(interface.Source.getSignalFromSignalGroup(Group, "dsp.LocationData_TC.Location.i%d.dMeas"%i)) # Angabe des Geraetes und des Signalnamens
      Client.addsignal(*signals) #entpacken der liste 
      return []

