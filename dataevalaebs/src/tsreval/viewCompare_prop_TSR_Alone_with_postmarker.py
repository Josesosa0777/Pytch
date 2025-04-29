# -*- dataeval: method -*-
# -*- coding: utf-8 -*-

"""
:Name:
	viewCompare_can_tsr_with_postmarker.py

:Type:
	View script

:Visualization Type:
	Plot

:Full Path:
	dataevalaebs/src/tsreval/viewCompare_can_tsr_with_postmarker.py

:Sensors:
	FLC25(CEM_TPF), postmarking data from JSON

:Short Description:
		TSR(Traffic sign recognition) is one of the safety and comfort ADAS function. It is important to check accurancy of information provided by camera sensor.
		This information is mainly sign class id, longitudinal distance, lateral distance etc. This information is visualized using different visualizers in Python Toolchain.
		Which then compared with manually labeled data from Postmarker tool using.

:Large Description:
	Event information shown in the table:
    is_propTSRAlone_value: Used "MFC5xx_Device_LMK_LmkGenLandmarkList_HeaderLmkList_TSSDetectedValue" signal
    is_postmarker_sign_detected: Data from postmarker
	Usage:
		- Shows comparison signals for postmarker traffic sign from JSON file and the can data

:Dependencies:
	fill_postmarker_traffic_signs@aebs.fill

:Output Data Image/s:
	.. image:: ../images/viewCompare_can_tsr_with_postmarker.png

.. note::
	For source code click on [source] tag beside functions
"""

import interface
import numpy as np
import datavis
from aebs.fill.fillFLC25_TSR import shift
import logging
sgs  = [
{
  "TSR_SpeedLimit1_E8_sE8": ("PropTSRAlone_E8","TSR_SpeedLimit1_E8_sE8"),
},

]


class View(interface.iView):
    dep = "fill_postmarker_traffic_signs@aebs.fill"
    optdep = ("calc_resim_deviation@aebs.fill")


    def check(self):
        modules = self.get_modules()
        group = self.source.selectSignalGroup(sgs)
        common_time, objects , resim_deviation,traffic_sign_report= modules.fill("fill_postmarker_traffic_signs@aebs.fill")
        indexes = 0

        if 'calc_resim_deviation@aebs.fill' in self.passed_optdep:
            _, indexes = modules.fill(self.optdep)
        else:
            logging.warning("'calc_resim_deviation' failed dependency.. Please check signal groups if it is resim "
                            "measurement.")


        return common_time, group, objects, indexes

    def fill(self, common_time, group, objects, indexes):
        return common_time, group, objects, indexes

    def view(self, common_time, group, objects, indexes):


        pn = datavis.cPlotNavigator(
            title="TSR evaluation : Postmarker ground truth data and PropTSRAlone_E8"
        )
        self.sync.addClient(pn)
        time, value, _ = group.get_signal_with_unit(
            "TSR_SpeedLimit1_E8_sE8", ScaleTime=common_time
        )
        time_is_propTSRAlone_value = common_time
        value_is_propTSRAlone_value = value

        mapping ={1 : "5", 2 :"10",  3 :"15",4 :"20",5 :"25", 6 :"30", 7 :"35",8 :"40", 9 :'45',10 :"50",11 :"55",12 :"60",13 :"65",\
                14 :"70",15 :"75",16 :"80", 17 :"85",18 :"90",19 :"95",20 :"100",21 :"105", 22 :"110", 23 :"115",24 :"120", 25 :"125",\
                26 :"130",27 :"135",28 :"140" }#,29 : "282",30 : "282",31:"310", 32:"311",35:"331",36:"336"}

        for val in mapping.keys():
            value_is_propTSRAlone_value[value_is_propTSRAlone_value==val]=mapping[val]

        value_is_propTSRAlone_value = shift(value_is_propTSRAlone_value, indexes, False)
        axis00 = pn.addAxis(
            ylabel="Sign detection",
        )

        pn.addSignal2Axis(axis00,"TSR_SpeedLimit1_E8_sE8",time,value_is_propTSRAlone_value,color="blue",linewidth=1.5,)


        pn.addSignal2Axis(
            axis00,
            "Postmarker_Label",
            time_is_propTSRAlone_value,
            objects[0]["sign_value_for_can"],
            color="red",
            linewidth=1.5,
            marker="o",
        )


        return
