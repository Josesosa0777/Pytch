# -*- dataeval: init -*-

from interface import iView

init_params = {
  'egg':    dict(spam=56),
  'eggegg': dict(spam=42),
}


class View(iView):
  def __init__(self, spam):
    self.spam = spam
