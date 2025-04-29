from collections import OrderedDict

lane_quality_dict = OrderedDict((
  (0  , u'0..25'),
  (1  , u'26..50'),
  (2  , u'51..75'),
  (3  , u'76..100')
))

maingroup2labels = OrderedDict((
  ('operational', [
    '76..100', '51..75', '26..50'
  ]),
  ('deactivated', [
    '0..25',
  ]),
  ('error', [
    'Not Available'
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
