# -*- dataeval: init -*-

import datavis
from taeval import view_hmi_dashboard


class View(view_hmi_dashboard.View):

  def view(self, group):
    t, LED_red = group.get_signal("LED_red")
    LED_yellow = group.get_value("LED_yellow")
    feedbacklamp = group.get_value("feedbacklamp")
    speaker = group.get_value("speaker")

    graph = datavis.cPlotNavigator(title="Turning Assist HMI")
    yticks = dict( (k,v) for k,v in zip([0,1, 2.5,3.5, 5,6, 7.5,8.5],[0,1]*4) )
    ax = graph.addAxis(xlabel="time [sec]", yticks=yticks)

    graph.addSignal2Axis(ax, 'feedbacklamp', t, feedbacklamp, offset=7.5, displayscaled=False, color='g')
    graph.addSignal2Axis(ax, 'yellow LED',   t, LED_yellow,   offset=5,   displayscaled=False, color='y')
    graph.addSignal2Axis(ax, 'red LED',      t, LED_red,      offset=2.5, displayscaled=False, color='r')
    graph.addSignal2Axis(ax, 'speaker',      t, speaker,                                       color='r', ls='--')
    self.sync.addClient(graph)
    return
