import os
import warnings
import time

from datalab.docxlab import tygra
from docx import Document
from templates import TemplateLoader
from tygra import TableOfContent

template_loader = None


def _build(story, file_path, f_template):
    global template_loader
    _, ext = os.path.splitext(file_path)
    if ext == '.doc':
        file_path.replace(ext, '.docx')
    elif ext != '.docx':
        warnings.warn("File extension should be '.docx', not '{}'".format(ext))
        file_path.replace(ext, 'docx')

    directory, file_name = os.path.split(file_path)
    if os.path.isfile("{}\~${}".format(directory, file_name)):
        t = time.strftime("%c").replace('/', '_').replace(' ', '_').replace(':', '_')
        file_path = file_path.replace('.docx', '_' + t + '.docx')
        warnings.warn("File is already opened, cannot rewrite it. New file is: '{}'".format(file_path))

    if f_template is not None:
        if isinstance(f_template, basestring):
            document = Document(f_template)  # the location of the template docx
        else:
            raise TypeError("Template doc path should be basestring, not '{}'".format(type(f_template)))
    else:
        document = Document()
    # load styles
    template_loader = TemplateLoader(document)
    template_loader.load_styles()
    # create doc
    for s in story:
        s.add_to_document(document)

    document.save(file_path)
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
        TableOfContent.toclevels = kwargs.pop('toclevels', 2)

    @classmethod
    def set_logo(cls, name):
        cls.LOGO = os.path.join(os.path.dirname(__file__), '..', 'pics', name)
        return

    def build(self, story, fp=None, f_template=None):
        if isinstance(fp, basestring):
            _build(story, fp, f_template)
        else:
            raise TypeError("Doc path should be basestring, not '{}'".format(type(fp)))

    def multiBuild(self, story, f=None, **kwargs):
        f_template = kwargs.pop("f_template", None)
        return self.build(story, f, f_template)
