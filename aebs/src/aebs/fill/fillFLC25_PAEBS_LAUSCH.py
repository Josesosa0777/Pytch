# -*- dataeval: init -*-
import logging
import numpy as np
from interface import iObjectFill
from measproc.IntervalList import intervalsToMask

logger = logging.getLogger('fillFLC25_PAEBS_DEBUG')

INVALID_ID = 300


class cFill(iObjectFill):
    dep = 'fill_flc25_paebs_lausch'

    def check(self):
        modules = self.get_modules()
        tracks = modules.fill("fill_flc25_paebs_lausch")
        return tracks

    def fill(self, tracks):
        import time
        start = time.time()
        logger.info("FLC25 PAEBS LAUSCH object retrieval is started, Please wait...")
        objects = []
        for id, track in tracks.iteritems():
            o = {}
            # Mandatory Signals
            o["id"] = np.where(track.dx.mask, INVALID_ID, id)
            o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
            o["label"] = np.full(len(o["id"]), "FLC25_PAEBS_LAUSCH", dtype=object)
            track.dx.data[track.dx.mask] = 0
            track.dy.data[track.dy.mask] = 0
            o["dx"] = track.dx.data
            o["dy"] = track.dy.data

            # Definition of Type >> Mapping of Motion State and Object Type
            type_arr = np.full_like(track.motion_state.data, self.get_grouptype('FLC25_PAEBS_LAUSCH_UNDEFINED'))
            type_arr[(track.motion_state.data == 4) & ~track.motion_state.mask] = self.get_grouptype(
                'FLC25_PAEBS_LAUSCH_PED_CROSS')
            type_arr[(track.motion_state.data != 4) & ~track.motion_state.mask] = self.get_grouptype(
                'FLC25_PAEBS_LAUSCH_PED_NOT_CROSS')

            o["type"] = type_arr
            init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
            o["init"] = intervalsToMask(init_intervals, track.dx.size)

            # Optional Signals
            o["collision_prob"] = track.collision_prob.data
            o["casc_dist"] = track.casc_dist.data
            o["mov_state"] = track.motion_state.data
            o["lane"] = track.lane.data
            o["dist_path"] = track.dist_path.data
            o["ttc"] = track.ttc.data
            o["vx_ref"] = track.vx_ref.data
            o["in_path"] = track.in_path.data
            o["vy"] = track.vy.data
            o["vx"] = track.vx.data
            o['obj_src'] = track.obj_src.data

            objects.append(o)

        done = time.time()
        elapsed = done - start
        logger.info("FLC25 PAEBS DEBUG object retrieval is completed in " + str(elapsed) + " seconds")
        return tracks.time, objects


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\Measurement\paebs_debug_pytch\working_files\mi5id787__2022-03-17_12-43-47.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    conti, objects = manager_modules.calc('fillFLC25_PAEBS_LAUSCH@aebs.fill', manager)
    print(objects)
