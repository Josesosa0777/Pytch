# -*- dataeval: init -*-

import numpy as np
import os
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask, maskToIntervals
from measparser.PostmarkerJSONParser import parse_icon_data
from pyutils.cache_manager import get_modules_cache, store_modules_cache
import logging

INVALID_TRACK_ID = -1
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")
logger = logging.getLogger("fillFLC25_TSR")


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
        # suppl_signs = {}
        # # suppl_track[0]["esupplclassid"][suppl_track[0]["esupplclassid"].mask] = 0
        #
        # # Add supplementary track if it has sign detected
        # for id, suppl_tracks in supplementary_sign_details.iteritems():
        #
        #     # Clean other values where sign is not detected
        #     suppl_sign_dict = {}
        #     for _id, suppl_track in suppl_tracks.items():
        #         suppl_track["esupplclassid"][suppl_track["esupplclassid"].mask] = 0
        #         invalid_mask = (suppl_track["esupplclassid"].data == 0.0)
        #         if np.all(invalid_mask):
        #             continue
        #         suppl_sign_dict[_id] = {"esupplclassid" : np.ma.array(suppl_track["esupplclassid"].data, mask = invalid_mask)}
        #     if suppl_sign_dict != {}:
        #         suppl_signs[id] = suppl_sign_dict

        def add_object(id, track, suppl_track=None):
            o = dict()

            if suppl_track is not None:
                mask = suppl_track["esupplclassid"].mask
                o["id"] = np.where(mask, -1, id) #TODO mask
                o["valid"] = ~mask #TODO mask
                o["label"] = np.array(["FLC25_TSR_SUPPL_%d_T" % (id) for id in o["id"]]) # TODO
                suppl_alive_intervals = maskToIntervals(~mask)
                init_intervals = [(st, st + 1) for st, end in suppl_alive_intervals] # TODO
                o["traffic_sign_id"] = suppl_track["esupplclassid"].astype(int)  # TODO
                o["universal_id"] = track.universal_id.astype(int) # TODO
                o["universal_id"] = np.ma.array(map(lambda uid: str(uid).replace(str(uid), str(uid) + "-SUPPL"), o["universal_id"]), mask=mask)
                # str(int(float(o["universal_id"][~mask][0]))) + "-SUPPL"
            else:
                mask = track.universal_id.mask
                o["id"] = np.where(mask, -1, id) #TODO mask
                o["valid"] = ~mask #TODO mask
                o["label"] = np.array(["FLC25_TSR_%d" % (id) for id in o["id"]]) # TODO
                init_intervals = [(st, st + 1) for st, end in track.alive_intervals] # TODO
                o["traffic_sign_id"] = track.traffic_sign_id.astype(int)  # TODO
                o["universal_id"] = track.universal_id.astype(int) # TODO

            # o["id"] = np.where(mask, -1, id) #TODO mask
            # o["valid"] = ~mask #TODO mask
            # o["label"] = np.array(["FLC25_TSR_%d" % (id) for id in o["id"]]) # TODO
            track.dx.data[mask] = 0
            track.dy.data[mask] = 0
            o["dx"] = track.dx.data
            o["dy"] = track.dy.data
            o["type"] = np.ones(track.dx.shape, dtype="int")
            o["type"][:] = self.get_grouptype("FLC25_TSR_STAT")
            # init_intervals = [(st, st + 1) for st, end in track.alive_intervals] # TODO
            o["init"] = intervalsToMask(init_intervals, track.dx.size)
            color_mask = np.reshape(np.repeat(mask, 3), (-1, 3))
            o["color"] = np.where(color_mask, [255, 69, 0], [255, 69, 0])

            o["image_mapping_data"] = identifier_to_icon_mapping
            # o["traffic_sign_id"] = track.traffic_sign_id.astype(int) #TODO
            # o["universal_id"] = track.universal_id.astype(int) # TODO
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
            o["sign_class"] = np.ma.masked_array(sign_class, mask=mask)
            o["sign_picture"] = np.ma.masked_array(sign_picture, mask=mask)
            o["sign_value"] = np.ma.masked_array(sign_value, mask=mask)
            o["sign_status"] = np.ma.masked_array(sign_status, mask=mask)
            o["sign_visibility_status"] = np.where(track.dx.data < 0, 0, 1)
            o["sign_visibility_status"][mask] = 0
            missing_sign_ids.extend(missing_signs)
            # objects[0]["sign_picture"][~objects[0]["sign_picture"].mask]

            objects.append(o)

        # for id, track in tracks.iteritems():
        #     add_object(id, track)
        for id, (track, suppl_tracks) in enumerate(zip(tracks.iteritems(), supplementary_sign_details.iteritems())):
            track = track[1]
            suppl_tracks = suppl_tracks[1]
            for _, suppl_track in suppl_tracks.iteritems():
                add_object(id, track, suppl_track)


        elapsed = time.time() - start_time
        missing_sign_ids = set(missing_sign_ids)
        if len(missing_sign_ids) > 0:
            logger.warning("Missing sign class IDs: {}".format(missing_sign_ids))
        logger.info(
            "FLC25 TSR object retrieval has completed in " + str(elapsed) + " seconds"
        )
        return tracks.time, objects

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
    conti, objects = manager_modules.calc("fillFLC25_TSR_SUPPL@aebs.fill", manager)
    # print(objects)
