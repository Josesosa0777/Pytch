# -*- dataeval: init -*-

"""
Count FCW events based on highest cascade phase
"""
from aebs.abc import view_quantity_vs_status_stats

init_params = {k: v for k, v in view_quantity_vs_status_stats.init_params.iteritems() if k.endswith("_mergedcount")}


class View(view_quantity_vs_status_stats.View):
		label_group = 'FCW cascade phase'
		search_class = 'fcwresim.search_events_fcw.Search'

		labels_to_show = ('preliminary warning', 'collision warning')

		base_title = "FCW events' highest phases"

		show_none = False
