# -*- dataeval: init -*-
import logging
import sys

import numpy as np

import datavis
from interface import iParameter, iView
from measparser.signalproc import rescale
from measparser.filenameparser import FileNameParser
from measproc.IntervalList import maskToIntervals

logger = logging.getLogger('')

class cMyView(iView):
    dep = 'fill_flc25_paebs_debug@aebs.fill', 'calc_paebs_resim_output@aebs.fill'

    def init(self):
        self.ResimData = None
        self.FltsObjNo = None
        self.CommonTime = None

    def check(self):
        modules = self.get_modules()
        paebs_objects_data = modules.fill('fill_flc25_paebs_debug@aebs.fill')
        resim_data_raw, time, total_mileage = self.modules.fill('calc_paebs_resim_output@aebs.fill')
        try:
            file_name = FileNameParser(self.source.BaseName).date_underscore
        except:
            file_name = self.source.BaseName.replace('.', '-').replace('_at_', '_').rsplit('_', 2)[0]
        self.ResimData = self._getDataFromCsv(file_name, resim_data_raw)
        self.CommonTime = paebs_objects_data.time

        return paebs_objects_data

    def view(self, paebs_objects_data):

        t = self.CommonTime

        pn = datavis.cPlotNavigator(title="Debug Data")
        ax = pn.addAxis(ylabel='Distance')
        delta_lon_dist_array, masked_array = self.getResimSignal('paebs_objects_{flts_id}_dist_along_ego_path')
        pn.addSignal2Axis(ax, 'Cascade Distance', t, paebs_objects_data[0].casc_dist, color='r', unit='m', ls='-')

        # Add paebs_situation_dist_lon
        pn.addSignal2Axis(ax, 'Lon. Distance', t, paebs_objects_data[0].dist_path, color='b', unit='m', ls='-')
        pn.addSignal2Axis(ax, 'Lon. Distance resim', t, np.ma.array(delta_lon_dist_array, mask=masked_array), unit='m')

        ax = pn.addTwinAxis(ax, ylabel='Time', color='g')
        delta_ttc_array, masked_array = self.getResimSignal('paebs_objects_{flts_id}_ttc')

        # Add paebs_situation_ttc
        pn.addSignal2Axis(ax, 'TTC', t, paebs_objects_data[0].ttc, color='g', unit='s', ls='-')
        pn.addSignal2Axis(ax, 'TTC resim', t, np.ma.array(delta_ttc_array, mask=masked_array), unit='s')

        ax = pn.addAxis(ylabel='Probability')
        delta_data_array, masked_array = self.getResimSignal('paebs_objects_{flts_id}_collision_probability')

        pn.addSignal2Axis(ax, 'Collision Probability', t, paebs_objects_data[0].collision_prob * 100, color='b',
                          unit='%', ls='-')
        pn.addSignal2Axis(ax, 'Collision_probability_resim', t, np.ma.array(delta_data_array * 100, mask=masked_array),
                          unit='%')

        mapping = {0: 'False', 1: 'True'}
        ax = pn.addAxis(ylabel='Trigger Status', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        delta_in_path_array, masked_array = self.getResimSignal('paebs_objects_{flts_id}_obj_in_path')

        # Add paebs_situation_in_path
        pn.addSignal2Axis(ax, "in Path", t, paebs_objects_data[0].in_path, unit='', color='r', ls='-')
        pn.addSignal2Axis(ax, 'in Path resim', t, np.ma.array(delta_in_path_array, mask=masked_array))

        mapping = {0: 'None', 1: 'Not Ready', 2: 'Temp. NA', 3: 'Driver Deact.', 4: 'Ready', 5: 'Driver Ovr',
                   6: 'Warning', 7: 'PB', 8: 'PB-ICB',
                   9: 'PB-SSB', 10: 'EB', 11: 'EB-ICB', 12: 'EB-SSB', 13: 'Error'}

        ax = pn.addAxis(ylabel='Internal State', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        pn.addSignal2Axis(ax, "Internal State", t, paebs_objects_data[0].internal_state, unit='', color='b', ls='-')

        mapping = {0: 'False', 1: 'True'}
        ax = pn.addTwinAxis(ax, ylabel='Status', yticks=mapping, ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
                            color='g')

        pn.addSignal2Axis(ax, 'Override active', t, paebs_objects_data[0].override_active, color='r', ls='-')
        pn.addSignal2Axis(ax, 'Operational', t, paebs_objects_data[0].operational, color='g', ls='-')

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
                flts_obj_id = self._selectFltsObject(item)
                if flts_obj_id is not None:
                    signal_name = signal_name.format(flts_id=flts_obj_id)
                else:
                    signal_name = signal_name.format(flts_id=0)
                    logger.error('No FLTS object ID retrievable for measurement: {}'.format(self.source.BaseName))
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
