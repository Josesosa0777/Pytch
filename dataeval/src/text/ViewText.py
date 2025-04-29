import re
from collections import OrderedDict

from Text import Text
from measparser.iParser import DEVICE_NAME_SEPARATOR

class ViewText(Text):
  channel = 'main'
  PREFIX = 'viewTemp'
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
    self._view_pat = MethodStartPat('view', 'view', 'trash')
    self._group_pat = re.compile('\\s+def\\s+view\(\\s*self\\s*,'
                                                  '\\s*\\w+\\s*,'
                                                  '\\s*(\\w+)')
    self._indent_pat = IndentPat()
    self.group_name = ''

    Text.__init__(self, name, config, control)
    return
  
  def update_metadata(self, line):
    """Scans a line of script text. If it finds a new instance of Plot Navigator, 
    List Navigator, new axis or new signals, it updates the corresponding metadata
    counters
    
    :parameters:
    line : String
      Contains one line of script code as text. 
    """
    self._number_LN += line.count('cListNavigator')
    self._number_PN += line.count('cPlotNavigator')
    self._number_axis += line.count('addAxis(')
    self._value_LN += line.count('.getSignalFromSignalGroup(')
    self._value_PN += line.count('.get_signal_with_unit(')
    return


  def read(self, fp):
    self._sections = OrderedDict([('import', Imports()), ('intermezzo', []),
                                  ('signal_groups', []), ('view', []),
                                  ('tail', [])])

    trash = []
    status = 'trash'

    for line in fp:
      self.update_metadata(line)
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
            status = self._view_pat(line)
            if status == 'view':
              self.group_name = self._group_pat.search(line).group(1)
              line = next(fp)
              self.update_metadata(line)
              indent = self._indent_pat(line)
              view_end_pat = MethodEndPat(indent, 'view', 'trash')
              status = view_end_pat(line)
              if status == 'trash':
                self._sections['view'] = View(indent, trash)
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
        regex = "\".*\].*\""
        match = re.search(regex, line)

        if match is None:
          if ']' in line:
            self._sections['signal_groups'] = SignalGroups(trash, self.control,
                                                           self.channel)
            status = 'trash'
            trash = []
        pass
      elif status == 'view':
        status = view_end_pat(line)
        if status == 'trash':
          self._sections['view'] = View(indent, trash)
          trash = []
        trash.append(line)
    self._sections['tail'] = trash
    fp.seek(0)
    return

  def check(self, fp):
    signal_groups_pat = SignalGroupsStartPat('signal_groups_watch',
                                             'signal_groups',
                                             'signal_groups',
                                             'trash')
    signal_groups_watch_pat = SignalGroupStartPat('signal_groups_watch',
                                                  'signal_groups',
                                                  'signal_groups',
                                                  'trash')
    view_pat = MethodGroupPat('view', 'view', 'trash')

    status = 'trash'
    statuses = set()

    for line in fp:
      if status == 'trash':
        status = signal_groups_pat(line)
        if status == 'signal_groups':
          statuses.add(status)
          status = 'trash'
        elif status == 'trash':
          status = view_pat(line)
          if status == 'view':
            statuses.add(status)
            status = 'trash'
      elif status == 'signal_groups_watch':
        status = signal_groups_watch_pat(line)
        if status == 'signal_groups':
          statuses.add(status)
          status = 'trash'
    fp.seek(0)
    return statuses == {'signal_groups', 'view'}

  def add_signal(self, short_device_name, signal_name):
    signal_groups = self._sections['signal_groups']
    alias = signal_groups.add_signal(short_device_name, signal_name)
    self.update()
    return alias

  def add_lines(self, lines):
    view = self._sections['view']
    view.add_lines(lines)
    self.update()
    return

  def add_modules(self, modules):
    imports = self._sections['import']
    imports.add_modules(modules)
    self.update()
    return

class SignalGroups:
  def __init__(self, lines, control, channel):
    self._name, signal_groups = ''.join(lines).split('=')
    self._signal_groups = eval(signal_groups)

    if len(self._signal_groups) == 1:
      self.index = 0

    else:
      manager = control.getManager()
      source = manager.get_source(channel)
      signal_group, self.index = source.selectSignalGroup(self._signal_groups,
                                                          GetIndex=True)

    signal_group = self._signal_groups[self.index]
    self._aliases = dict([(v, k) for k, v in signal_group.iteritems()])
    return

  def __iter__(self):
    yield self._name
    yield ' = [\n'
    for signal_group in self._signal_groups:
      yield '{\n'
      for alias, (short_device_name, signal_name) in signal_group.iteritems():
        yield '  "%s": ("%s", "%s"),\n' %(alias, short_device_name, signal_name)
      yield '},\n'
    yield ']\n'
    return

  def add_signal(self, short_device_name, signal_name):
    signal = short_device_name, signal_name
    if signal in self._aliases:
      alias = self._aliases[signal]
    else:
      alias = self.create_alias(short_device_name, signal_name)
      self._aliases[signal] = alias
      signal_group = self._signal_groups[self.index]
      signal_group[alias] = signal
    return alias

  def create_alias(self, short_device_name, signal_name):
    aliases = self._aliases.values()
    if signal_name in aliases:
      names = [signal_name]
      for ext in short_device_name.split(DEVICE_NAME_SEPARATOR):
        names.append(ext)
        alias = DEVICE_NAME_SEPARATOR.join(names)
        if alias not in aliases: break
      else:
        ValueError('No valid alias for %s %s' %(short_device_name, signal_name))
    else:
      alias = signal_name
    return alias

class Imports:
  def __init__(self):
    self._imports = set()
    self._lines = []
    return

  def __iter__(self):
    return iter(self._lines)

  def add_line(self, module, line, trash):
    self._imports.add(module)
    self._lines.extend(trash)
    self._lines.append(line)
    return

  def add_modules(self, modules):
    new_modules = modules.difference(self._imports)
    for module in new_modules:
      self._lines.append('import %s' %module)
      self._imports.add(module)
    return

class View:
  def __init__(self, indent, lines):
    self.indent = indent
    self._lines = lines
    return

  def __iter__(self):
    return iter(self._lines)

  def add_lines(self, lines):
    lines = [self.indent + line + '\n' for line in lines]
    self._lines.extend(lines)
    return

class SignalGroupsStartPat:
  start_pat = re.compile('^\\w+\\s*=\\s*\[')
  begin_pat = re.compile('^\\w+\\s*=\\s*\[\\s*\{')
  end_pat = re.compile('^\\w+\\s*=\\s*\[\\s*\{.*\}\\s*,?\\s*\]\\s*$')

  def __init__(self, start_status, begin_status, end_status, trash_status):
    self.start_status = start_status
    self.begin_status = begin_status
    self.end_status = end_status
    self.trash_status = trash_status
    return

  def __call__(self, line):
    match = self.end_pat.search(line)
    if match:
      status = self.end_status
    else:
      match = self.begin_pat.search(line)
      if match:
        status = self.begin_status
      else:
        match = self.start_pat.search(line)
        if match:
          status = self.start_status
        else:
          status = self.trash_status
    return status

class SignalGroupStartPat:
  begin_pat = re.compile('^\\s*\{[^\]]*$')
  end_pat = re.compile('^\\s*\{.*\}\\s*,?\\s*\]\\s*$')
  skip_pat = re.compile('^\\s*$')

  def __init__(self, start_status, begin_status, end_status, trash_status):
    self.start_status = start_status
    self.begin_status = begin_status
    self.end_status = end_status
    self.trash_status = trash_status
    return

  def __call__(self, line):
    match = self.end_pat.search(line)
    if match:
      status = self.end_status
    else:
      match = self.begin_pat.search(line)
      if match:
        status = self.begin_status
      else:
        match = self.skip_pat.search(line)
        if match:
          status = self.start_status
        else:
          status = self.trash_status
    return status

class ImportsPat:
  single_pat = re.compile('^import\\s+(\\w+)')
  from_pat = re.compile('^from\\s+(\\w+)\\s+import\\s+(\\w+)')

  def __call__(self, line):
    match = self.single_pat.search(line)
    if match:
      module = match.group(1)
    else:
      match = self.from_pat.search(line)
      if match:
        module = match.groups()
      else:
        module = None
    return module

class MethodStartPat:
  def __init__(self, method_name, start_status, trash_status):
    self.pat = re.compile('^\\s+def\\s+%s\(' %method_name)
    self.start_status = start_status
    self.trash_status = trash_status
    return

  def __call__(self, line):
    match = self.pat.search(line)
    status = self.start_status if match else self.trash_status
    return status

class MethodEndPat:
  def __init__(self, indent, body_status, end_status):
    self.body_status = body_status
    self.end_status = end_status

    self.indent_len = len(indent)

    self.return_pat = re.compile('^%sreturn' %indent)
    self.empty_pat = re.compile('^\n$')
    self.indent_pat = re.compile(r'^(\s*)')
    return

  def __call__(self, line):
    match = self.return_pat.search(line)
    if match:
      status = self.end_status
    else:
      match = self.empty_pat.search(line)
      if match:
        status = self.body_status
      else:
        indent = self.indent_pat.search(line).group(1)
        if len(indent) < self.indent_len:
          status = self.end_status
        else:
          status = self.body_status
    return status

class IndentPat:
  pat = re.compile(r'^(\s+)\S+')
  def __call__(self, line):
    match = self.pat.search(line)
    indent = match.group(1)
    return indent

class MethodGroupPat:
  def __init__(self, method_name, ok, no):
    self.pat = re.compile('^\\s+def\\s+%s\(self,\\s*\\w+,\\s*\\w+' %method_name)
    self.ok = ok
    self.no = no
    return

  def __call__(self, line):
    status = self.ok if self.pat.search(line) else self.no
    return status

class ViewTextTemplateRunner1(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner1'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner2(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner2'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner3(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner3'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner4(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner4'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner5(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner5'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner6(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner6'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner7(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner7'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner8(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner8'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner9(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner9'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return

class ViewTextTemplateRunner10(ViewText):
  channel = 'main'
  PREFIX = 'viewTemplateRunner10'
  def __init__(self, name, config, control):
    ViewText.__init__(self, name, config, control)
    return