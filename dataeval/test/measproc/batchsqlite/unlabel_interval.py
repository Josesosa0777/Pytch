from unittest import main

from interval_queries import BuildBatch

class TestLabel(BuildBatch):
  def test_unlabel_interval(self):
    for idx, start, end in self.iter_intervals():
      self.batch.unlabel_interval(idx, 'foo', 'bar')
      self.assertListEqual(self.batch.get_interval_labels(idx, 'foo'), [])
    return

if __name__ == '__main__':
  main()
