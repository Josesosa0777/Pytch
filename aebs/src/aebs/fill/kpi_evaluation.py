import copy
import math
import os
import sys
from itertools import chain

import matplotlib.pyplot as plt
import numpy
import scipy.io
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels
import numpy as np

class TSRKpiEvaluation():
    def __init__(self, matFilePath, txtFilePath, imgFilePath):
        kpi_input_data = matFilePath

        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.detCmpObjects = kpi_input_data['detection_compare_objects']['detection_compare_objectbuffer']
        self.gtDet = np.array(self.detCmpObjects['postmarker_detection'], dtype = int).tolist()
        self.contiDet = np.array(self.detCmpObjects['conti_detection'], dtype=int)
        self.gtObj = kpi_input_data['postmarker_objects']
        self.contiTSRObj = kpi_input_data['conti_tsr_objects']
        self.txtFilePath = txtFilePath
        self.imgFilePath = imgFilePath
        self.KBSupplementarySignList = [104812, 104811, 104030, 105236, 100100, 100400]
        self.intersectionOfGTContiIdx = []
        self.disjointOfGTContiIdx = []
        self.gtInfo = {}
        self.contiInfo = {}
        self.cmpGTContiInfo = {}
        self.fp2Info = {}
        self.gtIdx = self.gtInfo.keys()
        self.KBTSRList = []
        self.kpi = {}
        self.kpi['true_positive'] = 0
        self.kpi['false_positive'] = 0
        self.kpi['false_negative'] = 0
        self.kpi['tp_duplicate_id'] = []
        self.kpi['fp_error1_uid'] = []
        self.kpi['fp_error2_uid'] = []
        self.kpi['tp_list'] = []
        self.kpi['predicted_sig_class_id'] = []
        self.kpi['gt signal id'] = []
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
            print("Please check the file for : Format error / Float values within file / Spaces / Empty lines in the end / check against ref file.")
            raise

        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise



    def createGTInfo(self):
        for loopCount in range(len(self.gtDet)):
            if self.gtDet[loopCount] == 1:
                tmp_supplementary_sign = []
                tmp_supplementary_sign_quantity = []
                tmp_sign_class_id = []
                tmp_sign_quantity = []
                tmp_time = []
                self.gtInfo[loopCount] = {}
                bufferNumber = 0
                #x = self.gtObj.dtype.names
                #print(x, 'type:', type(x))
                for gtObjectBufferId in self.gtObj.keys():
                    bufferNumber = bufferNumber + 1
                    gtBuffer =self.gtObj[gtObjectBufferId]
                    gt_sign_class_id = gtBuffer['sign_class_id'][loopCount]
                    gt_quantity = gtBuffer['quantity'][loopCount]
                    gt_time = gtBuffer['time'][loopCount]

                    if (gt_sign_class_id > 0):
                        if bufferNumber >= 2:
                            if gt_sign_class_id in self.KBSupplementarySignList:
                                if __debug__:
                                    print('For Index:', loopCount,'Postmarker contains a supplementary sign:', gt_sign_class_id)
                                tmp_supplementary_sign.append(gt_sign_class_id)
                                tmp_supplementary_sign_quantity.append(gt_quantity)
                                self.gtInfo[loopCount]['supplementary_sign'] = tmp_supplementary_sign
                                self.gtInfo[loopCount]['supplementary_sign_quantity'] = tmp_supplementary_sign_quantity
                            else:
                                tmp_sign_class_id.append(gt_sign_class_id)
                                tmp_sign_quantity.append(gt_quantity)
                                tmp_time.append(gt_time)
                        else:
                            tmp_sign_class_id.append(gt_sign_class_id)
                            tmp_sign_quantity.append(gt_quantity)
                            tmp_time.append(gt_time)

                    self.gtInfo[loopCount]['sign_class_id'] = tmp_sign_class_id
                    self.gtInfo[loopCount]['quantity'] = tmp_sign_quantity
                    self.gtInfo[loopCount]['time'] = tmp_time

                    #print('---',len(self.gtInfo))
        if __debug__:
            print(self.gtInfo.keys())

    def createContiInfo(self):
        tmpTime = numpy.empty((self.contiDet.size, 1))
        tmpUid = numpy.empty((self.contiDet.size, 1))
        tmpTrafficSignId = numpy.empty((self.contiDet.size, 1))
        tmpStatus = numpy.empty((self.contiDet.size, 1))
        tmpSupplSignId = numpy.empty((self.contiDet.size, 1))

        for contiTSRBufferId in self.contiTSRObj.keys():
            contiBuffer = self.contiTSRObj[contiTSRBufferId]
            tmpTimeAsFloat = []
            for loopCount in range(self.contiDet.size):
                tmp = contiBuffer['time'][loopCount].astype(float)
                tmpTimeAsFloat.append(self.truncateValues(tmp))
            contiTime = numpy.asarray(tmpTimeAsFloat)
            contiTime = numpy.reshape(contiTime, (self.contiDet.size, 1))
            tmpTime = numpy.append(tmpTime, contiTime, axis = 1)

            tmpUid = numpy.column_stack((tmpUid, self.__convertToList(contiBuffer['uid'])))
            tmpTrafficSignId = numpy.column_stack((tmpTrafficSignId, self.__convertToList(contiBuffer['traffic_sign_id'])))
            tmpStatus = numpy.column_stack((tmpStatus, self.__convertToList(contiBuffer['status'])))
            tmpSupplSignId = numpy.column_stack((tmpSupplSignId, self.__convertToList(contiBuffer['suppl_sign_ids'])))

        self.contiInfo['consolidated_time'] = numpy.delete(tmpTime, 0, 1)
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
            gtIdx = list(self.gtIdx)[loopCount]
            contiTSRSign = self.contiInfo['consolidated_traffic_sign_id'][gtIdx][:]
            contiUid = self.contiInfo['consolidated_uid'][gtIdx][:]
            contiTime = self.contiInfo['consolidated_time'][gtIdx][:]

            tmpUid = numpy.row_stack((tmpUid,contiUid))
            tmpTrafficSignId = numpy.row_stack((tmpTrafficSignId,contiTSRSign))
            tmpTime = numpy.row_stack((tmpTime,contiTime))

        tmpTime = numpy.delete(tmpTime, 0, 0)
        tmpTrafficSignId = numpy.delete(tmpTrafficSignId, 0, 0)
        tmpUid = numpy.delete(tmpUid, 0, 0)
        self.contiInfo['filtered_traffic_sign_id'] = tmpTrafficSignId
        self.contiInfo['filtered_uid'] = tmpUid
        self.contiInfo['filtered_time'] = tmpTime


    def createInfoToCompare(self):
        self.gtIdx = self.gtInfo.keys()
        self.cmpGTContiInfo = copy.deepcopy(self.gtInfo)
        for loopCount in range(len(self.gtIdx)):
            idx = list(self.gtIdx)[loopCount]
            self.cmpGTContiInfo[idx]['quantity'] = 0
            if self.__keysExist(self.gtInfo, idx, "supplementary_sign_quantity") is True:
                self.cmpGTContiInfo[idx]['supplementary_sign_quantity'] = 0
        if __debug__:
            print('GT Dict with QTY INFO            :', self.gtInfo)
            print('Conti Dict Updated with QTY INFO :', self.cmpGTContiInfo)

    def fetchUniqueUids(self):
        uniqueValues = (numpy.unique(self.contiInfo['consolidated_uid']).astype(int))
        uniqueValues = [x for x in uniqueValues if x <= 100000]
        uniqueValues = [x for x in uniqueValues if x >= 0] #isinstance(uniqueValues[loopCount],int)
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
        ret.insert(0,0)
        ret.append(999999999999999999)
        return ret

    def updateKpiAsTpOrFp(self, idxToGT, contiUid, detection):
        idxToGT = idxToGT[0]
        self.gtInfo.get(idxToGT)
        gt = self.gtInfo[idxToGT]['sign_class_id'][0]
        gt_qua = self.gtInfo[idxToGT]['quantity'][0]
        detection = int(detection)
        detectedQuantity = self.cmpGTContiInfo[idxToGT]['quantity']
        detectionTime = self.cmpGTContiInfo[idxToGT]['time'][0]
        if __debug__:
            print('@[idx]:', idxToGT, '\nConti Dict=', self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=', self.gtInfo.get(idxToGT))
            print('\ngtx:', gt, 'c_sign_class_id', detection)
        if gt == detection:
            detectedQuantity = detectedQuantity + 1
            self.cmpGTContiInfo[idxToGT]['quantity'] = detectedQuantity
            self.report[(detection, idxToGT)] = {"verdict" : "True Positive"}
            if __debug__:
                print('The TSR @[idx]:', idxToGT, 'is a', 'True Positive!', '\nConti Dict=',
                      self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=', self.gtInfo.get(idxToGT),
                      '\n\n---------------------------------------------------------------------------------')
            if self.cmpGTContiInfo[idxToGT]['quantity'] > self.gtInfo[idxToGT]['quantity']:
                self.kpi['true_positive'] = self.kpi['true_positive']
                self.kpi['tp_duplicate_id'].append(contiUid)
                if __debug__:
                    print('Since the TSR @[idx]:', idxToGT,
                          'conti_qty > gt_qty , it is a False Positive. \n -------------------------------------')
            else:
                self.kpi['true_positive'] = self.kpi['true_positive'] + 1
                self.kpi['tp_list'].append(contiUid)
                self.kpi['predicted_sig_class_id'].append(detection)
                self.kpi['gt signal id'].append(gt)
        else:
            self.kpi['false_positive'] = self.kpi['false_positive'] + 1
            self.kpi['fp_error1_uid'].append(contiUid)
            self.kpi['predicted_sig_class_id'].append(detection)
            self.kpi['gt signal id'].append(gt)
            self.report[(detection, idxToGT)] = {"verdict" : "False Positive"}
            if __debug__:
                print('The TSR @[idx]:', idxToGT, 'is a', 'False Positive!', '\nConti Dict=',
                      self.cmpGTContiInfo.get(idxToGT), '\nGT    Dict=', self.gtInfo.get(idxToGT), '\n -------------------------------------')

    def evaluateSupplSign(self, commonIdx, bufferId, uId):
        startIdx = bufferId * 3
        endIdx = bufferId + 3
        value = self.contiInfo['consolidated_suppl_sign_id'][commonIdx][0, startIdx:endIdx]
        if numpy.any(value) == True:
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
        #supplementary signs
        for loopCount in range(len(self.gtIdx)):
            gtIdx = list(self.gtIdx)[loopCount]
            if (self.__keysExist(self.gtInfo,gtIdx, "supplementary_sign")) is True:
                if __debug__:
                    print('Supplementary exists in GT:', self.__keysExist(self.gtInfo,gtIdx, "supplementary_sign"))
                gtSupplementarySign = self.gtInfo[gtIdx]['supplementary_sign']
                gtTime = self.gtInfo[gtIdx]['time']
                gtTimeTruncated = [round(num, 1) for num in gtTime]
                isSupplementarySignPresent = gtSupplementarySign in self.contiInfo['filtered_traffic_sign_id'][loopCount][:]
                self.kpi['supplementary_sign']['fp']['time'] = self.kpi['supplementary_sign']['fp_error1']['time'] + self.kpi['supplementary_sign']['fp_error2']['time']
                supplementaryTimeTruncated = [round(num, 1) for num in self.kpi['supplementary_sign']['fp']['time']]
                if __debug__:
                    print('CHECKing:', self.kpi['supplementary_sign']['fp']['time'])
                    print('GT Time:', gtTime, type(gtTime))
                isTimePresent = any(item in gtTimeTruncated for item in supplementaryTimeTruncated)
                if  isSupplementarySignPresent is False and isTimePresent is False:
                    self.kpi['supplementary_sign']['false_negative'] = self.kpi['supplementary_sign']['false_negative'] + 1
                    if __debug__:
                        print('False Negative for Supplementary sign @GroundTruth time', gtTime, 'Index:',gtIdx)
                    self.kpi['supplementary_sign']['fn']['uid'].append(gtIdx)
                    self.kpi['supplementary_sign']['fn']['time'].append(gtTime)

        #regular
        for loopCount in range(len(self.gtIdx)):
            idx = list(self.gtIdx)[loopCount]
            gtQuantity = self.gtInfo[idx]['quantity'][0]
            gtSignTd = self.gtInfo[idx]['sign_class_id'][0]
            detectedQuantity = self.cmpGTContiInfo[idx]['quantity']
            detectionTime = self.cmpGTContiInfo[idx]['time'][0]

            if detectedQuantity < gtQuantity: ##TODO: False Negative Calculation
                self.report[(gtSignTd, idx)] = {"verdict": "False Negative"}
                self.kpi['false_negative'] = self.kpi['false_negative'] + (gtQuantity - detectedQuantity)
                if __debug__:
                    print('@[idx]', idx,'GT Sign ID=',gtSignTd, 'and GT    Qty:', gtQuantity, ',but Conti  Qty:',
                          detectedQuantity)
        self.kpi['false_negative'] = self.kpi['false_negative'] - 1
        if self.kpi['false_negative'] < 0:
            self.kpi['false_negative'] = 0

    def evaluateKpi(self):
        filteredUid = []
        intersectionOfGTContiIdx = []
        disjointOfGTContiIdx = []
        for uniqueUidIdx in range(len(self.contiInfo['unique_uid'])):
            uniqueUid = self.contiInfo['unique_uid'][uniqueUidIdx]
            uidMatrix = self.findIdxOfAGivenUid(uniqueUid)
            uidRowValues = list(uidMatrix[0])
            uidColValues = list(uidMatrix[1])
            areValContinuous = self.checkForContinuity(uidRowValues)
            rowValues = []
            prevLen = 0
            for loopCount in range(len(areValContinuous)):
                if (loopCount + 1) < len(areValContinuous):
                    if areValContinuous[loopCount + 1] > 1:
                        contiTSRInfoForAUniqueUID = []
                        contiStatusInfoForAUniqueUID = []
                        startIdx = prevLen
                        rowValues.append(uidRowValues[loopCount])
                        prevLen = prevLen + len(rowValues)
                        endIdx = prevLen
                        colValues = uidColValues[startIdx:endIdx]
                        #if __debug__:
                            #print('For UID', uniqueUid, '\nthe last element is: ', rowValues[len(rowValues) - 1], 'of the stripped buffer:', rowValues)
                            #print('\n--------------------------------------------\n')
                            #print(colValues)

                        for subLoopCount in range(len(rowValues)):
                            test = self.contiInfo['consolidated_uid'][rowValues[subLoopCount], colValues[subLoopCount]]
                            if ((int)(self.contiInfo['consolidated_uid'][rowValues[subLoopCount], colValues[subLoopCount]]) == uniqueUid):
                                if((int)(self.contiInfo['consolidated_status'][rowValues[subLoopCount], colValues[subLoopCount]]) == 1):
                                    contiTSRInfoForAUniqueUID.append((self.contiInfo['consolidated_traffic_sign_id'][rowValues[subLoopCount], colValues[subLoopCount]]))

                        contiIdxVal_subset = []
                        contiTSRVal_subset = []
                        for subLoopCount, curElement in enumerate(contiTSRInfoForAUniqueUID):
                            prevElement = contiTSRInfoForAUniqueUID[subLoopCount - 1] if subLoopCount > 0 else None
                            nextElement = contiTSRInfoForAUniqueUID[subLoopCount + 1] if subLoopCount < len(contiTSRInfoForAUniqueUID) - 1 else None
                            contiIdxVal_subset.append(rowValues[subLoopCount])
                            contiTSRVal_subset.append(contiTSRInfoForAUniqueUID[subLoopCount])
                            if curElement == nextElement:
                                if __debug__:
                                    pass
                                    #print('Element is the same, continue to read the values', end="\r")
                            else:
                                #if __debug__:
                                    #print('idx values are', contiIdxVal_subset)
                                    #print('Conti_TSR_Sign', contiTSRVal_subset)
                                if (any(item in self.KBTSRList for item in contiTSRVal_subset)) is True:
                                    filteredUid.append(uniqueUid)
                                    if (any(item in self.gtIdx for item in contiIdxVal_subset)) is True:
                                        val = [x for x in contiIdxVal_subset if x in self.gtIdx]
                                        idx = contiIdxVal_subset.index(val)
                                        contiBufferId = colValues[idx]
                                        if __debug__:
                                            print('Common Index b/w GT and Conti det is:', str(val), 'for UID : ', uniqueUid,
                                                  'in conti buffer:', contiBufferId)
                                        intersectionOfGTContiIdx.append(uniqueUid)
                                        #calculatetp
                                        self.updateKpiAsTpOrFp(val, uniqueUid, contiTSRVal_subset[-1])
                                        self.evaluateSupplSign(val, contiBufferId, uniqueUid)
                                        contiIdxVal_subset = []
                                        contiTSRVal_subset = []
                                    else: ##TODO: False Positive Type-2 Calculation
                                        self.fp2Info[subLoopCount] = {}
                                        list_of_FP_type2_uID_timeInst = []
                                        disjointOfGTContiIdx.append(uniqueUid)
                                        self.kpi['false_positive'] = self.kpi['false_positive'] + 1
                                        self.kpi['fp_error2_uid'].append(uniqueUid)
                                        self.fp2Info[subLoopCount]['uId'] = uniqueUid
                                        self.fp2Info[subLoopCount]['signClass'] = contiTSRVal_subset[0]
                                        tTime = numpy.unique(self.contiInfo['consolidated_time'][contiIdxVal_subset][:,1])
                                        list_of_FP_type2_uID_timeInst.append(tTime)
                                        self.fp2Info[subLoopCount]['time'] = list_of_FP_type2_uID_timeInst
                                        # self.report[(self.fp2Info[subLoopCount]['signClass'], subLoopCount)] = {"verdict": "False Positive"}
                                        print('@[idx]:', subLoopCount, 'is a', 'False Positive!', '\nConti Dict=', self.fp2Info.get(subLoopCount), '\n--------------------------------------------------------------------------------------')
                                    contiIdxVal_subset = []
                                    contiTSRVal_subset = []
                                else:
                                    contiTSRVal_subset = []
                                    contiIdxVal_subset = []
                        rowValues = []
                    else:
                        rowValues.append(uidRowValues[loopCount])
        self.contiInfo['filtered_uid'] = filteredUid
        self.intersectionOfGTContiIdx = intersectionOfGTContiIdx
        self.disjointOfGTContiIdx = disjointOfGTContiIdx
        self.updateKpiForFN()

    def __printData(self):
        print('GT     :', self.gtInfo.items())
        print('Conti  :', self.cmpGTContiInfo.items())

        print('\n--------------Final Evaluated Main Sign Category--------------------------------------\n')
        print('list_of_TP                                   :', self.kpi['tp_list'])
        print('extra_True_Positive_duplicate_id             :', self.kpi['tp_duplicate_id'])

        print('list_of_FP_type1 (Wrong Classfication)       :', self.kpi['fp_error1_uid'])
        print('list_of_FP_type2 (Detection without GT info) :', self.kpi['fp_error2_uid'])
        #print('list_of_FP_type2_uID:', self.kpi['fp_error2_uid'])

        print('\n--------------Supplementary Sign Category---------------------------------------------\n')

        if len(self.kpi['supplementary_sign']['fp_error1']['uid']) != 0:
            print('suppl_uid_fp_list_type1 :', self.kpi['supplementary_sign']['fp_error1']['uid'], 'suppl_uid_fp_timeInst_type1:',
                  self.kpi['supplementary_sign']['fp_error1']['time'])
        if len(self.kpi['supplementary_sign']['fp_error2']['uid']) != 0:
            print('\nsuppl_uid_fp_list_type2 :', self.kpi['supplementary_sign']['fp_error2']['uid'], 'suppl_uid_fp_timeInst_type2:',
                  self.kpi['supplementary_sign']['fp_error2']['time'])

        print('suppl_uid_fn_list :', self.kpi['supplementary_sign']['fn']['uid'], 'suppl_uid_fn_timeInst:', self.kpi['supplementary_sign']['fn']['time'])

        print('TP Suppl        :', self.kpi['supplementary_sign']['true_positive'])
        print('FP Suppl Type-1 :', len(self.kpi['supplementary_sign']['fp_error1']['uid']))
        print('FP Suppl Type-2 :', len(self.kpi['supplementary_sign']['fp_error2']['uid']))
        print('FN Suppl        :', self.kpi['supplementary_sign']['false_negative'])

        print('\n--------------Final KPI of Main Sign Category-----------------------------------------\n')
        ##TODO: Cumulative TP, FP, FN count
        self.cumulative_results = {
            "TP": len(self.kpi['tp_list']),
            "FP": len(self.kpi['fp_error1_uid']) + len(self.kpi['fp_error2_uid']),
            "FN": self.kpi['false_negative']
        }
        print('TP   :', self.cumulative_results["TP"])
        print('FP   :', self.cumulative_results["FP"])
        print('FN   :', self.cumulative_results["FN"])

        print('--------------------------------------------------------------------------------------\n')

        print('Filtered_uID_list:', self.contiInfo['filtered_uid'])

        print('COMMON_GT_CONTI_DET_IDX_IDS      :', self.intersectionOfGTContiIdx)
        print('NO_COMMON_GT_CONTI_DET_IDX_IDS   :', self.disjointOfGTContiIdx)

        print('GT           :', self.gtInfo)
        print('Conti Final  :', self.cmpGTContiInfo)

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

        ab = AnnotationBbox(im, (coord, 3.5), xybox=(0., -25.), frameon=False,    ####To adjust the position of the Traffic Sign Logos in the Confusion Matrix.(image. coord, 0) Adjust the '0' to anything. positive makes the x-axis label to come down.
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
        return


    def displayData(self):
        self.__printData()
        self.showConfusionMatrixAndSaveData()
        # filename2 = self.file2name+'/newdata.xlsx'
        # self.appendingData(filename2, result, sheet_name=self.filename)


if __name__ == "__main__":
    matFilePath = r'C:\KBData\__PythonToolchain\Meas\TSR\report\mi5id1648__2021-10-15_16-04-48\mi5id1648__2021-10-15_16-04-48_export.mat'
    txtFilePath = r"C:\KBData\__PythonToolchain\Development\tsr_kpi_evaluation\SR_signs.txt"
    imgFilePath = r"C:\KBData\__PythonToolchain\Development\pytch_bitbucket\dataio\src\measparser\images\{}.png"
    kpi = TSRKpiEvaluation(matFilePath, txtFilePath, imgFilePath)
    kpi.createKBTSRList()
    kpi.createGTInfo()
    kpi.createInfoToCompare()
    kpi.createContiInfo()
    kpi.fetchUniqueUids()
    kpi.evaluateKpi()
    kpi.displayData()
