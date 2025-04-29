# -*- dataeval: init -*-
import logging

import numpy as np

import datavis
from interface import iView

logger = logging.getLogger()


def unpackBits(x, num_bits):
    if np.issubdtype(x.dtype, np.floating):
        x = x.astype(int)
        logger.warning("Numpy data type had to be casted to integer!")
    xshape = list(x.shape)
    x = x.reshape([-1, 1])
    mask = 2 ** np.arange(num_bits, dtype=x.dtype).reshape([1, num_bits])
    return (x & mask).astype(bool).astype(int).reshape(xshape + [num_bits])


class cMyView(iView):
    dep = "fill_flc25_paebs_debug@aebs.fill"

    def check(self):
        sgs = [
            {
                "prob_entry_cw_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_warning_entry_prob_min",
                ),
                "prob_entry_pb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_partial_braking_entry_prob_min",
                ),
                "prob_entry_eb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_emergency_braking_entry_prob_min",
                ),
                "prob_entry_icb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_icb_entry_prob_min",
                ),
                "prob_entry_lsb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_low_speed_entry_prob_min",
                ),
                "prob_cancel_cw_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_warning_cancel_prob_max",
                ),
                "prob_cancel_pb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_partial_braking_cancel_prob_max",
                ),
                "prob_cancel_eb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_emergency_braking_cancel_prob_max",
                ),
                "flts_paebs_class_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_class_check_enable"
                ),
                "flts_paebs_source_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_source_check_enable"
                ),
                "flts_paebs_object_flags_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_object_flags_check_enable"
                ),
                "flts_paebs_quality_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_quality_check_enable"
                ),
                "flts_paebs_motion_state_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_motion_state_check_enable"
                ),
                "flts_paebs_life_time_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_life_time_check_enable"
                ),
                "flts_paebs_lane_conf_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_lane_conf_check_enable"
                ),
                "flts_paebs_ego_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_ego_lane_check_enable"
                ),
                "flts_paebs_adj_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_adj_lane_check_enable"
                ),
                "flts_paebs_border_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_border_lane_check_enable"
                ),
                "flts_paebs_ttc_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_ttc_check_enable"
                ),
                "flts_paebs_source_radar_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_paebs_source_radar_check_enable"),
            },
            {
                "prob_entry_cw_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_warning_entry_prob_min",
                ),
                "prob_entry_pb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_partial_braking_entry_prob_min",
                ),
                "prob_entry_eb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_emergency_braking_entry_prob_min",
                ),
                "prob_entry_icb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_icb_entry_prob_min",
                ),
                "prob_entry_lsb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_low_speed_entry_prob_min",
                ),
                "prob_cancel_cw_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_warning_cancel_prob_max",
                ),
                "prob_cancel_pb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_partial_braking_cancel_prob_max",
                ),
                "prob_cancel_eb_thresh": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_PaebsParams_paebs_emergency_braking_cancel_prob_max",
                ),
                "flts_paebs_class_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_class_check_enable"
                ),
                "flts_paebs_source_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_source_check_enable"
                ),
                "flts_paebs_object_flags_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_object_flags_check_enable"
                ),
                "flts_paebs_quality_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_quality_check_enable"
                ),
                "flts_paebs_motion_state_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_motion_state_check_enable"
                ),
                "flts_paebs_life_time_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_life_time_check_enable"
                ),
                "flts_paebs_lane_conf_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_lane_conf_check_enable"
                ),
                "flts_paebs_ego_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_ego_lane_check_enable"
                ),
                "flts_paebs_adj_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_adj_lane_check_enable"
                ),
                "flts_paebs_border_lane_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_border_lane_check_enable"),

                "flts_paebs_ttc_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_ttc_check_enable"),

                "flts_paebs_source_radar_check_enable": (
                    "MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
                    "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_ImParams_flts_paebs_source_radar_check_enable"),
            },
        ]
        modules = self.get_modules()
        paebs_objects_data = modules.fill("fill_flc25_paebs_debug@aebs.fill")

        # select signals
        group = self.source.selectLazySignalGroup(sgs)
        # give warning for not available signals
        for alias in sgs[0]:
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        return paebs_objects_data, group

    def view(self, paebs_objects_data, group):
        t = paebs_objects_data.time

        pn = datavis.cPlotNavigator(title="PAEBS Debug Data")

        # Plot 1: Collision Analysis
        # Axis left
        ax = pn.addAxis(ylabel="Distance", ylim=(0.0, 50.0))
        pn.addSignal2Axis(
            ax,
            "Cascade Distance",
            t,
            paebs_objects_data[0].casc_dist,
            color="r",
            unit="m",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Lon. Distance along Ego Path",
            t,
            paebs_objects_data[0].dist_path,
            color="b",
            unit="m",
            ls="-",
        )

        if hasattr(paebs_objects_data[0], 'dist_react'):
            pn.addSignal2Axis(ax, 'ARS Reaction Distance', t, paebs_objects_data[0].dist_react, ls="--", color="m", unit="m")
            ax.fill_between(t, paebs_objects_data[0].dist_react, 300.0, color="black", alpha="0.3")

        # Axis right
        ax = pn.addTwinAxis(ax, ylabel="Time", color="g")
        pn.addSignal2Axis(
            ax, "TTC", t, paebs_objects_data[0].ttc, color="g", unit="s", ls="-"
        )

        # Plot 2: Cascade Probabilities
        data = paebs_objects_data[0].collision_prob * 100
        ax = pn.addAxis(ylabel="Probability")
        pn.addSignal2Axis(
            ax,
            "Collision Probability",
            t,
            data.astype(int),
            color="r",
            unit="%",
            ls="-",
        )
        # Parameter Graphs
        if "prob_entry_cw_thresh" in group:
            time, value = group.get_signal("prob_entry_cw_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "CW Entry", time, data.astype(int), color="g", ls="-", unit="%"
            )
        if "prob_entry_pb_thresh" in group:
            time, value = group.get_signal("prob_entry_pb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "PB Entry", time, data.astype(int), color="b", ls="-", unit="%"
            )
        if "prob_entry_eb_thresh" in group:
            time, value = group.get_signal("prob_entry_eb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "EB Entry", time, data.astype(int), color="m", ls="-", unit="%"
            )
        if "prob_entry_lsb_thresh" in group:
            time, value = group.get_signal("prob_entry_lsb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "LSB Entry", time, data.astype(int), color="c", ls="-", unit="%"
            )
        if "prob_entry_icb_thresh" in group:
            time, value = group.get_signal("prob_entry_icb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "ICB Entry", time, data.astype(int), color="#FFA500", ls="-", unit="%"
            )
        if "prob_cancel_cw_thresh" in group:
            time, value = group.get_signal("prob_cancel_cw_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "CW Cancel", time, data.astype(int), color="g", ls="--", unit="%"
            )
        if "prob_cancel_pb_thresh" in group:
            time, value = group.get_signal("prob_cancel_pb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "PB Cancel", time, data.astype(int), color="b", ls="--", unit="%"
            )
        if "prob_cancel_eb_thresh" in group:
            time, value = group.get_signal("prob_cancel_eb_thresh")
            data = value * 100
            pn.addSignal2Axis(
                ax, "EB Cancel", time, data.astype(int), color="m", ls="--", unit="%"
            )

        # Plot 3: Cascade Commands
        mapping = {0: "False", 1: "True"}
        # Axis left
        ax = pn.addAxis(
            ylabel="Cascade Command Status",
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
        )
        pn.addSignal2Axis(
            ax,
            "Allow Collision Warning",
            t,
            paebs_objects_data[0].allow_cw,
            unit="",
            color="g",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Allow Partial Braking",
            t,
            paebs_objects_data[0].allow_pb,
            unit="",
            color="b",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Allow Emergency Braking",
            t,
            paebs_objects_data[0].allow_eb,
            unit="",
            color="m",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Allow In-Crash Braking",
            t,
            paebs_objects_data[0].allow_icb,
            unit="",
            color="#FFA500",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Allow Standstill Braking",
            t,
            paebs_objects_data[0].allow_ssb,
            unit="",
            color="c",
            ls="-",
        )
        pn.addSignal2Axis(
            ax,
            "Cancel Collision Warning",
            t,
            paebs_objects_data[0].cancel_cw,
            unit="",
            color="g",
            ls="--",
        )
        pn.addSignal2Axis(
            ax,
            "Cancel Partial Braking",
            t,
            paebs_objects_data[0].cancel_pb,
            unit="",
            color="b",
            ls="--",
        )
        pn.addSignal2Axis(
            ax,
            "Cancel Emergency Braking",
            t,
            paebs_objects_data[0].cancel_eb,
            unit="",
            color="m",
            ls="--",
        )
        # Axis right
        ax = pn.addTwinAxis(
            ax,
            ylabel="in Path Flag",
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
            color="r",
        )
        pn.addSignal2Axis(
            ax, "in Path", t, paebs_objects_data[0].in_path, unit="", color="r", ls="-"
        )

        # Plot 4: States
        # Axis left
        mapping = {
            0: "None",
            1: "Not Ready",
            2: "TemporarilyNotAvailable",
            3: "DeactivatedByDriver",
            4: "Ready",
            5: "DriverOverride",
            6: "LowSpeedBraking",
            7: "Warning",
            8: "PartialBraking",
            9: "PartialBrakingIcb",
            10: "PartialBrakingSsb",
            11: "EmergencyBraking",
            12: "EmergencyBrakingIcb",
            13: "EmergencyBrakingSsb",
            14: "Error",
            15: "BrakeHold",
            16: "LowSpeedBrakingBrakeHold"
        }
        ax = pn.addAxis(
            ylabel="Internal State",
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
        )
        pn.addSignal2Axis(
            ax,
            "Internal State",
            t,
            paebs_objects_data[0]["internal_state"],
            unit="",
            color="b",
            ls="-",
        )
        # Axis left
        mapping = {0: "False", 1: "True"}
        ax = pn.addTwinAxis(
            ax,
            ylabel="Status",
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
            color="g",
        )
        pn.addSignal2Axis(
            ax,
            "Override active",
            t,
            paebs_objects_data[0].override_active,
            color="r",
            ls="-",
        )
        pn.addSignal2Axis(
            ax, "Operational", t, paebs_objects_data[0].operational, color="g", ls="-"
        )

        # Plot 5: PAEBS Bitfield and Object Flags (Optional)
        # Axis left
        if hasattr(paebs_objects_data[0], 'paebs_bitfield_value') and hasattr(paebs_objects_data[0],
                                                                              'object_flags_value'):

            mapping_paebs_raw = {
                0: ('Class', 'flts_paebs_class_check_enable'),
                1: ('Source', 'flts_paebs_source_check_enable'),
                2: ('Object Flags', 'flts_paebs_object_flags_check_enable'),
                3: ('Quality', 'flts_paebs_quality_check_enable'),
                4: ('Motion State', 'flts_paebs_motion_state_check_enable'),
                5: ('TPF Life Time', 'flts_paebs_life_time_check_enable'),
                6: ('Lane Confidence', 'flts_paebs_lane_conf_check_enable'),
                7: ('Ego Lane', 'flts_paebs_ego_lane_check_enable'),
                8: ('Adjacent Lane', 'flts_paebs_adj_lane_check_enable'),
                9: ('Border Lane', 'flts_paebs_border_lane_check_enable'),
                10: ('TTC', 'flts_paebs_ttc_check_enable'),
                11: ('Source Radar', 'flts_paebs_source_radar_check_enable'),
            }

            mapping_paebs = {key: value[0] for key, value in mapping_paebs_raw.items()}
            mapping_params = {key: value[1] for key, value in mapping_paebs_raw.items()}

            mapping_object = {
                12: "PoE valid",
                13: "Maintenance State valid",
                14: "RCS VRU valid",
                15: "ID dx valid",
            }

            l_max = len(mapping_paebs) + len(mapping_object)
            mapping_combined = mapping_paebs.copy()
            mapping_combined.update(mapping_object)
            mapping_ticks_paebs = {key: ('' if key > len(mapping_paebs) - 1 else value) for key, value in
                                   mapping_combined.items()}
            mapping_ticks_object = {key: ('' if key <= len(mapping_paebs) - 1 else value) for key, value in
                                    mapping_combined.items()}

            num = paebs_objects_data[0].paebs_bitfield_value
            res = unpackBits(num, len(mapping_paebs))
            bitfields_collector = np.split(res, len(mapping_paebs), 1)

            ax = pn.addAxis(
                ylabel="FLTS PAEBS Bitfields",
                yticks=mapping_ticks_paebs,
                ylim=(- 0.5, l_max - 0.5),
            )

            for i, bitfields in enumerate(bitfields_collector):
                bitfields = bitfields.reshape(-1)
                bitfields = np.ma.masked_where(bitfields == 0, bitfields)
                bitfields = np.ma.where(bitfields == 1, np.int(i), bitfields)

                time, value = group.get_signal(mapping_params[i])

                if bool(value[0]):
                    ls = '-'
                else:
                    ls = '--'

                pn.addSignal2Axis(
                    ax,
                    mapping_combined[i],
                    t,
                    bitfields,
                    unit="",
                    color="b",
                    ls=ls,
                )

            # Axis right

            num = paebs_objects_data[0].object_flags_value
            res = unpackBits(num, len(mapping_object))
            bitfields_collector = np.split(res, len(mapping_object), 1)

            ax = pn.addTwinAxis(
                ax,
                ylabel="FLTS Object Flags",
                yticks=mapping_ticks_object,
                ylim=(- 0.5, l_max - 0.5),
                color="r"
            )

            for i, bitfields in enumerate(bitfields_collector):
                j = i + len(mapping_paebs)
                bitfields = bitfields.reshape(-1)
                bitfields = np.ma.masked_where(bitfields == 0, bitfields)
                bitfields = np.ma.where(bitfields == 1, np.int(j), bitfields)

                pn.addSignal2Axis(
                    ax,
                    mapping_combined[j],
                    t,
                    bitfields,
                    unit="",
                    color="r",
                    ls="-",
                )

        else:
            logger.warning(
                'Signal "paebs_bitfield_value" and/or "object_flags_value" not available. '
                'Will not be plotted by {script}'.format(script=__name__))

        self.sync.addClient(pn)

        return
