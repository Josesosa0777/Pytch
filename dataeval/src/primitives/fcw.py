from measproc.IntervalList import maskToIntervals
from primitives.bases import Primitive
import numpy as np


class FcwPhases(Primitive):
    def __init__(self, time, prelimnary_warning, collision_warning):
        Primitive.__init__(self, time)
        # phases
        self.prelimnary_warning = prelimnary_warning
        self.collision_warning = collision_warning

        return

    def merge_phases(self, level):
        if level == 0:
            return [], []

        phases = [self.prelimnary_warning, self.collision_warning]

        if (np.any(phases[0])) and (np.any(phases[1])):
            merge = maskToIntervals(phases[1])
            boolean_state = True
        else:
            merge = maskToIntervals(phases[0])
            boolean_state = False

        jump = [[start] for start, end in merge]
        for mask in phases[1:level]:
            intervals = maskToIntervals(mask)
            jump, merge = self.join_phases(jump, merge, intervals)
        return jump, merge, boolean_state

    @staticmethod
    def join_phases(jumps, head, tail):
        """
        >>> head =  [(12, 34), (56, 58), (92, 93)]
        >>> jumps = [[12],     [56],     [92]]
        >>> tail =  [(34, 45), (58, 66)]
        >>> FcwPhases.join_phases(jumps, head, tail)
        ([[12, 34], [56, 58], [92]], [(12, 45), (56, 66), (92, 93)])
        """
        join = []
        for jump, (head_start, head_end) in zip(jumps, head):
            for tail_part in tail:
                tail_start, tail_end = tail_part
                if tail_start == head_end:
                    join.append((head_start, tail_end))
                    jump.append(tail_start)
                    break
            else:
                join.append((head_start, head_end))
                continue
            tail.remove(tail_part)
        return jumps, join
