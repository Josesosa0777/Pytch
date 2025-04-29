# -*- dataeval: init -*-
import numpy as np
import logging
import sys
from interface import iParameter, iView
import datavis
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import maskToIntervals

logger = logging.getLogger('view_paebs_object_data')


class cMyView(iView):
    dep = (
        'fill_flc25_paebs_debug@aebs.fill', 'calc_paebs_resim_output@aebs.fill'
    )
    optdep = ("fill_ground_truth_raw_tracks@aebs.fill")

    def init(self):
        self.ResimData = None
        self.FltsObjNo = None
        self.CommonTime = None

    def check(self):
        self.module_all = self.get_modules()
        paebs_object = self.module_all.fill('fill_flc25_paebs_debug@aebs.fill')
        resim_data_raw, time, total_mileage = self.modules.fill('calc_paebs_resim_output@aebs.fill')
        try:
            file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
        self.ResimData = self._getDataFromCsv(file_name, resim_data_raw)
        self.CommonTime = paebs_object.time

        return paebs_object

    def view(self, paebs_object):

        if 'fill_ground_truth_raw_tracks@aebs.fill' in self.passed_optdep:
            gt_track = self.module_all.fill("fill_ground_truth_raw_tracks@aebs.fill")
            paebs_object = paebs_object.rescale(gt_track["time"])
        else:
            logger.info("Ground truth data is not available")
            gt_track = {}

        t = self.CommonTime

        pn = datavis.cPlotNavigator(title="Object Data")
        masked_array = np.ones(t.shape, dtype=bool)

        ax = pn.addAxis(ylabel='x-Distance')
        delta_dx_array, masked_array = self.getResimSignal('obj_distance_x')

        # Add obj_distance_x
        pn.addSignal2Axis(ax, 'dx', t, paebs_object[0].dx, color='b', unit='m', ls='-')
        pn.addSignal2Axis(ax, 'dx resim', t, np.ma.array(delta_dx_array, mask=masked_array), unit='m')

        dx_max = paebs_object[0].dx + paebs_object[0].dx_std
        dx_min = paebs_object[0].dx - paebs_object[0].dx_std

        pn.addSignal2Axis(ax, 'dx_max', t, dx_max, ls="--", unit='m', color='#000000')
        pn.addSignal2Axis(ax, 'dx_min', t, dx_min, ls="--", unit='m', color='#000000')
        ax.fill_between(t, dx_max, dx_min, color="green", alpha="0.3")

        if "dx" in gt_track:
            pn.addSignal2Axis(ax, 'dx_gt', t, gt_track["dx"], color='r', unit='m', ls='-')

        ax = pn.addAxis(ylabel='y-Distance')

        delta_dy_array, masked_array = self.getResimSignal('obj_distance_y')

        # Add obj_distance_y
        pn.addSignal2Axis(ax, 'dy', t, paebs_object[0].dy, color='b', unit='m', ls='-')
        pn.addSignal2Axis(ax, 'dy resim', t, np.ma.array(delta_dy_array, mask=masked_array), unit='m')

        dy_max = paebs_object[0].dy + paebs_object[0].dy_std
        dy_min = paebs_object[0].dy - paebs_object[0].dy_std

        pn.addSignal2Axis(ax, 'dy_max', t, dy_max, ls="--", color='#000000')
        pn.addSignal2Axis(ax, 'dy_min', t, dy_min, ls="--", color='#000000')
        ax.fill_between(t, dy_max, dy_min, color="green", alpha="0.3")

        if "dy" in gt_track:
            pn.addSignal2Axis(ax, 'dy_gt', t, gt_track["dy"], color='r', unit='m', ls='-')

        if "vx" in gt_track:
            pn.addSignal2Axis(ax, 'vx_gt', t, gt_track["vx"], color='r', unit='m', ls='-')

        # Add obj_relative_velocity_x
        delta_vx_rel_array, masked_array = self.getResimSignal('obj_relative_velocity_x')

        ax = pn.addAxis(ylabel='Lon. Velocity')
        pn.addSignal2Axis(ax, 'vx_rel', t, paebs_object[0].vx, color='b', unit='m', ls='--')
        pn.addSignal2Axis(ax, 'vx_rel resim', t, np.ma.array(delta_vx_rel_array, mask=masked_array), unit='m')

        # Add obj_absolute_velocity_y
        delta_vy_abs_array, masked_array = self.getResimSignal('obj_absolute_velocity_y')
        ax = pn.addAxis(ylabel='Lat. Velocity')
        pn.addSignal2Axis(ax, 'vy_abs', t, paebs_object[0].vy_abs, color='b', unit='m', ls='-')
        pn.addSignal2Axis(ax, 'vy_abs resim', t, np.ma.array(delta_vy_abs_array, mask=masked_array), unit='m')

        vy_abs_max = paebs_object[0].vy + paebs_object[0].vy_std
        vy_abs_min = paebs_object[0].vy - paebs_object[0].vy_std

        pn.addSignal2Axis(ax, 'vy_abs_max', t, vy_abs_max, ls="--", color='#000000')
        pn.addSignal2Axis(ax, 'vy_abs_min', t, vy_abs_min, ls="--", color='#000000')
        ax.fill_between(t, vy_abs_max, vy_abs_min, color="green", alpha="0.3")

        if "vy_abs" in gt_track:
            pn.addSignal2Axis(ax, 'vy_abs_gt', t, gt_track["vy_abs"], color='r', unit='m', ls='-')

        delta_vy_rel_array, masked_array = self.getResimSignal('obj_relative_velocity_y')
        ax = pn.addAxis(ylabel='Pred. y-Distance')

        if "vy_abs" in gt_track:
            dy_ttc_gt = gt_track["dy"] + gt_track["vy_abs"] * np.clip(-1 * np.divide(gt_track["dx"], gt_track["vx"]), 0,
                                                                      20)
            pn.addSignal2Axis(ax, 'dy_ttc_gt', t, dy_ttc_gt, color='r', unit='m', ls='-')

        # Add obj_motion_state
        ylabel_text = "Obj. Motion State"
        mapping = {0: 'not detected', 1: 'moving', 2: 'moving stopped', 3: 'static', 4: 'crossing',
                   5: 'oncoming', 6: 'oncoming stopped', 7: 'default', 15: 'not available'}

        delta_motion_state_array, masked_array = self.getResimSignal('obj_motion_state', mapping)

        ax = pn.addAxis(ylabel=ylabel_text, yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        pn.addSignal2Axis(ax, ylabel_text, t, paebs_object[0].motion_state, unit='', color='b', ls='-')
        pn.addSignal2Axis(ax, 'Obj.Motion_State resim', t, np.ma.array(delta_motion_state_array, mask=masked_array))

        # Add obj_lane
        ylabel_text = 'Associated Lane'
        mapping = {0: 'Unknown', 1: 'Ego', 2: 'Left', 3: 'Right', 4: 'Left Outside', 5: 'Right Outside',
                   6: 'Outside of Border Left', 7: 'Outside of Border Right'}

        delta_lane_array, masked_array = self.getResimSignal('obj_lane', mapping)

        ax = pn.addTwinAxis(ax, ylabel=ylabel_text, yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                            color='g')
        pn.addSignal2Axis(ax, ylabel_text, t, paebs_object[0].lane, unit='', color='g', ls='-')
        pn.addSignal2Axis(ax, 'Associated Lane resim', t,
                          np.ma.array(delta_lane_array, mask=masked_array))

        self.sync.addClient(pn)
        return

    @staticmethod
    def _getDataFromCsv(file_name, paebs_resim_data):
        # type: (str, list) -> list
        """
        Extracts the resimulation results from parsed .csv data that are matching the measurement file
        that is currently loaded.

        :param file_name: File name of the currently loaded measurement file.
        :param paebs_resim_data: Raw resimulation output data parsed from .csv file.
        :return: Matching resimulation results.
        """

        valid_data = []

        for files in paebs_resim_data:
            name = ""
            if 'camera' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_camera')[0].replace('_at_', '_')
            elif 'radar' in files['Measurement File']:
                name = files['Measurement File'].replace('.', '-').split('_radar')[0].replace('_at_', '_')
            if name == file_name:
                valid_data.append(files)
        return valid_data

    def getResimSignal(self, signal_name, mapping={}):
        # type: (str, dict) -> (np.ndarray, np.ndarray)
        """
        Method retrieves the PAEBS resimulation result for a specified signal and returns it as array with constant
        values. The shape of the array is derived from the common time array for this class.
        The number of occupied elements with the constant value is hard coded in here.
        Background: The result of the resimulation provides only one value for one event. For more user-friendly
        illustration in diagrams, this value is represented as a constant over a limited time interval.
        Signals or results that apply to several FLTS objects must be assigned and selected
        to the actually relevant CEM.
        This is done by requiring such signals to contain a fixed Python placeholder when their name is
        passed as an input argument.
        The actually relevant FLTS object can be identified based on the corresponding CEM object number,
        which is available for each FLTS object in the resimulation results.
        The number of this FLTS object is inserted in the placeholder within the signal name and the
        appropriate resimulation result is obtained using this completed signal name.
        In addition, a map can be transferred, which maps integer values to associated string values
        in the case of the Enum data type. This map is inverted in order to assign the string values returned by
        the resimulation to integer values, which can only be displayed in diagrams.

        :param signal_name: Name of the signal in the resimulation output .csv file, including placeholder for FLTS object dependant signals.
        :param mapping: Integer to Enum string map.
        :return: Result values, Mask values.
        """

        mask_array = np.ones(self.CommonTime.shape, dtype=bool)
        data_array = np.zeros(self.CommonTime.shape, dtype=float)

        if mapping:
            inv_map = {v.upper(): k for k, v in mapping.iteritems()}
        else:
            inv_map = {}

        for item in self.ResimData:
            interval = self._getIndex((long(item["Start Time Abs"]), long(item["End Time Abs"]),), self.CommonTime)
            if '{flts_id}' in signal_name:
                signal_name = signal_name.format(flts_id=self._selectFltsObject(item))
            value_raw = item[signal_name]
            if mapping:
                value = value_raw.replace('_', ' ')
                value = inv_map[value]
            else:
                value = float(value_raw)
            data_array[(interval[0] - 10):(interval[0] + 10)] = value
            mask_array[(interval[0] - 10):(interval[0] + 10)] = False

        return data_array, mask_array

    @staticmethod
    def _selectFltsObject(resim_event_result):
        # type: (dict) -> int
        """
        Method finds the number/index of the FLTS object that references the actually relevant CEM object.
        For this purpose, all values for the "paebs_objects_{flts_id}_id" signal are compared with the ID
        of the relevant CEM object (signal: "obj_id") for all FLTS objects (hard-coded maximum number)
        and the number of the matching FLTS object is returned.

        :param resim_event_result: Resimulation result for a specific event.
        :return: FLTS object number
        """

        FLTS_MAX = 3
        cem_obj_id = int(resim_event_result['obj_id'])
        for obj_no in range(FLTS_MAX):
            flts_id_name = 'paebs_objects_{flts_id}_id'.format(flts_id=obj_no)
            flts_id = resim_event_result[flts_id_name]
            if cem_obj_id == int(flts_id):
                return obj_no
        return 0

    @staticmethod
    def _getIndex(interval, time):
        # type: (tuple, np.ndarray) -> (int, int)
        """
        Method evaluates the index in a time array that corresponds to the start and end time of
        a PAEBS event interval, expressed in absolute time values.

        :param interval: Start and End time of an PAEBS event interval
        :param time: Time array.
        :return: Start and end index.
        """

        st_time, ed_time = interval
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        start_index = (np.abs(time - st_time)).argmin()
        end_index = (np.abs(time - ed_time)).argmin()
        if start_index == end_index:
            end_index += 1
        return start_index, end_index
