from measproc.IntervalList import intervalsToMask, maskToIntervals
from primitives.bases import Primitive

class LdwsStatus(Primitive):
  def __init__(self, time,warning, ready, deactivate_by_driver):
    Primitive.__init__(self, time)
    # phases
    self.warning = warning
    self.ready = ready
    self.deactivate_by_driver = deactivate_by_driver
    return

  def merge_phases(self, level):
    if level == 0:
      return [], []
      
    phases = [self.warning, self.ready, self.deactivate_by_driver]

    merge = maskToIntervals(phases[0])
    jump = [[start] for start, end in merge]
    for mask in phases[1:level]:
      intervals = maskToIntervals(mask)
      jump, merge = self.join_phases(jump, merge, intervals)
    return jump, merge

  @staticmethod
  def join_phases(jumps, head, tail):
    """
    >>> head =  [(12, 34), (56, 58), (92, 93)]
    >>> jumps = [[12],     [56],     [92]]
    >>> tail =  [(34, 45), (58, 66)]
    >>> LdwsStatus.join_phases(jumps, head, tail)
    ([[12, 34], [56, 58], [92]], [(12, 45), (56, 66), (92, 93)])
    """
    join = []
    for jump, (head_start, head_end) in zip(jumps, head):
      for tail_part in tail:
        tail_start, tail_end = tail_part
        if tail_start == head_end:
          join.append( (head_start, tail_end) )
          jump.append(tail_start)
          break
      else:
        join.append( (head_start, head_end) )
        continue
      tail.remove(tail_part)
    return jumps, join

