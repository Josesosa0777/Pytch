from control import SingleControl

class cCompareControl(SingleControl):
  Interface = 'iCompare'
  def getBaseName(self):
    return self.config.get('Measurement', 'compare')

  def getSource(self, channel):
    self.config.baseload(self.manager)
    return self.manager.get_source(channel)

