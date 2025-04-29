class cGroupParam():
  "Holds the parameters of a group"
  
  def __init__(self, Types, KeyCode, Visible, IsCurve):
    if not (KeyCode.isupper() or KeyCode.isdigit()):
      raise ValueError('Only numbers and capital letters are valid keycodes.')
    self.KeyCode = KeyCode
    """:type: str
    Keycode of the group.
    CONVENTION: Only numbers and capital letters are used for this purpose;
    ValueError is raised otherwise.
    Key handler in VideoPlayer must be updated in case of changing this
    convention."""
    self.Types = Types
    """:type: tuple<int>
    Container of the group types"""
    self.Visible = Visible
    """:type: bool    
    Visibility toggle"""
    self.IsCurve = IsCurve
    """:type: bool    
    Toggle for groups represented as curves"""
    return
  
  def __iter__(self):
    iterator = iter(self.Types)
    return iterator

  def activate(self, Types):
    self.Types = set(Types)
    return
  
  def copy(self):
    GroupParam = cGroupParam(self.Types, self.KeyCode, self.Visible,
                             self.IsCurve)
    return GroupParam

  def update(self, GroupParam):
    self.Types.update(GroupParam.Types)
    return

  def __eq__(self, GroupParam):
    Eq =     isinstance(GroupParam, cGroupParam)\
         and self.Types == GroupParam.Types\
         and self.Visible == GroupParam.Visible\
         and self.IsCurve == GroupParam.IsCurve
    return Eq

def filterParamDict(ParamDict, Names):
  Filtered = {}
  for Name, Param in ParamDict.iteritems():
    if Name not in Names: continue
    for GroupName, Group in Param.iteritems():
      if GroupName in Filtered:
        FilteredGroup = Filtered[GroupName]
        FilteredGroup.update(Group)
      else:
        Filtered[GroupName] = Group.copy()
  return Filtered

