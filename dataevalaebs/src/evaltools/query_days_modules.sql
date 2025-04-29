--Query measurement days and the run modules

SELECT DISTINCT STRFTIME("%Y-%m-%d", DATE(me.start, "-4 hour")) AS day,
                mo.class AS module
FROM measurements AS me
JOIN entries AS en ON en.measurementid = me.id
JOIN modules AS mo ON mo.id = en.moduleid
ORDER BY day, module;
