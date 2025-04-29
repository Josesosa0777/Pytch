import re
import copy
from collections import OrderedDict

from Text import Text
from ViewText import ImportsPat, SignalGroupsStartPat, SignalGroupStartPat, \
                     MethodStartPat, View, Imports, IndentPat, SignalGroups, \
                     MethodEndPat, MethodGroupPat

class SearchText(Text):
  channel = 'main'
  PREFIX = 'searchTemp'
  def __init__(self, name, config, control):
    self._imports_pat = ImportsPat()
    self._signal_groups_start_pat = SignalGroupsStartPat('signal_groups_watch',
                                                         'signal_groups_build',
                                                         'signal_groups',
                                                         'trash')
    self._signal_group_start_pat = SignalGroupStartPat('signal_groups_watch',
                                                       'signal_groups_build',
                                                       'signal_groups',
                                                       'trash')
    self._search_pat = MethodStartPat('search', 'search', 'trash')
    self._group_pat = re.compile('\\s+def\\s+search\(\\s*self\\s*,\\s*(\\w+)')
    self._indent_pat = IndentPat()
    self.group_name = ''

    Text.__init__(self, name, config, control)
    return

  def read(self, fp):
    self._sections = OrderedDict([('import', Imports()), ('intermezzo', []),
                                  ('signal_groups', []), ('search', []),
                                  ('tail', [])])

    trash = []
    status = 'trash'

    for line in fp:
      if status == 'trash':
        module = self._imports_pat(line)
        if module:
          self._sections['import'].add_line(module, line, trash)
          status = 'import'
          trash = []
        else:
          status = self._signal_groups_start_pat(line)
          if status != 'trash' and not self._sections['signal_groups']:
            self._sections['intermezzo'] = trash
            trash = []
            if status == 'signal_groups':
              self._sections[status] = SignalGroups([line], self.control,
                                                    self.channel)
              status = 'trash'
            else:
              trash.append(line)
          else:
            trash.append(line)
            status = self._search_pat(line)
            if status == 'search':
              self.group_name = self._group_pat.search(line).group(1)
              line = next(fp)
              indent = self._indent_pat(line)
              search_end_pat = MethodEndPat(indent, 'search', 'trash')
              status = search_end_pat(line)
              if status == 'trash':
                self._sections['search'] = Search(indent, trash)
                trash = []
              trash.append(line)
      elif status == 'import':
        module = self._imports_pat(line)
        if module:
          self._sections['import'].add_line(module, line, trash)
          trash = []
        else:
          status = 'trash'
          trash.append(line)
      elif status == 'signal_groups_watch':
        trash.append(line)
        status = self._signal_group_start_pat(line)
        if status == 'signal_groups':
          self._sections[status] = SignalGroups(trash, self.control,
                                                self.channel)
          trash = []
      elif status == 'signal_groups_build':
        trash.append(line)
        if ']' in line:
          self._sections['signal_groups'] = SignalGroups(trash, self.control,
                                                         self.channel)
          status = 'trash'
          trash = []
        pass
      elif status == 'search':
        status = search_end_pat(line)
        if status == 'trash':
          self._sections['search'] = Search(indent, trash)
          trash = []
        trash.append(line)
    self._sections['tail'] = trash
    return

  def add_report(self, lines, removable_subs):
    search = self._sections['search']
    temp_lines = copy.copy(search.get_lines())
    for line in temp_lines:
      for sub in removable_subs:
        if sub in line:
          search.remove(line)
    self.add_lines(lines)
    return

  def add_lines(self, lines):
    search = self._sections['search']
    search.add_lines(lines)
    self.update()
    return

  def add_signal(self, short_device_name, signal_name):
    signal_groups = self._sections['signal_groups']
    alias = signal_groups.add_signal(short_device_name, signal_name)
    self.update()
    return alias

  def check(self, fp):
    signal_groups_pat = SignalGroupsStartPat('signal_groups_watch',
                                             'signal_groups',
                                             'signal_groups',
                                             'trash')
    signal_groups_watch_pat = SignalGroupStartPat('signal_groups_watch',
                                                  'signal_groups',
                                                  'signal_groups',
                                                  'trash')
    search_pat = SearchMethodGroupPat('search', 'search', 'trash')

    status = 'trash'
    statuses = set()

    for line in fp:
      if status == 'trash':
        status = signal_groups_pat(line)
        if status == 'signal_groups':
          statuses.add(status)
          status = 'trash'
        elif status == 'trash':
          status = search_pat(line)
          if status == 'search':
            statuses.add(status)
            status = 'trash'
      elif status == 'signal_groups_watch':
        status = signal_groups_watch_pat(line)
        if status == 'signal_groups':
          statuses.add(status)
          status = 'trash'
    return statuses == {'signal_groups', 'search'}

class Search(View):
  def remove(self, removable):
    self._lines.remove(removable)
    return

  def get_lines(self):
    return self._lines

class SearchMethodGroupPat(MethodGroupPat):
  def __init__(self, method_name, ok, no):
    MethodGroupPat.__init__(self, method_name, ok, no)
    self.pat = re.compile('^\\s+def\\s+%s\(self,\\s*\\w+' %method_name)
    return
