import scipy.io
import numpy as np
import os

from aebs.fill.dspace_exporter.readmat73 import loadmat

BUFFER_SIZE = 100
# TODO re-define entire logic while debugging matlab script
def get_absolute_distaces(controldesk_mat_file_path, pytchOutputFolder):
		# Loading the fused data
		controldesk_matfile_obj = loadmat(controldesk_mat_file_path)
		if controldesk_matfile_obj:
				mat_file_path = os.path.splitext(os.path.basename(controldesk_mat_file_path))[0]
				controldesk_matfile_obj = controldesk_matfile_obj[mat_file_path]
		end = controldesk_matfile_obj['Y'][0]['Data'].size

		FellowDistance_orig_4 = {}  # ModelDesk table vectors, all detections separated (each detection correpsponds
		# to a fellow)
		FellowLateralOffset_orig_4 = {}
		ASMTime_4 = {}
		SegmentTimeLength_4 = {}
		signal_present_4 = {}  # Time stamps where detection is present, separated
		FellowType_4 = {}

		Delay_4 = {}
		Delay_44 = {}

		BUFFER_ROW_SIZE = (len(controldesk_matfile_obj["Y"]) - 2) / 2
		BUFFER_COL_SIZE = controldesk_matfile_obj['Y'][0]['Data'][107:].size
		FILTERED_BUFFER_ROW_SIZE = 0
		for nnn in range(BUFFER_ROW_SIZE + 1):
				if np.count_nonzero(controldesk_matfile_obj["Y"][nnn]["Data"]) != 0:
						FILTERED_BUFFER_ROW_SIZE += 1

		ASMTime_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		FellowLateralOffset_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		FellowDistance_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])
		ModelDeskType_orig = np.zeros(shape = [FILTERED_BUFFER_ROW_SIZE, BUFFER_COL_SIZE])

		# Movement data of the fellow vehicles
		for nnn in range(BUFFER_ROW_SIZE):
				if np.count_nonzero(controldesk_matfile_obj["Y"][nnn]["Data"]) != 0:
						ASMTime_orig[nnn, :] = controldesk_matfile_obj['Y'][len(controldesk_matfile_obj['Y'])-1]['Data'][107:end]
						FellowLateralOffset_orig[nnn, :] = controldesk_matfile_obj['Y'][nnn]['Data'][107:end]
						FellowDistance_orig[nnn, :] = controldesk_matfile_obj['Y'][nnn + BUFFER_ROW_SIZE]['Data'][107:end]

		ASMTime = ASMTime_orig
		# Generating the new array of the fellow vehicle order
		nn = 0
		time_unit = 52.98 / len(controldesk_matfile_obj['Y'][len(controldesk_matfile_obj['Y']) - 1]['Data'])
		FellowOrder = np.zeros(len(FellowDistance_orig)-1)


		for ii in range(FILTERED_BUFFER_ROW_SIZE):
				mm = 0
				# nn = 1; needed for FellowDistance_orig_4_struct...
				mlast = 0
				END_COUNT = len(FellowDistance_orig[ii, :])  # TODO can be taken out of loop
				# Generating cell arrays containing all detections separated
				if FellowDistance_orig[ii][0] != 0:  # Fellow Object detected from begining of interval
						mfirst = 0
						while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
								mm = mm + 1
						mlast = mm
						FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
						FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
						ASMTime_4[nn] = ASMTime_orig[0, 0:mm - mfirst + 1] #np.ndarray.flatten(ASMTime_orig, 1)[0:mm - mfirst + 1]
						# Delay_4[nn] = 0
						SegmentTimeLength_4[nn] = mm * time_unit
						Delay_44[nn] = 0
						signal_present_4[nn] = range(mfirst, mlast, 1)
						# FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
						FellowType_4[nn] = 1
						FellowOrder[ii] = FellowOrder[ii] + 1
						mm = mm + 1
						nn = nn + 1

				while mm < END_COUNT - 1:
						if FellowDistance_orig[ii][mm] == 0 and FellowDistance_orig[ii][mm + 1] != 0:
								# TODO  ii
								mfirst = mm + 1
								while (mm < END_COUNT - 1) and (FellowDistance_orig[ii][mm + 1] != 0):
										mm = mm + 1
								Delay_44[nn] = (mfirst-mlast) * time_unit
								mlast = mm
								FellowDistance_orig_4[nn] = FellowDistance_orig[ii][mfirst:mlast]
								FellowLateralOffset_orig_4[nn] = FellowLateralOffset_orig[ii][mfirst:mlast]
								ASMTime_4[nn] = ASMTime_orig[0, 0:mm - mfirst + 1] #np.ndarray.flatten(ASMTime, 1)[0:mm - mfirst + 1]

								SegmentTimeLength_4[nn] = (mlast - mfirst) * time_unit
								signal_present_4[nn] = range(mfirst, mlast, 1)
								# FellowType_4[nn] = np.bincount(np.array(ModelDeskType_orig[ii][mfirst:mm], dtype = int)).argmax()
								FellowType_4[nn] = 1
								FellowOrder[ii] = FellowOrder[ii] + 1
								mm = mm + 1
								nn = nn + 1
						else:
								mm = mm + 1

		# Exporting the ModelDesk table of the fellow vehicles to a MAT file
		for nnn in range(0, len(ASMTime_4.keys())):
				ASMTime = ASMTime_4[nnn]
				FellowDistance = FellowDistance_orig_4[nnn]
				FellowLateralOffset = FellowLateralOffset_orig_4[nnn]
				FellowDict = {}
				if len(FellowDistance) < len(ASMTime):
						ASMTime = ASMTime[1:]
				FellowDict['ASMTime'] = ASMTime
				FellowDict['FellowPosition'] = FellowDistance
				FellowDict['FellowLateralOffset'] = FellowLateralOffset
				FelloMovementName = "FellowMovement" + str(nnn) + ".mat"
				scipy.io.savemat(os.path.join(pytchOutputFolder, FelloMovementName), FellowDict)

		fileID_6 = open(os.path.join(pytchOutputFolder, 'FellowOrder.txt'), 'w')
		for element in FellowOrder:
				fileID_6.write('{}\n'.format(int(element)))
		fileID_6.close()

		fileID_6 = open(os.path.join(pytchOutputFolder, 'SegmentTimeLength_4.txt'), 'w')
		for element in SegmentTimeLength_4.values():
				fileID_6.write('{}\n'.format(element))
		fileID_6.close()

		fileID_6 = open(os.path.join(pytchOutputFolder, 'Delay_MD.txt'), 'w')
		for element in Delay_44.values():
				fileID_6.write('{}\n'.format(element))
		fileID_6.close()


if __name__ == "__main__":
		controldesk_mat_file_path = "C:\KBData\exp1_.mat"
		pytchOutputFolder = r"E:\TCI_Akshata\output\controldesk"
		get_absolute_distaces(controldesk_mat_file_path, pytchOutputFolder)