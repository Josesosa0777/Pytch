import os
import unittest

from measproc.vidcalibs import VidCalibs

def build_file_name(vehicle, date, camera="", description="", ext="avi",
                    vehicle_date_sep="__"):
  filename = "%s" % vehicle
  if description:
    filename += "__%s" % description
  filename += vehicle_date_sep + date
  if camera:
    filename += "__%s" % camera
  if ext:
    filename = os.path.extsep.join((filename, ext))
  return filename

class TestParseMeasurement(unittest.TestCase):
  def do_single_test(self, vehicle, date, camera="", description="", ext="avi",
                     date_ref=None, **kwargs):
    filename = build_file_name(vehicle, date, camera, description, ext, **kwargs)
    vehicle_r, camera_r, date_r = VidCalibs.parse_measurement(filename)
    date = date_ref or date # workaround case when '-' is replaced by '_' in date
    for token in ("vehicle", "date", "camera"):
      self.assertTrue(eval("%s==%s_r" % (token, token)),
                      "Improper parser result for %s" % token)
    return
  
  def test_all_provided_basic(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","camera","description")

  def test_all_provided__date_dash(self):
    self.do_single_test("vehicle","2000-01-02-03-04-05","camera","description", date_ref="2000-01-02_03-04-05")

  def test_all_provided__vehicle_date_sep(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","camera","description", vehicle_date_sep='_')

  def test_nodesc_basic(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","camera","")

  def test_nocam_basic(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","","description")

  def test_nodesc_nocam_basic(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","","")

  def test_came__ra(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","came__ra","")

  def test_date_in_desc(self):
    self.do_single_test("vehicle","2000-01-02_03-04-05","",
                        "description_2001-08-05_09-02-01")

if __name__ == '__main__':
  unittest.main()
