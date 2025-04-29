--Query measurements and the run modules

SELECT STRFTIME("%Y-%m-%d", DATE(me.start, "-4 hour")) AS day,
       me.basename AS measurement,
	   mo.class AS module,
	   re.name AS result
FROM measurements AS me
JOIN entries AS en ON en.measurementid = me.id
JOIN modules AS mo ON mo.id = en.moduleid
JOIN results AS re ON re.id = en.resultid
ORDER BY day, measurement, module, result;
