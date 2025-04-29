# -*- dataeval: init -*-

from viewInit import View

init_params = {
  'egg':    dict(spam=23),
  'eggegg': dict(spam=32),
}


class MyView(View):
  def __init__(self, spam):
    self.spam = spam
