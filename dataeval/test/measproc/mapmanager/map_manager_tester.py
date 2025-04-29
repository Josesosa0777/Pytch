import unittest
import numpy as np
import os
import shutil
from PIL import Image, ImageChops
import cStringIO
import tempfile
import sqlite3
import subprocess
import argparse
import sys

import measproc.mapbbox as mbox
import measproc.MapTileCalculation as mtc
import measproc.mapmanager as mapman
import measproc.GenMaperitiveScripts as mapscript


parser = argparse.ArgumentParser()
parser.add_argument('--maperitive', 
                    help='location of map rendering software, Maperitive, default is %(default)s',
                    default=r'C:\Maperitive\Maperitive.exe')
parser.add_argument('-v', '--verbose',
                    help='Verbose output',
                    action="store_true",
                    default=False)
parser.add_argument('-q', '--quiet',
                    help='Minimal output',
                    action="store_true",
                    default=False)
parser.add_argument('-f', '--failfast',
                    help='Stop on first failure',
                    action="store_true",
                    default=False)
parser.add_argument('-c', '--catch',
                    help='Catch control-C and display results',
                    action="store_true",
                    default=False)
parser.add_argument('-b', '--buffer',
                    help='Buffer stdout and stderr during test runs',
                    action="store_true",
                    default=False)
parser.add_argument('unittest_args', nargs='*',
                    help=("Which part of the unittest to run."
                          "Examples:\n"
                          "  %(prog)s                         "
                          "  - run default set of tests\n"
                          "  %(prog)s MyTestSuite             "
                          "  - run suite 'MyTestSuite'\n"
                          "  %(prog)s MyTestCase.testSomething"
                          "  - run MyTestCase.testSomething"
                          "  %(prog)s MyTestCase              "
                          "  - run all 'test*' test methods in MyTestCase"))
args = parser.parse_args()
if not os.path.exists(args.maperitive):
  raise mapman.MapManagerError('%s: %s is not present\n'
                               % (__file__, args.maperitive))

flags = []
for key, value in vars(args).iteritems():
  if type(value) == bool and value:
    flags.append("--%s" % key)

argv = flags + args.unittest_args
sys.argv[1:] = argv


class SetUpMapManagerTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    min_lon = 19.015
    max_lon = 19.035
    min_lat = 47.445
    max_lat = 47.465
    cls.map_bbox_large = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    min_lon = 19.020
    max_lon = 19.030
    min_lat = 47.450
    max_lat = 47.460
    cls.map_bbox_small_incl = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    min_lon = 19.013
    max_lon = 19.015
    min_lat = 47.442
    max_lat = 47.445
    cls.map_bbox_small_excl = mbox.MapBbox(min_lon, min_lat, max_lon, max_lat)
    
    cls.min_zoom = 7
    cls.max_zoom = 16
    
    cls.spoilt_tile_data = {'zoom': np.array([16, 16, 16, 15]),
                            'tile_col': np.array([36229, 36231, 36232, 18114]),
                            'tile_row': np.array([42604, 42608, 42608, 21302])}
    
    cls.testdir = tempfile.mkdtemp(prefix='files_for_testing_',
                                   dir=os.path.dirname(__file__))
    
    mapdb_loc = os.path.join(cls.testdir, 'testing_mapdb.mapdb')
    cls.test_mapdb = mapman.MapManager(mapdb_loc)
    
    mbtiles_name_template = 'testing_mbtiles'
    dl_script_map_bbox =\
        mapscript.createMaperitiveScript4MapDb(cls.testdir,\
            cls.map_bbox_large, min_zoom_level=cls.min_zoom,
            max_zoom_level=cls.max_zoom,
            mbtiles_name_template=mbtiles_name_template)
    mbtiles_name =\
        cls.map_bbox_large.to_file_name(prefix=mbtiles_name_template,
                                        suffix='.mbtiles')
    cls.mbtiles_loc = os.path.join(cls.testdir, mbtiles_name)
    
    exit_script = mapscript.createMaperitiveExitScript(cls.testdir)
    
    subprocess.call([args.maperitive, dl_script_map_bbox, exit_script])
    return
  
  @classmethod
  def tearDownClass(cls):
    shutil.rmtree(cls.testdir)
    return


class MapManagerTest(SetUpMapManagerTest):
  def test_01_create_mapdb(self):
    self.test_mapdb.create_mapdb()
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    map_db_cur.execute("""SELECT name FROM sqlite_master
                          WHERE type='table'""")
    tables_in_mapdb = map_db_cur.fetchall()
    tables_in_mapdb = [table for table, in tables_in_mapdb]
    mapdb_created = 'tiles' in tables_in_mapdb and 'metadata' in tables_in_mapdb
    self.assertTrue(mapdb_created)
    return
  
  def test_02_update_mapdb(self):
    self.test_mapdb.update_mapdb(self.mbtiles_loc)
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    tiles_OK_4_zoom = []
    for zoom in xrange(self.min_zoom, self.max_zoom + 1, 1):
      tile_cols, tile_rows = self.test_mapdb.get_tile_cols_rows(map_db_cur, zoom)
      ref_tile_locs = self.map_bbox_large.get_tile_locs(zoom)
      ref_tile_cols, ref_tile_rows = zip(*ref_tile_locs)
      ref_tile_cols = list(set(ref_tile_cols))
      ref_tile_cols.sort()
      ref_tile_rows = list(set(ref_tile_rows))
      ref_tile_rows.sort()
      tiles_OK_4_zoom.append(tile_cols == ref_tile_cols
                             and tile_rows == ref_tile_rows)
    self.assertTrue(np.all(tiles_OK_4_zoom))
    return
  
  def test_03_check_map_bbox_presence_incl(self):
    map_bbox_present, min_zoom, max_zoom =\
        self.test_mapdb.check_map_bbox_presence(self.map_bbox_small_incl,
                                                self.min_zoom,
                                                self.max_zoom)
    totally_present = (map_bbox_present and min_zoom == self.min_zoom
                       and max_zoom == self.max_zoom)
    self.assertTrue(totally_present)
    return
  
  def test_04_check_map_bbox_presence_excl(self):
    map_bbox_present, _, _ =\
        self.test_mapdb.check_map_bbox_presence(self.map_bbox_small_excl,
                                                self.min_zoom,
                                                self.max_zoom)
    self.assertFalse(map_bbox_present)
    return
  
  def test_05_get_zooms_map_bbox(self):
    zooms_in_mapdb = self.test_mapdb.get_zooms_map_bbox(self.map_bbox_small_incl)
    ref_zooms = range(self.min_zoom, self.max_zoom + 1, 1)
    zoom_levels_match = zooms_in_mapdb == ref_zooms
    self.assertTrue(zoom_levels_match)
    return
  
  def img_equal(self, img1, img2):
    return ImageChops.difference(img1, img2).getbbox() is None
  
  def test_06_draw_map_image(self):
    zoom_level_of_test = 16
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    query = """SELECT tile_data FROM tiles
               WHERE zoom_level = ?
               AND tile_column = ?
               AND tile_row = ?"""
    map_image, map_orig_tile =\
        self.test_mapdb.draw_map_image(self.map_bbox_small_incl,
                                       zoom_level_of_test)
    ref_map_orig_tile =\
        self.map_bbox_small_incl.get_tile_locs(zoom_level_of_test)[0]
    ref_map_ur_tile =\
        self.map_bbox_small_incl.get_tile_locs(zoom_level_of_test)[-1]
    ref_x_tile_count, ref_y_tile_count =\
        self.map_bbox_small_incl.count_tiles(zoom_level_of_test)
    orig_tile_is_OK = (ref_map_orig_tile[0] == map_orig_tile.x
                       and ref_map_orig_tile[1] == map_orig_tile.y)
    map_image_size_is_OK = map_image.size == (mtc.TILE_SIZE * ref_x_tile_count,
                                              mtc.TILE_SIZE * ref_y_tile_count)
    ll_crop_bbox = (0, map_image.size[1] - mtc.TILE_SIZE,
                    mtc.TILE_SIZE, map_image.size[1])
    ll_tile_img = map_image.crop(ll_crop_bbox)
    map_db_cur.execute(query, (zoom_level_of_test, ref_map_orig_tile[0],
                               ref_map_orig_tile[1]))
    ll_tile_from_mapdb = map_db_cur.fetchone()
    ll_tile_from_mapdb = ll_tile_from_mapdb[0]
    ll_tile_from_mapdb = mapman.load_image(ll_tile_from_mapdb)
    ll_tiles_identical = self.img_equal(ll_tile_img, ll_tile_from_mapdb)
    ur_crop_bbox = (map_image.size[0] - mtc.TILE_SIZE, 0,
                    map_image.size[0], mtc.TILE_SIZE)
    ur_tile_img = map_image.crop(ur_crop_bbox)
    map_db_cur.execute(query, (zoom_level_of_test, ref_map_ur_tile[0],
                               ref_map_ur_tile[1]))
    ur_tile_from_mapdb = map_db_cur.fetchone()
    ur_tile_from_mapdb = ur_tile_from_mapdb[0]
    ur_tile_from_mapdb = mapman.load_image(ur_tile_from_mapdb)
    ur_tiles_identical = self.img_equal(ur_tile_img, ur_tile_from_mapdb)
    drawn_img_is_OK = (orig_tile_is_OK and map_image_size_is_OK
                       and ll_tiles_identical and ur_tiles_identical)
    self.assertTrue(drawn_img_is_OK)
    return
  
  def test_07_get_meta_data(self):
    meta_in_mapdb = self.test_mapdb.get_meta_data()
    meta_name_in_mapdb = meta_in_mapdb.keys()
    meta_name_in_mapdb.sort()
    meta_value_in_mapdb = meta_in_mapdb.values()
    meta_value_in_mapdb.sort()
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    map_query = map_db_cur.execute("SELECT name, value FROM metadata")
    ref_meta = map_query.fetchall()
    ref_meta_name, ref_meta_value = zip(*ref_meta)
    ref_meta_name = list(ref_meta_name)
    ref_meta_value = list(ref_meta_value)
    ref_meta_name.sort()
    ref_meta_value.sort()
    for idx, value in enumerate(ref_meta_value):
      try:
        ref_meta_value[idx] = int(value)
      except ValueError:
        continue
    meta_data_is_OK = (meta_name_in_mapdb == ref_meta_name
                       and meta_value_in_mapdb == ref_meta_value)
    self.assertTrue(meta_data_is_OK)
    return
  
  def check_mapdb_integrity_testing(self, mask):
    spoilt_tiles_data = (self.spoilt_tile_data['zoom'][mask],
                         self.spoilt_tile_data['tile_col'][mask],
                         self.spoilt_tile_data['tile_row'][mask])
    color = (241, 238, 232)
    query = """UPDATE tiles SET tile_data = ?
               WHERE zoom_level = ? AND
               tile_column = ? AND tile_row = ?"""
    tile_img = Image.new('RGBA', (256, 256), color)
    buf = cStringIO.StringIO()
    tile_img.save(buf, format='PNG')
    buf_img = buf.getvalue()
    img2db = sqlite3.Binary(buf_img)
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    for zoom, tile_col, tile_row in zip(*spoilt_tiles_data):
      zoom, tile_col, tile_row = int(zoom), int(tile_col), int(tile_row)
      map_db_cur.execute(query, (img2db, zoom, tile_col, tile_row))
    map_db.commit()
    map_db.close()
    probl_tiles = self.test_mapdb.check_mapdb_integrity()
    tile_check_is_OK = []
    for zoom, tiles in probl_tiles.iteritems():
      for tile in tiles:
        tile_check_is_OK.append(np.any(zoom == spoilt_tiles_data[0])
                                and np.any(tile.x == spoilt_tiles_data[1])
                                and np.any(tile.y == spoilt_tiles_data[2]))
    return tile_check_is_OK
  
  def fix_mapdb_integrity(self):
    probl_tiles_before_fix = self.test_mapdb.check_mapdb_integrity()
    self.test_mapdb.fix_tiles_in_mapdb(self.mbtiles_loc, probl_tiles_before_fix)
    probl_tiles_after_fix = self.test_mapdb.check_mapdb_integrity()
    fix_is_OK = len(probl_tiles_after_fix) == 0
    return fix_is_OK
  
  def test_08_check_mapdb_integrity_one_tile(self):
    mask = np.array([0])
    tile_check_is_OK = self.check_mapdb_integrity_testing(mask)
    self.assertTrue(len(tile_check_is_OK) == 1 and np.all(tile_check_is_OK))
    return
  
  def test_09_fix_tiles_in_mapdb_one_tile(self):
    fix_is_OK = self.fix_mapdb_integrity()
    self.assertTrue(fix_is_OK)
    return
  
  def test_10_check_mapdb_integrity_neighboring_tiles(self):
    mask = np.array([1, 2])
    tile_check_is_OK = self.check_mapdb_integrity_testing(mask)
    self.assertTrue(len(tile_check_is_OK) == 2 and np.all(tile_check_is_OK))
    return
  
  def test_11_fix_tiles_in_mapdb_neighboring_tiles(self):
    fix_is_OK = self.fix_mapdb_integrity()
    self.assertTrue(fix_is_OK)
    return
  
  def test_12_check_mapdb_integrity_tiles_at_diff_zooms(self):
    mask = np.array([0, 3])
    tile_check_is_OK = self.check_mapdb_integrity_testing(mask)
    self.assertTrue(len(tile_check_is_OK) == 2 and np.all(tile_check_is_OK))
    return
  
  def test_13_fix_tiles_in_mapdb_tiles_at_diff_zooms(self):
    fix_is_OK = self.fix_mapdb_integrity()
    self.assertTrue(fix_is_OK)
    return
  
  def test_14_delete_map_bbox(self):
    min_zoom_for_del = 14
    max_zoom_for_del = 15
    self.test_mapdb.delete_map_bbox(self.map_bbox_small_incl, min_zoom_for_del,
                                    max_zoom_for_del)
    map_db = sqlite3.connect(self.test_mapdb.map_db_loc)
    map_db_cur = map_db.cursor()
    tiles_are_deleted = []
    for zoom in xrange(min_zoom_for_del, max_zoom_for_del + 1):
      for tile_col, tile_row in self.map_bbox_small_incl.get_tile_locs(zoom):
        map_db_cur.execute("""SELECT tile_data FROM tiles
                               WHERE zoom_level = ? AND
                               tile_column = ? AND tile_row = ?""",
                            (zoom, tile_col, tile_row))
        tile = map_db_cur.fetchone()
        if tile is None:
          tiles_are_deleted.append(True)
    self.assertTrue(np.all(tiles_are_deleted))
    return


if __name__ == "__main__":
  unittest.main()
