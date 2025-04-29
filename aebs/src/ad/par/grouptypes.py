"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.

Type definitions for groups
"""

__docformat__ = "restructuredtext en"

NONES = {'NONE_TYPE'}

MEAS_TRAJ = {'MEAS_TRAJ', 'NONE_TYPE'}

REC_TRAJ = {'REC_TRAJ', 'NONE_TYPE'}

DIFF_TRAJ = {'DIFF_TRAJ', 'NONE_TYPE'}

TRAJ_GEN_POLY = {'TRAJ_GEN_POLY', 'NONE_TYPE'}
TRAJ_GEN_POLY_VEL = {'TRAJ_GEN_POLY_VEL', 'NONE_TYPE'}

TRAJ_GEN_BEZIER = {'TRAJ_GEN_BEZIER', 'NONE_TYPE'}
TRAJ_GEN_BEZIER_VEL = {'TRAJ_GEN_BEZIER_VEL', 'NONE_TYPE'}

GroupTypes = set()
for Name, Value in globals().items():
  if Name == 'GroupTypes' or not isinstance(Value, set): continue
  GroupTypes.update(Value)

if __name__ == '__main__':
  print NONES
