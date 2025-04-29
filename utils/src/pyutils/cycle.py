from collections import deque

class BiCycle(object):
  "Bidirectional cycle iterator"
  def __init__(self, iterable, start=0):
    self._data = deque(iterable)
    self._data.rotate(-start)
    return

  def current(self):
    return self._data[0]

  def next(self, steps=1):
    self._data.rotate(-steps)
    return self.current()

  def prev(self, steps=1):
    self._data.rotate(steps)
    return self.current()

  def __iter__(self):
    return self
