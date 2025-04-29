import re
from collections import OrderedDict

from Text import Text
from ViewText import MethodStartPat, MethodEndPat, IndentPat

class AnalyzeText(Text):
  PREFIX = 'analyzeTemp'
  def __init__(self, name, config, control):
    self._analyze_pat = MethodStartPat('analyze', 'analyze', 'head')
    self._indent_pat = IndentPat()
    self.indent = ''

    Text.__init__(self, name, config, control)
    return

  def read(self, fp):
    self._sections = OrderedDict([('head', []), ('analyze', []), ('tail', [])])

    status = 'head'

    for line in fp:
      if status == 'head':
        status = self._analyze_pat(line)
        if status == 'analyze':
          self._sections[status].append(line)
          line = fp.next()
          self.indent = self._indent_pat(line)
          analyze_end_pat = MethodEndPat(self.indent, 'analyze', 'tail')
          status = analyze_end_pat(line)
      elif status == 'analyze':
        status = analyze_end_pat(line)
      self._sections[status].append(line)
    return

  def check(self, fp):
    pat = re.compile('\\s+def\\s+analyze\(self')
    status = True
    for line in fp:
      if pat.search(line): break
    else:
      status = False
    return status

  def add_lines(self, lines):
    lines = [self.indent + line + '\n' for line in lines]
    analyze = self._sections['analyze']
    analyze.extend(lines)
    self.update()
    return

