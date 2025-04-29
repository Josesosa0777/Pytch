# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from numpy.core.fromnumeric import size

signals = [
    {"acc_xbr": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_AccOutput_control_output_acc_brake_acceleration_demand")},
    {"acc_xbr": ("XBR_d0B_s2A","ExtlAccelerationDemand")}
]
class cFill(iCalc):
        dep = ('fill_flc25_cem_tpf_tracks', 'calc_common_time-flc25')
        def check(self):
            modules = self.get_modules()
            source = self.get_source()
            common_time = modules.fill('calc_common_time-flc25')
            signal_group = source.selectSignalGroup(signals)
            tracks = modules.fill("fill_flc25_cem_tpf_tracks")[0]
            return tracks, signal_group, common_time

        def fill(self, tracks, signal_group, common_time):
            events = []
            _, xbr_signal, _ = signal_group.get_signal_with_unit('acc_xbr', ScaleTime=common_time)
            xbr_signal_mask = xbr_signal < 0

            # vx_tar_rel > 0 AND (lane.right -> lane.same OR lane.left -> lane.same)
            for _, track in tracks.iteritems():
                objects = {}
                # target relative speed > 0
                velocity_mask = track.vx > 0
                # lane change
                # 0 same, 1 left, 2 right
                # 1 -> 0
                # insert initial state

                # left to same lane
                lane_change_from_left_mask = (track._eAssociatedLane[1:] - track._eAssociatedLane[:-1]) == -1
                lane_change_from_left_mask = np.insert(lane_change_from_left_mask, 0, False)
                # right to same lane
                lane_change_from_right_mask = (track._eAssociatedLane[1:] - track._eAssociatedLane[:-1]) == -2
                lane_change_from_right_mask = np.insert(lane_change_from_right_mask, 0, False)

                actual_lane_mask = track._eAssociatedLane == 0
                lane_change_left = lane_change_from_left_mask & actual_lane_mask
                lane_change_right = lane_change_from_right_mask & actual_lane_mask

                dx_mask = track.dx > 5

                lane_mask = (lane_change_left | lane_change_right)

                event_mask = velocity_mask & xbr_signal_mask & dx_mask

                objects['event_mask'] = event_mask
                objects['vx'] = track.vx
                objects['dx'] = track.dx
                objects['time'] = track.time
                objects['acc_xbr'] = xbr_signal

                events.append(objects)
                
            return common_time, events


if __name__ == '__main__':
        from config.Config import init_dataeval
        meas_path = r"c:\KBData\PYTCH_SAMPLE_MEAS\mi5id787__2021-10-26_16-44-26.h5"
        config, manager, manager_modules = init_dataeval(['-m', meas_path])
        tracks = manager_modules.calc('calc_high_speed_cut_in@aebs.fill', manager)
        print(tracks)