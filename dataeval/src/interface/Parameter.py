from .module import Parameter

class iParameter:
  def __init__(self):
    self.Keys = ()
    """:type: str
    Container of the name of the attributes genKeys method generate it."""
    pass

  def genKeys(self):
    """Generate the `Keys` attribute. This method has to be run at the end of
    the constructor."""
    Keys = []
    for Name in dir(self):
      if (( not Name.startswith('__') or not Name.endswith('__'))
        and not hasattr(self.__class__, Name)):
        Value = getattr(self, Name)
        if not callable(Value):
          Keys.append(Name)
    self.Keys = tuple(Keys)
    pass

  def getSign(self):
    Signature = Parameter.from_module(self, self.Keys)
    Signature = Signature.to_str()
    return Signature

  def __str__(self):
    return self.getSign()

