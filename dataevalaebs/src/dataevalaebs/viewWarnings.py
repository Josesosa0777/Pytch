"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

# ------------------------------------------------------------------------------------------------------------------
# Action Coordinator ACO of Predictive Safety Systems
ACOs = [ ['ECU_0_0', 'acooptiRequest', 'acoopti.__b_AcoNoFb.__b_Aco.request_B',             1],
         ['ECU_0_0', 'acoacoiRequest', 'acoacoi.__b_AcoNoFb.__b_Aco.request_B',             1],
         ['ECU_0_0', 'acobrajRequest', 'acobraj.__b_AcoCoFb.__b_Aco.request_B',             1],
         ['ECU_0_0', 'acopebpRequest', 'acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B', 1],
         ['ECU_0_0', 'acopebeRequest', 'acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B', 1],
         ['ECU_0_0', 'acopebmRequest', 'acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B', 1],
         ['ECU_0_0', 'acoxbadRequest', 'acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B', 1]]

ACOs_not_used = [['ECU_0_0', 'acowarbRequest', 'acowarb.__b_AcoNoFb.__b_Aco.request_B', 1],
                 ['ECU_0_0', 'acobeltRequest', 'acobelt.__b_AcoNoFb.__b_Aco.request_B', 1],
                 ['ECU_0_0', 'acobrapRequest', 'acobrap.__b_AcoNoFb.__b_Aco.request_B', 1],
                 ['ECU_0_0', 'acochasRequest', 'acochas.__b_AcoNoFb.__b_Aco.request_B', 1],
                 ['ECU_0_0', 'acohbatRequest', 'acohbat.__b_AcoNoFb.__b_Aco.request_B', 1]]

# used to be downward compatible
Warnings = ACOs + ACOs_not_used

""":type: list
Parameter for viewer functions to see the Action Coordinator ACOs.
[[DeviceName<str>, Title<str>, SignalName<str>, CheckValue<int>]]"""

#  ACOs control the Human Machine Interface
#  acooptiRequest -> ECU.asf.HmiReq_TC.requestFlags.l.OptInfoReq_b
#  acoacoiRequest -> ECU.asf.HmiReq_TC.requestFlags.l.AcousticInfoReq_b



# ------------------------------------------------------------------------------------------------------------------
# REactions Patterns REPs of Predictive Safety Systems
#   (status == 6) means reaction pattern is locked
REPs = [ ['ECU_0_0', 'Reaction Pattern Prewarning',           'repprew.__b_Rep.__b_RepBase.status', 6],
         ['ECU_0_0', 'Reaction Pattern Acute Warning',        'repacuw.__b_Rep.__b_RepBase.status', 6],
         ['ECU_0_0', 'Reaction Pattern Reaction Time Gain',   'repretg.__b_Rep.__b_RepBase.status', 6],
         ['ECU_0_0', 'Reaction Pattern Deceleration Support', 'repdesu.__b_Rep.__b_RepBase.status', 6]]
""":type: list
Parameter for viewer functions to see the currently used reaction patterns.
[[DeviceName<str>, Title<str>, SignalName<str>, CheckValue<int>]]"""

# currently not used REPs (keep it here and move to list above if used)
REPs_not_used = [ ['ECU_0_0', 'Reaction Pattern Information',               'repinfo.__b_Rep.__b_RepBase.status', 6],
                  ['ECU_0_0', 'Reaction Pattern Latent Danger Information', 'repladi.__b_Rep.__b_RepBase.status', 6],
                  ['ECU_0_0', 'Reaction Pattern HBA',                       'repbrph.__b_Rep.__b_RepBase.status', 6],
                  ['ECU_0_0', 'Reaction Pattern Brake Prefill',             'repbrpp.__b_Rep.__b_RepBase.status', 6],
                  ['ECU_0_0', 'Reaction Pattern Auto Brake',                'repaubr.__b_Rep.__b_RepBase.status', 6]]

Iveco_warnings = [['ACC1_27(98FE6F27)_1_', 'ACCDistanceAlertSignal', 'ACCDistanceAlertSignal', 1]]
                  
Iveco_warnings_vis_ats0 =  [['ECU_0_0', 'ats.Po_TC.PO.i0.dxvFilt', 'ats.Po_TC.PO.i0.dxvFilt', 1],
                  ['ECU_0_0', 'ats.Po_TC.PO.i0.dycAct', 'ats.Po_TC.PO.i0.dycAct', 1],
                  ['ECU_0_0', 'ats.Po_TC.PO.i0.vxvFilt', 'ats.Po_TC.PO.i0.vxvFilt', 1]]
Iveco_warnings_vis_ats4 = [['ECU_0_0', 'ats.Po_TC.PO.i4.dxvFilt', 'ats.Po_TC.PO.i4.dxvFilt', 1],
                  ['ECU_0_0', 'ats.Po_TC.PO.i4.dycAct', 'ats.Po_TC.PO.i4.dycAct', 1]]
Iveco_warnings_vis_general_data = [['ECU_0_0', 'evi.General_T20.vxvRef',               'evi.General_T20.vxvRef', 1],
                                    ['ECU_0_0', 'evi.General_T20.psiDtOpt',               'evi.General_T20.psiDtOpt', 1],
                                    ['ECU_0_0', 'dcp.kapCourse',               'dcp.kapCourse', 1],
                                    ['ECU_0_0', 'evi.MovementData_T20.kapCurvTraj',               'evi.MovementData_T20.kapCurvTraj', 1]]
Iveco_warnings_object_interface_data = [['ACC1_27(98FE6F27)_1_', 'DistanceToForwardVehicle',               'DistanceToForwardVehicle', 1],
                                    ['ACC1_27(98FE6F27)_1_', 'SpeedOfForwardVehicle',               'SpeedOfForwardVehicle', 1]]

'''
2011-12-09 gueckeru:
this is obsolete - see searchDirk.py, viewDirk.py
Dirk = [['DIRK(98FFD02A)_1_', 'DFMgreenbutton', 'DFM_green_button', 1],
       ['DIRK(98FFD02A)_1_', 'DFMredbutton', 'DFM_red_button', 1]]

Dirk_Cnt = [['DIRK(98FFD02A)_1_', 'DFMCntredbutton', 'DFM_Cnt_red_button', 1],
       ['DIRK(98FFD02A)_1_', 'DFMCntgreen', 'DFM_Cnt_green', 1]]
'''

       
""":type: list
Parameter for viewer functions to see the not currently used reaction patterns.
[[DeviceName<str>, Title<str>, SignalName<str>, CheckValue<int>]]"""

# keep it becaused it is probably used by another module written by Jonas
Warnings2 =  REPs + REPs_not_used
""":type: list
Parameter for viewer functions to see the warnings.
[[DeviceName<str>, Title<str>, SignalName<str>, CheckValue<int>]]"""

# ------------------------------------------------------------------------------------------------------------------
# Intros of situation detection SIT 
Intros = [['ECU_0_0', 'SAM', 'sit.IntroFinder_TC.Intro.i0.Id', 1],
          ['ECU_0_0', 'SXM', 'sit.IntroFinder_TC.Intro.i0.Id', 2],
          ['ECU_0_0', 'SAS', 'sit.IntroFinder_TC.Intro.i0.Id', 3],
          ['ECU_0_0', 'LAM', 'sit.IntroFinder_TC.Intro.i0.Id', 4],
          ['ECU_0_0', 'RAM', 'sit.IntroFinder_TC.Intro.i0.Id', 5],
          ['ECU_0_0', 'SEM', 'sit.IntroFinder_TC.Intro.i0.Id', 6]] 
""":type: list
Parameter for viewer functions to see the SIT intros.
[[DeviceName<str>, Title<str>, SignalName<str>, CheckValue<int>]]"""
  
# ------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
  import sys
  import os

  import aebs.proc
  import datavis
  import viewFUSoverlay

  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Sync    = datavis.cSynchronizer()    
    Source  = aebs.proc.cLrr3Source('ECU_0_0', sys.argv[1])

    # Warnings (Action Coordinators)    
    Reports  = Source.findEvents(ACOs, 10.0)  
    datavis.viewEvents( Sync, Source, ACOs,    'ACOs', 100)  
    datavis.viewReports(Sync, Source, Reports, 'ACOs', 'm')  

    # Reaction Patterns 
    Reports = Source.findEvents(REPs, 10.0)  
    datavis.viewEvents( Sync, Source, REPs,    'REPs', 200)  
    datavis.viewReports(Sync, Source, Reports, 'REPs', 'b')  

    # Intros  
    Reports = Source.findEvents(Intros, 10.0)  
    datavis.viewEvents( Sync, Source, Intros,  'Intros', 300)  
    datavis.viewReports(Sync, Source, Reports, 'Intros', 'b')  

    if os.path.exists(AviFile):
      viewFUSoverlay.viewFUSoverlay(Sync, Source, AviFile)
      
    Sync.run()    
    raw_input("Press Enter to Exit\n")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
