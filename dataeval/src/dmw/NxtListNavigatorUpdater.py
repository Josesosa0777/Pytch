import logging

import os
import re
from PySide import QtGui, QtCore

from PlotNavigatorFrame import SimpleSignal
from PySide.QtCore import Qt
from PySide.QtGui import QIcon

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class cListNavigatorUpdater():
  def __init__(self, Text, title):

    self.logger = logging.getLogger()

    self.Text = Text

    self.Imports = set()
    self.Imports.add('datavis')
    self.Imports.add('interface')

    self.Tags = dict(Client    = 'client',
                     Time      = 'time',
                     Value     = 'value',
                     Group     = Text.group_name,
                     Alias     = '',
                     Title     = title,
                     Unit= '',
                     GroupName = 'Default',
                     background = '#fff',
                     ClientCounter = -1,
                     ValueCounter = -1,
                     CurrentClient = -1)
    self.Constructor = '%(Client)s%(CurrentClient)02d = ' \
                       'datavis.cListNavigator(title="%(Title)s")'
    self.AddClient   = 'self.sync.addClient(%(Client)s%(CurrentClient)02d )'
    self.RemoveDefault = 'del %(Client)s%(CurrentClient)02d.groups[\'Default\']'
    self.GetSignal   = '%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s' \
                       ' = %(Group)s.get_signal("%(Alias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addsignal("%(Alias)s%(Index)s%(Unit)s", ' \
                       '(%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s%(Index)s), ' \
                       'groupname="%(GroupName)s",bg="%(background)s")'
    self.GetCustomSignal = '%(Time)s_custom_%(Alias)s,' \
                           ' %(Value)s_custom_%(Alias)s,' \
                           ' = %(Group)s.get_signal("%(OriginalAlias)s")'

    self.GetCustomSignalWithRescale = '%(Time)s_custom_%(Alias)s,' \
                           ' %(Value)s_custom_%(Alias)s,' \
                           ' = %(Group)s.get_signal("%(OriginalAlias)s", **rescale_kwargs)'

    pass

  def addCustomSignal(self, groupname, custom_signal_data, background='#fff'):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    custom_signal_name = custom_signal_data[0]
    custom_signals_list= custom_signal_data[1]
    custom_signal_expression= custom_signal_data[2]
    custom_signal_unit = custom_signal_data[3]
    time_signal_name, expression = self.addCustomExpressionSupportingSignals(custom_signals_list,
                                                                             custom_signal_expression)
    custom_signal_expression = expression
    self.Tags['Unit'] = "[" + custom_signal_unit + "]"
    self.Tags['OriginalAlias'] = custom_signal_name
    self.Tags['Alias'] = custom_signal_name
    self.Tags['Group'] = self.Text.group_name
    self.Tags['GroupName'] = groupname
    self.Tags['background'] = background
    Lines = []
    Lines.append("time_" + custom_signal_name + " = time_custom_" + time_signal_name)
    Lines.append("value_" + custom_signal_name + " = " + custom_signal_expression)

    Lines.append(self.AddSignal % self.Tags)
    self.Text.add_lines(Lines)

  def create(self):
    self.incrementClientCounter()
    # self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    self.Text.add_modules(self.Imports)
    self.Text.add_lines((self.Constructor %self.Tags,
                         self.AddClient   %self.Tags,"del client00.groups[\'Default\']"))
    pass

  def addSignals(self, groupname,signals,background='#fff'):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    Lines = []
    for DevName, SigName, unit in signals:
      self.incrementValueCounter()
      # self.ValueNrIncreasedSignal.signal.emit()
      self.Tags['Index'] = ''
      if len(SigName.split('[:,')) == 2:
        (SigName, Index) = SigName.split('[')
        self.Tags['Index'] = '[' + Index

      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', self.Text.add_signal(DevName, SigName))
      self.Tags['Unit']      = "["+unit +"]"
      self.Tags['Group']     = self.Text.group_name
      self.Tags['GroupName'] = groupname
      self.Tags['background']= background
      # print(self.GetSignal %self.Tags)
      # print(self.AddSignal %self.Tags)
      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    print(self.Text.get_text())
    pass


  def addCustomExpressionSupportingSignals(self, signals, expression):
    Lines = []
    first_signal = True
    for signal_custom_name, (DevName, SigName, Unit) in signals:
      self.incrementValueCounter()
      # self.ValueNrIncreasedSignal.signal.emit()
      self.Tags['Index'] = ''
      if len(SigName.split('[:,'))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index

      alias = self.Text.add_signal(DevName, SigName)
      self.Tags['OriginalAlias'] = alias

      if '-' in alias:
        alias_signal_name, alias_device_name = alias.split("-")
        self.Tags['Alias'] = alias_device_name + "_" + alias_signal_name
      else:
        self.Tags['Alias'] = alias

      self.Tags['Group'] = self.Text.group_name
      # self.Tags['GroupName'] = self.GroupNameEntry.text()
      if first_signal is True:
        Lines.append(self.GetCustomSignal %self.Tags)
      else:
        Lines.append(self.GetCustomSignalWithRescale % self.Tags)

      if not "value_custom_" + self.Tags['Alias']  in expression:
        expression = expression.replace("value_custom_" + SigName, "value_custom_" + self.Tags['Alias'])

      if first_signal is True:
        Lines.append("rescale_kwargs = {'ScaleTime': time_custom_" + self.Tags['Alias'] + "}")
        first_signal = False
    self.Text.add_lines(Lines)
    return self.Tags['Alias'], expression

  def update_from_metadata(self):
    """Updates the tagged counters when the script has been loaded from
    a file instead of being created manually during the current session
    """
    for _ in xrange(self.Text._number_LN):
      self.incrementClientCounter()
      self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    for _ in xrange(self.Text._value_LN):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
    return

  def incrementClientCounter(self):
    self.Tags['ClientCounter'] += 1
    return

  def incrementValueCounter(self):
    self.Tags['ValueCounter'] += 1
    return

  def resetCounters(self):
    self.Tags['ClientCounter'] = -1
    self.Tags['ValueCounter'] = -1
    self.Tags['CurrentClient'] = -1
    return
