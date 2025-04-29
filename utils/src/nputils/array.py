from collections import OrderedDict

import numpy as np
import scipy.io as spio


def recarray_to_dict(a, dict_cls=OrderedDict):
  " put arbitrary-level nested numpy record array into dict "
  if a.dtype.fields is None:
    return a
  d = dict_cls()
  for name in a.dtype.names:
    d[name] = recarray_to_dict( a[name], dict_cls=dict_cls )
  return d

def dict_to_recarray(d):
  """ put arbitrary-level nested dictionary (with field names as keys
  and 1-D numpy arrays of the same size as values) into record array
  http://stackoverflow.com/a/32336904/3275557
  """
  size = [None] # workaround closure problem with recursive functions, see http://stackoverflow.com/a/2516870/3275557
  def create_dtype(d):
    " traverse nested dict and create dtype for structured array "
    l = []
    for k,v in d.iteritems():
      if isinstance(v,np.ndarray):
        l.append((k,v.dtype))
        if size[0] is None:
          size[0] = v.size
        else:
          assert v.size == size[0]
      else:
        l.append((k,create_dtype(v)))
    return l
  def copy_values(v, a):
    " copy values from nested dict to structured array "
    if a.dtype.names:
      for n in a.dtype.names:
        copy_values(v[n], a[n])
    else:
      a[:] = v
  # create dtype
  dtype = create_dtype(d)
  # create empty placeholder array
  arr = np.empty(size[0], dtype=dtype)
  # copy values to array
  copy_values(d, arr)
  # return with record array
  return arr.view(np.recarray)


class recarrayview(np.ndarray):
  """ get a view on a numpy record array, instead of creating a copy

  usage: instead of
    arr_copy = arr[ ['x', 'y'] ]
  use
    arr_view = recarrayview(arr, ('x', 'y'))

  http://stackoverflow.com/a/11815517/3275557
  """
  def __new__(subtype, x, fields):
    dtype = {f: x.dtype.fields[f] for f in fields}
    return np.ndarray.__new__(subtype, x.shape, dtype,
                              buffer=x, strides=x.strides)

def loadmat(filename):
  '''
  this function should be called instead of direct spio.loadmat
  as it cures the problem of not properly recovering python dictionaries
  from mat files. It calls the function check keys to cure all entries
  which are still mat-objects

  modified based on http://stackoverflow.com/a/29126361/3275557
  '''
  data = spio.loadmat(filename, struct_as_record=False, squeeze_me=True)
  return _check_keys(data)

def _check_keys(dict):
  '''
  checks if entries in dictionary are mat-objects. If yes
  todict is called to change them to nested dictionaries
  '''
  for key in dict:
    if isinstance(dict[key], spio.matlab.mio5_params.mat_struct):
      dict[key] = _todict(dict[key])
  return dict

def _todict(matobj):
  '''
  A recursive function which constructs from matobjects nested dictionaries
  '''
  dict = {}
  for strg in matobj._fieldnames:
    elem = matobj.__dict__[strg]
    if isinstance(elem, spio.matlab.mio5_params.mat_struct):
      dict[strg] = _todict(elem)
    elif isinstance(elem,np.ndarray) and elem.dtype == np.object:
      dict[strg] = _tolist(elem)
    else:
      dict[strg] = elem
  return dict

def _tolist(ndarray):
  '''
  A recursive function which constructs lists from cellarrays
  (which are loaded as numpy ndarrays), recursing into the elements
  if they contain matobjects.
  '''
  elem_list = []
  for sub_elem in ndarray:
    if isinstance(sub_elem, spio.matlab.mio5_params.mat_struct):
      elem_list.append(_todict(sub_elem))
    elif isinstance(sub_elem,np.ndarray) and sub_elem.dtype == np.object:
      elem_list.append(_tolist(sub_elem))
    else:
      elem_list.append(sub_elem)
  return elem_list
