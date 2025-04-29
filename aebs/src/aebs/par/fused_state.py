from collections import OrderedDict

fused_dict = OrderedDict((
  (0  , u'None'),
  (1  , u'Prediction'),
  (2  , u'Radar only'),
  (3  , u'Camera only'),
  (4  , u'Fused')
))

maingroup2labels = OrderedDict((
  ('operational', [
    'Camera only', 'Radar only', 'Prediction', 'Fused'
  ]),
  ('deactivated', [
    'None',
  ])
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
