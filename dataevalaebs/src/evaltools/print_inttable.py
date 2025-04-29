# -*- dataeval: init -*-

"""
Queries the entries in the database according to the given parameter:
* default: query all entries
* last_entries: query the latest version of the entries
* last_start: query the entries registered by the latest search session run

The returned entries will be printed to the standard output.
"""

import analyze_all

init_params = analyze_all.print_init_params

class Analyze(analyze_all.Analyze):
  pass
