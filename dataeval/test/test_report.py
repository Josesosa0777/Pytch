import unittest
import shutil

import numpy

import measproc
from measproc.Report       import cIntervalListReport, cFileReport
from measproc.IntervalList import cIntervalList

measproc.Report.RepDir = 'build'

def create_report():
  time = numpy.arange(0, 10, 1e-2)
  intervallist = cIntervalList(time)
  return cIntervalListReport(intervallist, 'foo', ['spam', 'egg'])

class Report(unittest.TestCase):
  def setUp(self):
    self.report = create_report()
    return

  def test_addInterval(self):
    interval = 12, 42
    self.report.addInterval(interval)
    return

  def test_removeInterval(self):
    interval = 22, 33
    self.report.addInterval(interval)
    self.report.removeInterval(interval)
    return

  def test_vote(self):
    interval = 44, 55
    self.report.addInterval(interval)
    self.report.vote(interval, 'spam')
    return

  def test_getVote(self):
    interval = 67, 89
    self.report.addInterval(interval)
    self.report.vote(interval, 'egg')
    self.assertSetEqual(self.report.getIntervalVotes(interval), 
                        {'egg'})
    return
  
  def test_setComment(self):
    interval = 32, 54
    self.report.setComment(interval, 'spam spam')
    return

  def test_getComment(self):
    interval = 38, 56
    comment = 'spam spam'
    self.report.setComment(interval, comment)
    self.assertEqual(self.report.getComment(interval),
                     comment)
    return

  def test_devote(self):
    interval = 87, 99
    vote = 'spam'
    self.report.addInterval(interval)
    self.report.vote(interval, vote)
    self.assertSetEqual(self.report.getIntervalVotes(interval),
                        {vote})
    self.report.devote(interval, vote)
    self.assertNotIn(vote, self.report.getIntervalVotes(interval))
    return

  def test_addVote(self):
    vote = 'snake'
    self.report.addVote(vote)
    self.assertIn(vote, self.report.getVotes())
    return

  def test_addVotes(self):
    votes = 'snake', 'pyon'
    self.report.addVotes(votes)
    for vote in votes:
      self.assertIn(vote, self.report.getVotes())
    return

  def test_rmVote(self):
    vote = 'spam'
    self.report.rmVote(vote)
    self.assertNotIn(vote, self.report.getVotes())
    self.report.addVote(vote)
    return

  def test_toggle_filter(self):
    vote = 'spam'
    interval = 36, 75
    self.report.addInterval(interval)
    self.report.toggle(interval, vote)
    self.assertIn(interval, self.report.filter(vote))
    self.report.toggle(interval, vote)
    self.assertNotIn(interval, self.report.filter(vote))
    return

  def tearDown(self):
    self.report.save()
    return
  pass

class EntryComment(unittest.TestCase):
  def setUp(self):
    report = create_report()
    self.comment = 'fo is never bar'
    report.ReportAttrs['Comment'] = self.comment
    report.save()
    self.name = report.PathToSave
    return

  def test(self):
    report = cFileReport(self.name)
    self.assertEqual(report.getEntryComment(),
                     self.comment)
    return
  pass

class Vote(unittest.TestCase):
  def setUp(self):
    self.interval = 23, 43
    self.vote = 'spam'
    report = create_report()
    report.addInterval(self.interval)
    report.vote(self.interval, self.vote)
    report.save()
    self.name = report.PathToSave
    return

  def test(self):
    report = cFileReport(self.name)
    self.assertSetEqual(report.getIntervalVotes(self.interval),
                        {self.vote})
  pass

class DeVote(Vote):
  def test(self):
    report = cFileReport(self.name)
    report.devote(self.interval, self.vote)
    self.assertSetEqual(report.getIntervalVotes(self.interval),
                        set())
    return

class Toggle(Vote):
  def test(self):
    report = cFileReport(self.name)
    self.assertSetEqual(report.getIntervalVotes(self.interval),
                        {self.vote})
    report.toggle(self.interval, self.vote)
    self.assertSetEqual(report.getIntervalVotes(self.interval),
                        set())
    return

class Comment(unittest.TestCase):
  def setUp(self):
    self.interval = 23, 43
    self.comment = 'pyon'
    report = create_report()
    report.addInterval(self.interval)
    report.setComment(self.interval, self.comment)
    report.save()
    self.name = report.PathToSave
    return

  def test(self):
    report = cFileReport(self.name)
    self.assertEqual(report.getComment(self.interval),
                     self.comment)
    return

class AddVote(unittest.TestCase):
  def setUp(self):
    self.vote= 'pyon'
    report = create_report()
    report.addVote(self.vote)
    report.save()
    self.name = report.PathToSave
    return

  def test(self):
    report = cFileReport(self.name)
    self.assertIn(self.vote,
                  report.getVotes())
    return

class RmVote(unittest.TestCase):
  def setUp(self):
    self.vote= 'spam'
    report = create_report()
    report.rmVote(self.vote)
    report.save()
    self.name = report.PathToSave
    return

  def test(self):
    report = cFileReport(self.name)
    self.assertNotIn(self.vote,
                     report.getVotes())
    return

def tearDownModule():
  shutil.rmtree(measproc.Report.RepDir)

if __name__ == '__main__':
  unittest.main()
