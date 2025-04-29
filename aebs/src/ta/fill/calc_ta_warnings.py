# -*- dataeval: init -*-

from interface import iCalc

# defining how a signal group looks like
sgs = [{
    "warning1"          : ("HMI_TA_OUT", "LED_yellow_TA"),
    "warning2"          : ("HMI_TA_OUT", "LED_red_TA"),
}]

class Calc(iCalc):

    def check(self):
        warnings = self.source.selectSignalGroup(sgs)
        return warnings

    def fill(self, warnings):
        time, warning1 = warnings.get_signal('warning1')
        warning1 = warning1.astype(bool)
        warning2 = warnings.get_value('warning2', ScaleTime=time).astype(bool)
        return time, (warning1, warning2)
