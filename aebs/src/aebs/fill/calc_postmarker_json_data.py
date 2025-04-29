# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from interface import iCalc
from collections import OrderedDict
import logging
import os

CONFIG_DIRECTORY = os.path.join(os.path.dirname(__file__), "config")
logger = logging.getLogger("calc_json_data")


class cFill(iCalc):

    def check(self):
        return

    def fill(self):
        marker_data = {}
        source = self.get_source()
        import json
        try:
            json_file_path = os.path.splitext(source.FileName)[0] + ".json"
            if not os.path.isfile(json_file_path):
                raise Exception("Postmarker data not found, Place the json file along with the input measurement")
            f = open(json_file_path)
            marker_data = json.load(f)
            f.close()
        except Exception as e:
            logger.critical(str(e))

        meta_info_reports = []
        if 'Meta Information' in marker_data:
            try:
                label_metadata = marker_data['Meta Information']
                recording_name = marker_data['Meta Information']["Recording Name"]
                del label_metadata["Recording Name"]
                markers = [str(x) for x in sorted([int(label) for label in label_metadata.keys()])]
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
                        if label_metadata[marker][0] == pytch_report["Name"] and label_metadata[marker][1] == \
                                pytch_report["Value"] and label_metadata[marker][
                            2].lower().lower() != label_metadata_value:
                            pytch_report[str(label_metadata[marker][2])] = marker
                            markers.remove(marker)
                            markers.remove(row_index)
                            break
                    if len(pytch_report) == 4:
                        if pytch_report not in meta_info_reports:
                            meta_info_reports.append(pytch_report)
                    else:
                        print("Missing info for marker %s" % pytch_report["Name"] + "_" + marker)
            except Exception as e:
                logger.warning("Exception while reading Meta Information from JSON:\n" + str(e))
        traffic_sign_report = []
        empty_sign_data = []
        meas_start_time = None
        try:
            meas_start_time = meta_info_reports[0]["Start"]
        except:
            logger.warning("Could not find time reference for delta calculations from postmarker json")
        if 'Traffic Signs' in marker_data:
            try:
                config_file = os.path.join(CONFIG_DIRECTORY, "SR_signs.txt")

                traffic_signs = marker_data['Traffic Signs']
                traffic_signs_markers = [str(x) for x in sorted([int(label) for label in traffic_signs.keys()])]
                tmp_traffic_sign_data = OrderedDict()
                # Prepare ordered dict to iterate on
                for key in traffic_signs_markers:
                    tmp_traffic_sign_data[key] = traffic_signs[key]

                for row_index, value in tmp_traffic_sign_data.items():
                    pytch_report = {}
                    pytch_report["new_sign_class"] = str(value[0])
                    if value[1] == "":  # Sign data is mandatory field so we cannot proceed without it
                        empty_sign_data.append(tuple(value))
                        continue
                    pytch_report["conti_sign_class"] = str(value[1])
                    pytch_report["description"] = str(value[2])
                    pytch_report["status"] = str(value[3])
                    if len(value) == 5:  # 5th field is quantity of same signs detected
                        pytch_report["quantity"] = int(str(value[4]))
                    else:
                        pytch_report["quantity"] = 1

                    # if value[3] == 'true':
                    # 		pytch_report["status"] = 1
                    # else:
                    # 		pytch_report["status"] = 0
                    pytch_report["Start"] = row_index
                    pytch_report["End"] = row_index
                    pytch_report["delta_reference"] = int(row_index) - int(meas_start_time)
                    traffic_sign_report.append(pytch_report)
                print("traffic_sign_report:",traffic_sign_report)
            except Exception as e:
                logger.warning("Exception while reading Traffic Signs from JSON:" + str(e))
        if empty_sign_data:
            logger.critical(
                "Empty conti_sign_class for record: {},\n Please check it out in Postmarker JSON file".format(
                    set(empty_sign_data)))

        # Calculate weather condition percetage
        weather_conditions = {'Clear': 0, 'Cloudy': 0, 'Rain': 0, 'Snow': 0, 'Fog': 0, 'Hail': 0}
        time_conditions = {'Day': 0, 'Twilight': 0, 'Night': 0}

        for meta_info in meta_info_reports:
            if meta_info['Name'] == u'Weather Conditions':
                if meta_info['Value'] == u'Clear':
                    weather_conditions['Clear'] = weather_conditions['Clear'] + 1
                elif meta_info['Value'] == u'Cloudy':
                    weather_conditions['Cloudy'] = weather_conditions['Cloudy'] + 1
                elif meta_info['Value'] == u'Rain':
                    weather_conditions['Rain'] = weather_conditions['Rain'] + 1
                elif meta_info['Value'] == u'Snow':
                    weather_conditions['Snow'] = weather_conditions['Snow'] + 1
                elif meta_info['Value'] == u'Fog':
                    weather_conditions['Fog'] = weather_conditions['Fog'] + 1
                elif meta_info['Value'] == u'Hail':
                    weather_conditions['Hail'] = weather_conditions['Hail'] + 1

                # check intervals
                for id, traffic_signs_data in enumerate(traffic_sign_report):
                    if int(meta_info['Start']) <= int(traffic_signs_data['Start']) <= int(meta_info['End']):
                        traffic_sign_report[id]['weather_condition'] = str(meta_info['Value'])

            if meta_info['Name'] == u'Time':
                if meta_info['Value'] == u'Day':
                    time_conditions['Day'] = time_conditions['Day'] + 1
                elif meta_info['Value'] == u'Twilight':
                    time_conditions['Twilight'] = time_conditions['Twilight'] + 1
                elif meta_info['Value'] == u'Night':
                    time_conditions['Night'] = time_conditions['Night'] + 1

                # check intervals
                for id, traffic_signs_data in enumerate(traffic_sign_report):
                    if int(meta_info['Start']) <= int(traffic_signs_data['Start']) <= int(meta_info['End']):
                        traffic_sign_report[id]['time_condition'] = str(meta_info['Value'])

        return meta_info_reports, traffic_sign_report


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\TSR_evaluation\data\weather_condition_check\2021-10-14\mi5id787__2021-10-14_15-43-55_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_postmarker_json_data@aebs.fill', manager)
    print flr25_common_time
