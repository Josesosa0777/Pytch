import logging

import numpy as np
from datavis import pyglet_workaround # should be before scipy.io import to avoid avbin ImportError
from scipy.io import savemat

from preproc_xcp_meas_for_resim import multimedia_signal, synch_common_time

non_real_valued_sigs = ("HMI_main_switch", "NumofDetectionsTransmitted", "TurnIndicatorLeft", "TurnIndicatorRight",
                        "ReverseGearDetected")

vehi_sgs  = [
    # checkpoint 1.5
    {
        "LateralAcceleration": ("VDC2_3E", "VDC2_LatAccel_3E"),
        "YawRate": ("VDC2_3E", "VDC2_YawRate_3E"),
        "SteeringWheelAngle": ("VDC2_3E", "VDC2_SteerWhlAngle_3E"),
        "Front_axle_speed": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),
        "HMI_main_switch": ("HMI_IN", "mainswitch_TA"),
        "TurnIndicatorLeft": ("Aux_Stat_ZBR_1", "TurningIndicator_left"),
        "TurnIndicatorRight": ("Aux_Stat_ZBR_1", "TurningIndicator_right"),
        "CurrentGear": ("ETC2_03", "ETC2_CurrentGear_03"),
    },
]

logger = logging.getLogger()

def preproc(infile, outfile):
    from config.Config import init_dataeval

    config, manager, manager_modules = init_dataeval(['-m', infile])
    mb79_targets = manager_modules.calc('calc_mb79_raw_targets@aebs.fill', manager)
    t_synch = synch_common_time(mb79_targets.time)
    detection_signals = pack_detection_signals(mb79_targets)
    source = manager.get_source()
    vehicle_signals = load_vehicle_signals(source, t_synch)
    mdict = dict(t=t_synch)
    mdict.update(detection_signals)
    mdict.update(vehicle_signals)
    correct_data_type_of_all_zero_signals(mdict)
    # load video time
    vid_group = source.selectSignalGroup(multimedia_signal)
    mdict["Multimedia_1"] = vid_group.get_value("Multimedia_1", ScaleTime=t_synch)
    # save mat file
    savemat(outfile, mdict, long_field_names=True, do_compression=True, oned_as='column')
    return

def pack_detection_signals(mb79_targets):
    num_targets = mb79_targets.num_targets
    d = { 'NumofDetectionsTransmitted' : num_targets }
    shape = (mb79_targets.time.size, num_targets.max())
    dummy_target = mb79_targets.itervalues().next()
    for signame in ('CoGRange','Azimuth', 'CoGDoppler', 'StdRange','StdAzimuth', 'StdDoppler', 'PowerDB'):
        attr = '_' + signame # preprocessed CAN signals are cached with underscore prefix
        arr = np.zeros(shape, dtype=dummy_target[attr].dtype) # initialize with zeros (safer than empty)
        for col, target in enumerate( mb79_targets.itervalues() ): # mb79_targets assumed to be ordered by message number
            arr[:, col] = target[attr].data
        d[signame] = arr
    return d

def load_vehicle_signals(source, t):
    group = source.selectSignalGroup(vehi_sgs)
    d = { alias : group.get_value(alias, ScaleTime=t) for alias in group }
    # patch signals the same way as in TA/InputSelector block (TODO: move to matlab?)
    logger.info("Front_axle_speed, SteeringAngle and ReverseGearDetected calculated in line with TA/InputSelector.")
    d["Front_axle_speed"] /= 3.6  # km/h -> m/s
    d["SteeringAngle"] = d["SteeringWheelAngle"] / 21.  # steering wheel ratio
    d["ReverseGearDetected"] = d["CurrentGear"] < 0
    # remove CAN signals not on interface
    d.pop("SteeringWheelAngle")
    d.pop("CurrentGear")
    return d

def correct_data_type_of_all_zero_signals(d):
    # set real-valued all-zero signals to be of data type double (instead of uint8)
    for signame, arr in d.items(): # iterate and mutate
        if (    signame not in non_real_valued_sigs
            and not arr.any() # all zero
            and not np.issubdtype(arr.dtype, np.float) ):
                newarr = arr.astype(np.float64)
                d[signame] = newarr
                logger.info("%s data type changed from %s to %s." %(signame, arr.dtype, newarr.dtype))
    return

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Preprocess measurement signals for re-simulation")
    parser.add_argument('infile', help='Input file path')
    parser.add_argument('outfile', help='Output (mat) file path')
    args = parser.parse_args()
    preproc(args.infile, args.outfile)
