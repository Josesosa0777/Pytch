# -*- dataeval: init -*-

import datavis
from interface import iView

sgs = [
            {
                "left_lane_marking_type": ( "MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_type"),
                "left_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_id"),
                "ego_right_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_quality"),
                 "left_clothoidNear_offset": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_clothoidNear_offset"),

                "right_lane_marking_id": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_id"),
                "right_lane_marking_type": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_type"),

                "right_clothoidNear_offset": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_right_clothoidNear_offset"),
                "left_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t", "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_left_lane_marking_c0"),
                "right_lane_marking_c0": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AoaOutput_im_input_sensor_lanes_right_lane_marking_c0"),
                "ego_left_quality": ("MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_ego_left_quality"),
            },
        ]
class View(iView):
    def check(self):
        group = self.source.selectSignalGroupOrEmpty(sgs)
        return group

    def view(self, group):
        pn = datavis.cPlotNavigator(title="LD_Keep_Alive")
        axis00 = pn.addAxis()

        time_left_lane_marking_id, value_left_lane_marking_id, unit_left_lane_marking_id = group.get_signal_with_unit("left_lane_marking_id")
        pn.addSignal2Axis(axis00,
                                "left_lane_marking_id",
                                time_left_lane_marking_id,
                                value_left_lane_marking_id,
                                unit=unit_left_lane_marking_id)

        time_right_lane_marking_id, value_right_lane_marking_id, unit_right_lane_marking_id = group.get_signal_with_unit("right_lane_marking_id")

        pn.addSignal2Axis(axis00,
                                "right_lane_marking_id",
                                time_right_lane_marking_id,
                                value_right_lane_marking_id,
                                unit=unit_right_lane_marking_id)
        axis01 = pn.addAxis()

        time_custom_left_lane_marking_type, value_custom_left_lane_marking_type, unit_custom_left_lane_marking_type = group.get_signal_with_unit("left_lane_marking_type")
        rescale_kwargs = {'ScaleTime': time_custom_left_lane_marking_type}

        time_isVirtual = time_custom_left_lane_marking_type
        value_isVirtual = value_custom_left_lane_marking_type == 0
        unit_isVirtual = ""
        pn.addSignal2Axis(axis01, "isLeftVirtual", time_isVirtual, value_isVirtual, unit=unit_isVirtual)

        time_custom_right_lane_marking_type, value_custom_right_lane_marking_type, unit_custom_right_lane_marking_type = group.get_signal_with_unit("right_lane_marking_type")
        rescale_kwargs = {'ScaleTime': time_custom_right_lane_marking_type}
        time_isRightVirtual = time_custom_right_lane_marking_type
        value_isRightVirtual = value_custom_right_lane_marking_type == 0
        unit_isRightVirtual = ""
        pn.addSignal2Axis(axis01, "isRightVirtual", time_isRightVirtual, value_isRightVirtual,unit=unit_isRightVirtual)

        axis02 = pn.addAxis()
        time_left_clothoidNear_offset, value_left_clothoidNear_offset, unit_left_clothoidNear_offset = group.get_signal_with_unit("left_clothoidNear_offset")
        pn.addSignal2Axis(axis02, "left_clothoidNear_offset",
                                time_left_clothoidNear_offset,
                                value_left_clothoidNear_offset,
                                unit=unit_left_clothoidNear_offset)

        time_left_lane_marking_c0, value_left_lane_marking_c0, unit_left_lane_marking_c0 = group.get_signal_with_unit("left_lane_marking_c0")
        pn.addSignal2Axis(axis02,
                                "left_lane_marking_c0",
                                time_left_lane_marking_c0,
                                value_left_lane_marking_c0,
                                unit=unit_left_lane_marking_c0)

        axis03 = pn.addAxis()
        time_right_clothoidNear_offset, value_right_clothoidNear_offset, unit_right_clothoidNear_offset = group.get_signal_with_unit("right_clothoidNear_offset")
        pn.addSignal2Axis(axis03, "right_clothoidNear_offset",
                                time_right_clothoidNear_offset,
                                value_right_clothoidNear_offset,
                                unit=unit_right_clothoidNear_offset)

        time_right_lane_marking_c0, value_right_lane_marking_c0, unit_right_lane_marking_c0 = group.get_signal_with_unit("right_lane_marking_c0")
        pn.addSignal2Axis(axis03,
                                "right_lane_marking_c0",
                                time_right_lane_marking_c0,
                                value_right_lane_marking_c0,
                                unit=unit_right_lane_marking_c0)

        axis04 = pn.addAxis()
        time_ego_left_quality, value_ego_left_quality, unit_ego_left_quality = group.get_signal_with_unit("ego_left_quality")
        pn.addSignal2Axis(axis04, "ego_left_quality",
                                time_ego_left_quality,
                                value_ego_left_quality,
                                unit=unit_ego_left_quality)

        time_ego_right_quality, value_ego_right_quality, unit_ego_right_quality = group.get_signal_with_unit("ego_right_quality")
        pn.addSignal2Axis(axis04, "ego_right_quality",
                                time_ego_right_quality,
                                value_ego_right_quality,
                                unit=unit_ego_right_quality)
        self.sync.addClient(pn)
        return
