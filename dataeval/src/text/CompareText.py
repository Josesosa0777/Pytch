from collections import OrderedDict

from Text import Text
from ViewText import SignalGroupsStartPat, SignalGroupStartPat, SignalGroups

class CompareText(Text):
  PREFIX = 'compareTemp'
  channel = 'compare'

  def __init__(self, filename, config, control):
    self._signal_groups_start_pat = SignalGroupsStartPat('signal_groups_watch',
                                                         'signal_groups_build',
                                                         'signal_groups',
                                                         'head')
    self._signal_group_start_pat = SignalGroupStartPat('signal_groups_watch',
                                                       'signal_groups_build',
                                                       'signal_groups',
                                                       'head')

    Text.__init__(self, filename, config, control)
    return

  def read(self, filename):
    self._sections = OrderedDict([('head', []), ('signal_groups', []),
                                  ('tail', [])])

    status = 'head'
    trash = []

    with open(filename) as fp:
      for line in fp:
        if status == 'head':
          status = self._signal_groups_start_pat(line)
          if status == 'signal_groups' and not self._sections['signal_groups']:
            self._sections['signal_groups'] = SignalGroups([line], self.control,
                                                           self.channel)
            status = 'tail'
          elif status not in ('signal_groups', 'head'):
            trash.append(line)
          else:
            self._sections[status].append(line)
        elif status == 'signal_groups_watch':
          status = self._signal_group_start_pat(line)
          trash.append(line)
          if status == 'signal_groups':
            self._sections['signal_groups'] = SignalGroups(trash, self.control,
                                                           self.channel)
            trash = []
          elif status == 'head':
            self._sections[status].extend(trash)
            trash = []
        elif status == 'signal_groups_build':
          trash.append(line)
          if ']' in line:
            self._sections['signal_groups'] = SignalGroups(trash, self.control,
                                                           self.channel)
            trash = []
            status = 'tail'
        elif status == 'tail':
          self._sections[status].append(line)
    return

  def check(self, filename):
    signal_groups_pat = SignalGroupsStartPat('signal_groups_watch',
                                             'signal_groups',
                                             'signal_groups',
                                             'trash')
    signal_groups_watch_pat = SignalGroupStartPat('signal_groups_watch',
                                                  'signal_groups',
                                                  'signal_groups',
                                                  'trash')

    status = 'trash'
    statuses = set()

    with open(filename) as fp:
      for line in fp:
        if status == 'trash':
          status = signal_groups_pat(line)
          if status == 'signal_groups':
            statuses.add(status)
            status = 'trash'
        elif status == 'signal_groups_watch':
          status = signal_groups_watch_pat(line)
          if status == 'signal_groups':
            statuses.add(status)
            status = 'trash'
    return statuses == {'signal_groups'}

  def add_signal(self, short_device_name, signal_name):
    signal_groups = self._sections['signal_groups']
    alias = signal_groups.add_signal(short_device_name, signal_name)
    self.update()
    return alias

