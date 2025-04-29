# -*- dataeval: init -*-

import numpy as np
import os
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measparser.PostmarkerJSONParser import parse_icon_data
from pyutils.cache_manager import get_modules_cache, store_modules_cache
import logging
from measproc.IntervalList import maskToIntervals

INVALID_TRACK_ID = -1
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")

logger = logging.getLogger("fillFLC25_TSR_SHORTLISTED")

conti_focused_sign_class_list = [
    274505,
    274506,
    274510,
    274511,
    274515,
    274516,
    274520,
    274521,
    274525,
    274526,
    274530,
    274531,
    274535,
    274536,
    274540,
    274541,
    274545,
    274546,
    274550,
    274551,
    274555,
    274556,
    274560,
    274561,
    274565,
    274566,
    274570,
    274571,
    274575,
    274576,
    274580,
    274581,
    274585,
    274586,
    274590,
    274591,
    274595,
    274596,
    274600,
    274601,
    274605,
    274606,
    274610,
    274611,
    274615,
    274616,
    274620,
    274621,
    274625,
    274626,
    274630,
    274631,
    274640,
    274641,
    278200,
    278201,
    278300,
    278301,
    282000,
    282001,
    310000,
    311000,
    325000,
    326000,
    251000,
    260000,
    250000,
    331000,
    336000,
    262000,
    264000,
    265000,
    276000,
    276001,
    277001,
    277000,
    280000,
    280001,
    281000,
    281001,
    222100,
    209200,
    267000,
    104812,
    104811,
    104030,
    105236,
    100100,
    100400,
    152000,
]


class cFill(iObjectFill):
    dep = "fill_flc25_tsr_raw_tracks"

    def check(self):
        modules = self.get_modules()
        lmk_tracks, supplementary_sign_details = modules.fill("fill_flc25_tsr_raw_tracks")
        return lmk_tracks, supplementary_sign_details

    def fill(self, tracks, supplementary_sign_details):
        objects = []
        hasImageData = True
        missing_sign_ids = []
        # Prepare data for TSR sign images, sign class, value, active_status etc.
        config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")
        # Identifier_to_icon_mapping is  mapping dictionary for images with respect to defined image identifier
        # Traffic sign data is used in table navigator
        traffic_sign_data_for_table, identifier_to_icon_mapping = parse_icon_data(
            config_file=config_file, seperator="="
        )
        import time

        logger.info("FLC25 TSR object retrieval has started, Please wait...")
        start_time = time.time()

        for id, track in tracks.iteritems():
            o = dict()
            invalid_mask = track.dx.mask
            o["traffic_sign_id"] = track.traffic_sign_id.astype(int)
            interval_list = maskToIntervals(~invalid_mask)

            conti_class_focused_filtered_mask = self.update_sign_class_focused_mask(
                interval_list, invalid_mask, o["traffic_sign_id"]
            )
            alive_intervals = maskToIntervals(~conti_class_focused_filtered_mask)
            o["id"] = np.where(conti_class_focused_filtered_mask, -1, id)
            o["valid"] = ~conti_class_focused_filtered_mask
            o["label"] = np.array(["FLC25_TSR_SHORTLISTED_%d_T" % (id) for id in o["id"]])
            track.dx.data[conti_class_focused_filtered_mask] = 0
            track.dy.data[conti_class_focused_filtered_mask] = 0
            o["dx"] = track.dx.data
            o["dy"] = track.dy.data
            o["type"] = np.ones(track.dx.shape, dtype="int")
            o["type"][:] = self.get_grouptype("FLC25_TSR_SHORTLISTED_STAT")
            init_intervals = [(st, st + 1) for st, end in alive_intervals]
            o["init"] = intervalsToMask(init_intervals, track.dx.size)
            color_mask = np.reshape(
                np.repeat(conti_class_focused_filtered_mask, 3), (-1, 3)
            )
            o["color"] = np.where(color_mask, [255, 69, 0], [255, 69, 0])

            o["image_mapping_data"] = identifier_to_icon_mapping

            o["universal_id"] = track.universal_id.astype(int)
            o[
                "traffic_existence_probability"
            ] = track.traffic_existence_probability.data
            o["traffic_sign_confidence"] = track.traffic_sign_confidence.data
            # [traffic_sign_data_for_table.get(str(item), item)[0] for idx, item in enumerate(o["traffic_sign_id"].data) if str(item) in traffic_sign_data_for_table]
            traffic_sign_data_for_table["--"] = "", "", "Not Applicable", "Inactive"
            (
                sign_class,
                sign_value,
                sign_picture,
                sign_status,
                missing_signs,
            ) = self.get_traffic_data(o["traffic_sign_id"], traffic_sign_data_for_table)
            o["sign_class"] = np.ma.masked_array(
                sign_class, mask=conti_class_focused_filtered_mask
            )
            o["sign_picture"] = np.ma.masked_array(
                sign_picture, mask=conti_class_focused_filtered_mask
            )
            o["sign_value"] = np.ma.masked_array(
                sign_value, mask=conti_class_focused_filtered_mask
            )
            o["sign_status"] = np.ma.masked_array(
                sign_status, mask=conti_class_focused_filtered_mask
            )
            o["sign_visibility_status"] = np.where(
                track.dx.data < 0, 0, 1
            )
            o["sign_visibility_status"][track.dx.mask] = 0
            o["traffic_sign_id"] = np.ma.masked_array(
                o["traffic_sign_id"], mask=conti_class_focused_filtered_mask
            )
            missing_sign_ids.extend(missing_signs)
            objects.append(o)

        elapsed = time.time() - start_time
        missing_sign_ids = set(missing_sign_ids)
        if len(missing_sign_ids) > 0:
            logger.warning("Missing sign class IDs: {}".format(missing_sign_ids))
        logger.info(
            "FLC25 TSR object retrieval has completed in " + str(elapsed) + " seconds"
        )
        return tracks.time, objects

    def update_sign_class_focused_mask(
        self, interval_list, conti_class_focused_filtered_mask, traffic_sign_ids
    ):
        # conti_focused_sign_class_list
        for external_interval in interval_list:
            unique_ids_in_interval = set(
                traffic_sign_ids[external_interval[0] : external_interval[1]]
            )
            for unique_id in unique_ids_in_interval:
                if unique_id not in conti_focused_sign_class_list:
                    internal_intervals = maskToIntervals(
                        traffic_sign_ids[external_interval[0] : external_interval[1]]
                        == unique_id
                    )
                    # traffic_sign_ids[interval[0] + internal_intervals[0]:interval[1] + internal_intervals[1]]
                    #
                    for internal_interval in internal_intervals:
                        conti_class_focused_filtered_mask[
                            external_interval[0]
                            + internal_interval[0] : external_interval[0]
                            + internal_interval[1]
                        ] = True

        return conti_class_focused_filtered_mask

    def get_traffic_data(self, traffic_sign_id, traffic_sign_data_for_table):
        traffic_data = {}
        sign_class = []
        sign_picture = []
        sign_value = []
        sign_status = []
        missing_sign_ids = []
        for item in traffic_sign_id:
            if str(item) in traffic_sign_data_for_table:
                sign_class.append(traffic_sign_data_for_table.get(str(item), item)[1])
                sign_picture.append(traffic_sign_data_for_table.get(str(item), item)[0])
                sign_value.append(traffic_sign_data_for_table.get(str(item), item)[2])
                sign_status.append(traffic_sign_data_for_table.get(str(item), item)[3])
            else:
                missing_sign_ids.append(item)
                # sign_icon_path, sign_class, value, active_status = "", "", "Not Applicable", "Inactive"
                sign_class.append("Missing Data")
                sign_picture.append("Missing Data")
                sign_value.append("Missing Data")
                sign_status.append("Missing Data")
        return sign_class, sign_value, sign_picture, sign_status, missing_sign_ids


# def parse_icon_data(config_file, seperator="="):
# 		identifier_to_icon_mapping = {}
# 		traffic_sign_data = {}
# 		with open(config_file) as fp:
# 				Lines = fp.readlines()
# 				for line in Lines:
# 						sign_icon_path, sign_class, value, active_status = "", "", "Not Applicable", "Inactive"
# 						icon_data_to_load, sign_id = line.split(seperator)
# 						icon_data_to_load, sign_id = icon_data_to_load.strip(), sign_id.strip()
# 						raw_data = icon_data_to_load.split("_")
# 						if raw_data[-1] == "ACTIVE":
# 								if raw_data[-2].isdigit():
# 										value = int(raw_data[-2])
# 										del raw_data[-1]
#
# 								del raw_data[-1]
# 								active_status = "Active"
# 						else:
# 								if raw_data[-1].isdigit():
# 										value = int(raw_data[-1])
# 										del raw_data[-1]
# 										active_status = "Inactive"
#
# 						sign_class = "_".join(raw_data)
# 						sign_icon_path = os.path.join(IMAGE_DIRECTORY, sign_class + "_Europe.png")
# 						if not os.path.exists(sign_icon_path):
# 								sign_icon_path = os.path.join(IMAGE_DIRECTORY, "NoImageAvailable_Europe.png")
# 						traffic_sign_data[sign_id] = (sign_icon_path, sign_class, value, active_status,)
# 						identifier_to_icon_mapping[sign_id] = sign_icon_path
#
# 		return traffic_sign_data, identifier_to_icon_mapping


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\__PythonToolchain\Meas\TSR\2021-07-22\mi5id787__2021-07-22_05-46-55.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    conti, objects = manager_modules.calc("fillFLC25_TSR@aebs.fill", manager)
    print(objects)
