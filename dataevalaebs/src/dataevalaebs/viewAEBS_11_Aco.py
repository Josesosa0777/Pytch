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

SignalGroups = [{"acoacoi.__b_AcoNoFb.__b_Aco.status": ("ECU", "acoacoi.__b_AcoNoFb.__b_Aco.status"),
                 "acobelj.__b_AcoNoFb.__b_Aco.status": ("ECU", "acobelj.__b_AcoNoFb.__b_Aco.status"),
                 "acobelt.__b_AcoNoFb.__b_Aco.status": ("ECU", "acobelt.__b_AcoNoFb.__b_Aco.status"),
                 "acobraj.__b_AcoCoFb.__b_Aco.status": ("ECU", "acobraj.__b_AcoCoFb.__b_Aco.status"),
                 "acobrap.__b_AcoNoFb.__b_Aco.status": ("ECU", "acobrap.__b_AcoNoFb.__b_Aco.status"),
                 "acochas.__b_AcoNoFb.__b_Aco.status": ("ECU", "acochas.__b_AcoNoFb.__b_Aco.status"),
                 "acohbat.__b_AcoNoFb.__b_Aco.status": ("ECU", "acohbat.__b_AcoNoFb.__b_Aco.status"),
                 "acoopti.__b_AcoNoFb.__b_Aco.status": ("ECU", "acoopti.__b_AcoNoFb.__b_Aco.status"),
                 "acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.status": ("ECU", "acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                 "acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.status": ("ECU", "acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                 "acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.status": ("ECU", "acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                 "acowarb.__b_AcoNoFb.__b_Aco.status": ("ECU", "acowarb.__b_AcoNoFb.__b_Aco.status"),
                 "acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.status": ("ECU", "acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:  
      #####################
      #Action coordinator #
      #####################
      Client = datavis.cPlotNavigator(title="Action coordinator", figureNr=206)
      interface.Sync.addClient(Client)
      Client.addsignal('acoacoi', interface.Source.getSignalFromSignalGroup(Group, "acoacoi.__b_AcoNoFb.__b_Aco.status"),
                       'acobelj', interface.Source.getSignalFromSignalGroup(Group, "acobelj.__b_AcoNoFb.__b_Aco.status"),
                       'acobelt', interface.Source.getSignalFromSignalGroup(Group, "acobelt.__b_AcoNoFb.__b_Aco.status"),
                       'acobraj', interface.Source.getSignalFromSignalGroup(Group, "acobraj.__b_AcoCoFb.__b_Aco.status"),
                       'acobrap', interface.Source.getSignalFromSignalGroup(Group, "acobrap.__b_AcoNoFb.__b_Aco.status"),
                       'acochas', interface.Source.getSignalFromSignalGroup(Group, "acochas.__b_AcoNoFb.__b_Aco.status"),
                       'acohbat', interface.Source.getSignalFromSignalGroup(Group, "acohbat.__b_AcoNoFb.__b_Aco.status"),
                       'acoopti', interface.Source.getSignalFromSignalGroup(Group, "acoopti.__b_AcoNoFb.__b_Aco.status"),
                       'acopebe', interface.Source.getSignalFromSignalGroup(Group, "acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                       'acopebm', interface.Source.getSignalFromSignalGroup(Group, "acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                       'acopebp', interface.Source.getSignalFromSignalGroup(Group, "acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"),
                       'acowarb', interface.Source.getSignalFromSignalGroup(Group, "acowarb.__b_AcoNoFb.__b_Aco.status"),
                       'acoxbad', interface.Source.getSignalFromSignalGroup(Group, "acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.status"))
      return []

