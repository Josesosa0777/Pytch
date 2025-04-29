# -*- dataeval: init -*-

from interface.Interfaces import iFill

init_params = {
  'bar': dict(spam=42),
  'baz': dict(spam=24),
}

class Fill(iFill):
  channels = 'main', 'can1'
  def init(self, spam):
    self.spam = spam
    return

  def check(self):
    signal_groups = [{'egg': ('spam', 'egg')}]
    source = self.get_source('main')
    signal_group = source.selectSignalGroup(signal_groups)
    return signal_group

  def fill(self, signal_group):
    return 42

