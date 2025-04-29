# -*- dataeval: init -*-

from interface import iView
import datavis

init_params = {
  'AEB' : {'func_name':'AEB', 'dep_name':'fill_flr20_aeb_track@aebs.fill'},
  'ACC' : {'func_name':'ACC', 'dep_name':'fill_flr20_acc_track@aebs.fill'},
  'UMO' : {'func_name':'UMO', 'dep_name':'fill_flr20_aeb_track@aebs.fill'},
}

MPS_2_KPH = 3.6

class MyView(iView):
  dep = 'fill_flr20_aeb_track@aebs.fill', 'fill_flr20_acc_track@aebs.fill'

  def init(self, func_name, dep_name):
    self.func_name = func_name
    self.dep_name = dep_name
    return

  def check(self):
    modules = self.get_modules()
    track = modules.fill(self.dep_name)
    group = self.get_source().selectSignalGroup([{
      "ego_speed": ("General_radar_status", "actual_vehicle_speed"),
    }])
    return track, group

  def view(self, track, group):
    pn = datavis.cPlotNavigator(title='FLR20 %s track' %self.func_name, fontSize='medium')
    t = track.time
    ego_speed = group.get_value('ego_speed', ScaleTime=t) * MPS_2_KPH
    track_speed = track.vx * MPS_2_KPH
    # speed
    ax = pn.addAxis(ylabel='speed', ylim=(-5.0, 95.0))
    pn.addSignal2Axis(ax, 'ego speed', t, ego_speed, unit='kph')
    pn.addSignal2Axis(ax, 'target speed', t, ego_speed+track_speed, unit='kph')
    # dx
    ax = pn.addAxis(ylabel='rel. long distance', ylim=(0.0, 80.0))
    pn.addSignal2Axis(ax, 'dx', t, track.dx, unit='m')
    ax = pn.addTwinAxis(ax, ylabel='rel. lat distance', ylim=(-15.0, 15.0), color='g')
    pn.addSignal2Axis(ax, 'dy', t, track.dy, unit='m', color='g')
    # mov_state
    mapping = track.mov_state.mapping
    ax = pn.addAxis(ylabel='moving state', yticks=mapping,
                    ylim=(min(mapping)-0.5, max(mapping)+0.5))
    pn.addSignal2Axis(ax, 'mov_st', t, track.mov_state.join())
    # confidence
#    ax = pn.addAxis(ylabel='confidence', yticks={0:0, 1:1, 2:'no', 3:'yes'},
#                    ylim=(-0.1, 3.1))
#    pn.addSignal2Axis(ax, 'radar conf', t, track.radar_conf)
#    pn.addSignal2Axis(ax, 'video conf', t, track.video_conf)
#    pn.addSignal2Axis(ax, 'video associated', t, track.fused, offset=2,
#                      displayscaled=True)
    # register client
    sync = self.get_sync()
    sync.addClient(pn)
    return
