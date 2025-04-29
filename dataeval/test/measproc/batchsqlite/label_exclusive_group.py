from unittest import main

from interval_queries import BuildBatch

class TestLabel(BuildBatch):
  labels = {'foo': (True, ['bar', 'baz'])}
  def test_label_interval(self):
    for idx, start, end in self.iter_intervals():
      self.assertListEqual(self.batch.get_interval_labels(idx, 'foo'), ['bar'])
      self.batch.label_interval(idx, 'foo', 'baz')
      self.assertListEqual(self.batch.get_interval_labels(idx, 'foo'), ['baz'])
    return

if __name__ == '__main__':
  main()
