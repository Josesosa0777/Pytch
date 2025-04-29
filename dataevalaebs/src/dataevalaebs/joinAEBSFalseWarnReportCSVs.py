import csv
import sys
import os
import fnmatch
import numpy

try:
  filedir = sys.argv[1] # command line parameter should be the location of the folder containing CSV files (the resulting txt file will also be placed here)
except IndexError:
  print 'Please give command line parameter indicating the full path of the folder containing the CSV files.'
  print 'NOTE: Location of the resulting joint CSV file will be in that folder directory.'
  exit()

jointCSVName = 'OverallReportStat.csv'

jointCSVFileHeader = []
jointCSVFileRows = []

if os.path.exists(os.path.join(filedir, jointCSVName)):
  os.remove(os.path.join(filedir, jointCSVName))

csvFilesReadIn = {}
csvHeaderLengths = {}
csvRowLengthsConsistent = {}
for root, dirs, filenames in os.walk(filedir):
  for filename in sorted(filenames):
    if fnmatch.fnmatch(filename, '*.csv'):
      csvFile = open(os.path.join(root, filename), 'rb')
      dialect = csv.Sniffer().sniff(csvFile.read(1024))
      csvFile.seek(0)
      inputCSV = csv.reader(csvFile, dialect)
      csvFilesReadIn[filename] = inputCSV
      
      rowLengths = []
      for rowNum, row in enumerate(inputCSV):
        rowLengths.append(len(row))
        if rowNum == 0:
          csvHeaderLengths[filename] = len(row)
      
      if numpy.any(numpy.diff(rowLengths) == 0):
        csvRowLengthsConsistent[filename] = True
      else:
        csvRowLengthsConsistent[filename] = False

csvHeaderLength = numpy.argmax(numpy.bincount(csvHeaderLengths.values())) # only files having header length with the highest occurrence will be joined

for filename in csvFilesReadIn.keys():
  if len(csvFilesReadIn[filename][0]) == csvHeaderLength and csvRowLengthsConsistent[filename]:
    for rowNum, row in enumerate(csvFilesReadIn[filename]):
      date = os.path.splitext(filename)[0]
      if rowNum == 0 and len(jointCSVFileHeader) == 0:
        jointCSVFileHeader = row.insert(0, "Date")
      elif rowNum == 0:
        pass
      else:
        jointCSVFileRows.append(row.insert(0, date))
  else:
    if len(csvFilesReadIn[filename][0]) == csvHeaderLength:
      reason = "header length mismatch"
    elif csvRowLengthsConsistent[filename] == False:
      reason = "inconsistent row length"
    print >> sys.stderr, "The file %s cannot be joined with the others! Reason: %s" %(filename, reason)

jointCSVFileRows.insert(0, jointCSVFileHeader)

outputCSV = csv.writer(open(os.path.join(filedir, jointCSVName), 'wb'), delimiter=':', lineterminator='\n')
outputCSV.writerows(jointCSVFileRows)

