import cPickle as pickle
import gzip
import os
import logging
from os.path import expanduser

home = expanduser("~")
modules_cache_storage = {}
logger = logging.getLogger('cache_manager')

def store_modules_cache(source, script_name, data):
		"""
		Stores prepared data to disk in pickle format
		:param source:
			Source file object
		:param script_name:
			Script name, result of which will be stored in cache
			e.g.  fill_flc25_polylines@aebs.fill
		:param data:
			data dictionary to be stored in cache
		:return:
		"""
		if (script_name, source.MeasHash) not in modules_cache_storage.keys():
				cache_data = {}
				cache_data["data"] = data
				cache_data["hash"] = source.MeasHash
				modules_cache_storage[(script_name, source.MeasHash)] = data
				directory_path = os.path.join(home, ".aebs")
				directory_path = os.path.join(directory_path, "modules_cache")
				if not os.path.isdir(directory_path):
						os.mkdir(directory_path)

				measurement_filename = os.path.splitext(source.BaseName)[0]
				processed_directory_name = measurement_filename + "_processed"

				directory_path = os.path.join(directory_path, processed_directory_name)
				if not os.path.isdir(directory_path):
						os.mkdir(directory_path)

				tmp_pickle_file_name = os.path.join(directory_path, script_name + "_InProgress.pickle")
				final_pickle_file_name = os.path.join(directory_path, script_name + ".pickle")
				# Clean any existing final pickle before, renaming final will not be allowed if its already exists
				if os.path.exists(final_pickle_file_name):
						os.remove(final_pickle_file_name)
				pickle_file_handle = gzip.GzipFile(tmp_pickle_file_name, 'w')
				pickle.dump(cache_data, pickle_file_handle)
				pickle_file_handle.close()
				try:
						os.rename(tmp_pickle_file_name, final_pickle_file_name)
				except:
						pass


def get_modules_cache(source, script_name):
		"""
		Gets script data from RAM if exists else fetches from disk cache(stored in .pickle)
		:param source:
			Source file objects
		:param script_name:
			Script name, result data of which will be fetched from cache
			e.g.  fill_flc25_polylines@aebs.fill
		:return:
			cache data of the script
			None: if the required data(checked against hash of meas) is not available in the cache
		"""
		if (script_name, source.MeasHash) not in modules_cache_storage.keys():
				pickle_file_name = get_modules_cache_file_path(source, script_name)
				if os.path.exists(pickle_file_name):
						cache_data = pickle.load(gzip.GzipFile(pickle_file_name, "rb"))
						if source.MeasHash == cache_data["hash"]:
								modules_cache_storage[(script_name, source.MeasHash)] = cache_data["data"]
						else:
								logger.info("Hash value of measurement {} in the script {} did not match with the stored cache. Cleaning the cache.".format(source.FileName, script_name))
								os.remove(pickle_file_name)
								return None
				else:
						return None
		return modules_cache_storage[(script_name, source.MeasHash)]


def is_modules_cache_available(source, script_name):
		"""
		Check if the cache available for the given script
		:param source:
			Source file objects
		:param script_name:
			Script name, result data of which will be fetched from cache
			e.g.  fill_flc25_polylines@aebs.fill
		:return:
			True: If local cache available eighter in RAM or in the disk storage
			False: Cache miss
		"""
		if (script_name, source.MeasHash) not in modules_cache_storage.keys():
				pickle_file_name = get_modules_cache_file_path(source, script_name)
				if os.path.exists(pickle_file_name):
						return True
				else:
						return False
		else:
				return True


def get_modules_cache_file_path(source, script_name):
		directory_path = os.path.join(home, ".aebs/modules_cache")
		measurement_filename = os.path.splitext(source.BaseName)[0]
		processed_directory_name = measurement_filename + "_processed"
		processed_directory_path = os.path.join(directory_path, processed_directory_name)
		pickle_file_name = os.path.join(processed_directory_path, script_name + ".pickle")
		return pickle_file_name


# =============================== Mat parser local caching ====================================
def store_meas_cache(source, data):
		modules_cache_storage[source] = data


def get_meas_cache(source):
		return modules_cache_storage[source]


def is_meas_cache_available(source):
		if source not in modules_cache_storage.keys():
				return False
		else:
				return True
