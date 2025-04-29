import sys
import getopt

from measparser.SignalSource import cSignalSource
 


opts, args = getopt.getopt(sys.argv[1:], 'm:u:')
optdict = dict(opts)

backup = optdict.get('-u', 'd:/measurement/backup')
meas   = optdict.get('-m', 'comparison_all_sensors_2012-08-21_16-46-26.MF4')

source = cSignalSource(meas, backup)

sg = { 
       # recorded
       "fus.SVidBasicInput_TC.dMountOffsetVid"             : ("RadarFC", "fus.SVidBasicInput_TC.dMountOffsetVid"),
       # NOT recorded
       "fus.SVidBasicInput_TC.dLongOffsetObjToVidCoordSys" : ("RadarFC", "fus.SVidBasicInput_TC.dLongOffsetObjToVidCoordSys"),
     }
sgs = [sg,]
groups, errors = source._filterSignalGroups(sgs)
source.save()

error, = errors
missing_signal_error = error['Missing signals']
assert missing_signal_error == {'RadarFC': set(['fus.SVidBasicInput_TC.dLongOffsetObjToVidCoordSys'])}
missing_devices_error = error['Missing devices']
assert missing_devices_error == set()
