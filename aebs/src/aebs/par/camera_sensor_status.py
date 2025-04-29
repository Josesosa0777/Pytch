from collections import OrderedDict
from itertools import chain

flc20_sensor_status_dict = OrderedDict((
  ( 0, u'Fully Operational'),
  ( 1, u'Warming up / Initializing'),
  ( 2, u'Partially Blocked'),
  ( 3, u'Blocked'),
  ( 4, u'Misaligned'),
  ( 5, u'Slightly Blocked'),  # was 'Reserved' before
  ( 6, u'Reserved'),
  ( 7, u'Reserved'),
  ( 8, u'Reserved'),
  ( 9, u'Reserved'),
  (10, u'Reserved'),
  (11, u'Reserved'),
  (12, u'Reserved'),
  (13, u'Reserved'),
  (14, u'Error'),
  (15, u'NotAvailable'),
))

#flc20_sensor_status_2_dict = {
#   0: u'Fully Operational',
#   1: u'Warming up/Initializing',
#   2: u'Image Degraded/Objects Invalid',
#   3: u'Camera Blocked/No Image',
#   4: u'Misaligned',
#   5: u'Image Degraded/Objects Valid',
#   6: u'Reserved',
#   7: u'Reserved',
#   8: u'Reserved',
#   9: u'Reserved',
#  10: u'Reserved',
#  11: u'Reserved',
#  12: u'Reserved',
#  13: u'Reserved',
#  14: u'Permanent Error',
#  15: u'Not Available',
#}

maingroup2labels = OrderedDict((
  ('operational', [
    'Fully Operational', 'Slightly Blocked',
  ]),
  ('reduced performance', [
    'Partially Blocked', 'Misaligned',
  ]),
  ('blocked', [
    'Blocked',
  ]),
  ('n/a', [
    'Error', 'NotAvailable', 'Warming up / Initializing', 'Reserved',
  ]),
))
assert set(chain(*maingroup2labels.values())) == set(flc20_sensor_status_dict.itervalues())

label2color = {
  'Fully Operational':         (0.0, 1.0, 0.0),
  'Warming up / Initializing': (0.0, 0.8, 0.0),
  'Misaligned':                (0.0, 0.6, 0.0),
  'Slightly Blocked':          (0.0, 0.4, 0.0),
  'Partially Blocked':         (0.5, 0.5, 0.5),
  'Blocked':                   (0.0, 0.0, 0.0),
  'Error':                     (1.0, 0.0, 0.0),
  'Reserved':                  (1.0, 0.0, 0.0),
  'NotAvailable':              (0.7, 0.0, 0.0),
}
assert set(label2color) == set(flc20_sensor_status_dict.itervalues())

maingroup2color = {
  'operational':         (0.0, 1.0, 0.0),
  'reduced performance': (0.0, 0.4, 0.0),
  'blocked':             (0.0, 0.0, 0.0),
  'n/a':                 (1.0, 0.0, 0.0),
}
assert set(maingroup2color) == set(maingroup2labels)

def reverse2(dd):
  res = OrderedDict()
  for k, v in dd.iteritems():
    for v2 in v:
      res[v2] = k
  return res


label2maingroup = reverse2(maingroup2labels)
