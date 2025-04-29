# -*- dataeval: init -*-

from interface import iView

class cComment(iView):
  def view(self):
    source = self.get_source()
    print source.getFileComment()
    return
