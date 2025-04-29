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
    is_can_detected_value: Used "MFC5xx_Device_LMK_LmkGenLandmarkList_HeaderLmkList_TSSDetectedValue" signal
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

  "TSSDetectedValue": ("FLC_PROP1_sE8", "TSSDetectedValue"),
},
{

  "TSSDetectedValue": ("FLC_PROP1_E8_sE8", "FLCProp1_TSSDetectedValue_E8"),

},
{

  "TSSDetectedValue": ("FLC_PROP1","TSSDetectedValue_sE8"),

},
  {

  "TSSDetectedValue": ("FLC_PROP1_E8","FLCProp1_TSSDetectedValue_E8_sE8"),

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
            logging.warning("'calc_resim_deviation' failed dependency.. Please check signal groups if it is resim measurement.")


        return common_time, group, objects, indexes

    def fill(self, common_time, group, objects, indexes):
        return common_time, group, objects, indexes

    def view(self, common_time, group, objects, indexes):


        pn = datavis.cPlotNavigator(
            title="TSR evaluation : Postmarker ground truth data and CAN TSSDetectedValue"
        )
        self.sync.addClient(pn)
        time, value, _ = group.get_signal_with_unit(
            "TSSDetectedValue", ScaleTime=common_time
        )
        time_is_can_detected_value = common_time
        value_is_can_detected_value = value != 251
        value_is_can_detected_value = shift(value_is_can_detected_value, indexes, False)
        mapping = {0: "Not detected", 1: "Detected"}
        axis00 = pn.addAxis(
            ylabel="Sign detection",
        )

        pn.addSignal2Axis(axis00,"TSSDetectedValue",time,value,color="blue",linewidth=1.5,)


        pn.addSignal2Axis(
            axis00,
            "Postmarker_Label",
            time_is_can_detected_value,
            objects[0]["sign_value_for_can"],
            color="red",
            linewidth=1.5,
            marker="o",
        )


        return
