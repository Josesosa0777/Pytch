class Params(dict):
  def filter(self, status_names):
    filtered = Params()
    for status_name, param in self.iteritems():
      if status_name in status_names:
        filtered.update(param)
    return filtered

  def copy(self):
    other = dict.copy(self)
    other = self.__class__(other)
    return other


class GroupParams(Params):
  def filter(self, status_names):
    filtered = GroupParams()
    for status_name, param in self.iteritems():
      if status_name in status_names:
        for group_name, group in param.iteritems():
          if group_name in filtered:
            filtered_group = filtered[group_name]
            filtered_group.update(group)
          else:
            filtered[group_name] = group
    return filtered

  def activate(self, grouptypes, prj_name):
    activated_params = GroupParams()
    for status_name, param in self.iteritems():
      activated = {}
      for group_name, group in param.iteritems():
        types = grouptypes.get_types(prj_name, group.Types)
        activated_group = group.copy()
        activated_group.activate(types)
        activated[group_name] = activated_group
      activated_params[status_name] = activated
    return activated_params

  def build_type_params(self, type_values):
    build = TypeParams()
    missing = set()
    for status, group in self.iteritems():
      build_types = {}
      for groupname, types in group.iteritems():
        for type_ in types:
          if type_ in type_values:
            build_types[type_] = type_values[type_]
          else:
            missing.add(type_)
      build[status] = build_types
    return build, missing

  def build_groupname_params(self, groupname_values):
    build = Params()
    missing = set()
    for status, group in self.iteritems():
      build_values = {}
      for groupname in group:
        if groupname in groupname_values:
          build_values[groupname] = groupname_values[groupname]
        else:
          missing.add(groupname)
      build[status] = build_values
    return build, missing

class TypeParams(Params):
  def activate(self, grouptypes, prj_name):
    activated_params = TypeParams()
    for status_name, param in self.iteritems():
      activated = {}
      for type_name, value in param.iteritems():
        type_number = grouptypes.get_type(prj_name, type_name)
        activated[type_number] = value
      activated_params[status_name] = activated
    return activated_params

quanames = {}
labels = {}
tags = {}
viewangles = Params()
groups = GroupParams()
legends = TypeParams()
shapelegends = TypeParams()
grouptypes = set()

