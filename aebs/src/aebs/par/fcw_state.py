from collections import OrderedDict

fcw_state_dict = OrderedDict((
  ( 0, u'Not ready'),
  ( 1, u'Temporary n/a'),
  ( 2, u'Deactivated by driver'),
  ( 3, u'Ready'),
  ( 4, u'Driver override'),
  ( 5, u'Collision warning active'),
  ( 6, u'Collision warning with braking'),
  (14, u'Error'),
  (15, u'Not available'),
))

maingroup2labels = OrderedDict((
  ('operational', [
    'Temporary n/a', 'Ready', 'Driver override', 'Collision warning active',
    'Collision warning with braking',
  ]),
  ('deactivated', [
    'Deactivated by driver',
  ]),
  ('error', [
    'Error', 'Not available', 'Not ready',
  ]),
))

maingroup2color = {
  'operational': (0.0, 1.0, 0.0),
  'deactivated': '0.75',
  'error': 'r',
}

def reverse2(dd):
  res = OrderedDict()
  for k, v in dd.iteritems():
    for v2 in v:
      res[v2] = k
  return res


label2maingroup = reverse2(maingroup2labels)