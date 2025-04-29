import unittest
import numpy as np

import measproc.MapTileCalculation as mtc
from coord_calc import SetUpMapCalcTest


class TestTile(SetUpMapCalcTest):
  def test_tile_TMS_to_pixel_corners(self):
    ll_crnr_pixel, ur_crnr_pixel = self.tile_TMS.to_pixel_corners()
    check_value = ((np.allclose(self.ll_pixel_TMS.x, ll_crnr_pixel.x)
                    and np.allclose(self.ll_pixel_TMS.y, ll_crnr_pixel.y))
                   and (np.allclose(self.ur_pixel_TMS.x, ur_crnr_pixel.x)
                        and np.allclose(self.ur_pixel_TMS.y, ur_crnr_pixel.y)))
    self.assertTrue(check_value)
    return
  
  def test_tile_TMS_to_coord_corners(self):
    ll_crnr_coord, ur_crnr_coord = self.tile_TMS.to_coord_corners(self.zoom_level)
    check_value = (self.ll_coord == ll_crnr_coord
                   and self.ur_coord == ur_crnr_coord)
    self.assertTrue(check_value)
    return
  
  def test_tile_TMS_norm_pixel(self):
    ref_pix_x = self.pixel_TMS.x - self.ll_pixel_TMS.x
    ref_pix_y = self.pixel_TMS.y - self.ll_pixel_TMS.y
    normed_pix = self.tile_TMS.norm_pixel(self.pixel_TMS)
    check_value = (np.allclose(ref_pix_x, normed_pix.x)
                   and np.allclose(ref_pix_y, normed_pix.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_TMS_unnorm_x_pixel(self):
    unnormed_pix_x = self.tile_TMS.unnorm_x_pixel(self.pixel_2_unnorm_TMS)
    self.assertEqual(unnormed_pix_x, self.pixel_TMS.x)
    return
  
  def test_tile_TMS_unnorm_y_pixel(self):
    unnormed_pix_y = self.tile_TMS.unnorm_y_pixel(self.pixel_2_unnorm_TMS)
    self.assertEqual(unnormed_pix_y, self.pixel_TMS.y)
    return
  
  def test_tile_TMS_unnorm_pixel(self):
    unnormed_pix = self.tile_TMS.unnorm_pixel(self.pixel_2_unnorm_TMS)
    check_value = (np.allclose(unnormed_pix.x, self.pixel_TMS.x)
                   and np.allclose(unnormed_pix.y, self.pixel_TMS.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_TMS_norm_then_unnorm_pixel(self):
    normed_pix = self.tile_TMS.norm_pixel(self.pixel_TMS)
    unnormed_pix = self.tile_TMS.unnorm_pixel(normed_pix)
    check_value = (np.allclose(self.pixel_TMS.x, unnormed_pix.x)
                   and np.allclose(self.pixel_TMS.y, unnormed_pix.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_OSM_to_pixel_corners(self):
    ll_crnr_pixel, ur_crnr_pixel = self.tile_OSM.to_pixel_corners()
    check_value = ((np.allclose(self.ll_pixel_OSM.x, ll_crnr_pixel.x)
                    and np.allclose(self.ll_pixel_OSM.y, ll_crnr_pixel.y))
                   and (np.allclose(self.ur_pixel_OSM.x, ur_crnr_pixel.x)
                        and np.allclose(self.ur_pixel_OSM.y, ur_crnr_pixel.y)))
    self.assertTrue(check_value)
    return
  
  def test_tile_OSM_to_coord_corners(self):
    ll_crnr_coord, ur_crnr_coord = self.tile_OSM.to_coord_corners(self.zoom_level)
    check_value = (self.ll_coord == ll_crnr_coord
                   and self.ur_coord == ur_crnr_coord)
    self.assertTrue(check_value)
    return
  
  def test_tile_OSM_norm_pixel(self):
    ref_pix_x = self.pixel_OSM.x - self.ll_pixel_OSM.x
    ref_pix_y = self.pixel_OSM.y - self.ll_pixel_OSM.y
    normed_pix = self.tile_OSM.norm_pixel(self.pixel_OSM)
    check_value = (np.allclose(ref_pix_x, normed_pix.x)
                   and np.allclose(ref_pix_y, normed_pix.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_OSM_unnorm_x_pixel(self):
    unnormed_pix_X = self.tile_OSM.unnorm_x_pixel(self.pixel_2_unnorm_OSM)
    self.assertEqual(unnormed_pix_X, self.pixel_OSM.x)
    return
  
  def test_tile_OSM_unnorm_y_pixel(self):
    unnormed_pix_Y = self.tile_OSM.unnorm_y_pixel(self.pixel_2_unnorm_OSM)
    self.assertEqual(unnormed_pix_Y, self.pixel_OSM.y)
    return
  
  def test_tile_OSM_unnorm_pixel(self):
    unnormed_pix = self.tile_OSM.unnorm_pixel(self.pixel_2_unnorm_OSM)
    check_value = (np.allclose(unnormed_pix.x, self.pixel_OSM.x)
                   and np.allclose(unnormed_pix.y, self.pixel_OSM.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_OSM_norm_then_unnorm_pixel(self):
    normed_pix = self.tile_OSM.norm_pixel(self.pixel_OSM)
    unnormed_pix = self.tile_OSM.unnorm_pixel(normed_pix)
    check_value = (np.allclose(self.pixel_OSM.x, unnormed_pix.x)
                   and np.allclose(self.pixel_OSM.y, unnormed_pix.y))
    self.assertTrue(check_value)
    return
  
  def test_tile_norm_pixel_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.tile_TMS.norm_pixel(self.pixel_OSM)
    return
  
  def test_tile_unnorm_x_pixel_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.tile_TMS.unnorm_x_pixel(self.pixel_OSM)
    return
  
  def test_tile_unnorm_y_pixel_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.tile_TMS.unnorm_x_pixel(self.pixel_OSM)
    return
  
  def test_tile_unnorm_pixel_gen_map_tile_calc_error(self):
    with self.assertRaises(mtc.MapTileCalcError):
      self.tile_TMS.unnorm_pixel(self.pixel_OSM)
    return

if __name__ == "__main__":
  unittest.main()
