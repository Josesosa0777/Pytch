--Query measurements that have been removed from batch.db

select distinct me.basename
from measurements as me
join entries as en on me.id not in (select measurementid from entries)





