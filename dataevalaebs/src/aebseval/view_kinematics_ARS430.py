# -*- dataeval: init -*-

"""
Plot AEBS-relevant kinematic information

Plot basic attributes of ego vehicle and primary track, including speed,
distance etc.
"""

from numpy import rad2deg

import datavis
from interface import iView
from measparser.signalproc import rescale

DETAIL_LEVEL = 0

mps2kph = lambda v: v * 3.6


class View(iView):
    dep = 'calc_conti_ars430_aebs@aebs.fill', 'fill_flr20_aeb_track@aebs.fill', 'calc_flr20_egomotion@aebs.fill'

    def view(self):
        # process signals
        ARS430track = self.modules.fill(self.dep[0])
        FLR20track = self.modules.fill(self.dep[1])
        ARS430time = ARS430track.time
        FLR20time = FLR20track.time
        ego = self.modules.fill(self.dep[2])

        # create plot
        pn = datavis.cPlotNavigator(title='Ego vehicle and obstacle kinematics')

        # speed----------------------------------------------------------------------------------
        ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 105.0))

        # egospeed is from the FLR20 use that time
        ego_vx = rescale(ego.time, ego.vx, FLR20time)[1]
        pn.addSignal2Axis(ax, 'ego speed', FLR20time, ego_vx, unit='km/h')
        # FLR20 target speed
        track_vx_abs =  ego_vx + FLR20track.vx  # v_ego + v_track
        pn.addSignal2Axis(ax, 'AC100 speed', FLR20time, mps2kph(track_vx_abs), unit='km/h')
        # ARS430 target speed
        track_vx = rescale(ARS430time, ARS430track.vx, FLR20time)[1] + mps2kph(ego_vx) # v_ego + v_track
        pn.addSignal2Axis(ax, 'ARS430 speed', FLR20time, track_vx, unit='km/h')

        # acceleration---------------------------------------------------------------------------
        ax = pn.addAxis(ylabel='acceleration', ylim=(-5.0, 5.0))
        # ego acceleration
        pn.addSignal2Axis(ax, 'ego acceleration', FLR20time, ego.ax, unit='m/s^2')
        # AC100 acceleration
        pn.addSignal2Axis(ax, 'AC100 obj. accel.', FLR20time, FLR20track.ax_abs, unit='m/s^2')
        # ARS430 acceleration
        track_ax = rescale(ARS430time, ARS430track.ax, FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 obj. accel.', FLR20time, track_ax+ego.ax, unit='m/s^2')

        # yaw rate-------------------------------------------------------------------------------
        if DETAIL_LEVEL > 0:
            ax = pn.addAxis(ylabel="yaw rate", ylim=(-12.0, 12.0))
            pn.addSignal2Axis(ax, "yaw rate", FLR20time, rad2deg(ego.yaw_rate), unit="deg/s")

        # dx-------------------------------------------------------------------------------------
        ax = pn.addAxis(ylabel='long. dist.', ylim=(0.0, 80.0))
        # AC100 object dx
        pn.addSignal2Axis(ax, 'AC100 dx', FLR20time, FLR20track.dx, unit='m')
        # ARS430 object dx
        track_dx = rescale(ARS430time, ARS430track.dx, FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 dx', FLR20time, track_dx, unit='m', color='k')
        # dy-------------------------------------------------------------------------------------
        ax = pn.addTwinAxis(ax, ylabel='lat. dist.', ylim=(-15.0, 15.0), color='g')
        # AC100 object dy
        pn.addSignal2Axis(ax, 'AC100 dy', FLR20time, FLR20track.dy, unit='m', color='g')
        # ARS430 object dy
        track_dy = rescale(ARS430time, ARS430track.dy, FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 dy', FLR20time, track_dy, unit='m', color='r')

        # mov_state------------------------------------------------------------------------------
        mapping = FLR20track.mov_state.mapping
        ax = pn.addAxis(ylabel='moving state', yticks=mapping,
                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        # AC100 object mov state
        pn.addSignal2Axis(ax, 'AC100 obst. mov_st', FLR20time, FLR20track.mov_state.join(), color='b')
        # ARS430 object mov state
        track_ms = rescale(ARS430time, ARS430track.mov_state.join(), FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 obst. mov_st', FLR20time, track_ms, color='g')

        # collision relevancy--------------------------------------------------------------------
        ax = pn.addAxis(ylabel='coll. relev.', ylim=(0, 15))
        # ARS430 object collision relevancy
        track_dx = rescale(ARS430time, ARS430track.coll_relev, FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 coll. relev.', FLR20time, track_dx)

        # classification-------------------------------------------------------------------------
        mapping = ARS430track.obj_type.mapping
        ax = pn.addAxis(ylabel='object class', yticks=mapping,
                        ylim=(min(mapping) - 0.5, max(mapping) + 0.5))
        # ARS430 object class
        track_dx = rescale(ARS430time, ARS430track.obj_type.join(), FLR20time)[1]
        pn.addSignal2Axis(ax, 'ARS430 obj. class', FLR20time, track_dx, color='g')

        # register client
        self.sync.addClient(pn)
        return