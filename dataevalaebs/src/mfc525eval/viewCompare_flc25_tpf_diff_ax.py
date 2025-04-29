# -*- dataeval: init -*-

import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict(('TRACK_%03d' % i, dict(id=i)) for i in xrange(0, 100))


class cMyView(iView):
		dep = 'fill_flc25_cem_tpf_tracks@aebs.fill',

		def init(self, id):
				self.id = id
				return

		def check(self):
				modules = self.get_modules()
				flc25_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")
				assert self.id in flc25_tracks, 'Track %d is not recorded' % self.id

				flc25_tracks = flc25_tracks[self.id]

				return flc25_tracks

		def view(self, flc25_tracks):
				t = flc25_tracks.time
				pn = datavis.cPlotNavigator(title='Actual fArelX Vs differentiated accel.: track #%d' % self.id)

				actual_ax = flc25_tracks.ax
				actual_vx = flc25_tracks.vx

				diff_ax = np.gradient(actual_vx, np.gradient(t))
				# ax
				ax = pn.addAxis(ylabel='ax')
				pn.addSignal2Axis(ax, 'actual long. accel.', t, actual_ax, unit='m/s^2',color="green")
				pn.addSignal2Axis(ax, 'differentiated long. accel.', t, diff_ax, unit='m/s^2', color="blue")

				# register client
				sync = self.get_sync()
				sync.addClient(pn)
				return


if __name__ == '__main__':
		from config.Config import init_dataeval

		meas_path = r"C:\KBData\__PythonToolchain\Meas\TSR\HMC-QZ-STR__2021-02-15_16-51-57.h5"
		config, manager, manager_modules = init_dataeval(['-m', meas_path])
		manager.build(['viewCompare_flc25_tpf_diff_ax@mfc525eval'], show_navigators=True)