import os
import glob

from measparser.SignalSource import cSignalSource
from measparser.iParser import iParser
from measproc.IntervalList import findBounds

class BaseConv(object):
  def __init__(self, meas_root, meas_dir, time_dev, time_sig):
    self.meas_root = meas_root
    self.meas_dir = os.path.join(meas_root, meas_dir)
    self.time_dev = time_dev
    self.time_sig = time_sig
    self._basenames = {}
    "{ basename<str> : (fullname<str>, time<ndarray> [,value<ndarray>]) }"
    return

  def get_intervals(self, basename, start, end):
    """
    :Parameters:
      basename : str
        Measurement basename
      start : int or float
        Interval start
      end : int or float
        Interval end
    :ReturnType: list
    :Return: [ (fullname<str>, time<ndarray>, start<int>, end<int>), ]
    """
    raise NotImplementedError()

  def get_unique_measname(self, basename):
    fullnames = glob.glob( os.path.join(self.meas_dir, basename) )
    assert fullnames, 'No measurement found for basename "%s" under "%s"'\
                      %(basename, self.meas_dir)
    assert len(fullnames) < 2, 'Multiple measurements found for basename '\
                               ' "%s" under "%s"' %(basename, self.meas_dir)
    fullname, = fullnames
    return fullname

  def get_time(self, source):
    dev = source.getUniqueName(self.time_sig, self.time_dev, FavorMatch=True)
    time = source.getTime( source.getTimeKey(dev, self.time_sig) )
    return time

  def get_signal(self, source):
    dev = source.getUniqueName(self.time_sig, self.time_dev, FavorMatch=True)
    time, value = source.getSignal(dev, self.time_sig)
    return time, value


class KbtoolsConv(BaseConv):
  def get_intervals(self, basename, t_start, t_dura):
    if basename in self._basenames:
      fullname, time = self._basenames[basename]
    else:
      fullname = self.get_unique_measname(basename)
      source = cSignalSource(fullname)
      time = self.get_time(source)
      source.save()
      self._basenames[basename] = fullname, time
    start, end = findBounds(time, t_start, t_start+t_dura)
    intervals = [(fullname, time, start, end), ]
    return intervals


class EyeqConv(BaseConv):
  def __init__(self, meas_root, meas_dir, time_dev, time_sig, extension):
    BaseConv.__init__(self, meas_root, meas_dir, time_dev, time_sig)
    self.extension = extension
    return

  def get_intervals(self, video_basename, frame_start, frame_end, max_steps=5):
    intervals = []
    frame_start, frame_end = int(frame_start), int(frame_end) # cast for safety
    d = iParser.getStartDateFromFileName(video_basename)
    meas_date = d.strftime('%Y-%m-%d')
    meas_glob = os.path.join(self.meas_root, meas_date, self.extension)
    fullnames = glob.glob(meas_glob)
    dates = [iParser.getStartDateFromFileName(e) for e in fullnames]
    indices = [idx for idx,date in enumerate(dates) if d < date]
    first_idx = max(0, indices[0] - 1)
    for fullname in fullnames[first_idx:first_idx+max_steps]:
      basename = os.path.basename(fullname)
      if basename in self._basenames:
        _, time, frames = self._basenames[basename]
      else:
        source = cSignalSource(fullname)
        time, frames = self.get_signal(source)
        source.save()
        self._basenames[basename] = fullname, time, frames
      try:
        start, end = findBounds(frames, frame_start, frame_end)
      except AssertionError:
        pass
      else:
        intervals.append( (fullname, time, start, end) )
    return intervals
