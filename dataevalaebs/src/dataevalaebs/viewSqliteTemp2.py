import interface
from datavis.report2navigator import Report2Navigator

DefParam = interface.NullParam

class cView(interface.iView):
  def view(self, param=DefParam):
    repNav = Report2Navigator()
    for report, fetch in interface.Report2s.iteritems():
      title = repNav.addReport(report)
      for intervalid, _, _ in fetch:
        repNav.markIntervalForever(title, intervalid)
    interface.Sync.addClient(repNav)
    return
