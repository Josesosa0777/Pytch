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

import numpy as np

DefParam = interface.NullParam

SignalGroups = [{"csi.VehicleData_TC.nMot": ("ECU", "csi.VehicleData_TC.nMot"),
                 "csi.VehicleData_TC.psiDt": ("ECU", "csi.VehicleData_TC.psiDt"),
                 "csi.VelocityData_TC.vDis": ("ECU", "csi.VelocityData_TC.vDis"),
                 "ABSActive": ("EBC1", "ABSActive"),                 
                 "csi.VelocityData_TC.vxwflRaw": ("ECU", "csi.VelocityData_TC.vxwflRaw"),
                 "csi.VelocityData_TC.vxwfrRaw": ("ECU", "csi.VelocityData_TC.vxwfrRaw"),
                 "csi.VelocityData_TC.vxwrlRaw": ("ECU", "csi.VelocityData_TC.vxwrlRaw"),
                 "csi.VelocityData_TC.vxwrrRaw": ("ECU", "csi.VelocityData_TC.vxwrrRaw"),
                 "evi.General_TC.vxvRef": ("ECU", "evi.General_TC.vxvRef"),
                 "csi.VehicleData_T20.alpDtSteeringWheel": ("ECU", "csi.VehicleData_T20.alpDtSteeringWheel"),
                 "csi.XCustomerData_T20.alpSteeringWheel": ("ECU", "csi.XCustomerData_T20.alpSteeringWheel"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ###################
      #CAN input signals#
      ###################
      Client = datavis.cPlotNavigator(title="CAN_input", figureNr=102)
      interface.Sync.addClient(Client)
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_TC.nMot")
      Client.addSignal2Axis(Axis, "nMot", Time, Value, unit="1/min")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "evi.General_TC.vxvRef")
      Client.addSignal2Axis(Axis, "vRef", Time, Value, unit="m/s")   
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_TC.psiDt")
      Client.addSignal2Axis(Axis, "psiDt", Time, Value, unit="1/s")  
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vDis")
      Client.addSignal2Axis(Axis, "vDis", Time, Value, unit="m/s")     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vxwflRaw")
      Client.addSignal2Axis(Axis, "vfl", Time, Value, unit="m/s")     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vxwfrRaw")
      Client.addSignal2Axis(Axis, "vfr", Time, Value, unit="m/s")     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vxwrlRaw")
      Client.addSignal2Axis(Axis, "vrl", Time, Value, unit="m/s")     
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VelocityData_TC.vxwrrRaw")
      Client.addSignal2Axis(Axis, "vrr", Time, Value, unit="m/s")  
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "ABSActive")
      Client.addSignal2Axis(Axis, "ABSActive", Time, Value, unit="")
      Axis = Client.addAxis()
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.alpDtSteeringWheel")
      Client.addSignal2Axis(Axis, "alpDtSteeringWheel", Time, Value, unit="rad/s")
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.XCustomerData_T20.alpSteeringWheel")
      Client.addSignal2Axis(Axis, "alpSteeringWheel", Time, Value, unit="rad")   

      Client = datavis.cListNavigator(title="Steering_Wheel_grad")
      interface.Sync.addClient(Client) 
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.VehicleData_T20.alpDtSteeringWheel")
      Client.addsignal("alpDtSteeringWheel_grad", (Time, Value*180/np.pi), groupname="Default") 
      Time, Value = interface.Source.getSignalFromSignalGroup(Group, "csi.XCustomerData_T20.alpSteeringWheel")
      Client.addsignal("alpSteeringWheel_grad", (Time, Value*180/np.pi), groupname="Default")   
      return []

