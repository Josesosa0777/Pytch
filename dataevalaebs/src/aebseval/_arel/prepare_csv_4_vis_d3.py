import os
import sys
import csv
from collections import OrderedDict


csv_file_path = sys.argv[1]

# parse file and separate aRel ON and OFF rows
with open(csv_file_path, 'r') as f:
  reader = csv.DictReader(f, delimiter=';')
  fieldnames = reader.fieldnames # store it as file can't be accessed via reader outside this context
  rows_off = OrderedDict() # keep original order
  rows_on = {}
  for row in reader:
    name = row['Name']
    key = name.replace("aOn", "").replace("aOff", "")
    d = rows_on if 'aOn' in name else rows_off
    d[key] = row

def check_collision(row):
  impact = bool( int(row["IMPACT"]) )
  collision = impact and row["Reason"] != "Impact after successful cascade"
  return collision

# create new csv file with only aRel OFF rows + extra columns using aRel ON data
dirname = os.path.dirname(csv_file_path)
out_csv_file_path = os.path.join(dirname, 'mbt_summary_d3.csv')
with open(out_csv_file_path, 'wb') as f: # 'wb' mode is needed to avoid empty lines btw rows
  fieldnames_extra = ['coll_in_casc',
                      't_warn_st_diff',
                      't_warn_st_from_acc',
                      'obst_stopped_in_casc',
                      't_part_st_diff',
                      't_warn_dura',
                      ]
  fieldnames_new = [n if n!='ttc(WP1)' else 'dt(WP1)' for n in fieldnames] + fieldnames_extra
  writer = csv.DictWriter(f, fieldnames_new, delimiter=',')
  writer.writeheader()
  for key, row_off in rows_off.iteritems():
    row_new = dict(row_off)
    row_new['dt(WP1)'] = row_new.pop('ttc(WP1)')
    row_on = rows_on[key]
    # warning trigger point difference of aRel ON and OFF
    row_new['t_warn_st_diff'] = float( row_on['t(WP1)'] ) - float( row_off['t(WP1)'] )
    # partial braking trigger point difference of aRel ON and OFF
    row_new['t_part_st_diff'] = float( row_on['t(WP2)'] ) - float( row_off['t(WP2)'] )
    # warning duration of aRel OFF
    row_new['t_warn_dura'] = float( row_off['t(WP2)'] ) - float( row_off['t(WP1)'] )
    # warning trigger point from start of acceleration
    t_warn_st_from_acc = float( row_off['t(WP1)'] ) - float( row_off['time_of_acceleration_change'] )
    row_new['t_warn_st_from_acc'] = t_warn_st_from_acc
    # obstacle stopped in cascade
    if float(row_off["obst_vx(avoid)"]) == 0.0:
      if row_off["Reason"] == "Unknown reason for impact":
        # we run into a stopped obstacle during cascade
        obst_stopped_in_casc = 'STOPPED_RUN_OVER'
      else:
        # cascade successfully ended on a stopped obstacle
        obst_stopped_in_casc = 'STOPPED'
    else:
      obst_stopped_in_casc = 'NOT_STOPPED'
    row_new['obst_stopped_in_casc'] = obst_stopped_in_casc
    # check if collision occured in cascade (not after)
    collision_off = check_collision(row_off)
    collision_on = check_collision(row_on)
    if collision_on:
      if collision_off:
        coll_in_casc = 'BOTH_FAILED'
      else:
        coll_in_casc = 'ON_FAILED'
    else:
      if collision_off:
        coll_in_casc = 'OFF_FAILED'
      else:
        coll_in_casc = 'BOTH_PASSED'
    row_new['coll_in_casc'] = coll_in_casc
    # row_new['coll_in_casc'] = 'FAILED' if collision_off else 'PASSED'
    # write new row
    writer.writerow(row_new)
