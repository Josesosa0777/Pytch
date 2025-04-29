# -*- dataeval: init -*-

"""
Prints the measurement comment to the standard output and to the logger.
The fill method returns the raw string value that can be easily used by
other modules, too.
"""

from interface import iView

class View(iView):
  def fill(self):
    comment = self.source.getFileComment()
    return comment
  
  def view(self, comment):
    self.logger.info("Measurement comment:\n\n%s\n\n" % comment)
    print "Measurement comment:\n\n%s\n\n" % comment
    return
