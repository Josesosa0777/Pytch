class GroupTypes:
  def __init__(self):
    self._projects = {}
    return

  def clear(self):
    self._projects.clear()
    return

  def add_types(self, prj_name, types):
    all_types = set(self._projects.get(prj_name, set()))
    all_types.update(types)
    self._projects[prj_name] = list(all_types)
    return

  def get_type(self, prj_name, type_name):
    assert prj_name in self._projects,\
           '%s is not a registered project name.' %prj_name
    types = self._projects[prj_name]
    assert type_name in types,\
           '%s is not registered in %s project.' %(type_name, prj_name)
    type_number = types.index(type_name)
    return type_number

  def get_types(self, prj_name, types):
    type_numbers = [self.get_type(prj_name, type_name)
                    for type_name in types]
    return type_numbers

  def copy(self):
    grouptypes = GroupTypes()
    grouptypes._projects = self._projects.copy()
    return grouptypes

