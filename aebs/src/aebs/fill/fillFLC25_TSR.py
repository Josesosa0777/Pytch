# -*- dataeval: init -*-

import numpy as np
import os
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from measparser.PostmarkerJSONParser import parse_icon_data
from pyutils.cache_manager import get_modules_cache, store_modules_cache
import logging

INVALID_TRACK_ID = -1
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")
logger = logging.getLogger("fillFLC25_TSR")


class cFill(iObjectFill):
    dep = "fill_flc25_tsr_raw_tracks"
    optdep = ("calc_resim_deviation")

    def check(self):
        return

    def fill(self):
        self.module_all = self.get_modules()
        tracks, _ = self.module_all.fill("fill_flc25_tsr_raw_tracks")
        if 'calc_resim_deviation' in self.passed_optdep:
            resim_deviation, indexes = self.module_all.fill("calc_resim_deviation")
        else:
            indexes = 0
            logging.warning(
                    "'calc_resim_deviation' failed dependency.. Please check signal groups if it is resim measurement.")
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
            o["id"] = np.where(track.universal_id.mask, -1, id)
            o["valid"] = ~track.universal_id.mask
            o["label"] = np.array(["FLC25_TSR_%d_T" % (id) for id in o["id"]])
            track.dx.data[track.dx.mask] = 0
            track.dy.data[track.dy.mask] = 0
            o["dx"] = track.dx.data
            o["dy"] = track.dy.data
            o["dz"] = track.dz.data
            o["type"] = np.ones(track.dx.shape, dtype="int")
            o["type"][:] = self.get_grouptype("FLC25_TSR_STAT")
            init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
            o["init"] = intervalsToMask(init_intervals, track.dx.size)
            color_mask = np.reshape(np.repeat(track.universal_id.mask, 3), (-1, 3))
            o["color"] = np.where(color_mask, [255, 69, 0], [255, 69, 0])

            o["image_mapping_data"] = identifier_to_icon_mapping
            o["traffic_sign_id"] = track.traffic_sign_id.astype(int)
            o["etrack"] = track.etrackCharacteristics.astype(int)
            o["etrackBinary"] = track.etrackBinary
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
            o["sign_class"] = np.ma.masked_array(sign_class, mask=track.dx.mask)
            o["sign_picture"] = np.ma.masked_array(sign_picture, mask=track.dx.mask)
            o["sign_value"] = np.ma.masked_array(sign_value, mask=track.dx.mask)
            o["sign_status"] = np.ma.masked_array(sign_status, mask=track.dx.mask)
            o["sign_visibility_status"] = np.where(track.dx.data < 0, False, True)
            o["sign_visibility_status"][track.dx.mask] = False
            missing_sign_ids.extend(missing_signs)
            objects.append(o)

        elapsed = time.time() - start_time
        missing_sign_ids = set(missing_sign_ids)
        if len(missing_sign_ids) > 0:
            logger.warning("Missing sign class IDs: {}".format(missing_sign_ids))
        logger.info(
            "FLC25 TSR object retrieval has completed in " + str(elapsed) + " seconds"
        )
        # isinstance(objects[0]["sign_value"], np.ma.MaskedArray)
        shifted_objects = []
        fill_value_idx = 0
        for obj in objects:
            shifted_obj = {}
            for key, value in obj.items():
                if isinstance(obj[key], np.ma.MaskedArray):
                    shift_mask = shift(obj[key].mask, indexes, True)
                    fill_value_idx = np.argmax(obj[key].mask == True)
                    shift_data = shift(obj[key].data, indexes, obj[key].data[fill_value_idx])
                    shifted_arr = np.ma.array(shift_data, mask=shift_mask)
                elif type(obj[key]).__module__ == np.__name__:
                    shifted_arr = shift(obj[key], indexes, obj[key][fill_value_idx])
                else:
                    shifted_arr = obj[key]
                shifted_obj[key] = shifted_arr
            shifted_objects.append(shifted_obj)
        return tracks.time, shifted_objects


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

def shift(arr, num, fill_value=np.nan):
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result[:] = arr
    return result

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

    meas_path = r"C:\KBData\TSR\test\2021-11-16\mi5id5321__2021-11-16_10-55-20_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    conti, objects = manager_modules.calc("fillFLC25_TSR@aebs.fill", manager)
    print(objects)
