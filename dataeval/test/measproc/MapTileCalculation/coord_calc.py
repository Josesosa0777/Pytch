import unittest
import numpy as np

import measproc.MapTileCalculation as mtc

class SetUpMapCalcTest(unittest.TestCase):
  def setUp(self):
    self.zoom_level = 21
    
    lons = np.array([19.026260375976562, 19.026432037353515])
    lats = np.array([47.4594334284045, 47.45954949060109])
    lon_lat = (np.mean(lons), np.mean(lats))
    self.bbox_coord = mtc.Coord(lons, lats)
    self.ll_coord = mtc.Coord(lons[0], lats[0])
    self.ur_coord = mtc.Coord(lons[1], lats[1])
    self.coord = mtc.Coord(*lon_lat)
    lon_small_diff = lon_lat[0] + 7.e-5
    lat_small_diff = lon_lat[1] + 4.5e-4
    self.coord_small_diff = mtc.Coord(lon_small_diff, lat_small_diff)
    
    pixel_bbox_values_x = np.array([296809472, 296809728])
    pixel_bbox_values_y_OSM = np.array([187822336, 187822592])
    pixel_bbox_values_y_TMS = np.array([349048320, 349048576])
    pixel_xy = (np.mean(pixel_bbox_values_x), np.mean(pixel_bbox_values_y_OSM))
    self.pixel_OSM = mtc.Pixel(*pixel_xy, used_spec='OSM')
    self.pixel_2_unnorm_OSM = mtc.Pixel(pixel_xy[0] - pixel_bbox_values_x[0],
                                        pixel_xy[1] - pixel_bbox_values_y_OSM[0],
                                        used_spec='OSM')
    pixel_xy = (np.mean(pixel_bbox_values_x), np.mean(pixel_bbox_values_y_TMS))
    self.pixel_TMS = mtc.Pixel(*pixel_xy, used_spec='TMS')
    self.pixel_2_unnorm_TMS = mtc.Pixel(pixel_xy[0] - pixel_bbox_values_x[0],
                                        pixel_xy[1] - pixel_bbox_values_y_TMS[0],
                                        used_spec='TMS')
    self.ll_pixel_OSM = mtc.Pixel(pixel_bbox_values_x[0],
                                  pixel_bbox_values_y_OSM[0],
                                  used_spec='OSM')
    self.ll_pixel_TMS = mtc.Pixel(pixel_bbox_values_x[0],
                                  pixel_bbox_values_y_TMS[0],
                                  used_spec='TMS')
    self.ur_pixel_OSM = mtc.Pixel(pixel_bbox_values_x[1],
                                  pixel_bbox_values_y_OSM[1],
                                  used_spec='OSM')
    self.ur_pixel_TMS = mtc.Pixel(pixel_bbox_values_x[1],
                                  pixel_bbox_values_y_TMS[1],
                                  used_spec='TMS')
    
    self.TMS_tile_coord = (1159412, 1363470)
    self.tile_TMS = mtc.Tile(*self.TMS_tile_coord, used_spec='TMS')
    self.OSM_tile_coord = (1159412, 733681)
    self.tile_OSM = mtc.Tile(*self.OSM_tile_coord, used_spec='OSM')
    return


class TestCoord(SetUpMapCalcTest):
  def test_coord_iter(self):
    try:
      iter(self.coord)
    except TypeError:
      self.assertTrue(False)
    else:
      self.assertTrue(True)
    return
  
  def test_coord_eq_with_no_diff(self):
    bbox_coord = mtc.Coord(self.ll_coord.lon, self.ll_coord.lat)
    self.assertEqual(self.ll_coord, bbox_coord)
    return
  
  def test_coord_eq_with_small_diff(self):
    self.assertEqual(self.coord, self.coord_small_diff)
    return
  
  def test_coord_not_eq(self):
    self.assertNotEqual(self.coord, self.ll_coord)
    return
  
  def test_coord_to_OSM_pixel(self):
    pix = self.ll_coord.to_pixel(self.zoom_level, spec='OSM')
    check_value = (np.allclose(pix.x, self.ll_pixel_OSM.x)
                   and np.allclose(pix.y, self.ll_pixel_OSM.y))
    self.assertTrue(check_value)
    return
  
  def test_coord_to_TMS_pixel(self):
    pix = self.ll_coord.to_pixel(self.zoom_level, spec='TMS')
    check_value = (np.allclose(pix.x, self.ll_pixel_TMS.x)
                   and np.allclose(pix.y, self.ll_pixel_TMS.y))
    self.assertTrue(check_value)
    return
  
  def test_coord_to_TMS_tile(self):
    tile = self.coord.to_tile(self.zoom_level, spec='TMS')
    check_value = (np.allclose(tile.x, self.TMS_tile_coord[0])
                   and np.allclose(tile.y, self.TMS_tile_coord[1]))
    self.assertTrue(check_value)
    return
  
  def test_coord_to_OSM_tile(self):
    tile = self.coord.to_tile(self.zoom_level, spec='OSM')
    check_value = (np.allclose(tile.x, self.OSM_tile_coord[0])
                   and np.allclose(tile.y, self.OSM_tile_coord[1]))
    self.assertTrue(check_value)
    return
  
  def test_coord_to_pixel_then_back_to_coord(self):
    pix = self.coord.to_pixel(self.zoom_level)
    coord_back = pix.to_coord(self.zoom_level)
    self.assertEqual(self.coord, coord_back)
    return
  
  def test_coord_to_pixel_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.coord.to_pixel(self.zoom_level, spec='ABC')
    return
  
  def test_coord_to_tile_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.coord.to_tile(self.zoom_level, spec='ABC')
    return


if __name__ == "__main__":
  unittest.main()
