# -*- dataeval: init -*-

"""
Count, mileage and duration of label occurrences
"""

from collections import OrderedDict
from itertools import cycle
import logging

import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

from interface.Interfaces import iView
from aebs.par.labels import default as def_labels
from datavis.MatplotlibNavigator import MatplotlibNavigator

init_params = {
  'print_count': dict(
    kind_class="Count", plot_method="print_results"),
  'print_mergedcount': dict(
    kind_class="MergedCount", plot_method="print_results"),
  'print_mileage': dict(
    kind_class="Mileage", plot_method="print_results"),
  'print_duration': dict(
    kind_class="Duration", plot_method="print_results"),
  'pie_count': dict(
    kind_class="Count", plot_method="plot_pie_chart"),
  'pie_mergedcount': dict(
    kind_class="MergedCount", plot_method="plot_pie_chart"),
  'pie_mileage': dict(
    kind_class="Mileage", plot_method="plot_pie_chart"),
  'pie_duration': dict(
    kind_class="Duration", plot_method="plot_pie_chart"),
  'bar_count': dict(
    kind_class="Count", plot_method="plot_bar_chart"),
  'bar_mergedcount': dict(
    kind_class="MergedCount", plot_method="plot_bar_chart"),
  'bar_FLR20_mergedcount': dict(
    kind_class="MergedCount", plot_method="plot_bar_chart", search_param="%FLR21%"),
  'bar_ARS430_mergedcount': dict(
    kind_class="MergedCount", plot_method="plot_bar_chart", search_param="%ARS430%"),
  'bar_mileage': dict(
    kind_class="Mileage", plot_method="plot_bar_chart"),
  'bar_duration': dict(
    kind_class="Duration", plot_method="plot_bar_chart"),
}

#JOIN = "JOIN"
JOIN = "LEFT JOIN"
"""
Use the specified JOIN (LEFT/RIGHT JOIN) operation in the queries.
LEFT JOIN works properly in a way that it checks for unlabeled intervals, too.
(RIGHT) JOIN does not check for unlabeled intervals (those are ignored, if any),
however, it radically reduces the processing time.
Use LEFT JOIN to get proper results in all cases, but if you are aware what
you are doing, (RIGHT) JOIN could also be activated for fast results.
TODO: implement proper solution also with (RIGHT) JOIN.
"""

class View(iView):
  search_class = None  # search class to filter for (TBD)
  label_group = None   # label group to filter for (TBD)
  entry_title = "%"    # match all entry titles (do not filter) by default

  base_title = ""  # plot title
  
  labels_to_show = None  # show all labels by default
  show_empties = True  # show also the labels with no occurrences
  show_none = True  # show the unlabeled intervals
  _none_key = 'not classified'  # text for the unlabeled intervals
  labelmap = None  # use original labels by default, do not group or rename
  
  # TODO: extend followings for bar chart, too
  show_legend = True  # display legend or not
  show_piece_label = False  # display label on the chart itself
  autopct = '%.1f%%'  # label value precision
  label2color = {}  # colors for labels
  _none_color = 'r'  # color of the unlabeled intervals
  
  def init(self, kind_class, plot_method, search_param='%'):
    self.kind_class = kind_class
    self.plot_method = plot_method
    self.search_param = search_param # search param to filter for (modules.param LIKE search_param; "%" match everything)
    return
  
  def check(self):
    view_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    cnt = self.batch.query("""
      SELECT COUNT(*) FROM %(entries)s AS en
      JOIN modules AS mo ON en.moduleid = mo.id
      JOIN results AS re ON en.resultid = re.id
      WHERE mo.class = :search_class AND
            en.title LIKE :entry_title AND
            re.name != "error"
      """ % dict(entries=view_name),
      search_class=self.search_class,
      entry_title=self.entry_title,
      fetch_one=True)[0]
    assert cnt > 0, "No entries found for '%s' class" % self.search_class
    return view_name
  
  def fill(self, view_name):
    # process self
    if self.label_group is not None:
      _labels = def_labels[self.label_group][1]
    else:
      _labels = []
    if self.labelmap is not None:
      assert all(label in self.labelmap for label in _labels), "Not all labels mapped"
      labelmap = self.labelmap
    else:
      labelmap = OrderedDict((label, label) for label in _labels)
    
    query_kwargs = dict(
      search_class=self.search_class,
      search_param=self.search_param,
      label_group=self.label_group,
      entry_title=self.entry_title,
    )
    
    kinds = EntriesViewsResultCollector()
    for view_name in self.iter_entries_views():
      # instantiate kind class based on module parameter
      kind = globals()[self.kind_class](labelmap, self.labels_to_show,
        self.show_empties, self.show_none, self._none_key)
      # run query
      res = self.batch.query(kind.QUERY_PAT % dict(entries=view_name, join=JOIN), **query_kwargs)
      kind.process_query_result(res)
      # save result
      kinds[view_name] = kind
    return kinds
  
  def iter_entries_views(self, entries_creator='create_table_from_last_entries'):
    """
    Iterates through the dates pairwise in
    "self.start_date --> self.global_params['datelist'] --> self.end_date"
    and yields a corresponding temporary 'entries' table name that contains
    the entry ids of the specified intervals.
    """
    # attention: code currently duplicated in analyze_all
    if entries_creator is None:
      yield 'entries'
      return
    middatelist = self.global_params.get('datelist', "").split()
    dates = [self.start_date] + middatelist + [self.end_date]
    create = getattr(self.batch, entries_creator)  # returns a method
    i = 0
    while i < len(dates):
      start_date = dates[i]; i += 1
      end_date = dates[i]; i += 1
      view_name = create(start_date=start_date, end_date=end_date)
      yield view_name
    return
  
  def view(self, kinds):
    # prepare "canvas" to draw on
    if self.plot_method == "print_results":
      ax = self.logger
    else:
      title = self.base_title
      nav = MatplotlibNavigator(title=title)
      nav.setUserWindowTitle(title)
      ax = nav.fig.add_subplot(1,1,1)
      self.sync.addStaticClient(nav)
    # prepare plot parameters
    if self.plot_method == "plot_pie_chart":
      label2color = self.label2color.copy()
      label2color.setdefault(self._none_key, self._none_color)
      kwargs = dict(show_legend=self.show_legend,
        show_piece_label=self.show_piece_label, autopct=self.autopct,
        label2color=label2color)
    else:
      kwargs = {}
    # plot
    plot = globals()[self.plot_method]
    plot(kinds, ax, **kwargs)
    return


class Kind(OrderedDict):
  QUERY_PAT = None
  ylabel = ""
  is_integer = False
  
  def __init__(self, labels=None, labels_to_show=None,
               show_empties=True, show_none=True, none_key="None"):
    # process arguments
    if labels is None:
      _labels = []
    if isinstance(labels, dict):
      self.labelmap = labels
      _labels = labels.values()
    else:
      self.labelmap = OrderedDict((label, label) for label in labels)
      _labels = labels
    assert none_key not in _labels, "Multi-purpose usage of '%s'" % none_key
    # init
    OrderedDict.__init__(self, ((label, 0.0) for label in _labels+[none_key]))
    self.labels_to_show = \
      labels_to_show if labels_to_show is not None else _labels  # all by default
    self.show_empties = show_empties
    self.show_none = show_none
    self.none_key = none_key
    return
  
  def __add__(self, other):
    sum_ = self.__copy__()
    for k, v in other.iteritems():
      if k not in sum_:
        sum_[k] = v
      else:
        sum_[k] += v
    # TODO: handle remaining attributes (e.g. labels_to_show) (design needed)
    return sum_
  
  def copy(self):  # override OrderedDict.copy()
    # create new instance
    other = self.__class__(
      labels=self.labelmap,
      labels_to_show=self.labels_to_show,
      show_empties=self.show_empties,
      show_none=self.show_none,
      none_key=self.none_key)
    # copy items
    for k, v in self.iteritems():
      other[k] = v
    return other
  
  def __copy__(self):  # for copy.copy()
    return self.copy()
  
  def process_query_result(self, res):
    for label, value in res:
      try:
        key = self.labelmap[label] if label is not None else self.none_key
      except KeyError:
        raise KeyError("Unexpected label found in the database: '%s'" % label)
      self[key] += value
    return
  
  def iter_visible_keys(self):
    for k in self.iterkeys():
      if k == self.none_key and self.show_none:
        yield k
      elif k in self.labels_to_show and (self.show_empties or self[k] > 0):
        yield k
    return
  def visible_keys(self):
    return list(self.iter_visible_keys())
  
  def iter_visible_values(self):
    for k in self.iter_visible_keys():
      yield self[k]
    return
  def visible_values(self):
    return list(self.iter_visible_values())
  
  def iter_visible_items(self):
    for k in self.iter_visible_keys():
      yield (k, self[k])
    return
  def visible_items(self):
    return list(self.iter_visible_items())
  
  def get_total(self):
    return sum(self.itervalues())
  total = property(get_total)
  
  def _print_kind(self, value):
    return "%.2f" % value
  
  def print_results(self, logger, **kwargs):
    return print_results({"custom": self}, logger, **kwargs)
  
  def plot_pie_chart(self, ax, **kwargs):
    return plot_pie_chart({"custom": self}, ax, **kwargs)
  
  def plot_bar_chart(self, ax, **kwargs):
    return plot_bar_chart({"custom": self}, ax, **kwargs)

class Count(Kind):
  QUERY_PAT = """
    SELECT la.name AS label_name,
           COUNT(*) AS cnt
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id
    
    %(join)s (
      SELECT interval2label.entry_intervalid, labels.name
      FROM   interval2label
      JOIN labels ON labels.id = interval2label.labelid
      JOIN labelgroups ON labelgroups.id = labels.groupid
      WHERE labelgroups.name = :label_group
    ) AS la ON la.entry_intervalid = ei.id
    
    WHERE mo.class = :search_class AND
          en.title LIKE :entry_title
    
    GROUP BY la.name
  """
  
  ylabel = "#occurrences"
  is_integer = True
  
  def _print_kind(self, value):
    if value == 1:
      return "1 occurrence"
    return "%d occurrences" % value

class MergedCount(Count):  # count 1 for intervals within 2 seconds (select first interval only)
  QUERY_PAT = """
    SELECT la.name AS label_name,
           COUNT(*) AS cnt
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id
    
    %(join)s (
      SELECT interval2label.entry_intervalid, labels.name
      FROM   interval2label
      JOIN labels ON labels.id = interval2label.labelid
      JOIN labelgroups ON labelgroups.id = labels.groupid
      WHERE labelgroups.name = :label_group
    ) AS la ON la.entry_intervalid = ei.id
    
    WHERE mo.class = :search_class AND
          mo.param LIKE :search_param AND
          en.title LIKE :entry_title AND
          NOT EXISTS (
            SELECT * FROM entryintervals ei_2
            JOIN %(entries)s en_2 ON ei_2.entryid = en_2.id
            WHERE en_2.id = en.id AND
                  ei_2.id != ei.id AND
                  ei.start_time-ei_2.end_time BETWEEN 0 AND 2
          )
    
    GROUP BY la.name
  """

class Mileage(Kind):
  QUERY_PAT = """
    SELECT la.name AS label_name,
           TOTAL(qu.value) AS distance_km
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id
    
    %(join)s (
      SELECT quantities.entry_intervalid, quantities.value
      FROM   quantities
      JOIN quanames ON quanames.id = quantities.nameid
      JOIN quanamegroups ON quanamegroups.id = quanames.groupid
      WHERE quanamegroups.name = "ego vehicle"
        AND quanames.name = "driven distance"
    ) AS qu ON qu.entry_intervalid = ei.id
    
    %(join)s (
      SELECT interval2label.entry_intervalid, labels.name
      FROM   interval2label
      JOIN labels ON labels.id = interval2label.labelid
      JOIN labelgroups ON labelgroups.id = labels.groupid
      WHERE labelgroups.name = :label_group
    ) AS la ON la.entry_intervalid = ei.id
    
    WHERE mo.class = :search_class AND
          en.title LIKE :entry_title
    
    GROUP BY la.name
  """
  
  ylabel = "mileage [km]"
  
  def _print_kind(self, value):
    return "%.1f km" % value

class Duration(Kind):
  QUERY_PAT = """
    SELECT la.name AS label_name,
           TOTAL(ei.end_time - ei.start_time) / 3600. AS time_hours
    FROM entryintervals ei
    JOIN %(entries)s en ON ei.entryid = en.id
    JOIN modules mo ON en.moduleid = mo.id
    
    %(join)s (
      SELECT interval2label.entry_intervalid, labels.name
      FROM   interval2label
      JOIN labels ON labels.id = interval2label.labelid
      JOIN labelgroups ON labelgroups.id = labels.groupid
      WHERE labelgroups.name = :label_group
    ) AS la ON la.entry_intervalid = ei.id
    
    WHERE mo.class = :search_class AND
          en.title LIKE :entry_title
    
    GROUP BY la.name
  """
  
  ylabel = "duration [h]"
  
  def _print_kind(self, value):
    return "%.1f hours" % value


class EntriesViewsResultCollector(OrderedDict):
  # attention: code currently duplicated in analyze_all
  def get_all(self):
    res = None
    for val in self.itervalues():
      if res is None:
        res = val
        continue
      res += val
    return res
  all = property(get_all)


def print_results(kinds, logger):
  for view_name, kind in kinds.iteritems():
    logger.info("Using subset: %s" % view_name)
    logger.info("<TOTAL> %s" % kind._print_kind(kind.total))
    for label, value in kind.iter_visible_items():
      if kind.total > 0.0:
        logger.info("+-- <%s> %s (%.1f %%)" %
          (label, kind._print_kind(value), float(value)/kind.total*100.0))
      else:
        # no percentage available if total is 0
        logger.info("+-- <%s> %s" % (label, kind._print_kind(value)))
  return

def plot_pie_chart(kinds, ax, show_legend=False, show_piece_label=True,
                   autopct='%.1f%%', label2color=None):
  if len(kinds) != 1:
    logging.getLogger().warning("Pie chart is not yet able to visualize "
                                "multi-dim data; showing total...")
  kind = kinds.all  # TODO: display the kinds somehow differently (design needed)
  
  if not kind.visible_keys():
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    return
  if not autopct: autopct = ''  # handle e.g. None properly
  if label2color is None: label2color = {}
  data = np.array( kind.visible_values(), dtype=np.float )
  if kind.total > 0.0:
    data /= kind.total
  indices = range(len(data))
  x = data[indices]
  labels = np.array( kind.visible_keys() )[indices]
  explode = [0.05 for _ in x]
  _labels = labels if show_piece_label else None
  _autopct = autopct if show_piece_label else ''
  def_colors = cycle(mpl.rcParams['axes.color_cycle'])
  colors = [label2color.get(l) or def_colors.next() for l in labels]
  patches, texts, autotexts = ax.pie(x, labels=_labels, autopct=_autopct,
    explode=explode, colors=colors, shadow=True)
  for text in autotexts:
    text.set_color('w')
  if show_legend:
    if autopct:
      # reconstruct labels to include ratio
      txt = "%%s (%s)" % autopct
      _labels = np.array([txt % (l, d*100.0) for l, d in zip(labels, x)])
    box = ax.get_position()
    ax.set_position((box.x0, box.y0, 0.8 * box.width, box.height))
    ax.legend(patches, _labels, loc='center left',
      bbox_to_anchor=(1.0, 0.5)).draggable(True)
  return

def plot_bar_chart(kinds, ax):
  kindlist = kinds.values()
  all_visible_keys = kinds.all.visible_keys()
  is_integer_kind = kindlist[0].is_integer  # same for all items, so for item[0]
  ylabel = kindlist[0].ylabel  # same for all items, so for item[0]
  
  if not all_visible_keys:
    ax.set_xticklabels([])
    ax.set_ylabel(ylabel)
    return
  
  # params
  width = 0.5  # TODO: add possibility to define absolute bar width
  xtick_rotation_angle = 40.0
  if len(kindlist) > 1:  # TODO: replace with "if 'datelist' in self.global_params"
    colors = cycle(['0.75'] + mpl.rcParams['axes.color_cycle'])
  else:
    colors = cycle(mpl.rcParams['axes.color_cycle'])
  # derived vars
  half_width = width / 2.0
  xtick_hor_align = 'right' if xtick_rotation_angle >= 0.0 else 'left'
  x = np.arange(len(all_visible_keys))
  # plot
  bottom = np.zeros(x.size)
  max_height = 0
  for i, kind in enumerate(kindlist):
    arr = np.array([kind[key] for key in all_visible_keys])
    rectangles = ax.bar(x, arr, width, color=colors.next(), bottom=bottom)
    bottom += arr
    
    max_height = max(max_height, bottom.max())
    if i == len(kindlist)-1:
      # show numbers on top of the bars - only for top dataset
      for rect in rectangles:
        height = rect.get_height()
        if is_integer_kind:
          fmt = "%.0f"
          min_height = 0.0
        else:
          fmt = "%.2f"
          min_height = 0.01
        if len(kindlist) > 1:  # TODO: replace with "if 'datelist' in self.global_params"
          fmt = "+" + fmt
        if height > min_height:
          rect_x = rect.get_x() + rect.get_width() / 2.0
          rect_y = 1.03 * (rect.get_y() + height)
          ax.text(rect_x, rect_y, fmt % height, ha='center', va='bottom')
  
  # further customize
  ax.set_xticks(x + half_width)
  ax.set_xticklabels(all_visible_keys,
    rotation=xtick_rotation_angle, horizontalalignment=xtick_hor_align)
  ax.set_xlim(x[0] - half_width, x[-1] + width + half_width)
  ax.set_ylim(0.0, max_height * 1.3)
  ax.set_ylabel(ylabel)
  if is_integer_kind:
    ax.get_yaxis().set_major_locator(MaxNLocator(integer=True)) # only int ticks
  return
