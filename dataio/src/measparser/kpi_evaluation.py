import copy
import math
import sys
import os
import matplotlib.pyplot as plt
import numpy
import numpy as np
import json
from natsort import natsorted
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

TSR_SIGNS_FILE_PATH = os.path.join(os.path.dirname(__file__), "config", "SR_sign_classes.txt")
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images\{}.png")


class TSRKpiEvaluation():
    def __init__(self, kpi_input_data):

        if not os.path.isfile(TSR_SIGNS_FILE_PATH):
            raise IOError("TSR Traffic sign class text file missing from: {}".format(TSR_SIGNS_FILE_PATH))
        if not os.path.exists(os.path.dirname(IMAGE_DIRECTORY)):
            raise IOError("TSR Sign class images missing from: {}".format(IMAGE_DIRECTORY))
        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.detCmpObjects = kpi_input_data['detection_compare_objects']['detection_compare_objectbuffer']
        self.folder_path = os.path.dirname(self.filename)
        self.nameOfFile = self.filename.split('\\')[-3]
        self.gtDet = np.array(self.detCmpObjects['postmarker_detection'], dtype=int).tolist()
        self.contiDet = np.array(self.detCmpObjects['conti_detection'], dtype=int)
        self.gtObj = kpi_input_data['postmarker_objects']
        self.contiTSRObj = kpi_input_data['conti_tsr_objects']
        self.txtFilePath = TSR_SIGNS_FILE_PATH
        self.imgFilePath = IMAGE_DIRECTORY
        self.KBSupplementarySignList = [104812, 104811, 104030, 105236, 100100, 100400]
        self.intersectionOfGTContiIdx = []
        self.disjointOfGTContiIdx = []
        self.gtInfo = {}
        self.gtIdxRange = []
        self.contiInfo = {}
        self.cmpGTContiInfo = {}
        self.fp2Info = {}
        self.gtIdx = self.gtInfo.keys()
        self.KBTSRList = []
        self.kpi = {}
        # self.jsonObjected = {}
        self.kpi['true_positive'] = 0
        self.kpi['false_positive'] = 0
        self.kpi['false_negative'] = 0
        self.kpi['tp_duplicate_id'] = []
        self.kpi['fp_error1_uid'] = []
        self.kpi['fp_error2_uid'] = []
        self.kpi['tp_list'] = []

        self.kpi['predicted_sig_class_id'] = []
        self.kpi['gt signal id'] = []
        self.newTPEvent = {}
        self.newFNEvent = {}
        self.newFPEvent = {}
        self.kpi['supplementary_sign'] = {}
        self.kpi['supplementary_sign']['true_positive'] = 0
        self.kpi['supplementary_sign']['fp_error1'] = 0
        self.kpi['supplementary_sign']['fp_error2'] = 0
        self.kpi['supplementary_sign']['false_positive'] = 0
        self.kpi['supplementary_sign']['false_negative'] = 0
        self.kpi['supplementary_sign']['tp'] = {}
        self.kpi['supplementary_sign']['tp']['uid'] = []
        self.kpi['supplementary_sign']['tp']['time'] = []
        self.kpi['supplementary_sign']['fp_error1'] = {}
        self.kpi['supplementary_sign']['fp_error1']['uid'] = []
        self.kpi['supplementary_sign']['fp_error1']['time'] = []
        self.kpi['supplementary_sign']['fp'] = {}
        self.kpi['supplementary_sign']['fp']['time'] = []
        self.kpi['supplementary_sign']['fp_error2'] = {}
        self.kpi['supplementary_sign']['fp_error2']['uid'] = []
        self.kpi['supplementary_sign']['fp_error2']['time'] = []
        self.kpi['supplementary_sign']['fn'] = {}
        self.kpi['supplementary_sign']['fn']['uid'] = []
        self.kpi['supplementary_sign']['fn']['time'] = []

        self.report = {}
        self.cumulative_results = {}

    def __keysExist(self, element, *keys):
        if not isinstance(element, dict):
            raise AttributeError('keys_exists() expects dict as first argument.')
        if len(keys) == 0:
            raise AttributeError('keys_exists() expects at least two arguments, one given.')
        _element = element
        for key in keys:
            try:
                _element = _element[key]
            except KeyError:
                return False
        return True

    def truncateValues(self, value):
        return math.floor(value * 10 ** 1) / 10 ** 1

    def __convertToList(self, buffer):
        return buffer

    # reading and formatting line from SR_sign_classes.txt
    def createKBTSRList(self):
        try:
            with open(self.txtFilePath, "r") as file:
                lines = [line.rstrip() for line in file.readlines()]
            for loopCount in range(0, len(lines)):
                lines[loopCount] = int(lines[loopCount])
            if __debug__:
                print("\nKB TSR List : " + str(lines))
            self.KBTSRList = lines

        except OSError as err:
            print("OS error: {0}".format(err))
            raise

        except ValueError:
            print(
                "Please check the file for : Format error / Float values within file / Spaces / Empty lines in the end / check against ref file.")
            raise

        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    # Creating ground truth info from json
    def createGTInfo(self):
        global GtIdxWindowRange
        GtIdxWindowRange = 40
        for loopCount in range(len(self.gtDet)):
            if self.gtDet[loopCount] == 1:
                tmp_supplementary_sign = []
                tmp_supplementary_sign_quantity = []
                tmp_sign_class_id = []
                tmp_sign_quantity = []
                tmp_time = []
                tmp_index = []
                tmp_weather_condition = []
                tmp_time_condition = []
                self.gtInfo[loopCount] = {}
                bufferNumber = 0
                for gtObjectBufferId in self.gtObj.keys():
                    bufferNumber = bufferNumber + 1
                    gtBuffer = self.gtObj[gtObjectBufferId]
                    gt_sign_class_id = gtBuffer['sign_class_id'][loopCount]
                    gt_quantity = gtBuffer['quantity'][loopCount]
                    gt_time = gtBuffer['time'][loopCount]
                    gt_weather_condition = gtBuffer['weather_condition'][loopCount]
                    gt_time_condition = gtBuffer['time_condition'][loopCount]

                    if (gt_sign_class_id > 0):  # to ensure id is not carring junk value
                        if bufferNumber >= 2:  # 0th and 1st buffer -- main traffic sign
                            if gt_sign_class_id in self.KBSupplementarySignList:
                                if __debug__:
                                    print('For Index:', loopCount, 'Postmarker contains a supplementary sign:',
                                          gt_sign_class_id)
                                tmp_supplementary_sign.append(gt_sign_class_id)
                                tmp_supplementary_sign_quantity.append(gt_quantity)
                                self.gtInfo[loopCount]['supplementary_sign'] = tmp_supplementary_sign
                                self.gtInfo[loopCount]['supplementary_sign_quantity'] = tmp_supplementary_sign_quantity
                            else:
                                tmp_sign_class_id.append(gt_sign_class_id)
                                tmp_sign_quantity.append(gt_quantity)
                                tmp_time.append(gt_time)
                                tmp_weather_condition.append(gt_weather_condition)
                                tmp_time_condition.append(gt_time_condition)
                                tmp_index = [loopCount, (loopCount + GtIdxWindowRange)]
                        else:
                            tmp_sign_class_id.append(gt_sign_class_id)
                            tmp_sign_quantity.append(gt_quantity)
                            tmp_time.append(gt_time)
                            tmp_weather_condition.append(gt_weather_condition)
                            tmp_time_condition.append(gt_time_condition)
                            tmp_index.extend([loopCount, (loopCount + GtIdxWindowRange)])

                    self.gtInfo[loopCount]['sign_class_id'] = tmp_sign_class_id
                    self.gtInfo[loopCount]['quantity'] = tmp_sign_quantity
                    self.gtInfo[loopCount]['time'] = tmp_time
                    self.gtInfo[loopCount]['index'] = tmp_index
                    self.gtInfo[loopCount]['weather_condition'] = tmp_weather_condition
                    self.gtInfo[loopCount]['time_condition'] = tmp_time_condition

        for keyz in self.gtInfo.keys():
            self.gtIdxRange.append(self.gtInfo[keyz][
                                       'index'])  ##GtIdxWindowRange = 100, to consider GTIdx at two different point of time/index instead of one. self.gtIdx[counterx] -> firstpoint of GT marking ; self.gtIdx[counterx] +100 -> Secondpoint of same GT marking.

        try:
            self.gtIdxRange = sorted([item for sublist in self.gtIdxRange for item in sublist])
        except Exception as e:
            print("Exception occured for gtIdxRange ")
        print('---', len(self.gtInfo))
        print("gtInfo:", self.gtInfo)
        if __debug__:
            print(self.gtInfo.keys())

    # creating conti info for TSR lmk from .h5 file
    def createContiInfo(self):
        tmpTime = numpy.empty((self.contiDet.size, 1))
        tmpUid = numpy.empty((self.contiDet.size, 1))
        tmpTrafficSignId = numpy.empty((self.contiDet.size, 1))
        tmpStatus = numpy.empty((self.contiDet.size, 1))
        tmpSupplSignId = numpy.empty((self.contiDet.size, 1))

        for contiTSRBufferId in natsorted(self.contiTSRObj.keys()):
            contiBuffer = self.contiTSRObj[contiTSRBufferId]
            tmpTimeAsFloat = []
            for loopCount in range(self.contiDet.size):
                tmp = contiBuffer['time'][loopCount].astype(float)
                tmpTimeAsFloat.append(self.truncateValues(tmp))
            contiTime = numpy.asarray(tmpTimeAsFloat)
            contiTime = numpy.reshape(contiTime, (self.contiDet.size, 1))
            tmpTime = numpy.append(tmpTime, contiTime, axis=1)

            tmpUid = numpy.column_stack((tmpUid, self.__convertToList(contiBuffer['uid'])))
            tmpTrafficSignId = numpy.column_stack(
                (tmpTrafficSignId, self.__convertToList(contiBuffer['traffic_sign_id'])))
            tmpStatus = numpy.column_stack((tmpStatus, self.__convertToList(contiBuffer['status'])))
            tmpSupplSignId = numpy.column_stack((tmpSupplSignId, self.__convertToList(contiBuffer['suppl_sign_ids'])))

        self.contiInfo['consolidated_time'] = numpy.delete(tmpTime, 0, 1)  # just to ignore 0s from numpy array
        self.contiInfo['consolidated_uid'] = numpy.delete(tmpUid, 0, 1)
        self.contiInfo['consolidated_traffic_sign_id'] = numpy.delete(tmpTrafficSignId, 0, 1)
        self.contiInfo['consolidated_status'] = numpy.delete(tmpStatus, 0, 1)
        self.contiInfo['consolidated_suppl_sign_id'] = numpy.delete(tmpSupplSignId, 0, 1)
        if __debug__:
            print('Shape of uID ndarray:', self.contiInfo['consolidated_uid'].shape)
            print('Shape of tsr_sign ndarray:', self.contiInfo['consolidated_traffic_sign_id'].shape)
            print('Shape of obj_status ndarray:', self.contiInfo['consolidated_status'].shape)
            print('Shape of conti_time_instance ndarray:', self.contiInfo['consolidated_time'].shape)

        tmpTime = numpy.zeros((1, self.contiInfo['consolidated_time'].shape[1]))
        tmpUid = numpy.zeros((1, self.contiInfo['consolidated_time'].shape[1]))
        tmpTrafficSignId = numpy.zeros((1, self.contiInfo['consolidated_time'].shape[1]))

        for loopCount in range(len(self.gtIdx)):
            gtIdx_x = list(self.gtIdx)[loopCount]
            contiTSRSign = self.contiInfo['consolidated_traffic_sign_id'][gtIdx_x][:]
            contiUid = self.contiInfo['consolidated_uid'][gtIdx_x][:]
            contiTime = self.contiInfo['consolidated_time'][gtIdx_x][:]

            tmpUid = numpy.row_stack((tmpUid, contiUid))
            tmpTrafficSignId = numpy.row_stack((tmpTrafficSignId, contiTSRSign))
            tmpTime = numpy.row_stack((tmpTime, contiTime))

        tmpTime = numpy.delete(tmpTime, 0, 0)
        tmpTrafficSignId = numpy.delete(tmpTrafficSignId, 0, 0)
        tmpUid = numpy.delete(tmpUid, 0, 0)
        self.contiInfo['filtered_traffic_sign_id'] = tmpTrafficSignId
        self.contiInfo['filtered_uid'] = tmpUid
        self.contiInfo['filtered_time'] = tmpTime
        print("ContiInfo:", self.contiInfo)

    # To show the conti detection info (qty and event classification)
    def createInfoToCompare(self):
        self.gtIdx = self.gtInfo.keys()
        self.cmpGTContiInfo = copy.deepcopy(self.gtInfo)
        for loopCount in range(len(self.gtIdx)):
            idx = list(self.gtIdx)[loopCount]
            self.cmpGTContiInfo[idx]['quantity'] = 0
            self.cmpGTContiInfo[idx]['Event'] = "FalseNegative"
            if self.__keysExist(self.gtInfo, idx, "supplementary_sign_quantity") is True:
                self.cmpGTContiInfo[idx]['supplementary_sign_quantity'] = 0
        if __debug__:
            print('GT Dict with QTY INFO            :', self.gtInfo)
            print('Conti Dict Updated with QTY INFO :', self.cmpGTContiInfo)
        print("compareInfo:", self.cmpGTContiInfo)

    def fetchUniqueUids(self):
        uniqueValues = (numpy.unique(self.contiInfo['consolidated_uid']).astype(int))
        # conti id can take any value in between 0-100000 [100000 is a rational value not confirmed by conti]
        uniqueValues = [x for x in uniqueValues if x <= 100000]
        uniqueValues = [x for x in uniqueValues if x >= 0]
        self.contiInfo['unique_uid'] = []
        for loopCount in range(len(uniqueValues)):
            if uniqueValues[loopCount] != 0:
                self.contiInfo['unique_uid'].append(uniqueValues[loopCount])

        if __debug__:
            print('uniqueValues', self.contiInfo['unique_uid'])

    def findIdxOfAGivenUid(self, uid):
        return numpy.where((self.contiInfo['consolidated_uid'] == (uid)))

    def checkForContinuity(self, src):
        ret = [next - current for current, next in zip(src, src[1:])]
        ret.insert(0, 0)  # 0 = start point
        ret.append(999999999999999999)  # to mark end
        return ret

    def updateKpiAsTpOrFp(self, idxToGT, contiUid, detection, contiBufferId, tpQty,
                          fpQty):
        idxToGT = idxToGT[0]

        contiuidList = []
        duplicateDetIdx = 0
        if self.gtInfo.has_key(
                idxToGT) is False:  ##if this condition is pass, it means the second GT point is considered
            duplicateDetIdx = idxToGT
            idxToGT = idxToGT - GtIdxWindowRange
            # self.gtInfo.get(idxToGT)
            gt = self.gtInfo[idxToGT]['sign_class_id'][0]
            gt_qua = self.gtInfo[idxToGT]['quantity'][0]
            detectionTime = self.contiInfo['consolidated_time'][idxToGT]
            detectedQuantity = self.cmpGTContiInfo[idxToGT]['quantity']
        else:
            # self.gtInfo.get(idxToGT)
            gt = self.gtInfo[idxToGT]['sign_class_id'][0]
            gt_qua = self.gtInfo[idxToGT]['quantity'][0]
            detection = int(detection)
            detectionTime = self.cmpGTContiInfo[idxToGT]['time'][0]
            detectedQuantity = self.cmpGTContiInfo[idxToGT]['quantity']
            if __debug__:
                print('@[idx]:', idxToGT, '\nConti Dict=', self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=',
                      self.gtInfo.get(idxToGT))
                print('\ngtx:', gt, 'c_sign_class_id', detection)
        # to check TP based on sign ID
        if gt == detection:
            detectedQuantity = detectedQuantity + 1
            self.cmpGTContiInfo[idxToGT]['quantity'] = detectedQuantity
            gtInfoAtIdx = self.gtInfo.get(idxToGT)

            if self.cmpGTContiInfo[idxToGT]['quantity'] > self.gtInfo[idxToGT]['quantity'][
                0]:  # To check duplicate TP events containing same sign based on GT qty
                self.kpi['true_positive'] = self.kpi['true_positive']
                self.kpi['tp_duplicate_id'].append(contiUid)
                fpQty = self.cmpGTContiInfo[idxToGT]['quantity'] - self.gtInfo[idxToGT]['quantity'][0]#self.kpi['true_positive'] - fpQty
                if self.newFPEvent.has_key(str(int(detection))):
                    self.newFPEvent[str(int(detection))] += fpQty
                else:
                    self.newFPEvent[str(int(detection))] = fpQty
                # ------------------------------------------------ Condition for late detections------------------------------------------------
                if duplicateDetIdx != 0:
                    self.report[(detection, self.contiInfo['consolidated_time'][duplicateDetIdx][0])] = {
                        "verdict": "False Positive Type 2", "conti_uid": contiUid,
                        "contiBufferId": contiBufferId,
                        "weather_condition": str(self.cmpGTContiInfo[idxToGT]['weather_condition'][0]),
                        "time_condition": str(self.cmpGTContiInfo[idxToGT]['time_condition'][0])}
                else:
                    self.report[(detection, gtInfoAtIdx['time'][0])] = {"verdict": "False Positive Type 2",
                                                                        "conti_uid": contiUid,
                                                                        "contiBufferId": contiBufferId,
                                                                        "weather_condition": str(
                                                                            self.cmpGTContiInfo[idxToGT][
                                                                                'weather_condition'][0]),
                                                                        "time_condition": str(
                                                                            self.cmpGTContiInfo[idxToGT][
                                                                                'time_condition'][0])}
                # ------------------------------------------------
                if __debug__:
                    print('Since the TSR @[idx]:', idxToGT,
                          'conti_qty > gt_qty , it is a False Positive. \n -------------------------------------')
            else:  # Checking for TP
                if __debug__:
                    print('The TSR @[idx]:', idxToGT, 'is a', 'True Positive!', '\nConti Dict=',
                          self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=', gtInfoAtIdx,
                          '\n\n---------------------------------------------------------------------------------')
                self.kpi['true_positive'] = self.kpi['true_positive'] + 1
                self.kpi['tp_list'].append(contiUid)
                tpQty = self.kpi['true_positive'] - tpQty

                if self.newTPEvent.has_key(str(int(gt))):
                    self.newTPEvent[str(int(gt))] += tpQty
                else:
                    self.newTPEvent[str(int(gt))] = tpQty

                self.kpi['predicted_sig_class_id'].append(detection)
                self.kpi['gt signal id'].append(gt)
                self.cmpGTContiInfo[idxToGT]['Event'] = 'TruePositive'
                self.cmpGTContiInfo[idxToGT]['uID'] = contiUid
                self.report[(detection, gtInfoAtIdx['time'][0])] = {"verdict": "True Positive", "conti_uid": contiUid,
                                                                    "contiBufferId": contiBufferId,
                                                                    "weather_condition": str(
                                                                        self.cmpGTContiInfo[idxToGT][
                                                                            'weather_condition'][0]),
                                                                    "time_condition": str(
                                                                        self.cmpGTContiInfo[idxToGT]['time_condition'][
                                                                            0])}
        else:  # checking for FP type 1
            self.kpi['false_positive'] = self.kpi['false_positive'] + 1
            self.kpi['fp_error1_uid'].append(contiUid)
            self.kpi['predicted_sig_class_id'].append(detection)
            self.kpi['gt signal id'].append(gt)
            # w.r.t Contis detection
            if self.newFPEvent.has_key(str(int(detection))):
                self.newFPEvent[str(int(detection))] += 1
            else:
                self.newFPEvent[str(int(detection))] = 1
            # w.r.t GT marking
            if self.newFPEvent.has_key(str(int(gt))):
                self.newFPEvent[str(int(gt))] += 1
            else:
                self.newFPEvent[str(int(gt))] = 1

            gtInfoAtIdx = self.gtInfo.get(idxToGT)
            self.cmpGTContiInfo[idxToGT]['Event'] = 'FalsePositive'
            self.cmpGTContiInfo[idxToGT]['uID'] = contiUid
            self.report[(detection, gtInfoAtIdx['time'][0])] = {"verdict": "False Positive Type 1",
                                                                "conti_uid": contiUid, "contiBufferId": contiBufferId,
                                                                "weather_condition": str(
                                                                    self.cmpGTContiInfo[idxToGT]['weather_condition'][
                                                                        0]), "time_condition": str(
                    self.cmpGTContiInfo[idxToGT]['time_condition'][0])}  # gtInfoAtIdx['uId']}

            if __debug__:
                print('The TSR @[idx]:', idxToGT, 'is a', 'False Positive!', '\nConti Dict=',
                      self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=', gtInfoAtIdx,
                      '\n -------------------------------------')

    def evaluateSupplSign(self, commonIdx, bufferId, uId):
        startIdx = bufferId * 3
        endIdx = bufferId + 3
        value = self.contiInfo['consolidated_suppl_sign_id'][commonIdx][0, startIdx:endIdx]
        if (numpy.any(value) == True) and (numpy.any(value) in self.KBSupplementarySignList):
            supplementarySign = [numpy.nonzero(value)]
            gtSupplementarySign = self.gtInfo[commonIdx]['supplementary_sign']
            gtSupplementarySignQuantity = self.gtInfo[commonIdx]['supplementary_sign_quantity']
            if gtSupplementarySignQuantity != 0:
                if __debug__:
                    print('gt_supplementary_sign:', gtSupplementarySign, 'gt_supplementary_sign_quantity:',
                          gtSupplementarySignQuantity)
                    print('suppl_signs', supplementarySign)
                detectedQuantity = self.contiInfo[commonIdx]['supplementary_sign_quantity']
                if len(supplementarySign) < 2:
                    if gtSupplementarySign == supplementarySign[0]:
                        self.kpi['supplementary_sign']['true_positive'] = ['supplementary_sign']['true_positive'] + 1
                        detectedQuantity = detectedQuantity + 1
                        self.contiInfo[commonIdx]['supplementary_sign_quantity'] = detectedQuantity
                        self.kpi['supplementary_sign']['tp']['uid'].append(uId)
                        self.kpi['supplementary_sign']['tp']['time'].append(self.contiInfo[commonIdx]['time'])
                    else:
                        self.kpi['supplementary_sign']['fp_error1'] = self.kpi['supplementary_sign']['fp_error1'] + 1
                        if __debug__:
                            print('FP_suppl_sign_type1 Negative of Supplementary')
                        self.kpi['supplementary_sign']['fp_error1']['uid'].append(uId)
                        self.kpi['supplementary_sign']['fp_error1']['time'].append(self.contiInfo[commonIdx]['time'])
            else:
                self.kpi['supplementary_sign']['fp_error2'] = self.kpi['supplementary_sign']['fp_error2'] + 1
                if __debug__:
                    print('FP_suppl_sign_type2 Negative of Supplementary')
                self.kpi['supplementary_sign']['fp_error2']['uid'].append(uId)
                self.kpi['supplementary_sign']['fp_error2']['time'].append(self.contiInfo[commonIdx]['time'])

    def updateKpiForFN(self):
        # supplementary traffsigns
        fnQty = 0
        for loopCount in range(len(self.gtIdx)):
            gtIdx = list(self.gtIdx)[loopCount]
            if (self.__keysExist(self.gtInfo, gtIdx, "supplementary_sign")) is True:
                if __debug__:
                    print('Supplementary exists in GT:', self.__keysExist(self.gtInfo, gtIdx, "supplementary_sign"))
                gtSupplementarySign = self.gtInfo[gtIdx]['supplementary_sign']
                gtTime = self.gtInfo[gtIdx]['time']
                gtTimeTruncated = [round(num, 1) for num in gtTime]
                isSupplementarySignPresent = gtSupplementarySign in self.contiInfo['filtered_traffic_sign_id'][
                                                                        loopCount][:]
                self.kpi['supplementary_sign']['fp']['time'] = self.kpi['supplementary_sign']['fp_error1']['time'] + \
                                                               self.kpi['supplementary_sign']['fp_error2']['time']
                supplementaryTimeTruncated = [round(num, 1) for num in self.kpi['supplementary_sign']['fp']['time']]
                if __debug__:
                    print('CHECKing:', self.kpi['supplementary_sign']['fp']['time'])
                    print('GT Time:', gtTime, type(gtTime))
                isTimePresent = any(item in gtTimeTruncated for item in supplementaryTimeTruncated)
                if isSupplementarySignPresent is False and isTimePresent is False:
                    self.kpi['supplementary_sign']['false_negative'] = self.kpi['supplementary_sign'][
                                                                           'false_negative'] + 1
                    if __debug__:
                        print('False Negative for Supplementary sign @GroundTruth time', gtTime, 'Index:', gtIdx)
                    self.kpi['supplementary_sign']['fn']['uid'].append(gtIdx)
                    self.kpi['supplementary_sign']['fn']['time'].append(gtTime)

        # regular traffic signs
        for loopCount in range(len(self.gtInfo)):
            idx = list(self.gtInfo)[loopCount]
            gtQuantity = self.gtInfo[idx]['quantity'][0]
            try:
                start, end = self.gtInfo[idx]['index']
            except TypeError as e:
                start = self.gtInfo[idx]['index']
                end = start
            gtSignTd = self.gtInfo[idx]['sign_class_id'][0]
            if self.cmpGTContiInfo.has_key(start):
                detectedQuantity = self.cmpGTContiInfo[idx]['quantity']
                detectionTime = self.cmpGTContiInfo[idx]['time'][0]
            # elif self.cmpGTContiInfo.has_key(end):
            #     detectedQuantity = self.cmpGTContiInfo[idx]['quantity']
            #     detectionTime = self.cmpGTContiInfo[idx]['time'][0]
            else:
                detectedQuantity = 0
                detectionTime = self.cmpGTContiInfo[idx]['time'][0]

            # if start in key
            # detectedQuantity = self.cmpGTContiInfo[idx]['quantity']
            # detectionTime = self.cmpGTContiInfo[idx]['time'][0]

            if detectedQuantity < gtQuantity and (gtSignTd in self.KBTSRList):  ##TODO: False Negative Calculation
                self.report[(gtSignTd, detectionTime)] = {"verdict": "False Negative",
                                                          "conti_uid": 99999999, "contiBufferId": None,
                                                          "weather_condition": str(
                                                              self.cmpGTContiInfo[idx]['weather_condition'][
                                                                  0]), "time_condition": str(
                        self.cmpGTContiInfo[idx]['time_condition'][0])}
                self.kpi['false_negative'] = self.kpi['false_negative'] + (gtQuantity - detectedQuantity)
                # temp=fnQty
                fnQty = self.kpi['false_negative'] - fnQty
                if self.newFNEvent.has_key(str(int(gtSignTd))):
                    temp = self.newFNEvent[str(int(gtSignTd))]
                    self.newFNEvent[str(int(gtSignTd))] += (gtQuantity - detectedQuantity)
                else:
                    temp =0
                    self.newFNEvent[str(int(gtSignTd))] = (gtQuantity - detectedQuantity)

                searchedGTqty=0
                for sign, timestamp in self.report.keys():
                    # Removing duplicate event data of FP1 from FN
                    if (self.report.has_key((sign, timestamp))):# Too ignore deleted events
                        if self.report[(sign, timestamp)][
                            'verdict'] == "False Positive Type 1":  # To ignore already classified event in FP1 data
                            if timestamp == detectionTime:
                                if (self.report.has_key((gtSignTd, detectionTime))):  # Check FN event
                                    self.report.pop((gtSignTd, detectionTime))
                                    self.kpi['false_negative'] = self.kpi['false_negative'] - (
                                            gtQuantity - detectedQuantity)
                                    if self.newFNEvent.has_key(str(int(gtSignTd))):
                                        self.newFNEvent[str(int(gtSignTd))] = temp
                        # Correcting misclassified events due to sign status False in FN and FP
                        elif self.report[(sign, timestamp)]['verdict'] == "False Positive Type 2" and sign == gtSignTd:
                            if math.trunc(timestamp) in range(math.trunc(detectionTime) - 3,
                                                              math.trunc(detectionTime) + 2):
                                if searchedGTqty < gtQuantity:#To avaoid duplicate detection deletion
                                    if (self.report.has_key((gtSignTd, detectionTime))):  # Check FN event

                                        if self.report[(gtSignTd, detectionTime)]['verdict'] == "False Negative":
                                            self.report[(gtSignTd, detectionTime)]['verdict'] = 'True Positive'
                                            self.report[(gtSignTd, detectionTime)]['conti_uid'] = \
                                            self.report[(sign, timestamp)]['conti_uid']



                                    self.kpi['false_negative'] = self.kpi['false_negative'] - (
                                            gtQuantity - detectedQuantity)

                                    if self.newFNEvent.has_key(str(int(gtSignTd))):
                                        if (self.newFNEvent[str(int(gtSignTd))] > 0):
                                            self.newFNEvent[str(int(gtSignTd))] = self.newFNEvent[
                                                                                          str(int(gtSignTd))] - 1

                                    if self.newFPEvent.has_key(str(int(sign))):
                                        if (self.newFPEvent[str(int(sign))] > 0):
                                            self.newFPEvent[str(int(sign))] = self.newFPEvent[str(int(sign))] - 1

                                    if self.newTPEvent.has_key(str(int(gtSignTd))):
                                        self.newTPEvent[str(int(gtSignTd))] = self.newTPEvent[str(int(gtSignTd))] + 1
                                    else:
                                        self.newTPEvent[str(int(gtSignTd))] = 1

                                    self.kpi['true_positive'] = self.kpi['true_positive'] + 1
                                    self.kpi['tp_list'].append(self.report[(sign, timestamp)]['conti_uid'])

                                    self.kpi['false_positive'] = self.kpi['false_positive'] - 1

                                    self.report.pop((sign, timestamp))  # removing FP
                                    searchedGTqty = searchedGTqty + 1

                if __debug__:
                    print('@[idx]', idx, 'GT Sign ID=', gtSignTd, 'and GT    Qty:', gtQuantity, ',but Conti  Qty:',
                          detectedQuantity)
        # self.kpi['false_negative'] = self.kpi['false_negative'] - 1
        if self.kpi['false_negative'] < 0:
            self.kpi['false_negative'] = 0
            self.newFNEvent[str(int(gtSignTd))] = 0

    def evaluateKpi(self):
        filteredUid = []
        intersectionOfGTContiIdx = []
        disjointOfGTContiIdx = []
        fpQty = 0
        elsefpQty = 0

        for uniqueUidIdx in range(len(self.contiInfo['unique_uid'])):
            uniqueUid = self.contiInfo['unique_uid'][uniqueUidIdx]
            uidMatrix = self.findIdxOfAGivenUid(uniqueUid)
            uidRowValues = list(uidMatrix[0])
            uidColValues = list(uidMatrix[1])
            areValContinuous = self.checkForContinuity(
                uidRowValues)  # extracting detection index range for considered UID
            rowValues = []
            prevLen = 0
            for loopCount in range(len(areValContinuous)):
                # Checking only for continuous uids
                if (loopCount + 1) < len(areValContinuous):
                    if areValContinuous[
                        loopCount + 1] > 1:  # condition to differntiate more than one continuous index range for a give uid
                        contiTSRInfoForAUniqueUID = []
                        contiStatusInfoForAUniqueUID = []
                        startIdx = prevLen
                        rowValues.append(uidRowValues[loopCount])
                        prevLen = prevLen + len(rowValues)
                        endIdx = prevLen
                        colValues = uidColValues[startIdx:endIdx]
                        # if __debug__:
                        # print('For UID', uniqueUid, '\nthe last element is: ', rowValues[len(rowValues) - 1], 'of the stripped buffer:', rowValues)
                        # print('\n--------------------------------------------\n')
                        # print(colValues)
                        falseExistenceRangeOfUid_Row = []
                        falseExistenceRangeofUid_Col_BufferId = []
                        for subLoopCount in range(len(rowValues)):
                            # test = self.contiInfo['consolidated_uid'][rowValues[subLoopCount], colValues[subLoopCount]]
                            if ((int)(self.contiInfo['consolidated_uid'][
                                          rowValues[subLoopCount], colValues[subLoopCount]]) == uniqueUid):
                                if ((int)(self.contiInfo['consolidated_status'][
                                              rowValues[subLoopCount], colValues[subLoopCount]]) == 1) and (
                                subLoopCount) == len(colValues) - 1:
                                    falseExistenceRangeOfUid_Row.append(rowValues[subLoopCount])
                                    falseExistenceRangeofUid_Col_BufferId.append(colValues[subLoopCount])
                                elif ((int)(self.contiInfo['consolidated_status'][
                                                rowValues[subLoopCount], colValues[subLoopCount]]) == 1):
                                    contiTSRInfoForAUniqueUID.append((self.contiInfo['consolidated_traffic_sign_id'][
                                        rowValues[subLoopCount], colValues[subLoopCount]]))
                                else:
                                    falseExistenceRangeOfUid_Row.append(rowValues[subLoopCount])
                                    falseExistenceRangeofUid_Col_BufferId.append(colValues[subLoopCount])

                        contiIdxVal_subset = []
                        contiTSRVal_subset = []
                        gtIdxinRange = []
                        # --------------------Check for same traffic sign in consecutive indices within the considered continuous index range of the uid (e.g index range is 1-10 , uid 10 is carring trafic sign 50 for some indices n then for some other sign )
                        for subLoopCount, curElement in enumerate(contiTSRInfoForAUniqueUID):
                            prevElement = contiTSRInfoForAUniqueUID[subLoopCount - 1] if subLoopCount > 0 else None
                            nextElement = contiTSRInfoForAUniqueUID[subLoopCount + 1] if subLoopCount < len(
                                contiTSRInfoForAUniqueUID) - 1 else None
                            contiIdxVal_subset.append(rowValues[subLoopCount])
                            contiTSRVal_subset.append(contiTSRInfoForAUniqueUID[subLoopCount])
                            if curElement == nextElement:
                                if __debug__:
                                    pass
                                    # print('Element is the same, continue to read the values', end="\r")
                            else:
                                # if __debug__:
                                # print('idx values are', contiIdxVal_subset)
                                # print('Conti_TSR_Sign', contiTSRVal_subset)
                                if (any(item in self.KBTSRList for item in contiTSRVal_subset)) is True:
                                    filteredUid.append(uniqueUid)
                                    # counts = 0
                                    # for counts in range(len(self.gtIdx)):
                                    # startGTrangeIdx = self.gtIdx[counts]
                                    # endGTrangeIdx = startGTrangeIdx + 100
                                    # GTrangeOfIdx = range(startGTrangeIdx, endGTrangeIdx, 1)
                                    # contiIdxVal_subset = range(contiIdxVal_subset[0]-50, contiIdxVal_subset[-1]+1, 1)
                                    # self.gtIdx = sorted(self.gtIdx)
                                    # for i in range(0,len(self.gtIdx),2):
                                    #    Range = range(self.gtIdx[i], self.gtIdx[i+1],1)
                                    #    gtIdxinRange.append(Range)

                                    if (any(item in self.gtIdxRange for item in contiIdxVal_subset)) is True:
                                        val = [x for x in contiIdxVal_subset if x in self.gtIdxRange]
                                        oldval=val
                                        delta = val[-1] - val[0]
                                        if len(val) > 1 and delta > GtIdxWindowRange:
                                            val = [x for x in contiIdxVal_subset[-200:] if x in self.gtIdxRange]
                                            if len(val)==0:
                                                idx = contiIdxVal_subset.index(oldval[0])
                                                val=oldval
                                            else:
                                                idx = contiIdxVal_subset.index(val[0])
                                        else:
                                            # val = val[0]
                                            idx = contiIdxVal_subset.index(val[0])

                                        if len(falseExistenceRangeofUid_Col_BufferId) > 0:
                                            contiBufferId = falseExistenceRangeofUid_Col_BufferId[-1]

                                        if __debug__:
                                            print(
                                            'Common Index b/w GT and Conti det is:', str(val), 'for UID : ', uniqueUid,
                                            'in conti buffer:', contiBufferId)
                                        intersectionOfGTContiIdx.append(uniqueUid)
                                        ##TODO:calculate TP
                                        tpQty = self.kpi['true_positive']
                                        fpQty = self.kpi['false_positive']
                                        elsefpQty = fpQty
                                        self.updateKpiAsTpOrFp(val, uniqueUid, contiTSRVal_subset[-1], contiBufferId,
                                                               tpQty, fpQty)
                                        self.evaluateSupplSign(val, contiBufferId, uniqueUid)
                                        contiIdxVal_subset = []
                                        contiTSRVal_subset = []
                                    else:  ##TODO: False Positive Type-2 Calculation
                                        self.fp2Info[subLoopCount] = {}
                                        if len(falseExistenceRangeofUid_Col_BufferId) > 0:
                                            contiBufferId = falseExistenceRangeofUid_Col_BufferId[-1]

                                        list_of_FP_type2_uID_timeInst = []
                                        disjointOfGTContiIdx.append(uniqueUid)
                                        self.kpi['false_positive'] = self.kpi['false_positive'] + 1
                                        self.kpi['fp_error2_uid'].append(uniqueUid)
                                        self.fp2Info[subLoopCount]['uId'] = uniqueUid
                                        self.fp2Info[subLoopCount]['signClass'] = contiTSRVal_subset[0]

                                        if self.newFPEvent.has_key(str(int(contiTSRVal_subset[0]))):
                                            self.newFPEvent[str(int(contiTSRVal_subset[0]))] += 1
                                        else:
                                            self.newFPEvent[str(int(contiTSRVal_subset[0]))] = 1

                                        tTime = numpy.unique(
                                            self.contiInfo['consolidated_time'][contiIdxVal_subset][:, 0])
                                        list_of_FP_type2_uID_timeInst.append(tTime)
                                        self.fp2Info[subLoopCount]['time'] = list_of_FP_type2_uID_timeInst
                                        fp2InfoAtIdx = self.fp2Info.get(subLoopCount)
                                        # if len(fp2InfoAtIdx['time'][0]) == 2:
                                        #   self.report[(self.fp2Info[subLoopCount]['signClass'], fp2InfoAtIdx['time'][0][0])] = {"verdict": "False Positive Type 2", "conti_uid" : self.fp2Info[subLoopCount]['uId'], "contiBufferId": contiBufferId}
                                        if len(fp2InfoAtIdx['time'][0]) >= 2:
                                            self.report[(
                                            self.fp2Info[subLoopCount]['signClass'], fp2InfoAtIdx['time'][0][1])] = {
                                                "verdict": "False Positive Type 2",
                                                "conti_uid": self.fp2Info[subLoopCount]['uId'],
                                                "contiBufferId": contiBufferId, "weather_condition": str(
                                                    self.cmpGTContiInfo[self.cmpGTContiInfo.keys()[0]][
                                                        'weather_condition'][0]),
                                                "time_condition": str(
                                                    self.cmpGTContiInfo[self.cmpGTContiInfo.keys()[0]][
                                                        'time_condition'][0])}
                                        else:
                                            self.report[(
                                            self.fp2Info[subLoopCount]['signClass'], fp2InfoAtIdx['time'][0][0])] = {
                                                "verdict": "False Positive Type 2",
                                                "conti_uid": self.fp2Info[subLoopCount]['uId'],
                                                "contiBufferId": contiBufferId, "weather_condition": str(
                                                    self.cmpGTContiInfo[self.cmpGTContiInfo.keys()[0]][
                                                        'weather_condition'][0]),
                                                "time_condition": str(
                                                    self.cmpGTContiInfo[self.cmpGTContiInfo.keys()[0]][
                                                        'time_condition'][0])}
                                        print('@[idx]:', subLoopCount, 'is a', 'False Positive!', '\nConti Dict=',
                                              fp2InfoAtIdx,
                                              '\n--------------------------------------------------------------------------------------')
                                        # print(subLoopCount)
                                    contiIdxVal_subset = []
                                    contiTSRVal_subset = []
                                else:
                                    contiTSRVal_subset = []
                                    contiIdxVal_subset = []
                        # --------------------
                        rowValues = []
                    else:
                        rowValues.append(uidRowValues[loopCount])
        self.contiInfo['filtered_uid'] = filteredUid
        self.intersectionOfGTContiIdx = intersectionOfGTContiIdx
        self.disjointOfGTContiIdx = disjointOfGTContiIdx
        self.updateKpiForFN()

        # Add duplicate TP note to FP2
        for report_identifier, verdict in self.report.items():
            _, fp_event_time = report_identifier
            # Removing duplicate event data of FP1 from FN
            if (self.report.has_key((_, fp_event_time))):  # Too ignore deleted events
                if self.report[(_, fp_event_time)]['verdict'] == "False Positive Type 1":
                    # To Correct classification of ghost obj detection at the same time of TP
                    # Bcz of which it went to FP1 instead of FP2...
                    # If TP is there for same timestamp then another detction should be considered as FP2
                    for tp_sign, tp_time in self.report.keys():
                        if (self.report.has_key((tp_sign, tp_time))):  # Too ignore deleted events
                            if self.report[(tp_sign, tp_time)]['verdict'] == "True Positive" and fp_event_time == tp_time:
                                self.report[(_, fp_event_time)]['verdict'] = "False Positive Type 2"

            if verdict['verdict'] == 'False Positive Type 2':
                for idf, verd in self.report.items():
                    id, tp_time = idf
                    if id == _ and verd['verdict'] == 'True Positive':
                        if math.trunc(fp_event_time) in range(math.trunc(tp_time)-1, math.trunc(tp_time) + 2):  # duplicate detection event found
                            verdict['Note'] = "Duplicate True Positive"

    def __printData(self):

        print('GT     :', sorted(self.gtInfo.items()))
        print('Conti  :', sorted(self.cmpGTContiInfo.items()))

        print('\n--------------Final Evaluated Main Sign Category--------------------------------------\n')
        print('list_of_TP                                   :', self.kpi['tp_list'])
        print('extra_True_Positive_duplicate_id             :', self.kpi['tp_duplicate_id'])

        print('list_of_FP_type1 (Wrong Classfication)       :', self.kpi['fp_error1_uid'])
        print('list_of_FP_type2 (Detection without GT info) :', self.kpi['fp_error2_uid'])
        # print('list_of_FP_type2_uID:', self.kpi['fp_error2_uid'])

        print('\n--------------Supplementary Sign Category---------------------------------------------\n')

        if len(self.kpi['supplementary_sign']['fp_error1']['uid']) != 0:
            print('suppl_uid_fp_list_type1 :', self.kpi['supplementary_sign']['fp_error1']['uid'],
                  'suppl_uid_fp_timeInst_type1:',
                  self.kpi['supplementary_sign']['fp_error1']['time'])
        if len(self.kpi['supplementary_sign']['fp_error2']['uid']) != 0:
            print('\nsuppl_uid_fp_list_type2 :', self.kpi['supplementary_sign']['fp_error2']['uid'],
                  'suppl_uid_fp_timeInst_type2:',
                  self.kpi['supplementary_sign']['fp_error2']['time'])

        print('suppl_uid_fn_list :', self.kpi['supplementary_sign']['fn']['uid'], 'suppl_uid_fn_timeInst:',
              self.kpi['supplementary_sign']['fn']['time'])

        print('TP Suppl        :', self.kpi['supplementary_sign']['true_positive'])
        print('FP Suppl Type-1 :', len(self.kpi['supplementary_sign']['fp_error1']['uid']))
        print('FP Suppl Type-2 :', len(self.kpi['supplementary_sign']['fp_error2']['uid']))
        print('FN Suppl        :', self.kpi['supplementary_sign']['false_negative'])

        print('\n--------------Final KPI of Main Sign Category-----------------------------------------\n')
        ##TODO: Cumulative TP, FP, FN count
        self.cumulative_results = {
            "Conti_KPI": {
                "TP": len(self.kpi['tp_list']),
                "FP": len(self.kpi['fp_error1_uid']) + len(self.kpi['fp_error2_uid']) + len(
                    self.kpi['tp_duplicate_id']),
                "FN": self.kpi['false_negative']
            }
        }
        # print ("Report: ",self.report)
        print('TP   :', self.cumulative_results["Conti_KPI"]["TP"])
        print('FP   :', self.cumulative_results["Conti_KPI"]["FP"])
        print('FN   :', self.cumulative_results["Conti_KPI"]["FN"])

        print('--------------------------------------------------------------------------------------\n')

        print('Filtered_uID_list:', self.contiInfo['filtered_uid'])

        print('COMMON_GT_CONTI_DET_IDX_IDS      :', self.intersectionOfGTContiIdx)
        print('NO_COMMON_GT_CONTI_DET_IDX_IDS   :', self.disjointOfGTContiIdx)

        print('GT           :', sorted(self.gtInfo.items()))
        print('Conti Final  :', sorted(self.cmpGTContiInfo.items()))

        print('GT           :', self.kpi['gt signal id'])
        print('Predictions  :', self.kpi['predicted_sig_class_id'])

    def __getFlag(self, name):
        path = self.imgFilePath.format(name.title())
        # im = cv2.imread(path, cv2.COLOR_RGB2GRAY)
        # im = cv2.resize(im, (64, 64))
        im = plt.imread(path)
        return im

    def __offset_image(self, coord, name, ax, size_h):
        img = self.__getFlag(name)
        im = OffsetImage(img, zoom=0.5)
        im.image.axes = ax

        ab = AnnotationBbox(im, (coord, 3.5), xybox=(0., -25.), frameon=False,
                            ####To adjust the position of the Traffic Sign Logos in the Confusion Matrix.(image. coord, 0) Adjust the '0' to anything. positive makes the x-axis label to come down.
                            xycoords='data', boxcoords="offset points", pad=0)

        ax.add_artist(ab)
        ab = AnnotationBbox(im, (-0.5, coord), xybox=(-25., 0.), frameon=False,
                            xycoords='data', boxcoords="offset points", pad=0)
        ax.add_artist(ab)

    def showConfusionMatrixAndSaveData(self):
        labels = unique_labels(self.kpi['gt signal id'], self.kpi['predicted_sig_class_id'])
        cm = confusion_matrix(self.kpi['gt signal id'], self.kpi['predicted_sig_class_id'])
        if __debug__:
            print('CF:\n', cm, 'type:', type(cm))
        x_label = [str(x) for x in labels]
        if __debug__:
            print('x_label', x_label)

        fig, ax = plt.subplots()
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        width, height = fig.get_size_inches()
        im = ax.imshow(cm, cmap="Blues_r")
        ax.tick_params(axis='x', which='major', pad=42)
        ax.tick_params(axis='y', which='major', pad=35)
        for rowCount, c in enumerate(x_label):
            for colCount, d in enumerate(x_label):
                self.__offset_image(rowCount, c, ax, height)
                text = ax.text(colCount, rowCount, cm[rowCount, colCount],
                               ha="center", va="center", color="black")
        ax.set_xlabel('Continental Traffic Sign Detection')
        ax.set_ylabel('KB Ground Truth')
        ax.set_title("KB TSR KPI")
        plt.savefig(self.filename)
        # self.jsonObjected = dict((k, self.cumulative_results[k]) for k in ["TP", "FP", "FN"] if k in self.cumulative_results)
        # json_object = self.folder_path+'\\'+self.nameOfFile+"_overallpredictions"+'.json'
        # with open(json_object, "w") as outfile:
        # json.dump(self.jsonObjected, outfile, indent=4)
        return

    def updateJsonForTrafficSignwiseCount(self):
        data = {}
        tpEvent = {}
        fpEvent = {}
        fnEvent = {}
        json_object = self.folder_path + '.json'

        if os.path.exists(json_object):
            fp = open(json_object, 'r')
            data = json.load(fp)
            fp.close()
            tpEvent = data["TruePositive"]
            fpEvent = data["FalsePositive"]
            fnEvent = data["FalseNegative"]

        print ("data:", data)
        print ("Eventwise data:", tpEvent, fpEvent, fnEvent)
        flag = 0

        summary_path = os.path.dirname(self.folder_path) + "\\TrafficSignSummary.json"

        if os.path.exists(summary_path):
            f = open(summary_path, 'r')
            summaryData = json.load(f)
            flag = 1
            f.close()

        tp_sign_ids = self.newTPEvent.keys()
        print ("newTPEvent Sign ids:", tp_sign_ids)
        for sign_class_id in tp_sign_ids:

            if self.newTPEvent:
                if tpEvent.has_key(sign_class_id):
                    tpEvent[sign_class_id] = self.newTPEvent[sign_class_id] + tpEvent[sign_class_id]
                else:
                    tpEvent[sign_class_id] = self.newTPEvent[sign_class_id]

            if flag == 1:
                if summaryData["TruePositive"].has_key(sign_class_id):
                    summaryData["TruePositive"][sign_class_id] = summaryData["TruePositive"][sign_class_id] + \
                                                                 self.newTPEvent[sign_class_id]
                else:
                    summaryData["TruePositive"][sign_class_id] = self.newTPEvent[sign_class_id]

        fn_sign_ids = self.newFNEvent.keys()
        print ("newFNEvent Sign ids:", fn_sign_ids)
        for sign_class_id in fn_sign_ids:

            if self.newFNEvent:
                if fnEvent.has_key(sign_class_id):
                    fnEvent[sign_class_id] = self.newFNEvent[sign_class_id] + fnEvent[sign_class_id]
                else:
                    fnEvent[sign_class_id] = self.newFNEvent[sign_class_id]
            if flag == 1:
                if summaryData["FalseNegative"].has_key(sign_class_id):
                    summaryData["FalseNegative"][sign_class_id] = summaryData["FalseNegative"][sign_class_id] + \
                                                                  self.newFNEvent[sign_class_id]
                else:
                    summaryData["FalseNegative"][sign_class_id] = self.newFNEvent[sign_class_id]

        fp_sign_ids = self.newFPEvent.keys()
        print ("newFPEvent Sign ids:", fp_sign_ids)
        for sign_class_id in fp_sign_ids:

            if self.newFPEvent:
                if fpEvent.has_key(sign_class_id):
                    fpEvent[sign_class_id] = self.newFPEvent[sign_class_id] + fpEvent[sign_class_id]
                else:
                    fpEvent[sign_class_id] = self.newFPEvent[sign_class_id]
            if flag == 1:
                if summaryData["FalsePositive"].has_key(sign_class_id):
                    summaryData["FalsePositive"][sign_class_id] = summaryData["FalsePositive"][sign_class_id] + \
                                                                  self.newFPEvent[sign_class_id]
                else:
                    summaryData["FalsePositive"][sign_class_id] = self.newFPEvent[sign_class_id]

        data["TruePositive"] = tpEvent
        data["FalsePositive"] = fpEvent
        data["FalseNegative"] = fnEvent

        with open(json_object, "w") as outfile:
            json.dump(data, outfile, indent=4)

        if os.path.exists(summary_path):
            with open(summary_path, "w") as outfile:
                json.dump(summaryData, outfile, indent=4)
        else:
            with open(summary_path, "w") as outfile:
                json.dump(data, outfile, indent=4)

    def displayData(self):
        self.__printData()
        self.showConfusionMatrixAndSaveData()
        self.updateJsonForTrafficSignwiseCount()


if __name__ == "__main__":
    pass
    # TODO not supported anymore
    # matFilePath = r'C:\KBData\__PythonToolchain\Meas\TSR\report\mi5id1648__2021-10-15_16-04-48\mi5id1648__2021-10-15_16-04-48_export.mat'
    # kpi = TSRKpiEvaluation(matFilePath)
    # kpi.createKBTSRList()
    # kpi.createGTInfo()
    # kpi.createInfoToCompare()
    # kpi.createContiInfo()
    # kpi.fetchUniqueUids()
    # kpi.evaluateKpi()
    # kpi.displayData()
