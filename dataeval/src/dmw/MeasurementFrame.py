from PySide import QtGui, QtCore

from OptionFrames import cFileOption, cMultiFileOption
from interface.modules import ModuleName

class cMeasurementFrame(QtGui.QFrame):
  DEFAULT_CHANNEL = 'main'
  def __init__(self, config, section, layout):
    QtGui.QFrame.__init__(self)
    config.UpdateCallbacks.append(self.update)
    self.config = config
    self.section = section
    self.channels = set()
    self.wildcard = self.config.getQtExtendedStyleWildCard()
    self.layout = layout

    self.main_ch = cFileOption(None, config, 'Measurement', self.DEFAULT_CHANNEL,
                          filter=self.wildcard)
    self.channels.add(self.DEFAULT_CHANNEL)
    main_ch_layout = QtGui.QHBoxLayout()
    self.layout.addWidget(self.main_ch.Label, 1, 0)
    self.layout.addWidget(self.main_ch.Value, 1, 2)
    self.layout.addWidget(self.main_ch.knoobleQBtn, 1, 3)
    self.layout.addWidget(self.main_ch.OpenFileBtn, 1, 4)
    self.layout.addWidget(self.main_ch.OpenLastUsedFileBtn, 1, 5)

    self.main_ch.is_save_last_files=True
    self.main_ch.file_type='Measurements'

    self.layout.addWidget(self.main_ch.knoobleLabel, 3, 0)
    self.layout.addWidget(self.main_ch.knoobleValue, 3, 2)
    # self.layout.addWidget(self.main_ch.labelSearchText, 3, 3)

    self.main_ch.OpenLastUsedFileBtn.clicked.connect(self.main_ch.showLastOpenedFilesDialog)
    self.other_meases = cMultiFileOption(self.config, 'Measurement','',
                                         filter=self.wildcard)
    self.layout.addWidget(self.other_meases.Selector, 5, 0)
    self.layout.addWidget(self.other_meases.Value, 5, 2)
    self.layout.addWidget(self.other_meases.OpenFileBtn, 5, 3)

    self.update()
    return

  def update(self):
    channels = set([self.DEFAULT_CHANNEL,])
    modules = [module for module in self.config.options(self.section)
                      if self.config.getboolean(self.section, module)]

    for module in modules:
      active_params = []
      modname, _, prj = ModuleName.split(module)
      ext_mods = [ModuleName.create(modname, param, prj)
                 for param in self.config.options(module)
                 if self.config.getboolean(module, param)]
      for ext_mod in ext_mods:
        chs_ = self.config.get('Channels', ext_mod)
        chs = chs_.split(',')
        for ch in chs:
          channels.add(ch)

    new_channels = channels.difference(self.channels)
    obsolated_channels = self.channels.difference(channels)
    extra_chs = channels.difference(set([self.DEFAULT_CHANNEL]))

    if new_channels or obsolated_channels:

      for channel in (sorted(new_channels)):
        if channel == self.DEFAULT_CHANNEL: continue

        self.other_meases.addItem(channel)
        self.channels.add(channel)

      for channel in obsolated_channels:
        if channel == self.DEFAULT_CHANNEL: continue

        self.other_meases.rmItem(channel)
        self.channels.remove(channel)
    else:
      for channel in self.channels:
        if self.other_meases is not None:
          self.other_meases.update()
          self.main_ch.update()
    return
