import collections

class OrderedSet(collections.MutableSet):
  """
  Set that remembers original insertion order
  
  Source:
  http://code.activestate.com/recipes/576694/ - referenced by:
  https://docs.python.org/2/library/collections.html - referenced by:
  http://stackoverflow.com/questions/1653970/does-python-have-an-ordered-set
  """
  
  def __init__(self, iterable=None):
    self.end = end = [] 
    end += [None, end, end]         # sentinel node for doubly linked list
    self.map = {}                   # key --> [key, prev, next]
    if iterable is not None:
        self |= iterable
    return

  def __len__(self):
    return len(self.map)

  def __contains__(self, key):
    return key in self.map

  def add(self, key):
    if key not in self.map:
      end = self.end
      curr = end[1]
      curr[2] = end[1] = self.map[key] = [key, curr, end]
    return

  def discard(self, key):
    if key in self.map:        
      key, prev, next = self.map.pop(key)
      prev[2] = next
      next[1] = prev
    return

  def __iter__(self):
    end = self.end
    curr = end[2]
    while curr is not end:
      yield curr[0]
      curr = curr[2]

  def __reversed__(self):
    end = self.end
    curr = end[1]
    while curr is not end:
      yield curr[0]
      curr = curr[1]

  def pop(self, last=True):
    if not self:
      raise KeyError('set is empty')
    key = self.end[1][0] if last else self.end[2][0]
    self.discard(key)
    return key

  def __repr__(self):
    if not self:
      return '%s()' % (self.__class__.__name__,)
    return '%s(%r)' % (self.__class__.__name__, list(self))

  def __eq__(self, other):
    if isinstance(other, OrderedSet):
      return len(self) == len(other) and list(self) == list(other)
    return set(self) == set(other)


if __name__ == '__main__':
  s = OrderedSet('abracadaba')
  t = OrderedSet('simsalabim')
  print(s | t)
  print(s & t)
  print(s - t)
