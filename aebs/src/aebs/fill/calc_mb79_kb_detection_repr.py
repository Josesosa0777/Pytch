# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.fill import calc_mb79_kb_targets

signals = [{
    "Azimuth":      ("TA", "tracking_in_Azimuth_selected"),
    "CoGDoppler":   ("TA", "tracking_in_CoGDoppler_selected"),
    "PowerDB":      ("TA", "tracking_in_PowerDB_selected"),
    "StdAzimuth":   ("TA", "tracking_in_StdAzimuth_selected"),
    "CoGRange":     ("TA", "tracking_in_CoGRange_selected"),
    "StdDoppler":   ("TA", "tracking_in_StdDoppler_selected"),
    "StdRange":     ("TA", "tracking_in_StdRange_selected"),
}]

num_of_det_sig = [{
    "NumOfDetectionsTransmitted":   ("TA", "tracking_in_NumofDetectionsTransmitted_selected"),
}]


class Calc(calc_mb79_kb_targets.Calc):
  side_sgs = num_of_det_sig
  sgs = signals


if __name__ == '__main__':
  from config.Config import init_dataeval

  meas_path = r'\\file\Messdat\DAS\ConvertedMeas\TurningAssist\06xB365\2016-11-08-Clustering\B365__2016-11-08_11-11-31_resim_2016_12_02-11_23_53_more.mat'
  config, manager, manager_modules = init_dataeval(['-m', meas_path])
  kb_repr_det = manager_modules.calc('calc_mb79_kb_detection_repr@aebs.fill', manager)
  dummy_id, dummy_target = kb_repr_det.iteritems().next()
  print dummy_id
  print dummy_target.range_rate
