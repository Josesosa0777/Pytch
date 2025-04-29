import unittest

import numpy

from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

class TestCase(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 10, 1e-2)
    intervallist = cIntervalList(time)
    self.title = 'foo likes pyon'
    self.report = Report(intervallist, self.title)
    self.report.addVoteGroups({'pyon':    (True,  ['atomsk', 'naota']),
                               'bazinga': (False, ['warm',   'kitty'])})
    return

  def test_getTitle(self):
    self.assertEqual(self.report.getTitle(), self.title)
    return

  def test_getEntryComment(self):
    self.comment = 'spamspam'
    self.report.setEntryComment(self.comment)
    self.assertEqual(self.report.getEntryComment(), self.comment)
    return

  def test_addInterval(self):
    interval = 11, 22
    intervalid = self.report.addInterval(interval)
    return

  def test_addVoteGroup(self):
    groupname = 'spam'
    exclusive = False
    votes = 'egg', 'eggegg'
    self.report.addVoteGroup(groupname, exclusive, votes)
    return

  def test_addVoteGroups(self):
    votegroups = {'foo': (True,  ['bar', 'baz']),
                  'goo': (False, ['car', 'caz'])}
    self.report.addVoteGroups(votegroups)
    return
  
  def test_vote(self):
    interval = 1, 2
    groupname = 'pyon'
    vote = 'atomsk'
    intervalid = self.report.addInterval(interval)
    self.report.vote(intervalid, groupname, vote)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote))
    return

  def test_vote_exclusive(self):
    interval = 2, 3
    groupname = 'pyon'
    vote1 = 'atomsk'
    intervalid = self.report.addInterval(interval)
    self.report.vote(intervalid, groupname, vote1)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote1))
    vote2 = 'naota'
    self.report.vote(intervalid, groupname, vote2)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote2))
    self.assertFalse(self.report.checkVote(intervalid, groupname, vote1))
    return

  def test_vote_nonexclusive(self):
    interval = 3, 4
    groupname = 'bazinga'
    vote1 = 'warm'
    intervalid = self.report.addInterval(interval)
    self.report.vote(intervalid, groupname, vote1)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote1))
    vote2 = 'kitty'
    self.report.vote(intervalid, groupname, vote2)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote2))
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote1))
    return

  def test_devote(self):
    interval = 4, 5
    groupname = 'pyon'
    vote = 'atomsk'
    intervalid = self.report.addInterval(interval)
    self.report.vote(intervalid, groupname, vote)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote))
    self.report.devote(intervalid, groupname, vote)
    self.assertFalse(self.report.checkVote(intervalid, groupname, vote))
    return
  
  def test_toggle(self):
    interval = 5, 6
    groupname = 'pyon'
    vote = 'atomsk'
    intervalid = self.report.addInterval(interval)
    self.report.toggle(intervalid, groupname, vote)
    self.assertTrue(self.report.checkVote(intervalid, groupname, vote))
    self.report.toggle(intervalid, groupname, vote)
    self.assertFalse(self.report.checkVote(intervalid, groupname, vote))
    return

  def test_rmVoteGroup(self):
    groupname = 'spam'
    exclusive = False
    votes = 'egg', 'eggegg'
    self.report.addVoteGroup(groupname, exclusive, votes)
    self.report.rmVoteGroup(groupname)
    return

class TestReportSort(unittest.TestCase):
  def setUp(self):
    time = numpy.arange(0, 10, 1e-2)
    intervallist = cIntervalList(time)
    self.title = 'foo likes pyon'
    self.report = Report(intervallist, self.title)
    self.report.addVoteGroups({'pyon':    (True,  ['atomsk', 'naota']),
                               'bazinga': (False, ['warm',   'kitty'])})
    index = self.report.addInterval( (3,5) )
    self.report.vote(index, 'pyon', 'naota')
    index = self.report.addInterval( (8,10) )
    self.report.vote(index, 'bazinga','warm')
    self.report.setComment(index, 'baaad')
    index = self.report.addInterval( (0,1) )
    self.report.vote(index, 'pyon', 'atomsk')
    self.report.setComment(index, 'soso')
    self.report.sort()
    return

  def test_sort_intervallist(self):
    self.assertTrue(self.report.intervallist == [(0,1), (3,5), (8,10)])
    return

  def test_sort_intervallist_comment(self):
    self.assertTrue(self.report.getComment(0) == 'soso')
    return

  def test_sort_intervallist_votes(self):
    self.assertTrue( self.report.checkVote(2, 'bazinga', 'warm') )
    return

if __name__ == '__main__':
  unittest.main()
