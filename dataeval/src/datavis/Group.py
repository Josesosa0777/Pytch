class iGroup(object):
  def __init__(self, KeyCodeCrossTable=None):  
    self.KeyCodes = {}
    """:type: dict
    Key code to hide or show object groups."""
    self.KeyCodeCrossTable = KeyCodeCrossTable
    """:type: dict    
    Cross table to resolve the GUI key event key code {'A': KeyCodeOfA, }"""
    self.Groups = {}
    """:type: dict
    Container of the goups"""
    self.Toggles = {}
    """:type: dict
    Toggle switches for `Groups`"""
    self.OrigVisibility = {}
    self.Invisibles = []
    """:type: list
    Container of the invisble `Groups` values"""
    self.Labels = []
    """:type: list
    Switch On/Off labels of the groups"""
    self.LabelIndices = {}
    """:type: dict
    {GroupName:self.LabelsIndex<int>}"""
    self.Buffers = {}
    """:type: dict
    {GroupName<str>:GropValues<list>}""" 
    self.CurveTypes = set()
    """:type: set
    Container of curve types"""

    pass
  
  def copy(self, Other):
    """
    :Parameters:
      Other : `iGroup`
    """
    self.KeyCodes          = Other.KeyCodes
    self.KeyCodeCrossTable = Other.KeyCodeCrossTable
    self.Groups            = Other.Groups
    self.Toggles           = Other.Toggles
    self.Invisibles        = Other.Invisibles
    self.Labels            = Other.Labels
    self.LabelIndices      = Other.LabelIndices
    self.Buffers           = Other.Buffers
    pass
    
  def addGroup(self, GroupName, GroupParam):
    """
    :Parameters:
      GroupName : str
      GroupParam: cGroupParam
    """
    self.Labels.append('(%s) %s: %s'%(GroupParam.KeyCode, GroupName, 'On' if GroupParam.Visible else 'Off'))
    if self.KeyCodeCrossTable:
      KeyCode = self.KeyCodeCrossTable[GroupParam.KeyCode]
    else:
      KeyCode = GroupParam.KeyCode
    self.Groups[GroupName] = GroupParam.Types
    self.KeyCodes[KeyCode] = GroupName
    self.Toggles[GroupName] = GroupParam.Visible
    self.OrigVisibility[GroupName] = GroupParam.Visible
    self.LabelIndices[GroupName] = len(self.Labels)-1
    self.Buffers[GroupName] = []
    self.setGroup(GroupName, GroupParam.Visible, GroupParam.KeyCode)
    self.selectGroup(GroupName)
    if GroupParam.IsCurve:
        self.CurveTypes = self.CurveTypes.union(GroupParam.Types)
    pass
  
  def addGroups(self, Groups):
    """
    :Parameters:
      Groups : dict
        {GroupName<str>: GroupParam<cGroupParam>,}
    """
    GroupNames = Groups.keys()
    GroupNames.sort()
    for GroupName in GroupNames:
      GroupParam = Groups[GroupName]
      self.addGroup(GroupName, GroupParam)
    pass
  
  def selectGroup(self, GroupName):
    """
    :Parameters:
      GroupName : str
    """
    try:
      Toggle = self.Toggles[GroupName]
      Index  = self.LabelIndices[GroupName]
      Label  = self.Labels[Index]
      Buffer = self.Buffers[GroupName]
      if Toggle:
        while Buffer:
          Type = Buffer.pop()
          self.Invisibles.remove(Type)
      else:
        Types = self.Groups[GroupName]
        self.Invisibles.extend(Types)
        Buffer.extend(Types)
      self.Labels[Index] = Label.replace('Off', 'On') if Toggle else Label.replace('On', 'Off')
      self._setVisible(GroupName, Toggle)
      self.Toggles[GroupName] = not Toggle
      pass
    except:
      pass

  def getKeyCode(self, Name):
    for KeyCode, Group in self.KeyCodes.iteritems():
      if Group == Name:
        return KeyCode
    raise KeyError('KeyCodes does not contain <%s>' %Name)
    
  def _setVisible(self, GroupName, Visible):
    """
    :Parameters:
      GroupName : str
      Visible : bool
    """
    pass
  
  def setGroup(self, GroupName, Visible, KeyCode):
    """
    :Parameters:
      GroupName : str
      Visible : bool
      KeyCode : str
    """
    pass
  
  pass  
