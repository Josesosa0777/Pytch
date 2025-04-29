import unittest

from reportlab.platypus import Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents

from datalab.story import intro, toc

class TestIntro(unittest.TestCase):
  def setUp(self):
    self.story = intro('foo', 'bar')
    return

  def test(self):
    self.assertEqual(len(self.story), 3)
    
    title, heading, summary = self.story
    
    self.assertIsInstance(title, Paragraph)
    self.assertIsInstance(heading, Paragraph)
    self.assertIsInstance(summary, Paragraph)
    return

class TestToc(unittest.TestCase):
  def setUp(self):
    self.story = toc()
    return

  def test(self):
    self.assertEqual(len(self.story), 2)

    heading, toc = self.story

    self.assertIsInstance(heading, Paragraph)
    self.assertIsInstance(toc, TableOfContents)
    return

unittest.main()
