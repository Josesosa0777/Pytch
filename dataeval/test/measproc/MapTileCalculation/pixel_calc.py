import unittest

import measproc.MapTileCalculation as mtc
from coord_calc import SetUpMapCalcTest


class TestPixel(SetUpMapCalcTest):
  def test_pixel_TMS_to_lon(self):
    lon = mtc.Pixel.to_lon(self.ll_pixel_TMS.x, self.zoom_level)
    self.assertAlmostEqual(lon, self.ll_coord.lon)
    return
  
  def test_pixel_TMS_to_lat(self):
    lat = mtc.Pixel.to_lat(self.ll_pixel_TMS.y, self.zoom_level, spec='TMS')
    self.assertAlmostEqual(lat, self.ll_coord.lat)
    return
  
  def test_pixel_TMS_to_coord(self):
    coord = self.ll_pixel_TMS.to_coord(self.zoom_level)
    self.assertEqual(coord, self.ll_coord)
    return
  
  def test_pixel_OSM_to_lon(self):
    lon = mtc.Pixel.to_lon(self.ll_pixel_OSM.x, self.zoom_level)
    self.assertAlmostEqual(lon, self.ll_coord.lon)
    return
  
  def test_pixel_OSM_to_lat(self):
    lat = mtc.Pixel.to_lat(self.ll_pixel_OSM.y, self.zoom_level, spec='OSM')
    self.assertAlmostEqual(lat, self.ll_coord.lat)
    return
  
  def test_pixel_OSM_to_coord(self):
    coord = self.ll_pixel_OSM.to_coord(self.zoom_level)
    self.assertEqual(coord, self.ll_coord)
    return
  
  def test_pixel_to_lat_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      mtc.Pixel.to_lat(self.pixel_TMS.y, self.zoom_level, spec='ABC')
    return


if __name__ == "__main__":
  unittest.main()
