# -*- dataeval: init -*-

import datavis
from interface import iView


class View(iView):
    def check(self):
        sgs = [
            {
                "ui8_BlockageStatus": ("MFC5xx Device.CB.pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
                "FrontAxleSpeed": ("EBC2", "FrontAxleSpeed_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "ui8_BlockageStatus": ("MFC5xx Device.CB.pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
                "FrontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "ui8_BlockageStatus": ("MFC5xx Device.CB.pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
                "FrontAxleSpeed": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                   "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
                "steering_wheel_angle": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
                                         "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            },
            {
                "ui8_BlockageStatus": (
                    "pCbRteOut", "MFC5xx_Device_CB_pCbRteOut_ui8_BlockageStatus"),
                "FrontAxleSpeed": (
                    "MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),
                "steering_wheel_angle": (
                    "MTSI_stKBFreeze_020ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_driver_steering_wheel_angle"),
            }
        ]
        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="Blockage Status", yAutoZoom=True, fontSize='xx-small')
        mapping_yticks = {0: "CB_UNKNOWN_STATUS", 1: "CB_NO_BLOCKAGE", 3: "CB_CONDENSATION", 4: "CB_TOP_PART_BLOCKAGE",
                          5: "CB_BOTTOM_PART_BLOCKAGE", 6: "CB_BLOCKAGE", 7: "CB_LEFT_PART_BLOCKAGE",
                          8: "CB_RIGHT_PART_BLOCKAGE"}
        mapping_yticks = dict((k, "(%s) %d" % (v, k)) for k, v in mapping_yticks.iteritems())

        ax = pn.addAxis(ylabel="Blockage status", yticks=mapping_yticks)
        ax.set_ylim((-1.0, 8.0))
        if 'ui8_BlockageStatus' in group:
            time00, value00, unit00 = group.get_signal_with_unit("ui8_BlockageStatus")
            pn.addSignal2Axis(ax, "blockage status", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Ego Speed")
        if 'FrontAxleSpeed' in group:
            time00, value00, unit00 = group.get_signal_with_unit("FrontAxleSpeed")
            pn.addSignal2Axis(ax, "ego speed", time00, value00, unit=unit00)

        ax = pn.addAxis(ylabel="Steering Wheel Angle")
        if 'steering_wheel_angle' in group:
            time00, value00, unit00 = group.get_signal_with_unit("steering_wheel_angle")
            pn.addSignal2Axis(ax, "steering_wheel_angle", time00, value00, unit=unit00)

        self.sync.addClient(pn)
        return
