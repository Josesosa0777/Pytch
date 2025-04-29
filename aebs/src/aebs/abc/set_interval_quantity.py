# -*- dataeval: init -*-

from interface.Interfaces import iCalc

class Calc(iCalc):
  # Class variables to be overridden in descendant class
  dep = None             # e.g. ('calc_egomotion',)
  quantity_group = None  # e.g. 'ego vehicle'
  quantity = None        # e.g. 'speed start'
  
  def __call__(self, report):
    """
    Sets the pre-defined quantity to all intervals of the given report.
    """
    quas = self.batch.get_quanamegroup(self.quantity_group)
    report.setNames(self.quantity_group, quas)
    
    fill = self.modules.fill(self.dep[0]).rescale(report.intervallist.Time)
    
    for idx, (start, end) in report.iterIntervalsWithId():
      report.set(idx, self.quantity_group, self.quantity,
                 self.calc_quantity(fill, start, end))
    return
  
  def calc_quantity(self, fill, start, end):
    """
    Defines how to calculate the quantity (specified in the class) for a given
    interval, based on the given dependency's result.
    
    To be overridden in descendant class.
    """
    raise NotImplementedError()  # e.g.  return fill.vx[start]
