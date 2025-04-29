"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import PlotNavigator
import ReportNavigator

def viewEvents(Sync, Source, Events, MainTitle, FgNr):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `lrr3proc.cLrr3Source`
      Signal source to get mdf signals.
    Events : list
      Container of the selected Events [[ECU<str>, Title<str>, SignalName<str>, CheckValue<int>],]
    MainTitle : str
      Title of the plot window
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  """
  PN = PlotNavigator.cPlotNavigator(MainTitle, FgNr)
  for ECU, Title, SignalName, CheckValue in Events:
    Signal = Source.getSignal(ECU, SignalName)
    PN.addsignal(Title, Signal)
  Sync.addClient(PN)
  pass

def viewReports(Sync, Source, Reports, MainTitle, Color):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `lrr3proc.cLrr3Source`
      Signal source to get mdf signals.
    Events : list
      Container of the selected Events [[ECU<str>, Title<str>, SignalName<str>, CheckValue<int>],]
    MainTitle : str
      Title of the plot window
    Color : str
      Color for visualization the interval on the PlotNavigator.
  """
  RN = ReportNavigator.cReportNavigator(MainTitle, Color)
  for Report in Reports:
    Title = Report.getTitle()
    RN.addReport(Title, Report)
  Sync.addClient(RN)
  pass
