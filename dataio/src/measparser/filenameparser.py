import re
from datetime import datetime, timedelta


class FileNameParser(object):
  pattern = re.compile(r"""
    (?P<base1>
      (?P<base2>
        (?P<base3>
          (?P<vehicle>.+?)            # e.g. "M1SH10"
          (__(?P<description>.+))?    # optional
        )
        _{1,2}
        (?P<date>                     # e.g. "2015-08-06_17-18-07"
          (?P<year>\d{4})-
          (?P<month>\d{2})-
          (?P<day>\d{2})[_-]
          (?P<hour>\d{2})-
          (?P<min>\d{2})-
          (?P<sec>\d{2})
        )
      )
      (_{1,2}(?P<device>.+?))?        # optional, e.g. "J1939_Channel_1"
    )
    (?P<extension>\.[^\.]+)?          # optional, e.g. ".BLF"
    $                                 # end of string
    """, re.VERBOSE)

  def __new__(cls, filename):
    if cls.pattern.search(filename) is not None:
      return object.__new__(cls, filename)
    else:
      return None

  def __init__(self, filename):
    self._filename = filename
    self._mo = self.pattern.search(filename)
    self._groups = list(self._mo.groupdict().viewkeys())
    date = self._mo.group('date')
    sep = date[10]
    self._fmt = '%Y-%m-%d' + sep + '%H-%M-%S'
    self._fmt_underscore = '%Y-%m-%d_%H-%M-%S'
    self._date_tobj = datetime.strptime(date, self._fmt)
    self._date = date
    return

  def __getattr__(self, name):
    if name in self._groups:
      return self._mo.group(name)
    else:
      raise AttributeError("'FileNameParser' object has no attribute '{}'".format(name))

  @property
  def date_tobj(self):
    return self._date_tobj

  @property
  def date_underscore(self):
    return self._date_tobj.strftime(self._fmt_underscore)

  def group(self, group_name):
    return self._mo.group(group_name)

  def timedelta(self, seconds):
    new_date_tobj = self._date_tobj + timedelta(seconds=seconds)
    new_date = new_date_tobj.strftime(self._fmt)
    new_filename = self._filename.replace(self._date, new_date)
    return new_filename

  @staticmethod
  def get_meastag(meas, tag):
    mo = FileNameParser.pattern.search(meas)
    if mo is None:
      return None
    return mo.group(tag)
