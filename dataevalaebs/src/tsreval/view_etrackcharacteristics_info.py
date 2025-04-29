# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView
from collections import OrderedDict
import copy


class View(iView):
    def check(self):
        sgs = [
            {
                "etrackCharacteristics_1": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark0_Specifics_TrafficSign_etrackCharacteristics"),
                "etrackCharacteristics_2": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark1_Specifics_TrafficSign_etrackCharacteristics"),
                "etrackCharacteristics_3": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark2_Specifics_TrafficSign_etrackCharacteristics"),
                "uId_1": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark0_uId"),
                "uId_2": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark1_uId"),
                "uId_3": (
                    "MFC5xx Device.LMK.LmkGenLandmarkList",
                    "MFC5xx_Device_LMK_LmkGenLandmarkList_aLandmark2_uId"),

            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        etrack_objects,etrack_objects1,etrack_objects2,etrack_objects3 = [],[],[],[]

        if 'etrackCharacteristics_1' in group and 'uId_1' in group:
            time00, value00, unit00 = group.get_signal_with_unit("etrackCharacteristics_1")
            time11, value11, unit11 = group.get_signal_with_unit("uId_1")
            obj = {}
            obj['etrackCharacteristics'] = value00
            obj['uId'] = value11
            obj['valid'] = (value11 != 255)
            binary_value = np.array([np.binary_repr(value, width=16) for value in value00])
            obj['binary_value'] = binary_value
            etrack_objects1.append(obj)

        if 'etrackCharacteristics_2' in group and 'uId_2' in group:
            time22, value22, unit22 = group.get_signal_with_unit("etrackCharacteristics_2")
            time33, value33, unit33 = group.get_signal_with_unit("uId_2")
            obj = {}
            obj['etrackCharacteristics'] = value22
            obj['uId'] = value33
            obj['valid'] = (value33 != 255)
            binary_value = np.array([np.binary_repr(value, width=16) for value in value22])
            obj['binary_value'] = binary_value
            etrack_objects2.append(obj)

        if 'etrackCharacteristics_3' in group and 'uId_3' in group:
            time44, value44, unit44 = group.get_signal_with_unit("etrackCharacteristics_3")
            time55, value55, unit55 = group.get_signal_with_unit("uId_3")
            obj = {}
            obj['etrackCharacteristics'] = value44
            obj['uId'] = value55
            obj['valid'] = (value55 != 255)
            binary_value = np.array([np.binary_repr(value, width=16) for value in value44])
            obj['binary_value'] = binary_value
            etrack_objects3.append(obj)
            
        etrack_objects = etrack_objects1 + etrack_objects2 + etrack_objects3

        table_headers_mapping = OrderedDict(
            [
                ("uId", "uID"),
                ("etrackCharacteristics","Decimal_value"),
                ("binary_value", "Binary_value"),
            ]
        )
        return time00, etrack_objects, table_headers_mapping

    def view(self, time00, valid_object, table_headers_mapping):

        table_nav = datavis.cTableNavigator(title="View Etrack Characteristic")
        self.sync.addClient(table_nav)

        table_nav.addtabledata(time00, valid_object, table_headers_mapping)

        return


if __name__ == "__main__":
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\TSR_evaluation\data\europe_data\2021-10-11\mi5id787__2021-10-11_16-06-46_tsrresim.h5"
    config, manager, manager_modules = init_dataeval(["-m", meas_path])
    manager.build(["view_etrackcharacteristics_info@tsreval"], show_navigators=True)
    print("Done")