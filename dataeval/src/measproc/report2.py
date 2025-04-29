from copy import deepcopy, copy

from IntervalList import cIntervalList

class IntervalListContainer:
  def __init__(self, intervallist, title):
    self.title = title
    self.intervallist = intervallist.copy()
    self.comment = ''
    return

  def copy_into(self, other): 
    other.title = self.title
    other.comment = self.comment
    return other

  def rescale(self, time):
    intervallist = self.intervallist.rescale(time)
    return intervallist

  def getEntryComment(self):
    return self.comment

  def setEntryComment(self, comment):
    self.comment = comment
    return

  def isEmpty(self):
    return self.intervallist.isEmpty()

  def _addInterval(self, interval):
    lower, upper = interval
    return self.intervallist.add(lower, upper)

  def _sort(self, **kwargs):
    indices = self.intervallist.argsort(**kwargs)
    self.intervallist.reorder(indices)
    return indices

  def getIntervalIndices(self, interval):
    lower, upper = interval
    return self.intervallist.getIntervalIndices(lower, upper)
    
  def iterIntervalIds(self):
    return xrange(len(self.intervallist))

  def iterIntervalsWithId(self):
    return enumerate(self.intervallist)

  def _rmInterval(self, intervalid):
    self.intervallist.pop(intervalid)
    return

  def getTitle(self):
    return self.title
 
  def getTimeInterval(self, intervalid):
    lower, upper = self.intervallist[intervalid]
    return self.intervallist.getTimeInterval(lower, upper)

  def getTimeIndex(self, time):
    return self.intervallist.getTimeIndex(time)

  def findIntervals(self, time):
    index = self.getTimeIndex(time)
    return self.intervallist.findIntervals(index)

  def findIntervalIds(self, time):
    index = self.getTimeIndex(time)
    return self.intervallist.findIntervalIds(index)

  def findIntervalIdsWithin(self, interval):
    lower, upper = interval
    ids = self.intervallist.findIntervalIdsWithin(lower, upper)
    return ids

class Quantity(IntervalListContainer):
  def __init__(self, intervallist, title, names):
    """
    :Parameters:
      intervallist : `measproc.IntervalList.cIntervalList`
      title : str
      names : dict
        {groupname<str>: [valuename<str>]}
    """
    IntervalListContainer.__init__(self, intervallist, title)
    self._quantities = [{} for e in xrange(len(intervallist))]
    self._names = names
    return

  def copy_into(self, other):
    IntervalListContainer.copy_into(self, other)
    other._quantities = deepcopy(self._quantities)
    return other

  def addInterval(self, interval):
    self._quantities.append({})
    return self._addInterval(interval)

  def addSingletonInterval(self, interval):
    """
    Add the given interval to the report - if not yet already part of it.
    ValueError is raised if multiple instances of the given interval already
    exist in the report.
    """
    if interval not in self.intervallist:
      # interval not yet existing
      index = self.addInterval(interval)
    else:
      # interval already exists
      inds = self.getIntervalIndices(interval)
      if len(inds) > 1:
        # multiple instances already exist --> can't be singleton
        raise ValueError("Multiple instances of the given interval already exist")
      index = inds[0]
    return index

  def rmInterval(self, intervalid):
    self._rmInterval(intervalid)
    del self._quantities[intervalid]
    return

  def set(self, intervalid, groupname, valuename, value):
    self.check(intervalid, groupname, valuename)
    quantities = self._quantities[intervalid]
    group = quantities.setdefault(groupname, {})
    if isinstance(value,str):
      if '0x' in value :
        group[valuename] = (value if value is not None else 'nan')
    else:
      group[valuename] = float(value if value is not None else 'nan')
    return

  def check(self, intervalid, groupname, valuename):
    self.checkName(groupname, valuename)
    self.checkIntervalId(intervalid)
    return

  def checkName(self, groupname, valuename):
    assert groupname in self._names,\
           '%s is not a registered group name' %groupname
    assert valuename in self._names[groupname],\
           '%s is not a registered name in %s group' %(valuename, groupname)
    return

  def checkIntervalId(self, intervalid):
    assert intervalid < len(self._quantities),\
    'Invalid interval id: %d' %intervalid
    return

  def get(self, intervalid, groupname, valuename, *args):
    try:
      self.check(intervalid, groupname, valuename)
    except AssertionError:
      if args:
        value, = args
      else:
        raise
    else:
      quantities = self._quantities[intervalid]
      value = quantities[groupname][valuename]
    return value

  def pop(self, intervalid, groupname, valuename, *args):
    try:
      self.check(intervalid, groupname, valuename)
    except AssertionError:
      if args:
        value, = args
      else:
        raise
    else:
      quantities = self._quantities[intervalid]
      value = quantities[groupname].pop(valuename)
    return value

  def sort(self, **kwargs):
    indices = self._sort(**kwargs)
    self._quantities[:] = [self._quantities[i] for i in indices]
    return indices

  def setNames(self, groupname, valuenames):
    self._names[groupname] = valuenames
    return

  def getNames(self):
    return self._names

  def getQuantities(self, intervalid):
    """
    :Parameters:
      intervalid : int
    :ReturnType: dict
    :Return: {groupname<str>: {valuename<str>: value<float>}}
    """
    self.checkIntervalId(intervalid)
    return self._quantities[intervalid]


class Report(Quantity):
  def __init__(self, intervallist, title, votes=None, names=None):
    names = names if names is not None else {}
    votes = votes if votes is not None else {}

    Quantity.__init__(self, intervallist, title, names)

    self.comments = ['' for e in xrange(len(intervallist))]
    self.votes = [{} for e in xrange(len(intervallist))]
    self.exclusives = set()
    self.groupnames = {}
    self.addVoteGroups(votes)
    return

  def copy_into(self, other):
    Quantity.copy_into(self, other)
    other.comments  = copy(self.comments)
    other.votes = deepcopy(self.votes)
    return other

  def rescale(self, time):
    intervallist = IntervalListContainer.rescale(self, time)
    scaled = Report(intervallist, self.title, votes=self.getVoteGroups(),
                    names=self.getNames())
    self.copy_into(scaled)
    return scaled

  @classmethod
  def from_reportxml(cls, report, delete, rename, vote2label, labels):
    votes = [rename.get(vote, vote) for vote in report.getVotes()
             if vote not in delete]
    _labels = {}
    for vote in votes:
      groupname = vote2label[vote]
      _labels[groupname] = labels[groupname]
    title = report.getTitle()
    self = cls(report.IntervalList, title, _labels)
    self.setEntryComment(report.ReportAttrs['Comment'])

    for i, interval in enumerate(report.IntervalList):
      comment = report.getComment(interval)
      self.setComment(i, comment)
      for vote in report.getIntervalVotes(interval):
        if vote in delete: continue
        vote = rename.get(vote, vote)
        groupname = vote2label[vote]
        self.vote(i, groupname, vote)
    return self

  def __str__(self):
    lines = []
    for intervalid, votegroups in enumerate(self.votes):
      lower, upper = self.intervallist[intervalid]
      lines.append('#%d [%d-%d]' %(intervalid, lower, upper))
      for groupname, votes in votegroups.iteritems():
        line = [groupname, ','.join(votes)]
        line = '='.join(line)
        lines.append(line)
    return '\n'.join(lines)

  def addInterval(self, interval):
    self.votes.append({})
    self.comments.append('')
    return Quantity.addInterval(self, interval)

  def sort(self, **kwargs):
    """
    Sort the intervals and corresponding report items.

    :Keywords:
      cmp : function
        Comparison function
      reverse : bool
        Sort in reverse order, default is False.
    """
    indices = Quantity.sort(self, **kwargs)
    self.votes[:] = [self.votes[i] for i in indices]
    self.comments[:] = [self.comments[i] for i in indices]
    return

  def rmInterval(self, intervalid):
    Quantity.rmInterval(self, intervalid)
    del self.comments[intervalid]
    del self.votes[intervalid]
    return

  def addVoteGroup(self, groupname, exclusive, votes):
    if exclusive:
      self.exclusives.add(groupname)
    self.groupnames[groupname] = votes
    return

  def addVoteGroups(self, votes):
    for groupname, (exclusive, votes) in votes.iteritems():
      self.addVoteGroup(groupname, exclusive, votes)
    return

  def getVoteGroup(self, groupname):
    return self.isVoteGroupExclusive(groupname), self.groupnames[groupname]

  def getVoteGroups(self):
    return dict([(groupname, self.getVoteGroup(groupname))
                 for groupname in self.groupnames])

  def hasVoteGroup(self, groupname):
    return groupname in self.groupnames

  def isVoteGroupExclusive(self, groupname):
    return groupname in self.exclusives

  def rmVoteGroup(self, groupname):
    if groupname in self.exclusives:
      self.exclusives.remove(groupname)
    for votegroups in self.votes:
      if groupname in votegroups:
        del votegroups[groupname]
    return

  def setComment(self, intervalid, comment):
    self.comments[intervalid] = comment
    return

  def getComment(self, intervalid):
    return self.comments[intervalid]

  def vote(self, intervalid, groupname, vote):
    votegroups = self.votes[intervalid]
    if groupname not in self.exclusives:
      votegroup = votegroups.setdefault(groupname, set())
      votegroup.add(vote)
    else:
      votegroups[groupname] = {vote}
    return
 
  def devote(self, intervalid, groupname, vote):
    votegroups = self.votes[intervalid]
    votegroup = votegroups[groupname]
    votegroup.remove(vote)
    return

  def toggle(self, intervalid, groupname, vote):
    votegroups = self.votes[intervalid]
    votegroup = votegroups.setdefault(groupname, set())
    if vote in votegroup:
      if groupname not in self.exclusives:
        votegroup.remove(vote)
      else:
        votegroup.clear()
    else:
      if groupname in self.exclusives:
        votegroup.clear()
      votegroup.add(vote)
    return

  def checkVote(self, intervalid, groupname, vote):
    votegroups = self.votes[intervalid]
    if groupname in votegroups:
      votegroup = votegroups[groupname]
      return vote in votegroup
    else:
      return False

  def getVotes(self, intervalid):
    return self.votes[intervalid]

  def getIntervallistByVote(self, groupname, vote):
    intervallist = cIntervalList(self.intervallist.Time)
    for id, (lower, upper) in self.iterIntervalsWithId():
      if self.checkVote(id, groupname, vote):
        intervallist.add(lower, upper)
    return intervallist
  
class CreateParams:
  def __init__(self, time, title, labels, comment=''):
    self.time = time
    self.title = title
    self.labels = labels
    self.comment = comment
    return

  def __call__(self):
    intervallist = cIntervalList(self.time)
    report = Report(intervallist, self.title, self.labels)
    report.setEntryComment(self.comment)
    return report


class IntervalAddParams:
  def __init__(self, interval, votegroup, vote, comment=''):
    self.interval = interval
    self.votegroup = votegroup
    self.vote = vote
    self.comment = comment
    return

  def __call__(self, report):
    intervalid = report.addInterval(self.interval)
    report.vote(intervalid, self.votegroup, self.vote)
    report.setComment(intervalid, self.comment)
    return intervalid


class CreateQuantity:
  def __init__(self, time, title, names):
    self.time = time
    self.title = title
    self.names = names
    return

  def __call__(self):
    intervallist = cIntervalList(self.time)
    quantity = Report(intervallist, self.title, names=self.names)
    return quantity

class AddQuantity:
  def __init__(self, interval, groupname, valuename, value):
    self.interval = interval
    self.groupname = groupname
    self.valuename = valuename
    self.value = value
    return

  def __call__(self, quantity):
    intervalid = quantity.addInterval(self.interval)
    quantity.set(intervalid, self.groupname, self.valuename, self.value)
    return intervalid

