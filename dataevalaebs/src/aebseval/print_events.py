# -*- dataeval: init -*-

"""
Prints a virtual Interval Table to the standard output.

The containing intervals are determined by the dependent analyze script, which
can be selected by parameter. 
"""

import analyze_events

init_params = analyze_events.print_init_params

class Analyze(analyze_events.Analyze):
  pass
