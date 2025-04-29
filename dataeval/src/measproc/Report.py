import os
import xml.dom.minidom
import tempfile

import numpy

import IntervalList
import measparser

RepDir = None

TITLE_SEPARATOR = '.'
""":type: str
Separator between the title and random name in the path"""


def correctTitle(Title):
  """
  Corrects the given title parameter if it contains invalid characters for file name.
  
  :Parameters:
    Title : str
  :ReturnType: str
  :Return: Correct title
  """
  for invalidChar in '_.:;\\/':
    Title = Title.replace(invalidChar, '-')
  return Title

def createPath(Title, Home, Suffix):
  if Home is None:
    Home = os.path.abspath(os.curdir)
  elif not os.path.exists(Home):
    os.makedirs(Home)
  Title = correctTitle(Title)
  fd, Path = tempfile.mkstemp(prefix=Title+TITLE_SEPARATOR, suffix=Suffix, dir=Home)
  os.close(fd)
  return Path
    
def getTitle(Name, WithoutExt):
  """
  Get the title of the report.

  :Parameters:
    WithoutExt : bool
      Send the title with the with the file extension or not. 
  :ReturnType: str
  """
  Title = os.path.basename(Name)
  if WithoutExt:
    Title = Title.split(TITLE_SEPARATOR)
    Title = Title[0]
  return Title

class iEntry:
  TITLE_SEPARATOR = TITLE_SEPARATOR
  correctTitle = staticmethod(correctTitle)
  def __init__(self, PathToSave, Title=None):
    self.PathToSave = PathToSave
    """:type: str
    Path where to save the entry"""
    self.Title = Title if Title is not None else getTitle(PathToSave, True)
    """:type: str
    Name to identify the entry"""
    self.ReportAttrs = {'MeasLMD': 'unknown'}
    self.ShownAttrs = []
    pass
  
  def getTitle(self, WithoutExt=True):
    """
    :Parameters:
      WithoutExt : bool
        Send the title with the with the file extension or not. Default is 
        without.
    Get the title of the report.
    :ReturnType: str
    """
    if not WithoutExt:
      return getTitle(self.PathToSave, False)  # silly but backward compatible
    return self.Title
  
  def save(self):
    return

  def getEntryComment(self):
    return ''


class iXmlNpy(iEntry):
  def getTimeFile(self): 
    File, Ext = os.path.splitext(self.PathToSave)
    File += '.npy'
    return File
  pass


class iReport(iXmlNpy):
  VOTE_SEP = ':'
  """Report class for measproc.cIntervalList."""
  def __init__(self, PathToSave, Title=None):
    iEntry.__init__(self, PathToSave, Title)

    self.IntervalList = []
    """:type: IntervalList.cIntervalList
    Container of the intervals."""
    self.IntervalAttrs = {}
    """:type: dict
    Container of the Interval attributes."""
    self.ReportAttrs.update({'Version'     : '0.1.0',
                             'Comment'     : '',
                             'NoIntervals' : 0})
    """:type: dict
    Container of the Report attributes."""
    self.ShownAttrs = ['NoIntervals', 'Comment']
    pass
    
  def save(self):
    """
    Save the repor into `XmlFile` if any modification is made on it.
    
    :ReturnType: str
    :Return: Last modification date of the report.
    """
    Document = xml.dom.minidom.Document()
    Report   = Document.createElement('Report')        
    
    for Attr in 'Version', 'Comment':
      Report.setAttribute(Attr,  str(self.ReportAttrs[Attr]))
    Report.setAttribute('Votes', self.VOTE_SEP.join(self.getVotes()))
    Document.appendChild(Report)
    
    for Lower, Upper in self.IntervalList:
      Interval = Document.createElement('Interval')
      Interval.setAttribute('Lower', str(Lower))
      Interval.setAttribute('Upper', str(Upper))
      Attrs = self.IntervalAttrs[(Lower, Upper)]
      Interval.setAttribute('Comment', Attrs['Comment'])
      Interval.setAttribute('Vote', self.VOTE_SEP.join(Attrs['Vote']))
      Report.appendChild(Interval)
    
    TimeFile = self.getTimeFile()
    if not os.path.exists(TimeFile):
      numpy.save(TimeFile, self.IntervalList.Time)
    
    XmlStr = Document.toprettyxml()
    if os.path.exists(self.PathToSave):
      XmlFile = open(self.PathToSave).read()
      if XmlFile == XmlStr:
        return measparser.getLastModDate(self.PathToSave)
    open(self.PathToSave, 'w').write(XmlStr)
    return measparser.getLastModDate(self.PathToSave)
  
  def getEntryComment(self):
    return self.ReportAttrs['Comment']

  def removeInterval(self, Interval):
    """
    :Parameters:
      Interval : tuple
        (Lower<int>, Upper<int>)      
    """
    if Interval in self.IntervalList:
      self.IntervalList.remove(*Interval)
    IntervalAttrs = self.IntervalAttrs[Interval]
    for Vote in IntervalAttrs['Vote']:
      self.ReportAttrs[Vote] -= 1
    self.ReportAttrs['NoIntervals'] = len(self.IntervalList)
    del self.IntervalAttrs[Interval]
    pass
  
  def addInterval(self, Interval):  
    """
    :Parameters:
      Interval : tuple
        (Lower<int>, Upper<int>)      
    """
    if Interval not in self.IntervalList:
      self.IntervalList.add(*Interval)
    
    self.IntervalAttrs[Interval] = {'Vote': set(), 'Comment': ''} 
    self.ReportAttrs['NoIntervals'] = len(self.IntervalList)
    pass
    
  def vote(self, Interval, Vote):
    """
    Vote to the `Interval` of the `IntervalList`.
    
    :Parameters:
      Interval : tuple
        (Lower<int>, Upper<int>)
      Vote : str
        'valid' 'invalid' or 'missed'
    """
    self.IntervalAttrs[Interval]['Vote'].add(Vote)
    self.ReportAttrs[Vote] += 1
    pass

  def devote(self, Interval, Vote):
    self.IntervalAttrs[Interval]['Vote'].remove(Vote)
    self.ReportAttrs[Vote] -= 1
    return

  def getIntervalVotes(self, Interval):
    return self.IntervalAttrs[Interval]['Vote']

  def toggle(self, Interval, Vote):
    if self.checkVote(Interval, Vote):
      self.devote(Interval, Vote)
    else:
      self.vote(Interval, Vote)
    return

  def checkVote(self, Interval, Vote):
    return Vote in self.IntervalAttrs[Interval]['Vote']
    
  def addVote(self, Vote):
    if Vote in self.ReportAttrs:
      return
    self.ReportAttrs[Vote] = 0
    self.ShownAttrs.insert(-1, Vote)
    return

  def addVotes(self, Votes):
    for Vote in Votes:
      self.addVote(Vote)
    return

  def rmVote(self, Vote):
    del self.ReportAttrs[Vote]
    self.ShownAttrs.remove(Vote)
    Vote = set([Vote])
    for Attr in self.IntervalAttrs.itervalues():
      Attr['Vote'].difference_update(Vote)
    return

  def getVotes(self):
    return self.ShownAttrs[1:-1]
  
  def filter(self, Vote):
    Intervals = IntervalList.cIntervalList(self.IntervalList.Time)
    for Interval, Attrs in self.IntervalAttrs.iteritems():
      if self.checkVote(Interval, Vote):
        Intervals.add(*Interval)
    return Intervals

  def getComment(self, Interval):
    Attrs = self.IntervalAttrs[Interval]
    Comment = Attrs['Comment']
    return Comment
  
  def setComment(self, Interval, Comment):
    if Interval not in self.IntervalAttrs:
      self.addInterval(Interval)
    Attrs = self.IntervalAttrs[Interval]
    Attrs['Comment'] = Comment
    pass
  
class cIntervalListReport(iReport):    
  """Create report from IntervalList."""
  def __init__(self, IntervalList, Title, Votes=('invalid', 'missed', 'valid')):
    """
    :Parameters:
      Source : `measproc.cEventFinder`
      IntervalList : `measproc.cIntervalList`
      Title : str
    """
    PathToSave = createPath(Title, RepDir, '.xml')
    iReport.__init__(self, PathToSave, Title)

    self.ReportAttrs['Comment']     = ''
    self.ReportAttrs['NoIntervals'] = len(IntervalList)
    self.addVotes(Votes)
    
    self.IntervalList = IntervalList
    for Lower, Upper in IntervalList:
      self.IntervalAttrs[(Lower, Upper)] = {'Vote': set(), 'Comment': ''}
    pass

class cEmptyReport(iReport):
  def __init__(self, Title):
    PathToSave = createPath(Title, RepDir, '.xml')
    iReport.__init__(self, PathToSave, Title)

    Time = numpy.zeros(1)
    self.IntervalList = IntervalList.cIntervalList(Time)
    pass
    
class cFileReport(iReport):    
  """Create report from `Report` xml file"""
  def __init__(self, ReportFile, Title=None):
    """
    :Parameters:
      Source : `measproc.cEventFinder`
      Report : str
    """
    iReport.__init__(self, ReportFile, Title)
    
    Document = xml.dom.minidom.parse(ReportFile)
    Report,  = Document.getElementsByTagName('Report')    
    
    for Attr in self.ReportAttrs.iterkeys():
      if Report.hasAttribute(Attr):
        self.ReportAttrs[Attr] = Report.getAttribute(Attr)

    Time = self.getTimeFile()
    Time = numpy.load(Time)
    self.IntervalList = IntervalList.cIntervalList(Time)
    
    if Report.hasAttribute('Votes'):
      Votes = Report.getAttribute('Votes').split(self.VOTE_SEP)
    else:
      Votes = 'invalid', 'missed', 'valid'
    self.addVotes(Votes)

    ObsolatedVote = set(['none'])

    for Interval in Report.getElementsByTagName('Interval'):
      Lower = int(Interval.getAttribute('Lower'))
      Upper = int(Interval.getAttribute('Upper'))
      self.IntervalList.add(Lower, Upper)
      Attrs = {'Vote': set(), 'Comment': ''}
      if Interval.hasAttribute('Comment'):
        Attrs['Comment'] = Interval.getAttribute('Comment')
      if Interval.hasAttribute('Vote'):
        Vote = Interval.getAttribute('Vote')
        if Vote:
          Vote = set(Vote.split(self.VOTE_SEP))
          Vote.difference_update(ObsolatedVote)
          Attrs['Vote'] = Vote
      self.IntervalAttrs[(Lower, Upper)] = Attrs
    
    for Attrs in self.IntervalAttrs.itervalues():
      for Vote in Attrs['Vote']:
        self.ReportAttrs[Vote] += 1

    self.ReportAttrs['NoIntervals'] = len(self.IntervalList)
    return    

class CreateParams:
  def __init__(self, Time, Title, Votes, DirName):
    self.Time = Time
    self.Title = Title
    self.Votes = Votes
    self.DirName = DirName
    return

  def __call__(self):
    global RepDir
    RepDir = self.DirName
    Intervals = IntervalList.cIntervalList(self.Time)
    return cIntervalListReport(Intervals, self.Title, self.Votes) 

class IntervalAddParams:
  def __init__(self, Interval, Vote, Comment=''):
    self.Interval = Interval
    self.Vote = Vote
    self.Comment = Comment
    return

  def __call__(self, Report):
    Report.addInterval(self.Interval)
    Report.vote(self.Interval, self.Vote)
    Report.setComment(self.Interval, self.Comment)
    return

