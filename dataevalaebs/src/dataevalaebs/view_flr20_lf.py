# -*- dataeval: init -*-

import interface
import datavis

init_params = {
  "validity": dict(
    show_validity=True,
    show_coeffs=False,
    show_videostatus=False,
    short=False),
  "validity_coeffs": dict(
    show_validity=True,
    show_coeffs=True,
    show_videostatus=False,
    short=False),
  "validity_coeffs_videostatus": dict(
    show_validity=True,
    show_coeffs=True,
    show_videostatus=True,
    short=False),
  "overview": dict(
    show_validity=True,
    show_coeffs=False,
    show_videostatus=True,
    short=True),
}

BOOL_YLIM = (-0.1, 1.3)
VIEWRANGE_YLIM = (-5.0, 140.0)

class cView(interface.iView):
  def init(self, show_validity, show_coeffs, show_videostatus, short):
    self.show_validity = show_validity
    self.show_coeffs = show_coeffs
    self.show_videostatus = show_videostatus
    self.short = short
    return
  
  def check(self):
    sg = {}
    if self.show_validity:
      sg.update({
        "LF_is_CVD_valid": ("General_radar_status", "LF_is_CVD_valid"),
        "LF_is_video_valid": ("General_radar_status", "LF_is_video_valid"),
        "LF_is_radar_valid": ("General_radar_status", "LF_is_radar_valid"),
        "LF_is_eHorizon_valid": ("General_radar_status", "LF_is_eHorizon_valid"),
      })
    if self.show_coeffs:
      sg.update({
        "LF_heading_angle": ("General_radar_status", "LF_heading_angle"),
        "LF_curvature": ("General_radar_status", "LF_curvature"),
        "LF_curvature_rate": ("General_radar_status", "LF_curvature_rate"),
      })
    if self.show_videostatus:
      sg.update({
        "VideoStatus": ("Video_Data_General_B", "SensorStatus"),
        "ViewRange_Left": ("Video_Lane_Left_B", "View_Range_Left_B"),
        "ViewRange_Right": ("Video_Lane_Right_B", "View_Range_Right_B"),
      })
    group = self.get_source().selectSignalGroup([sg])
    return group
  
  def view(self, group):
    if self.short:  # only the most important signals
      pn = datavis.cPlotNavigator(title="Lane fusion")
      
      if self.show_validity:
        t, v, u = group.get_signal_with_unit("LF_is_video_valid")
        ax = pn.addAxis(ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "LF_is_video_valid", t, v, unit=u)
      
      if self.show_videostatus:
        t, v, u = group.get_signal_with_unit("VideoStatus")
        ax = pn.addAxis(ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "VideoStatus", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("ViewRange_Left")
        ax = pn.addAxis(ylim=VIEWRANGE_YLIM)
        pn.addSignal2Axis(ax, "ViewRange_Left", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("ViewRange_Right")
        pn.addSignal2Axis(ax, "ViewRange_Right", t, v, unit=u)
    
    else:  # all relevant signals
      n_cols = self.show_coeffs + self.show_validity + self.show_videostatus
      subplotGeom = (4, n_cols)
      pn = datavis.cPlotNavigator(title="Lane fusion", subplotGeom=subplotGeom)
      
      colNr = 0
      if self.show_validity:
        colNr = colNr + 1
        t, v, u = group.get_signal_with_unit("LF_is_CVD_valid")
        ax = pn.addAxis(rowNr=1, colNr=colNr, ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "LF_is_CVD_valid", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("LF_is_video_valid")
        ax = pn.addAxis(rowNr=2, colNr=colNr, ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "LF_is_video_valid", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("LF_is_radar_valid")
        ax = pn.addAxis(rowNr=3, colNr=colNr, ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "LF_is_radar_valid", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("LF_is_eHorizon_valid")
        ax = pn.addAxis(rowNr=4, colNr=colNr, ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "LF_is_eHorizon_valid", t, v, unit=u)
      
      if self.show_coeffs:
        colNr = colNr + 1
        t, v, u = group.get_signal_with_unit("LF_heading_angle")
        ax = pn.addAxis(rowNr=1, colNr=colNr)
        pn.addSignal2Axis(ax, "LF_heading_angle", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("LF_curvature")
        ax = pn.addAxis(rowNr=2, colNr=colNr)
        pn.addSignal2Axis(ax, "LF_curvature", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("LF_curvature_rate")
        ax = pn.addAxis(rowNr=3, colNr=colNr)
        pn.addSignal2Axis(ax, "LF_curvature_rate", t, v, unit=u)
      
      if self.show_videostatus:
        colNr = colNr + 1
        t, v, u = group.get_signal_with_unit("VideoStatus")
        ax = pn.addAxis(rowNr=1, colNr=colNr, ylim=BOOL_YLIM)
        pn.addSignal2Axis(ax, "VideoStatus", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("ViewRange_Left")
        ax = pn.addAxis(rowNr=2, colNr=colNr, ylim=VIEWRANGE_YLIM)
        pn.addSignal2Axis(ax, "ViewRange_Left", t, v, unit=u)
        t, v, u = group.get_signal_with_unit("ViewRange_Right")
        ax = pn.addAxis(rowNr=3, colNr=colNr, ylim=VIEWRANGE_YLIM)
        pn.addSignal2Axis(ax, "ViewRange_Right", t, v, unit=u)
    
    sync = self.get_sync()
    sync.addClient(pn)
    return
