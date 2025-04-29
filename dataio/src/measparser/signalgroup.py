import logging
from collections import OrderedDict

import numpy as np

from signalproc import selectTimeScale, rescale
from pyutils.functional import cached_attribute

logger = logging.getLogger()

class SignalGroupError(BaseException):
  pass

def str_error(error):
  messages = []
  title = 'Missing devices'
  content = error[title]
  if content:
    messages.append('  %s:' %title)
    for name in content:
      messages.append('    %s' %name)
  titles = error.keys()
  titles.remove(title)
  for title in titles:
    content = error[title]
    if content:
      messages.append('  %s:' %title)
      for major, minors in content.iteritems():
        for minor in minors:
          messages.append('    %-37s %-40s' %(major, minor))
          major = ''
  message = '\n'.join(messages)
  return message
  
def check_emptyerror(error):
  for value in error.itervalues():
    if value:
      return False
  return True

def str_errors(errors):
  messages = []
  for i, error in enumerate(errors):
    if not check_emptyerror(error):
      messages.append('#%d' %i)
      message = str_error(error)
      messages.append(message)
  message = '\n'.join(messages)
  return message

def check_onevalid(signalgroups, errors, length):
  """
  Check `signalgroups` it contains at least one full/valid
  signal group which has the `length` length.
  SignalGroupError is risen if it is not found.

  :Parameter:
    signalgroups : list
      [{alias<str>: (deviceName<str>, signalName<str>), }, ]
    errors : list
      [message<str>,]
    length : int
  :Exceptions:
    SignalGroupError
  """
  for signalgroup in signalgroups:
    if len(signalgroup) == length:
      return
  message = str_errors(errors)
  raise SignalGroupError(message)

def check_allvalid(signalgroups, errors, length):
  """
  Check `signalgroups` contains only valid
  signal groups which have the `length` length.
  SignalGroupError is risen if it is not found.

  :Parameter:
    signalgroups : list
      [{alias<str>: (deviceName<str>, signalName<str>), }, ]
    errors : list
      [message<str>,]
    length : int
  :Exceptions:
    SignalGroupError
  """
  for signalgroup in signalgroups:
    if len(signalgroup) != length:
      message = str_errors(errors)
      raise SignalGroupError(message)
  return

def select_allvalid_sgs(signalgroups, length, message=None):
  """
  Select groups from `signalgroups` that meet the `length` requirement.
  SignalGroupError is raised if no such group found.

  :Parameter:
    signalgroups : list
      [{alias<str>: (deviceName<str>, signalName<str>), }, ]
    length : int
      Required group length
    message : str, optional
      Error message when all valid group not found
  :Returns:
    allvalid_groups : list
      [{alias<str>: (deviceName<str>, signalName<str>), }, ]
  :Exceptions:
    SignalGroupError
  """
  allvalid_groups = [g for g in signalgroups if len(g) == length]
  if not allvalid_groups:
    msg = 'All valid group not found!' if message is None else message
    raise SignalGroupError(msg)
  return allvalid_groups

def check_by_original(originals, filtereds, errors):
  for original, filtered in zip(originals, filtereds):
    if len(original) != len(filtered):
      message = str_errors(errors)
      raise SignalGroupError(message)
  return

def select_firstvalid(signalgroups, errors, length):
  for i, signalgroup in enumerate(signalgroups):
    if len(signalgroup) == length:
      break
  else:
    message = str_errors(errors)
    raise SignalGroupError(message)
  return i, signalgroup

def select_longest(signalgroups, errors):
  winner, selected = _select_longest(signalgroups, errors)
  return selected

def _select_longest(signalgroups, errors):
  check = -1
  selected = None
  winner = None
  for i, signalgroup in enumerate(signalgroups):
    length = len(signalgroup)
    if length > check:
      check = length
      selected = signalgroup
      winner = i
  if selected is None:
    message = str_errors(errors)
    raise SignalGroupError(message)
  return winner, selected

def extract_signals(*signalgroups):
  for signalgroup in extract_dict(signalgroups):
    for alias, signal in signalgroup.iteritems():
      if isinstance(alias, (str, unicode)):
        if len(signal) == 2:
          devicename, signalname = signal
          if (    isinstance(devicename, (str, unicode))
              and isinstance(signalname, (str, unicode))):
            yield signal

def extract_dict(signalgroups):
  if isinstance(signalgroups, dict):
    yield signalgroups
  elif isinstance(signalgroups, (list, tuple)):
    for signalgroup in signalgroups:
      for group in extract_dict(signalgroup):
        yield group

def select_sgl_first_allvalid(filteredsglist, length):
  """
  Select the first `signalgroups` that contains only valid
  signal groups which have the `length` length.
  SignalGroupError is risen if none found.

  :Parameter:
    filteredsglist : list
      [(signalgroups, errors)]
    length : int
  :Returns:
    signalgroups : list
      [{alias<str>: (deviceName<str>, signalName<str>), }, ]
  :Exceptions:
    SignalGroupError
  """
  winner, signalgroups = _select_sgl_first_allvalid(filteredsglist, length)
  return signalgroups

def _select_sgl_first_allvalid(filteredsglist, length):
  messages = []
  for i, (signalgroups, errors) in enumerate(filteredsglist):
    messages.append("*%d*\n%s"%(i, str_errors(errors)))
    try:
      check_allvalid(signalgroups, errors, length)
    except SignalGroupError:
      pass
    else:
      return i, signalgroups
  else:
    raise SignalGroupError("\n".join(messages))

class SignalGroupList(list):
  def __init__(self, winner, validated_signalgroups, source):
    list.__init__(self)
    self.winner = winner
    for signalgroup_dict in validated_signalgroups:
      signalgroup = SignalGroup(winner, signalgroup_dict, source)
      self.append(signalgroup)
    return

  @classmethod
  def from_first_allvalid(cls, conc_signalgroups, source, **kwargs):
    check = len(conc_signalgroups[0][0])
    filtered = [source._filterSignalGroups(signalgroups, **kwargs) 
                for signalgroups in conc_signalgroups]
    winner, validated = _select_sgl_first_allvalid(filtered, check)
    self = cls(winner, validated, source)
    return self

  @classmethod
  def from_arbitrary(cls, arbitrary_signalgroups, source, **kwargs):
    check = len(arbitrary_signalgroups[0])
    filtered, errors = source._filterSignalGroups(arbitrary_signalgroups,
                                                  **kwargs)
    validated = select_allvalid_sgs(filtered, check)
    self = cls(None, validated, source)
    return self

  def get_value(self, alias, **kwargs):
    value = [group.get_value(alias, **kwargs) for group in self]
    return value

  def get_values(self, aliases, **kwargs):
    """
    WARNING: the signals can have different times, please use `ScaleTime`
    keyword to scale them to a common one.
    """
    values = [group.get_values(aliases, **kwargs) for group in self]
    return values

  def select_time_scale(self, strictly_growing_check=True):
    times = []
    for group in self:
      times.extend(group.get_all_times().values())
    time = selectTimeScale(times, strictly_growing_check)
    return time

class SignalGroup(dict):
  all_def_results = {  # all predefined default results to be returned in case of unavailable signal
    'empty': {
      'time': np.empty(0),
      'value': np.empty(0),
      'unit': "",
      'conversion_rule': {},
    },
    'None': {
      'time': None,
      'value': None,
      'unit': None,
      'conversion_rule': None,
    },
  }

  def __init__(self, winner, validated_signalgroup, source,
               all_aliases=None, def_results=None):
    """
    Initialize SignalGroup instance.

    :Parameters:
      winner : int or str
      validated_signalgroup : list
      source : cSignalSource
      all_aliases : list, optional
        List of aliases which result SignalGroupError (instead of KeyError)
        in case they are not part of the SignalGroup instance (e.g. because
        it is missing or invalid in the measurement).
      def_results : dict, optional
        Replace given values (time, value, unit etc.) with the specified ones
        instead of raising SignalGroupError.
        If None, SignalGroupError will not be suppressed.
        See any *value* of SignalGroup.all_def_results dictionary for example.
    """
    dict.__init__(self, validated_signalgroup)
    self.winner = winner
    self._source = source
    self.all_aliases = all_aliases if all_aliases is not None else \
                       validated_signalgroup.keys()
    self.enable_def_results = def_results is not None
    self.def_results = def_results if self.enable_def_results else \
                       self.all_def_results['None']
    return

  def copy(self):
    group = dict.copy(self)
    group = SignalGroup(self.winner, group, self._source,
      all_aliases=self.all_aliases, def_results=self.def_results)
    group.enable_def_results = self.enable_def_results
    return group

  @classmethod
  def from_named_signalgroups(cls, named_signalgroups, source, **kwargs):
    signalgroups = named_signalgroups.values()
    self = cls.from_first_valid(signalgroups, source, **kwargs)
    self.winner = named_signalgroups.keys()[self.winner]
    return self

  @classmethod
  def from_first_valid(cls, signalgroups, source, **kwargs):
    filtered, errors = source._filterSignalGroups(signalgroups, **kwargs)
    check = len(signalgroups[0])
    winner, signalgroup = select_firstvalid(filtered, errors, check)

    self = cls(winner, signalgroup, source)
    return self

  @classmethod
  def from_longest(cls, signalgroups, source, def_results=None, **kwargs):
    filtered, errors = source._filterSignalGroups(signalgroups, **kwargs)
    winner, signalgroup = _select_longest(filtered, errors) 
    all_aliases = signalgroups[0].keys() if signalgroups else []
    self = cls(winner, signalgroup, source,
      all_aliases=all_aliases, def_results=def_results)
    return self

  def __getitem__(self, alias):
    """
    Get signal definition for 'alias'.
    
    SignalGroupError is raised if the signal is missing or invalid (and
    therefore 'alias' is not part of the SignalGroup);
    KeyError is raised if 'alias' is completely invalid (e.g. misspelled).
    """
    if alias in self.invalid_aliases:
      raise SignalGroupError("'%s'" % alias)
    return dict.__getitem__(self, alias)

  @cached_attribute
  def invalid_aliases(self):
    """
    List of aliases where the corresponding signal has been excluded from
    the group due to its unavailability in the measurement.
    """
    return [alias for alias in self.all_aliases if alias not in self]

  def on_signal_group_error(self, err, def_result):
    """
    Raise SignalGroupError or return default value instead (depending on the
    SignalGroup instance initialization).
    """
    if not self.enable_def_results:
      raise Exception
    logger.debug("%s not available; using default values" % err.message)
    return def_result

  def get_signal(self, alias, **kwargs):
    """
    :KeyWords:
      Keywords are added to `cSignalSource.getSignal`
    """
    try:
      device_name, signal_name = self[alias]
    except SignalGroupError as err:
      return self.on_signal_group_error(err,
        (self.def_results['time'], self.def_results['value']))
    time, value = self._source.getSignal(device_name, signal_name, **kwargs)
    return [time, value]

  def get_signal_with_unit(self, alias, **kwargs):
    time, value = self.get_signal(alias, **kwargs)
    unit = self.get_unit(alias)
    return time, value, unit

  def get_value(self, alias, **kwargs):
    try:
      device_name, signal_name = self[alias]
      original_signal_name = signal_name
      # if len(original_signal_name.split('[')) == 2:
      #   (signal_name, index) = original_signal_name.split('[')
      #   signal_index = '[' + index
      # else:
      signal_index = ''
    except SignalGroupError as err:
      return self.on_signal_group_error(err, self.def_results['value'])
    time, value = self._source.getSignal(device_name, signal_name, **kwargs)
    if signal_index != '':
      value = eval('value' + signal_index)
    return value

  def get_all_values(self, **kwargs):
    values = self.get_values(self.iterkeys(), **kwargs)
    return values

  def get_values(self, aliases, **kwargs):
    """
    WARNING: the signals can have different times, please use `ScaleTime`
    keyword to scale them to a common one.
    """
    values = OrderedDict((alias, self.get_value(alias, **kwargs))
                         for alias in aliases)
    return values

  def get_time(self, alias):
    try:
      device_name, signal_name = self[alias]
    except SignalGroupError as err:
      return self.on_signal_group_error(err, self.def_results['time'])
    timekey = self._source.getTimeKey(device_name, signal_name)
    time = self._source.getTime(timekey)
    return time

  def get_all_times(self):
    times = self.get_times(self.iterkeys())
    return times
    
  def get_times(self, aliases):
    times = OrderedDict((alias, self.get_time(alias)) for alias in aliases)
    return times

  def get_unit(self, alias):
    try:
      device_name, signal_name = self[alias]
    except SignalGroupError as err:
      return self.on_signal_group_error(err, self.def_results['unit'])
    unit = self._source.getPhysicalUnit(device_name, signal_name)
    return unit

  def select_time_scale(self, strictly_growing_check=True):
    times = self.get_all_times()
    time = selectTimeScale(times.values(), strictly_growing_check)
    return time

  def get_conversion_rule(self, alias):
    try:
      device_name, signal_name = self[alias]
    except SignalGroupError as err:
      return self.on_signal_group_error(err, self.def_results['conversion_rule'])
    return self._source.Parser.getConversionRule(device_name, signal_name)

class VirtualGroup(dict):
  def __init__(self, time, values):
    '''
    :Parameters:
      time : `numpy.ndarray`
      values : `numpy.ndarray`
        StructArray
    '''
    dict.__init__(self, values.dtype.descr)
    self._time = time
    self._values = values
    return

  def copy(self):
    group = VirtualGroup(self._time, self._values)
    return group

  def get_signal_with_unit(self, alias, **kwargs):
    time, value = self.get_signal(alias, **kwargs)
    unit = self.get_unit(alias)
    return time, value, unit

  def get_all_values(self, **kwargs):
    values = self.get_values(self, **kwargs)
    return values

  def get_values(self, aliases, **kwargs):
    values = OrderedDict((alias, self.get_value(alias, **kwargs))
                         for alias in aliases)
    return values

  def get_value(self, alias, **kwargs):
    value = self._values[alias]
    if 'ScaleTime' in kwargs:
      time, value = rescale(self._time, value, **kwargs)
    return value

  def get_all_times(self):
    times = self.get_times(self)
    return times

  def get_times(self, aliass):
    times = [self._time for alias in aliass]
    return times

  def get_time(self, alias):
    return self._time

  def select_time_scale(self):
    return self._time

  def get_conversion_rule(self, alias):
    return {}

  def get_unit(self, alias):
    return ''
