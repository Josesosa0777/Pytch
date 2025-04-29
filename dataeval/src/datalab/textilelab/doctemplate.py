import os
import sys
from datalab.textilelab import tygra


def _build(story, fp):
  fp.write("".join([flowable.print_() for flowable in story]) )
  fp.flush()
  return


class StoryBuilder(object):
  def __init__(self):
    self.story = []

  def add(self, element):
    if isinstance(element, StoryBuilder):
      element = element.story
    if not isinstance(element, (tuple, set, list)):
      element = [element]
    for e in element:
      if isinstance(e, (tuple, list, set)):
        self.add(e)
      else:
        self.story += [e]

  def __add__(self, other):
    self.add(other)
    return self


class SimpleDocTemplate(object):
  FOOTER = ""
  HEADER = ""
  LOGO = os.path.join(os.path.dirname(__file__), '..', 'pics', 'Knorr_logo.png')
  
  tygra = tygra
  
  def __init__(self, *args, **kwargs):
    pass
  
  @classmethod
  def set_logo(cls, name):
    cls.LOGO = os.path.join(os.path.dirname(__file__), '..', 'pics', name)
    return
  
  def build(self, story, f=None):
    if isinstance(f, basestring):
      with open(f, 'w') as fp:
        return _build(story, fp)
    else:
      fp = f if f is not None else sys.stdout
      return _build(story, fp)
  
  def multiBuild(self, story, f=None, **_):
    # kwargs are there to catch reportlab and docxlab specific options
    return self.build(story, f)
