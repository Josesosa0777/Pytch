import os
import sys
import imp
import logging
from StringIO import StringIO

from PySide import QtGui, QtCore

#TO import from memory
#http://stackoverflow.com/questions/14191900/pythonimport-module-from-memory
class StringImporter(object):
  def __init__(self, modules):
     self._modules = dict(modules)
     return

  def find_module(self, fullname, path):
    if fullname in self._modules.keys():
       return self
    return None

  def load_module(self, fullname):
    if not fullname in self._modules.keys():
       raise ImportError(fullname)

    new_module = imp.new_module(fullname)
    mod = self._modules[fullname]
    mod.seek(0)
    exec mod.read() in new_module.__dict__
    return new_module

class Text:
  PREFIX = 'spam'
  def __init__(self, filename, config, control):
    self.config = config
    self.control = control
    self.temp = ''
    self._sections = {}
    self._number_LN = 0
    self._number_PN = 0
    self._number_axis = 0
    self._value_LN = 0
    self._value_PN = 0
    self.importer = None
    self.update_by_file(filename)
    return

  def write_temp(self, prefix, text):
    scandir = self.config.getMainModuleDir(os.curdir)

    #name = os.path.join(scandir, prefix + '.py')
    self.temp = StringIO()
    self.temp.write(text.encode('utf-8'))

    self.temp.seek(0)

    prj_name = self.config.getMainPath()
    modulename = '%s.%s' %(prj_name, self.PREFIX)
    self.importer = StringImporter({modulename : self.temp})
    sys.meta_path.append(self.importer)
    return self.PREFIX

  def get_text(self):
    lines = []
    for section in self._sections.itervalues():
      lines.extend(section)
    lines = ''.join(lines)
    return lines

  def read(self, filename):
    return

  def update_text_frame(self):
    'update function of the text frame'
    return
  
  def update_nav_metadata(self):
    """Callback: Updates navigator metadata"""
    return

  def add_module(self, name, active_parameters, filename=None):
    prj_name = self.config.getMainPath()
    if filename is None:
      module = self.config.scanMemoryModule(name, prj_name, self.temp)
    else:
      module = self.config.scanInterfaceModule(filename, prj_name)
    self.config.initModule(module)
    module.hold_parameters(active_parameters)
    self.config.activateModule(module.interface, module.name, module.parameters,
                               module.prj, module.channels)
    manager = self.control.getManager()
    self.config.loadNameSpace(manager)
    return

  @staticmethod
  def rm_temp_from_ext(config, control, name, temp, importer):
    prj_name = config.getMainPath()
    module = config.scanMemoryModule(name, prj_name, temp)
    manager = control.getManager()
    config.removeModule(manager, module.interface, module.name, module.prj)
    if importer is not None:
      sys.meta_path.remove(importer)
    return

  def rm(self, filename):
    prj_name = self.config.getMainPath()
    modulename = '%s.%s' %(prj_name, self.PREFIX)
    active_parameters = self.rm_module(self.PREFIX)
    if self.importer is not None:
      sys.meta_path.remove(self.importer)
      self.importer = None
    return active_parameters

  def rm_module(self, name, filename=None):
    prj_name = self.config.getMainPath()
    if filename is None:
      module = self.config.scanMemoryModule(name, prj_name, self.temp)
    else:
      module = self.config.scanInterfaceModule(filename, prj_name)
      self.rm_file(filename)
    manager = self.control.getManager()
    self.config.removeModule(manager, module.interface, module.name, module.prj)
    active_parameters = self.config.getActiveOptions(module.name)
    return active_parameters

  def rm_file(self, filename):
    os.remove(filename)
    pyc = filename.replace('.py', '.pyc')
    if os.path.isfile(pyc):
      os.remove(pyc)
    return

  def update_by_text(self, text):
    active_parameters = self.rm(self.temp)
    self.write_temp(self.PREFIX, text)
    self.read(self.temp)
    self.add_module(self.PREFIX, active_parameters)
    self.config.update()
    return

  def update_by_file(self, filename):
    target_file = open(filename)
    self.read(target_file)
    self.write_temp(self.PREFIX, self.get_text())
    active_parameters = set()
    self.add_module(self.PREFIX, active_parameters)
    self.update_text_frame()
    self.config.update()
    return

  def update(self):
    active_parameters = self.rm(self.temp)
    self.write_temp(self.PREFIX, self.get_text())
    self.add_module(self.PREFIX, active_parameters)
    self.update_text_frame()
    self.config.update()
    return

  def close(self):
    self.rm(self.temp)
    return

  def open(self, filename):
    target_file = open(filename)
    if self.check(target_file):
      self.rm(self.temp)
      self.update_by_file(filename)
      self.update_nav_metadata()
    else:
      self.config.log('Invalid module: %s\n' %filename, Level=logging.ERROR)
    return

  def save(self, filename):
    filename = filename + '.py' if not filename.endswith('.py') else filename
    if os.path.exists(filename):
      try:
        self.rm_module(self.PREFIX, filename=filename)
      except ValueError:
        pass
    open(filename, 'w').write(self.get_text().encode('utf-8'))
    active_parameters = set()
    self.add_module(self.PREFIX, active_parameters, filename=filename)
    self.config.update()
    pass

  def get_init_dir(self):
    return self.config.getMainModuleDir(os.curdir)

