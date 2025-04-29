"""
Provides the dbc files in the package directory as a dictionary,
with basenames as keys and fullnames as values.
"""

import os

dbc_dir = os.path.abspath(os.path.dirname(__file__))
dbc2filename = {}

for f in os.listdir(dbc_dir):
  if os.path.splitext(f)[1] == '.dbc':
    dbc2filename[f] = os.path.join(dbc_dir, f)

# backward compatibility for renamed file:
dbc2filename['AC100_SMess_PTC_1.52.dbc'] = os.path.join(dbc_dir, 'AC100_SMess_P0.dbc')
