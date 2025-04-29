--$ @, measurement, start, end, duration, track_id, ttc_min
SELECT DISTINCT pperror.ei_id,
                pperror.me_name,
                MAX(pperror.start_time, aebscand.start_time, lanesvis.start_time),
                MIN(pperror.end_time, aebscand.end_time, lanesvis.end_time),
                MIN(pperror.end_time, aebscand.end_time, lanesvis.end_time)-MAX(pperror.start_time, aebscand.start_time, lanesvis.start_time),
                aebscand.tr_id,
                aebscand.ttc_min
FROM (
  SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id, me.basename me_name
  FROM entryintervals ei
  JOIN entries en ON en.id = ei.entryid
  JOIN modules mo ON mo.id = en.moduleid
  JOIN measurements me ON me.id = en.measurementid

  JOIN quantities qu1 ON qu1.entry_intervalid = ei.id
  JOIN quanames qn1 ON qn1.id = qu1.nameid
  JOIN quanamegroups qg1 ON qg1.id = qn1.groupid

  WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search" AND
        qn1.name = "rms error avg" AND
        qg1.name = "path prediction" AND
        qu1.value > 1.5
) pperror
JOIN (
  SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id, la.name tr_id, qu2.value ttc_min
  FROM entryintervals ei
  JOIN entries en ON en.id = ei.entryid
  JOIN modules mo ON mo.id = en.moduleid

  JOIN interval2label i2l ON i2l.entry_intervalid = ei.id
  JOIN labels la ON la.id = i2l.labelid
  JOIN labelgroups lg ON lg.id = la.groupid

  JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
  JOIN quanames qn2 ON qn2.id = qu2.nameid
  JOIN quanamegroups qg2 ON qg2.id = qn2.groupid

  WHERE mo.class = "dataevalaebs.search_aebs_candidates.Search" AND
        qu2.value < 3.0 AND
        qn2.name = "ttc min" AND
        qg2.name = "target" AND
        lg.name = "AC100 track"
) aebscand ON aebscand.me_id = pperror.me_id AND
              MAX(aebscand.start_time, pperror.start_time) <=
                MIN(aebscand.end_time, pperror.end_time)
JOIN (
  SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
  FROM entryintervals ei
  JOIN entries en ON en.id = ei.entryid
  JOIN modules mo ON mo.id = en.moduleid
  WHERE mo.class = "dataevalaebs.search_lanes_visible.Search"
) lanesvis ON lanesvis.me_id = pperror.me_id AND
              MAX(lanesvis.start_time, aebscand.start_time, pperror.start_time) <=
                MIN(lanesvis.end_time, aebscand.end_time, pperror.end_time)

;
--$ validity
--! LABEL standard
--$ comment
--! COMMENT