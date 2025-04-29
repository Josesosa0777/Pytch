"""
Plot histogram of a quantity
"""

import importlib

import numpy as np

import datavis
from interface import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

import view_quantity_vs_status_stats


init_params = {
  'duration': dict(kind_class="Duration"),
  'mileage' : dict(kind_class="Mileage"),
  'probability' : dict(kind_class="Probability"),
}


class View(iView):
  search_class = None  # search class to filter for (TBD)
  entry_title = "%"    # match all entry titles (do not filter) by default
  quanamegroup = None  # quantity group to filter for (TBD)
  quaname = None       # quantity to get value from (TBD)

  base_title = ""      # plot title
  bins = None          # override bins of search class
  hist_kwargs = {}     # histogram options, e.g. log=True for logarithmic scale

  @property
  def search_cls(self):
    module_name, class_name = self.search_class.rsplit('.', 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls

  def init(self, kind_class):
    self.kind_class = kind_class
    self.bins = self.bins #or self.search_cls.bins
    self.cnt = None
    return

  check = view_quantity_vs_status_stats.View.check.__func__
  iter_entries_views = view_quantity_vs_status_stats.View.iter_entries_views.__func__

  # TODO: enable when self.batch.select_entryintervals() available
  # def check(self):
  #   view_name = self.batch.create_table_from_last_entries(
  #     start_date=self.start_date, end_date=self.end_date)
  #   entryintervals = self.batch.select_entryintervals(
  #     entries=view_name,
  #     search_class=self.search_class,
  #     entry_title=self.entry_title
  #   )
  #   self.cnt = len(entryintervals)
  #   return view_name

  def fill(self, view_name):
    kinds = view_quantity_vs_status_stats.EntriesViewsResultCollector()
    query_kwargs = dict(
      search_class=self.search_class,
      entry_title=self.entry_title,
      quanamegroup=self.quanamegroup,
      quaname=self.quaname,
    )
    for view_name in self.iter_entries_views():
      cls = globals()[self.kind_class]
      kind = cls()
      # run query
      res = self.batch.query(kind.QUERY_PAT % dict(entries=view_name), **query_kwargs)
      kind.process_query_result(res)
      # TODO: enable when self.batch.select_entryintervals() available
      # if kind.data.size < self.cnt:
      #   cnt_missing = self.cnt - kind.data.size
      #   self.logger.warn('Missing quantities ignored in %d of %d cases' %(cnt_missing, self.cnt))
      kinds[view_name] = kind
    return kinds

  def view(self, kinds):
    # TODO: code duplicated from view_quantity_vs_status_stats
    title = self.base_title
    nav = MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    self.sync.addStaticClient(nav)
    ax = nav.fig.add_subplot(1,1,1)
    # preprocess data
    data    = [kind.data.quantity for kind in kinds.itervalues()]
    weights = [kind.data.weight   for kind in kinds.itervalues()]
    # plot histogram

    try:
      ax.hist(data, self.bins, weights=weights, stacked=True, **self.hist_kwargs)
      ax.set_ylabel(kind.ylabel)

    except:
      self.logger.warning('No quantities found, histogram will not be plotted.')

    return


class Kind(object):
  QUERY_PAT = None
  ylabel = ""
  dtype = np.dtype([('quantity', np.float64), ('weight', np.float64)])

  def __init__(self):
    self.data = None
    return

  def process_query_result(self, res):
    data = np.array(res, dtype=self.dtype)
    self.data = data.view(np.recarray)
    return


class Duration(Kind):
  QUERY_PAT = """
    SELECT qu.value as qu_value, (ei.end_time - ei.start_time) / 3600. AS time_hours
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id

    JOIN (
      SELECT quantities.entry_intervalid, quantities.value
      FROM   quantities
      JOIN quanames ON quanames.id = quantities.nameid
      JOIN quanamegroups ON quanamegroups.id = quanames.groupid
      WHERE quanamegroups.name = :quanamegroup
        AND quanames.name = :quaname
    ) AS qu ON qu.entry_intervalid = ei.id

    WHERE mo.class = :search_class AND
          en.title LIKE :entry_title
  """

  ylabel = "duration [h]"


class Mileage(Kind):
  QUERY_PAT = """
    SELECT qu.value as qu_value, qu_mileage.value AS distance_km
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id

    JOIN (
      SELECT quantities.entry_intervalid, quantities.value
      FROM   quantities
      JOIN quanames ON quanames.id = quantities.nameid
      JOIN quanamegroups ON quanamegroups.id = quanames.groupid
      WHERE quanamegroups.name = :quanamegroup
        AND quanames.name = :quaname
    ) AS qu ON qu.entry_intervalid = ei.id

    JOIN (
      SELECT quantities.entry_intervalid, quantities.value
      FROM   quantities
      JOIN quanames ON quanames.id = quantities.nameid
      JOIN quanamegroups ON quanamegroups.id = quanames.groupid
      WHERE quanamegroups.name = "ego vehicle"
        AND quanames.name = "driven distance"
    ) AS qu_mileage ON qu_mileage.entry_intervalid = ei.id

    WHERE mo.class = :search_class AND
          en.title LIKE :entry_title
  """

  ylabel = "mileage [km]"
  
  
class Probability(Kind):
    QUERY_PAT = """
        SELECT 100*qu.value as qu_value, 1 as weight
        FROM entryintervals ei
        JOIN %(entries)s en ON ei.entryid = en.id
        JOIN modules mo ON en.moduleid = mo.id

        JOIN (
            SELECT quantities.entry_intervalid, quantities.value
            FROM   quantities
            JOIN quanames ON quanames.id = quantities.nameid
            JOIN quanamegroups ON quanamegroups.id = quanames.groupid
            WHERE quanamegroups.name = :quanamegroup
            AND quanames.name = :quaname
        ) AS qu ON qu.entry_intervalid = ei.id

        WHERE mo.class = :search_class AND
                en.title LIKE :entry_title
        """

    ylabel = "cum. Count [-]"
  