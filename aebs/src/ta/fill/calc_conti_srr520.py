# -*- dataeval: init -*-

import numpy as np

from collections import OrderedDict
from interface import iCalc
from primitives.bases import Primitive, PrimitiveCollection
from measparser.signalgroup import SignalGroupError

# defining how a signal group will look like
signal_group_template_list = [{
    "x"          : ("SRR_OBJ_{track_id:02d}_C", "fDistX_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_C_CAN2"),
    "y"          : ("SRR_OBJ_{track_id:02d}_C", "fDistY_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_C_CAN2"),
    "speed_x"    : ("SRR_OBJ_{track_id:02d}_B", "fVrelX_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_B_CAN2"),
    "speed_y"    : ("SRR_OBJ_{track_id:02d}_B", "fVrelY_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_B_CAN2"),
    "class"      : ("SRR_OBJ_{track_id:02d}_A", "eObjType_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_A_CAN2"),
    "moving"     : ("SRR_OBJ_{track_id:02d}_D", "eDynamicProperty_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_D_CAN2"),
    "valid"      : ("SRR_OBJ_{track_id:02d}_C", "bObjectValid_SrrRLObj{track_id:02d}_SRR_OBJ_{track_id:02d}_C_CAN2")
},
{
    "x"         : ("SRR_OBJ_{track_id:02d}_C", "fDistX_SrrRLObj{track_id:02d}"),
    "y"         : ("SRR_OBJ_{track_id:02d}_C", "fDistY_SrrRLObj{track_id:02d}"),
    "speed_x"   : ("SRR_OBJ_{track_id:02d}_B", "fVrelX_SrrRLObj{track_id:02d}"),
    "speed_y"   : ("SRR_OBJ_{track_id:02d}_B", "fVrelY_SrrRLObj{track_id:02d}"),
    "class"     : ("SRR_OBJ_{track_id:02d}_A", "eObjType_SrrRLObj{track_id:02d}"),
    "moving"    : ("SRR_OBJ_{track_id:02d}_D", "eDynamicProperty_SrrRLObj{track_id:02d}"),
    "valid"     : ("SRR_OBJ_{track_id:02d}_C", "bObjectValid_SrrRLObj{track_id:02d}")
},
]


class SRR520Objects(Primitive):

    def __init__(self, id, common_time, group):
        super(SRR520Objects, self).__init__(common_time)
        self._group = group
        self.x = self._group.get_value("x", ScaleTime=self.time)
        self.y = self._group.get_value("y", ScaleTime=self.time)
        self.speed_x = self._group.get_value("speed_x", ScaleTime=self.time)
        self.speed_y = self._group.get_value("speed_y", ScaleTime=self.time)
        self.obj_class = self._group.get_value("class", ScaleTime=self.time)
        self.moving = self._group.get_value("moving", ScaleTime=self.time)
        self.valid = self._group.get_value("valid", ScaleTime=self.time)
        self.id = id
        return


class Calc(iCalc):

    def check(self):
        groups = OrderedDict()
        for msg_num in xrange(12):
            sg = [{ alias: (devtempl.format(track_id=msg_num), sigtempl.format(track_id=msg_num))
                   for alias, (devtempl, sigtempl) in
                   signal_group_template.iteritems() }
                   for signal_group_template in signal_group_template_list]
            try:
                groups[msg_num] = self.source.selectSignalGroup(sg)
            # if the error is raised on the 6th message then it is a single radar config, else pass the error
            except SignalGroupError:
                if msg_num == 6:
                    break
                else:
                    raise
        return groups

    def fill(self, groups):
        common_time = groups[0].get_time("x")
        targets = PrimitiveCollection(common_time)
        for id, group in groups.iteritems():
            targets[id] = SRR520Objects(id, common_time, group)
        return targets


if __name__ == '__main__':
    from config.Config import init_dataeval
    meas_path = r'C:\KBData\TAevalData\DAF__2018-04-25\DAF__2018-04-25_09-20-38.mat'
    # meas_path = r'C:\KBData\TAevalData\DAF__2018-04-25_07-03-26.mat'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    srr520 = manager_modules.calc('calc_conti_srr520@ta.fill', manager)
    dummy_id, dummy_target = srr520.iteritems().next()
    print dummy_id
    print dummy_target.x
    print dummy_target.y
