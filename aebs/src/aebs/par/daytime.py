from collections import OrderedDict

daytime_dict = OrderedDict((
  ( 0, u'day'),
  ( 1, u'night'),
  ( 2, u'dusk'),
))

maingroup2labels = OrderedDict((
  ('day', [
    'day',
  ]),
  ('night', [
    'night', 'dusk',
  ]),
))

label2color = {
  'day': (0.0, 1.0, 0.0),  # green
  'night': '0.3',
  'dusk': '0.6',
}

maingroup2color = {
  'day': label2color['day'],
  'night': label2color['night'],
}

def reverse2(dd):
  res = OrderedDict()
  for k, v in dd.iteritems():
    for v2 in v:
      res[v2] = k
  return res


label2maingroup = reverse2(maingroup2labels)
