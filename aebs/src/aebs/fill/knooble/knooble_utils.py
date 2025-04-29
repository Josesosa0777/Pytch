import hashlib
import re
import logging
import os
logger = logging.getLogger("knooble_utils")
PYTCH_SUPPORTED_FILE_FORMATS = [".h5", ".mf4", ".mat"]


def getFilenameHash(file_name):
		""""This function returns the md5 hash
		of the file passed into it"""
		regex_mi5id_pattern = '\d*$'  # Split h5/rrec get wor
		rrec_regex_date_pattern = '\d{4}.\d{2}.\d{2}_at_\d{2}.\d{2}.\d{2}'
		h5_regex_date_pattern = '\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
		extracted_mi5_id, extracted_datetime = "", ""
		file_name, ext = os.path.splitext(file_name)
		if ext.lower() in PYTCH_SUPPORTED_FILE_FORMATS:
				mi5_id_string = file_name.split("__")[0]
				extracted_mi5_id = re.compile(regex_mi5id_pattern).findall(mi5_id_string)
				extracted_datetime = re.compile(h5_regex_date_pattern).findall(file_name)
				if len(extracted_mi5_id) > 1 and len(extracted_datetime) > 0:
						extracted_mi5_id = extracted_mi5_id[0]
						extracted_datetime = extracted_datetime[0]
				else:
						logger.critical("Filename {} does not match standard Pytch naming pattern".format(file_name))
						return False
		elif ext.lower() == '.rrec':
				mi5_id_string = file_name.split("-")[-1]
				extracted_mi5_id = re.compile(regex_mi5id_pattern).findall(mi5_id_string)
				extracted_datetime = re.compile(rrec_regex_date_pattern).findall(file_name)
				if len(extracted_mi5_id) > 1 and len(extracted_datetime) > 0:
						extracted_mi5_id = extracted_mi5_id[0]
						extracted_datetime = extracted_datetime[0]
						date, time = extracted_datetime.split("_at_")
						date = date.replace(".", "-")
						time = time.replace(".", "-")
						extracted_datetime = date + "_" + time  # Pytch format
				else:
						logger.critical("Filename {} does not match standard DCNVT naming pattern".format(file_name))
						return False
		else:
				logger.critical("Skipping {}, Not supported in Knooble".format(file_name + ext))
				return False

		hash_string = extracted_mi5_id + extracted_datetime
		hash_md5 = hashlib.sha224(hash_string.lower().encode('utf-8'))
		# hash_md5 = hashlib.md5()
		# try:
		# 		with open(file_path, "rb") as f:
		# 				for chunk in iter(lambda: f.read(500000), b""):
		# 						hash_md5.update(chunk)
		# except Exception as e:
		# 		logger.critical(str(e))
		return hash_md5.hexdigest()
