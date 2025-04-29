import sys
import os

import datavis
import viewFUSoverlay
import viewTracks
import aebs.proc

VideoFile = None
MeasFile = None

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_14-55_05.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_14-55_05.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-01_07.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-01_07.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-04_08.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-04_08.MDF'

# VideoFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-31_13.avi'
# MeasFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-31_13.MDF'

# wObstacle 1
# VideoFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-59_17.avi'
# MeasFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-59_17.MDF'

# wObstacle 2
# VideoFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-53_16.avi'
# MeasFile = '//strs0003/Measure1/DAS/PEB/2010_08_17_release__AEBS_ACC_for_MAN_v2010-07-28__CsabaFix/AEBS_H05.2604_2010-08-17_15-53_16.MDF'

# wObstacle 3
# VideoFile = '//strs0003/Measure1/DAS/PEB/2010_07_27_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-27_11-58_14.avi'
# MeasFile = '//strs0003/Measure1/DAS/PEB/2010_07_27_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-27_11-58_14.MDF'

# Clara
# MeasFile = '//strw1463/clarax/Release/release__AEBS_ACC_for_MAN_v2010-08-23__IAAHMI_2/measurement/canape/moni_scu_DIAB_BSAMPLE_E200Z6V_2010-08-23_11-45_0112.MDF'

# IAA-check 1
# VideoFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_11-10_02.avi'
# MeasFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_11-10_02.MDF'

# IAA-check 2
# VideoFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_13-58_12.avi'
# MeasFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_13-58_12.MDF'
# VideoFile = r'd:\Messdaten\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_13-58_12.avi'
# MeasFile = r'd:\Messdaten\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_13-58_12.MDF'

# IAA-check 3
# VideoFile = r'D:\Messdaten\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_14-28_18.avi'
# MeasFile = r'D:\Messdaten\2010_09_10_release__AEBS_ACC_for_MAN_v2010-09-07__IAAHMI_11\AEBS_06x-B365_2010-09-10_14-28_18.MDF'

# IAA-crash
# VideoFile = r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-20_32.avi'
# MeasFile =  r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-20_32.MDF'

# IAA-non-crash
# VideoFile = r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-14_31.avi'
# MeasFile =  r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-14_31.MDF'

# IAA-non-crash 2
# VideoFile = r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-35_34.avi'
# MeasFile =  r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-35_34.MDF'

# SI fast-Crash
VideoFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_20_release__AEBS_ACC_for_MAN_v2010-09-20__PredictAdjust_03\AEBS_06x-B365_2010-09-20_16-22_37.avi'
MeasFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_20_release__AEBS_ACC_for_MAN_v2010-09-20__PredictAdjust_03\AEBS_06x-B365_2010-09-20_16-22_37.MDF'

if len(sys.argv) > 1:
  MeasFile   = sys.argv[1]
  Head, Tail = os.path.splitext(sys.argv[1])
  VideoFile  = Head + '.avi'
  
Sync = datavis.cSynchronizer()

Source = aebs.proc.cLrr3Source(MeasFile, ECU='ECU_0_0')

# FUSindex = '12'
# OHLindex = '23'

# FUSindex = '9'
# OHLindex = '32'

# FUSindex = '5'
# OHLindex = '24'

# FUSindex = '16'
# OHLindex = '36'

# wObstacle 1
# FUSindex = '6'
# OHLindex = '35'

# wObstacle 2
# FUSindex = '0'
# OHLindex = '35'

# wObstacle 3
# FUSindex = '29'
# OHLindex = '6'

# CLara
# FUSindex = '29'
# OHLindex = '11'

# IAA-Check 1
# FUSindex = '15'
# OHLindex = '13'

# IAA-Check 2
# FUSindex = '14'
# OHLindex = '12'

# IAA-Check 3
# FUSindex = '3'
# OHLindex = '10'

# IAA-crash
# FUSindex = '12'
# OHLindex = '19'

# IAA-non-crash
# FUSindex = '5'
# OHLindex = '10'

# IAA-non-crash 2
# FUSindex = '17'
# OHLindex = '12'

importantindex = 0

retgtime, retgstatus = Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.status')
for zeitindex in xrange(len(retgstatus)):
    if retgstatus[zeitindex] == 6:
        importantindex = zeitindex
        # print('drin')
        break

tempzeit, mrfdx = Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.dxv', ScaleTime = retgtime )
# print(importantindex)
# print(mrfdx[importantindex])


        
for fus_index in range(33):
    tempzeit, fusdx = Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(fus_index) + '.dxv', ScaleTime = retgtime )
    if ((fusdx[importantindex] == mrfdx[importantindex]) and (mrfdx[importantindex] != 0.0)):
        FUSindex = fus_index
        break

for ohl_index in range(40):
    tempzeit, ohldx = Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i' + str(ohl_index) + '.dx', ScaleTime = retgtime )
    if ((ohldx[importantindex] == mrfdx[importantindex]) and (mrfdx[importantindex] != 0.0)):
        OHLindex = ohl_index
        break



Client = datavis.cPlotNavigator()
Client.addsignal('FusObj.i' + str(FUSindex) + '.wExistProb', Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(FUSindex) + '.wExistProb'),
				 'Mrf.wExistProb', Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.wExistProb'),
				 'FusObj.i' + str(FUSindex) + '.wObstacle', Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(FUSindex) + '.wObstacle'),
				 'Mrf.wObstacle', Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.wObstacle'),
				 threshold=0.352,
				 color=['-','-','-','-']
				 )
Client.addsignal('Mrf.dxv', Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.dxv'),
				 'Mrf.vxv', Source.getSignal('ECU_0_0', 'Mrf._.PssObjectDebugInfo.vxv'),
				 'OhlObj.i' + str(OHLindex) + '.dbPowerFilt', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i' + str(OHLindex) + '.internal.dbPowerFilt'),
				 'OhlObjInd.i' + str(OHLindex) + '.dbPowerFilt', Source.getSignal('ECU_0_0', 'ohl.SensorInfo_TC.OhlObjInd.i' + str(OHLindex) + '.dbPowerFilt'),
				 'OhlObj.i' + str(OHLindex) + '.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i' + str(OHLindex) + '.dx'),
				 'FusObj.i' + str(FUSindex) + '.dxv', Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(FUSindex) + '.dxv'),
                 'XBR_SRCcontrol', Source.getSignal('EBC1(98F001FE)_1_', 'SourceAddressOfControllingDeviceForBrakeControl')
				 )
Sync.addClient(Client)


Client = datavis.cPlotNavigator()
Client.addsignal('retg.tBlockingTimer', Source.getSignal('ECU_0_0', 'repretg.tBlockingTimer'),
                 'retg.aPartialBraking', Source.getSignal('ECU_0_0', 'repretg.aPartialBraking'),
                 'retg.aAvoid_DEBUG', Source.getSignal('ECU_0_0', 'repretg.aAvoid_DEBUG'),
                 'retg.status', Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.status'),
                 'retg.ObjectIsVideoValidated_b', Source.getSignal('ECU_0_0', 'repretg.ObjectIsVideoValidated_b'),
   				 'IMU_XAccel', Source.getSignal('IMU_XAccel_and_YawRate(306)_2_', 'X_Accel'),
				 'XBR_Accel_Demand', Source.getSignal('XBR(8C040B2A)_1_', 'Ext_Acceleration_Demand'),
				 'ABSactive', Source.getSignal('EBC1(98F001FE)_1_', 'ABSActive'),
                 factor=[1.0,1.0,1.0,1.0,1.0,10.0,1.0,1.0]
				 )
Client.addsignal('sas.Deputy_ACUW', Source.getSignal('ECU_0_0', 'pressas.ShotTheDeputy_ACUW'),
                 'sas.Deputy_RETG', Source.getSignal('ECU_0_0', 'pressas.ShotTheDeputy_RETG'),
                 'Sheriff_ACUW', Source.getSignal('ECU_0_0', 'repacuw.ShotTheSheriff'),
                 'Sheriff_RETG', Source.getSignal('ECU_0_0', 'repretg.ShotTheSheriff'),
                 'Exec_ACUW', Source.getSignal('ECU_0_0', 'repacuw.__b_Rep.__b_RepBase.ExecutionStatus'),
                 'Exec_RETG', Source.getSignal('ECU_0_0', 'repretg.__b_Rep.__b_RepBase.ExecutionStatus'),
                 'XBR_actMode', Source.getSignal('EBC5_EBS5(98FDC40B)_1_', 'XBR_Active_Control_Mode'),
                 'AcoActACUW', Source.getSignal('ECU_0_0', 'repacuw.tAcoActivationTimer'),
                 'AcoActRETG', Source.getSignal('ECU_0_0', 'repretg.tAcoActivationTimer'),
				 )              
Sync.addClient(Client)


Client = datavis.cPlotNavigator()
Client.addsignal('pressas.wSkillAvoid', Source.getSignal('ECU_0_0', 'pressas.wSkillAvoid'),
                 'pressas.wSkillAvoidPredicted', Source.getSignal('ECU_0_0', 'pressas.wSkillAvoidPredicted'),
                 'pressas.wSkillAvoidLeft', Source.getSignal('ECU_0_0', 'pressas.wSkillAvoidLeft'),
                 'pressas.wSkillAvoidRight', Source.getSignal('ECU_0_0', 'pressas.wSkillAvoidRight'),
                 factor=[-16.0, -16.0, -16.0, -16.0],
				 )
Client.addsignal('BPact', Source.getSignal('ECU_0_0', 'namespaceSIT._.Egve._.BPAct_b'),
                 'GPact', Source.getSignal('ECU_0_0', 'csi.DriverActions_T20.Driveractions.Driveractions.GPAct_b'),
                 'Kickdown', Source.getSignal('ECU_0_0', 'csi.XCustomerData_T20.CustData.flags.MO_Kickdown_b'),
                 'GPsignature', Source.getSignal('ECU_0_0', 'asf.XDriverActions_T20.driverActions.w.GPSignatureRegognised_b'),
                 'fak1GPPos', Source.getSignal('ECU_0_0', 'csi.DriverActions_T20.fak1uGPPos'),
                 # 'GPPos', Source.getSignal('ECU_0_0', 'namespaceSIT._.Egve._.GPPos_uw'),
                 # factor=[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0, 1.0/65535.0]
                 # factor=[1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0, 1.0,1.0,1.0]
				 )              
Sync.addClient(Client)



# viewFUSoverlay.viewFUSoverlay(Sync, Source, VideoFile)
# Sync.addClient(Client, Source.getSignal('Multimedia_0_0','Multimedia_1'))

if VideoFile is not None:
    viewFUSoverlay.viewFUSoverlay(Sync, Source, VideoFile)
#Sync.addClient(datavis.cVideoNavigator(VideoFile), Source.getSignal('Multimedia_0_0','Multimedia_1'))



# Client = viewFUSoverlay.viewFUSoverlay(Sync, Source, VideoFile)
# Sync.addClient(Client)

# Client = datavis.cVideoNavigator(VideoFile)
# Client.addsignal('Multimedia_0_0.Multimedia_1', Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
# Sync.addClient(Client, Source.getSignal('Multimedia_1'))


# Client = datavis.cListNavigator()
# Client.addsignal('OhlObj.i12.dbPowerFilt', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i12.internal.dbPowerFilt'))
# Client.addsignal('OhlObjInd.i12.dbPowerFilt', Source.getSignal('ECU_0_0', 'ohl.SensorInfo_TC.OhlObjInd.i12.dbPowerFilt'))
# Client.addsignal('OhlObj.i12.maxDbPowerFilt', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i12.internal.maxDbPowerFilt'))
# Client.addsignal('OhlObj.i12.Index', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i12.internal.Index'))
# Client.addsignal('FusObj.i12.Handle', Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i12.Handle'))
# Sync.addClient(Client)

# ## tut #   
Client = datavis.cListNavigator()
Client.addsignal('ECU_0_0.pressam.aComfortSwingOut', Source.getSignal('ECU_0_0', 'pressam.aComfortSwingOut'))
Client.addsignal('ECU_0_0.pressas.aComfortSwingOut', Source.getSignal('ECU_0_0', 'pressas.aComfortSwingOut'))
# Client.addsignal('FusObj.i' + str(FUSindex) + '.dxv', Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(FUSindex) + '.dxv'))
# Client.addsignal('OhlObj.i0.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i0.dx'))
# Client.addsignal('OhlObj.i1.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i1.dx'))
# Client.addsignal('OhlObj.i2.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i2.dx'))
# Client.addsignal('OhlObj.i3.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i3.dx'))
# Client.addsignal('OhlObj.i4.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i4.dx'))
# Client.addsignal('OhlObj.i5.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i5.dx'))
# Client.addsignal('OhlObj.i6.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i6.dx'))
# Client.addsignal('OhlObj.i7.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i7.dx'))
# Client.addsignal('OhlObj.i8.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i8.dx'))
# Client.addsignal('OhlObj.i9.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i9.dx'))
# Client.addsignal('OhlObj.i10.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i10.dx'))
# Client.addsignal('OhlObj.i11.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i11.dx'))
# Client.addsignal('OhlObj.i12.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i12.dx'))
# Client.addsignal('OhlObj.i13.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i13.dx'))
# Client.addsignal('OhlObj.i14.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i14.dx'))
# Client.addsignal('OhlObj.i15.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i15.dx'))
# Client.addsignal('OhlObj.i16.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i16.dx'))
# Client.addsignal('OhlObj.i17.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i17.dx'))
# Client.addsignal('OhlObj.i18.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i18.dx'))
# Client.addsignal('OhlObj.i19.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i19.dx'))
# Client.addsignal('OhlObj.i20.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i20.dx'))
# Client.addsignal('OhlObj.i21.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i21.dx'))
# Client.addsignal('OhlObj.i22.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i22.dx'))
# Client.addsignal('OhlObj.i23.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i23.dx'))
# Client.addsignal('OhlObj.i24.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i24.dx'))
# Client.addsignal('OhlObj.i25.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i25.dx'))
# Client.addsignal('OhlObj.i26.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i26.dx'))
# Client.addsignal('OhlObj.i27.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i27.dx'))
# Client.addsignal('OhlObj.i28.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i28.dx'))
# Client.addsignal('OhlObj.i29.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i29.dx'))
# Client.addsignal('OhlObj.i30.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i30.dx'))
# Client.addsignal('OhlObj.i31.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i31.dx'))
# Client.addsignal('OhlObj.i32.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i32.dx'))
# Client.addsignal('OhlObj.i33.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i33.dx'))
# Client.addsignal('OhlObj.i34.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i34.dx'))
# Client.addsignal('OhlObj.i35.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i35.dx'))
# Client.addsignal('OhlObj.i36.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i36.dx'))
# Client.addsignal('OhlObj.i37.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i37.dx'))
# Client.addsignal('OhlObj.i38.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i38.dx'))
# Client.addsignal('OhlObj.i39.dx', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i39.dx'))
Sync.addClient(Client)

# Client = datavis.cListNavigator()
# Client.addsignal('OhlObj.i0', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i0.c.c.Valid_b'))
# Client.addsignal('OhlObj.i1', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i1.c.c.Valid_b'))
# Client.addsignal('OhlObj.i2', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i2.c.c.Valid_b'))
# Client.addsignal('OhlObj.i3', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i3.c.c.Valid_b'))
# Client.addsignal('OhlObj.i4', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i4.c.c.Valid_b'))
# Client.addsignal('OhlObj.i5', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i5.c.c.Valid_b'))
# Client.addsignal('OhlObj.i6', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i6.c.c.Valid_b'))
# Client.addsignal('OhlObj.i7', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i7.c.c.Valid_b'))
# Client.addsignal('OhlObj.i8', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i8.c.c.Valid_b'))
# Client.addsignal('OhlObj.i9', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i9.c.c.Valid_b'))
# Client.addsignal('OhlObj.i10', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i10.c.c.Valid_b'))
# Client.addsignal('OhlObj.i11', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i11.c.c.Valid_b'))
# Client.addsignal('OhlObj.i12', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i12.c.c.Valid_b'))
# Client.addsignal('OhlObj.i13', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i13.c.c.Valid_b'))
# Client.addsignal('OhlObj.i14', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i14.c.c.Valid_b'))
# Client.addsignal('OhlObj.i15', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i15.c.c.Valid_b'))
# Client.addsignal('OhlObj.i16', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i16.c.c.Valid_b'))
# Client.addsignal('OhlObj.i17', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i17.c.c.Valid_b'))
# Client.addsignal('OhlObj.i18', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i18.c.c.Valid_b'))
# Client.addsignal('OhlObj.i19', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i19.c.c.Valid_b'))
# Client.addsignal('OhlObj.i20', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i20.c.c.Valid_b'))
# Client.addsignal('OhlObj.i21', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i21.c.c.Valid_b'))
# Client.addsignal('OhlObj.i22', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i22.c.c.Valid_b'))
# Client.addsignal('OhlObj.i23', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i23.c.c.Valid_b'))
# Client.addsignal('OhlObj.i24', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i24.c.c.Valid_b'))
# Client.addsignal('OhlObj.i25', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i25.c.c.Valid_b'))
# Client.addsignal('OhlObj.i26', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i26.c.c.Valid_b'))
# Client.addsignal('OhlObj.i27', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i27.c.c.Valid_b'))
# Client.addsignal('OhlObj.i28', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i28.c.c.Valid_b'))
# Client.addsignal('OhlObj.i29', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i29.c.c.Valid_b'))
# Client.addsignal('OhlObj.i30', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i30.c.c.Valid_b'))
# Client.addsignal('OhlObj.i31', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i31.c.c.Valid_b'))
# Client.addsignal('OhlObj.i32', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i32.c.c.Valid_b'))
# Client.addsignal('OhlObj.i33', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i33.c.c.Valid_b'))
# Client.addsignal('OhlObj.i34', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i34.c.c.Valid_b'))
# Client.addsignal('OhlObj.i35', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i35.c.c.Valid_b'))
# Client.addsignal('OhlObj.i36', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i36.c.c.Valid_b'))
# Client.addsignal('OhlObj.i37', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i37.c.c.Valid_b'))
# Client.addsignal('OhlObj.i38', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i38.c.c.Valid_b'))
# Client.addsignal('OhlObj.i39', Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i39.c.c.Valid_b'))
# Sync.addClient(Client)



viewTracks.viewTracks(Sync, Source, 22, MeasFile)



Sync.run()    
raw_input("Press Enter to Exit")
Sync.close()

