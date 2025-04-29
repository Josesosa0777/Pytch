from collections import OrderedDict

import numpy as np
from scipy.io import savemat

from measparser import cSignalSource
from measparser.signalgroup import SignalGroupError

sg_release_1_2 = {
    # tracking input signals
    "Front_axle_speed"           : ("TA", "tracking_in_FrontAxleSpeed"),
    "Azimuth"                    : ("TA", "tracking_in_Azimuth"),
    "AzimuthOffset"              : ("TA", "tracking_par_AzimuthOffset"),
    "SteeringAngle"              : ("TA", "tracking_in_SteeringWheelAngle"), # wrong XCP naming
    "CoGDoppler"                 : ("TA", "tracking_in_CoGDoppler"),
    "YawRate"                    : ("TA", "tracking_in_YawRate"),
    "NumofDetectionsTransmitted" : ("TA", "tracking_in_NumOfDetectionsTransmitted"),
    "LateralAcceleration"        : ("TA", "tracking_in_LateralAcceleration"),
    "CoGRange"                   : ("TA", "tracking_in_CoGRange"),
    "HMI_main_switch"            : ("TA", "tracking_in_TAMainSwitch"),
    # warning triggering input signals
    "TurnIndicatorRight": ("TA", "warn_trigg_in_turn_ind_right"),
    #"warn_trigg_in_dy_rel_sensor": ("TA", "warn_trigg_in_dy_rel_sensor"),
    #"warn_trigg_in_vx_over_gnd_sensor": ("TA", "warn_trigg_in_vx_over_gnd_sensor"),
    #"warn_trigg_in_dx_rel_sensor": ("TA", "warn_trigg_in_dx_rel_sensor"),
    #"warn_trigg_in_vy_over_gnd_sensor": ("TA", "warn_trigg_in_vy_over_gnd_sensor"),
    #"warn_trigg_in_vx_ego_sensor": ("TA", "warn_trigg_in_vx_ego_sensor"),
    #"warn_trigg_in_vref": ("TA", "warn_trigg_in_vref"),
    #"warn_trigg_in_main_switch": ("TA", "warn_trigg_in_main_switch"),
    #"warn_trigg_in_ego_motion_state": ("TA", "warn_trigg_in_ego_motion_state"),
    #"warn_trigg_in_track_motion_state": ("TA", "warn_trigg_in_track_motion_state"),
    #"warn_trigg_in_tracking_status": ("TA", "warn_trigg_in_tracking_status"),
    #"warn_trigg_in_vy_ego_sensor": ("TA", "warn_trigg_in_vy_ego_sensor"),
    # recorded output signals
}

multimedia_signal = [{
    "Multimedia_1": ("Multimedia", "Multimedia_1"),
}]

def upgrade_sg_release_1_3(alias, dn, sn):
    if alias == "SteeringAngle":
        sn = sn.replace("Wheel","") # correct XCP naming SteeringWheelAngle -> SteeringAngle
    elif alias == "Front_axle_speed":
        sn = "warn_trigg_in_vref" # known XCP issue, "tracking_in_FrontAxleSpeed" cannot be identified at compile time
    else:
        pass # keep original signal
    return alias, (dn, sn)

sg_release_1_3 = dict( upgrade_sg_release_1_3(alias, dn, sn) for alias, (dn,sn) in sg_release_1_2.iteritems() )

sg_release_1_5 = {
    # new signals in CP 1.5
    "StdRange"            : ("TA", "tracking_in_StdRange"),
    "StdDoppler"          : ("TA", "tracking_in_StdDoppler"),
    "StdAzimuth"          : ("TA", "tracking_in_StdAzimuth"),
    "PowerDB"             : ("TA", "tracking_in_PowerDB"),
    "TurnIndicatorLeft"   : ("TA", "warn_trigg_in_turn_ind_left"),
    "ReverseGearDetected" : ("TA", "warn_trigg_in_reverse_gear_detected"),
}
# update with old signals
sg_release_1_5.update(sg_release_1_3)
# removed signal
sg_release_1_5.pop("AzimuthOffset")

sgs = OrderedDict(
    # put latest release on top as it is checked in this order
    release_1_5 = sg_release_1_5,
    release_1_3 = sg_release_1_3,
    release_1_2 = sg_release_1_2,
)

def synch_common_time(t):
    """ make common time synchronous (uniformly spaced) """
    t_start = round( t[0] ) # set start time to an integer value
    dt_mean = np.mean( np.diff(t) )
    dt = round(dt_mean, 2) # round to 2nd digit (10ms precision -> TODO: enough?)
    t_end = t_start + (t.size-1)*dt
    t_synch = np.linspace(t_start, t_end, num=t.size) # t_end included
    return t_synch

def preproc(infile, outfile):
    source = cSignalSource(infile)
    # match available signals to a known release's required group of signals
    errors = OrderedDict() # release_name : error_msg
    for release_name, sg in sgs.iteritems():
        try:
            group = source.selectSignalGroup( [sg] )
        except SignalGroupError, e:
            errors[release_name] = e.message
        else:
            break # matching group found, exit loop
    else:
        # no matching group found, stop processing
        release_msgs = '\n\n'.join( "%s:\n%s" %(release_name, msg) for release_name, msg in errors.iteritems() )
        msg = "Measurement doesn't contain required signals of any known relese.\n\nMissing signals:\n%s" %release_msgs
        raise RuntimeError(msg)
    # get common time (assuming each XCP signal on same fixed-step time domain)
    dummy_alias = group.iterkeys().next()
    t = group.get_time(dummy_alias)
    # make common time synchronous (uniformly spaced)
    t_synch = synch_common_time(t)
    mdict = dict(t=t_synch)
    # load signals
    for alias in group:
        v = group.get_value(alias)
        assert v.shape[0] == t_synch.size, 'Error: signal "%s" size %d does not match with time size %d' %(alias, v.shape[0], t_synch.size)
        if alias == "PowerDB" and v.dtype != np.float64:
            v = v.astype(np.float64) # recorded as uint8, cast to double for simulation
        mdict[alias] = v
    # load debug signals (all XCP data for now)
    devname = "TA"
    PosDevTags = [devname]
    NegDevTags = ["_"]
    PosSigTags, NegSigTags = [], []
    MatchCase = True
    DisableEmpty = True # don't load empty signals
    dbg_signames = source.querySignalNames(PosDevTags, NegDevTags, PosSigTags, NegSigTags, MatchCase, DisableEmpty)
    dbg_sg = { signame : (short_devname, signame) for short_devname, signame in dbg_signames if short_devname == devname } # "whole word" filter on device name (TODO: add to querySignalNames)
    dbg_group = source.selectSignalGroup( [dbg_sg] ) # should not raise error as signals come from querySignalNames
    dbg = { str(signame) : dbg_group.get_value(signame) for signame in dbg_group } # str() needed as savemat fails for nested dicts with unicode keys, see scipy #3487
    mdict["debug"] = dbg
    # select multimedia signal group
    vid_group = source.selectSignalGroup(multimedia_signal)
    # load video time
    vid_time = vid_group.get_value("Multimedia_1", ScaleTime=t_synch)
    # save multimedia times
    mdict["Multimedia_1"] = vid_time
    # save mat file
    savemat(outfile, mdict, long_field_names=True, do_compression=True, oned_as='column')
    return


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Preprocess measurement signals for re-simulation")
    parser.add_argument('infile', help='Input file path')
    parser.add_argument('outfile', help='Output (mat) file path')
    args = parser.parse_args()
    preproc(args.infile, args.outfile)
