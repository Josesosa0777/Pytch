# -*- dataeval: init -*-

from evaltools import view_tracknav_lanes

__doc__ = view_tracknav_lanes.__doc__

init_params = view_tracknav_lanes.init_params

class View(view_tracknav_lanes.View):
  TRACKNAV_PARAMS = dict(
    LengthMin=-15.0, LengthMax=15.0,
    WidthMin=-15.0, WidthMax=3.0,
    EgoXOffset=-1.25, EgoYOffset=0.0,
  )
