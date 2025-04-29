# -*- coding: utf-8 -*-

import unittest

from measparser.mf4 import parseFileComment

xml_comment = """
<HDcomment>
  <TX>
    sw:  MAN_OI_AEBS_2012-11-05

    HW: CVR3-C3 sample -23°C

    Comment ça va ? Très bien. öűő

    stationäres Ziel (balloon car)
    vEgo=40km/h konst.
    Ergebniss: iO. (Abstand 1,5m)
  </TX>
  <common_properties><e name="author"/>
    <e name="department">T/CES3.2</e>
    <e name="project">AEBS/ACC</e>
    <e name="subject">06S-0174</e>
  </common_properties>
</HDcomment>
"""

class Test(unittest.TestCase):
  def test(self):
    comment = parseFileComment(xml_comment)
    self.assertTrue(isinstance(comment, str))
    self.assertFalse(isinstance(comment, unicode))
    return

if __name__ == '__main__':
  unittest.main()

