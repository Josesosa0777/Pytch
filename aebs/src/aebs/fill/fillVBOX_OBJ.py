# -*- dataeval: init -*-

from interface.Interfaces import iObjectFill

class Fill(iObjectFill):
  dep = 'calc_vbox_object',
  #dep = 'calc_vbox_staticpoint-boxberg_2014-03-20',
  
  def fill(self):
    obj = self.modules.fill(self.dep[0])

    obj_ = dict(
      id=0,
      label='VBox Object',
      dx=obj.dx,
      dy=obj.dy,
      type=self.get_grouptype('VBOX_OBJ'),
    )
    return obj.time, [obj_]
