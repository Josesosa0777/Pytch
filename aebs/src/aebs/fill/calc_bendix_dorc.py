# -*- dataeval: init -*-
from interface.Interfaces import iCalc

class Calc(iCalc):
  PRESSED = 1

  group = [
    ('DFM_green_button', ('DBM', 'DFM_green_button')),
    ('DFM_red_button', ('DBM', 'DFM_red_button')),
  ]
  def check(self):
    group = self.get_source().selectSignalGroup([dict(self.group)])
    return group

  def fill(self, group):
    t, green_button = group.get_signal('DFM_green_button')
    red_button = group.get_value('DFM_red_button', ScaleTime=t)
    red_pressed = (red_button == self.PRESSED)
    green_pressed = (green_button == self.PRESSED)
    return t, red_pressed, green_pressed
