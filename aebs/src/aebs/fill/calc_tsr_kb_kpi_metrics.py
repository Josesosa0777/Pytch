# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


from interface import iCalc
import logging
import os
import numpy as np
from tsreval.view_tsr_can_signals import sgs as can_sgs_grp
from measparser.kb_kpi_evaluation import TSRKBKpiEvaluation
mainLogger = logging.getLogger('end_run_state')
logger = logging.getLogger('end_run')

class cFill(iCalc):
    dep = (
        "calc_common_time-tsrresim",
        "fill_postmarker_traffic_signs",
        "fillFLC25_TSR",
    )
    optdep = ("calc_resim_deviation",'Calc_PropTSRAlone',)

    def check(self):
        kpi_input_data = {}
        self.tsr_alone_signals={}
        source = self.get_source()

        self.module_all = self.get_modules()

        self.common_time = self.module_all.fill(self.dep[0])
        t, self.postmarker_tsr, resim_deviation, self.traffic_sign_report = self.modules.fill(
            self.dep[1])
        self.conti_tsr_time, conti_tsr_objects = self.modules.fill(self.dep[2])


        # If traffic sign data is not present skip processing to skip current measurement
        if not self.postmarker_tsr:
            logger.warning("Missing traffic sign data or could not extract data from postmarker json format")
            return kpi_input_data, {}
        self.common_time = self.module_all.fill(self.optdep[0])

        # CAN signals collection
        can_signal_group = self.source.selectSignalGroupOrEmpty(can_sgs_grp)
        self.can_signals = {}
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
            print ("TSR CAN signals missing, please update signal group in dataevalaebs/src/tsreval/view_tsr_can_signals.py")
            logger.critical(
                "TSR CAN signals missing, please update signal group in dataevalaebs/src/tsreval/view_tsr_can_signals.py")
        if self.can_signals=={}:
            self.tsr_alone_signals = self.modules.fill(self.optdep[1])

        idx = np.argwhere(self.postmarker_tsr[0]["is_sign_detected"].data == True)
        det_idx = idx.reshape(idx.shape[1], idx.shape[0])[0]
        gt_data=[]
        existance_true =0
        existance_false=0
        for gt_det_idx in det_idx:
            gt={}
            gt['weather_condition']=self.postmarker_tsr[0]['weather_condition'][gt_det_idx]
            gt['time_condition'] = self.postmarker_tsr[0]['time_condition'][gt_det_idx]
            gt['quantity'] = self.postmarker_tsr[0]['sign_quantity'][gt_det_idx]
            gt['conti_sign_class'] = self.postmarker_tsr[0]['sign_class_id'][gt_det_idx]
            gt['status'] = self.postmarker_tsr[0]['sign_status'][gt_det_idx]
            gt['sign_value'] = self.postmarker_tsr[0]['sign_value'][gt_det_idx]
            gt['sign_quantity'] = self.postmarker_tsr[0]['sign_quantity'][gt_det_idx]
            gt['sign_value_for_can'] = self.postmarker_tsr[0]['sign_value_for_can'][gt_det_idx]
            gt['resim_time'] = self.conti_tsr_time[gt_det_idx]
            if gt['status']:
                existance_true = existance_true + gt['quantity']
            else:
                existance_false = existance_false + gt['quantity']
            gt_data.append(gt)

        kpi_input_data["GT_data"]=gt_data
        kpi_input_data["GT_existance_false"] = existance_false
        kpi_input_data["GT_existance_true"] = existance_true
        kpi_input_data["can_data"] = self.can_signals
        kpi_input_data["PropTSRAlone"] = self.tsr_alone_signals
        kpi_input_data['postmarker_tsr'] = self.postmarker_tsr
        kpi_input_data['conti_tsr_time'] = self.conti_tsr_time
        kpi_input_data["confusion_matrix_image_path"] = os.path.splitext(source.FileName)[0] + ".png"
        kpi = TSRKBKpiEvaluation(kpi_input_data)
        return kpi_input_data, kpi

    def fill(self, kpi_input_data, kpi):

        # If traffic sign data is not present skip processing to skip current measurement
        if not self.postmarker_tsr:
            return self.conti_tsr_time, {}, {}
        self.filename = kpi_input_data["confusion_matrix_image_path"]
        self.folder_path = os.path.dirname(self.filename)
        if self.tsr_alone_signals == {}:
            cumulative_results,kpi_report=kpi.evaluateKpi()
        else:
            cumulative_results,kpi_report=kpi.evaluatePropTSRAloneKpi()
        kpi.displayData()
        return self.conti_tsr_time, kpi_report, cumulative_results


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\TSR\Ford_KBKPI_EU_Turkey\measurement\2021-10-11\mi5id787__2021-10-11_17-30-24_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_common_time = manager_modules.calc('calc_tsr_kb_kpi_metrics@aebs.fill', manager)
    print flr25_common_time
