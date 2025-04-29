# -*- dataeval: init -*-

import datavis
from interface import iView

# def_param = interface.NullParam

sgs = [
    {
        "Left_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeLeft_available"),
        "Right_available": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeRight_available"),
        "Left_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeLeft_clothoidNear_offset"),
        "Right_clothoidNear_offset": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeRight_clothoidNear_offset"),
        "Left_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeLeft_clothoidNear_validTo"),
        "Right_clothoidNear_validTo": (
        "MFC5xx Device.LD.LdOutput", "MFC5xx_Device_LD_LdOutput_road_roadEdgeRight_clothoidNear_validTo"),
    },
]


class View(iView):
    def check(self):
        # select signals
        group = self.source.selectLazySignalGroup(sgs)

        # give warning for not available signals
        for alias in sgs[0].keys():
            if alias not in group:
                self.logger.warning("Signal for '%s' not available" % alias)

        return group

    def view(self, group):

        pn = datavis.cPlotNavigator(title="Road Edge Signals")

        axis00 = pn.addAxis(ylabel="Availability")
        axis01 = pn.addAxis(ylabel="ClothoidNear_offset")
        axis02 = pn.addAxis(ylabel="ClothoidNear_validTo")

        if "Left_available" in group:
            time, value, unit = group.get_signal_with_unit("Left_available")
            pn.addSignal2Axis(axis00, "Left_available", time, value, unit=unit)
        if "Right_available" in group:
            time, value, unit = group.get_signal_with_unit("Right_available")
            pn.addSignal2Axis(axis00, "Right_available", time, value, unit=unit)

        if "Left_clothoidNear_offset" in group:
            time, value, unit = group.get_signal_with_unit("Left_clothoidNear_offset")
            pn.addSignal2Axis(axis01, "Left_clothoidNear_offset", time, value, unit=unit)
        if "Right_clothoidNear_offset" in group:
            time, value, unit = group.get_signal_with_unit("Right_clothoidNear_offset")
            pn.addSignal2Axis(axis01, "Right_clothoidNear_offset", time, value, unit=unit)

        if "Left_clothoidNear_validTo" in group:
            time, value, unit = group.get_signal_with_unit("Left_clothoidNear_validTo")
            pn.addSignal2Axis(axis02, "Left_clothoidNear_validTo", time, value, unit=unit)
        if "Right_clothoidNear_validTo" in group:
            time, value, unit = group.get_signal_with_unit("Right_clothoidNear_validTo")
            pn.addSignal2Axis(axis02, "Right_clothoidNear_validTo", time, value, unit=unit)

        self.sync.addClient(pn)
        return
