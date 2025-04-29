"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

from Lrr3Source import cLrr3Source
from IBEOSource import cIBEOSource
from AEBSWarningSim import calcAEBSDeceleration
from AEBSWarningSim import calcAEBSActivity
from AEBSWarningSim import calcDriverActive
from AEBS_ASF_WarningSim import calcASFaAvoid
from AEBS_ASF_WarningSim import calcASF_aYAvoid
from AEBS_ASF_WarningSim import calcASFActivity
from RoadTypeClassification import calcRoadTypes
import filters

cLrr3SourceECU_0_0 = lambda FileName: cLrr3Source(FileName, ECU='ECU_0_0')

DefStatus = {"LRR3_LOC":1,"LRR3_OHL":1,"LRR3_FUS":1,"LRR3_ATS":1,"LRR3_POS":1,"LRR3_SIT":1,
             "CVR3_LOC":1,"CVR3_OHL":1,"CVR3_FUS":1,"CVR3_SIT":1,"CVR3_ATS":1,"CVR3_POS":1,
             "AC100":1,"ESR":1,"IBEO":1,"Iteris":1,"VFP":1,"MobilEye":1}


statusSignalsCrossTable = {"LRR3_LOC":('ECU_0_0',"rmp.D2lLocationData_TC.Location.i0.dMeas"),
                           "LRR3_OHL":('ECU_0_0','ohl.ObjData_TC.OhlObj.i0.dx'),
                           "LRR3_FUS":('ECU_0_0','fus.ObjData_TC.FusObj.i0.dxv'),
                           "LRR3_ATS":('ECU_0_0','ats.Po_T20.PO.i0.dxvFilt'),
                           "LRR3_POS":('ECU_0_0','fus.ObjData_TC.FusObj.i0.Handle'),
                           "LRR3_SIT":('ECU_0_0','sit.RelationGraph_TC.ObjectList.i0'),
                           "CVR3_LOC":('MRR1plus_0_0',"dsp.LocationData_TC.Location.i0.dMeas"),
                           "CVR3_OHL":('MRR1plus_0_0','ohl.ObjData_TC.OhlObj.i0.dx'),
                           "CVR3_FUS":('MRR1plus_0_0','fus.ObjData_TC.FusObj.i0.dxv'),
                           "CVR3_SIT":('MRR1plus_0_0','sit.RelationGraph_TC.ObjectList.i0'),
                           "CVR3_ATS":('MRR1plus_0_0','ats.Po_T20.PO.i0.dxvFilt'),
                           "CVR3_POS":('MRR1plus_0_0','fus.ObjData_TC.FusObj.i0.Handle'),
                           "AC100":('Tracks(663)_2_','tr0_track_selection_status'),
                           "ESR":('ESR_Track01(500)_4_ESR','CAN_TX_TRACK_RANGE_01'),
                           "IBEO":('Ibeo_List_header(500)_3_Ibeo','Ibeo_Number_of_objects'),
                           "Iteris":('Iteris_object_follow(98FF00E8)_1_','PO_target_range_OFC'),
                           "VFP":('VISION_OBSTACLE_MSG1(675)_4_VFP','CAN_VIS_OBS_RANGE'),
                           "MobilEye":('obstacle_0_info(720)_3_','Distance_to_Obstacle_0')}

status = None


DefTypeAngles = {"LRR3_LOC":[15,'r',0.1],"LRR3_OHL":[15,'r',0.1],"LRR3_FUS":[15,'r',0.1],"LRR3_ATS":[15,'r',0.1],"LRR3_POS":[15,'r',0.1],"LRR3_SIT":[15,'r',0.1],
                 "CVR3_LOC":[35,'r',0.1],"CVR3_OHL":[35,'r',0.1],"CVR3_FUS":[35,'r',0.1],"CVR3_SIT":[35,'r',0.1],"CVR3_POS":[35,'r',0.1],"CVR3_ATS":[35,'r',0.1],
                 "AC100":[14,'r',0.1],"ESR":[45,'r',0.1],"VFP":[48.7,'g',0.1],"IBEO":[35,'b',0.1],"Iteris":[50,'g',0.1],"MobilEye":[50,'g',0.1]}

DefGroups = {       'LRR3_LOC':['LRR3_LOC', [34,35], 'Y', False],
                    'CVR3_LOC':['CVR3_LOC', [18,19], 'X', False],
                    'LRR3_OHL':['LRR3_OHL', [26,27], 'K', False],
                    'CVR3_OHL':['CVR3_OHL', [20,21], 'O', False],
                    'LRR3_FUS':['LRR3_FUS', [0,2], '1', False],
                    'CVR3_FUS':['CVR3_FUS', [32,33], 'F', False],
                    'LRR3_SIT':['LRR3_SIT', [16,17], 'N', False],
                    'CVR3_SIT':['CVR3_SIT', [28,29], 'H', False],
                    'LRR3_POS':['LRR3_POS', [24,25], 'B', False],
                    'CVR3_POS':['CVR3_POS', [22,23], 'P', False],
                    'LRR3_ATS':['LRR3_ATS', [30,31], '8', False],
                    'CVR3_ATS':['CVR3_ATS', [3,4], 'A', False],
                    'AC100':['AC100', [5,6], '2', False],
                    'ESR':['ESR', [7,8], '3', False],
                    'IBEO':['IBEO', [10,9], '4', False],
                    'VFP':['VFP', [11,12,13], '5', False],
                    'Iteris':['Iteris', [14], '6', False],
                    'MobilEye':['MobilEye', [15], '7', False]
                    }

StandartGroups = {  'Intros':['Intros', [1], 'I', False],
                    'stationary':['stationary', [2,6,8,12,9,17,21,4,23,33,29,31,27,25], '0', False],
                    'moving':['moving', [0,14,15,10,11,7,5,16,20,3,22,24,26,30,34,28,32,99], '9', True],
                    'CVR3_LOC_invalid':['CVR3_LOC_invalid', [19],'Q', False],
                    'LRR3_LOC_invalid':['LRR3_LOC_invalid', [35],'W', False]}


Defms = 10
Defmew = 0


DefLegend = {   6:dict(label='AC100     - Stationary', marker='+', ms=Defms, mew=Defmew),
                5:dict(label='AC100     - Moving',     marker='^', ms=Defms, mew=Defmew),
                2:dict(label='LRR3_FUS  - Stationary', marker='$F$', ms=Defms, mew=Defmew),
                0:dict(label='LRR3_FUS  - Moving',     marker='$f$', ms=Defms, mew=Defmew),
                1:dict(label='Intros',      marker='o', ms=Defms, mew=Defmew),
                7:dict(label='ESR       - Moving',     marker='H', ms=Defms, mew=Defmew),
                8:dict(label='ESR       - Stationary', marker='.', ms=Defms, mew=Defmew),
                9:dict(label='IBEO      - Stationary', marker='_', ms=Defms, mew=Defmew),
                10:dict(label='IBEO      - Moving', marker='*', ms=Defms, mew=Defmew),
                11:dict(label='VFP       - Moving', marker='+', ms=Defms, mew=Defmew),
                12:dict(label='VFP       - Stationary', marker='2', ms=Defms, mew=Defmew),
                13:dict(label='VFP       - Pedestrian', marker='h', ms=Defms, mew=Defmew),
                14:dict(label='Iteris    - Moving', marker='v', ms=Defms, mew=Defmew),
                15:dict(label='MobilEye  - Moving', marker='1', ms=Defms, mew=Defmew),
                30:dict(label='LRR3_ATS  - Moving', marker='$A$', ms=Defms, mew=Defmew),
                31:dict(label='LRR3_ATS  - Stationary', marker='$a$', ms=Defms, mew=Defmew),
                18:dict(label='CVR3_LOC  - Valid', marker='$C$', ms=Defms, mew=Defmew),
                19:dict(label='CVR3_LOC  - Invalid', marker='$c$', ms=Defms, mew=Defmew),
                20:dict(label='CVR3_OHL  - Moving', marker='$O$', ms=Defms, mew=Defmew),
                21:dict(label='CVR3_OHL  - Stationary', marker='$o$', ms=Defms, mew=Defmew),
                28:dict(label='CVR3_SIT  - Moving', marker='$S$', ms=Defms, mew=Defmew),
                29:dict(label='CVR3_SIT  - Stationary', marker='$s$', ms=Defms, mew=Defmew),
                22:dict(label='CVR3_POS  - Moving', marker='$P$', ms=Defms, mew=Defmew),
                23:dict(label='CVR3_POS  - Stationary', marker='$p$', ms=Defms, mew=Defmew),
                24:dict(label='LRR3_POS  - Moving', marker='$P$', ms=Defms, mew=Defmew),
                25:dict(label='LRR3_POS  - Stationary', marker='$p$', ms=Defms, mew=Defmew),
                26:dict(label='LRR3_OHL  - Moving', marker='$O$', ms=Defms, mew=Defmew),
                27:dict(label='LRR3_OHL  - Stationary', marker='$o$', ms=Defms, mew=Defmew),
                3:dict(label='CVR3_ATS  - Moving', marker='$A$', ms=Defms, mew=Defmew),
                4:dict(label='CVR3_ATS  - Stationary', marker='$a$', ms=Defms, mew=Defmew),
                16:dict(label='LRR3_SIT  - Moving', marker='$S$', ms=Defms, mew=Defmew),
                17:dict(label='LRR3_SIT  - Stationary', marker='$s$', ms=Defms, mew=Defmew),
                32:dict(label='CVR3_FUS  - Moving', marker='$F$', ms=Defms, mew=Defmew),
                33:dict(label='CVR3_FUS  - Stationary', marker='$f$', ms=Defms, mew=Defmew),
                34:dict(label='LRR3_LOC  - Valid', marker='$C$', ms=Defms, mew=Defmew),
                35:dict(label='LRR3_LOC  - Invalid', marker='$c$', ms=Defms, mew=Defmew),
                99:dict(label='NoneType', marker='',ms=Defms,mew=Defmew)
                }
