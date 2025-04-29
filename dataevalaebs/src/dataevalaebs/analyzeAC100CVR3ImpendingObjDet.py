import os
import csv
import interface

class cParameter(interface.iParameter):
  def __init__(self, SearchSign,
               SearchClass='dataevalaebs.searchAC100CVR3ImpendingObjDet.cSearch'):
    self.SearchSign = SearchSign
    self.SearchClass = SearchClass
    self.genKeys()
    pass

# instantiation of module parameters
analyzeStationaryObjDet = cParameter('objNature=Stationary')
analyzeMovingObjDet = cParameter('objNature=Moving')

class cAnalyze(interface.iAnalyze):
  def analyze(self, Param):
    Batch = self.get_batch()
    Start = Batch.get_last_entry_start()
    EntryIds = Batch.filter(start=Start, param=Param.SearchSign,
                            class_name=Param.SearchClass, result='passed',
                            type='measproc.cFileReport')
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(EntryIds)

    if Param.SearchSign == 'objNature=Stationary':
      filename = 'UseCaseEvaluation_Stationary_OverallResults.csv'
    elif Param.SearchSign:
      filename = 'UseCaseEvaluation_Moving_OverallResults.csv'
    filename = os.path.join(Batch.dirname, filename)
    OutputCSV = csv.writer(open(filename, 'w'), delimiter=';',
                           lineterminator='\n')

    Row1 = ['']
    Row2 = ['']
    Row3 = ['Collision object']
    Row4 = ['first detected']
    Row5 = ['classified as obstacle']
    Row6 = ['warning given']

    EntryIds = Batch.filter(start=Start, param=Param.SearchSign,
                            class_name=Param.SearchClass,
                            type='measproc.FileWorkSpace', order='measurement')
    for EntryId in EntryIds:
      WorkSpace = Batch.wake_entry(EntryId)

      Row1.extend([Batch.get_entry_attr(EntryId, 'measurement'), ''])
      Row2.extend(['Longitudinal distance (dx) [m]', ''])
      Row3.extend(['CVR3', 'AC100'])

      if not WorkSpace.workspace['ResError']:
        if len(WorkSpace.workspace['CVR3_dxDet']) == 1 and len(WorkSpace.workspace['AC100_dxDet']) == 1:
          Row4.extend([WorkSpace.workspace['CVR3_dxDet'].flatten()[0], WorkSpace.workspace['AC100_dxDet'].flatten()[0]])
          Row5.extend([WorkSpace.workspace['CVR3_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['CVR3_dxAsObs'].flatten()) != 0 else 0, WorkSpace.workspace['AC100_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['AC100_dxAsObs'].flatten()) != 0 else 0])
          Row6.extend(['n/a', WorkSpace.workspace['AC100_dxCW'].flatten()[0] if len(WorkSpace.workspace['AC100_dxCW'].flatten()) != 0 else 0])

        elif len(WorkSpace.workspace['CVR3_dxDet']) == 0:
          Row4.extend(['No interval has been found for CVR3', WorkSpace.workspace['AC100_dxDet'].flatten()[0]])
          Row5.extend(['', WorkSpace.workspace['AC100_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['AC100_dxAsObs'].flatten()) != 0 else 0])
          Row6.extend(['', WorkSpace.workspace['AC100_dxCW'].flatten()[0] if len(WorkSpace.workspace['AC100_dxCW'].flatten()) != 0 else 0])

        elif len(WorkSpace.workspace['AC100_dxDet']) == 0:
          Row4.extend([WorkSpace.workspace['CVR3_dxDet'].flatten()[0], 'No interval has been found for AC100'])
          Row5.extend([WorkSpace.workspace['CVR3_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['CVR3_dxAsObs'].flatten()) != 0 else 0, ''])
          Row6.extend(['n/a', ''])

        elif len(WorkSpace.workspace['CVR3_dxDet']) > 1:
          Row4.extend(['More than one interval has been found for CVR3', WorkSpace.workspace['AC100_dxDet'].flatten()[0]])
          Row5.extend(['', WorkSpace.workspace['AC100_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['AC100_dxAsObs'].flatten()) != 0 else 0])
          Row6.extend(['', WorkSpace.workspace['AC100_dxCW'].flatten()[0] if len(WorkSpace.workspace['AC100_dxCW'].flatten()) != 0 else 0])

        elif len(WorkSpace.workspace['AC100_dxDet']) > 1:
          Row4.extend([WorkSpace.workspace['CVR3_dxDet'].flatten()[0], 'More than one interval has been found for AC100'])
          Row5.extend([WorkSpace.workspace['CVR3_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['CVR3_dxAsObs'].flatten()) != 0 else 0, ''])
          Row6.extend(['n/a', ''])

      elif WorkSpace.workspace['ResError'] == 'No relevant object found for both CVR3 and AC100!' or WorkSpace.workspace['ResError'] == 'More than one relevant objects found for both CVR3 and AC100!':
        Row4.extend([WorkSpace.workspace['ResError'].flatten()[0], ''])
        Row5.extend(['', ''])
        Row6.extend(['', ''])

      elif WorkSpace.workspace['ResError'] == 'No relevant object found for CVR3 but AC100 is OK!' or WorkSpace.workspace['ResError'] == 'More than one relevant objects found for CVR3 but AC100 is OK!':
        Row4.extend([WorkSpace.workspace['ResError'].flatten()[0], WorkSpace.workspace['AC100_dxDet'].flatten()[0]])
        Row5.extend(['', WorkSpace.workspace['AC100_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['AC100_dxAsObs'].flatten()) != 0 else 0])
        Row6.extend(['', WorkSpace.workspace['AC100_dxCW'].flatten()[0] if len(WorkSpace.workspace['AC100_dxCW'].flatten()) != 0 else 0])

      elif WorkSpace.workspace['ResError'] == 'No relevant object found for AC100 but CVR3 is OK!' or WorkSpace.workspace['ResError'] == 'More than one relevant objects found for AC100 but CVR3 is OK!':
        Row4.extend([WorkSpace.workspace['CVR3_dxDet'].flatten()[0], WorkSpace.workspace['ResError'].flatten()[0]])
        Row5.extend([WorkSpace.workspace['CVR3_dxAsObs'].flatten()[0] if len(WorkSpace.workspace['CVR3_dxAsObs'].flatten()) != 0 else 0, ''])
        Row6.extend(['n/a', ''])

    Rows2BeWritten = [Row1, Row2, Row3, Row4, Row5, Row6]
    OutputCSV.writerows(Rows2BeWritten)
