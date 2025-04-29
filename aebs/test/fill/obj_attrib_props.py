from collections import namedtuple

import numpy as np

AttribProps = namedtuple('AttribProps', ('dtype', 'min', 'max'))

bool_default = AttribProps(np.bool, None, None)
uint_default = AttribProps(np.unsignedinteger, None, None)
float_default = AttribProps(np.float, None, None)
float_min_0 = AttribProps(np.float, 0., None)
float_min_0_max_1 = AttribProps(np.float, 0., 1.)

attrib_props = dict(
  time           = float_default,
  id             = uint_default,
  refl_id        = uint_default,
  radar_id       = uint_default,
  video_id       = uint_default,
  dx             = float_default,
  dy             = float_default,
  vx             = float_default,
  vy             = float_default,
  ax             = float_default,
  ay             = float_default,
  range          = float_default,
  range_rate     = float_default,
  angle          = float_default,
  angle_left     = float_default,
  angle_right    = float_default,
  power          = float_min_0,
  conf           = float_min_0_max_1,
  radar_conf     = float_min_0_max_1,
  video_conf     = float_min_0_max_1,
  fused          = bool_default,
  aeb_track      = bool_default,
  acc_track      = bool_default,
  mov_state      = dict(
    stat         = bool_default,
    stopped      = bool_default,
    moving       = bool_default,
    unknown      = bool_default,
  ),
  mov_dir        = dict(
    oncoming     = bool_default,
    ongoing      = bool_default,
    undefined    = bool_default,
  ),
  tr_state       = dict(
    valid        = bool_default,
    measured     = bool_default,
    hist         = bool_default,
  ),
  obj_type       = dict(
    car          = bool_default,
    truck        = bool_default,
    motorcycle   = bool_default,
    unknown      = bool_default,
  ),
  brake_light    = dict(
    on           = bool_default,
    off          = bool_default,
    unknown      = bool_default,
  ),
  blinker        = dict(
    off          = bool_default,
    left         = bool_default,
    right        = bool_default,
    both         = bool_default,
    unknown      = bool_default,
  ),
  lane           = dict(
    same         = bool_default,
    left         = bool_default,
    right        = bool_default,
    uncorr_left  = bool_default,
    uncorr_right = bool_default,
    unknown      = bool_default,
  ),
)
