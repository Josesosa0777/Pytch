# -*- dataeval: init -*-

import datavis
from interface import iParameter, iView


class cParameter(iParameter):
		def __init__(self, id):
				self.id = id
				self.genKeys()


# instantiation of module parameters
init_params = dict(('TRACK_%02d' % i, dict(id=i)) for i in xrange(40))


class cMyView(iView):
		dep = 'fill_flr25_aeb_track@aebs.fill', 'calc_radar_egomotion-flr25@aebs.fill'

		def init(self, id):
				self.id = id
				return

		def check(self):
				modules = self.get_modules()
				tracks = modules.fill(self.dep[0])
				# assert self.id in tracks, 'Track %d is not recorded' %self.id
				ego = modules.fill(self.dep[1])
				track = tracks[self.id]
				return track, ego

		def view(self, track, ego):
				t = track.time
				pn = datavis.cPlotNavigator(title='FLR25 track #%d' % self.id)
				# flags
				yticks = dict((k, v) for k, v in zip(xrange(6), [0, 1] * 3))
				ax = pn.addAxis(ylabel='flags', yticks=yticks)
				pn.addSignal2Axis(ax, 'fused', t, track.fused, offset=4, displayscaled=False)
				pn.addSignal2Axis(ax, 'measured', t, track.tr_state.measured, offset=2, displayscaled=False)
				pn.addSignal2Axis(ax, 'aeb', t, track.aeb_track)
				# dx
				ax = pn.addAxis()
				pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
				ax = pn.addAxis()
				pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m')
				pn.addSignal2Axis(ax, 'dy corr', t, track.dy_corr, unit='m')
				ax = pn.addAxis()
				pn.addSignal2Axis(ax, 'yaw rate', t, ego.yaw_rate, unit='rad/s')
				# vx
				ax = pn.addAxis()
				# pn.addSignal2Axis(ax, 'vx', t, track.vx, unit='m/s')
				pn.addSignal2Axis(ax, 'ego speed', t, ego.vx, unit='m/s')
				# # conf
				# ax = pn.addAxis()
				# pn.addSignal2Axis(ax, 'credib', t, track.credib)
				# pn.addSignal2Axis(ax, 'radar_conf', t, track.radar_conf)
				# moving state
				ax = pn.addAxis(ylabel='mov_st', yticks=track.mov_state.mapping)
				pn.addSignal2Axis(ax, 'mov_st', t, track.mov_state.join())
				# register client
				sync = self.get_sync()
				sync.addClient(pn)
				return
