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
YEL = (255./256., 255./256., 0.)  # YELLOW color
ORA = (255./256., 200./256., 10./256.)  # ORANGE color
BLU = (66./256., 134./256., 244./256.)  # BLUE color

SOUND_LINES =         r'$\|\cdot\ \ \ \ \cdot\|$'
INTRO =               r'$]\ \ \ \ \ \ [$'
GREATER_LESS_THAN =   r'$>\ \ \ \ \ \ <$'

LegendValues = {
  'NONE_TYPE':    ('NoneType',        dict(marker='',  ms=MS, mew=MEW, mec=MEC, mfc=MFC, color=COL, ls=LS,  lw=LW, alpha=ALP)),
  'CONTI_SRR320': ('CONTI_SRR320',    dict(marker='v', ms=MS, mew=MEW * 2, mec='g', mfc=MFC, color='g', ls=LS, lw=LW, alpha=ALP)),
  'CONTI_SRR520': ('CONTI_SRR520',    dict(marker='v', ms=MS, mew=MEW * 2, mec='g', mfc=MFC, color='g', ls=LS, lw=LW, alpha=ALP)),
  'CONTI_SRR520_radar_1': ('CONTI_SRR520_r1',    dict(marker='v', ms=MS, mew=MEW * 2, mec='g', mfc=MFC, color='g', ls=LS, lw=LW, alpha=ALP)),
  'CONTI_SRR520_radar_2': ('CONTI_SRR520_r2',    dict(marker='o', ms=MS, mew=MEW * 2, mec='y', mfc=MFC, color='y', ls=LS, lw=LW, alpha=ALP)),
  'BSM_CAM'     : ('BSM_CAM',   dict(marker='', ms=MS*2, mew=MEW, mec='r', mfc='r', color='r', ls=LS, lw=LW, alpha=0.51, fill=1)),
  'BSM_LS'     :  ('BSM_LS',    dict(marker='', ms=MS*2, mew=MEW, mec=ORA, mfc=ORA, color=ORA, ls=LS, lw=LW, alpha=0.4, fill=1)),
  'BSM_HS'     :  ('BSM_HS',    dict(marker='', ms=MS*2, mew=MEW, mec=YEL, mfc=YEL, color=YEL, ls=LS, lw=LW, alpha=0.4, fill=1)),
  'BSM_DRAD_LONG':('BSM_DRAD_LONG', dict(marker='', ms=MS*2, mew=MEW, mec=BLU, mfc=BLU, color=BLU, ls=LS, lw=LW, alpha=0.4, fill=1)),
  'BSM_DRAD_LAT': ('BSM_DRAD_LAT',  dict(marker='', ms=MS*2, mew=MEW, mec=BLU, mfc=BLU, color=BLU, ls=LS, lw=LW, alpha=0.4, fill=1)),
}
""":type: dict
Container of legend and display style definitions {GroupType<str> : (Legend<str>, DisplayStyle<dict>), }"""
