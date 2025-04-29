import csv
import math
import sys, getopt
import numpy as np
from measparser.SignalSource import findParser, cSignalSource
from scipy import signal

def resultToCSV(inputmeasurement, inputcsv,header,outputcsv,threshold):
		with open(inputcsv, 'r') as fin:
				reader = csv.reader(fin, delimiter='\t')
				Parser = findParser(inputmeasurement)
				parser = Parser(inputmeasurement)
				with open( outputcsv,'w') as fout:
						writer = csv.writer(fout, delimiter='\t')
						writer.writerow(header)
						for row in reader:
								field = row[0].split(",")
								try:
										arsvalue_temp, arstimekey_temp = parser.getSignal(field[0], field[1])
										arstimevalue_temp = parser.getTime(arstimekey_temp)

										mfcvalue, mfctimekey = parser.getSignal(field[2],field[3])
										mfctimevalue = parser.getTime(mfctimekey)

								except KeyError:
										print(
												"Can't gather information about signals. \nPlease check if DeviceNames and SignalNames are correct "
												"and available in measurement")
										return

								arstimevalue, arsvalue = cSignalSource.rescale(arstimevalue_temp, arsvalue_temp, mfctimevalue)
								#Considering precision loss conversion situation

								precision_conversion = ((((arsvalue - float(field[4])) / float(field[5])) + 0.5))
								arsvalue_actual = (precision_conversion * float(field[5])) + float(field[4])

								if (np.all(mfcvalue==0) & np.all(arsvalue==0) ) :
										new_value = ",PASS"
										row.append(new_value)
										writer.writerow(row)
								elif  (np.all(np.abs(np.subtract(arsvalue_actual,mfcvalue))<=0.1)):
										new_value = ",PASS"
										row.append(new_value)
										writer.writerow(row)
								else:
										lag = get_max_correlation(mfcvalue,arsvalue)
										if ((lag>=-threshold) & (lag<=threshold)) :
												new_value = ",PASS"
												row.append(new_value)
												writer.writerow(row)
										else:
												new_value = ",FAIL"
												row.append(new_value)
												writer.writerow(row)

				fout.close()
		fin.close()
		print(" Verdicts are updated in %s" %outputcsv)

def get_max_correlation(original, match):
		z = signal.fftconvolve(original, match[::-1], mode = "full")
		lags = np.arange(z.size) - (match.size - 1)
		max_lag = lags[np.argmax(np.abs(z))]
		return max_lag

def main(argv):
		measurement  = ""
		inputfile = ''
		outputfile = ''
		max_lag_threshold = 0
		header =[]
		try:
			opts, args = getopt.getopt(argv,"r:i:c:o:t:")
		except getopt.GetoptError:
			print ('python -m compare_signals -r <measurementname> -i <inputcsv> -c <headerincommaseperatedstring> -o <outputcsv> -t <thresholdvalue>')
			sys.exit(2)
		for opt, arg in opts:
				if opt in ("-h"):
						print("python -m compare_signals -r <measurementname> -i <inputcsv> -c <headerincommaseperatedstring> -o <outputcsv> -t <thresholdvalue>")
						sys.exit(0)
				if opt in ("-i", "--icsv"):
						inputfile = arg
				elif opt in ("-o", "--ocsv"):
						outputfile = arg
				elif opt in ("-r", "--meas"):
						measurement = arg
				elif opt in ("-c", "--header"):
						header = [arg.lstrip("[").rstrip("]")]
				elif opt in ("-t", "--lag"):
						max_lag_threshold = int(arg)

		resultToCSV(measurement, inputfile, header, outputfile, max_lag_threshold)
if __name__ == "__main__":
		main(sys.argv[1:])



#python -m compare_signals -r "C:\Users\wattamwa\Desktop\measurments\DI-Retest\new\mi5id787__2022-01-20_13-17-30.mat" -i "C:\Users\wattamwa\Desktop\FusionList.csv" -c [ARS-Devices,ARS-Signals,MFC_Devices,MFC-Signals,Offset,Factor,Verdict] -o  "C:\Users\wattamwa\Desktop\FusionListOutput.csv" -t "5"
# -r "C:\Users\wattamwa\Desktop\measurments\DI-Retest\back_to_back_test\ars_road_inc\mi5id787__2022-02-08_14-27-43.h5" -i "C:\Users\wattamwa\Desktop\measurments\DI-Retest\back_to_back_test\ars_road_inc\FusionListInput.csv" -c [ARS-Devices,ARS-Signals,MFC_Devices,MFC-Signals,Offset,Factor,Verdict] -o "C:\Users\wattamwa\Desktop\measurments\DI-Retest\back_to_back_test\ars_road_inc\FusionListOutput.csv" -t "5"