import json
import logging
import os
from collections import OrderedDict
import numpy as np
from aebs.par import postmarker_enums

logger = logging.getLogger("PostmarkerJSONParser")
CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")


class PostmarkerJSONParser:
    @staticmethod
    def is_postmarker_json(FileName):
        postmarker_data = None
        if FileName.endswith(".json") and os.path.isfile(FileName):
            try:
                f = open(FileName)
                raw_data = json.load(f)
                # data_source = raw_data["Other Information"]["Data Source"]
                # if data_source.lower() == "postmarker":
                # 		postmarker_data = raw_data
                postmarker_data = raw_data
                f.close()
            except Exception as e:
                logger.warning(str(e))

        return postmarker_data

    TIME_PREFIX = "t_"

    def __init__(self, postmarker_raw_data_dict, time):
        """
        :param postmarker_raw_data_dict: Postmarker tool JSON raw data dictionary
        """
        self.postmarker_raw_data = postmarker_raw_data_dict
        self.common_time = time

    def get_meta_info(self):
        meta_info_reports = []
        if "Meta Information" in self.postmarker_raw_data:
            label_metadata = self.postmarker_raw_data["Meta Information"]
            del label_metadata["Recording Name"]
            markers = [
                str(x) for x in sorted([int(label) for label in label_metadata.keys()])
            ]
            tmp_label_metadata = OrderedDict()
            # Prepare ordered dict to iterate on
            for key in markers:
                tmp_label_metadata[key] = label_metadata[key]

            for row_index, value in tmp_label_metadata.items():
                pytch_report = {}
                marker = []
                if row_index not in markers:
                    continue
                if "Single" in value:
                    pytch_report["Name"] = value[0]
                    pytch_report["Value"] = value[1]
                    pytch_report["Start"] = row_index
                    pytch_report["End"] = row_index
                    meta_info_reports.append(pytch_report)
                    continue

                pytch_report["Name"] = value[0]
                pytch_report["Value"] = value[1]
                pytch_report[str(value[2])] = row_index
                label_metadata_value = value[2].lower()
                for marker in markers:
                    if (
                        label_metadata[marker][0] == pytch_report["Name"]
                        and label_metadata[marker][1] == pytch_report["Value"]
                        and label_metadata[marker][2].lower().lower()
                        != label_metadata_value
                    ):
                        pytch_report[str(label_metadata[marker][2])] = marker
                        markers.remove(marker)
                        markers.remove(row_index)
                        break
                if len(pytch_report) == 4:
                    if pytch_report not in meta_info_reports:
                        meta_info_reports.append(pytch_report)
                else:
                    print(
                        "Missing info for marker %s" % pytch_report["Name"]
                        + "_"
                        + marker
                    )
        return meta_info_reports

    def get_traffic_info(self):
        traffic_sign_report = []
        if "Traffic Signs" in self.postmarker_raw_data:
            traffic_signs = self.postmarker_raw_data["Traffic Signs"]
            traffic_signs_markers = [
                str(x) for x in sorted([int(label) for label in traffic_signs.keys()])
            ]
            tmp_traffic_sign_data = OrderedDict()
            # Prepare ordered dict to iterate on
            for key in traffic_signs_markers:
                tmp_traffic_sign_data[key] = traffic_signs[key]

            for row_index, value in tmp_traffic_sign_data.items():
                pytch_report = {}
                pytch_report["new_sign_class"] = value[0]
                pytch_report["conti_sign_class"] = value[1]
                pytch_report["description"] = value[2]
                if value[3] == "true":
                    pytch_report["status"] = 1
                else:
                    pytch_report["status"] = 0
                pytch_report["Start"] = row_index
                pytch_report["End"] = row_index
                traffic_sign_report.append(pytch_report)

        return traffic_sign_report

    def get_meta_info_signals(self, meta_info_reports):
        signals = {}
        postmarker_env_time = np.zeros(self.common_time.shape, dtype=bool)
        postmarker_roadtype = np.zeros(self.common_time.shape, dtype=bool)
        postmarker_vehicle_headlamp = np.zeros(self.common_time.shape, dtype=int)
        postmarker_weather_conditions = np.zeros(self.common_time.shape, dtype=int)
        postmarker_road_edge = np.zeros(self.common_time.shape, dtype=int)
        postmarker_street_objects = np.zeros(self.common_time.shape, dtype=int)
        postmarker_obj_on_side_of_road = np.zeros(self.common_time.shape, dtype=int)
        postmarker_traffic_event = np.zeros(self.common_time.shape, dtype=int)
        postmarker_moving_objects = np.zeros(self.common_time.shape, dtype=int)
        postmarker_country_code = np.zeros(self.common_time.shape, dtype=int)
        for traffic_obj in meta_info_reports:
            st_idx, ed_idx = self.get_index(
                float(traffic_obj["Start"]), float(traffic_obj["End"])
            )
            if traffic_obj["Name"] == "Time":
                postmarker_env_time[st_idx:ed_idx] = postmarker_enums.TIME[
                    traffic_obj["Value"]
                ]
            elif traffic_obj["Name"].lower() == "road type":
                postmarker_roadtype[st_idx:ed_idx] = postmarker_enums.ROAD_TYPE[
                    traffic_obj["Value"]
                ]
            elif traffic_obj["Name"].lower() == "vehicle headlamp":
                postmarker_vehicle_headlamp[
                    st_idx:ed_idx
                ] = postmarker_enums.VEHICLE_HEADLAMP[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "weather conditions":
                postmarker_weather_conditions[
                    st_idx:ed_idx
                ] = postmarker_enums.WEATHER_CONDITIONS[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "road edge":
                postmarker_road_edge[st_idx:ed_idx] = postmarker_enums.ROAD_EDGE[
                    traffic_obj["Value"]
                ]
            elif traffic_obj["Name"].lower() == "street objects":
                postmarker_street_objects[
                    st_idx:ed_idx
                ] = postmarker_enums.STREET_OBJECTS[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "object on side of roads":
                postmarker_obj_on_side_of_road[
                    st_idx:ed_idx
                ] = postmarker_enums.OBJECT_ON_SIDE_OF_ROAD[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "traffic event":
                postmarker_traffic_event[
                    st_idx:ed_idx
                ] = postmarker_enums.TRAFFIC_EVENT[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "moving objects":
                postmarker_moving_objects[
                    st_idx:ed_idx
                ] = postmarker_enums.MOVING_OBJECTS[traffic_obj["Value"]]
            elif traffic_obj["Name"].lower() == "country code":
                postmarker_country_code[st_idx:ed_idx] = postmarker_enums.COUNTRY_CODE[
                    traffic_obj["Value"]
                ]
            else:
                logger.warning("Label not found: {}".format(traffic_obj["Name"]))
                continue

        signals["postmarker_roadtype"] = (postmarker_roadtype, "t_Postmarker_time", "")
        signals["postmarker_vehicle_headlamp"] = (
            postmarker_vehicle_headlamp,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_weather_conditions"] = (
            postmarker_weather_conditions,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_road_edge"] = (
            postmarker_road_edge,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_street_objects"] = (
            postmarker_street_objects,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_obj_on_side_of_road"] = (
            postmarker_obj_on_side_of_road,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_traffic_event"] = (
            postmarker_traffic_event,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_moving_objects"] = (
            postmarker_moving_objects,
            "t_Postmarker_time",
            "",
        )
        signals["postmarker_country_code"] = (
            postmarker_country_code,
            "t_Postmarker_time",
            "",
        )

        return self.common_time, signals

    def get_inferred_traffic_sign_signals(self, traffic_sign_report):
        config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")
        traffic_sign_data_for_table, identifier_to_icon_mapping = parse_icon_data(
            config_file=config_file, seperator="="
        )
        signals = {}
        # Extract possible signals from both structures
        # Fill up signals dictionary, referring common time nd array
        is_traffic_sign_detected = np.zeros(self.common_time.shape, dtype=bool)
        postmarker_sign_class_id = np.zeros(self.common_time.shape, dtype=int)
        postmarker_sign_class = np.empty(self.common_time.shape, dtype=object)
        postmarker_sign_path = np.empty(self.common_time.shape, dtype=object)
        postmarker_sign_value = np.empty(self.common_time.shape, dtype=object)
        postmarker_sign_status = np.empty(self.common_time.shape, dtype=object)
        for traffic_obj in traffic_sign_report:
            st_idx, ed_idx = self.get_index(
                float(traffic_obj["Start"]), float(traffic_obj["Start"])
            )
            is_traffic_sign_detected[st_idx:ed_idx] = True
            postmarker_sign_class_id[st_idx:ed_idx] = int(
                traffic_obj["conti_sign_class"]
            )
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
        postmarker_sign_class[st_idx:ed_idx] = class_name
        postmarker_sign_path[st_idx:ed_idx] = sign_path
        postmarker_sign_value[st_idx:ed_idx] = value
        postmarker_sign_status[st_idx:ed_idx] = status
        tsr_mask = is_traffic_sign_detected
        signals["Postmarker_is_sign_detected"] = (
            is_traffic_sign_detected,
            "t_Postmarker_time",
            "",
        )
        signals["Postmarker_sign_class_id"] = (
            np.ma.array(postmarker_sign_class_id, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        signals["sign_class"] = (
            np.ma.array(postmarker_sign_class, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        signals["sign_icon_path"] = (
            np.ma.array(postmarker_sign_path, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        signals["sign_value"] = (
            np.ma.array(postmarker_sign_value, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        signals["sign_status"] = (
            np.ma.array(postmarker_sign_status, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        signals["Postmarker_valid"] = (tsr_mask, "t_Postmarker_time", "")
        return self.common_time, signals

    def get_traffic_sign_signals(self, traffic_sign_report):
        # config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")
        # traffic_sign_data_for_table, identifier_to_icon_mapping = parse_icon_data(config_file=config_file, seperator="=")
        signals = {}
        # Extract possible signals from both structures
        # Fill up signals dictionary, referring common time nd array
        is_traffic_sign_detected = np.zeros(self.common_time.shape, dtype=bool)
        postmarker_sign_class_id = np.zeros(self.common_time.shape, dtype=int)
        # postmarker_sign_class = np.empty(self.common_time.shape, dtype=object)
        # postmarker_sign_path = np.empty(self.common_time.shape, dtype=object)
        # postmarker_sign_value = np.empty(self.common_time.shape, dtype=object)
        # postmarker_sign_status = np.empty(self.common_time.shape, dtype=object)
        for traffic_obj in traffic_sign_report:
            st_idx, ed_idx = self.get_index(
                float(traffic_obj["Start"]), float(traffic_obj["Start"])
            )
            is_traffic_sign_detected[st_idx:ed_idx] = True
            postmarker_sign_class_id[st_idx:ed_idx] = int(
                traffic_obj["conti_sign_class"]
            )
            # try:
            # 		sign_path, class_name, value, status = traffic_sign_data_for_table[traffic_obj["conti_sign_class"]]
            # except:
            # 		sign_path, class_name, value, status = "Missing data", "Missing data", "Missing data", "Missing data"
            # postmarker_sign_class[st_idx:ed_idx] = class_name
            # postmarker_sign_path[st_idx:ed_idx] = sign_path
            # postmarker_sign_value[st_idx:ed_idx] = value
            # postmarker_sign_status[st_idx:ed_idx] = status
        tsr_mask = is_traffic_sign_detected
        signals["Postmarker_is_sign_detected"] = (
            is_traffic_sign_detected,
            "t_Postmarker_time",
            "",
        )
        signals["Postmarker_sign_class_id"] = (
            np.ma.array(postmarker_sign_class_id, mask=~tsr_mask),
            "t_Postmarker_time",
            "",
        )
        # signals["sign_class"] = (np.ma.array(postmarker_sign_class, mask=~tsr_mask), "t_Postmarker_time", "")
        # signals["sign_icon_path"] = (np.ma.array(postmarker_sign_path, mask=~tsr_mask), "t_Postmarker_time", "")
        # signals["sign_value"] = (np.ma.array(postmarker_sign_value, mask=~tsr_mask), "t_Postmarker_time", "")
        # signals["sign_status"] = (np.ma.array(postmarker_sign_status, mask=~tsr_mask), "t_Postmarker_time", "")
        # signals["Postmarker_valid"] = (tsr_mask, "t_Postmarker_time", "")
        return self.common_time, signals

    def get_index(self, st_time, ed_time):
        # Conversion microsec_to_sec
        st_time = st_time / 1000000.0
        ed_time = ed_time / 1000000.0
        # If type of json label is single- Add 1 sec time before and after it, Indicating event interval
        # if st_time == ed_time:
        # 		st_time = st_time #- 0.001
        # 		ed_time = ed_time #+ 0.001

        st_index = max(self.common_time.searchsorted(st_time, side="right") - 1, 0)
        ed_index = max(self.common_time.searchsorted(ed_time, side="right") - 1, 0)

        if st_index == ed_index:
            ed_index += 1
        return st_index, ed_index


def parse_icon_data(config_file, seperator="="):
    identifier_to_icon_mapping = {}
    traffic_sign_data = {}
    with open(config_file) as fp:
        Lines = fp.readlines()
        for line in Lines:
            sign_icon_path, sign_class, value, active_status = (
                "",
                "",
                "Not Applicable",
                "Inactive",
            )
            icon_data_to_load, sign_id = line.split(seperator)
            icon_data_to_load, sign_id = icon_data_to_load.strip(), sign_id.strip()
            raw_data = icon_data_to_load.split("_")
            # TODO Below logic for active or inactive is outdated, need an update
            if raw_data[-1] == "ACTIVE":
                if raw_data[-2].isdigit():
                    value = int(raw_data[-2])
                    del raw_data[-1]

                del raw_data[-1]
                active_status = "Active"
            else:
                if raw_data[-1].isdigit():
                    value = int(raw_data[-1])
                    del raw_data[-1]
                    active_status = "Inactive"

            sign_class = "_".join(raw_data)
            sign_icon_path = os.path.join(IMAGE_DIRECTORY, str(sign_id) + ".png")
            if not os.path.exists(sign_icon_path):
                sign_icon_path = os.path.join(
                    IMAGE_DIRECTORY, str(int(sign_id) + 1) + ".png"
                )
                if not os.path.exists(sign_icon_path):
                    sign_icon_path = os.path.join(
                        IMAGE_DIRECTORY, str(int(sign_id) - 1) + ".png"
                    )
                    if not os.path.exists(sign_icon_path):
                        sign_icon_path = os.path.join(
                            IMAGE_DIRECTORY, "NoImageAvailable_Europe.png"
                        )
            traffic_sign_data[sign_id] = (
                sign_icon_path,
                sign_class,
                value,
                active_status,
            )
            identifier_to_icon_mapping[sign_id] = sign_icon_path

    return traffic_sign_data, identifier_to_icon_mapping
