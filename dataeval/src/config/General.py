import section

class cSection(section.cSection):
  def initConfig(self, Modules):
    self.Config.add_section('GroupTypes')
    self.Config.add_section('VidCalibs')
    self.Config.add_section('DocTemplates')
    
    self.Config.set('General', 'Report', '')
    self.Config.set('General', 'BatchFile', '')
    self.Config.set('General', 'RepDir', '')    
    self.Config.set('General', 'MeasPath', '')
    self.Config.set('General', 'Backup', '')
    self.Config.set('General', 'MapDb', '')

    self.Config.add_section('Measurement')
    for channel in Modules.get_channels():
      self.Config.set('Measurement', channel, '')
    return

