import Report

FigEntryDir = None


class FigEntry(Report.iEntry):
  pass

class DinFigEntry(FigEntry):
  def __init__(self, title, fig):
    path = Report.createPath(title, FigEntryDir, '.png')
    Report.iEntry.__init__(self, path, title)
    fig.savefig(path, format='png')
    return
    

class FileFigEntry(FigEntry):
  def __init__(self, filename, title=None):
    Report.iEntry.__init__(self, filename, title)
    return


class CreateParams:
  def __init__(self, title, fig, dir_name):
    self.title = title
    self.fig = fig
    self.dir_name = dir_name
    return

  def __call__(self):
    global FigEntryDir
    FigEntryDir = self.dir_name
    return DinFigEntry(self.title, self.fig)
