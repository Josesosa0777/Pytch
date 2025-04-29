# -*- dataeval: init -*-

"""
:Name:
	view_postmarker_traffic_data.py

:Type:
	View script

:Visualization Type:
	Table visualization

:Full Path:
	dataevalaebs/src/tsreval/view_postmarker_traffic_data.py

:Sensors:
	FLC25(CEM_TPF)

:Short Description:
		Postmarker tool is an internal tool developed for labeling ground truth data. This manually labeled data is
		then compared with actual MFC525 camera detected traffic sign data. This search script finds out all such
		intervals where there is a label. This is the used for detailed analysis with conti sensor data.
		It stores conti sign class ID and postmarker_Lane_ref status.
		the sign is of type speed limit etc.

:Large Description:
	Event information shown in the table:
		Sign Class ID : Conti Sign Class ID
		Sign Picture
		Sign Class Name : Sign Class Name
		Value : Sign value if applicatble
		Sign Status : postmarker_Lane_ref status
	Usage:
		- Shows postmarker traffic sign event details from JSON file in a tabular format

:Dependencies:
	fill_postmarker_traffic_signs@aebs.fill

:Output Data Image/s:
	.. image:: ../images/view_postmarker_traffic_data.png


"""

import os
from collections import OrderedDict
import datavis
from interface import iView
init_params = {
    "default": dict(flag=dict(tsr_default=True)),
    "REPORT": dict(flag=dict(tsr_report=True)),
}


class cMyView(iView):
    dep = "fill_postmarker_traffic_signs@aebs.fill"

    def init(self, flag):
        self.flag = flag

    def check(self):
        modules = self.get_modules()
        # Header names should match objects keys
        # table_headers mapping:  {<key_in_objects> : <key_to_show_in_headers>}

        table_headers_mapping = OrderedDict(
                [
                    ("sign_class_id", "Sign Class ID"),
                    ("sign_icon_path", "Sign Picture"),
                    ("sign_class", "Sign Class Name"),
                    ("sign_value", "Value"),
                    ("sign_status", "Postmarker_Lane_ref"),
                    ("sign_quantity", "Quantity"),
                ]
        )

        time, objects,resim_deviation,traffic_sign_report = modules.fill("fill_postmarker_traffic_signs@aebs.fill")
        if self.flag.get("tsr_report"):
            table_headers_mapping = OrderedDict(
                    [
                        ("sign_class_id", "SignID"),
                        ("sign_value", "Value"),
                        ("sign_status", "Existance"),
                        ("sign_quantity", "Quantity"),
                    ]
            )
        return time, objects, table_headers_mapping

    def view(self, time, objects, table_headers_mapping):

        table_nav = datavis.cTableNavigator(
            title="Traffic sign data from Postmarker JSON"
        )
        self.sync.addClient(table_nav)

        table_nav.addtabledata(time, objects, table_headers_mapping)
        return


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"E:\measurements\TSR_evaluation\with_postmarker_data\HMC-QZ-STR__2021-02-24_14-51-04.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    manager.build(["view_postmarker_traffic_visualizer@tsreval"], show_navigators=True)
    print("Done")
