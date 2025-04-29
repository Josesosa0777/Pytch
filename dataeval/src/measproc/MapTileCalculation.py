import numpy

RADIUS = 6378137
"""
Earth's radius given in meters.
"""

TILE_SIZE = 256
"""
Size of one tile in pixels. As tiles are square shaped only one side is needed
to be given. All web map services use a value of 256. If to be modified values
that are multiples of 256 shall only be given.
"""

INITIAL_RESOLUTION = 2 * numpy.pi * RADIUS / TILE_SIZE
ORIGIN_SHIFT = 2 * numpy.pi * RADIUS / 2.0


class MapTileCalcError(BaseException):
  """
  Calculation parameters (specification and tile size) are wrong.
  """
  pass


class Coord(object):
  def __init__(self, lon, lat):
    self.lon = lon
    self.lat = lat
    return
  
  def __iter__(self):
    yield self.lon
    yield self.lat
  
  def __eq__(self, other):
    coords_close = (numpy.allclose(self.lon, other.lon)
                    and numpy.allclose(self.lat, other.lat))
    return coords_close
  
  def to_pixel(self, zoom, spec='TMS'):
    """
    Converts lon/lat in WGS84 Datum to pixel coordinates of the TMS (or OSM)
    Global Mercator pyramid. Be aware that the pixels are defined globally!
    """
    mx = self.lon * ORIGIN_SHIFT / 180.0
    my = (numpy.log(numpy.tan((90 + self.lat) * numpy.pi / 360.0)) /
          (numpy.pi / 180.0))
    my = my * ORIGIN_SHIFT / 180.0
    x = (mx + ORIGIN_SHIFT) / resolution(zoom)
    y = (my + ORIGIN_SHIFT) / resolution(zoom)
    if spec == 'OSM':
      y = convert_y_pixel(y, zoom)
    elif spec != 'TMS':
      raise MapTileCalcError("%s is not a supported specification! Please "
                             "only use either TMS or OSM."
                             % spec)
    pixel = Pixel(x, y, used_spec=spec)
    return pixel
  
  def to_tile(self, zoom, spec='TMS'):
    """
    Determines the tile's coordinate which contains the location, lon/lat in
    WGS84 Datum. The key word argument `spec` is the specification to be used
    for the calculation of tile coordinates. Can have two values only: either
    'TMs' or 'OMS'. Default value is 'TMS' as this is the one used by
    Maperitive at present.
    """
    pix = self.to_pixel(zoom)
    x_tile = int(numpy.ceil(pix.x / float(TILE_SIZE)) - 1)
    y_tile = int(numpy.ceil(pix.y / float(TILE_SIZE)) - 1)
    if spec == 'OSM':
      y_tile = convert_y_tile(y_tile, zoom)
    elif spec != 'TMS':
      raise MapTileCalcError("%s is not a supported specification! Please "
                             "only use either TMS or OSM."
                             % spec)
    tile = Tile(x_tile, y_tile, used_spec=spec)
    return tile


class Pixel(object):
  def __init__(self, x, y, used_spec='TMS'):
    self.x = x
    self.y = y
    self.spec = used_spec
    return
  
  @classmethod
  def to_lon(cls, x, zoom):
    """
    Convert x pixel coordinate of the TMS (or OSM) Global Mercator pyramid to
    longitude in WGS84 Datum. Be aware that globally defined pixels should be
    given!
    """
    mx = x * resolution(zoom) - ORIGIN_SHIFT
    lon = (mx / ORIGIN_SHIFT) * 180.0
    return lon
  
  @classmethod
  def to_lat(cls, y, zoom, spec='TMS'):
    """
    Convert y pixel coordinate of the TMS (or OSM) Global Mercator pyramid to
    latitude in WGS84 Datum. Be aware that globally defined pixels should be
    given!
    """
    if spec == 'OSM':
      y = convert_y_pixel(y, zoom)
    elif spec != 'TMS':
      raise MapTileCalcError("%s is not a supported specification! Please "
                             "only use either TMS or OSM."
                             % spec)
    my = y * resolution(zoom) - ORIGIN_SHIFT
    lat = (my / ORIGIN_SHIFT) * 180.0
    lat =\
        180 / numpy.pi * (2 * numpy.arctan(numpy.exp(lat * numpy.pi / 180.0)) -
                          numpy.pi / 2.0)
    return lat
  
  def to_coord(self, zoom):
    lon = self.to_lon(self.x, zoom)
    lat = self.to_lat(self.y, zoom, spec=self.spec)
    coord = Coord(lon, lat)
    return coord


class Tile(object):
  def __init__(self, x, y, used_spec='TMS'):
    self.x = x
    self.y = y
    self.spec = used_spec
    return
  
  def to_pixel_corners(self):
    """
    Determines the lower left and upper right corners of a tile given in pixel
    coordinates of the TMS (or OSM) Global Mercator pyramid for a given zoom
    level. Be aware that the pixels are defined globally!
    """
    ll_crnr_px = self.x * TILE_SIZE
    ll_crnr_py = self.y * TILE_SIZE
    ll_crnr_pixel = Pixel(ll_crnr_px, ll_crnr_py, used_spec=self.spec)
    ur_crnr_px = (self.x + 1) * TILE_SIZE
    ur_crnr_py = (self.y + 1) * TILE_SIZE
    ur_crnr_pixel = Pixel(ur_crnr_px, ur_crnr_py, used_spec=self.spec)
    return ll_crnr_pixel, ur_crnr_pixel
  
  def to_coord_corners(self, zoom):
    """
    Determines the lower left and upper right corners of a tile given in lon/lat
    in WGS84 Datum.
    """
    ll_crnr_pixel, ur_crnr_pixel = self.to_pixel_corners()
    ll_crnr_coord = ll_crnr_pixel.to_coord(zoom)
    ur_crnr_coord = ur_crnr_pixel.to_coord(zoom)
    return ll_crnr_coord, ur_crnr_coord
  
  def norm_pixel(self, pixel):
    """
    Normalizes pixel "coordinates" of a point or path so that it can be
    displayed on the map region of interest. The reference of the normalization
    is the tile by which this class has been instantiated!
    """
    if pixel.spec != self.spec:
      raise MapTileCalcError("The specifications of the reference tile and "
                             "the pixel to be normalized differs! "
                             "Specification of the tile: %s\n"
                             "Specification of the pixel: %s"
                             % (self.spec, pixel.spec))
    ll_crnr_pixel, _ = self.to_pixel_corners()
    norm_val_x = ll_crnr_pixel.x
    norm_val_y = ll_crnr_pixel.y
    norm_x = numpy.ones_like(pixel.x) * norm_val_x
    norm_y = numpy.ones_like(pixel.y) * norm_val_y
    normed_x = pixel.x - norm_x
    normed_y = pixel.y - norm_y
    pixel = Pixel(normed_x, normed_y, used_spec=self.spec)
    return pixel
  
  def unnorm_x_pixel(self, pixel):
    """
    Does the opposite of normalizeCoords for x coordinates.
    """
    if pixel.spec != self.spec:
      raise MapTileCalcError("The specifications of the reference tile and "
                             "the pixel to be unnormalized differs! "
                             "Specification of the tile: %s\n"
                             "Specification of the pixel: %s"
                             % (self.spec, pixel.spec))
    norm_values = self.to_pixel_corners()[0]
    norm_val_x = norm_values.x
    norm_x = numpy.ones_like(pixel.x) * norm_val_x
    unnormed_x = pixel.x + norm_x
    return unnormed_x
  
  def unnorm_y_pixel(self, pixel):
    """
    Does the opposite of normalizeCoords for y coordinates.
    """
    if pixel.spec != self.spec:
      raise MapTileCalcError("The specifications of the reference tile and "
                             "the pixel to be unnormalized differs! "
                             "Specification of the tile: %s\n"
                             "Specification of the pixel: %s"
                             % (self.spec, pixel.spec))
    norm_values = self.to_pixel_corners()[0]
    norm_val_y = norm_values.y
    norm_y = numpy.ones_like(pixel.y) * norm_val_y
    unnormed_y = pixel.y + norm_y
    return unnormed_y
  
  def unnorm_pixel(self, pixel):
    """
    Does the opposite of normalizeCoords for x coordinates.
    """
    unnormed_x = self.unnorm_x_pixel(pixel)
    unnormed_y = self.unnorm_y_pixel(pixel)
    pixel = Pixel(unnormed_x, unnormed_y)
    return pixel


def resolution(zoom):
  """"
  Resolution (meters/pixel) for given zoom level (measured at Equator)
  """
  return INITIAL_RESOLUTION / (2**zoom)

def zoom_for_pixel_resolution(pixel_resolution):
  """
  Maximal scale down zoom of the pyramid closest to the pixel resolution.
  Pixel resolution is a value given in meters/pixel which expresses the
  distance in meters a pixel covers.
  """
  scale_down_zoom = None
  for i in range(30):
    if pixel_resolution > resolution(i):
      scale_down_zoom = i-1 if i != 0 else 0  # We don't want to scale up
      break
  return scale_down_zoom

def convert_y_tile(y_tile, zoom):
  """
  Converts tiles from TMS specification to OMS and vica versa.
  """
  return (2**zoom - 1) - y_tile

def convert_y_pixel(y_pixel, zoom):
  """
  Converts tiles from TMS specification to OMS and vica versa.
  """
  return (2**zoom - 1) * TILE_SIZE - y_pixel

def get_distance_from_lat_lon(coord_A, coord_B):
  """
  Calculate distance between two coordinate in meter using the Haversine formula.
  https://en.wikipedia.org/wiki/Haversine_formula
  """
  coord_A_lat, coord_A_lon = numpy.deg2rad(coord_A.lat), numpy.deg2rad(coord_A.lon)
  coord_B_lat, coord_B_lon = numpy.deg2rad(coord_B.lat), numpy.deg2rad(coord_B.lon)
  delta_lat = coord_B_lat - coord_A_lat
  delta_lon = coord_B_lon - coord_A_lon
  a_value = numpy.square(numpy.sin(delta_lat / 2)) + (numpy.cos(coord_A_lat) * numpy.cos(coord_B_lat) *
                                                      numpy.square(numpy.sin(delta_lon / 2)))
  c_value = 2 * numpy.arctan2(numpy.sqrt(a_value), numpy.sqrt(1 - a_value))
  return RADIUS * c_value
