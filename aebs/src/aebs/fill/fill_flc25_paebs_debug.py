# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging
import numpy.ma as ma
import numpy as np
from enum import Enum
import PaebsBrakeModelModule as paebs
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import (
    TrackingState,
)
from primitives.bases import PrimitiveCollection
import numpy
from pyutils.functional import cached_attribute

logger = logging.getLogger()


class Source(Enum):
    """
    Enum representing the possible sources of a signal. Offers easier handling for redundant device information for
    all signals from the same source/device.
    """
    ARS = 0
    EM = 1
    CEM = 2
    PAEBS_DEBUG = 3
    PAEBS_HMI = 4
    PAEBS_PARAM = 5
    VEHICLE_INPUT = 6
    TRACK_SELECTION = 7
    AOA = 8
    PAEBS_OBJECT = 9
    FCU = 10
    PAEBS_OBJECT_2 = 11

    def __str__(self):
        # type: () -> str
        """
        Overloaded function to ensure that only the name of the enum will be printed.
        @return: Name of enum.
        """
        return self.name


class PaebsDevices(object):
    """
    Class that offers possibility to associate device name, source enum and maximum number of objects per device.
    Shall reduce the effort to define signals by saving structured information on dicts within class attributes.
    No instantiation necessary.
    """
    _device_names = {}
    _no_obj = {}

    @classmethod
    def registerDevice(cls, source, device, maxNoObj=None):
        # type: (Enum, str, int) -> None
        """
        Function offers the possibility to save device specific information on this class.
        @param source: The source of the signal represented by "Source" enum.
        @param device: The name of the signal device.
        @param maxNoObj: Maximum number of objects which provide the same base signal, only distinguished by index.
        Default value is None to indicate that there is just one source object without index available.
        """
        cls._device_names[source] = device
        cls._no_obj[source] = maxNoObj

    @classmethod
    def getDeviceName(cls, source):
        # type: (Enum) -> str
        """
        Function returns the name of a device after providing the Source enum. The Name needs to be registered first
        by "registerDevice" method.
        @param source: The source of the signal represented by "Source" enum.
        @return: The name of the signal device.
        """
        return cls._device_names[source]

    @classmethod
    def getMaxObjNo(cls, source):
        # type: (Enum) -> int
        """
        Function returns the maximum number of objects which provide the same base signal, only distinguished by index.
        The number needs to be registered first by "registerDevice" method.
        @param source: The source of the signal represented by "Source" enum.
        @return: Maximum number of objects which provide the same base signal, only distinguished by index.
        """
        return cls._no_obj[source]


class PaebsSignal(object):
    def __init__(self, baseShortName, device, fullName, source, index=None, signalGroup=1):
        # type: (str, str, str, Enum, int or str, int or tuple or list) -> None
        """
        Instantiates an object that corresponds to a single signal for paebs. Used for structured saving of data.
        @param baseShortName: The shortname of the signal independent of a potentially associated
        object number (e.g. CEM).
        @param device: The name of the signal device.
        @param fullName: The full name of the signal.
        @param source: The source of the signal represented by "Source" enum.
        @param index: The number of the object (e.g. CEM) that is associated with the signal.
        @param signalGroup: Number(s) of the associated signal group.
        """
        self.BaseShortname = baseShortName
        self.Device = device
        self.Fullname = fullName.format(index=str(index))
        self.Index = index
        self.Source = source

        # Handle different input types >> iterable values are needed
        if not isinstance(signalGroup, tuple) and not isinstance(signalGroup, list):
            signalGroup = [signalGroup]
        self.SignalGroup = signalGroup

        # Handle signals that need to be indexed
        if index is not None:
            self.Shortname = '{baseShortName}_{index}'.format(baseShortName=baseShortName, index=index)
        else:
            self.Shortname = baseShortName


class PaebsSignalGroups(object):
    """
    Class offers possibility to save, check, manage and provide structured information about signals that are
    mandatory for paebs debug track(s).
    """

    # Add or remove allowed shortnames here. Helps to avoid misspelling in the signal definition.
    _allowedBaseShortNames = ['paebs_debug_obj_index', 'life_time', 'dx', 'dy', 'fDistXStd', 'dist_along_ego_path',
                              'fDistY', 'fDistYStd', 'ego_lon_accel', 'vx_rel', 'fVrelXStd', 'lon_veloc_rel_ref',
                              'fVabsX', 'fVabsXStd', 'fVrelY', 'fVrelYStd', 'fVabsY', 'fVabsYStd', 'fDistX',
                              'collision_probability', 'obj_in_path', 'ttc', 'partial_emergency_brake_distance',
                              'emergency_brake_distance', 'full_cascade_brake_distance', 'classification',
                              'detected', 'obj_src', 'uiClassConfidence', 'uiProbabilityOfExistence',
                              'eAssociatedLane', 'uiAssociatedLaneConfidence', 'motion_state', 'system_state',
                              'internal_state', 'warning_level', 'allow_brake_hold', 'allow_emergency',
                              'allow_icb', 'allow_low_speed_braking', 'allow_partial', 'allow_ssb', 'allow_warning',
                              'cancel_emergency', 'cancel_partial', 'cancel_warning', 'low_speed_operational',
                              'operational', 'override_active', 'aoa_object_index', 'paebs_warning_time_min',
                              'paebs_partial_braking_delay', 'paebs_partial_braking_time_min',
                              'paebs_partial_braking_demand', 'paebs_partial_braking_demand_ramp_start',
                              'paebs_brake_demand_ramping_jerk', 'paebs_emergency_braking_demand_assumption',
                              'paebs_emergency_braking_delay', 'object_dx', 'paebs_bitfield_value', 'paebs_obj_index',
                              'object_flags_value', 'lat_dist_ref_at_ttc', 'fReactionDistance'
                              ]
    # Provides overview about registered names during debugging
    registered_shortNames = {}
    # Saves all registered signal group integers
    SignalGroups = []
    # Collects PaebsSignal objects
    Signals = []
    # Saves filter data
    ValidObjNo = {}

    @classmethod
    def registerSignal(cls, baseShortName, fullName, source, signalGroup=1):
        # type: (str, str, Enum, int) -> PaebsSignalGroups
        """
        Function offers the possibility to save signal specific information on this class.
        This is realized by instantiating PaebsSignal objects and saving them in a list as class attribute.
        If the signal needs to be indexed, this will be done as well by instantiating the full number of
        necessary signals. Precondition is that the inputted fullName parameter contains a "[{index}]" placeholder
        which takes the specific object index that is associated with the signal. The necessary number of
        indexed signals is retrieved from the PaebsDevice class, where the devices and max. object numbers need to
        be registered first. It is assumed that the index intervall is from [0 : max. object number - 1]
        (e.g. 0...99 for signals from CEM objects).
        If an object specific filter is implemented by the "setObjectFilter" method, only defined indexes will be
        instantiated, not the full range.
        Furthermore, an overview dict about all registered signals and associated signal groups will be created and
        the validity of the signal definition will be checked, criteria:
        1. Duplicated signals.
        2. Allowed signal shortnames (define in class attribute _allowedBaseShortNames) to avoid misspelling.
        3. Plausible signal groups.
        @param baseShortName: The shortname of the signal independent of a potentially associated
        object number (e.g. CEM).
        @param fullName: The full name of the signal.
        @param source: The source of the signal represented by "Source" enum.
        @param signalGroup: Number(s) of the associated signal group.
        @return: PaebsSignalGroups class --> No instantiation
        """

        # Instantiate PaebsSignal objects
        signals = []
        addSgnFlag = None

        # Check allowance for shortname
        if baseShortName in cls._allowedBaseShortNames:
            maxNoObj = PaebsDevices.getMaxObjNo(source)

            if maxNoObj is None:
                # non-indexed signal
                signals.append(PaebsSignal(baseShortName=baseShortName,
                                           device=PaebsDevices.getDeviceName(source),
                                           fullName=fullName,
                                           source=source,
                                           index=None,
                                           signalGroup=signalGroup
                                           )
                               )
            else:
                # indexed signals
                for obj_idx in range(0, maxNoObj):

                    # Filter
                    if source in cls.ValidObjNo.keys():
                        if obj_idx not in cls.ValidObjNo[source]:
                            addSgnFlag = False
                        else:
                            addSgnFlag = True
                    else:
                        addSgnFlag = True

                    # Instantiation of indexed signals.
                    if addSgnFlag:
                        signals.append(PaebsSignal(baseShortName=baseShortName,
                                                   device=PaebsDevices.getDeviceName(source),
                                                   fullName=fullName,
                                                   source=source,
                                                   index=obj_idx,
                                                   signalGroup=signalGroup
                                                   )
                                       )
                    else:
                        logger.debug('Paebs signal shortname: {} has been filtered.'.format(baseShortName))

            # Creation of overview dict.
            for sgn in signals:
                for number in sgn.SignalGroup:
                    if sgn.BaseShortname in cls.registered_shortNames.keys():
                        if sgn.Shortname in cls.registered_shortNames[sgn.BaseShortname].keys():
                            if number in cls.registered_shortNames[sgn.BaseShortname][sgn.Shortname]:
                                logger.error('Paebs signal shortname: {} is already registered in signal '
                                             'group: {} and will be ignored.'.format(sgn.Shortname, str(number)))
                            else:
                                cls.registered_shortNames[sgn.BaseShortname][sgn.Shortname].append(number)
                        else:
                            cls.registered_shortNames[sgn.BaseShortname][sgn.Shortname] = [number]
                    else:
                        cls.registered_shortNames[sgn.BaseShortname] = {sgn.Shortname: [number]}
                    if number not in cls.SignalGroups:
                        cls.SignalGroups.append(number)

            # Save on class attribute
            cls.Signals.extend(signals)
        else:
            logger.error('Paebs signal shortname: {} is not allowed for use and '
                         'will be ignored!!!'.format(baseShortName))

        return PaebsSignalGroups()

    @classmethod
    def setObjectFilter(cls, source, id_array):
        # type: (Enum, numpy.ndarray) -> None
        """
        Function offers possibility to implement a filter for relevant object indices.
        By the inputted numpy array it is calculated which indices are actually used in the current
        measurement data. This is conducted by removing duplicated indices and sorting. The result will
        be saved, associated with the source, on the class attribute (dict) "ValidObjNo".
        Once implemented, only signal names carrying these indices will be saved during registration.
        Assumption: An index > 100 is not representing an actual tracked object, hence a signal with such an
        index is not of interest and will be filtered even when present in the numpy id array.
        @param source: The source of the signal represented by "Source" enum.
        @param id_array: Numpy array that contains the valid object index for every timestamp.
        """
        id_array = id_array[id_array <= 100]
        cls.ValidObjNo[source] = list(np.sort(np.unique(id_array)))

    @classmethod
    def getSignalGroups(cls):
        # type: () -> list
        """
        Creates a list of signal groups needed to create the desired Flc25PaebsDebugObjectTrack
        from the signal objects stored on the class attributes, which have been created during signal registration.

        Schema: [[{shortName:(deviceName, fullName),...},...],...]

        SignalGroup: {shortName:(deviceName, fullName),...} >> Dict that associates all registered
        signal shortname with device name and full signal name.

        SignalGroups: [SignalGroup1,...] >> List of different signal groups that might represent different device
        and full signal names for the same and additional shortnames.
        In case the names of signals have changed or new signals have been added, this concept helps ensure backwards
        compatibility with older measurements. The source manager of the PyTCh is able to arbitrate the different
        signal groups and the select the one which refers to actual available signals in the measurement file.

        MessageGroup: [SignalGroups1,...] >> List of signal groups that are associated to one tracked object.
        It will trigger the creation of several Flc25PaebsDebugObjectTrack(s) if required.
        Each track will later receive the appropriate signal group from the source manager.

        Hint: For now, there is only one message group, means one object/track for Paebs Debug Signals defined.
        This means in fact only signal groups of a track are actually passed, but in this method a message group list
        is formally created to remain easily extendable.

        @return: Message group, respectively signal groups of registered signals.
        """
        messageGroup = []
        signalGroups = [{} for _ in range(max(cls.SignalGroups))]
        for sgn in cls.Signals:
            for SignalGroup in sgn.SignalGroup:
                sgn_grp_index = SignalGroup - 1
                signalGroups[sgn_grp_index][sgn.Shortname] = (sgn.Device, sgn.Fullname)

        messageGroup.append(signalGroups)

        return messageGroup

    @classmethod
    def getAttributeNames(cls):
        # type: () -> list
        """
        Function returns all shortnames (including index!) that are successfully registered.
        These names will be later the attribute names on the Flc25PaebsDebugObjectTrack, .e.g.
        shortname_signalA_ID34 >> Flc25PaebsDebugObjectTrack._shortname_signalA_ID34.
        @return: List of all registered shortnames.
        """
        out = []
        for sgn in cls.Signals:
            out.append(sgn.Shortname)
        return out


def processPaebsSignalNames(filter_obj=None):
    # type: (dict) -> (list, list)
    """
    Core function for signal definition.
    The following steps need to be conducted:
    1. Registration of devices (providing: source, device name and max. number of objects).
    2. Implementation of object filters, if required (providing: {source1: id_array1,...}).
    3. Registration of signals (providing: base shortname, signal full name, source and signal group(s))

    Hint: The returned tuple will be available as global variable. This necessary to pass the Calc and the
    Flc25PaebsDebugObjectTrack class necessary information about defined signals without major interventions
    in the PyTCh framework.

    @param filter_obj: Dictionary that assigns the source enum to an array of legal object indices
    @return: Message groups, Shortname list
    """
    if filter_obj is None:
        filter_obj = {}

    # 1. Registration of Devices
    PaebsDevices.registerDevice(source=Source.PAEBS_HMI,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t')
    PaebsDevices.registerDevice(source=Source.PAEBS_DEBUG,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t')
    PaebsDevices.registerDevice(source=Source.AOA,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t',
                                maxNoObj=3)
    PaebsDevices.registerDevice(source=Source.VEHICLE_INPUT,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t')
    PaebsDevices.registerDevice(source=Source.PAEBS_PARAM,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t')
    PaebsDevices.registerDevice(source=Source.CEM,
                                device='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas',
                                maxNoObj=100)
    PaebsDevices.registerDevice(source=Source.PAEBS_OBJECT,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t',
                                maxNoObj=2)
    PaebsDevices.registerDevice(source=Source.PAEBS_OBJECT_2,
                                device='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t',
                                maxNoObj=2)
    PaebsDevices.registerDevice(source=Source.FCU,
                                device='MFC5xx Device.FCU.FCUArsRangeData')

    # 2. Implementing Object Filter
    for source, id_array in filter_obj.items():
        PaebsSignalGroups.setObjectFilter(source, id_array)

    # 3. Registration of Signals
    PaebsSignalGroups.registerSignal(baseShortName='classification',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_classification',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='detected',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_detected',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='dx',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_dx',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_debug_obj_index',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_id',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='life_time',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_life_time',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='motion_state',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_motion_state',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='obj_src',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_source',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='ttc',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_ttc',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='vx_rel',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_relevant_object_vx_rel',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='system_state',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_system_state',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='warning_level',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t.sFlc25_PaebsOutput.hmi.paebs_warning_level',
                                     source=Source.PAEBS_HMI,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_brake_hold',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_brake_hold',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_emergency',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_emergency',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_icb',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_icb',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_low_speed_braking',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_low_speed_braking',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_partial',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_partial',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_ssb',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_ssb',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='allow_warning',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_allow_warning',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='cancel_emergency',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_cancel_emergency',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='cancel_partial',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_cancel_partial',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='cancel_warning',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_cancel_warning',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='emergency_brake_distance',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_emergency_brake_distance',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='full_cascade_brake_distance',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_full_cascade_brake_distance',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='internal_state',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_internal_state',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='low_speed_operational',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_low_speed_operational',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='operational',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_operational',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='override_active',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_override_active',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='partial_emergency_brake_distance',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sPAEBS_debug_signals.paebs_partial_emergency_brake_distance',
                                     source=Source.PAEBS_DEBUG,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='aoa_object_index',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].id',
                                     source=Source.AOA,
                                     signalGroup=(1, 2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='collision_probability',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].collision_probability',
                                     source=Source.AOA,
                                     signalGroup=(1, 2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='dist_along_ego_path',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].dist_along_ego_path',
                                     source=Source.AOA,
                                     signalGroup=(1, 2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='lon_veloc_rel_ref',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].lon_veloc_rel_ref',
                                     source=Source.AOA,
                                     signalGroup=(1, 2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='obj_in_path',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].obj_in_path',
                                     source=Source.AOA,
                                     signalGroup=(1, 2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='lat_dist_ref_at_ttc',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.sensor_input.paebs_object[{index}].lat_dist_ref_at_ttc',
                                     source=Source.AOA,
                                     signalGroup=(1, 2,3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_warning_time_min',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_warning_time_min',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_partial_braking_delay',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_partial_braking_delay',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_partial_braking_time_min',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_partial_braking_time_min',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_partial_braking_demand',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_partial_braking_demand',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_partial_braking_demand_ramp_start',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_partial_braking_demand_ramp_start',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_brake_demand_ramping_jerk',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_brake_demand_ramping_jerk',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_emergency_braking_demand_assumption',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_emergency_braking_demand_assumption',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_emergency_braking_delay',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t.sFlc25_PaebsParams.paebs_emergency_braking_delay',
                                     source=Source.PAEBS_PARAM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='ego_lon_accel',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlc25_PaebsInput.vehicle_input.ego_lon_accel',
                                     source=Source.VEHICLE_INPUT,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fDistX',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fDistX',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fDistXStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fDistXStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fDistY',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fDistY',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fDistYStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fDistYStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVrelXStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVrelXStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVabsX',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVabsX',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVabsXStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVabsXStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVrelY',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVrelY',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVrelYStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVrelYStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVabsY',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVabsY',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fVabsYStd',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].kinematic.fVabsYStd',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='uiClassConfidence',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].classification.uiClassConfidence',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='uiProbabilityOfExistence',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].qualifiers.uiProbabilityOfExistence',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='eAssociatedLane',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].laneStatus.eAssociatedLane',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='uiAssociatedLaneConfidence',
                                     fullName='MFC5xx Device.CEM_FDP_KB.CEM_FDP_KB_M_p_TpfOutputIfMeas.aObject[{index}].laneStatus.uiAssociatedLaneConfidence',
                                     source=Source.CEM,
                                     signalGroup=(1, 2, 3, 4)
                                     )

    PaebsSignalGroups.registerSignal(baseShortName='paebs_bitfield_value',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].paebs_bitfield_value',
                                     source=Source.PAEBS_OBJECT,
                                     signalGroup=(2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_obj_index',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].id',
                                     source=Source.PAEBS_OBJECT,
                                     signalGroup=(2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='object_flags_value',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].object_flags_value',
                                     source=Source.PAEBS_OBJECT,
                                     signalGroup=(2, 3)
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_bitfield_value',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].paebs_bitfield_value',
                                     source=Source.PAEBS_OBJECT_2,
                                     signalGroup=1
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='paebs_obj_index',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].id',
                                     source=Source.PAEBS_OBJECT_2,
                                     signalGroup=1
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='object_flags_value',
                                     fullName='MFC5xx Device.KB.MTSI_stKBFreeze_040ms_t.sFlts_PaebsDebugSignals.paebs_object[{index}].object_flags_value',
                                     source=Source.PAEBS_OBJECT_2,
                                     signalGroup=1
                                     )
    PaebsSignalGroups.registerSignal(baseShortName='fReactionDistance',
                                     fullName='MFC5xx Device.FCU.FCUArsRangeData.fReactionDistance',
                                     source=Source.FCU,
                                     signalGroup=(1, 2)
                                     )

    return PaebsSignalGroups.getSignalGroups(), PaebsSignalGroups.getAttributeNames()


# Launch global variables after signals definition process
"""
Message groups and shortnames need to be passed as global variables to the Calc class.
"""
message_group, short_names = processPaebsSignalNames()


# >>>CLASS DEFINITIONS<<<
class Flc25PaebsDebugObjectTrack(ObjectFromMessage):
    """
    Track class for debugging purposes in PAEBS.
    Class instances are carrying all relevant PAEBS debugging signals as private properties.
    Signal data (masked numpy arrays) are cached and only loaded at call of associated attribute.

    CACHING: All names in cls._attribs are saved as cached attribute with prefix (defined in base class) "_" on
    the class. This means that each of that attribute carries as value a reference on an instance of the
    "cached_attribute" class. This instance in turn carries the name of the attribute and a reference on
    the "cls._create" method from the Flc25PaebsDebugObjectTrack as property.
    When this attribute is called the first time it returns the result of the function call
    cls._create(attribute name), that will be the associated signal array saved on the inputted source object.
    At the same time the result will be saved directly on the attribute and overwrite the reference on the
    "cached_attribute" instance. Hence, from the second call on, the signal array will be returned directly.
    All functions that are defined on the class and not registered in the cls._reserved_names attribute,
    will be cached similarly, means, an attribute of the same name as the function will be implemented
    on the Flc25PaebsDebugObjectTrack and at the first call of this "function related attribute"
    the "cached_attribute" instance will call the function and save the reference on the result of the function call.
    To retrieve the result value of the function an attribute call on the Flc25PaebsDebugObjectTrack
    without "()" is sufficient.

    ATTENTION: The class and thus also the data of the "_attribs" property are already loaded by the module manager
    before an instantiation takes place and before this attribute of the entire class can be effectively changed by
    the Calc instance. As a result, the private attributes are already created with the names corresponding
    to the "_attribs" property content and their associated signal data are loaded from the cache when accessed later.
    Any subsequent change to this property only results in restricted access to the attributes that already exist.
    By using the cache, multiple instantiation and the implementation of many signals should only have a minor impact
    on generation time.

    """

    # Class Attributes

    _attribs = tuple(short_names)  # Names of the attributes that shall grant access to signal data, must be
    # identical with the shortnames of the message/signal group
    _special_methods = 'alive_intervals'  # Protected method names that can't be used twice per signal group definition
    _reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)
    _CEM_OBJ_NUM = 100  # Maximum number of CEM objects, maximum number of expected signals of the same base shortname
    _AOA_OBJ_NUM = 3  # Maximum number of AOA objects, maximum number of expected signals of the same base shortname
    _PAEBS_OBJ_NUM = 2  # Maximum number of PAEBS objects, maximum number of expected signals of the same base shortname

    def __init__(self, obj_id, time, source, group, invalid_mask, scaletime=None):
        # type: (int, numpy.array, object, list, numpy.array, numpy.array) -> None
        """
        Constructor of one track.

        @param obj_id: Index of instantiated track/tracked object
        @param time: time array that shall be base of all signal data
        @param source: Source manager
        @param group: Signal groups for track with current index
        @param invalid_mask: Boolean array to indicate validity of any datapoint in the signals.
        @param scaletime: Time on which all signals shall be scaled
        """

        # Save Inputs
        self._invalid_mask = invalid_mask
        self._group = group

        # Instantiate ObjectFromMessage
        super(Flc25PaebsDebugObjectTrack, self).__init__(
            obj_id, time, None, None, scaleTime=None
        )

        return

    def get_selection_timestamp(self, timestamp):
        # type: (numpy.array) -> int
        """

        @param timestamp:
        @return:
        """
        start, end = self.alive_intervals.findInterval(timestamp)
        return start

    def _create(self, signalName):
        # type: (str) -> numpy.array
        """
        Indispensable method that grants runtime access to a signal from the parsed measurement data in the cache
        via attributes assigned to them.

        @param signalName: Signal shortname
        @return: Signal data
        """
        value = self._group.get_value(signalName, ScaleTime=self.time)
        mask = ~self._invalid_mask
        out = np.ma.masked_all_like(value)
        out.data[mask] = value[mask]
        out.mask &= ~mask
        return out

    def _getCemSignal(self, signalShortName):
        # type: (str) -> numpy.array
        """
        Method that assembles the required signal data at any discrete point in time from the corresponding signal data
        of all available CEM objects, depending on which CEM object currently represents the relevant tracked object
        according to the paebs debug object index.
        To do this, the object index is read out element by element and the attributes are accessed with
        the appropriate indexed signal short name.

        @param signalShortName: Base shortname of the requested CEM signal.
        @return: Assembled signal data, coming from multiple CEM objects.
        """
        # Create array filled with zeros from main value dx
        cem_sgn = np.zeros_like(self._dx)

        # Create Mask indicating valid Cem Object ID
        cem_mask = np.where(self._paebs_debug_obj_index.data < self._CEM_OBJ_NUM, True, False)

        # Initiate Array representing Indices
        indices = np.arange(len(self._paebs_debug_obj_index.data), dtype=np.int32)

        # Reduce Array to valid Indices
        indices = indices[cem_mask]

        # Raw Eval Command to retrieve a specific Element in Signal Array
        # from Track Object >> self._fDistY_67[2354]
        cmd_raw = "self._%s_%s[%s]"

        # Loop through valid Indices only
        for index in indices:
            # Get current Cem Object ID
            id_value = self._paebs_debug_obj_index.data[index]

            # Retrieve requested Signal Array Element and replace on temporary Array
            cmd = cmd_raw % (signalShortName, id_value, index)
            cem_sgn.data[index] = eval(cmd)

        return cem_sgn

    def _getObjectSignal(self, signalShortName, objectName):
        # type: (str, str) -> numpy.array
        """
        Abstract and reusable Method that assembles the required signal data at any discrete point in time
        from the corresponding signal data of all available X objects, depending on which X object currently
        represents the relevant tracked object.

        X: AOA | PAEBS objects.

        Realization is identical for all object names, but signal names and numbers of objects are different.
        This is taken into account by the SELECTOR dict, which maps the signal name scheme and the class attribute
        that carries the information about the maximum number of tracked objects onto the selected/transmitted
        object name.

        Paebs object index and the index of the X object refer both to CEM objects.
        In order to determine which X object is relevant at which point in time, the indices of all X objects
        must be compared element by element with the Paebs object index.
        The matching X object is therefore also the relevant one for the corresponding discrete point in time
        and its signal short names are therefore also called in order to access the signal data
        and add them to the result array.

        This method can be extended by further object names/types. To do this, the SELECTOR dict must be adjusted
        and a new class attribute created that represents the maximum number of objects.

        @param signalShortName: Base shortname of the requested signal.
        @param objectName: Name of the tracked object that provides the requested signal.
        @return: Assembled signal data, coming from multiple objects of the same name.
        """
        SELECTOR = {'AoA': (self._AOA_OBJ_NUM, 'aoa_object_index_%d'),
                    'Paebs': (self._PAEBS_OBJ_NUM, 'paebs_obj_index_%d')}

        # Check implementation of object name
        if objectName in SELECTOR.keys():

            signalShortNameList = []

            for obj in xrange(SELECTOR[objectName][0]):
                # Create List containing possible signal names in dependance of object index
                signalShortNameList.append(
                    (signalShortName + "_%d" % obj, SELECTOR[objectName][1] % obj)
                )

            # Create array filled with zeros from main value dx
            res_sgn = np.zeros_like(self._dx)

            # Create Mask indicating valid Cem Object ID
            res_mask = np.where(self._paebs_debug_obj_index.data < self._CEM_OBJ_NUM, True, False)

            # Initiate Array representing Indices
            indices = np.arange(len(self._paebs_debug_obj_index.data), dtype=np.int32)

            # Reduce Array to valid Indices
            indices = indices[res_mask]

            for index in indices:

                # Get current Cem Object ID
                id_value = self._paebs_debug_obj_index.data[index]

                # Identify suitable AOA Object bearing same ID
                for sgn in signalShortNameList:

                    cmd_sgn_raw = "self._" + sgn[0] + ".data[%d]"
                    cmd_obj_id_raw = "self._" + sgn[1] + ".data[%d]"

                    obj_id_ref = eval(cmd_obj_id_raw % index)

                    if obj_id_ref == id_value:
                        res_sgn.data[index] = eval(cmd_sgn_raw % index)
                        break

            return res_sgn

        else:
            logger.error('Object name: "{objName}" is not implemented on "{className} class". '
                         'An zero array will be returned for {signal}.'.format(objName=objectName,
                                                                               className=self.__class__.__name__,
                                                                               signal=signalShortName))
            return np.zeros_like(self.dx)

    def _getPaebsSignal(self, signalShortName):
        # type: (str) -> numpy.array
        """
        Method that returns the required PAEBS object signal based on the transmitted short name.
        To do this, the "_getObjectSignal" method is called with the appropriate parameters.

        @param signalShortName: 
        @return: 
        """
        return self._getObjectSignal(signalShortName, 'Paebs')

    def _getAoaSignal(self, signalShortName):
        # type: (str) -> numpy.array
        """
        Method that returns the required AOA object signal based on the transmitted short name.
        To do this, the "_getObjectSignal" method is called with the appropriate parameters.

        @param signalShortName: registered base shortname of the required signal.
        @return: signal data
        """
        return self._getObjectSignal(signalShortName, 'AoA')

    # IDENTIFICATION

    def id(self):
        # type: () -> numpy.array
        """
        Attribute that retrieves an artificially generated array of the track ID that has been transmitted
        to the constructor.

        @return: Signal data containing track ID.
        """
        data = np.repeat(np.uint8(self._id), self.time.size)
        arr = np.ma.masked_array(data, mask=self._dx.mask)
        return arr

    def object_index(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - CEM object index whose signals are base of the scalar paebs debug signals.

        @return: signal data
        """
        return self._paebs_debug_obj_index

    def life_time(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Lifetime of the tracked CEM object whose signals are base of the scalar paebs debug signals.

        @return: signal data
        """
        return self._life_time

    def paebs_bitfield_value(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Bitfield values [-] (submitted as integer) of the front looking track selection representing the state
        of the single selection criteria for PAEBS objects.
        Conditions:
        1. Bit 0: class --> == CAR | TRUCK | MOTORCYCLE | BYCICLE | OTHER VEHICLE
        2. Bit 1: source --> == FUSED | RADAR | (CAMERA_ONLY & flts_paebs_allow_camera_only_objects)
        3. Bit 2: object_flags --> quality > "flts_flc25_ts_prob_filter" without id change &
                                maintenance state == measured | predicted &
                                rcs shall be valid &
                                dx >= 0 &
                                id ~= 255
        4. Bit 3: quality --> shall reach a certain threshold
        5. Bit 4: motion_state_crossing --> == CROSSING
        6. Bit 5: life_time --> > certain threshold
        7. Bit 6: lane_conf --> > certain threshold
        8. Bit 7: ego_lane --> Checks if the object is in the ego lane with high lane confidence
        9. Bit 8: adj_lane --> Checks if the object is in the adjacent lane with high lane confidence
        10. Bit 9: in_border --> Checks if the object is in the border with high lane confidence
        11. Bit 10: ttc --> > certain threshold
        12. Bit 11: source_radar --> ==  RADAR

        @return: signal data
        """
        return self._getPaebsSignal('paebs_bitfield_value')

    def object_flags_value(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Object flags values [-] (submitted as integer) of the front looking track selection representing the state
        of the single selection criteria for objects in general.
        Conditions:
        1. Bit 0: poe_valid
        2. Bit 1: maintenance_state_valid
        3. Bit 2: rcs_vehicle_valid
        4. Bit 3: id_dx_valid

        @return: signal data
        """
        return self._getPaebsSignal('object_flags_value')

    # GEOMETRY

    def dx(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Longitudinal distance [m] between ego vehicle and tracked object.

        Mandatory for Tracknav!

        @return: signal data
        """
        return self._dx

    def dx_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m] within the signal data of "dx".

        @return: signal data
        """
        return self._getCemSignal("fDistXStd")

    def dist_path(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Longitudinal distance [m] between vehicle and tracked object along the predicted ego vehicle path.

        @return: signal data
        """
        return self._getAoaSignal("dist_along_ego_path")

    def dy(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Lateral distance [m] between ego vehicle and tracked object.

        Mandatory for Tracknav!

        @return: signal data
        """
        return self._getCemSignal("fDistY")

    def dy_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m] within the signal data of "dy".

        @return: signal data
        """
        return self._getCemSignal("fDistYStd")

    def dy_ttc(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Lateral distance [m] between vehicle and tracked object at predicted collision time.

        @return: signal data
        """

        return self._getAoaSignal('lat_dist_ref_at_ttc')

    def dist_react(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Longitudinal distance [m] between ego vehicle and tracked object.


        @return: signal data
        """
        return self._fReactionDistance

    def range(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - The Shortest distance [m] between ego vehicle and tracked object.

        @return: signal data
        """
        return np.sqrt(np.square(self.dx) + np.square(self.dy))

    def angle(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Angle [RAD] between longitudinal axis of ego vehicle and tracked object.

        @return: signal data
        """
        return np.arctan2(self.dy, self.dx)

    # KINEMATIC
    def ax(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative longitudinal acceleration [m/s²] between ego vehicle and tracked object.

        @return: signal data
        """
        return self._ego_lon_accel

    def vx(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative longitudinal velocity [m/s] between ego vehicle and tracked object.

        Mandatory for Tracknav!

        @return: signal data
        """
        return self._vx_rel

    def vx_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m/s] within the signal data of "vx".

        @return: signal data
        """
        return self._getCemSignal("fVrelXStd")

    def vx_ref(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative longitudinal velocity [m/s] between ego vehicle and tracked object in referenced coordinate system.

        @return: signal data
        """
        return self._getAoaSignal("lon_veloc_rel_ref")

    def vx_abs(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Absolute longitudinal velocity [m/s] between ego vehicle and tracked object.

        @return: signal data
        """
        return self._getCemSignal("fVabsX")

    def vx_abs_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m/s] within the signal data of "vx_abs".

        @return: signal data
        """
        return self._getCemSignal("fVabsXStd")

    def vy(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative lateral velocity [m/s] between ego vehicle and tracked object.

        @return: signal data
        """

        return self._getCemSignal("fVrelY")

    def vy_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m/s] within the signal data of "vy".

        @return: signal data
        """
        return self._getCemSignal("fVrelYStd")

    def vy_abs(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Absolute lateral velocity [m/s] between ego vehicle and tracked object.

        @return: signal data
        """
        return self._getCemSignal("fVabsY")

    def vy_abs_std(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Standard deviation [m/s] within the signal data of "vy_abs".

        @return: signal data
        """
        return self._getCemSignal("fVabsYStd")

    # PAEBS CALCULATIONS

    def collision_prob(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Collision probability [-] calculated by PAEBS.

        @return: signal data
        """
        return self._getAoaSignal("collision_probability")

    def in_path(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate if tracked object is in the current predicted path of the ego velocity.

        @return: signal data
        """
        return self._getAoaSignal("obj_in_path")

    def ttc(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Time to Collision [s] calculated by forward-looking track selection.

        @return: signal data
        """
        return self._ttc

    def invttc(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Inverse Time to Collision [1/s].

        @return: signal data
        """
        return 1.0 / self.ttc

    def dist_pb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Predicted distance [m] covered by the ego vehicle until the start of the partial braking phase.

        @return: signal data
        """
        return self._partial_emergency_brake_distance

    def dist_eb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Predicted distance [m] covered by the ego vehicle until the start of the emergency braking phase.

        @return: signal data
        """
        return self._emergency_brake_distance

    def casc_dist(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Predicted distance [m] covered by the ego vehicle when going through the full PAEBS warning and braking cascade.

        @return: signal data
        """
        return self._full_cascade_brake_distance

    # CLASSIFICATION

    def obj_type(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Classified type [Enum] of the tracked object.

        Enum:
        1. POINT(0)
        2. CAR(1)
        3. TRUCK(2)
        4. PEDESTRIAN(3)
        5. MOTORCYCLE(4)
        6. BICYCLE(5)
        7. WIDE(6)
        8. UNCLASSIFIED(7)
        9. OTHER_VEHICLE(8)
        10. NOT_AVAILABLE(15) 

        @return: signal data
        """
        return self._classification

    def detected(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate that an object is detected at a certain point in time.

        @return: signal data
        """
        return self._detected

    def obj_src(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Type of source [Enum] that has tracked the object.

        Enum:
        1. UNKNOWN(0)
        2. RADAR_ONLY(1)
        3. CAMERA_ONLY(2)
        4. FUSED(3)
        5. NOT_AVAILABLE(255)

        @return: signal data
        """
        return self._obj_src

    def class_conf(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Probability [-] about the correct classification of the tracked object.

        @return: signal data
        """
        return self._getCemSignal("uiClassConfidence")

    def prob_exist(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Probability [-] that the tracked object is actually existing.

        @return: signal data
        """
        return self._getCemSignal("uiProbabilityOfExistence")

    def lane(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Associated lane [Enum] in which the tracked object is located from perspective of ego vehicle.

        Enum:
        1. UNKNOWN = 0,
        2. LANE_EGO = 1,
        3. LANE_LEFT = 2,
        4. LANE_RIGHT = 3,
        5. LANE_OUTSIDE_LEFT = 4,
        6. LANE_OUTSIDE_RIGHT = 5,
        7. LANE_LEFT_OUTSIDE_OF_ROAD_BORDERS = 6,
        8. LANE_RIGHT_OUTSIDE_OF_ROAD_BORDERS = 7,
        9. LANE_SNA = 255

        @return: signal data
        """
        return self._getCemSignal("eAssociatedLane")

    def lane_conf(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Probability [-] about the correct lane association of the tracked object.

        @return: signal data
        """
        return self._getCemSignal("uiAssociatedLaneConfidence")

    def motion_state(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Classified motion state [Enum] of the tracked object.

        Enum:
        1. NOT_DETECTED(0)
        2. MOVING(1)
        3. MOVING_STOPPED(2)
        4. STATIC(3)
        5. CROSSING(4)
        6. ONCOMING(5)
        7. DEFAULT(6)
        8. NOT_AVAILABLE(15)

        @return: signal data
        """
        return self._motion_state

    # STATES

    def system_state(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - PAEBS System State [Enum] transmitted to the HMI.

        Enum:
        1. IS_NOT_READY(0)
        2. TEMP_NOT_AVAILABLE(1)
        3. IS_DEACTIVATED_BY_DRIVER(2)
        4. IS_READY(3)
        5. DRIVER_OVERRIDES_SYSTEM(4)
        6. COLLISION_WARNING_ACTIVE(5)
        7. COLLISION_WARNING_WITH_BRAKING(6)
        8. EMERGENCY_BRAKING_ACTIVE(7)
        9. LIMITED_PERFORMANCE(8)
        10. ERROR_INDICATION(14)
        11. NOT_AVAILABLE(15)

        @return: signal data
        """
        return self._system_state

    def internal_state(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - PAEBS Internal State [Enum].

        Enum:
        1. None(0)
        2. NotReady(1)
        3. TemporarilyNotAvailable(2)
        4. DeactivatedByDriver(3)
        5. Ready(4)
        6. DriverOverride(5)
        7. LowSpeedBraking(6)
        8. Warning(7)
        9. PartialBraking(8)
        10. PartialBrakingIcb(9)
        11. PartialBrakingSsb(10)
        12. EmergencyBraking(11)
        13. EmergencyBrakingIcb(12)
        14. EmergencyBrakingSsb(13)
        15. BrakeHold(15)
        16. LowSpeedBrakingBrakeHold(16)
        17. Error(14)

        @return: signal data
        """
        return self._internal_state

    def warning_level(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - PAEBS warning level [Enum] transmitted to the HMI.

        Enum:
        1. WARNING_LEVEL_IDLE(0)
        2. WARNING_LEVEL_WARN(2)
        3. WARNING_LEVEL_PARTIAL(4)
        4. WARNING_LEVEL_LOW_SPEED(5)
        5. WARNING_LEVEL_ICB_SSB(6)
        6. WARNING_LEVEL_EMERGENCY(7)
        7. WARNING_LEVEL_DONT_CARE(15)

        @return: signal data
        """
        return self._warning_level

    def allow_brake_hold(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to apply brake hold functionality.

        @return: signal data
        """
        return self._allow_brake_hold

    def allow_eb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to entry emergency braking phase.

        @return: signal data
        """
        return self._allow_emergency

    def allow_icb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to apply in-crash braking.

        @return: signal data
        """
        return self._allow_icb

    def allow_lsb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to apply low speed braking.

        @return: signal data
        """
        return self._allow_low_speed_braking

    def allow_pb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to entry partial braking phase.
        

        @return: signal data
        """
        return self._allow_partial

    def allow_ssb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to apply standstill braking.

        @return: signal data
        """
        return self._allow_ssb

    def allow_cw(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to entry collision warning phase.

        @return: signal data
        """
        return self._allow_warning

    def cancel_eb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to cancel emergency braking phase.

        @return: signal data
        """
        return self._cancel_emergency

    def cancel_pb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to cancel partial braking phase.

        @return: signal data
        """
        return self._cancel_partial

    def cancel_cw(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate permission for PAEBS to cancel collision warning phase.

        @return: signal data
        """
        return self._cancel_warning

    def operation_lsb(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate readiness of low speed braking.

        @return: signal data
        """
        return self._low_speed_operational

    def operational(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate readiness of PAEBS.

        @return: signal data
        """
        return self._operational

    def override_active(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate the activation of a driver override.

        @return: signal data
        """
        return self._override_active

    def tr_state(self):
        # type: () -> numpy.array
        """
        Function calculates the defined Tracking State of the tracked object.

        @return: signal data
        """
        valid = ma.masked_array(~self._dx.mask, self._dx.mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._dx.mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    # PAEBS Defined Signals

    def expVelRed(self):
        # type: () -> numpy.array
        """
        Function calculates the expected speed reduction [m/s] until crash or standstill at any point in time
        based on a numerical calculation of the necessary braking cascade that the ego vehicle has to go through.
        Vehicle parameters are required for the prediction, which characterize the course of the cascade,
        as well as the current distance between the ego vehicle and the tracked object, the relative speed and
        the vehicle acceleration.
        The calculation algorithm is identical to that used in the PAEBS.

        @return: signal data
        """
        # Function calculates and returns the expected velocity reduction based on official paebs brake model.

        # Fetch paebs parameter values
        warning_time_min = self._paebs_warning_time_min[0]
        partial_braking_delay = self._paebs_partial_braking_delay[0]
        emergency_braking_delay = self._paebs_emergency_braking_delay[0]
        partial_braking_time_min = self._paebs_partial_braking_time_min[0]
        partial_braking_demand = self._paebs_partial_braking_demand[0]
        partial_braking_demand_ramp_start = self._paebs_partial_braking_demand_ramp_start[0]
        brake_demand_ramping_jerk = self._paebs_brake_demand_ramping_jerk[0]
        emergency_braking_demand_assumption = self._paebs_emergency_braking_demand_assumption[0]

        # Check Necessity of Calculation
        obj_valid = np.where(self.dx.data > 80, True, False)  # Calculation only for detected objects

        # Consider additionally valid values for velocity and distance
        new_mask = self.vx_ref.mask | self.dist_path.mask | obj_valid

        # Create new masked array
        vel_rel = self.vx_ref
        vel_rel.mask = new_mask

        # Instantiate PaebsBrakeModel class
        obj = paebs.PaebsBrakeModel(warning_time_min, partial_braking_delay, partial_braking_time_min,
                                    emergency_braking_delay,
                                    partial_braking_demand_ramp_start, partial_braking_demand,
                                    brake_demand_ramping_jerk, emergency_braking_demand_assumption)

        # Retrieve configurations for each phase
        config_warning = obj.getCascadeConfigWarning(self.ax)
        config_partial = obj.getCascadeConfigPartial(self.ax)
        config_emergency = obj.getCascadeConfigEmergency(self.ax)

        # Calculate results for each configuration
        result_warning, result_perc_warning = obj.calcExpectedVelocityReduction(config_warning, vel_rel, self.dist_path)
        result_partial, result_perc_partial = obj.calcExpectedVelocityReduction(config_partial, vel_rel, self.dist_path)
        result_emergency, result_perc_emergency = obj.calcExpectedVelocityReduction(config_emergency, vel_rel,
                                                                                    self.dist_path)

        return [(result_warning, result_perc_warning), (result_partial, result_perc_partial),
                (result_emergency, result_perc_emergency)]

    # OTHER
    def alive_intervals(self):
        # type: () -> numpy.array
        """


        @return: signal data
        """
        new = self.tr_state.valid & ~self.tr_state.hist
        validIntervals = cIntervalList.fromMask(self.time, self.tr_state.valid)
        newIntervals = cIntervalList.fromMask(self.time, new)
        alive_intervals = validIntervals.split(st for st, _ in newIntervals)
        return alive_intervals


class Calc(iCalc):
    """
    iInterface class that is registered by PyTCh and provides functionalities to assess and process measured signals
    and to create Paebs specific tracks.
    Binds the "calc_common_time-flc25" module as dependency to get a common timescale for all signals.
    """

    # Bind module for calculation of common time for FLC25 signals
    dep = ("calc_common_time-flc25",)

    def check(self):
        # type: () -> (list, numpy.ndarray)
        """
        Checks the validity of the signal groups that are defined outside this class as global variables and
        retrieves the common timescale from the module within the dependencies. It passes
        the results to the fill method.
        @return: Selected, valid signals group per object, the common timescale as numpy array.
        """
        modules = self.get_modules()
        source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        groups = []
        for sg in message_group:  # Global variable, defined outside
            sg_arbit = source.selectSignalGroupOrNone(sg)
            if sg_arbit is not None:
                groups.append(sg_arbit)
            else:
                raise KeyError('No valid signal group found for measurement.')
        return groups, commonTime

    def fill(self, groups, common_time):
        # type: (list, numpy.ndarray) -> PrimitiveCollection
        """
        Core function that will be called by module manager.
        Flc25PaebsDebugObjectTrack(s) are instantiated by common timescale, signal groups and invalidity mask
        and returned afterwards. In this case one selected signal group is representing one tracked object that
        will result in one Flc25PaebsDebugObjectTrack.
        All tracks (so far only one but more are thinkable) will be packed into a PrimitiveCollection
        together with the timescale array.

        @param groups: List of selected signal group that won arbitration.
        @param common_time:
        @return:
        """

        # Initialization
        paebs_tracks = PrimitiveCollection(common_time)

        for _id, group in enumerate(groups):
            # Create validity mask by longitudinal distance as criterion
            dx = group.get_value("dx", ScaleTime=common_time)
            invalid_mask = (dx == 300) | (np.isnan(dx))  # VALID_FLAG = False

            # Instantiate Tracks
            paebs_tracks[_id] = Flc25PaebsDebugObjectTrack(
                _id,
                common_time,
                self.source,
                group,
                invalid_mask,
                scaletime=common_time
            )

        return paebs_tracks


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\evaluation\pytch2_eval\rrec2mf4\mf4_eval\2025-02-18\mi5id5649__2025-02-18_13-15-53.mf4"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    tracks = manager_modules.calc("fill_flc25_paebs_debug@aebs.fill", manager)
    print(tracks)
