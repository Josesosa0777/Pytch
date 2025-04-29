#!C:\Python27\python.exe
"""
Replace the getSignal calls in an interface with getSignalFromSignalGroup.

python group_signals.py viewFoo.py [viewSpam.py]

If no output file name (viewSpam.py) is added, then the input file (viewFoo.py) 
will be overwritten.
"""

import sys
import re

if '-h' in sys.argv:
  print __doc__
  exit()
  
try:
  old = sys.argv[1]
except IndexError:
  print __doc__
  exit()
try:
  new = sys.argv[2]
except IndexError:
  new = old

signal_group = {}  

s = open(old).read()
r = re.sub('#.*\n', '\n', s)

GetSignalPattern = re.compile('interface\.Source\.getSignal\(\\s*[\'"]([\\w\(\)_]+)[\'"]\\s*,\\s*[\'"]([\\w\.%]+)[\'"]\\s*(%\\w+)?')

def createAlias(device_name, signal_name):
  if '(' in device_name:
    device_name = device_name.split('(')[0]
  else:
    device_name = '_'.join(device_name.split('_')[:-2])
  if signal_name in signal_group and  device_name != signal_group[signal_name][0]:
    alias = signal_name, device_name
    alias = '.'.join(alias)
  else:
    alias = signal_name
  if '%' not in alias:
    signal_group[alias] = device_name, signal_name
  return alias

for match in re.finditer('(for\\s+\\w+\\s+in\\s+[\\w \t,\(\)]+[ \t]*:[ \t]*\n)(\\s+)', r):
  forhead   = match.group(1)
  forsearch = forhead.replace('(', '\\(').replace(')', '\\)')
  indent    = match.group(2)  
  match     = re.search('%s((%s.*\n)+)' %(forsearch, indent), r)  
  body = [forhead]
  for match in GetSignalPattern.findall(match.group(1)):
    body.append('  createAlias("%s", "%s" %s)' %match)
  exec '\n'.join(body)

for match in GetSignalPattern.finditer(r):
  device_name, signal_name, index_name = match.groups()
  if isinstance(index_name, str):
    index_match = re.search('%s\\s*=\\s*(\\d+)' %index_name.strip('%'), r)
    if index_match:
      index = int(index_match.group(1))
      signal_name = signal_name %index
  alias = createAlias(device_name, signal_name)  
  if index_name is None:
    index_name = ''    
  s = s.replace(match.group(0), 'interface.Source.getSignalFromSignalGroup(Group, "%s"%s' %(alias, index_name))
  
signal_group_head = 'SignalGroups = [{'
signal_group_str = []
signal_group_sep = '\n' + ' ' * len(signal_group_head)

for alias in sorted(signal_group):
  device_name, signal_name = signal_group[alias]
  signal_group_str.append('"%s": ("%s", "%s"),' %(alias, device_name, signal_name))
signal_group_str[0]  = signal_group_head + signal_group_str[0]
signal_group_str[-1] = signal_group_str[-1] + '},]'
signal_group_str     = signal_group_sep.join(signal_group_str)

pos = s.find('class')
s = s[:pos] + signal_group_str + '\n\n' + s[pos:]

indent = re.search('@classmethod\\s+def\\s+\\w+[\(\):\\w, =]+(\\s+)', s).group(1)
m = re.search('@classmethod\\s+def\\s+\\w+[\(\):\\w, =]+(((%s.+)|(\n[ \t]*))+)' %indent, s)
p = m.group(1)
r = p.replace(indent, indent + 2 * ' ')
s = re.sub('(@classmethod\\s+def\\s+\\w+[\(\):\\w, =]+)(\\s+)', '\\1\\2'
                                                                'try:\\2'
                                                                '  Group = interface.Source.selectSignalGroup(SignalGroups)\\2'
                                                                'except ValueError, error:\\2'
                                                                '  print __file__\\2'
                                                                '  print error.message\\2'
                                                                'else:\\2', s)

s = s.replace(p, r)

open(new, 'w').write(s)