# -*- dataeval: init -*-

import numpy as np

from interface import iParameter, iView
import datavis


class cParameter(iParameter):
	def __init__(self, id):
		self.id = id
		self.genKeys()


# instantiation of module parameters
init_params = dict(('TRACK_%02d' % i, dict(id = i)) for i in xrange(40))


class cMyView(iView):
	dep = 'fill_flr20_raw_tracks@aebs.fill'

	def init(self, id):
		self.id = id
		return

	def check(self):
		modules = self.get_modules()
		tracks, aeb_object = modules.fill("fill_flr20_raw_tracks@aebs.fill")
		assert self.id in [track["track"] for track in tracks], 'Track %d is not recorded' % self.id
		track = tracks[self.id]
		return track, aeb_object

	def view(self, track, aeb_object):
		t = track["time"]
		pn = datavis.cPlotNavigator(title = 'Filtered raw track #%d' % self.id)

		ax = pn.addAxis()
		pn.addSignal2Axis(ax, 'dx', t, track["dx"], unit = 'm')
		pn.addSignal2Axis(ax, 'dx_hyp', t, track["dx_hyp"], unit = 'm')
		pn.addSignal2Axis(ax, 'dx_aeb', t, aeb_object["dx"], unit = 'm')
		ax = pn.addAxis()
		pn.addSignal2Axis(ax, 'dy', t, track["dy"], unit = 'm')
		pn.addSignal2Axis(ax, 'dy_hyp', t, track["dy_hyp"], unit = 'm')
		pn.addSignal2Axis(ax, 'dy_aeb', t, aeb_object["dy"], unit = 'm')
		ax = pn.addAxis()

		pn.addSignal2Axis(ax, 'ttc', t, track["ttc"], unit = 'sec')

		# register client
		sync = self.get_sync()
		sync.addClient(pn)
		return
