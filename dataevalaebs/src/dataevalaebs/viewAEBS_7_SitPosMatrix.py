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

SignalGroups = [{"fus.ObjData_TC.FusObj.i0.dxv": ("ECU", "fus.ObjData_TC.FusObj.i0.dxv"),
                 "fus.ObjData_TC.FusObj.i1.dxv": ("ECU", "fus.ObjData_TC.FusObj.i1.dxv"),
                 "fus.ObjData_TC.FusObj.i10.dxv": ("ECU", "fus.ObjData_TC.FusObj.i10.dxv"),
                 "fus.ObjData_TC.FusObj.i11.dxv": ("ECU", "fus.ObjData_TC.FusObj.i11.dxv"),
                 "fus.ObjData_TC.FusObj.i12.dxv": ("ECU", "fus.ObjData_TC.FusObj.i12.dxv"),
                 "fus.ObjData_TC.FusObj.i13.dxv": ("ECU", "fus.ObjData_TC.FusObj.i13.dxv"),
                 "fus.ObjData_TC.FusObj.i14.dxv": ("ECU", "fus.ObjData_TC.FusObj.i14.dxv"),
                 "fus.ObjData_TC.FusObj.i15.dxv": ("ECU", "fus.ObjData_TC.FusObj.i15.dxv"),
                 "fus.ObjData_TC.FusObj.i16.dxv": ("ECU", "fus.ObjData_TC.FusObj.i16.dxv"),
                 "fus.ObjData_TC.FusObj.i17.dxv": ("ECU", "fus.ObjData_TC.FusObj.i17.dxv"),
                 "fus.ObjData_TC.FusObj.i18.dxv": ("ECU", "fus.ObjData_TC.FusObj.i18.dxv"),
                 "fus.ObjData_TC.FusObj.i19.dxv": ("ECU", "fus.ObjData_TC.FusObj.i19.dxv"),
                 "fus.ObjData_TC.FusObj.i2.dxv": ("ECU", "fus.ObjData_TC.FusObj.i2.dxv"),
                 "fus.ObjData_TC.FusObj.i20.dxv": ("ECU", "fus.ObjData_TC.FusObj.i20.dxv"),
                 "fus.ObjData_TC.FusObj.i21.dxv": ("ECU", "fus.ObjData_TC.FusObj.i21.dxv"),
                 "fus.ObjData_TC.FusObj.i22.dxv": ("ECU", "fus.ObjData_TC.FusObj.i22.dxv"),
                 "fus.ObjData_TC.FusObj.i23.dxv": ("ECU", "fus.ObjData_TC.FusObj.i23.dxv"),
                 "fus.ObjData_TC.FusObj.i24.dxv": ("ECU", "fus.ObjData_TC.FusObj.i24.dxv"),
                 "fus.ObjData_TC.FusObj.i25.dxv": ("ECU", "fus.ObjData_TC.FusObj.i25.dxv"),
                 "fus.ObjData_TC.FusObj.i26.dxv": ("ECU", "fus.ObjData_TC.FusObj.i26.dxv"),
                 "fus.ObjData_TC.FusObj.i27.dxv": ("ECU", "fus.ObjData_TC.FusObj.i27.dxv"),
                 "fus.ObjData_TC.FusObj.i28.dxv": ("ECU", "fus.ObjData_TC.FusObj.i28.dxv"),
                 "fus.ObjData_TC.FusObj.i29.dxv": ("ECU", "fus.ObjData_TC.FusObj.i29.dxv"),
                 "fus.ObjData_TC.FusObj.i3.dxv": ("ECU", "fus.ObjData_TC.FusObj.i3.dxv"),
                 "fus.ObjData_TC.FusObj.i30.dxv": ("ECU", "fus.ObjData_TC.FusObj.i30.dxv"),
                 "fus.ObjData_TC.FusObj.i31.dxv": ("ECU", "fus.ObjData_TC.FusObj.i31.dxv"),
                 "fus.ObjData_TC.FusObj.i32.dxv": ("ECU", "fus.ObjData_TC.FusObj.i32.dxv"),
                 "fus.ObjData_TC.FusObj.i4.dxv": ("ECU", "fus.ObjData_TC.FusObj.i4.dxv"),
                 "fus.ObjData_TC.FusObj.i5.dxv": ("ECU", "fus.ObjData_TC.FusObj.i5.dxv"),
                 "fus.ObjData_TC.FusObj.i6.dxv": ("ECU", "fus.ObjData_TC.FusObj.i6.dxv"),
                 "fus.ObjData_TC.FusObj.i7.dxv": ("ECU", "fus.ObjData_TC.FusObj.i7.dxv"),
                 "fus.ObjData_TC.FusObj.i8.dxv": ("ECU", "fus.ObjData_TC.FusObj.i8.dxv"),
                 "fus.ObjData_TC.FusObj.i9.dxv": ("ECU", "fus.ObjData_TC.FusObj.i9.dxv"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i0": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i0"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i1": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i1"),
                 "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i2": ("ECU", "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i2"),
                 "sit.IntroFinder_TC.Intro.i0.Id": ("ECU", "sit.IntroFinder_TC.Intro.i0.Id"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i0": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i0"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i1": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i1"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i2": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i2"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i3": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i3"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i4": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i4"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectList.i5": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectList.i5"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i1": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i1"),
                 "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i2": ("ECU", "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i2"),},]

class cView(interface.iView):
  @classmethod
  def view(Sync, cls, Param=DefParam): 
    try:
      Group = interface.Source.selectSignalGroup(SignalGroups)
    except measparser.signalgroup.SignalGroupError, error:
      print __file__
      print error.message
    else:
      ########################################
      #Position Matrix - Object list/relation#
      ########################################
      # signals=[] #Erstellen einer leeren Liste
      # for i in xrange(0,33,1):    #0= Beginn der Liste, 41= Ende der Liste, 1= Zaehlschritt
        # signals.append("FUS_dxv_i%d"%i)#Name der Signalbezeichnung
        # signals.append(interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.dxv"%i)) # Angabe des Geraetes und des Signalnamens
      # Client.addsignal(*signals) #entpacken der liste

      Index=12 #object ID to change for known object
      Client = datavis.cPlotNavigator(title="SIT - Position Matrix", figureNr=202) 
      interface.Sync.addClient(Client)
      Client.addsignal('FUS_dxv_i%d []'%Index, interface.Source.getSignalFromSignalGroup(Group, "fus.ObjData_TC.FusObj.i%d.dxv"%Index))
      Client.addsignal('SIT_Intro_Id []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.Id"))
      Client.addsignal('i0_FiltObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i0"),
                       'i1_FiltObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i1"),
                       'i2_FiltObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i2"))
      Client.addsignal('i0_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i0"),
                       'i1_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i1"),
                       'i2_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i2"))
      Client.addsignal('i3_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i3"),
                       'i4_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i4"),
                       'i5_IntroObjList []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectList.i5"))
      Client.addsignal('i0_FiltObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i0"),
                       'i1_FiltObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i1"),
                       'i2_FiltObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectRelation.i2")) 
      Client.addsignal('i0_ObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0"),
                       'i1_ObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i1"),
                       'i2_ObjRel []', interface.Source.getSignalFromSignalGroup(Group, "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i2")) 
      return []

