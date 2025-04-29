def conv_float(value, format_spec="%.2f"):
  if isinstance(value, float):
    value = format_spec % value
  return value

def vector2scalar(value, none_value=None):
  if value is None:
    return none_value
  if isinstance(value, (list, tuple, set)):
    if len(value) == 0:
      return none_value
    assert len(value) == 1, "0 or 1 value is accepted, found %d" % len(value)
    return value[0]
  return value

def vector2scalar2(value, none_value=None):
  if value is None:
    return none_value
  if isinstance(value, (list, tuple, set)):
    if len(value) == 0:
      return none_value
    else:
     return ', '.join(str(x) for x in value)
  return value