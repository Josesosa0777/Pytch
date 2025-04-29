from bases import Primitive

class EgoMotion(Primitive):
  def __init__(self, time, vx, yaw_rate, ax):
    Primitive.__init__(self, time)
    self.vx = vx
    self.yaw_rate = yaw_rate
    self.ax = ax
    return
class EgoMotionResim(Primitive):
  def __init__(self, time, vx, yaw_rate, ax,accped_pos,brkped_pos,steer_angle,dir_ind):
    Primitive.__init__(self, time)
    self.vx = vx
    self.yaw_rate = yaw_rate
    self.ax = ax
    self.accped_pos =accped_pos
    self.brkped_pos= brkped_pos
    self.steer_angle = steer_angle
    self.dir_ind = dir_ind
    return
