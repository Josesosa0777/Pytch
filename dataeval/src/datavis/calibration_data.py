class cCalibrationData:
  def __init__(self, camerax, cameray, cameraz, caliwidth, caliheight, fov, looktox, looktoy, upx):
    self.camerax    = camerax
    self.cameray    = cameray
    self.cameraz    = cameraz
    self.caliwidth  = caliwidth
    self.caliheight = caliheight
    self.fov        = fov
    self.looktox    = looktox
    self.looktoy    = looktoy
    self.upx        = upx
    return

  def get_values(self):
    attr_names = self.get_value_names()
    return tuple(getattr(self, a_n) for a_n in attr_names)

  @classmethod
  def get_value_names(cls):
    return cls.__dict__['__init__'].func_code.co_varnames[1:]