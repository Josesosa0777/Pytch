from testevalutils.data_provider import DataProvider
import numpy as np

from measproc.IntervalList import maskToIntervals
TRAFFICSIGNGROUNDTRUTHTIMESTAMP = 1644330223.55

#toDo: add 6-7 ground truth for each detection
import logging

logging.basicConfig(filename='test_4927442.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# dataProvider = DataProvider(r"C:\Users\wattamwa\Desktop\measurments\TSR_Testcases\mi5id5321__2021-09-14_20-38-50.h5")
dataProvider = DataProvider(r"D:\measurements\TSR_evaluation\tssdetected_status\mi5id787__2022-02-08_14-17-40.h5")
# signals.addSignal('EEC1_00_s00', 'EngineSpeed')
# dataProvider.showPreDefinedSignals()
# signals.showAllSignals()
engSpeedT, engSpeedV = dataProvider.signals['engspeed']
vxKmhSpeedT, vxKmhSpeedV = dataProvider.signals['vx_kmh']
tssCurrentRegionT, tssCurrentRegionV = dataProvider.signals['TSSCurrentRegion']
tssDetectedStatusT, tssDetectedStatusV = dataProvider.signals['TSSDetectedStatus']
commonTime= dataProvider.commonTime

detectionCount= 0
for indexOfSignPassed, indexOfStatusLastActive in maskToIntervals(tssDetectedStatusV ==1):
		detectionCount+=1
		logging.info("Detection {}".format(detectionCount))
		#indexOfSignPassed, indexOfStatusLastActive =maskToIntervals(tssDetectedStatusV ==1)[0]
		# indexOfSignPassed, indexOfStatusLastActive = 6648, 7668
		traveledDistanceBeforeSignPassed = 0
		indexCountAt100MeterBeforeSignPassed = 0

		logging.info("Checking final V_ego>=20kph must be reached atleast before a minimum distance of 100 meters is achieved between EGO vehicle and Traffic Sign post")
		while(traveledDistanceBeforeSignPassed<100):
				traveledDistanceBeforeSignPassed = np.trapz(vxKmhSpeedV[indexOfSignPassed - indexCountAt100MeterBeforeSignPassed:indexOfSignPassed], \
																										commonTime[indexOfSignPassed - indexCountAt100MeterBeforeSignPassed:indexOfSignPassed])
				indexCountAt100MeterBeforeSignPassed+=1

		indexToAt100MeterBeforeSignPassed= indexOfSignPassed - indexCountAt100MeterBeforeSignPassed
		# print(commonTime[indexToAt100MeterBeforeSignPassed])
		logging.info("v_ego:"+str(vxKmhSpeedV[indexToAt100MeterBeforeSignPassed]))
		logging.info(vxKmhSpeedV[indexToAt100MeterBeforeSignPassed] >= 20)
		logging.info(engSpeedV[indexToAt100MeterBeforeSignPassed] >= 500)

		logging.info("TssDetsctionStatus value must be zero before Ego at distance 100 meter from Traffic Sign Post:")
		assert tssDetectedStatusV[indexToAt100MeterBeforeSignPassed]==0," TSSDetectedStatus = 1, before approaching the Traffic Sign."
		logging.info(tssDetectedStatusV[indexToAt100MeterBeforeSignPassed]==0)

		logging.info("TssDetsctionStatus value must be one after Ego crossing Traffic Sign Post:")
		logging.info(tssDetectedStatusV[indexOfSignPassed:indexOfStatusLastActive])

		logging.info("TssCurrentRegion value must be some country code after Ego crossing Traffic Sign Post:")
		logging.info(tssCurrentRegionV[indexOfSignPassed:indexOfStatusLastActive])

		logging.info("Checking if TssDetectedStatus active after crossing  GroundTruth detection :")
		logging.info(tssDetectedStatusT[indexOfSignPassed]>TRAFFICSIGNGROUNDTRUTHTIMESTAMP)

		logging.info("Checking if TssDetectedStatus is all 0 before time of crossing Traffic Sign Post within 100meter distance:")
		logging.info(np.all(tssDetectedStatusV[indexToAt100MeterBeforeSignPassed:indexOfSignPassed]==0))

		logging.info("===================================================================================================")
		#toDo: print plot,image where grounthTruth detected,ROI for detection




