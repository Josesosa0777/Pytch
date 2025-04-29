import Report

TextEntryDir = None


class TextEntry(Report.iEntry):
  pass

class DinTextEntry(TextEntry):
  def __init__(self, title, text):
    path = Report.createPath(title, TextEntryDir, '.txt')
    Report.iEntry.__init__(self, path, title)
    f = open(path, 'w')
    f.write(text)
    f.close()
    return
    

class FileTextEntry(TextEntry):
  def __init__(self, filename, title=None):
    Report.iEntry.__init__(self, filename, title)
    f = open(filename)
    self.text = f.read()
    f.close()
    return

class CreateParams:
  def __init__(self, title, text, dir_name):
    self.title = title
    self.text = text
    self.dir_name = dir_name
    return

  def __call__(self):
    global TextEntryDir
    TextEntryDir = self.dir_name
    return DinTextEntry(self.title, self.text)
