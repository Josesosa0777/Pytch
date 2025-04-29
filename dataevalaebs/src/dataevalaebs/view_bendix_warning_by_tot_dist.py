# -*- dataeval: init -*-
from collections import OrderedDict

from interface.Interfaces import iView
from datavis.MatplotlibNavigator import MatplotlibNavigator

from search_bendix_warning import init_params as search_params

MILE_TO_KM = 1.6

class View(iView):
  def fill(self):
    batch = self.get_batch()
    view_name = batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    tot_dist = get_tot_dist(batch, view_name)

    warnings = OrderedDict()
    for param in search_params.itervalues():
      algo = param['algo']
      param_str = ','.join(["%s='%s'" % (name, param[name])
                            for name in sorted(param)])
      no_warnings, = batch.query("""
        SELECT COUNT(*) FROM %s en
          JOIN modules ON
               modules.id = en.moduleid

          JOIN entryintervals ON
               entryintervals.entryid = en.id

          JOIN interval2label algo_i2l ON
                              algo_i2l.entry_intervalid = entryintervals.id
          JOIN labels algo_labels ON
                      algo_labels.id = algo_i2l.labelid
          JOIN labelgroups algo_labelgroups ON
                           algo_labelgroups.id = algo_labels.groupid

        WHERE modules.class = :class_name
          AND modules.param = :param
          AND en.title = :title
          AND algo_labelgroups.name = :algo_group
          AND  algo_labels.name = :algo
      """ % view_name,

      fetchone=True,
      class_name='dataevalaebs.search_bendix_warning.Search',
      param=param_str,
      title='Bendix-event',
      algo_group='Bendix event',
      algo=algo,
      )
      warnings[algo] = no_warnings
    return tot_dist, warnings

  def view(self, tot_dist, warnings):
    width = 0.35
    #warnings.pop('13-LDW')
    ind = range(len(warnings))

    mile_tot_dist = tot_dist / MILE_TO_KM
    rel_dist = 100.0 / mile_tot_dist if abs(mile_tot_dist) > 1e-3 else 1.0
    values = [value * rel_dist for value in warnings.itervalues()]

    mn = MatplotlibNavigator()
    self.get_sync().addStaticClient(mn)
    mn.fig.suptitle('Warnings per 100 miles during %.1f miles' % mile_tot_dist)
    ax = mn.fig.add_subplot(1, 1, 1)
    up = max(values) * 1e-2
    for rect in ax.bar(ind, values, width):
      height = rect.get_height()
      ax.text(rect.get_x()+rect.get_width()*0.5, height+up, '%.2f' % height,
              ha='center', va='bottom')

    ax.set_xticks([i+0.5*width for i in ind])
    ax.set_xticklabels(warnings.keys())
    mn.fig.autofmt_xdate()
    return

def get_tot_dist(batch, view_name):
  tot_dist, = batch.query("""
    SELECT TOTAL(tot_dist.value)
      FROM %s en
      JOIN modules ON
           modules.id = en.moduleid

      JOIN entryintervals ON
           entryintervals.entryid = en.id

      JOIN quantities tot_dist ON
                      tot_dist.entry_intervalid = entryintervals.id
      JOIN quanames tot_dist_names ON
                    tot_dist_names.id = tot_dist.nameid
      JOIN quanamegroups tot_dist_namegroups ON
                         tot_dist_namegroups.id = tot_dist_names.groupid

    WHERE modules.class = :class_name
      AND tot_dist_namegroups.name = :tot_dist_group
      AND tot_dist_names.name = :tot_dist
  """ % view_name,

    fetchone=True,
    class_name='egoeval.roadtypes.search_roadtypes.Search',
    tot_dist_group='ego vehicle',
    tot_dist='driven distance',
  )
  return tot_dist
