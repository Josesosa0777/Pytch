from PIL import Image, ImageDraw
import logging
import cStringIO
import numpy
import os
import sqlite3
import sys

import measproc.MapTileCalculation as mtc


class MapManagerError(BaseException):
  pass


class MapManager(object):
  """
  Manages map databases and data-files. Downloads map data or map tile database
  from the Internet, checks integrity of the freshly downloaded database and
  inserts the tiles and other data to the local map database.
  :Parameters:
    maperitive_exe: str
      Location of the program, Maperitive on the hard disk drive. Maperitive is
      used for map data download and map rendering.
    maps_dir: str
      Root path of the map data and map database.
    map_db_name: str
      Name of the map database file to be used. If this is changed over time
      new data is saved into the database with the chosen file name.
  :Exception:
    MapManagerError: Any map management problem that cannot be fixed.
  """
  def __init__(self, map_db_loc):
    self.possible_map_bg_colors = [(241, 238, 232),
                                   (255, 255, 255),
                                   (242, 239, 233),
                                   (255, 254, 253),
                                   (24, 24, 24),
                                   (0, 0, 0)]
    """
    Possible values of map background colors for various rendering rules
    used by Maperitive (see *.mrules files in \Maperitive\Rules):
      - Default:      #F1EEE8 --> RGB (241, 238, 232)
      - Experimental: white   --> RGB (255, 255, 255)
      - GoogleMaps:   #F2EFE9 --> RGB (242, 239, 233)
      - Hiking:       #fffefd --> RGB (255, 254, 253)
      - PowerLines:   #181818 --> RGB (24, 24, 24)
      - urbanight:    black   --> RGB (0, 0, 0)
      - Wireframe:    #181818 --> RGB (24, 24, 24)
    Tile colors are given in RGBA: (R(ed), G(reen), B(lue), A(lpha)), where
    alpha is the transparency value, which is not used in comparison.
    """
    self.map_db_loc = map_db_loc
    self.osm_file = None
    self.logger = logging.getLogger()
    return

  def setOsmFile(self, osm):
    self.osm_file = osm
    return

  def check_map_bbox_presence(self, map_bbox, min_zoom_level, max_zoom_level):
    """
    Check if the map bounding box of interest at a given zoom level range
    (determined by: `min_zoom_level` and `max_zoom_level`) is in the main map
    database. The output is a list of a boolean value and a tuple. The boolean
    value is false if either the main database is missing or the map bounding
    box of interest is not in the database. If only certain zoom levels are
    missing the values of the tuple will be bounds of that zoom range otherwise
    its values are none.
    """
    # roi_presence_in_db: roi_in_db, min_zoom, max_zoom
    roi_presence_in_db = False, min_zoom_level, max_zoom_level
    if os.path.exists(self.map_db_loc):
      map_db = sqlite3.connect(self.map_db_loc)
      map_db_cur = map_db.cursor()
      zoom_in_db = set()
      zoom_levels = set(range(min_zoom_level, max_zoom_level + 1, 1))
      for zoom in zoom_levels:
        bbox_query = map_db_cur.execute("""SELECT tile_column, tile_row
                                           FROM tiles
                                           WHERE zoom_level = ?""",
                                        (zoom,))
        tiles_in_db = bbox_query.fetchall()
        tiles_in_bbox = set(map_bbox.get_tile_locs(zoom))
        tiles_in_db = set(tiles_in_db)
        if not tiles_in_bbox.difference(tiles_in_db):
          # there are no tiles present in the map bounding box that are missing
          # from the map database
          zoom_in_db.add(zoom)
      zooms_2_readjust = zoom_levels.difference(zoom_in_db)
      if zooms_2_readjust:
        new_min_zoom_level = min(zooms_2_readjust)
        new_max_zoom_level = max(zooms_2_readjust)
        roi_presence_in_db = False, new_min_zoom_level, new_max_zoom_level
      else:
        roi_presence_in_db = True, min_zoom_level, max_zoom_level
    return roi_presence_in_db

  def create_mapdb(self):
    """
    Creates the main map database if it is not already present.
    """
    if not os.path.exists(self.map_db_loc):
      map_db = sqlite3.connect(self.map_db_loc)
      map_db_cur = map_db.cursor()
      map_db_cur.execute("""CREATE TABLE tiles
                            (zoom_level  INTEGER,
                             tile_column INTEGER,
                             tile_row    INTEGER,
                             tile_data   BLOB);""")
      map_db_cur.execute("""CREATE UNIQUE INDEX tiles_unique
                            ON tiles(zoom_level, tile_column, tile_row);""")
      map_db_cur.execute("""CREATE TABLE metadata
                            (name  TEXT,
                             value TEXT);""")
      map_db_cur.execute("""CREATE UNIQUE INDEX metadata_unique
                            ON metadata(name);""")
      metadata_rows = [("name", "Map of measurements"),
                       ("type", "baselayer"),
                       ("version", "1"),
                       ("description", "Map tiles made with Maperitive"),
                       ("format", "png")]
      for name, value in metadata_rows:
        map_db_cur.execute("""INSERT OR IGNORE INTO metadata(name, value)
                              VALUES (?, ?)""",
                           (name, value))
      map_db.commit()
      map_db.close()
    else:
      self.logger.info("Map database already exists (%s)" % self.map_db_loc)
    return

  def update_mapdb(self, mbtiles_loc, db_ext='.mbtiles'):
    """
    Update the main map database with tiles and database contents data from the
    temporary mbtiles database located at `mbtiles_loc`.
    """
    if not os.path.exists(mbtiles_loc):
      raise MapManagerError("Database file (mbtiles) does not exists: %s"
                            % mbtiles_loc)
    elif not os.path.splitext(mbtiles_loc)[-1] == db_ext:
      raise MapManagerError("Requested file extension and database file "
                            "extension do not match!")

    mbtiles_db = sqlite3.connect(mbtiles_loc)
    mbtiles_db_cur = mbtiles_db.cursor()
    map_db = sqlite3.connect(self.map_db_loc)
    map_db_cur = map_db.cursor()

    mbtiles_db_cur.execute("""SELECT name FROM sqlite_master
                              WHERE type='table'""")
    tables_in_mbtiles = mbtiles_db_cur.fetchall()
    tables_in_mbtiles = [name for name, in tables_in_mbtiles]
    if tables_in_mbtiles:
      if (    'tiles' not in tables_in_mbtiles
          and 'metadata' not in tables_in_mbtiles):
        mbtiles_db.close()
        raise MapManagerError("The database does not contain appropriate "
                              "data for map creation: %s\n"
                              "No tile and metadata tables in database."
                              % os.path.basename(mbtiles_loc))
    else:
      mbtiles_db.close()
      raise MapManagerError("The database does not contain tables: %s\n"
                            % os.path.basename(mbtiles_loc))

    mbtiles_db_cur.execute("SELECT tile_data FROM tiles")
    mbtiles_db_tile, = mbtiles_db_cur.fetchone()
    png = load_image(mbtiles_db_tile)
    png_props = [("tile_mode", png.mode),
                 ("tile_size", png.size[0])]
    map_db_cur.execute("""SELECT name, value FROM metadata
                          WHERE name = ? OR name = ?""",
                       ('tile_mode', 'tile_size'))
    map_db_tile_props = dict(map_db_cur.fetchall())
    if len(map_db_tile_props.keys()) in [0, 1]:
      for name, value in png_props:
        map_db_cur.execute("""INSERT OR IGNORE INTO metadata(name, value)
                              VALUES (?, ?)""",
                           (name, value))
    else:
      if (png.mode != map_db_tile_props['tile_mode'] and
          png.size[0] != map_db_tile_props['tile_size']):
        raise MapManagerError("Image properties of tiles in inputed MBTiles "
                              "database (%s) is not the same as those in the "
                              "main map database! Tile image mode and size "
                              "do not match!"
                              % mbtiles_loc)
    mbtiles_db_cur.execute("SELECT * FROM tiles")
    for db_data in mbtiles_db_cur.fetchall():
      map_db_cur.execute("""INSERT OR IGNORE INTO
                            tiles(zoom_level, tile_column, tile_row, tile_data)
                            VALUES (?, ?, ?, ?)""",
                         db_data)
    map_db.commit()
    map_db.close()
    mbtiles_db.close()
    return

  def check_mapdb_integrity(self):
    """
    Checks if tiles inside the database are not empty, i.e. they contain usable
    data and not just a background color. Use this method after
    downloading/rendering map tiles but before updating the map database! Use
    this on the intermediate (temporary) mbtiles databases!
    """
    if os.path.exists(self.map_db_loc):
      map_db = sqlite3.connect(self.map_db_loc)
      map_db_cur = map_db.cursor()
    else:
      raise MapManagerError("Map database integrity check cannot be done "
                            "because the file does not exists:\n %s"
                            % self.map_db_loc)

    many_tile_query_text = """SELECT tile_data FROM tiles
                              WHERE zoom_level = ?
                              AND tile_column = ?
                              AND tile_row = ?"""

    min_zoom, max_zoom = self.get_zooms(map_db_cur)
    problematic_tiles = {}
    for zoom in xrange(min_zoom, max_zoom + 1, 1):
      tile_cols, tile_rows = self.get_tile_cols_rows(map_db_cur, zoom)
      empty_tiles = self.get_empty_tile_locs(map_db_cur, tile_cols,
                                             tile_rows, zoom)
      for empty_col, empty_row in empty_tiles:
        map_db_cur.execute(many_tile_query_text, (zoom, empty_col, empty_row))
        empty_tile, = map_db_cur.fetchone()

        neighbor_tiles = []

        map_db_cur.execute(many_tile_query_text,
                           (zoom, empty_col, empty_row + 1))
        upper_tile_in_db = map_db_cur.fetchone()
        if upper_tile_in_db is not None:
          upper_tile, = upper_tile_in_db
          tile_img = load_image(upper_tile)
          x_pixel, y_pixel = tile_img.size
          upper_box = (0, y_pixel - 1, x_pixel, y_pixel)
          neighbor_tiles.append([upper_tile, upper_box])
        else:
          neighbor_tiles.append([None, None])

        map_db_cur.execute(many_tile_query_text,
                           (zoom, empty_col, empty_row - 1))
        lower_tile_in_db = map_db_cur.fetchone()
        if lower_tile_in_db is not None:
          lower_tile, = lower_tile_in_db
          tile_img = load_image(lower_tile)
          x_pixel, _ = tile_img.size
          lower_box = (0, 0, x_pixel, 1)
          neighbor_tiles.append([lower_tile, lower_box])
        else:
          neighbor_tiles.append([None, None])

        map_db_cur.execute(many_tile_query_text,
                           (zoom, empty_col + 1, empty_row))
        right_tile_in_db = map_db_cur.fetchone()
        if right_tile_in_db is not None:
          right_tile, = right_tile_in_db
          tile_img = load_image(right_tile)
          _, y_pixel = tile_img.size
          right_box = (0, 0, 1, y_pixel)
          neighbor_tiles.append([right_tile, right_box])
        else:
          neighbor_tiles.append([None, None])

        map_db_cur.execute(many_tile_query_text,
                           (zoom, empty_col - 1, empty_row))
        left_tile_in_db = map_db_cur.fetchone()
        if left_tile_in_db is not None:
          left_tile, = left_tile_in_db
          tile_img = load_image(left_tile)
          x_pixel, y_pixel = tile_img.size
          left_box = (x_pixel - 1, 0, x_pixel, y_pixel)
          neighbor_tiles.append([left_tile, left_box])
        else:
          neighbor_tiles.append([None, None])

        empty_tile_colors = get_img_colors(empty_tile)
        cnt_tile_diff = 0
        for tile, box in neighbor_tiles:
          if tile is None or box is None: continue
          cropped_img_colors = get_img_colors(tile, crop_box=box)
          if len(cropped_img_colors) == 1:
            cropped_color_value = numpy.array(cropped_img_colors[0][-1][:-1])
            empty_color_value = numpy.array(empty_tile_colors[0][-1][:-1])
            if not numpy.allclose(cropped_color_value,
                                  empty_color_value, atol=2):
              cnt_tile_diff += 1
          else:
            cnt_tile_diff += 1
        if cnt_tile_diff:
          probl_zooms = problematic_tiles.setdefault(zoom, [])
          probl_zooms.append( mtc.Tile(empty_col, empty_row) )
    return problematic_tiles

  def get_zooms(self, map_db_cur):
    zoom_levels = map_db_cur.execute("SELECT zoom_level FROM tiles")
    zoom_levels = [zoom_level for zoom_level, in zoom_levels]
    min_zoom = min(zoom_levels)
    max_zoom = max(zoom_levels)
    return min_zoom, max_zoom

  def get_empty_tile_locs(self, map_db_cur, tile_cols, tile_rows, zoom):
    empty_tile_locs = []
    for tile_row in tile_rows:
      for tile_col in tile_cols:
        map_db_cur.execute("""SELECT tile_data FROM tiles
                              WHERE zoom_level = ?
                              AND tile_column = ?
                              AND tile_row = ?""",
                           (zoom, tile_col, tile_row))
        fetched_map_tile = map_db_cur.fetchone()
        if fetched_map_tile:
          map_tile, = fetched_map_tile
          tile_img_colors = get_img_colors(map_tile)
          # if tile has only one color and it is a map background color then
          # the tile is corrupt
          if (len(tile_img_colors) == 1
              and tile_img_colors[0][-1][:-1] in self.possible_map_bg_colors):
            empty_tile_locs.append((tile_col, tile_row))
    return empty_tile_locs

  def get_tile_cols_rows(self, map_db_cur, zoom):
    map_db_cur.execute("""SELECT tile_column, tile_row FROM tiles
                          WHERE zoom_level = ?""",
                       (zoom,))
    tile_props = map_db_cur.fetchall()
    tile_cols, tile_rows = zip(*tile_props)
    tile_cols = list(set(tile_cols))
    tile_cols.sort()
    tile_rows = list(set(tile_rows))
    tile_rows.sort()
    return tile_cols, tile_rows

  def fix_tiles_in_mapdb(self, mbtiles_loc, problematic_tiles):
    """
    If found attempt to fix problem of empty tiles in map database by
    redownloading map database for the affected zoom levels and update the
    problematic database with the new correct tiles.
    problematic_tiles : {zoom: [(tile_col, tile_row), ...]}
    """
    if not problematic_tiles: return

    if not os.path.exists(self.map_db_loc):
      raise MapManagerError("Map database fix cannot be done because the "
                            "file does not exists:\n %s"
                            % self.map_db_loc)

    map_db = sqlite3.connect(self.map_db_loc)
    mbtiles_db_cur = map_db.cursor()
    temp_db = sqlite3.connect(mbtiles_loc)
    temp_db_cur = temp_db.cursor()

    for zoom, tiles in problematic_tiles.iteritems():
      for tile in tiles:
        temp_db_cur.execute("""SELECT tile_data FROM tiles
                               WHERE zoom_level = ? AND
                               tile_column = ? AND tile_row = ?""",
                            (zoom, tile.x, tile.y))
        sel_fixed = temp_db_cur.fetchone()
        if sel_fixed:
          fixed_tile = sel_fixed[0]
          mbtiles_db_cur.execute("""UPDATE tiles SET tile_data = ?
                                    WHERE zoom_level = ? AND
                                    tile_column = ? AND tile_row = ?""",
                                 (fixed_tile, zoom, tile.x, tile.y))
    map_db.commit()
    temp_db.close()
    map_db.close()
    return

  def delete_map_bbox(self, map_bbox, min_zoom, max_zoom):
    """
    Deletes tiles from the map database defined by `map_bbox`, `min_zoom` and
    `max_zoom`. All zoom levels will be deleted between `min_zoom` and
    `max_zoom`! Use this with caution as it may hinder map display or delete all
    data from the map database rendering it useless!
    """
    map_db = sqlite3.connect(self.map_db_loc)
    map_db_cur = map_db.cursor()
    for zoom in xrange(min_zoom, max_zoom + 1, 1):
      tile_locs = map_bbox.get_tile_locs(zoom)
      for x_tile, y_tile in tile_locs:
        map_db_cur.execute("""DELETE FROM tiles
                              WHERE zoom_level = ? AND
                              tile_column = ? AND tile_row = ?""",
                           (zoom, x_tile, y_tile))
    map_db.commit()
    map_db.close()
    return

  def check_tiles_in_db(self, map_bbox, zoom):
    map_db = sqlite3.connect(self.map_db_loc)
    map_db_cur = map_db.cursor()

    tile_locs = map_bbox.get_tile_locs(zoom)
    for tile_col, tile_row in tile_locs:
      map_db_cur.execute("""SELECT tile_data FROM tiles
                                WHERE zoom_level = ?
                                AND tile_column = ?
                                AND tile_row = ?""",
                         (zoom, tile_col, tile_row))
      map_tile = map_db_cur.fetchone()
      if map_tile:
        return True
    return False

  def draw_map_image(self, map_bbox, zoom):
    """
    Draw map for the region given by its lower left and upper right corners at
    a given zoom level and return the image. Returns the map as a PIL image and
    the x and y coordinate number of the map's lower left tile.
    """
    map_db = sqlite3.connect(self.map_db_loc)
    map_db_cur = map_db.cursor()

    tile_props = self.get_meta_data()

    tile_locs = map_bbox.get_tile_locs(zoom)
    map_orig_tile = mtc.Tile(*tile_locs[0])
    tile_col_num, tile_row_num = map_bbox.count_tiles(zoom)
    map_image = Image.new(tile_props['tile_mode'],
                          (tile_props['tile_size'] * tile_col_num,
                           tile_props['tile_size'] * tile_row_num))
    missing_tiles = []
    for tile_col, tile_row in tile_locs:
      map_db_cur.execute("""SELECT tile_data FROM tiles
                            WHERE zoom_level = ?
                            AND tile_column = ?
                            AND tile_row = ?""",
                         (zoom, tile_col, tile_row))
      map_tile = map_db_cur.fetchone()
      if map_tile:
        map_tile = map_tile[0]
        map_tile_img = load_image(map_tile)
      else:
        map_tile_img = Image.new('RGBA',
                                 (tile_props['tile_size'],
                                  tile_props['tile_size']),
                                 color=(220, 220, 220))
        missing_tiles.append("zoom_level: %d, tile_col: %d, tile_row: %d"
                             % (zoom, tile_col, tile_row))

      tile_x_loc = (tile_col - map_orig_tile.x) * tile_props['tile_size']
      tile_y_loc = (tile_row - map_orig_tile.y) * tile_props['tile_size']
      # in case of TMS:
      tile_y_loc = abs(tile_y_loc - (map_image.size[1] -
                                     tile_props['tile_size']))

      map_image.paste(map_tile_img, (tile_x_loc, tile_y_loc))

    if missing_tiles:
      missing = "\n\t".join(missing_tiles)
      self.logger.warn("These tiles are missing from main map database:\n"
                       "\t%s" % missing)
    return map_image, map_orig_tile

  def get_meta_data(self):
    mapdb_metadata = {}
    map_db = sqlite3.connect(self.map_db_loc)
    map_db_cur = map_db.cursor()
    map_query = map_db_cur.execute("SELECT name, value FROM metadata")
    mapdb_metadata.update(map_query.fetchall())
    mapdb_metadata['version'] = int(mapdb_metadata['version'])
    mapdb_metadata['tile_size'] = int(mapdb_metadata['tile_size'])
    return mapdb_metadata

  def get_zooms_map_bbox(self, map_bbox):
    """
    Get zoom levels for which the given map region is fully present in the main
    map database.
    """
    if os.path.exists(self.map_db_loc):
      map_db = sqlite3.connect(self.map_db_loc)
      map_db_cur = map_db.cursor()
      map_db_cur.execute("SELECT DISTINCT zoom_level FROM tiles")
      zoom_levels = map_db_cur.fetchall()
      if zoom_levels:
        zooms_in_db_for_region = []
        zoom_levels = list(set([zoom_level for zoom_level, in zoom_levels]))
        zoom_levels.sort(reverse=True)
        for zoom in zoom_levels:
          map_db_cur.execute("""SELECT tile_column, tile_row FROM tiles
                                WHERE zoom_level = ?""",
                             (zoom,))
          tiles_in_db = map_db_cur.fetchall()
          if not tiles_in_db: continue
          tiles = map_bbox.get_tile_locs(zoom)
          tiles_in_bbox = set(tiles)
          tiles_in_db = set(tiles_in_db)
          if tiles_in_bbox.issubset(tiles_in_db):
            zooms_in_db_for_region.append(zoom)
        if zooms_in_db_for_region:
          zooms_in_db_for_region.sort()
        else:
          zoom = zoom_levels[int(len(zoom_levels) / 2) - 1]
          zooms_in_db_for_region.append(zoom)
          self.logger.warn("The requested map region cannot be retrieved from "
                           "the main map database at all! Please, update the "
                           "main map database!")
      else:
        raise MapManagerError("The database file does not contain the "
                              "required data (zoom levels)!")
    else:
      raise MapManagerError("Main map database does not exists!")
    return zooms_in_db_for_region


def load_image(image):
  img = cStringIO.StringIO(image)
  loaded_img = Image.open(img)
  return loaded_img


def get_img_colors(map_tile, crop_box=None):
  map_tile_img = load_image(map_tile)
  if crop_box:
    map_tile_img = map_tile_img.crop(crop_box)
  img_size = map_tile_img.size
  colormax = img_size[0] * img_size[1]
  tile_img_colors = map_tile_img.getcolors(maxcolors=colormax)
  return tile_img_colors
