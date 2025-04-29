import scipy.io

import Report

WorkSpaceDir = None


class WorkSpace(Report.iEntry):
  def __init__(self, PathToSave, Title=None):
    Report.iEntry.__init__(self, PathToSave, Title)
    self.workspace = {}
    return

  def save(self):
    scipy.io.savemat(self.PathToSave, self.workspace, oned_as='column')
    return

  def add(self, **values):
    self.workspace.update(values)
    return


class DinWorkSpace(WorkSpace):
  def __init__(self, title):
    path = Report.createPath(title, WorkSpaceDir, '.mat')
    WorkSpace.__init__(self, path, title)
    return


class FileWorkSpace(WorkSpace):
  def __init__(self, filename, title=None):
    WorkSpace.__init__(self, filename, title)
    scipy.io.loadmat(filename, self.workspace)
    return

class CreateParams:
  def __init__(self, Title, DirName):
    self.Title = Title
    self.DirName = DirName
    return

  def __call__(self):
    global WorkSpaceDir
    WorkSpaceDir = self.DirName
    return DinWorkSpace(self.Title)

