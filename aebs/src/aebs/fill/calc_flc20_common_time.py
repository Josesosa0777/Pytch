# -*- dataeval: init -*-

from interface import iCalc

sgs = [
  {"RefPoint_X": ("Video_Data_General_A", "RefPoint_X"),},  # FLC20
  {"RefPoint_X": ("Host_Vehicle", "Refpoint_X"),},  # old S-Cam
  {"RefPoint_X": ("trajectory_generator_flx20_autobox", "tg_lanes_input_left_c0"),},  # TODO xcp workaround
  {"RefPoint_X": ("ACC1_2A","SpeedOfForwardVehicle"),},
]

class cFill(iCalc):
  def check(self):
    source = self.get_source()
    group = source.selectSignalGroup(sgs)
    return group

  def fill(self, group):
    commonTime = group.get_time('RefPoint_X')
    return commonTime
