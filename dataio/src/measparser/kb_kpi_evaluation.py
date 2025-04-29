'''
Events:

True Positive: should be detected & is reflected on CAN
	[ground truth + 'existence = true'] == [FLC_PROP1.TSS_DetectedValue]

True Negative: shouldn't be detected & in not reflected on CAN
	[ground truth + 'existence = false'] != [FLC_PROP1.TSS_DetectedValue]
	[ground truth + 'existence = false'] ==251

False Negative: should be detected, but is not reflected on CAN
	[ground truth + 'existence = true'] == 251

False Positive Type 1: shouldn't be detected, but is reflected on CAN
	[ground truth + 'existence = false'] == [FLC_PROP1.TSS_DetectedValue]

False Positive Type 2: not GT at all, but some value reflected on CAN (Ghost sign)
	 [no ground truth at all] -- [FLC_PROP1.TSS_DetectedValue] (Ghost sign)

False Positive Type 3: should be detected, but is wrongly reflected on CAN
	[ground truth + 'existence = true'] != [FLC_PROP1.TSS_DetectedValue] && !=251

'''
import bisect

import numpy as np


class TSRKBKpiEvaluation:
    def __init__(self, kpi_input_data):
        self.kpi = {}
        self.kpi['true_positive'] = 0
        self.kpi['false_positive_type_1'] = 0
        self.kpi['false_positive_type_2'] = []
        self.kpi['false_positive_type_3'] = 0
        self.kpi['false_negative'] = 0
        self.kpi['true_negative'] = 0
        self.report = {}
        self.cumulative_results = {}
        self.gtObj = kpi_input_data['GT_data']
        self.postmarker_tsr = kpi_input_data['postmarker_tsr']
        self.can_data = kpi_input_data['can_data']
        self.propTSRAlone_data = kpi_input_data['PropTSRAlone']
        self.conti_tsr_time = kpi_input_data['conti_tsr_time']
        self.true_existance_gt = kpi_input_data['GT_existance_true']
        self.false_existance_gt = kpi_input_data['GT_existance_false']

    # Separate index if continues detection is for different Signs like 20 20 20 30
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

    # Index evaluation of Continues Detection in CAN means !=251
    def splitme_zip(self, a, d=1):
        a = a[0]
        m = np.concatenate(([True], a[1:] > a[:-1] + d, [True]))
        idx = np.flatnonzero(m)
        l = a.tolist()
        return [l[i:j] for i, j in zip(idx[:-1], idx[1:])]

    def get_CAN_signal_Data_idx_time(self):
        if self.can_data != {}:
            tssDetectedValue = self.can_data['TSSDetectedValue'][1]
            final_can_values_idx = []
            final_can_values_time = []
            # No can detection at all
            if len(np.argwhere(tssDetectedValue != 251)) != 0:
                can_set_values_idx = self.splitme_zip(
                    np.argwhere(tssDetectedValue != 251).reshape(np.argwhere(tssDetectedValue != 251).shape[1],
                                                                 np.argwhere(tssDetectedValue != 251).shape[0]))
                can_set_values_time = [self.can_data['TSSDetectedValue'][0][i[0]:i[-1] + 1] for i in can_set_values_idx]

                for can_item_idx, can_time_idx in zip(can_set_values_idx, can_set_values_time):
                    ret = self.checkForContinuity(tssDetectedValue[can_item_idx[0]:(can_item_idx[-1] + 1)])
                    for idx in ret:
                        final_can_values_idx.append(can_item_idx[idx[0]:(idx[-1] + 1)])
                        final_can_values_time.append(can_time_idx[idx[0]:(idx[-1] + 1)])

                return final_can_values_idx, final_can_values_time
            else:
                return [], []
        elif self.propTSRAlone_data != {}:
            tsr_SpeedLimit1_E8_sE8 = self.propTSRAlone_data['TSR_SpeedLimit1_E8_sE8'][1]
            final_SpeedLimit1values_idx = []
            final_SpeedLimit1values_time = []
            # No can detection at all
            if len(np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0)) != 0:
                can_set_values_idx = self.splitme_zip(
                    np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).reshape(np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).shape[1],
                                                                     np.argwhere(tsr_SpeedLimit1_E8_sE8 != 0).shape[0]))
                can_set_values_time = [self.propTSRAlone_data['TSR_SpeedLimit1_E8_sE8'][0][i[0]:i[-1] + 1] for i in
                                       can_set_values_idx]

                for can_item_idx, can_time_idx in zip(can_set_values_idx, can_set_values_time):
                    ret = self.checkForContinuity(tsr_SpeedLimit1_E8_sE8[can_item_idx[0]:(can_item_idx[-1] + 1)])
                    for idx in ret:
                        final_SpeedLimit1values_idx.append(can_item_idx[idx[0]:(idx[-1] + 1)])
                        final_SpeedLimit1values_time.append(can_time_idx[idx[0]:(idx[-1] + 1)])

                return final_SpeedLimit1values_idx, final_SpeedLimit1values_time
            else:
                return [], []
        # If both signals are not present
        else:
            return [], []

    def evaluateKpi(self):
        can_set_values_idx, can_set_values_time = self.get_CAN_signal_Data_idx_time()
        mapping_dict = {}
        can_data = {}
        gt_dict = {}

        # CAN data calculation
        for timelst, idx in zip(can_set_values_time, can_set_values_idx):
            can_signals = {}
            for alias, signal in self.can_data.items():
                try:
                    can_signals[alias] = signal[1][idx[0]]
                except Exception as e:
                    print(str(e))
            can_signals['can_duration'] = float(timelst[-1] - timelst[0])
            can_data[int(timelst[0])] = range(int(timelst[0]), int(timelst[-1])), can_signals

        for gt in self.gtObj:
            gt_dict[gt['resim_time']] = gt

        for gt_time in sorted(gt_dict.keys(), reverse=True):
            mapping_dict[gt_time] = []

            # Map CAN data to GT if exact timestamp is matching
            flag = 0
            for can in can_data.values():
                # can_last : just to check starting 5 timestamp
                # Its required in case of close detection
                can_last = 5
                if can_last > len(can[0]):
                    can_last = len(can[0])
                if int(gt_time) in can[0][:can_last]:
                    mapping_dict[gt_time].append(gt_dict[gt_time])
                    mapping_dict[gt_time].append(can[1])
                    can_data.pop(can[0][0])
                    flag = 1

            # Late Marking in CAN
            if flag == 0:
                for can in can_data.values():
                    can_last = 5
                    if can_last > len(can[0]):
                        can_last = len(can[0])
                    if int(gt_time) + 1 in can[0][:can_last] or int(gt_time) + 2 in can[0][:can_last]:
                        mapping_dict[gt_time].append(gt_dict[gt_time])
                        mapping_dict[gt_time].append(can[1])
                        can_data.pop(can[0][0])

            # In case there is no CAN detected value for current GT
            if mapping_dict[gt_time] == []:
                can_signals = {}
                can_signal_index = np.argmax(self.can_data["TSSCurrentRegion"][0] >= gt_time)
                for alias, signal in self.can_data.items():
                    try:
                        can_signals[alias] = signal[1][can_signal_index]
                    except Exception as e:
                        print("No Can Data")
                can_signals['can_duration'] = 0

                mapping_dict[gt_time].append(gt_dict[gt_time])
                mapping_dict[gt_time].append(can_signals)

        # Now can_data has extra can values 
        # mapping_dict has GT timestamp and its respective CAN timestamps

        # Event classification start-----------------------

        # 1.False Positive Type 2: not GT at all, but some value reflected on CAN (Ghost sign)
        # [no ground truth at all] -- [FLC_PROP1.TSS_DetectedValue] (Ghost sign)
        gt_time = gt_dict.keys()
        for xtra_can in can_data.values():
            gt = {}
            idx_to_gtinfo = bisect.bisect_left(gt_time, xtra_can[0][0])
            if idx_to_gtinfo > 0:
                idx_to_gtinfo = idx_to_gtinfo - 1

            gt["verdict"] = "False Positive Type 2"
            gt["weather_condition"] = self.gtObj[idx_to_gtinfo]['weather_condition']
            gt['time_condition'] = self.gtObj[idx_to_gtinfo]['time_condition']

            gt['conti_sign_class'] = xtra_can[1]['TSSDetectedValue']
            self.kpi['false_positive_type_2'].append(xtra_can[1]['TSSDetectedValue'])
            self.report[(xtra_can[0][0], gt['conti_sign_class'])] = gt, xtra_can[1]

        for item in mapping_dict.values():
            gt = item[0]
            can = item[1]
            # When existence is True or sign is relevant to the ego
            if gt['status']:
                # sign_value_for_can == None means it's a valid NA sign
                if gt['sign_value_for_can'] is not None:

                    # False Negative:  should be detected, but is not reflected on CAN
                    # [ground truth + existence = true] == 251
                    if can['TSSDetectedValue'] == 251:
                        gt["verdict"] = "False Negative"
                        self.kpi['false_negative'] += gt['sign_quantity']
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # True Positive:  should be detected & is reflected on CAN
                    # [ground truth + existence = true] == [FLC_PROP1.TSS_DetectedValue]
                    elif int(gt['sign_value_for_can']) == int(can['TSSDetectedValue']):
                        self.kpi['true_positive'] += gt['sign_quantity']
                        gt["verdict"] = "True Positive"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # False Positive Type 3:  should be detected, but is wrongly reflected on CAN
                    # [ground truth + existence = true] =! [FLC_PROP1.TSS_DetectedValue] && != 251
                    elif int(gt['sign_value_for_can']) != int(can['TSSDetectedValue']) and int(
                            can['TSSDetectedValue']) != 251:
                        self.kpi['false_positive_type_3'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 3"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                else:
                    # For NA sign no updates in CAN
                    if can['TSSDetectedValue'] == 251:
                        self.kpi['true_positive'] += gt['sign_quantity']
                        gt["verdict"] = "True Positive"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                    # For NA sign wrong value in CAN instead of 251
                    else:
                        self.kpi['false_positive_type_3'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 3"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

            # When existence is False or sign is irrelevant to the ego
            else:
                # sign_value_for_can == None means it's a valid NA sign
                if gt['sign_value_for_can'] is None:
                    if int(can['TSSDetectedValue']) == 251:
                        self.kpi['false_positive_type_1'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 1"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                    else:
                        self.kpi['true_negative'] += gt['sign_quantity']
                        gt["verdict"] = "True Negative"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                else:
                    # True Negative:  shouldn't be detected &  not reflected on CAN
                    # [ground truth + existence = false] != [FLC_PROP1.TSS_DetectedValue] || == 251
                    if int(gt['sign_value_for_can']) != int(can['TSSDetectedValue']) or int(
                            can['TSSDetectedValue']) == 251:
                        self.kpi['true_negative'] += gt['sign_quantity']
                        gt["verdict"] = "True Negative"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # False Positive Type 1:  shouldn't be detected, but is reflected on CAN
                    # [ground truth + existence = false] == [FLC_PROP1.TSS_DetectedValue]
                    elif int(gt['sign_value_for_can']) == int(can['TSSDetectedValue']):
                        self.kpi['false_positive_type_1'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 1"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

        # Event classification end-----------------------
        # cumulative_results calculation

        self.cumulative_results['TP'] = self.kpi['true_positive']
        self.cumulative_results['FN'] = self.kpi['false_negative']
        self.cumulative_results['FP1'] = self.kpi['false_positive_type_1']
        self.cumulative_results['FP2'] = len(self.kpi['false_positive_type_2'])
        self.cumulative_results['FP3'] = self.kpi['false_positive_type_3']
        self.cumulative_results['FP'] = self.cumulative_results['FP1'] + self.cumulative_results['FP2'] + \
                                        self.cumulative_results['FP3']
        self.cumulative_results['TN'] = self.kpi['true_negative']
        self.cumulative_results['Total_GT'] = self.false_existance_gt + self.true_existance_gt
        self.cumulative_results["GT_existance_false"] = self.false_existance_gt
        self.cumulative_results["GT_existance_true"] = self.true_existance_gt
        self.displayData()
        return self.cumulative_results, self.report

    def evaluatePropTSRAloneKpi(self):
        # Here PropTSRAlone signals are considered as CAN Data
        can_set_values_idx, can_set_values_time = self.get_CAN_signal_Data_idx_time()
        mapping_dict = {}
        propTSRAlone_data = {}
        gt_dict = {}
        propTSRAlone_used ={}
        #-------------------------------------------------------------------------------------------------------

        non_spd_lim_mapping = {0:0,278200: 29, 278300: 29, 282000: 30, 310000: 31, 311000: 32
            , 331000: 35, 336000: 36}
        explicit_spd_lim = {0: 0, 1: 5, 2: 10, 3: 15, 4: 20, 5: 25, 6: 30, 7: 35, 8: 40, 9: 45, 10: 50, 11: 55,
                            12: 60, 13: 65,
                            14: 70, 15: 75, 16: 80, 17: 85, 18: 90, 19: 95, 20: 100, 21: 105, 22: 110,
                            23: 115, 24: 120, 25: 125,
                            26: 130, 27: 135, 28: 140}
        #---------------------------------------------------------------------------------------------------------
        # CAN data calculation
        for timelst, idx in zip(can_set_values_time, can_set_values_idx):
            can_signals = {}
            for alias, signal in self.propTSRAlone_data.items():
                try:
                    can_signals[alias] = signal[1][idx[0]]
                except Exception as e:
                    print(str(e))
            can_signals['can_duration'] = float(timelst[-1] - timelst[0])
            propTSRAlone_data[int(timelst[0])] = range(int(timelst[0]), int(timelst[-1])), can_signals

        for gt in self.gtObj:
            gt_dict[gt['resim_time']] = gt

        for gt_time in sorted(gt_dict.keys(), reverse=True):
            mapping_dict[gt_time] = []

            # Map CAN data to GT if exact timestamp is matching
            # Late Marking in CAN

            exact_gt_match=0
            exact_time_match=0

            temp_gt = {}
            temp_can = {}
            temp_propTSRAlone_used = {}

            for can in propTSRAlone_data.values():

                if int(gt_time) in can[0]:
                    temp_gt=gt_dict[gt_time]
                    temp_can=can[1]
                    temp_propTSRAlone_used= can
                    exact_time_match=1

                    if explicit_spd_lim.has_key(can[1]["TSR_SpeedLimit1_E8_sE8"]) and gt_dict[gt_time]['sign_value_for_can'] != None:
                        can_detection= explicit_spd_lim[can[1]["TSR_SpeedLimit1_E8_sE8"]]
                        gt_detection = gt_dict[gt_time]['sign_value_for_can']

                        if int(gt_detection) == can_detection:
                            mapping_dict[gt_time].append(gt_dict[gt_time])
                            mapping_dict[gt_time].append(can[1])
                            propTSRAlone_used[can[0][0]] = can
                            # propTSRAlone_data.pop(can[0][0])
                            exact_gt_match=1
                            break
                            # propTSRAlone_data.pop(can[0][0])
                    elif non_spd_lim_mapping.has_key(gt_dict[gt_time]['conti_sign_class']):
                        gt_detection = gt_dict[gt_time]['conti_sign_class']
                        can_detection_value = non_spd_lim_mapping[gt_detection]

                        if can[1]["TSR_SpeedLimit1_E8_sE8"] == can_detection_value:
                            mapping_dict[gt_time].append(gt_dict[gt_time])
                            mapping_dict[gt_time].append(can[1])
                            propTSRAlone_used[can[0][0]] = can
                            # propTSRAlone_data.pop(can[0][0])
                            exact_gt_match=1
                            break

                # Late detection
                for can in propTSRAlone_data.values():
                    can_last = 5
                    if can_last > len(can[0]):
                        can_last = len(can[0])
                    if int(gt_time) + 1 in can[0][:can_last] or int(gt_time) + 2 in can[0][:can_last]:

                        if explicit_spd_lim.has_key(can[1]["TSR_SpeedLimit1_E8_sE8"]) and gt_dict[gt_time]['sign_value_for_can'] != None:
                            can_detection= explicit_spd_lim[can[1]["TSR_SpeedLimit1_E8_sE8"]]
                            gt_detection = gt_dict[gt_time]['sign_value_for_can']

                            if int(gt_detection) == can_detection:
                                mapping_dict[gt_time].append(gt_dict[gt_time])
                                mapping_dict[gt_time].append(can[1])
                                propTSRAlone_used[can[0][0]] = can
                                # propTSRAlone_data.pop(can[0][0])
                                exact_gt_match=1
                                break
                                # propTSRAlone_data.pop(can[0][0])
                        elif non_spd_lim_mapping.has_key(gt_dict[gt_time]['conti_sign_class']):
                            gt_detection = gt_dict[gt_time]['conti_sign_class']
                            can_detection_value = non_spd_lim_mapping[gt_detection]

                            if can[1]["TSR_SpeedLimit1_E8_sE8"] == can_detection_value:
                                mapping_dict[gt_time].append(gt_dict[gt_time])
                                mapping_dict[gt_time].append(can[1])
                                propTSRAlone_used[can[0][0]] = can
                                # propTSRAlone_data.pop(can[0][0])
                                exact_gt_match=1
                                break
                            # propTSRAlone_data.pop(can[0][0])
            if exact_gt_match != 1 and exact_time_match==1:
                mapping_dict[gt_time].append(temp_gt)
                mapping_dict[gt_time].append(temp_can)
                propTSRAlone_used[can[0][0]] = temp_propTSRAlone_used

            # In case there is no CAN detected value for current GT
            if mapping_dict[gt_time] == []:
                propTSRAlone_signals = {}
                can_signal_index = np.argmax(self.propTSRAlone_data["TSR_SpeedLimit1_E8_sE8"][0] >= gt_time)
                for alias, signal in self.propTSRAlone_data.items():
                    try:
                        propTSRAlone_signals[alias] = signal[1][can_signal_index]
                    except Exception as e:
                        print("No Prop_TSRAlone Data")
                propTSRAlone_signals['can_duration'] = 0

                mapping_dict[gt_time].append(gt_dict[gt_time])
                mapping_dict[gt_time].append(propTSRAlone_signals)

        # Now propTSRAlone_data has extra can values
        # mapping_dict has GT timestamp and its respective CAN timestamps

        # Event classification start-----------------------


        # 1.False Positive Type 2: not GT at all, but some value reflected on CAN (Ghost sign)
        # Ford:[no ground truth] && [PropTSRAlone.TSRSpeedLimit1] != 0

        gt_time = gt_dict.keys()
        xtra_propTSRALone_keys = set(propTSRAlone_data) - set(propTSRAlone_used)
        for xtra_can_key in propTSRAlone_data.keys():  # propTSRAlone_data has only xtra detection at this stage
            xtra_can= {}
            if xtra_can_key in xtra_propTSRALone_keys:
                xtra_can = propTSRAlone_data[xtra_can_key]
                gt = {}
                idx_to_gtinfo = bisect.bisect_left(gt_time, xtra_can[0][0])
                if idx_to_gtinfo > 0:
                    idx_to_gtinfo = idx_to_gtinfo - 1

                gt["verdict"] = "False Positive Type 2"
                gt["weather_condition"] = self.gtObj[idx_to_gtinfo]['weather_condition']
                gt['time_condition'] = self.gtObj[idx_to_gtinfo]['time_condition']

                gt['conti_sign_class'] = xtra_can[1]['TSR_SpeedLimit1_E8_sE8']
                self.kpi['false_positive_type_2'].append(xtra_can[1]['TSR_SpeedLimit1_E8_sE8'])
                self.report[(xtra_can[0][0], gt['conti_sign_class'])] = gt, xtra_can[1]

        for item in mapping_dict.values():
            gt = item[0]
            can = item[1]
            non_spd_lim_mapping_val=non_spd_lim_mapping.values()
            if explicit_spd_lim.has_key(can["TSR_SpeedLimit1_E8_sE8"]):
                can_explicit_spd = explicit_spd_lim[can["TSR_SpeedLimit1_E8_sE8"]]

            elif can["TSR_SpeedLimit1_E8_sE8"] in non_spd_lim_mapping.values():
                for (key,val) in non_spd_lim_mapping.items():
                    if val==can["TSR_SpeedLimit1_E8_sE8"]:
                        can_explicit_spd = key
                        break

            # When existence is True or sign is relevant to the ego
            if gt['status']:
                # sign_value_for_can == None means it's a valid NA sign
                if gt['sign_value_for_can'] is not None:
                    # False Negative:  should be detected, but is not reflected on CAN
                    # Ford: [ground truth + 'existence = true'] != [PropTSRAlone.TSRSpeedLimit1] && [PropTSRAlone.TSRSpeedLimit1] == 0
                    if (can_explicit_spd == 0 and can_explicit_spd != int(
                            gt['sign_value_for_can'])):
                        gt["verdict"] = "False Negative"
                        self.kpi['false_negative'] += gt['sign_quantity']
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # True Positive:  should be detected & is reflected on CAN
                    # Ford:        [ground truth + 'existence = true'] == [PropTSRAlone.TSRSpeedLimit1]
                    elif int(gt['sign_value_for_can']) == can_explicit_spd:
                        self.kpi['true_positive'] += gt['sign_quantity']
                        gt["verdict"] = "True Positive"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # False Positive Type 3:  should be detected, but is wrongly reflected on CAN Ford: [ground truth
                    # + 'existence = true'] != [PropTSRAlone.TSRSpeedLimit1] && [PropTSRAlone.TSRSpeedLimit1] != 0
                    elif (int(gt['sign_value_for_can']) != can_explicit_spd and can_explicit_spd != 0):
                        self.kpi['false_positive_type_3'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 3"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                # For non speed limit signs
                # Here can_explicit_spd will caculated as per GT class
                elif non_spd_lim_mapping.has_key(gt["conti_sign_class"]):
                    # False Negative:  should be detected, but is not reflected on CAN
                    # Ford: [ground truth + 'existence = true'] != [PropTSRAlone.TSRSpeedLimit1] && [PropTSRAlone.TSRSpeedLimit1] == 0
                    if non_spd_lim_mapping[gt["conti_sign_class"]] != int(can["TSR_SpeedLimit1_E8_sE8"]) and int(can["TSR_SpeedLimit1_E8_sE8"]) == 0:
                        gt["verdict"] = "False Negative"
                        self.kpi['false_negative'] += gt['sign_quantity']
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # True Positive:  should be detected & is reflected on CAN
                    # Ford:        [ground truth + 'existence = true'] == [PropTSRAlone.TSRSpeedLimit1]
                    elif non_spd_lim_mapping[gt["conti_sign_class"]] == int(can["TSR_SpeedLimit1_E8_sE8"]):
                        self.kpi['true_positive'] += gt['sign_quantity']
                        gt["verdict"] = "True Positive"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # False Positive Type 3:  should be detected, but is wrongly reflected on CAN Ford: [ground truth
                    # + 'existence = true'] != [PropTSRAlone.TSRSpeedLimit1] && [PropTSRAlone.TSRSpeedLimit1] != 0
                    elif non_spd_lim_mapping[gt["conti_sign_class"]] != int(
                            can["TSR_SpeedLimit1_E8_sE8"]) and int(can["TSR_SpeedLimit1_E8_sE8"]) != 0:
                        self.kpi['false_positive_type_3'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 3"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

            # When existence is False or sign is irrelevant to the ego
            else:
                # sign_value_for_can == None means it's a valid NA sign
                if non_spd_lim_mapping.has_key(gt["conti_sign_class"]):
                    if non_spd_lim_mapping[gt["sign_class"]] == can_explicit_spd:
                        self.kpi['false_positive_type_1'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 1"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                    else:
                        self.kpi['true_negative'] += gt['sign_quantity']
                        gt["verdict"] = "True Negative"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can
                else:
                    # True Negative:  shouldn't be detected &  not reflected on CAN
                    # [ground truth + existence = false] != [FLC_PROP1.TSS_DetectedValue] || == 251
                    if int(gt['sign_value_for_can']) != can_explicit_spd or int(
                            can_explicit_spd) == 0:
                        self.kpi['true_negative'] += gt['sign_quantity']
                        gt["verdict"] = "True Negative"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

                    # False Positive Type 1:  shouldn't be detected, but is reflected on CAN
                    # [ground truth + existence = false] == [FLC_PROP1.TSS_DetectedValue]
                    elif int(gt['sign_value_for_can']) == can_explicit_spd:
                        self.kpi['false_positive_type_1'] += gt['sign_quantity']
                        gt["verdict"] = "False Positive Type 1"
                        self.report[(gt['resim_time'], gt['conti_sign_class'])] = gt, can

        # Event classification end-----------------------
        # cumulative_results calculation

        self.cumulative_results['TP'] = self.kpi['true_positive']
        self.cumulative_results['FN'] = self.kpi['false_negative']
        self.cumulative_results['FP1'] = self.kpi['false_positive_type_1']
        self.cumulative_results['FP2'] = len(self.kpi['false_positive_type_2'])
        self.cumulative_results['FP3'] = self.kpi['false_positive_type_3']
        self.cumulative_results['FP'] = self.cumulative_results['FP1'] + self.cumulative_results['FP2'] + \
                                        self.cumulative_results['FP3']
        self.cumulative_results['TN'] = self.kpi['true_negative']
        self.cumulative_results['Total_GT'] = self.false_existance_gt + self.true_existance_gt
        self.cumulative_results["GT_existance_false"] = self.false_existance_gt
        self.cumulative_results["GT_existance_true"] = self.true_existance_gt
        self.displayData()
        return self.cumulative_results, self.report

    def displayData(self):
        print ("Cumulative_results:\n{}".format(self.cumulative_results))
        print ("Report:")
        for key in self.report:
            print ("\n{}".format(self.report[key]))