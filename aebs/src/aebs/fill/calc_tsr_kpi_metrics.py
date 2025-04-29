# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import glob
import math

from interface import iCalc
import logging
import os
import json
import numpy as np
from measparser.kpi_evaluation import TSRKpiEvaluation
from tsreval.view_tsr_can_signals import sgs as can_sgs_grp

mainLogger = logging.getLogger('end_run_state')
logger = logging.getLogger('end_run')

CAN_RECORDING_INDEX_AFTER_EXISTANCE_IS_FALSE = 30
CUMULATIVE_DATA = {}
RESULT_DATA = {}
FP = 0
FN = 0
TP = 0
KB_RECEIVED_CORRECTLY = 0
KB_RECEIVED_INCORRECTLY = 0
KBKPI = {}
KBKPI_DATA = {}
TSR_SIGNS_FILE_PATH = os.path.join(os.path.dirname(__file__), "config", "SR_sign_classes.txt")
signMappingFile_path = os.path.join(os.path.dirname(__file__), "config", "Sign_mapping.txt")
signMappingFile = open(signMappingFile_path, 'r')


class cFill(iCalc):
    dep = ('calc_common_time-tsrresim', 'fill_postmarker_traffic_signs', 'fillFLC25_TSR', 'fill_flc25_tsr_raw_tracks',)
    optdep = ('Calc_PropTSRAlone',)
    lateDetectionCalled = 0
    lateDetectionFlag = 1
    Total_GT = 0
    can_data = {}

    def check(self):
        kpi_input_data = {}
        source = self.get_source()
        kpi_input_data["confusion_matrix_image_path"] = os.path.splitext(source.FileName)[0] + ".png"

        _, postmarker_tsr, resim_deviation, self.traffic_sign_report = self.modules.fill(
            "fill_postmarker_traffic_signs@aebs.fill")
        self.common_time = _
        conti_tsr_time, conti_tsr_objects = self.modules.fill("fillFLC25_TSR@aebs.fill")
        self.conti_tsr_time = conti_tsr_time
        lmk_tracks, conti_tsr_suppl = self.modules.fill("fill_flc25_tsr_raw_tracks@aebs.fill")
        # If traffic sign data is not present skip processing to skip current measurement
        if not postmarker_tsr:
            logger.warning("Missing traffic sign data or could not extract data from postmarker json format")
            return conti_tsr_time, {}, False, {}
        sgs = [
            {
                "iNumOfUsedLandmarks": (
                    "LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_HeaderLmkList_iNumOfUsedLandmarks",
                ),
            },
            {
                "iNumOfUsedLandmarks": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_HeaderLmkList_iNumOfUsedLandmarks",
                ),
            },
        ]
        group = self.source.selectSignalGroupOrEmpty(sgs)
        _, value, _ = group.get_signal_with_unit(
            "iNumOfUsedLandmarks", ScaleTime=conti_tsr_time
        )
        is_conti_sign_detected = value > 0

        # <editor-fold desc="Prepare conti detection comparison with ground truth">
        postmarker_objectbufferlist = {}
        o = {}
        o["time"] = conti_tsr_time
        o["conti_detection"] = is_conti_sign_detected
        o["postmarker_detection"] = postmarker_tsr[0]["is_sign_detected"].data

        objectbuffer_key = "detection_compare_objectbuffer"
        postmarker_objectbufferlist[objectbuffer_key] = o

        kpi_input_data["detection_compare_objects"] = postmarker_objectbufferlist
        # </editor-fold>

        # <editor-fold desc="Prepare postmarker data">
        postmarker_objectbufferlist = {}
        for id, postmarker_track in enumerate(postmarker_tsr):
            o = {}
            o["time"] = conti_tsr_time
            o["sign_class_id"] = postmarker_track["sign_class_id"].data

            o["valid"] = postmarker_track["valid"].data

            o["quantity"] = postmarker_track["sign_quantity"].data

            o['weather_condition'] = postmarker_track['weather_condition'].data

            o['time_condition'] = postmarker_track['time_condition'].data

            objectbuffer_key = "postmarker_objectbuffer" + str(id)
            postmarker_objectbufferlist[objectbuffer_key] = o

        kpi_input_data["postmarker_objects"] = postmarker_objectbufferlist
        # </editor-fold>

        # <editor-fold desc="Prepare conti TSR data">
        conti_tsr_objectbufferlist = {}
        for id, track in enumerate(conti_tsr_objects):
            o = dict()
            o["valid"] = track["valid"]
            sign_id = track["traffic_sign_id"]
            o["traffic_sign_id"] = sign_id.data

            suppl_sign_ids = []
            for _id, suppl_sign_id in conti_tsr_suppl[id].iteritems():
                suppl_sign_ids.append(suppl_sign_id["esupplclassid"].data.astype(int))

            o["suppl_sign_ids"] = np.dstack(tuple(suppl_sign_ids))[0]
            suppl_uid = track["universal_id"].data.copy()
            suppl_uid[conti_tsr_suppl[id][0]["esupplclassid"].mask] = 0
            o["uid_suppl"] = suppl_uid

            uid = track["universal_id"]
            o["uid"] = uid.data

            status = track["sign_visibility_status"]
            o["status"] = status

            o["time"] = conti_tsr_time

            objectbuffer_key = "conti_tsr_objectbuffer" + str(id)
            conti_tsr_objectbufferlist[objectbuffer_key] = o

        kpi_input_data["conti_tsr_objects"] = conti_tsr_objectbufferlist
        # </editor-fold>
        # CAN signals collection
        can_signal_group = self.source.selectSignalGroupOrEmpty(can_sgs_grp)
        self.can_signals = {}
        self.tsr_alone_signals = {}
        try:
            self.can_signals["AutoHighLowBeamControl"] = can_signal_group.get_signal(
                "AutoHighLowBeamControl")
            self.can_signals["TSSCurrentRegion"] = can_signal_group.get_signal("TSSCurrentRegion")
            self.can_signals["TSSDetectedStatus"] = can_signal_group.get_signal("TSSDetectedStatus")
            self.can_signals["TSSDetectedUoM"] = can_signal_group.get_signal("TSSDetectedUoM")
            self.can_signals["TSSDetectedValue"] = can_signal_group.get_signal("TSSDetectedValue")
            self.can_signals["TSSLifeTime"] = can_signal_group.get_signal("TSSLifeTime")
            self.can_signals["TSSOverspeedAlert"] = can_signal_group.get_signal("TSSOverspeedAlert")
            if len(self.can_signals["AutoHighLowBeamControl"][0]) == 0:
                self.can_signals = {}

        except Exception as e:
            print (
                "TSR CAN signals missing, please update signal group in dataevalaebs/src/tsreval/view_tsr_can_signals.py")
            logger.critical(
                "TSR CAN signals missing, please update signal group in dataevalaebs/src/tsreval/view_tsr_can_signals.py")

        if self.can_signals == {}:
            self.tsr_alone_signals = self.modules.fill(self.optdep[0])

        kpi = TSRKpiEvaluation(kpi_input_data)
        if self.lateDetectionCalled == 0:
            conti_tsr_time, kpi_input_data, is_conti_sign_detected, kpi = self.lateDetection(conti_tsr_time,
                                                                                             kpi_input_data,
                                                                                             is_conti_sign_detected,
                                                                                             resim_deviation)
        return self.conti_tsr_time, kpi_input_data, is_conti_sign_detected, kpi

    def updatePostmarkerLable(self, time, event_time, resim_deviation):
        # time= FN time,event_time=FP time
        text_files = glob.glob(self.folder_path + "/*.json")
        flag = 0
        for json_file_path in text_files:
            # json_file_path = os.path.join(text_files[i]).replace("\\", "/")
            if not os.path.isfile(json_file_path):
                raise Exception(
                    "Postmarker data not found, Place the json file along with the measurements")

            if flag == 1:
                break
            else:
                # Read postmarker data
                f = open(json_file_path)
                marker_data = json.load(f)
                f.close()
                if 'Meta Information' in marker_data:
                    meas_start_time = sorted(marker_data['Meta Information'].keys())[0]
                    # meas_start_time = 1637074911031370

                if 'Traffic Signs' in marker_data:
                    traffic_signs = marker_data['Traffic Signs']

                    for item in traffic_signs.keys():

                        delta_ref = int(item) - int(meas_start_time)
                        delta_t = delta_ref / 1000000.0
                        s_time = self.common_time[0] + delta_t - resim_deviation

                        if math.trunc(s_time) == math.trunc(time):
                            delta_reference = delta_ref
                            print("found in json s_time:", s_time)

                            # Postmarker timestamp calculation
                            timestamp = 0
                            for item_dict in self.traffic_sign_report:
                                if delta_reference in item_dict.values():
                                    timestamp = item_dict['Start']
                                    print("old_time:", timestamp)

                            # Conti's timestamp calculation
                            new_timestamp = 0
                            delta_t = event_time - self.common_time[0] + resim_deviation
                            delta_ref = delta_t * 1000000.0
                            new_timestamp = int(delta_ref + int(meas_start_time))

                            print("updated old time: ", timestamp, "to new_time:", new_timestamp)

                            if (timestamp != 0 and new_timestamp != 0):
                                marker_data['Traffic Signs'][new_timestamp] = marker_data['Traffic Signs'][timestamp]
                                marker_data['Traffic Signs'].pop(timestamp)
                                print("Updated to ", marker_data['Traffic Signs'][new_timestamp])
                                mainLogger.info("Postmarker Data:: updated old time: ", str(timestamp), "to new_time:",
                                                str(new_timestamp))
                                with open(json_file_path, "w") as outfile:
                                    json.dump(marker_data, outfile, indent=4)
                                    flag = 1
                                break

    def lateDetection(self, conti_tsr_time, kpi_input_data, is_conti_sign_detected, resim_deviation):
        # --------------Update json timestamp for late detection by conti---------------------
        late_detections = []
        self.lateDetectionCalled = 1
        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.folder_path = os.path.dirname(self.filename)
        kpi = TSRKpiEvaluation(kpi_input_data)
        kpi.createKBTSRList()
        kpi.createGTInfo()
        kpi.createInfoToCompare()
        kpi.createContiInfo()
        kpi.fetchUniqueUids()
        kpi.evaluateKpi()

        for report_identifier, verdict in kpi.report.items():
            _, event_time = report_identifier
            if verdict['verdict'] == 'False Positive Type 2':
                for idf, verd in kpi.report.items():
                    id, time = idf
                    if (id == _ and verd['verdict'] == 'False Negative'):
                        if math.trunc(event_time) in range(math.trunc(time),
                                                           math.trunc(time) + 2):  # Late detection event found
                            late_detections.append(event_time)
                            print("Late Detections:", time, verd)
                            # Re-mark the timestamp as per conti's detection
                            self.updatePostmarkerLable(time, event_time, resim_deviation)
        if late_detections:
            conti_tsr_time, kpi_input_data, is_conti_sign_detected, kpi = self.check()
            self.lateDetectionFlag = 1
        else:
            self.lateDetectionFlag = 0
        return conti_tsr_time, kpi_input_data, is_conti_sign_detected, kpi

    def fill(self, conti_tsr_time, kpi_input_data, is_conti_sign_detected, kpi):
        # if self.lateDetectionFlag==0:
        # If traffic sign data is not present skip processing to skip current measurement
        if not self.traffic_sign_report:
            return conti_tsr_time, {}, {}, is_conti_sign_detected
        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.folder_path = os.path.dirname(self.filename)
        # kpi = TSRKpiEvaluation(kpi_input_data)
        if self.lateDetectionFlag == 1:  # to avoid evaluation on same data
            kpi.createKBTSRList()
            kpi.createGTInfo()
            kpi.createInfoToCompare()
            kpi.createContiInfo()
            kpi.fetchUniqueUids()
            kpi.evaluateKpi()
        kpi.displayData()
        kpi_report = {}
        signMappingFile_dict = {}
        self.jsonObjected = {}
        self.jsonObjectedKBkpi = {}
        self.KBKpi = {}
        self.KBKpi = {
            "KB": {
                'KB_Received_Incorrectly': 0,
                'KB_Received_Correctly': 0
            }
        }
        listOfSignsIgnored = [278200, 278201, 278300, 278301, 282000, 282001, 310000, 311000, 331000, 336000, 104812,
                              104811, 104030, 105236, 100100, 100400, 104040]
        # Mapping conti Id to Sign Value - as seen in CAN. Eg.: 274550 - 50. mapping means --> contiSignId = 274550 -- TSSDetectedValue = 50.
        for line in signMappingFile:
            contiSignValue, mappedValue = line.strip().split('=')
            signMappingFile_dict[contiSignValue.strip()] = mappedValue.strip()

        can_set_values_idx, can_set_values_time = self.get_CAN_signal_Data_idx_time()

        # CAN data calculation
        for timelst, idx in zip(can_set_values_time, can_set_values_idx):
            can_signals = {}
            for alias, signal in self.can_signals.items():
                try:
                    can_signals[alias] = signal[1][idx[0]]
                except Exception as e:
                    print(str(e))
            can_signals['can_duration'] = float(timelst[-1] - timelst[0])
            self.can_data[int(timelst[0])] = range(int(timelst[0]), int(timelst[-1])), can_signals

        self.can_data_fp = self.can_data
        for gt in kpi.gtInfo.values():
            self.Total_GT += gt['quantity'][0]

        for report_identifier, verdict in kpi.report.items():
            _, event_time = report_identifier
            can_signals={}
            buffer_id = verdict["contiBufferId"]
            if self.can_signals or self.tsr_alone_signals:
                if buffer_id is None:
                    can_signals = self.get_can_signals(event_time)
                    can_signals.update(verdict)
                    kpi_report[report_identifier] = can_signals
                    continue
                buffer_name = 'conti_tsr_objectbuffer{}'.format(buffer_id)
                conti_buffer = kpi_input_data["conti_tsr_objects"][buffer_name]
                status = conti_buffer["status"]
                timestamps = conti_buffer["time"]
                event_index = max(timestamps.searchsorted(event_time, side="right") - 1, 0)
                can_signals = self.get_can_signals(event_time)
                can_signals.update(verdict)
                contiLmkDetection = signMappingFile_dict.get(str(int(_)))
                if contiLmkDetection is not None and can_signals.has_key('TSSDetectedValue'):
                    if int(
                            contiLmkDetection) not in listOfSignsIgnored:  # KB_KPI Calculation comparing Conti LMK versus CAN Message.

                        if str(can_signals['TSSDetectedValue']) == contiLmkDetection:
                            self.KBKpi["KB"]['KB_Received_Correctly'] = self.KBKpi["KB"]['KB_Received_Correctly'] + 1

                        else:
                            self.KBKpi["KB"]['KB_Received_Incorrectly'] = self.KBKpi["KB"][
                                                                              'KB_Received_Incorrectly'] + 1

            else:
                can_signals = verdict
            kpi_report[report_identifier] = can_signals

        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.folder_path = os.path.dirname(self.filename)
        self.nameOfFile = self.filename.split('\\')[-3]
        global CUMULATIVE_DATA, FP, FN, TP, RESULT_DATA, KB_RECEIVED_CORRECTLY, KB_RECEIVED_INCORRECTLY, \
            KBKPI, KBKPI_DATA

        for key, value in kpi.cumulative_results.iteritems():
            for item, val in kpi.cumulative_results[key].iteritems():
                if item == 'FP':
                    FP = FP + val
                    RESULT_DATA['FP'] = FP
                elif item == 'FN':
                    FN = FN + val
                    RESULT_DATA['FN'] = FN
                elif item == 'TP':
                    TP = TP + val
                    RESULT_DATA['TP'] = TP
            CUMULATIVE_DATA[key] = RESULT_DATA
        json_object = self.folder_path + '\\' + self.nameOfFile + "_overallpredictions" + '.json'
        for key, value in self.KBKpi.iteritems():
            for item, val in self.KBKpi[key].iteritems():
                if item == 'KB_Received_Correctly':
                    KB_RECEIVED_CORRECTLY = KB_RECEIVED_CORRECTLY + val
                    KBKPI_DATA['KB_Received_Correctly'] = KB_RECEIVED_CORRECTLY
                elif item == 'KB_Received_Incorrectly':
                    KB_RECEIVED_INCORRECTLY = KB_RECEIVED_INCORRECTLY + val
                    KBKPI_DATA['KB_Received_Incorrectly'] = KB_RECEIVED_INCORRECTLY
            KBKPI[key] = KBKPI_DATA
        CUMULATIVE_DATA.update(KBKPI)
        with open(json_object, "w") as outfile:
            json.dump(CUMULATIVE_DATA, outfile, indent=4)
        # json.dump(self.KBKpi, outfile, indent=4)

        kpi.cumulative_results['Total_GT'] = self.Total_GT

        return self.conti_tsr_time, kpi_report, kpi.cumulative_results, is_conti_sign_detected

    def checkForContinuity(self, src):
        idx_lst = []
        break_lst = []
        index = 0

        for current, next in zip(src, src[1:]):
            if current != next:
                break_lst.append(index + 1)
            index += 1

        break_lst.append(index)
        idx_lst.append([0, break_lst[0]])

        for i in range(1, len(break_lst)):
            idx_lst.append([break_lst[i - 1], break_lst[i]])

        return idx_lst

    def splitme_zip(self, a, d=1):
        a = a[0]
        m = np.concatenate(([True], a[1:] > a[:-1] + d, [True]))
        idx = np.flatnonzero(m)
        l = a.tolist()
        return [l[i:j] for i, j in zip(idx[:-1], idx[1:])]

    def get_CAN_signal_Data_idx_time(self):
        if self.can_signals.has_key('TSSDetectedValue'):
            tssDetectedValue = self.can_signals['TSSDetectedValue'][1]
            final_can_values_idx = []
            final_can_values_time = []
            # No can detection at all
            if len(np.argwhere(tssDetectedValue != 251)) != 0:
                can_set_values_idx = self.splitme_zip(
                    np.argwhere(tssDetectedValue != 251).reshape(np.argwhere(tssDetectedValue != 251).shape[1],
                                                                 np.argwhere(tssDetectedValue != 251).shape[0]))
                can_set_values_time = [self.can_signals['TSSDetectedValue'][0][i[0]:i[-1] + 1] for i in can_set_values_idx]

                for can_item_idx, can_time_idx in zip(can_set_values_idx, can_set_values_time):
                    ret = self.checkForContinuity(tssDetectedValue[can_item_idx[0]:(can_item_idx[-1] + 1)])
                    for idx in ret:
                        final_can_values_idx.append(can_item_idx[idx[0]:(idx[-1] + 1)])
                        final_can_values_time.append(can_time_idx[idx[0]:(idx[-1] + 1)])

                return final_can_values_idx, final_can_values_time
            else:
                return [], []
        elif self.tsr_alone_signals != {}:
            tsr_SpeedLimit1_E8_sE8 = self.tsr_alone_signals['TSR_SpeedLimit1_E8_sE8'][1]
            final_SpeedLimit1values_idx = []
            final_SpeedLimit1values_time = []
            # No can detection at all
            if len(np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0)) != 0:
                can_set_values_idx = self.splitme_zip(
                    np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).reshape(np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).shape[1],
                                                                     np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).shape[0]))
                can_set_values_time = [self.tsr_alone_signals['TSR_SpeedLimit1_E8_sE8'][0][i[0]:i[-1] + 1] for i in
                                       can_set_values_idx]

                for can_item_idx, can_time_idx in zip(can_set_values_idx, can_set_values_time):
                    ret = self.checkForContinuity(tsr_SpeedLimit1_E8_sE8[can_item_idx[0]:(can_item_idx[-1] + 1)])
                    for idx in ret:
                        final_SpeedLimit1values_idx.append(can_item_idx[idx[0]:(idx[-1] + 1)])
                        final_SpeedLimit1values_time.append(can_time_idx[idx[0]:(idx[-1] + 1)])

                return final_SpeedLimit1values_idx, final_SpeedLimit1values_time
            else:
                return [], []
        else:
            return [],[]

    def get_can_signals(self, event_time):
        can_signals = {}
        can_data = {}
        can_set_values_idx, can_set_values_time = self.get_CAN_signal_Data_idx_time()
        idx = 0
        can_signal_index = -1
        for time_lst in can_set_values_time:
            if int(event_time) in range(int(time_lst[0]), int(time_lst[-1]) + 1):
                can_signal_index = can_set_values_idx[idx][0]
            idx += 1

        idx = 0
        if can_signal_index == -1:
            for time_lst in can_set_values_time:
                if int(event_time) in range(int(time_lst[0]) - 2, int(time_lst[-1]) + 1):
                    can_signal_index = can_set_values_idx[idx][0]
                idx += 1

        if can_signal_index == -1:
            if self.can_signals != {}:
                can_signal_index = np.argmax(self.can_signals["TSSCurrentRegion"][0] >= event_time)
            elif self.tsr_alone_signals != {}:
                can_signal_index = np.argmax(self.tsr_alone_signals["TSR_SpeedLimit1_E8_sE8"][0] >= event_time)

        if self.can_signals != {}:
            can_data = self.can_signals
        elif self.tsr_alone_signals != {}:
            can_data = self.tsr_alone_signals

        for alias, signal in can_data.items():
            try:
                can_signals[alias] = signal[1][can_signal_index]
            except Exception as e:
                logger.critical(str(e))
        return can_signals

if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\TSR\test\Ford\2021-10-11\mi5id787__2021-10-11_16-06-46_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_tsr_kpi_metrics@aebs.fill', manager)
    print flr25_common_time
