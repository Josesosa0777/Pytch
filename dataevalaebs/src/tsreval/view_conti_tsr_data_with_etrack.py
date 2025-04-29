# -*- dataeval: init -*-

"""
:Name:
	view_conti_tsr_data.py

:Type:
	View script

:Visualization Type:
	Table visualization

:Full Path:
	dataevalaebs/src/tsreval/view_conti_tsr_data.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
		Continental MFC525 Camera is used for detection of traffic sign objects in front of vehicles.
		MFC525 stores detected objects in object arrays[Maximum 50] internally with IDs 0-49.
		MFC525 camera also classifies the sign type[sign class id], sign status[Active/Inactive], Value in the sign if
		the sign is of type speed limit etc.

:Large Description:
	Event information shown in the table:
		uID : Conti sign id
		Sign Class ID : Conti Sign Class ID
		Sign Picture
		Sign Class Name : Sign Class Name
		Value : Sign value if applicatble
	Usage:
		- Shows traffic sign event details in a tabular format

:Dependencies:
	fillFLC25_TSR@aebs.fill

:Output Data Image/s:
	.. image:: ../images/view_conti_tsr_data.png
	   :height: 500px
	   :width: 500px
	   :scale: 50%
	   :alt: Plot Output
	   :align: left

:Signals:
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_uId"),
		("LmkGenLandmarkList",
		 "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_fMainExistenceProbability"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_eClassification"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_uiClassConfidence"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Specifics_TrafficSign_eSignId"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistX"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistY"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistZ"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Geometry_fHeight"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Geometry_fWidth"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistXStd"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistYStd"),
		("LmkGenLandmarkList", "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmarkI%dI_Generics_Position_fDistZStd"),
"""

import os
from collections import OrderedDict
import datavis
from interface import iView

init_params = {
    "CONTI_TSR": dict(flag=dict(tsr_default=True)),
    "REPORT": dict(flag=dict(tsr_report=True)),
    "CONTI_TSR_SUPPL": dict(flag=dict(tsr_suppl=True)),
    "CONTI_TSR_SHORTLISTED": dict(flag=dict(tsr_shortlisted=True)),
}


class cMyView(iView):
    optdep = "fillFLC25_TSR@aebs.fill", "fillFLC25_TSR_SUPPL@aebs.fill", "fillFLC25_TSR_SHORTLISTED@aebs.fill"

    def init(self, flag):
        self.flag = flag

    def check(self):
        modules = self.get_modules()
        subtitle = "All main signs"
        objects, objects1, objects2, objects3 = [], [], [], []

        # Header names should match objects keys
        # table_headers mapping:  {<key_in_objects> : <key_to_show_in_headers>}
        table_headers_mapping = OrderedDict(
                [
                    ("universal_id", "uID"),
                    ("traffic_sign_id", "Sign Class ID"),
                    ("sign_picture", "Sign Picture"),
                    ("sign_class", "Sign Class Name"),
                    ("sign_value", "Value"),
                    ("sign_visibility_status", "Sign Status"),
                    ("etrack","etrack"),
                    ("etrackBinary","etrackBinary")
                ]
        )

        if self.flag.get("tsr_shortlisted"):
            subtitle = "Shortlisted main signs"
            time, objects1 = modules.fill("fillFLC25_TSR_SHORTLISTED@aebs.fill")
        if self.flag.get("tsr_suppl"):
            subtitle = "Supplementary signs"
            time, objects2 = modules.fill("fillFLC25_TSR_SUPPL@aebs.fill")
        if self.flag.get("tsr_default"):
            time, objects3 = modules.fill("fillFLC25_TSR@aebs.fill")
        if self.flag.get("tsr_report"):
            time, objects3 = modules.fill("fillFLC25_TSR@aebs.fill")
            table_headers_mapping = OrderedDict(
                    [
                        ("universal_id", "uID"),
                        ("traffic_sign_id", "SignID"),
                        ("sign_value", "Value"),
                        ("sign_visibility_status", "Existance"),
                        ("etrack", "etrack"),
                        ("etrackBinary", "etrackBinary")
                    ]
            )

        objects = objects1 + objects2 + objects3
        return time, objects, subtitle, table_headers_mapping

    def view(self, time, objects, subtitle, table_headers_mapping):
        table_nav = datavis.cTableNavigator(title="Conti TSR data {}".format(subtitle))
        self.sync.addClient(table_nav)

        table_nav.addtabledata(time, objects, table_headers_mapping)

        return


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"E:\measurements\TSR_evaluation\with_postmarker_data\HMC-QZ-STR__2021-02-24_14-51-04.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    manager.build(["view_tsr_table_visualizer@tsreval"], show_navigators=True)
    print("Done")
