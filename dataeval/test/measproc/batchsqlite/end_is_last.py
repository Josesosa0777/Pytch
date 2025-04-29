from unittest import main

import numpy

from create_view_from_last_start import BuildBatch

class Test(BuildBatch):
  report = BuildBatch.report.copy()
  report['time'] = numpy.arange(0, 1, 1e-2)
  report['events'] = {
    ( 0,  13): {'labels': [('foo', 'bar')], 'quas': [('pyon', 'atomsk', 12.9)]},
    (50, 100): {'labels': [('foo', 'baz')], 'quas': [('pyon', 'naota',   2.9)]},
  }
  reports = [report]

  def test(self):
    lasts = dict((end, last)
                 for end, last in
                 self.batch.query('SELECT end, end_is_last FROM entryintervals'))
    self.assertDictEqual(lasts, {13: 0, 100: 1})
    return

if __name__ == '__main__':
  main()
