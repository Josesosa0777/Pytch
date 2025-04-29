# -*- dataeval: init -*-
"""
:Short Description:
		`More Information about ADMA, CEM_TPF, Usage and Output <../html/dataevalaebs.html#module-dataevalaebs.view_paebs_kpi_for_gt_raw_with_flc25_cem_tpf_tracks>`__

.. note::
	For source code click on [source] tag beside functions
"""
import numpy as np

from interface import iParameter, iView
import datavis

# instantiation of module parameters
init_params = dict(('TRACK_%03d' % i, dict(id=i)) for i in xrange(0, 100))


class cMyView(iView):
		dep = 'fill_flc25_cem_tpf_tracks@aebs.fill', 'fill_ground_truth_raw_tracks@aebs.fill'

		def init(self, id):
				self.id = id
				return

		def check(self):
				modules = self.get_modules()
				flc25_tracks, _ = modules.fill("fill_flc25_cem_tpf_tracks@aebs.fill")
				gt_track = modules.fill("fill_ground_truth_raw_tracks@aebs.fill")
				flc25_tracks = flc25_tracks.rescale(gt_track["time"])
				assert self.id in flc25_tracks, 'Track %d is not recorded' % self.id
				flc25_tracks = flc25_tracks[self.id]

				return flc25_tracks, gt_track

		def view(self, flc25_tracks, gt_track):
				t = flc25_tracks.time
				pn = datavis.cPlotNavigator(title='FLC25 internal track #%d' % self.id)

				# dx
				ax = pn.addAxis(ylabel='dx')
				dx_std_p = flc25_tracks.dx + flc25_tracks.dx_std
				dx_std_n = flc25_tracks.dx - flc25_tracks.dx_std
				pn.addSignal2Axis(ax, 'dx+std', t, dx_std_p,unit='m', ls="--" ,color="green")
				pn.addSignal2Axis(ax, 'dx-std', t, dx_std_n, unit='m', ls="--",color="green")
				pn.addSignal2Axis(ax, 'dx', t, flc25_tracks.dx, unit='m',color="green")
				pn.addSignal2Axis(ax, 'gt_dx', t, gt_track['dx'], unit='m')
				ax.fill_between(t, dx_std_p, dx_std_n, color="green", alpha="0.3")

				# dy
				ax = pn.addAxis(ylabel='dy')
				dy_std_p = flc25_tracks.dy + flc25_tracks.dy_std
				dy_std_n = flc25_tracks.dy - flc25_tracks.dy_std
				pn.addSignal2Axis(ax, 'dy+std', t, dy_std_p, unit='m', ls="--",color="green")
				pn.addSignal2Axis(ax, 'dy-std', t,dy_std_n , unit='m', ls="--",color="green")
				pn.addSignal2Axis(ax, 'dy', t, flc25_tracks.dy, unit='m',color="green")
				pn.addSignal2Axis(ax, 'gt_dy', t, gt_track['dy'], unit='m')
				ax.fill_between(t, dy_std_p, dy_std_n, color="green", alpha="0.3")

				# vx
				ax = pn.addAxis(ylabel='vx')
				vx_abs_std_p = flc25_tracks.vx_abs + flc25_tracks.vx_abs_std
				vx_abs_std_n = flc25_tracks.vx_abs - flc25_tracks.vx_abs_std
				pn.addSignal2Axis(ax, 'vx_abs+std', t,vx_abs_std_p , unit='m/s', ls="--",color="green")
				pn.addSignal2Axis(ax, 'vx_abs-std', t,vx_abs_std_n , unit='m/s', ls="--",color="green")
				pn.addSignal2Axis(ax, 'vx_abs', t, flc25_tracks.vx_abs, unit='m/s',color="green")
				pn.addSignal2Axis(ax, 'gt_vx_abs', t, gt_track['vx_abs'], unit='m/s')
				ax.fill_between(t, vx_abs_std_p, vx_abs_std_n, color="green", alpha="0.3")

				# vy
				ax = pn.addAxis(ylabel='vy')
				vy_abs_std_p =  flc25_tracks.vy_abs + flc25_tracks.vy_abs_std
				vy_abs_std_n = flc25_tracks.vy_abs - flc25_tracks.vy_abs_std
				pn.addSignal2Axis(ax, 'vy_abs+std', t, vy_abs_std_p,unit='m/s', ls="--" ,color="green")
				pn.addSignal2Axis(ax, 'vy_abs-std', t,vy_abs_std_n, unit='m/s', ls="--",color="green")
				pn.addSignal2Axis(ax, 'vy_abs', t, flc25_tracks.vy_abs, unit='m/s',color="green")
				pn.addSignal2Axis(ax, 'gt_vy_abs', t, gt_track['vy_abs'], unit='m/s')
				ax.fill_between(t,vy_abs_std_p,vy_abs_std_n,color="green",alpha="0.3")


				# register client
				sync = self.get_sync()
				sync.addClient(pn)
				return
