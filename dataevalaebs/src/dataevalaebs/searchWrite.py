import numpy

import measproc
import interface

class cParam(interface.iParameter): 
  def __init__(self, MergeLimit):
    self.MergeLimit = MergeLimit
    self.genKeys()
    return

DefParam = cParam(2e-2)    

class cWrite(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup([{'Write': ('', 'Write')}])
    return Group

  def fill(self, Group):
    return Group

  def search(self, Param, Group):
    Source = self.get_source('main')
    Batch = self.get_batch()

    Time, Value = Source.getSignalFromSignalGroup('Write')
    IntervalList = measproc.cIntervalList(Time)
    Report = measproc.cIntervalListReport(IntervalList, 'Write')
    Diff = numpy.diff(Time)
    Mask = Diff < Param.MergeLimit
    Mask = Mask.astype(int)
    Mask = numpy.concatenate([numpy.zeros(1, dtype=int), Mask])
    Diff = numpy.diff(Mask)
    Index = numpy.arange(Time.size, dtype=int)
    Ups = Index[Diff > 0]
    Ups = Ups.tolist()
    Downs  = Index[Diff < 0]
    Downs += 1
    Downs  = Downs.tolist()
    if Mask[-1] == 1:
      Downs.append(Time.size)
    for Up, Down in zip(Ups, Downs):
      Comments = []      
      for Index in xrange(Up, Down):
        Comment = Value[Index]        
        Comment = unicode(Comment, 'latin-1')  
        Comments.append(Comment)
      Comment = '\n'.join(Comments)
      Interval = Up, Down
      Report.setComment(Interval, Comment)
      Batch.add_entry(Report, self.NONE)
    return

