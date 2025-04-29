import xml.dom.minidom

import numpy

import Report

StatDir = None

class iStatistic(Report.iXmlNpy):
  def __init__(self, PathToSave, Title=None):
    Report.iEntry.__init__(self, PathToSave, Title)
    
    self.Axes = []
    self.TickLabels = {}
    self.Array = numpy.zeros(0)
    pass
  
  def save(self):
    Document = xml.dom.minidom.Document()
    Statistic = Document.createElement('Staistic')
    Document.appendChild(Statistic)
    for AxisName in self.Axes:
      Axis = Document.createElement('Axis')
      Axis.setAttribute('Name', AxisName)
      Statistic.appendChild(Axis)
      for TickLabel in self.TickLabels[AxisName]:
        Tick = Document.createElement('Tick')
        Tick.setAttribute('Name', TickLabel)
        Axis.appendChild(Tick)
    open(self.PathToSave, 'w').write(Document.toprettyxml())

    ArrayPath = self.getTimeFile()
    numpy.save(ArrayPath, self.Array)
    pass

  def pos(self, Names):
    Pos = [None for Dummy in Names]
    for AxisName, TickLabel in Names:
      Axis = self.Axes.index(AxisName)
      Tick = self.TickLabels[AxisName].index(TickLabel)
      Pos[Axis] = Tick
    Pos = tuple(Pos)
    return Pos
    
  def set(self, Names, Value):
    """
    :Parameters:
      Names : list
        [[AxisName<str>, TickLabel<str>]]
      Value : float  
    """
    Pos = self.pos(Names)
    self.Array.itemset(Pos, Value)
    pass

  def get(self, Names):
    Pos = self.pos(Names)
    Value = self.Array.item(Pos)
    return Value

class cDinStatistic(iStatistic):
  def __init__(self, Title, Axes):
    """
    :Parameters:
      Title : str 
      Axes : list
        [[AxisName<str>, [TickLabel<str>,]],]
    """
    PathToSave = Report.createPath(Title, StatDir, '.xml')
    iStatistic.__init__(self, PathToSave, Title)
    
    Dim = []
    for AxisName, TickLabels in Axes:
      Dim.append(len(TickLabels))
      self.Axes.append(AxisName)
      self.TickLabels[AxisName] = TickLabels
    self.Array = numpy.zeros(Dim)
    pass


class cFileStatistic(iStatistic):
  def __init__(self, FileName, Title=None):
    iStatistic.__init__(self, FileName, Title)

    Document = xml.dom.minidom.parse(FileName)
    for Axis in Document.getElementsByTagName('Axis'):
      AxisName = Axis.getAttribute('Name')
      self.Axes.append(AxisName)
      TickLabels = []
      for Tick in Axis.getElementsByTagName('Tick'):
        TickLabel = Tick.getAttribute('Name')
        TickLabels.append(TickLabel)
      self.TickLabels[AxisName] = TickLabels
    
    ArrayPath = FileName.replace('.xml', '.npy')
    self.Array = numpy.load(ArrayPath)
    pass

class CreateParams:
  def __init__(self, Title, Axes, DirName):
    self.Title = Title
    self.Axes = Axes
    self.DirName = DirName
    return

  def __call__(self):
    global StatDir
    StatDir = self.DirName
    return cDinStatistic(self.Title, self.Axes)

