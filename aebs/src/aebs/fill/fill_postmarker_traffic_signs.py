# -*- dataeval: init -*-

from interface import iCalc
import numpy as np
import os

# from fillFLC25_TSR import parse_icon_data
from measparser.PostmarkerJSONParser import parse_icon_data
from collections import OrderedDict
import logging
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")


class cFill(iCalc):
    dep = (
        "calc_postmarker_json_data",
        "calc_common_time-tsrresim",
    )
    optdep = ("calc_resim_deviation")

    def check(self):
        pass

    def fill(self):
        self.module_all = self.get_modules()
        meta_info_reports, traffic_sign_report = self.module_all.fill(self.dep[0])
        self.common_time = self.module_all.fill(self.dep[1])

        resim_deviation = 0
        if 'calc_resim_deviation' in self.passed_optdep:
            resim_deviation, _ = self.module_all.fill('calc_resim_deviation')
        else:
            logging.warning(
                    "'calc_resim_deviation' failed dependency.. Please check signal groups if it is resim measurement.")
        if len(traffic_sign_report) == 0:
            raise ValueError(
                "Missing traffic sign data or could not extract data from postmarker json format"
            )
        config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")
        traffic_sign_data_for_table, identifier_to_icon_mapping = parse_icon_data(
            config_file=config_file, seperator="="
        )

        """
        Single signals: 
            LmkGenLandmarkList
        Buffer signals[0-50]: 
            sign_class_id
            sign_class
            sign_icon_path
            sign_value
            sign_status
            is_traffic_sign_detected
            Uid : 255 being invalid default otherwise 1
        """
        signals = {}
        groups = []
        # Extract possible signals from both structures
        # Fill up signals dictionary, referring common time nd array
        for buffer_id in range(50):  # As there are 50 tracks for conti TSR
            buffer = {}
            buffer["uid"] = np.zeros(self.common_time.shape, dtype=int)
            buffer["uid"][:] = 255
            buffer["is_sign_detected"] = np.zeros(self.common_time.shape, dtype=bool)
            buffer["sign_class_id"] = np.zeros(self.common_time.shape, dtype=int)
            buffer["sign_class"] = np.empty(self.common_time.shape, dtype=object)
            buffer["sign_icon_path"] = np.empty(self.common_time.shape, dtype=object)
            buffer["sign_value"] = np.empty(self.common_time.shape, dtype=object)
            buffer["sign_value_for_can"] = np.empty(self.common_time.shape, dtype=object)
            buffer["sign_status"] = np.empty(self.common_time.shape, dtype=object)
            buffer["sign_quantity"] = np.zeros(self.common_time.shape, dtype=int)
            buffer["weather_condition"] = np.zeros(self.common_time.shape, dtype='S20')
            buffer["time_condition"] = np.zeros(self.common_time.shape, dtype='S20')
            groups.append(buffer)

        buffer_id = 0
        for traffic_obj in traffic_sign_report:
            st_idx, ed_idx = self.get_index(traffic_obj["delta_reference"], resim_deviation)
            buffer_id = self.get_buffer_id(0, groups, st_idx)

            groups[buffer_id]["uid"][st_idx] = 1
            print("group:",groups[buffer_id])
            groups[buffer_id]["is_sign_detected"][st_idx] = True
            groups[buffer_id]["sign_class_id"][st_idx] = int(str(traffic_obj["conti_sign_class"]))
            try:
                sign_path, class_name, value, status = traffic_sign_data_for_table[
                    traffic_obj["conti_sign_class"]
                ]
            except:
                sign_path, class_name, value, status = (
                    "Missing data",
                    "Missing data",
                    "Missing data",
                    "Missing data",
                )
            status = False
            if traffic_obj["status"] == 'true':
                status=True

            groups[buffer_id]["sign_class"][st_idx] = class_name
            groups[buffer_id]["sign_icon_path"][st_idx] = sign_path
            groups[buffer_id]["sign_value"][st_idx] = value
            try:
                groups[buffer_id]["sign_value_for_can"][st_idx] = float(value)
            except ValueError as e:
                groups[buffer_id]["sign_value_for_can"][st_idx] = None
            groups[buffer_id]["sign_status"][st_idx] = status
            groups[buffer_id]["sign_quantity"][st_idx] = traffic_obj["quantity"]
            groups[buffer_id]["weather_condition"][st_idx] = str(traffic_obj['weather_condition'])
            groups[buffer_id]["time_condition"][st_idx] = str(traffic_obj['time_condition'])

        lmk_tracks = []
        for _id, group in enumerate(groups):
            uid = group["uid"]
            invalid_mask = uid == 255

            if np.all(invalid_mask):
                continue
            lmk_track = {}
            lmk_track["sign_class_id"] = np.ma.array(
                group["sign_class_id"], mask=invalid_mask
            )
            lmk_track["is_sign_detected"] = np.ma.array(
                group["is_sign_detected"], mask=invalid_mask
            )
            lmk_track["valid"] = np.ma.array(
                group["is_sign_detected"], mask=invalid_mask
            )
            lmk_track["sign_class"] = np.ma.array(
                group["sign_class"], mask=invalid_mask
            )
            lmk_track["sign_icon_path"] = np.ma.array(
                group["sign_icon_path"], mask=invalid_mask
            )
            lmk_track["sign_value"] = np.ma.array(
                group["sign_value"], mask=invalid_mask
            )
            lmk_track["sign_value_for_can"] = np.ma.array(
                group["sign_value_for_can"], mask=invalid_mask
            )
            lmk_track["sign_status"] = np.ma.array(
                group["sign_status"], mask=invalid_mask
            )
            lmk_track["sign_quantity"] = np.ma.array(
                group["sign_quantity"], mask=invalid_mask
            )
            lmk_track['weather_condition'] = np.ma.array(
                group['weather_condition'], mask=invalid_mask
            )
            lmk_track['time_condition'] = np.ma.array(
                group['time_condition'], mask=invalid_mask
            )
            lmk_track["uid"] = np.ma.array(group["uid"], mask=invalid_mask)
            lmk_tracks.append(lmk_track)

        return self.common_time, lmk_tracks, resim_deviation, traffic_sign_report

    def get_buffer_id(self, buffer_id, groups, st_idx):
        if groups[buffer_id]["uid"][st_idx] != 255:
            buffer_id = self.get_buffer_id(buffer_id + 1, groups, st_idx)

        return buffer_id

    def get_index(self, delta_reference, resim_deviation):
        delta_t = delta_reference / 1000000.0
        st_time = self.common_time[0] + delta_t - resim_deviation
        st_index = max(self.common_time.searchsorted(st_time, side="right") - 1, 0)

        return st_index, st_index

if __name__ == "__main__":
    from config.Config import init_dataeval

    # meas_path = r"D:\TGP\TSR_test\resim_rrec\mi5id1703__2021-07-22_05-56-57.h5"
    meas_path = r"C:\KBData\Measurement\TSR_evaluation\data\weather_condition_check\2021-10-14\mi5id787__2021-10-14_15-43-55_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    tracks = manager_modules.calc("fill_postmarker_traffic_signs@aebs.fill", manager)
    print(tracks)
