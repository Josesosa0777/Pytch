import datavis
import interface

DefParam = interface.NullParam

class cViewReportNavigator(interface.iView):
  def view(self, param=DefParam):
    repNav = datavis.cReportNavigator()
    for report in interface.Reports.keys():
      repNav.addReport(report.getTitle(), report)
    interface.Sync.addClient(repNav)