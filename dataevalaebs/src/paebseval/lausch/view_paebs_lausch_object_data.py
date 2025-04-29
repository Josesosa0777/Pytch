# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import numpy as np
import logging

from interface import iView
import datavis

logger = logging.getLogger("view_paebs_lausch_object_data")


class PaebsDebugView(iView):
    dep = "fill_flc25_paebs_lausch@aebs.fill"
    optdep = "fill_ground_truth_raw_tracks@aebs.fill"

    def check(self):
        self.module_all = self.get_modules()
        paebs_object = self.module_all.fill("fill_flc25_paebs_lausch@aebs.fill")[0]
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
        pn.addSignal2Axis(ax, "dx", t, paebs_object.dx, color="b", unit="m", ls="-")

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

        pn.addSignal2Axis(ax, 'CEM Object ID', t, paebs_object.object_index, ls="-", color="g", unit="")

        # Plot 2: Lateral Object Distance
        ax = pn.addAxis(ylabel="y-Distance")
        pn.addSignal2Axis(ax, "dy", t, paebs_object.dy, color="b", unit="m", ls="-")

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
            ax, "vx_rel", t, paebs_object.vx, color="g", unit="m/s", ls="-"
        )
        pn.addSignal2Axis(
            ax, "vx_rel_ref", t, paebs_object.vx_ref, color="m", unit="m/s", ls="-"
        )

        if "vx" in gt_track:
            pn.addSignal2Axis(
                ax, "vx_gt", t, gt_track["vx"], color="r", unit="m/s", ls="-"
            )

        # Plot 4: Lateral Velocity
        ax = pn.addAxis(ylabel="Lat. Velocity")
        pn.addSignal2Axis(
            ax, "vy_rel", t, paebs_object.vy, color="b", unit="m/s", ls="-"
        )

        if "vy_abs" in gt_track:
            pn.addSignal2Axis(
                ax, "vy_abs_gt", t, gt_track["vy_abs"], color="r", unit="m/s", ls="-"
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
            paebs_object.motion_state,
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
            paebs_object.lane,
            unit="",
            color="g",
            ls="-",
        )
        # Plot 6: Object Detection
        # Left Axis
        ylabel_text = "Sensor Source"
        mapping = {
            0: "Unkown",
            1: "Radar only",
            2: "Camera only",
            3: "Fused",
            4: "Not Available",
        }
        ax = pn.addAxis(
            ax,
            ylabel=ylabel_text,
            yticks=mapping,
            ylim=(min(mapping) - 0.5, max(mapping) + 0.5)
        )
        pn.addSignal2Axis(
            ax, ylabel_text, t, paebs_object.obj_src, unit="", color="g", ls="-"
        )

        self.sync.addClient(pn)
        return
