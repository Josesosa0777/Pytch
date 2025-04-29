# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "frontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
    },
    {
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "frontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
    },
    {
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "frontAxleSpeed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
    },
    {
        "constructionSiteEventAvailable": (
            "MFC5xx Device.LD.LdOutput",
            "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        "frontAxleSpeed": ("CAN_MFC_Public_middle_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
    },
    {
        "constructionSiteEventAvailable": (
        "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
        "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_construction_zone_detected"),
        "frontAxleSpeed": ("CAN_MFC_Public_EBC2_0B", "EBC2_FrontAxleSpeed_0B"),
    }
]


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        common_time = self.modules.fill('calc_common_time-flc25')

        construction_site_time, construction_site_value, construction_site_unit = group.get_signal_with_unit(
            'constructionSiteEventAvailable', ScaleTime=common_time)
        frontAxleSpeed_time, frontAxleSpeed_value, frontAxleSpeed_unit = group.get_signal_with_unit(
            'frontAxleSpeed', ScaleTime=common_time)

        construction_site_masked_array = (construction_site_value == 1)

        return common_time, construction_site_masked_array, frontAxleSpeed_value


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Python_Toolchain_2\Evaluation_data\LDWS\constuction_site\2023-06-19\mi5id786__2023-06-19_11-14-17.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_construction_site_event@aebs.fill', manager)
    print data
