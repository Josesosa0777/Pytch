"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.

The module defines legend and display style for every single group type.
"""

__docformat__ = "restructuredtext en"

import grouptypes as gtps

MS         = 10      # default marker size
MEW        =  1      # default marker edge width
MEC        = 'k'     # default marker edge color
MFC        = 'None'  # default marker face color (transparent)
COL        = 'k'     # default color
LS         = ''      # default line style
LW         =  1      # default line width
ALP        =  1.0    # default alpha channel value

GRY = (200./256., 200./256., 200./256.)  # GRAY color

SOUND_LINES =         r'$\|\cdot\ \ \ \ \cdot\|$'
INTRO =               r'$]\ \ \ \ \ \ [$'
GREATER_LESS_THAN =   r'$>\ \ \ \ \ \ <$'

LegendValues = {
  'MEAS_TRAJ':    ('Measured traj',   dict(marker='',  ms=MS, mew=MEW, mec=MEC, mfc=MFC, color='b', ls='-', lw=2., alpha=ALP)),
  'REC_TRAJ':     ('Recorded traj',   dict(marker='',  ms=MS, mew=MEW, mec=MEC, mfc=MFC, color='r', ls='--',lw=2., alpha=ALP)),
  'DIFF_TRAJ':    ('Difference',      dict(marker='',  ms=MS, mew=MEW, mec=MEC, mfc=MFC, color=COL, ls='-', lw=2., alpha=ALP)),
  'TRAJ_GEN_POLY':('Trajectory poly', dict(marker='',  ms=4, mew=MEW, mec=MEC, mfc=MFC, color='g', ls='-', lw=2., alpha=ALP)),
  'TRAJ_GEN_POLY_VEL':('Trajectory poly velocity', dict(marker='o',  ms=4, mew=MEW, mec=MEC, mfc=MFC, color='g', ls='None', lw=0., alpha=ALP)),
  'TRAJ_GEN_BEZIER':('Trajectory bezier', dict(marker='',  ms=4, mew=MEW, mec=MEC, mfc=MFC, color='r', ls='-', lw=2., alpha=ALP)),
  'TRAJ_GEN_BEZIER_VEL':('Trajectory bezier velocity', dict(marker='x',  ms=4, mew=MEW, mec=MEC, mfc=MFC, color='r', ls='None', lw=0., alpha=ALP)),
  'NONE_TYPE':    ('NoneType',        dict(marker='',  ms=MS, mew=MEW, mec=MEC, mfc=MFC, color=COL, ls=LS,  lw=LW, alpha=ALP)),
}
""":type: dict
Container of legend and display style definitions {GroupType<str> : (Legend<str>, DisplayStyle<dict>), }"""
