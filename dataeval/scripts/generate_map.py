#!C:\Python27\python.exe
from datavis import pyglet_workaround  # necessary as early as possible (#164)

from argparse import ArgumentParser
import sys
import os
import tempfile
import subprocess
import glob
import shutil

import measproc.mapbbox as mb
import measproc.GenMaperitiveScripts as gms
from measproc.mapmanager import MapManager
from measproc.batchsqlite import Batch


parser = ArgumentParser()
parser.add_argument('-b', '--batch', help="Set the batch file.")
parser.add_argument('--repdir', help="Set the report directory.")
parser.add_argument('--mapdb',
                    help="Location of main map database to be created/updated.")
parser.add_argument('--zooms',
                    help=("Give zoom bounds in this form: "
                          "min_zoom max_zoom. "
                          "So 7 16 will set minimum zoom level to 7 and "
                          "maximum zoom level to 16. The default values "
                          "are: %(default)s where minimum zoom level is 7 and "
                          "maximum zoom level is 16."
                          ),
                    nargs=2, type=int,
                    default=[7, 16])
parser.add_argument('--bounds',
                    help=("Give map bounding box in this form: "
                          "min_lon min_lat max_lon max_lat."
                          "So 8.1 48.2 8.5 48.9 will set the coordinate "
                          "of the lower left corner of the map bounding "
                          "box 8.1 and 48.2 (longitude and latitude) and "
                          "that of the upper right bounding corner to be "
                          "8.5 and 48.9. It has effect only if batch file "
                          "is not given."),
                    nargs=4, type=float)
parser.add_argument('--maperitive',
                    help=("Location of Maperitive executable. The default "
                          "is %(default)s."),
                    default=r'C:\Maperitive\Maperitive.exe')
parser.add_argument('--all',
                    help=("Include intermediate areas into the map database "
                          "too and not just the smaller areas corresponding "
                          "to the particular measurement. Only has effect "
                          "if the batch file is to be used. The default "
                          "is %(default)s."),
                    action='store_true',
                    default=False)
parser.add_argument('--limitzoom',
                    help=("Limit maximum zoom level if needed to avoid "
                          "overly large map database. The default is "
                          "%(default)s."),
                    action='store_true',
                    default=False)
parser.add_argument('--useosm',
                    help=("Directory of OSM XML data files for map "
                          "database generation. The files should have the "
                          "map bounding box coordinates in their names! "
                          "Precise map database generation is not "
                          "guaranteed with this option!"))
args = parser.parse_args()

if not ((args.batch and args.repdir) or args.bounds):
  print >> sys.stderr, "Missing necessary data for map creation!\n"
  parser.print_help()
  exit(1)


print >> sys.stderr, "----- Main map database creation/update started. -----"
print >> sys.stderr, "Acquiring data for map generation..."

mapman = MapManager(args.mapdb)

# determine zoom level range
min_zoom_level, max_zoom_level = args.zooms

# determine map bounding box coordinates
map_bboxes = []
if args.batch and args.repdir:
  batch = Batch(args.batch, args.repdir, {}, {}, {}, {})
  try:
    start = batch.get_last_entry_start()
  except AssertionError, error:
    print >> sys.stderr, error.message
    exit(1)
  mapWorkspaceGroup = batch.filter(start=start,
                                   type='measproc.FileWorkSpace',
                                   class_name='searchAEBSWarnEval_Map.cSearch',
                                   title='AEBS-MapData')
  if mapWorkspaceGroup:
    for entry in mapWorkspaceGroup:
      workspace = batch.wake_entry(entry)
      measPath = batch.get_entry_attr(entry, 'fullmeas')
      map_bbox = mb.MapBbox.from_workspace(workspace)
      if map_bbox:
        map_bboxes.append(map_bbox)
  else:
    print >> sys.stderr, ("Map bounding box cannot be determined because of "
                          "no valid GPS data!")
    exit(2)
else:
  min_lon, min_lat, max_lon, max_lat = args.bounds
  map_bboxes.append( mb.MapBbox(min_lon, min_lat, max_lon, max_lat) )

if args.all:
  map_bboxes = [mb.MapBbox.from_mapbboxes(map_bboxes)]

print >> sys.stderr, "Generating Maperitive script (.mrc) files..."
mapdb_dir = os.path.dirname(args.mapdb)
temp_dir = tempfile.mkdtemp(suffix='', prefix='Temp_Scripts_Dbs_',
                            dir=mapdb_dir)
osm_presence = {}
if args.useosm:
  for osm_file in glob.glob(os.path.join(args.useosm, '*.osm')):
    osm_presence[osm_file] = mb.MapBbox.from_osm_name(osm_file)

map_bbox_zooms = {}
for map_bbox in map_bboxes:
  if args.limitzoom:
    max_zoom = map_bbox.limit_max_zoom_level(min_zoom_level, max_zoom_level)
    if max_zoom_level > max_zoom:
      print >> sys.stderr, ("WARNING: Max zoom level originally "
                            "chosen (%d) was too high! Max zoom "
                            "level re-adjusted to be %d."
                            % (max_zoom_level, max_zoom))
    map_bbox_zooms[map_bbox] = (min_zoom_level, max_zoom)
  else:
    map_bbox_zooms[map_bbox] = (min_zoom_level, max_zoom_level)

map_scripts = []
for map_bbox in map_bboxes:
  min_zoom, max_zoom = map_bbox_zooms[map_bbox]
  bound_in_db, min_zoom, max_zoom =\
      mapman.check_map_bbox_presence(map_bbox, min_zoom, max_zoom)
  if not bound_in_db:
    for osm_file, map_box in osm_presence.iteritems():
      if map_bbox in map_box:
        osm_2_use = osm_file
        break
    else:
      osm_2_use = None
    mrc_file = gms.createMaperitiveScript4MapDb(temp_dir, map_bbox,
                                                min_zoom_level=min_zoom,
                                                max_zoom_level=max_zoom,
                                                osm_2_use=osm_2_use)
    map_scripts.append(mrc_file)

if map_scripts:
  print >> sys.stderr, "Running Maperitive with script (.mrc) files..."
  if not os.path.exists(args.maperitive):
    print >> sys.stderr, ("Maperitive cannot be run! The executable file "
                          "might have been moved, its name changed or it is "
                          "actually not an executable file!")
    exit(3)
  map_scripts.append( gms.createMaperitiveExitScript(temp_dir) )
  map_scripts.insert(0, args.maperitive)
  subprocess.call(map_scripts)
else:
  print >> sys.stderr, "Running Maperitive was not needed..."

if not os.path.exists(mapman.map_db_loc):
  print >> sys.stderr, "Creating main map database..."
mapman.create_mapdb()
mbtiles_db_locs = glob.glob(os.path.join(temp_dir, '*.mbtiles'))
if mbtiles_db_locs:
  print >> sys.stderr, "Updating main map database..."
  for mbtiles_db_loc in mbtiles_db_locs:
      mapman.update_mapdb(mbtiles_db_loc)
else:
  print >> sys.stderr, "Updating main map database was not necessary..."

print >> sys.stderr, "Deleting temporary files and directories..."
shutil.rmtree(temp_dir)

print >> sys.stderr, "Checking main map database integrity..."
problematic_tiles = mapman.check_mapdb_integrity()
if problematic_tiles:
  temp_dir = tempfile.mkdtemp(suffix='', prefix='Temp_Scripts_Dbs_',
                              dir=mapdb_dir)
  prob_tiles_print = []
  prob_map_scripts = []
  for zoom_level, tiles in problematic_tiles.iteritems():
    prob_tiles_print.append("\t zoom level: %s; tiles: %s"
                            % (zoom_level, [(tile.x, tile.y) for tile in tiles]))
    for tile in tiles:
      ll_crnr_coord, ur_crnr_coord = tile.to_coord_corners(zoom_level)
      prob_map_bbox = mb.MapBbox(ll_crnr_coord.lon, ll_crnr_coord.lat,
                                 ur_crnr_coord.lon, ur_crnr_coord.lat)
      prob_map_script =\
          gms.createMaperitiveScript4MapDb(temp_dir, prob_map_bbox,
                                           min_zoom_level=zoom_level,
                                           max_zoom_level=zoom_level)
      prob_map_scripts.append(prob_map_script)
  print >> sys.stderr, ("Map database integrity errors found at:\n"
                        "%s\nAttempting fix..."
                        % '\n'.join(prob_tiles_print))
  prob_map_scripts.append( gms.createMaperitiveExitScript(temp_dir) )
  prob_map_scripts.insert(0, args.maperitive)
  subprocess.call(prob_map_scripts)
  for mbtiles_db_loc in glob.glob(os.path.join(temp_dir, '*.mbtiles')):
      mapman.fix_tiles_in_mapdb(mbtiles_db_loc, problematic_tiles)
  shutil.rmtree(temp_dir)
  print >> sys.stderr, "Fixing main map database finished."
else:
  print >> sys.stderr, "Main map database integrity is OK."
print >> sys.stderr, "----- Main map database creation/update finished. -----"
