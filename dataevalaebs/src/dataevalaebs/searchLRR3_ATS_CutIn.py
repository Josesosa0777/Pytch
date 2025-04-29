import interface
import aebs.proc
import aebs.fill
import measproc
from aebs.proc.filters import delStationaryObjects, delShorttimeObject,\
                              delLongrangeObjects

DefParam = interface.NullParam

class cLRR3_ATS_CutIn(interface.iSearch):
  minlivetime = 2
  maxrange = 0
  max_interval_length = 8

  dep = 'fillLRR3_ATS@aebs.fill',

  def fill(self):
    Modules = self.get_modules()
    scaletime, data = Modules.fill('fillLRR3_ATS@aebs.fill')

    delStationaryObjects(data)
    delShorttimeObject(scaletime,data,minlivetime=self.minlivetime)
    if self.maxrange!=0:
      delLongrangeObjects(data, maxrange=self.maxrange)

    len_scaletime=len(scaletime)

    starttime=0
    startindex=0
    endtime=0
    endindex=0
    actualid=0
    startid=0
    intervallists=[]

    #search CutIn Situations
    #Search for CutIn_from_left (track==2) and form right (track==3)
    for track in xrange(2,4):
      intervallist=measproc.cIntervalList(scaletime)
      for x in xrange(len_scaletime):
          actualid=data[track]["id"][x]
          endtime=scaletime[x]
          endindex=x
          if actualid!=startid and startid!=0:
            if data[0]["id"][x]==startid:
              for z in xrange(x+1,len_scaletime):
                baz=z
                delta_t = (scaletime[baz]-endtime)
                if data[0]["id"][z]!=startid or delta_t>self.max_interval_length/2:
                  break;
              if delta_t>self.max_interval_length/4:
                t_start = max(endtime-delta_t,0)
                egg = startindex
                for z in xrange(len_scaletime):
                  if scaletime[z]>t_start:
                    egg = z
                    break;
                if (endtime-starttime)>self.max_interval_length/8:
                  intervallist.add(egg,baz)
            startindex=endindex
            starttime=endtime
            startid=actualid
          if actualid!=startid and startid==0:
            startindex=endindex
            starttime=endtime
            startid=actualid
      intervallists.append(intervallist)
    Report_CutIn_from_Left = measproc.cIntervalListReport(intervallists[0], Title="CutInfromLeft")
    Report_CutIn_from_Right = measproc.cIntervalListReport(intervallists[1], Title="CutInfromRight")

    #Search Cut Out Situations
    intervallist_right=measproc.cIntervalList(scaletime)
    intervallist_left=measproc.cIntervalList(scaletime)
    track=0
    for x in xrange(len_scaletime):
          actualid=data[track]["id"][x]
          endtime=scaletime[x]
          endindex=x
          found=False
          if actualid!=startid and startid!=0:
            for track_search in xrange(2,4):
                if data[track_search]["id"][x]==startid:
                  for z in xrange(x+1,len_scaletime):
                    baz=z
                    delta_t = (scaletime[baz]-endtime)
                    if data[track_search]["id"][z]!=startid or delta_t>self.max_interval_length/2:
                      break;
                  if delta_t>self.max_interval_length/4:
                    t_start = max(endtime-delta_t,0)
                    egg = startindex
                    for z in xrange(len_scaletime):
                      if scaletime[z]>t_start:
                        egg = z
                        break;
                    if (endtime-starttime)>self.max_interval_length/8:
                      if track_search==2:
                        intervallist_left.add(egg,baz)
                      else:
                        intervallist_right.add(egg,baz)
                      break;
            startindex=endindex
            starttime=endtime
            startid=actualid
          if actualid!=startid and startid==0:
            startindex=endindex
            starttime=endtime
            startid=actualid
    intervallists.append(intervallist_left)
    intervallists.append(intervallist_right)
    Report_CutOut_Left = measproc.cIntervalListReport(intervallists[2], Title="CutOutLeft")
    Report_CutOut_Right = measproc.cIntervalListReport(intervallists[3], Title="CutOutRight")

    return [Report_CutIn_from_Left, Report_CutIn_from_Right, Report_CutOut_Left, Report_CutOut_Right]

  def search(self, Param, Reports):
    Batch = self.get_batch()
    for Report in Reports:
      Batch.add_entry(Report, self.NONE)
    return

