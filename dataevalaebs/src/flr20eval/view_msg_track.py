# -*- dataeval: init -*-

"""
Plots some attributes of the selected FLR21 message object.
The object can be selected using the module parameter, which corresponds to the
object's CAN message number (not internal identifier).
"""

from view_raw_track import View as RawTrackView

# instantiation of module parameters
init_params = dict( ('tr%d' %i, dict(id=i)) for i in xrange(21) )

class View(RawTrackView):
  dep = 'fill_flr20_msg_tracks@aebs.fill',
  TITLE_PAT = 'FLR21 track tr%d'
