import sys

import datavis
import viewFUSoverlayLRR3_AC100_ESR
import aebs.proc
import measparser

##############################################################
# Plots 2d-graph of given key attributes (see "keys" below)  #
# with Video and VideoOverlay of:                            #
# ATS_0 and POS_1 Object (CIPV)                              #
# ONLY FOR CVR3 !!!!!                                        #
##############################################################

MdfFile = sys.argv[1]

AviFile = MdfFile.lower().replace('.mdf', '.avi')
Sync    = datavis.cSynchronizer()
Source  = aebs.proc.cLrr3Source(MdfFile, ECU='ECU_0_0')

time_CVR3_ATS, CVR3_ATS_objects = viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source, **{"CVR3_ATS":1})
time_CVR3_POS, CVR3_POS_objects = viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source, **{"CVR3_POS":1})

CVR_ATS_0 = CVR3_ATS_objects[0]
CVR_POS_1 = CVR3_POS_objects[1]

keys=('dx','dy','dv','ax')
ylabel={'dx':'[m]','dy':'[m]','dv':'[m/s]','ax':'[m/s^2]'}


#prepare the signal plot
signals={}

for key in keys:
  signals[key]=[]
  signals[key].append('%s_%s'%(CVR_ATS_0["label"],key))
  signals[key].append((time_CVR3_ATS, CVR_ATS_0[key]))
  signals[key].append('%s_%s'%(CVR_POS_1["label"],key))
  signals[key].append((time_CVR3_POS, CVR_POS_1[key]))

  
#add the signals to the PlotNavigator without scaling
PN = datavis.cPlotNavigator('SIT compared to ATS',123)

for key in signals.iterkeys():
  PN.addsignal(ylabel=ylabel[key],xlabel='[s]',*signals[key])
  
Sync.addClient(PN)


#scale the signals for VideoOverlay on time_CVR3_ATS (time_CVR3_ATS==scaletime)
scaletime = time_CVR3_ATS

for key in ["dx","dy"]:
  CVR_POS_1[key] = measparser.cSignalSource.rescale(time_CVR3_POS,CVR_POS_1[key],scaletime)[1]

  
#prepare VideoOverlay and add the 2 Objects to it
VN = datavis.cVideoNavigator(AviFile, {})
vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime = scaletime)[1]
accel = Source.getSignal('MRR1plus_0_0','evi.General_TC.axvRef', ScaleTime=scaletime)[1]
VN.setobjects([CVR_ATS_0,CVR_POS_1], vidtime, accel / 50.)
vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=scaletime)[1]
Sync.addClient(VN, (scaletime, vidtime))


#Run the Sync
Sync.run()
raw_input('Press Enter to exit...')
Sync.close()
