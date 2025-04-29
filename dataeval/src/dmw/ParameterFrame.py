from PySide import QtGui, QtCore

from ModuleFrame import cModuleFrame
from interface.module import Parameter

class cParameterFrame(cModuleFrame):
  def __init__(self, root, Config, Section, ListBox, 
               SubFromOption=('',''), SubToOption=('','')):
    cModuleFrame.__init__(self, root, Config,  Section, ListBox, SubFromOption, 
                              SubToOption)
    self.layout = self.layout()
    self.Config = Config

    clone_btn  = QtGui.QPushButton('Clone')
    clone_btn.clicked.connect(self.clone)

    activate_btn = QtGui.QPushButton('Activate')
    activate_btn.clicked.connect(self.activate_param)

    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(clone_btn)
    hbox.addWidget(activate_btn)

    self.layout.addLayout(hbox)

    self.selected_parameter = ''
    self.selected_module = ''

    self.temp_param_name = ''

    self.param_layout = []
    self.ParameterSection.Actives.Options.itemClicked.connect(
                                                         self.parameterSelected)
    self.ParameterSection.Passives.Options.itemClicked.connect(
                                                         self.parameterSelected)
    self.ModuleSections.itemSelectedSignal.signal.connect(self.moduleSelected)
    return
    
  def clone(self):
    self.clear_parameter_interface()
    if not self.selected_parameter or not self.selected_module: return
    self.temp_param_name, Params = self.Config.cloneModuleParam(
                                self.selected_module, self.selected_parameter)

    for name, value in Params:
      param_label = QtGui.QLabel(name)
      param_value = QtGui.QLineEdit()
      param_value.setText(value)

      frame = QtGui.QFrame()

      param_hbox = QtGui.QHBoxLayout()
      param_hbox.addWidget(param_label)
      param_hbox.addWidget(param_value)
      frame.setLayout(param_hbox)
      frame.label = param_label
      frame.value = param_value
      self.param_layout.append(frame)

      self.layout.addWidget(frame)
    return
    
  def activate_param(self):
    if not self.selected_parameter or not self.selected_module \
       or not self.temp_param_name: return
    param_str_list = [(param_layout.label.text(), param_layout.value.text())
                       for param_layout in self.param_layout]
    params = Parameter.from_str_list(param_str_list)
    param_list = params.to_str()
    self.Config.param(self.selected_module, self.temp_param_name, param_list)
    self.Config.update()
    self.clear_parameter_interface()
    selected_module = self.ModuleSections.Actives.Options.findItems(
                                                           self.selected_module,  
                                                         QtCore.Qt.MatchExactly)
    self.ModuleSections.Actives.Options.setCurrentItem(selected_module[0])
    self.ModuleSections.emitSelectSignal(selected_module[0])
    return

  def parameterSelected(self, item):
    self.selected_parameter = item.text()
    return

  def moduleSelected(self, module):
    self.selected_module = module
    return

  def clear_parameter_interface(self):
   for parameter_layout in self.param_layout:
      parameter_layout.close()
   self.param_layout = []   
   return
    