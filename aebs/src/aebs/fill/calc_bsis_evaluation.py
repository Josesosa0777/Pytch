# -*- dataeval: init -*-

from interface import iCalc

sgs = [
    {
        "WarningLevel_Front": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Front_D0"),
        "WarningLevel_Right": ("CAN_MFC_Public_BSD2_D0", "BSD2_WarningLevel_Right_D0"),

        # Using Alternative signal for Quantity for BSIS
        "LatDispMIORightSide": ("CAN_MFC_Public_BSD4_D0", "BSD4_LatDispMIORightSide_D0"),
        "LonDispMIORightSide": ("CAN_MFC_Public_BSD4_D0", "BSD4_LonDispMIORightSide_D0"),

        # Quantity for MOIS
        "LatDispMIOFront": ("CAN_MFC_Public_BSD5_D0", "BSD5_LatDispMIOFront_D0"),
        "LonDispMIOFront": ("CAN_MFC_Public_BSD5_D0", "BSD5_LonDispMIOFront_D0"),

        "FrontAxleSpeed": ("CAN_MFC_Public_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
    }

]


class cFill(iCalc):
    dep = ('calc_common_time-flr25')

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        time = self.modules.fill('calc_common_time-flr25')

        warning_level_front_time, warning_level_front_value, warning_level_front_unit = group.get_signal_with_unit(
            'WarningLevel_Front', ScaleTime=time)
        warning_level_right_time, warning_level_right_value, warning_level_right_unit = group.get_signal_with_unit(
            'WarningLevel_Right', ScaleTime=time)

        LatDispMIORightSide_time, LatDispMIORightSide_value, LatDispMIORightSide_unit = group.get_signal_with_unit(
            'LatDispMIORightSide', ScaleTime=time)
        LonDispMIORightSide_time, LonDispMIORightSide_value, LonDispMIORightSide_unit = group.get_signal_with_unit(
            'LonDispMIORightSide', ScaleTime=time)

        LatDispMIOFront_time, LatDispMIOFront_value, LatDispMIOFront_unit = group.get_signal_with_unit(
            'LatDispMIOFront', ScaleTime=time)
        LonDispMIOFront_time, LonDispMIOFront_value, LonDispMIOFront_unit = group.get_signal_with_unit(
            'LonDispMIOFront', ScaleTime=time)

        FrontAxleSpeed_time, FrontAxleSpeed_value, FrontAxleSpeed_unit = group.get_signal_with_unit(
            'FrontAxleSpeed', ScaleTime=time)

        # SRR Warning
        MOIS_warning_from_front = (warning_level_front_value >= 1)

        BSIS_warning_from_right = (warning_level_right_value >= 1) & (FrontAxleSpeed_value>0) & (FrontAxleSpeed_value<33)

        LCDA_warning_from_right = (warning_level_right_value >= 1) & (FrontAxleSpeed_value>43) & (FrontAxleSpeed_value<90)

        return time,  warning_level_front_value,warning_level_right_value,MOIS_warning_from_front, BSIS_warning_from_right, \
            LatDispMIORightSide_value, LonDispMIORightSide_value, LatDispMIOFront_value, LonDispMIOFront_value, LCDA_warning_from_right


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\pytch2_development\SRR_eval\meas\2024-08-28\mi5id5506__2024-08-28_14-51-16.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    flr25_egomotion = manager_modules.calc('calc_bsis_evaluation@aebs.fill', manager)
