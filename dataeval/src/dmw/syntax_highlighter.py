from PySide import QtGui, QtCore

class PythonSyntaxHighlighter(QtGui.QSyntaxHighlighter):
  def __init__(self, *args, **kwargs):
    QtGui.QSyntaxHighlighter.__init__(self, *args, **kwargs)

    self.rules = []

    number_format = QtGui.QTextCharFormat()
    number_format.setForeground(QtCore.Qt.red)
    self.rules.append((QtCore.QRegExp('\\b[0-9]+'), number_format))

    function_format = QtGui.QTextCharFormat()
    function_format.setForeground(QtCore.Qt.magenta)
    regexp = QtCore.QRegExp("\\bdef\\s+[A-Za-z_]\\w*")
    self.rules.append((regexp, function_format))

    class_format = QtGui.QTextCharFormat()
    class_format.setFontWeight(QtGui.QFont.Bold)
    regexp = QtCore.QRegExp("\\bclass\\s+[A-Za-z_]\\w*")
    self.rules.append((regexp, class_format))

    blue_bold_format = QtGui.QTextCharFormat()
    blue_bold_format.setFontWeight(QtGui.QFont.Bold)
    blue_bold_format.setForeground(QtCore.Qt.blue)
    blue_bold_patterns = ['and ', 'as', 'assert', 'break', 'class', 'continue',
                          'def', 'del', 'elif', 'else', 'except', 'exec',
                          'False', 'finally', 'for', 'from', 'global', 'if',
                          'import', 'in', 'is', 'lambda', 'None', 'not', 'or',
                          'pass', 'print', 'raise', 'return', 'True', 'try',
                          'while', 'with', 'yield']

    patterns = ['\\b%s\\b' %pattern for pattern in blue_bold_patterns]
    self.rules.extend([(QtCore.QRegExp(pattern), blue_bold_format)
                                                       for pattern in patterns])

    char_format = QtGui.QTextCharFormat()
    char_format.setForeground(QtCore.Qt.gray)
    regexps = [QtCore.QRegExp(pattern) for pattern in ['\"[^"]*\"', "\'[^']*\'"]]
    for regexp in regexps:
      self.rules.append((regexp, char_format))

    green_format = QtGui.QTextCharFormat()
    green_format.setForeground(QtCore.Qt.darkGreen)
    self.rules.append((QtCore.QRegExp('#.*'), green_format))

    return

  def highlightBlock(self, text):
    for pattern, format in self.rules:
      ndx = pattern.indexIn(text)
      while ndx >= 0:
        length = pattern.matchedLength()
        self.setFormat(ndx, length, format)
        ndx = pattern.indexIn(text, ndx + length)
    return


if __name__ == '__main__':
  import os
  import sys
  app = QtGui.QApplication([])
  TEMPLATE_DIR = 'text\\templates'
  TEMPLATE = 'viewTemplate.py'
  ParentDir = os.path.dirname(os.path.dirname(__file__))
  DirName = os.path.join(ParentDir, TEMPLATE_DIR)
  FileName = os.path.join(DirName, TEMPLATE)
  plaintext = QtGui.QPlainTextEdit()
  file = open(FileName)
  highlighter = PythonSyntaxHighlighter(plaintext.document())
  plaintext.setPlainText(file.read())
  plaintext.show()
  sys.exit(app.exec_())

