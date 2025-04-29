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

CONTI_SRR320 ={'CONTI_SRR320', 'NONE_TYPE'}
CONTI_SRR520_radar_1 ={'CONTI_SRR520_radar_1', 'NONE_TYPE'}
CONTI_SRR520_radar_2 ={'CONTI_SRR520_radar_2', 'NONE_TYPE'}

BSM_CAM = {'BSM_CAM', 'NONE_TYPE'}
BSM_LS = {'BSM_LS', 'NONE_TYPE'}
BSM_HS = {'BSM_HS', 'NONE_TYPE'}
BSM_DRAD_LONG = {'BSM_DRAD_LONG', 'NONE_TYPE'}
BSM_DRAD_LAT = {'BSM_DRAD_LAT', 'NONE_TYPE'}

GroupTypes = set()
for Name, Value in globals().items():
  if Name == 'GroupTypes' or not isinstance(Value, set): continue
  GroupTypes.update(Value)

if __name__ == '__main__':
  print NONES
