# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import logging
import numpy.ma as ma
import numpy as np
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from measproc import cIntervalList
from measproc.IntervalList import maskToIntervals
from metatrack import (
    TrackingState,
)
from primitives.bases import PrimitiveCollection
import numpy

logger = logging.getLogger('fill_flc25_paebs_lausch')

sg = [
    {
        'relevant_obj_id': ('AEBS_MRO1', 'RelevantObject_ID1_sA0'),
        'internal_state': ('Lausch_PAEBS_0', 'paebs_internal_state_sE8'),
        'emergency_brake_distance': ('Lausch_PAEBS_0', 'paebs_emerg_brake_dist_sE8'),
        'override_active': ('Lausch_PAEBS_0', 'paebs_override_active_sE8'),
        'full_cascade_brake_distance': ('Lausch_PAEBS_0', 'paebs_full_casc_brake_dist_sE8'),
        'collision_probability': ('Lausch_PAEBS_0', 'paebs_obj_collision_probability_sE8'),
        'partial_emergency_brake_distance': ('Lausch_PAEBS_0', 'paebs_partial_emerg_brake_dist_sE8'),
        'ttc': ('Lausch_PAEBS_1', 'paebs_obj_ttc_sE8'),
        'low_speed_operational': ('Lausch_PAEBS_1', 'paebs_low_speed_operational_sE8'),
        'allow_low_speed_braking': ('Lausch_PAEBS_1', 'paebs_allow_low_speed_braking_sE8'),
        'allow_partial': ('Lausch_PAEBS_1', 'paebs_allow_partial_sE8'),
        'allow_warning': ('Lausch_PAEBS_1', 'paebs_allow_warning_sE8'),
        'cancel_emergency': ('Lausch_PAEBS_1', 'paebs_cancel_emergency_sE8'),
        'allow_ssb': ('Lausch_PAEBS_1', 'paebs_allow_ssb_sE8'),
        'allow_icb': ('Lausch_PAEBS_1', 'paebs_allow_icb_sE8'),
        'operational': ('Lausch_PAEBS_1', 'paebs_operational_sE8'),
        'obj_in_path': ('Lausch_PAEBS_1', 'paebs_obj_in_path_sE8'),
        'dist_along_ego_path': ('Lausch_PAEBS_1', 'paebs_obj_dist_along_ego_path_sE8'),
        'cancel_partial': ('Lausch_PAEBS_1', 'paebs_cancel_partial_sE8'),
        'cancel_warning': ('Lausch_PAEBS_1', 'paebs_cancel_warning_sE8'),
        'lon_veloc_rel_ref': ('Lausch_PAEBS_1', 'paebs_obj_lon_veloc_rel_ref_sE8'),
        'allow_emergency': ('Lausch_PAEBS_1', 'paebs_allow_emergency_sE8'),
        'eAssociatedLane_8': ('Lausch_FLTS_8', 'flts_lane_sE8'),
        'fVrelY_8': ('Lausch_FLTS_8', 'flts_vy_rel_sE8'),
        'motion_state_8': ('Lausch_FLTS_8', 'flts_motion_state_sE8'),
        'dx_8': ('Lausch_FLTS_8', 'flts_dx_sE8'),
        'vx_rel_8': ('Lausch_FLTS_8', 'flts_vx_rel_sE8'),
        'life_time_8': ('Lausch_FLTS_8', 'flts_life_time_sE8'),
        'fDistY_8': ('Lausch_FLTS_8', 'flts_dy_sE8'),
        'obj_src_8': ('Lausch_FLTS_8', 'flts_source_sE8'),
        'flts_id_8': ('Lausch_FLTS_8', 'flts_id_sE8'),
        'object_flags_value_9': ('Lausch_FLTS_9', 'flts_object_flags_sE8'),
        'paebs_bitfield_value_9': ('Lausch_FLTS_9', 'flts_paebs_bitfield_sE8'),
        'eAssociatedLane_10': ('Lausch_FLTS_10', 'flts_lane_sE8'),
        'fVrelY_10': ('Lausch_FLTS_10', 'flts_vy_rel_sE8'),
        'motion_state_10': ('Lausch_FLTS_10', 'flts_motion_state_sE8'),
        'dx_10': ('Lausch_FLTS_10', 'flts_dx_sE8'),
        'vx_rel_10': ('Lausch_FLTS_10', 'flts_vx_rel_sE8'),
        'life_time_10': ('Lausch_FLTS_10', 'flts_life_time_sE8'),
        'fDistY_10': ('Lausch_FLTS_10', 'flts_dy_sE8'),
        'obj_src_10': ('Lausch_FLTS_10', 'flts_source_sE8'),
        'flts_id_10': ('Lausch_FLTS_10', 'flts_id_sE8'),
        'object_flags_value_11': ('Lausch_FLTS_11', 'flts_object_flags_sE8'),
        'paebs_bitfield_value_11': ('Lausch_FLTS_11', 'flts_paebs_bitfield_sE8'),
    },
    {
        'relevant_obj_id': ('AEBS_MRO1', 'RelevantObject_ID1_sA0'),
        'internal_state': ('Lausch_PAEBS_0', 'paebs_internal_state'),
        'emergency_brake_distance': ('Lausch_PAEBS_0', 'paebs_emerg_brake_dist'),
        'override_active': ('Lausch_PAEBS_0', 'paebs_override_active'),
        'full_cascade_brake_distance': ('Lausch_PAEBS_0', 'paebs_full_casc_brake_dist'),
        'collision_probability': ('Lausch_PAEBS_0', 'paebs_obj_collision_probability'),
        'partial_emergency_brake_distance': ('Lausch_PAEBS_0', 'paebs_partial_emerg_brake_dist'),
        'ttc': ('Lausch_PAEBS_1', 'paebs_obj_ttc'),
        'low_speed_operational': ('Lausch_PAEBS_1', 'paebs_low_speed_operational'),
        'allow_low_speed_braking': ('Lausch_PAEBS_1', 'paebs_allow_low_speed_braking'),
        'allow_partial': ('Lausch_PAEBS_1', 'paebs_allow_partial'),
        'allow_warning': ('Lausch_PAEBS_1', 'paebs_allow_warning'),
        'cancel_emergency': ('Lausch_PAEBS_1', 'paebs_cancel_emergency'),
        'allow_ssb': ('Lausch_PAEBS_1', 'paebs_allow_ssb'),
        'allow_icb': ('Lausch_PAEBS_1', 'paebs_allow_icb'),
        'operational': ('Lausch_PAEBS_1', 'paebs_operational'),
        'obj_in_path': ('Lausch_PAEBS_1', 'paebs_obj_in_path'),
        'dist_along_ego_path': ('Lausch_PAEBS_1', 'paebs_obj_dist_along_ego_path'),
        'cancel_partial': ('Lausch_PAEBS_1', 'paebs_cancel_partial'),
        'cancel_warning': ('Lausch_PAEBS_1', 'paebs_cancel_warning'),
        'lon_veloc_rel_ref': ('Lausch_PAEBS_1', 'paebs_obj_lon_veloc_rel_ref'),
        'allow_emergency': ('Lausch_PAEBS_1', 'paebs_allow_emergency'),
        'eAssociatedLane_8': ('Lausch_FLTS_8', 'flts_lane'),
        'fVrelY_8': ('Lausch_FLTS_8', 'flts_vy_rel'),
        'motion_state_8': ('Lausch_FLTS_8', 'flts_motion_state'),
        'dx_8': ('Lausch_FLTS_8', 'flts_dx'),
        'vx_rel_8': ('Lausch_FLTS_8', 'flts_vx_rel'),
        'life_time_8': ('Lausch_FLTS_8', 'flts_life_time'),
        'fDistY_8': ('Lausch_FLTS_8', 'flts_dy'),
        'obj_src_8': ('Lausch_FLTS_8', 'flts_source'),
        'flts_id_8': ('Lausch_FLTS_8', 'flts_id'),
        'object_flags_value_9': ('Lausch_FLTS_9', 'flts_object_flags'),
        'paebs_bitfield_value_9': ('Lausch_FLTS_9', 'flts_paebs_bitfield'),
        'eAssociatedLane_10': ('Lausch_FLTS_10', 'flts_lane'),
        'fVrelY_10': ('Lausch_FLTS_10', 'flts_vy_rel'),
        'motion_state_10': ('Lausch_FLTS_10', 'flts_motion_state'),
        'dx_10': ('Lausch_FLTS_10', 'flts_dx'),
        'vx_rel_10': ('Lausch_FLTS_10', 'flts_vx_rel'),
        'life_time_10': ('Lausch_FLTS_10', 'flts_life_time'),
        'fDistY_10': ('Lausch_FLTS_10', 'flts_dy'),
        'obj_src_10': ('Lausch_FLTS_10', 'flts_source'),
        'flts_id_10': ('Lausch_FLTS_10', 'flts_id'),
        'object_flags_value_11': ('Lausch_FLTS_11', 'flts_object_flags'),
        'paebs_bitfield_value_11': ('Lausch_FLTS_11', 'flts_paebs_bitfield'),
    }
]


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

    _attribs = tuple(sg[0].keys())  # Names of the attributes that shall grant access to signal data, must be
    # identical with the shortnames of the message/signal group
    _special_methods = 'alive_intervals'  # Protected method names that can't be used twice per signal group definition
    _reserved_names = ObjectFromMessage._reserved_names + ('get_selection_timestamp',)

    def __init__(self, obj_id, time, source, group, invalid_mask, scaletime=None):
        # type: (int, numpy.array, object, list, numpy.array, numpy.array) -> None
        """
        Constructor of one track.

        @param obj_id: Index of instantiated track/tracked object
        @param time: time array that shall be base of all signal data
        @param source: cSource Source manager
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

    def _getFltsSignal(self, signal_short_name):
        # type: (str) -> numpy.array
        """
        Abstract and reusable Method that assembles the required signal data at any discrete point in time
        from the corresponding signal data of all available X objects, depending on which X object currently
        represents the relevant tracked object.

        X: FLTS objects.

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

        @param signal_short_name: Base shortname of the requested signal.
        @return: Assembled signal data, coming from multiple objects of the same name.
        """

        # Define potential SignalNames
        signal_short_names = []
        signal_short_names.append((signal_short_name, 'flts_id_8'))  # flts object 8 or 9
        index = int(signal_short_name[-1]) + 2  # flts object 10 or 11
        signal_short_names.append((signal_short_name[:-1] + '{}'.format(index), 'flts_id_10'))

        # Create array filled with zeros from main value dx
        res_sgn = np.zeros_like(self.internal_state)

        # Create Mask indicating valid Cem Object ID
        res_mask = np.where(self.object_index.data < 100, True, False)

        # Initiate Array representing Indices
        indices = np.arange(len(self.object_index.data), dtype=np.int32)

        # Reduce Array to valid Indices
        indices = indices[res_mask]

        for index in indices:

            # Get current Cem Object ID
            id_value = self.object_index.data[index]

            # Identify suitable FLTS Object bearing same ID
            for sgn in signal_short_names:

                cmd_sgn_raw = "self._" + sgn[0] + ".data[%d]"
                cmd_obj_id_raw = "self._" + sgn[1] + ".data[%d]"

                obj_id_ref = eval(cmd_obj_id_raw % index)

                if obj_id_ref == id_value:
                    dtype = eval("self._" + sgn[0] + ".dtype")
                    res_sgn = res_sgn.astype(dtype)
                    res_sgn.data[index] = eval(cmd_sgn_raw % index)
                    break

        return res_sgn

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
        return self._relevant_obj_id

    def life_time(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Lifetime of the tracked CEM object whose signals are base of the scalar paebs debug signals.

        @return: signal data
        """
        return self._getFltsSignal('life_time_8')

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
        return self._getFltsSignal('paebs_bitfield_value_9')

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
        return self._getFltsSignal('object_flags_value_9')

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
        return self._getFltsSignal('dx_8')

    def dist_path(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Longitudinal distance [m] between vehicle and tracked object along the predicted ego vehicle path.

        @return: signal data
        """
        return self._dist_along_ego_path

    def dy(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Lateral distance [m] between ego vehicle and tracked object.

        Mandatory for Tracknav!

        @return: signal data
        """
        return self._getFltsSignal('fDistY_8')

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
    def vx(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative longitudinal velocity [m/s] between ego vehicle and tracked object.

        Mandatory for Tracknav!

        @return: signal data
        """
        return self._getFltsSignal('vx_rel_8')

    def vx_ref(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative longitudinal velocity [m/s] between ego vehicle and tracked object in referenced coordinate system.

        @return: signal data
        """
        return self._lon_veloc_rel_ref

    def vy(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Relative lateral velocity [m/s] between ego vehicle and tracked object.

        @return: signal data
        """

        return self._getFltsSignal('fVrelY_8')

    # PAEBS CALCULATIONS

    def collision_prob(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Collision probability [-] calculated by PAEBS.

        @return: signal data
        """
        return self._collision_probability

    def in_path(self):
        # type: () -> numpy.array
        """
        Grants access to the private attribute (name defined by the short names of the signal groups)
        that carries the data of the following signal:
        - Flag to indicate if tracked object is in the current predicted path of the ego velocity.

        @return: signal data
        """
        return self._obj_in_path

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
        return self._getFltsSignal('obj_src_8')

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
        return self._getFltsSignal('eAssociatedLane_8')

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
        return self._getFltsSignal('motion_state_8')

    # STATES

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
        valid = ma.masked_array(~self._invalid_mask, self._invalid_mask)
        meas = np.ones_like(valid)
        hist = np.ones_like(valid)
        for st, end in maskToIntervals(~self._invalid_mask):
            if st != 0:
                hist[st] = False
        return TrackingState(valid=valid, measured=meas, hist=hist)

    # PAEBS Defined Signals

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
            obj_id = group.get_value("relevant_obj_id", ScaleTime=common_time)
            invalid_mask = (obj_id == 255) | (np.isnan(obj_id))  # VALID_FLAG = False

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

    meas_path = r"C:\KBData\Measurement\paebs_debug_pytch\working_files\mi5id787__2022-03-17_12-43-47.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    tracks = manager_modules.calc("fill_flc25_paebs_lausch@aebs.fill", manager)
    print(tracks)
