# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import numpy as np
import logging

from interface import iParameter, iView
import interface
import datavis

init_params = {'CascadePrediction': {'flag_casc_pred': True},
               'w/oCascadePrediction': {'flag_casc_pred': False}
               }

logger = logging.getLogger("view_paebs_object_data")


class PaebsDebugView(iView):
    dep = "fill_flc25_paebs_debug@aebs.fill"
    optdep = "fill_ground_truth_raw_tracks@aebs.fill"

    def init(self, flag_casc_pred):
        self.plot_casc_pred = flag_casc_pred

        return

    def check(self):
        self.module_all = self.get_modules()
        paebs_object = self.module_all.fill("fill_flc25_paebs_debug@aebs.fill")
        return paebs_object

    def view(self, paebs_object):
        if "fill_ground_truth_raw_tracks@aebs.fill" in self.passed_optdep:
            gt_track = self.module_all.fill("fill_ground_truth_raw_tracks@aebs.fill")
            paebs_object = paebs_object.rescale(gt_track["time"])
        else:
            logger.info("Ground truth data is not available")
            gt_track = {}

        t = paebs_object.time

        pn = datavis.cPlotNavigator(title="PAEBS Object Data")

        # Plot 1: Longitudinal Object Distance and CEM Object ID
        # Axis right
        ax = pn.addAxis(ylabel="x-Distance")
        pn.addSignal2Axis(ax, "dx", t, paebs_object[0].dx, color="b", unit="m", ls="-")

        dx_max = paebs_object[0].dx + paebs_object[0].dx_std
        dx_min = paebs_object[0].dx - paebs_object[0].dx_std

        pn.addSignal2Axis(ax, "dx_max", t, dx_max, ls="--", unit="m", color="#000000")
        pn.addSignal2Axis(ax, "dx_min", t, dx_min, ls="--", unit="m", color="#000000")
        ax.fill_between(t, dx_max, dx_min, color="green", alpha="0.3")

        if "dx" in gt_track:
            pn.addSignal2Axis(
                ax, "dx_gt", t, gt_track["dx"], color="r", unit="m", ls="-"
            )

        # Axis right

        ax = pn.addTwinAxis(
            ax,
            ylabel='CEM Object ID',
            ylim=(-1, 101),
            color="g",
        )

        cem_id = paebs_object[0].object_index
        cem_id_mask = np.where(cem_id <= 100, False, True)
        cem_id.mask = cem_id_mask

        pn.addSignal2Axis(ax, 'CEM Object ID', t, cem_id, ls="-", color="g", unit="")

        # Plot 2: Lateral Object Distance
        ax = pn.addAxis(ylabel="y-Distance")
        pn.addSignal2Axis(ax, "dy", t, paebs_object[0].dy, color="b", unit="m", ls="-")

        dy_max = paebs_object[0].dy + paebs_object[0].dy_std
        dy_min = paebs_object[0].dy - paebs_object[0].dy_std

        pn.addSignal2Axis(ax, "dy_max", t, dy_max, ls="--", color="#000000", unit="m")
        pn.addSignal2Axis(ax, "dy_min", t, dy_min, ls="--", color="#000000", unit="m")
        ax.fill_between(t, dy_max, dy_min, color="green", alpha="0.3")

        if hasattr(paebs_object[0], 'dy_ttc'):
            pn.addSignal2Axis(ax, "dy_ttc", t, paebs_object[0].dy_ttc, ls="-", color="g", unit="m")

        if "dy" in gt_track:
            pn.addSignal2Axis(
                ax, "dy_gt", t, gt_track["dy"], color="r", unit="m", ls="-"
            )
            if "vy_abs" in gt_track:
                dy_ttc_gt = gt_track["dy"] + gt_track["vy_abs"] * np.clip(
                    -1 * np.divide(gt_track["dx"], gt_track["vx"]), 0,
                    20)
                pn.addSignal2Axis(ax, 'dy_ttc_gt', t, dy_ttc_gt, color='#FFA500', unit='m', ls='-')

        # Plot 3: Longitudinal Velocity
        ax = pn.addAxis(ylabel="Lon. Velocity")
        pn.addSignal2Axis(
            ax, "vx_rel", t, paebs_object[0].vx, color="g", unit="m/s", ls="-"
        )
        pn.addSignal2Axis(
            ax, "vx_rel_ref", t, paebs_object[0].vx_ref, color="m", unit="m/s", ls="-"
        )

        if self.plot_casc_pred:
            pn.addSignal2Axis(
                ax, "vx_exp_red", t, paebs_object[0].expVelRed[0][0], color="#FF6300", unit="m/s", ls="-"
            )

        vx_rel_max = paebs_object[0].vx + paebs_object[0].vx_std
        vx_rel_min = paebs_object[0].vx - paebs_object[0].vx_std

        pn.addSignal2Axis(ax, "vx_rel_max", t, vx_rel_max, ls="--", color="#000000", unit="m/s")
        pn.addSignal2Axis(ax, "vx_rel_min", t, vx_rel_min, ls="--", color="#000000", unit="m/s")
        ax.fill_between(t, vx_rel_max, vx_rel_min, color="green", alpha="0.3")

        if "vx" in gt_track:
            pn.addSignal2Axis(
                ax, "vx_gt", t, gt_track["vx"], color="r", unit="m/s", ls="-"
            )

        pn.addSignal2Axis(
            ax, "vx_abs", t, paebs_object[0].vx_abs, color="b", unit="m/s", ls="-"
        )

        # Plot 4: Lateral Velocity
        ax = pn.addAxis(ylabel="Lat. Velocity")
        pn.addSignal2Axis(
            ax, "vy_abs", t, paebs_object[0].vy_abs, color="b", unit="m/s", ls="-"
        )

        vy_abs_max = paebs_object[0].vy_abs + paebs_object[0].vy_abs_std
        vy_abs_min = paebs_object[0].vy_abs - paebs_object[0].vy_abs_std

        pn.addSignal2Axis(ax, "vy_abs_max", t, vy_abs_max, ls="--", color="#000000", unit="m/s")
        pn.addSignal2Axis(ax, "vy_abs_min", t, vy_abs_min, ls="--", color="#000000", unit="m/s")
        ax.fill_between(t, vy_abs_max, vy_abs_min, color="green", alpha="0.3")

        if "vy_abs" in gt_track:
            pn.addSignal2Axis(
                ax, "vy_abs_gt", t, gt_track["vy_abs"], color="r", unit="m/s", ls="-"
            )

        pn.addSignal2Axis(
            ax, "vy_rel", t, paebs_object[0].vy, color="b", unit="m/s", ls="--"
        )

        # Plot 5: Classifications
        ylabel_text = "Obj. Motion State"
        mapping = {
            0: "Not Detected",
            1: "Moving",
            2: "Stopped",
            3: "Static",
            4: "Crossing",
            5: "Oncoming",
            6: "Default",
            15: "Not Available",
        }
        ax = pn.addAxis(
            ylabel=ylabel_text,
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
        )
        pn.addSignal2Axis(
            ax,
            "Motion State",
            t,
            paebs_object[0].motion_state,
            unit="",
            color="b",
            ls="-",
        )

        ylabel_text = "Associated Lane"
        mapping = {
            0: "Unknown",
            1: "Ego",
            2: "Left",
            3: "Right",
            4: "Outside Left",
            5: "Outside Right",
            6: "Outside of Road Left",
            7: "Outside of Road Right",
            8: "Not Available",
        }
        ax = pn.addTwinAxis(
            ax,
            ylabel=ylabel_text,
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
            color="g",
        )
        pn.addSignal2Axis(
            ax,
            "Lane State",
            t,
            paebs_object[0].lane,
            unit="",
            color="g",
            ls="-",
        )
        # Plot 6: Object Detection
        # Left Axis
        ylabel_text = "Object Type"
        mapping = {
            0: "Point",
            1: "Car",
            2: "Truck",
            3: "Pedestrian",
            4: "Motorcycle",
            5: "Bicycle",
            6: "Wide",
            7: "Unclassified",
            8: "Other Vehicle",
            15: "Not Available",
        }
        ax = pn.addAxis(
            ylabel=ylabel_text,
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
        )
        pn.addSignal2Axis(
            ax, ylabel_text, t, paebs_object[0].obj_type, unit="", color="b", ls="-"
        )
        # Right Axis
        ylabel_text = "Sensor Source"
        mapping = {
            0: "Unkown",
            1: "Radar only",
            2: "Camera only",
            3: "Fused",
            4: "Not Available",
        }
        ax = pn.addTwinAxis(
            ax,
            ylabel=ylabel_text,
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5),
            color="g",
        )
        pn.addSignal2Axis(
            ax, ylabel_text, t, paebs_object[0].obj_src, unit="", color="g", ls="-"
        )

        self.sync.addClient(pn)
        return
