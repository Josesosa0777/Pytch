from collections import OrderedDict

warning_cause = OrderedDict((
  ('no collision possible', OrderedDict((
    ('ghost object', [
      'ghost object', 'tunnel',
    ]),
    ('surroundings', [
      'bridge', 'overhead sign', 'ground reflection',
    ]),
  ))),
  ('collision possible', OrderedDict((
    ('infrastructure', [
      'road boundary', 'road exit', 'traffic island', 'parking vehicle',
      'roadside object', 'construction site',
    ]),
    ('traffic situation', [
      'crossing traffic', 'braking fw vehicle', 'accelerating fw vehicle',
      'overtaking', 'slower fw vehicle', 'sharp turn', 'in-lane obstacle',
      'passing by', 'following',
    ]),
  ))),
))


def poplevel(dd):
  res = OrderedDict()
  for v in dd.itervalues():
    for k2, v2 in v.iteritems():
      res[k2] = v2
  return res

def expand(dd):
  values = []
  for v in dd.itervalues():
    values += v
  return values

def reverse2(dd):
  res = OrderedDict()
  for k, v in dd.iteritems():
    for v2 in v:
      res[v2] = k
  return res


maingroup2labels = poplevel(warning_cause)

label2maingroup = reverse2(maingroup2labels)

all_labels = expand(maingroup2labels)



#def reverse1(dd):
#  inv_map = OrderedDict()
#  for k, v in dd.iteritems():
#    inv_map.setdefault(v, []).append(k)

#def reverse(dd):
#  return OrderedDict((v, k) for k, v in map.iteritems())

if __name__ == "__main__":
  print 1, maingroup2labels
  print 2, label2maingroup
  print 3, all_labels
