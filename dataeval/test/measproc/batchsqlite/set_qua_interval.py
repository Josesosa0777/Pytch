from unittest import main

from interval_queries import BuildBatch

class TestSetQua(BuildBatch):
  def test_label_interval(self):
    for idx, start, end in self.iter_intervals():
      self.batch.set_interval_qua(idx, 'pyon', 'atomsk', 42.0)
      self.assertEqual(self.batch.get_interval_qua(idx, 'pyon', 'atomsk'), 42.0)
    return

if __name__ == '__main__':
  main()
