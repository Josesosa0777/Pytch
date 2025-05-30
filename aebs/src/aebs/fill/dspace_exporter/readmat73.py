import os
import numpy as np
import h5py
import logging
try:
	from typing import Iterable
except:
		pass



def empty(*dims):
		if len(dims) == 1:
				return [[] for x in range(dims[0])]
		else:
				return [empty(*dims[1:]) for _ in range(dims[0])]


class AttrDict(dict):
		def __init__(self, *args, **kwargs):
				super(AttrDict, self).__init__(*args, **kwargs)

		def __getattr__(self, key):
				"""this prevents that built-in functions are overwritten"""
				if key == '__getstate__':
						raise AttributeError(key)
				if key in dir(dict):
						return dict.__getattr__(self, key)
				else:
						return self.__getitem__(key)

		def __setattr__(self, key, value):
				return self.__setitem__(key, value)


def print_tree(node):
		if node.startswith('#refs#/') or node.startswith('#subsystem#/'):
				return
		print(' ', node)


class HDF5Decoder():
		def __init__(self, verbose = True, use_attrdict = False,
		             only_include = None):

				if isinstance(only_include, str):
						only_include = [only_include]
				if only_include is not None:
						only_include = [s if s[0] == '/' else '/{}'.format(s) for s in only_include]
						only_include = [s[:-1] if s[-1] == '/' else s for s in only_include]
				self.verbose = verbose
				self._dict_class = AttrDict if use_attrdict else dict
				self.refs = {}  # this is used in case of matlab matrices
				self.only_include = only_include
				if only_include is not None:
						_vardict = dict(zip(only_include, [False] * len(only_include)))
						self._found_include_var = _vardict

		def is_included(self, hdf5):
				# if only_include is not specified, we always return True
				# because we load everything
				if self.only_include is None:
						return True
				# see if the current name is in any of the included variables
				for s in self.only_include:
						if s in hdf5.name:
								self._found_include_var[s] = True
						if s in hdf5.name or hdf5.name in s:
								return True
				return False

		def mat2dict(self, hdf5):

				if '#refs#' in hdf5:
						self.refs = hdf5['#refs#']
				d = self._dict_class()
				for var in hdf5:
						# this first loop is just here to catch the refs and subsystem vars
						if var in ['#refs#', '#subsystem#']:
								continue

						if not self.is_included(hdf5[var]):
								continue
						d[var] = self.unpack_mat(hdf5[var])

				if self.only_include is not None:
						for var, found in self._found_include_var.items():
								if not found:
										pass
						if not any(list(self._found_include_var.values())):
								print(hdf5.filename, 'contains the following vars:')
								hdf5.visit(print_tree)
				return d

		# @profile
		def unpack_mat(self, hdf5, depth = 0, MATLAB_class = None):
				"""
				unpack a h5py entry: if it's a group expand,
				if it's a dataset convert

				for safety reasons, the depth cannot be larger than 99
				"""
				if depth == 99:
						pass
				if isinstance(hdf5, (h5py._hl.group.Group)):
						d = self._dict_class()

						for key in hdf5:
								elem = hdf5[key]
								if not self.is_included(elem):
										continue
								if 'MATLAB_class' in elem.attrs:
										MATLAB_class = elem.attrs.get('MATLAB_class')
										if MATLAB_class is not None:
												MATLAB_class = MATLAB_class.decode()
								unpacked = self.unpack_mat(elem, depth = depth + 1,
								                           MATLAB_class = MATLAB_class)
								if MATLAB_class == 'struct' and len(elem) > 1 and \
												isinstance(unpacked, dict):
										values = unpacked.values()
										# we can only pack them together in MATLAB style if
										# all subitems are the same lengths.
										# MATLAB is a bit confusing here, and I hope this is
										# correct. see https://github.com/skjerns/mat7.3/issues/6
										allist = all([isinstance(item, list) for item in values])
										if allist:
												same_len = len(set([len(item) for item in values])) == 1
										else:
												same_len = False

										# convert struct to its proper form as in MATLAB
										# i.e. struct[0]['key'] will access the elements
										# we only recreate the MATLAB style struct
										# if all the subelements have the same length
										# and are of type list
										if allist and same_len:
												items = list(zip(*[v for v in values]))

												keys = unpacked.keys()
												struct = [{k: v for v, k in zip(row, keys)} for row in items]
												struct = [self._dict_class(d) for d in struct]
												unpacked = struct
								d[key] = unpacked

						return d
				elif isinstance(hdf5, h5py._hl.dataset.Dataset):
						if self.is_included(hdf5):
								return self.convert_mat(hdf5, depth, MATLAB_class = MATLAB_class)
				else:
						pass

		# @profile
		def _has_refs(self, dataset):
				if len(dataset.shape) < 2:
						return False
				# dataset[0].
				dataset[0][0]
				if isinstance(dataset[0][0], h5py.h5r.Reference):
						return True
				return False

		# @profile
		def convert_mat(self, dataset, depth, MATLAB_class = None):
				"""
				Converts h5py.dataset into python native datatypes
				according to the matlab class annotation
				"""
				# all MATLAB variables have the attribute MATLAB_class
				# if this is not present, it is not convertible
				if MATLAB_class is None and 'MATLAB_class' in dataset.attrs:
						MATLAB_class = dataset.attrs['MATLAB_class'].decode()

				if not MATLAB_class and not self._has_refs(dataset):
						if self.verbose:
								message = 'ERROR: not a MATLAB datatype: ' + \
								          '{}, ({})'.format(dataset, dataset.dtype)
								logging.error(message)
						return None

				# if has
				known_cls = ['cell', 'char', 'bool', 'logical', 'double', 'single',
				             'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16',
				             'uint32', 'uint64']

				if 'MATLAB_empty' in dataset.attrs.keys() and \
								MATLAB_class in ['cell', 'struct']:
						mtype = 'empty'
				elif MATLAB_class in known_cls:
						mtype = MATLAB_class
				elif self._has_refs(dataset):
						mtype = 'cell'
				else:
						mtype = MATLAB_class

				if mtype == 'cell':
						cell = []
						for ref in dataset:
								row = []
								# some weird style MATLAB have no refs, but direct floats or int
								if isinstance(ref, Iterable):
										for r in ref:
												entry = self.unpack_mat(self.refs.get(r), depth + 1)
												row.append(entry)
								else:
										row = [ref]
								cell.append(row)
						cell = list(map(list, zip(*cell)))  # transpose cell
						if len(cell) == 1:  # singular cells are interpreted as int/float
								cell = cell[0]
						return cell

				elif mtype == 'empty':
						dims = [x for x in dataset]
						return empty(*dims)

				elif mtype == 'char':
						string_array = np.ravel(dataset)
						string_array = ''.join([chr(x) for x in string_array])
						string_array = string_array.replace('\x00', '')
						return string_array

				elif mtype == 'bool':
						return bool(dataset)

				elif mtype == 'logical':
						arr = np.array(dataset, dtype = bool).T.squeeze()
						if arr.size == 1:
								arr = bool(arr)
						return arr

				elif mtype == 'canonical empty':
						return None

				# complex numbers need to be filtered out separately
				elif 'imag' in str(dataset.dtype):
						if dataset.attrs['MATLAB_class'] == b'single':
								dtype = np.complex64
						else:
								dtype = np.complex128
						arr = np.array(dataset)
						arr = (arr['real'] + arr['imag'] * 1j).astype(dtype)
						return arr.T.squeeze()

				# if it is none of the above, we can convert to numpy array
				elif mtype in ('double', 'single', 'int8', 'int16', 'int32', 'int64',
				               'uint8', 'uint16', 'uint32', 'uint64'):
						arr = np.array(dataset, dtype = dataset.dtype)
						return arr.T.squeeze()
				elif mtype == 'missing':
						arr = None
				else:
						if self.verbose:
								message = 'ERROR: MATLAB type not supported: ' + \
								          '{}, ({})'.format(mtype, dataset.dtype)
								logging.error(message)
						return None


def loadmat(filename, use_attrdict = False, only_include = None, verbose = True):
		"""
		Loads a MATLAB 7.3 .mat file, which is actually a
		HDF5 file with some custom matlab annotations inside

		:param filename: A string pointing to the file
		:param use_attrdict: make it possible to access structs like in MATLAB
												 using struct.varname instead of struct['varname']
												 WARNING: builtin dict functions cannot be overwritten,
												 e.g. keys(), pop(), ...
												 these will still be available by struct['keys']
		:param verbose: print warnings
		:param only_include: A list of HDF5 paths that should be loaded.
												 this can greatly reduce loading times. If a path
												 contains further sub datasets, these will be loaded
												 as well, e.g. 'struct/' will load all subvars of
												 struct, 'struct/var' will load only ['struct']['var']
		:returns: A dictionary with the matlab variables loaded
		"""
		assert os.path.isfile(filename), '{} does not exist'.format(filename)
		decoder = HDF5Decoder(verbose = verbose, use_attrdict = use_attrdict,
		                      only_include = only_include)

		ext = os.path.splitext(filename)[1].lower()
		if ext != '.mat':
				pass
		try:
				with h5py.File(filename, 'r') as hdf5:
						dictionary = decoder.mat2dict(hdf5)
				return dictionary
		except OSError:
				raise TypeError('{} is not a MATLAB 7.3 file. ' \
				                'Load with scipy.io.loadmat() instead.'.format(filename))


def savemat(filename, verbose = True):
		raise NotImplementedError


if __name__ == '__main__':
		# d = loadmat('../tests/testfile5.mat', use_attrdict=True)

		file = r"C:\KBData\__PythonToolchain\Development\dSpaceResim\rec1_006.mat"
		data = loadmat(file)
		print(data)