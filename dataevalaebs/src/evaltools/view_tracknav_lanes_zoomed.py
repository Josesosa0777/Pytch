# -*- dataeval: init -*-

import view_tracknav_lanes

__doc__ = view_tracknav_lanes.__doc__

init_params = view_tracknav_lanes.init_params

class View(view_tracknav_lanes.View):
  TRACKNAV_PARAMS = dict(
    LengthMin=-20.0, LengthMax=20.0,
    WidthMin=-20.0, WidthMax=20.0,
  )
