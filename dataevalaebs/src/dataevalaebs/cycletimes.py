import sys
import os

import numpy
import pylab

import datavis
import aebs.proc

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_14-55_05.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_14-55_05.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-01_07.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-01_07.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-04_08.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/AEBS_H05.2604_2010-07-19_15-04_08.MDF'


# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_17-50_05.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_17-50_05.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_16-54_00.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_16-54_00.MDF'

# VideoFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_17-08_01.avi'
# MeasFile = '//Strs0003/Measure1/DAS/PEB/2010_07_19_release__AEBS_ACC_for_MAN_v2010-07-16__FullCascade_enhancedOPC_bugfixed/endu/AEBS_DL_H05.2604_2010-07-19_17-08_01.MDF'

# IAA-crash
# VideoFile = r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-20_32.avi'
# MeasFile =  r'D:\Messdaten\2010_09_14_\AEBS_06x-B365_2010-09-14_14-20_32.MDF'

# STR-crash
VideoFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_20_release__AEBS_ACC_for_MAN_v2010-09-20__PredictAdjust_03\AEBS_06x-B365_2010-09-20_16-22_37.avi'
MeasFile = r'\\strs0003\Measure1\DAS\PEB\2010_09_20_release__AEBS_ACC_for_MAN_v2010-09-20__PredictAdjust_03\AEBS_06x-B365_2010-09-20_16-22_37.MDF'



if len(sys.argv) > 1:
  MeasFile   = sys.argv[1]
  Head, Tail = os.path.splitext(sys.argv[1])
  VideoFile  = Head + '.avi'
  
Sync = datavis.cSynchronizer()

Source = aebs.proc.cLrr3Source(MeasFile, ECU='ECU_0_0')

timedet, beam1 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i0.i0')
timedet, beam2 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i0.i1', ScaleTime = timedet )
timedet, beam3 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i0.i2', ScaleTime = timedet )
timedet, beam4 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i0.i3', ScaleTime = timedet )

numdets_ramp1 = numpy.sum([beam1, beam2, beam3, beam4], 0)

timedet, beam1 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i1.i0')
timedet, beam2 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i1.i1', ScaleTime = timedet )
timedet, beam3 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i1.i2', ScaleTime = timedet )
timedet, beam4 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i1.i3', ScaleTime = timedet )

numdets_ramp2 = numpy.sum([beam1, beam2, beam3, beam4], 0)

timedet, beam1 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i2.i0')
timedet, beam2 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i2.i1', ScaleTime = timedet )
timedet, beam3 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i2.i2', ScaleTime = timedet )
timedet, beam4 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i2.i3', ScaleTime = timedet )

numdets_ramp3 = numpy.sum([beam1, beam2, beam3, beam4], 0)

timedet, beam1 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i3.i0')
timedet, beam2 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i3.i1', ScaleTime = timedet )
timedet, beam3 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i3.i2', ScaleTime = timedet )
timedet, beam4 = Source.getSignal('ECU_0_0', 'rmp.T2dDetectionData_TC.NumDets.i3.i3', ScaleTime = timedet )

numdets_ramp4 = numpy.sum([beam1, beam2, beam3, beam4], 0)

numdets_overall = numpy.sum([numdets_ramp1, numdets_ramp2, numdets_ramp3, numdets_ramp4], 0)


timeohl, validity = Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i0.c.c.Valid_b')
validity_all = validity * 0

for ohlindex in range(40):
    timeohl, validity = Source.getSignal('ECU_0_0', 'ohl.ObjData_TC.OhlObj.i' + str(ohlindex) + '.c.c.Valid_b', ScaleTime = timeohl )
    validity_all = numpy.sum([validity, validity_all], 0)
    pass

timefus, handles = Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i0.Handle')
handles_all = handles * 0

for fusindex in range(33):
    timefus, handles = Source.getSignal('ECU_0_0', 'fus.ObjData_TC.FusObj.i' + str(fusindex) + '.Handle', ScaleTime = timefus )
    handles = numpy.clip(handles, 0, 1)
    handles_all = numpy.add(handles, handles_all)
    pass


    
Client = datavis.cPlotNavigator()
Client.addsignal('ohl', Source.getSignal('ECU_0_0', 'Rtm_TC.tOSTickOhlSMainDuration'),
				 'ohl_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickOhlSMainMAXDuration'),
				 'fus', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickFusSMainDuration'),
				 'fus_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickFusSMainMAXDuration'),
   				 'asfAvMainT20', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfXMainavT20Duration'),
				 'asfAvMainT20_max', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfXMainavT20MAXDurati'),
				 'asfMainT20', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfMainT20Duration'),
				 'asfMainT20_max', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfMainT20MAXDuration'),
				 'asfCvMainT20', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfXMaincvT20Duration'),
				 'asfCvMainT20_max', Source.getSignal('ECU_0_0','Rtm_T10.tOSTickEVAsfXMaincvT20MAXDurati'),
				 'sitsAvMain', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickSitSMainavDuration'),
				 'sitsAvMain_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickSitSMainavMAXDuration'),
				 'sitMain', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickSitMainDuration'),
				 'sitMain_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickSitMainMAXDuration'),
				 'asfXavMain', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfXMainavDuration'),
				 'asfXavMain_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfXMainavMAXDuration'),
				 'asfMain', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfMainDuration'),
				 'asfMain_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfMainMAXDuration'),
				 'asfXcvMain', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfXMaincvDuration'),
				 'asfXcvMain_max', Source.getSignal('ECU_0_0','Rtm_TC.tOSTickAsfXMaincvMAXDuration'),
                 ylabel='Duration of task in $\mu s$',
                 # factor=[1,1,1,1],
                 # offset=[0,0,0,0],
				 # color=['-','-','-','-']
				 )
# Numdets = Number of valid detections in ramp / beam
Client.addsignal('ramp1', (timedet,numdets_ramp1) ,
                 'ramp2', (timedet,numdets_ramp2) ,
                 'ramp3', (timedet,numdets_ramp3) ,
                 'ramp4', (timedet,numdets_ramp4) ,
                 'overall', (timedet,numdets_overall) ,
                 # factor=[1,1,1,1],
                 # offset=[0,0,0,0],
				 color=['.','.','.','.','.'],
                 ylabel='Number of detections'
				 )
Client.addsignal('# OHL', (timeohl, validity_all),
                 '# FUS', (timefus, handles_all),
                 ylabel='Number of objects',
				 )
Sync.addClient(Client)





# viewFUSoverlay.viewFUSoverlay(Sync, Source, VideoFile)

timeohl, ohlduration = Source.getSignal('ECU_0_0', 'Rtm_TC.tOSTickOhlSMainDuration')


histofig = pylab.figure()
histoplot1 = histofig.add_subplot(3,1,1)
histoplot1.hist(ohlduration, bins = 100, normed = True)
histoplot1.set_xlabel('Duration of OHL in $\mu s$')
histoplot2 = histofig.add_subplot(3,1,2)
histoplot2.hist(validity_all, bins = max(validity_all))
histoplot2.set_xlabel('Number of OHL objects')
histoplot2.set_xlim(0, max([max(validity_all), max(handles_all)]))
histoplot3 = histofig.add_subplot(3,1,3)
histoplot3.hist(handles_all, bins = max(handles_all))
histoplot3.set_xlabel('Number of FUS objects')
histoplot3.set_xlim(0, max([max(validity_all), max(handles_all)]))
histofig.show()

Sync.run()    
raw_input("Press Enter to Exit")
pylab.close(histofig)
Sync.close()

