import interface
import measproc

MRR1signalGroup = {'CVR3 Intro' : ('MRR1plus', 'sit.IntroFinder_TC.Intro.i0.Id')}
ECUsignalGroup  = {'LRR3 Intro' : ('ECU'     , 'sit.IntroFinder_TC.Intro.i0.Id')}
SignalGroups = [MRR1signalGroup, ECUsignalGroup]

NO_INTRO_FOUND = 0
INTRO_SAM = 1
INTRO_SXM = 2
INTRO_SAS = 3
INTRO_LAM = 4
INTRO_RAM = 5
INTRO_SEM = 6
introType2Name =  {NO_INTRO_FOUND       : 'No intro',
                   INTRO_SAM            : 'Same Approach Moving (SAM)',
                   INTRO_SXM            : 'Same Equal or Leave Moving (SXM)',
                   INTRO_SAS            : 'Same Approach Stationary (SAS)',
                   INTRO_LAM            : 'Left Approach Moving (LAM)',
                   INTRO_RAM            : 'Right Approach Moving (RAM)',
                   INTRO_SEM            : 'Same Equal Moving (SEM)',
                  }
class cParameter(interface.iParameter):
  def __init__(self, introType):
    self.introType = introType
    self.genKeys()
    self.introName = introType2Name[introType]
    pass

NO_INTRO_FOUND_Param = cParameter(NO_INTRO_FOUND)
INTRO_SAM_Param      = cParameter(INTRO_SAM)
INTRO_SXM_Param      = cParameter(INTRO_SXM)
INTRO_SAS_Param      = cParameter(INTRO_SAS)
INTRO_LAM_Param      = cParameter(INTRO_LAM)
INTRO_RAM_Param      = cParameter(INTRO_RAM)
INTRO_SEM_Param      = cParameter(INTRO_SEM)

class cSearchIntro(interface.iSearch):
  def search(self, Param):
    TitlePattern = '%s - %s'
    Batch = self.get_batch()
    Source = self.get_source('main')
    Comment =  '%s was inconsistent' %Source.FileName

    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)
          Intervals = Source.compare(Time, Value, measproc.equal, Param.introType)
          if len(Intervals) == 0:
            Result = self.FAILED
          else:
            Result = self.PASSED
          Title = TitlePattern %(Alias, Param.introName)
          Report = measproc.cIntervalListReport(Intervals, Title)
          Batch.add_entry(Report, Result)
        else:
          Result = self.INCONS
          Title = TitlePattern %(Alias, Param.introName)
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = Comment
          Batch.add_entry(Report, Result)
    pass

