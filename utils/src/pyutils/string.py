def rreplace(s, old, new, count):
  """ String replacement starting at the end of the string.
  http://stackoverflow.com/questions/2556108/how-to-replace-the-last-occurence-of-an-expression-in-a-string
  """
  li = s.rsplit(old, count)
  return new.join(li)
