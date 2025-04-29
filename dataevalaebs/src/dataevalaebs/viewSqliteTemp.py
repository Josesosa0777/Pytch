import interface
from datavis.report2navigator import Report2Navigator

DefParam = interface.NullParam

class cView(interface.iView):
  def view(self, param=DefParam):
    repNav = Report2Navigator()
    for report in interface.Report2s.keys():
      repNav.addReport(report)
    interface.Sync.addClient(repNav)
    return
