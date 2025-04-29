import unittest
import numpy

from datavis.backend_map import LonDegreeFormatter, LatDegreeFormatter
import measproc.MapTileCalculation as mtc


class SetUpDegreeFormatterTest(unittest.TestCase):
  def setUp(self):
    self.zoom_level = 16
    self.x_axis_val_range = numpy.linspace(19.015, 19.0225, 10)
    self.y_axis_val_range = numpy.linspace(47.445, 47.450, 10)
    axis_value_coords = []
    for x_val, y_val in zip(self.x_axis_val_range, self.y_axis_val_range):
      axis_value_coords.append(mtc.Coord(x_val, y_val))
    self.map_orig_tile = axis_value_coords[0].to_tile(self.zoom_level)
    orig_tile_ll_corner = self.map_orig_tile.to_pixel_corners()[0]
    axis_value_ll_corner = axis_value_coords[0].to_pixel(self.zoom_level)
    self.crop_norm_value = (axis_value_ll_corner.x - orig_tile_ll_corner.x,
                            axis_value_ll_corner.y - orig_tile_ll_corner.y)
    self.x_axis_tick_values = []
    self.y_axis_tick_values = []
    for axis_value_coord in axis_value_coords:
      x_value = (axis_value_coord.to_pixel(self.zoom_level).x -
                 orig_tile_ll_corner.x -
                 self.crop_norm_value[0])
      y_value = (axis_value_coord.to_pixel(self.zoom_level).y -
                 orig_tile_ll_corner.y -
                 self.crop_norm_value[1])
      self.x_axis_tick_values.append(x_value)
      self.y_axis_tick_values.append(y_value)
    return


class DegreeFormatterTest(SetUpDegreeFormatterTest):
  @staticmethod
  def convert_dec_degrees_to_DMS(dec_degrees):
    dec_degrees = round(dec_degrees, 10)
    dec_sec = dec_degrees * 3600
    minutes = numpy.divide(dec_sec, 60)
    seconds = numpy.fmod(dec_sec, 60)
    degrees = numpy.divide(minutes, 60)
    minutes = numpy.fmod(minutes, 60)
    return int(degrees), int(minutes), seconds
  
  def test_lon_degree_formatter(self):
    deg_formatter = LonDegreeFormatter(self.zoom_level, self.map_orig_tile,
                                       self.crop_norm_value)
    lon_degs = []
    ref_lon_degs = []
    for value, ref_value in zip(self.x_axis_tick_values, self.x_axis_val_range):
      lon_degs.append(deg_formatter(value))
      degrees, minutes, seconds = self.convert_dec_degrees_to_DMS(ref_value)
      ref_lon_deg = u"%d\xb0 %d\' %.2f\'\'" % (degrees, minutes, seconds)
      ref_lon_degs.append(ref_lon_deg)
    formatting_is_OK = ref_lon_degs == lon_degs
    self.assertTrue(formatting_is_OK)
    return
  
  def test_lat_degree_formatter(self):
    deg_formatter = LatDegreeFormatter(self.zoom_level, self.map_orig_tile,
                                       self.crop_norm_value)
    lat_degs = []
    ref_lat_degs = []
    for value, ref_value in zip(self.y_axis_tick_values, self.y_axis_val_range):
      lat_degs.append(deg_formatter(value))
      degrees, minutes, seconds = self.convert_dec_degrees_to_DMS(ref_value)
      ref_lat_deg = u"%d\xb0 %d\' %.2f\'\'" % (degrees, minutes, seconds)
      ref_lat_degs.append(ref_lat_deg)
    formatting_is_OK = ref_lat_degs == lat_degs
    self.assertTrue(formatting_is_OK)
    return


if __name__ == "__main__":
  unittest.main()
