# -*- dataeval: init -*-

"""
Prints the FLC20 software version to the standard output and to the logger.
The fill method returns the raw string value that can be easily used by
other modules, too.
"""

from collections import OrderedDict

from interface import iView

all_sgs = {
  'Pictus': [{
    'pictus_version' : ('Video_Data_General_A', 'Pictus_SW_Version'),
  }],
  'MobilEye': [OrderedDict((
    ('app_version_A', ('Video_Data_General_A', 'Application_Version_A')),
    ('app_version_B', ('Video_Data_General_A', 'Application_Version_B')),  
    ('app_version_C', ('Video_Data_General_A', 'Application_Version_C')), 
    ('app_version_D', ('Video_Data_General_A', 'Application_Version_D')),
  ))],
  'Protocol': [OrderedDict((
    ('protocol_version_A', ('Video_Data_General_A', 'Protocol_Version_A')),
    ('protocol_version_B', ('Video_Data_General_A', 'Protocol_Version_B')), 
    ('protocol_version_C', ('Video_Data_General_A', 'Protocol_Version_C')),
    ('protocol_version_D', ('Video_Data_General_A', 'Protocol_Version_D')),
  ))],
}

init_params = {}
for ver_type in all_sgs.iterkeys():
  init_params[ver_type] = dict(ver_type=ver_type)

class View(iView):
  def init(self, ver_type):
    self.ver_type = ver_type
    return

  def check(self):
    group = self.source.selectSignalGroup(all_sgs[self.ver_type])
    return group

  def fill(self, group):
    version_parts = []
    group_def = all_sgs[self.ver_type][0]
    for alias in group_def.iterkeys():
      version_parts.append("%d" % group.get_value(alias)[0])
    version_str = ".".join(version_parts)
    return version_str

  def view(self, version_str):
    msg = "FLC20 %s version: %s" % (self.ver_type, version_str)
    self.logger.info(msg)
    print msg
    return
