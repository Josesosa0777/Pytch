# -*- dataeval: init -*-

from interface.Interfaces import iCalc

calculators = {
  'start': lambda signal, st, end: signal[st],
  'end':   lambda signal, st, end: signal[end-1],
  'min':   lambda signal, st, end: signal[st:end].min(),
  'max':   lambda signal, st, end: signal[st:end].max(),
  'avg':   lambda signal, st, end: signal[st:end].mean(),
  'std':   lambda signal, st, end: signal[st:end].std(),
 #'diff':  lambda signal, st, end: signal[end-1] - signal[st],
}
init_params = dict((key, dict(quantity_kind=key)) for key in calculators)

class Calc(iCalc):
  # Class variables to be overridden in descendant class
  dep = None             # e.g. ('calc_egomotion',)
  quantity_group = None  # e.g. 'ego vehicle'
  quantity_base = None   # e.g. 'speed'
  
  def init(self, quantity_kind):
    self.quantity_kind = quantity_kind
    return
  
  def __call__(self, report):
    """
    Sets the pre-defined quantity to all intervals of the given report.
    """
    quantity = "%s %s" % (self.quantity_base, self.quantity_kind)
    quas = self.batch.get_quanamegroup(self.quantity_group)
    assert quantity in quas, "Not registered quantity: '%s'" % quantity
    report.setNames(self.quantity_group, quas)
    
    fill = self.modules.fill(self.dep[0]).rescale(report.intervallist.Time)
    signal = self.calc_signal(fill)
    
    for idx, (start, end) in report.iterIntervalsWithId():
      report.set(idx, self.quantity_group, quantity,
        self.calc_quantity_for_signal(signal, start, end))
    return
  
  def calc_signal(self, fill):
    """
    Defines how to calculate the signal that is the basis of the quantity
    calculation, based on the given dependency's result.
    
    To be overridden in descendant class.
    """
    raise NotImplementedError()  # e.g.  return fill.vx
  
  def calc_quantity_for_signal(self, signal, start, end):
    return calculators[self.quantity_kind](signal, start, end)
