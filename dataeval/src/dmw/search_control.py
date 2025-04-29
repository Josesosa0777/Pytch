from control import SingleControl

class SearchControl(SingleControl):
  Interface = 'iSearch'
  def getSource(self, channel):
    self.config.load(self.manager, self.Interface)
    source = self.manager.get_source(channel)
    return source

  def getBaseName(self):
    BaseName = self.config.get('General', 'BatchFile')
    return BaseName
