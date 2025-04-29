# -*- dataeval: init -*-

from PySide import QtCore
from interface import iView
from datavis.LedNavigator import LedNavigator

hmi_signals = [
{
  "LED_red":        ("TA", "LED_red"),
  "LED_yellow":     ("TA", "LED_yellow"),
  "feedbacklamp":   ("TA", "feedbacklamp"),
  "speaker":        ("TA", "speaker"),
},
{
  "LED_red":        ("TA", "LED_red_TA"),
  "LED_yellow":     ("TA", "LED_yellow_TA"),
  "feedbacklamp":   ("TA", "feedbacklamp_TA"),
  "speaker":        ("TA", "sound_TA"),
}]


class View(iView):

  def check(self):
    group = self.source.selectSignalGroup(hmi_signals)
    return group

  def view(self, group):
    time, LED_red = group.get_signal("LED_red")
    LED_yellow = group.get_value("LED_yellow")
    feedbacklamp = group.get_value("feedbacklamp")
    speaker = group.get_value("speaker")

    led_panel = LedNavigator(time)
    led_panel.addLed("left", "red", "Red LED", LED_red)
    led_panel.addLed("right", "yellow", "Yellow LED", LED_yellow)
    led_panel.addLed("top-center", "green", "System State", feedbacklamp)
    led_panel.addLed("bottom-center", "red", "Speaker", speaker)
    self.sync.addClient(led_panel)
    return
