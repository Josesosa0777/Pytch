import logging
import re
from collections import OrderedDict
import numpy as np
import glob
import os
import json
import datetime

# Purpose: To write the data by parsing json created by KPI_evaluation script which stores eventwise count for every traffic sign detected
# by conti...................



class TrafficSignWiseCount:
    marker_data = {}
    empty_sign_data = []
    traffic_sign_report = []
    tpEvent = {}
    fnEvent = {}
    fpEvent = {}
    summary = {}
    gt = {}
    TSR_SIGNS_FILE_PATH = os.path.join(os.path.dirname(__file__), "config", "SR_sign_classes.txt")

    def readJsonEventWiseCount(self, path):
        if(os.path.exists(path)):
            f = open(path, 'r')
            jsonData = json.load(f)
            f.close()
            self.tpEvent = jsonData["TruePositive"]
            self.fnEvent = jsonData["FalseNegative"]
            self.fpEvent = jsonData["FalsePositive"]
        else:
            print('Json is not created..')

    def isValidMeasDir(self,root, folder):
        # is directory?
        fullfolder = os.path.join(root, folder)
        if not os.path.isdir(fullfolder):
            return False
        # looks like date?
        if not re.match('\d{4}-\d{2}-\d{2}', folder):
            return False
        # is date valid?
        try:
            datetime.datetime.strptime(folder, '%Y-%m-%d')
        except ValueError:
            return False
        # contains files?
        if not any(os.path.isfile(os.path.join(fullfolder, f))
                   for f in os.listdir(fullfolder)):
            return False
        # should be valid...
        return True

    def onlySummaryReportGen(self,measRootFolderPath,dbFolderPath):
        for folder in os.listdir(measRootFolderPath):
            if not self.isValidMeasDir(measRootFolderPath, folder):
                continue

            path = os.path.join(measRootFolderPath, folder)
            self.parseJsonAndCreateCsv(path,dbFolderPath)
            print("csv generated for traffic sign data : ", folder)

    def parseJsonAndCreateCsv(self, path,dbfolderPath):
        text_files = glob.glob(path + "/*.json")
        self.readJsonEventWiseCount(path + ".json")
        self.traffic_sign_report = []
        print("Traffic sign report:", self.traffic_sign_report)
        for i in range(len(text_files)):
            json_file_path = os.path.join(text_files[i]).replace("\\", "/")
            if not os.path.isfile(json_file_path):
                raise Exception("Postmarker data not found, Place the json file along with the measurements")
            f = open(json_file_path)
            marker_data = json.load(f)
            f.close()

            if 'Traffic Signs' in marker_data:
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
                        self.empty_sign_data.append(tuple(value))
                        continue
                    pytch_report["conti_sign_class"] = str(value[1])
                    pytch_report["description"] = str(value[2])
                    pytch_report["status"] = str(value[3])
                    if len(value) == 5:  # 5th field is quantity of same signs detected
                        pytch_report["quantity"] = int(str(value[4]))
                    else:
                        pytch_report["quantity"] = 1

                    self.traffic_sign_report.append(pytch_report)

        print(self.traffic_sign_report)

        signs = np.loadtxt(self.TSR_SIGNS_FILE_PATH)
        uniqueVal = signs.tolist()

        a = np.zeros((len(uniqueVal), 4))

        arr = np.column_stack((uniqueVal, a))
        for i in range(len(self.traffic_sign_report)):
            sign = int(self.traffic_sign_report[i]['conti_sign_class'])
            qty = self.traffic_sign_report[i]['quantity']

            if sign in uniqueVal:
                idx = np.where(arr == sign)
                rwo = int(idx[0])
                arr[rwo][1] = arr[rwo][1] + qty  # update GT count
                if (self.gt.has_key(sign)):
                    self.gt[sign] = self.gt[sign] + qty
                else:
                    self.gt[sign] = qty

                if (self.tpEvent.has_key(str(sign))):
                    arr[rwo][2] = self.tpEvent[str(sign)]
                    self.tpEvent.pop(str(sign))
                if (self.fpEvent.has_key(str(sign))):
                    arr[rwo][3] = self.fpEvent[str(sign)]
                    self.fpEvent.pop(str(sign))
                if (self.fnEvent.has_key(str(sign))):
                    arr[rwo][4] = self.fnEvent[str(sign)]
                    self.fnEvent.pop(str(sign))

        # False positive may hold signs not marked in JSON
        # Below loop covers all those remaining signs
        for sign in self.fpEvent.keys():
            sign = int(sign)
            if sign in uniqueVal:
                idx = np.where(arr == sign)
                rwo = int(idx[0])
                arr[rwo][3] = arr[rwo][3] + self.fpEvent[str(sign)]

        # -----------------------------------------------------

        summary_path = os.path.dirname(path) + "\\TrafficSignSummary.json"

        if os.path.exists(summary_path):
            f = open(summary_path, 'r')
            data = json.load(f)
            f.close()
            data['gt'] = self.gt
            with open(summary_path, "w") as outfile:
                json.dump(data, outfile, indent=4)
        else:
            print("TrafficSignSummary.json not found")

        np.savetxt(dbfolderPath + "\\"+ path.split('\\')[-1]+'_Traffic_Sign_Wise_Count.csv', arr, delimiter=',', fmt='%f',
                   header='Traffic_sign_Id,GT,TruePositive,FalsePositive,FalseNegative')  # path.split('/')[-1]

        #if (os.path.exists(path+".json")):
            #os.remove(path + ".json")