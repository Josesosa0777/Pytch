import logging

import os
import re
IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")


class cPlotNavigatorUpdater():
  def __init__(self,  Text, title='', template_geometry='(0,0)'):
    self.logger = logging.getLogger()
    self.Text = Text
    self.Imports = set()
    self.Imports.add('datavis')
    self.Imports.add('interface')

    self.Tags = dict(Client   = 'client',
                     Geometry = template_geometry,
                     Axis     = 'axis',
                     Time     = 'time',
                     Value    = 'value',
                     Group    = Text.group_name,
                     Alias    = '',
                     UnitVar  = 'unit',
                     OffsetVar  = None,
                     FactorVar  = None,
                     DisplayeScaledVar  = True,
                     Title    = title,
                     SignalLabel = '',
                     ylabel = '',
                     xlabel = '',
                     rowNr= 0,
                     colNr= 0,
                     yticks='{}',
                     ClientCounter = -1,
                     AxisCounter = -1,
                     ValueCounter = -1,
                     CurrentClient = -1)
    self.Constructor = '%(Client)s%(CurrentClient)02d = datavis.cPlotNavigator'\
                       '(title="%(Title)s", subplotGeom=eval("%(Geometry)s"))'
    self.AddClient   = 'self.sync.addClient(%(Client)s%(CurrentClient)02d)'
    self.AddAxis     = '%(Axis)s%(AxisCounter)02d = ' \
                        '%(Client)s%(CurrentClient)02d.addAxis(grid=True,xlabel ="%(xlabel)s",ylabel = "%(ylabel)s",yticks = eval("%(yticks)s"),rowNr=%(rowNr)d,' \
                       'colNr=%(colNr)d)'
    self.GetSignal   = '%(Time)s_%(Alias)s,' \
                       ' %(Value)s_%(Alias)s,' \
                       ' %(UnitVar)s_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s")'
    self.AddSignal   = '%(Client)s%(CurrentClient)02d.addSignal2Axis' \
                       '(%(Axis)s%(AxisCounter)02d, "%(SignalLabel)s", ' \
                       '%(Time)s_%(Alias)s, ' \
                       '%(Value)s_%(Alias)s%(Index)s, ' \
                       'offset=%(OffsetVar)s, ' \
                       'factor=%(FactorVar)s, ' \
                       'displayscaled=%(DisplayScaledVar)s,' \
                       'unit=%(UnitVar)s_%(Alias)s)'
    self.GetCustomSignal   = '%(Time)s_custom_%(Alias)s,' \
                       ' %(Value)s_custom_%(Alias)s,' \
                       ' %(UnitVar)s_custom_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s")'
    self.GetCustomSignalWithRescale = '%(Time)s_custom_%(Alias)s,' \
                       ' %(Value)s_custom_%(Alias)s,' \
                       ' %(UnitVar)s_custom_%(Alias)s = ' \
                       '%(Group)s.get_signal_with_unit("%(OriginalAlias)s", **rescale_kwargs)'
    pass


  def addCustomSignal(self, custom_signal_data):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before there isn't a Plot/List Navigator")
      return
    custom_signal_name = custom_signal_data[0]
    custom_signals_list= custom_signal_data[1]
    custom_signal_expression= custom_signal_data[2]
    custom_signal_unit = custom_signal_data[3]
    time_signal_name, expression = self.addCustomExpressionSupportingSignals(custom_signals_list, custom_signal_expression)
    custom_signal_expression = expression
    self.Tags['SignalLabel'] = custom_signal_data[4]
    self.Tags['OffsetVar'] = custom_signal_data[5]
    self.Tags['FactorVar'] = custom_signal_data[6]
    self.Tags['DisplayScaledVar'] = custom_signal_data[7]
    self.Tags['OriginalAlias'] = custom_signal_name
    self.Tags['Alias'] = custom_signal_name
    self.Tags['Group'] = self.Text.group_name
    self.Tags['Unit'] = ''
    Lines = []

    Lines.append("time_" + custom_signal_name + " = time_custom_" + time_signal_name)
    Lines.append("value_" + custom_signal_name + " = " + custom_signal_expression)
    Lines.append("unit_" + custom_signal_name + " = \"" + custom_signal_unit + "\"")
    Lines.append(self.AddSignal % self.Tags)
    self.Text.add_lines(Lines)

  def create(self,plot_detail):
    self.incrementClientCounter()
    self.incrementAxisCounter()
    # self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    self.Text.add_modules(self.Imports)
    self.Tags["Axis"] = plot_detail[1]
    self.Tags["ylabel"] = plot_detail[3]
    self.Tags["xlabel"] = plot_detail[2]
    self.Tags["rowNr"] = int(plot_detail[5])
    self.Tags["colNr"] = int(plot_detail[6])
    if plot_detail[4].strip() == "":
      self.Tags["yticks"]= "{}"
    else:
      self.Tags["yticks"] = plot_detail[4]

    self.Text.add_lines((self.Constructor %self.Tags,
                         self.AddClient   %self.Tags,
                         self.AddAxis     %self.Tags))
    pass

  def addAxis(self,plot_detail):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Axis cannot be added before there isn't a Plot/List Navigator")
      return
    self.incrementAxisCounter()
    self.Tags["Axis"] = plot_detail[1]
    self.Tags["ylabel"] = plot_detail[3]
    self.Tags["xlabel"] =plot_detail[2]
    self.Tags["rowNr"]=int(plot_detail[5])
    self.Tags["colNr"]=int(plot_detail[6])
    if plot_detail[4].strip() == "":
      self.Tags["yticks"]= "{}"
    else:
      self.Tags["yticks"] = plot_detail[4]
    self.Text.add_lines((self.AddAxis %self.Tags,))
    pass

  def addSignals(self, signals):
    if self.Tags['ClientCounter'] < 0 or self.Tags['CurrentClient'] < 0:
      self.logger.error("Please add Plot/List Navigator first by clicking on Add Plot/ Add List, Signal(s) cannot be added before "
                  "there isn't a Plot/List Navigator")
      return
    Lines = []
    for DevName, SigName, Unit, Label, Offset, Factor, DisplayScaled in signals:
      self.incrementValueCounter()
      # self.ValueNrIncreasedSignal.signal.emit()
      self.Tags['Index'] = ''
      if len(SigName.split('[:,'))==2:
          (SigName, Index) = SigName.split('[')
          self.Tags['Index'] = '[' + Index

      self.Tags['SignalLabel'] = Label + self.Tags['Index']
      if Offset is not None:
          if Offset == "":
              Offset = None
          else:
              Offset = float(Offset)
      if Factor is not None:
          if Factor == "":
              Factor = None
          else:
              Factor = float(Factor)
      self.Tags['OffsetVar'] = Offset
      self.Tags['FactorVar'] = Factor
      self.Tags['DisplayScaledVar'] = DisplayScaled
      self.Tags['OriginalAlias'] = self.Text.add_signal(DevName, SigName)
      self.Tags['Alias'] = re.sub('[^a-zA-Z0-9]+', '_', self.Text.add_signal(DevName, SigName))
      self.Tags['Group']   = self.Text.group_name
      self.Tags['Unit']    = Unit

      Lines.append(self.GetSignal %self.Tags)
      Lines.append(self.AddSignal %self.Tags)
    self.Text.add_lines(Lines)
    # print(self.Text.get_text())
    pass


  def addCustomExpressionSupportingSignals(self,signals, expression):
    Lines = []
    first_signal = True
    for signal_custom_name, (DevName, SigName, Unit) in signals:
      self.incrementValueCounter()

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
      self.Tags['Unit'] = Unit
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
    for _ in xrange(self.Text._number_PN):
      self.incrementClientCounter()
      self.ClientNrIncreasedSignal.signal.emit()
    self.Tags['CurrentClient'] = self.Tags['ClientCounter']
    for _ in xrange(self.Text._number_axis):
      self.incrementAxisCounter()
    for _ in xrange(self.Text._value_PN):
      self.incrementValueCounter()
      self.ValueNrIncreasedSignal.signal.emit()
    return
    
  def incrementClientCounter(self):
    self.Tags['ClientCounter'] += 1
    return

  def incrementAxisCounter(self):
    self.Tags['AxisCounter'] += 1
    return

  def incrementValueCounter(self):
    self.Tags['ValueCounter'] += 1
    return

  def resetCounters(self):
    self.Tags['ClientCounter'] = -1
    self.Tags['AxisCounter'] = -1
    self.Tags['ValueCounter'] = -1
    self.Tags['CurrentClient'] = -1
    return
