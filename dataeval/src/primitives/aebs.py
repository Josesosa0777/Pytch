from measproc.IntervalList import intervalsToMask, maskToIntervals
from primitives.bases import Primitive

class AebsPhases(Primitive):
  def __init__(self, time,
               warning, partial, emergency, incrash,
               acoustical, optical):
    Primitive.__init__(self, time)
    # phases
    self.warning = warning
    self.partial_braking = partial
    self.emergency_braking = emergency
    self.incrash_braking = incrash
    # hmi
    self.acoustical_warning = acoustical
    self.optical_warning = optical
    return

  def merge_phases(self, level):
    if level == 0:
      return [], []
      
    phases = [self.warning, self.partial_braking, self.emergency_braking,
              self.incrash_braking]

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
    >>> AebsPhases.join_phases(jumps, head, tail)
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

