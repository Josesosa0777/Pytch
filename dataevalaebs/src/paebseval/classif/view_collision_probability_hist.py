# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

"""
Sum up the occurences of collision probability values at warning start.
"""

from aebs.abc.view_quantity_hist import init_params, View, Probability

class View(View):

  search_class = 'paebseval.search_events_paeb.Search'
  entry_title = 'PAEBS warnings'
  quanamegroup = 'PAEBS Debug'
  quaname = 'collision probability'
  base_title = "PAEBS Collision Probability at Warning Start [%]"
  bins = xrange(0,105,5)
  hist_kwargs = {'cumulative':True,'color':'r'}
  
