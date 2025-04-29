# -*- dataeval: init -*-

"""
Prints the KB-specific FLR21 IDs to the standard output and to the logger.
The fill method returns a dictionary with int values that can be easily used by
other modules, too.
"""

from interface import iView

signals = (
  "SMess_Protocol_Version",
  "KBAEBS_Lib_VersionMajor",
  "KBAEBS_Lib_VersionMinor",
  "KBAEBS_Cust_VersionMajor",
  "KBAEBS_Cust_VersionMinor",
  "KBAEBS_Priv_VersionMajor",
  "KBAEBS_Priv_VersionMinor",
  "KBAEBS_Priv_Customer_ID",
)

sgs = [{s: ("ACC_S98", s) for s in signals}]

class View(iView):
  def check(self):
    group = self.source.selectLazySignalGroup(sgs)
    assert group, "KB-specific FLR21 ID information not available"
    return group
  
  def fill(self, group):
    return {s: int(group.get_value(s)[0]) for s in signals if s in group}
  
  def view(self, versions):
    NA = "n/a"
    msg = ["KB-specific FLR21 IDs:"]
    
    msg.append("* S-Message Protocol Version: %s" %
      versions.get("SMess_Protocol_Version", NA))
    msg.append("* KB AEBS Library Version: %s.%s" %
      (versions.get("KBAEBS_Lib_VersionMajor", NA),
       versions.get("KBAEBS_Lib_VersionMinor", NA)))
    msg.append("* KB AEBS Customer Dataset Version: %s.%s" %
      (versions.get("KBAEBS_Cust_VersionMajor", NA),
       versions.get("KBAEBS_Cust_VersionMinor", NA)))
    msg.append("* KB AEBS Private Dataset Version: %s.%s" %
      (versions.get("KBAEBS_Priv_VersionMajor", NA),
       versions.get("KBAEBS_Priv_VersionMinor", NA)))
    msg.append("* KB AEBS Customer ID: %s" %
      versions.get("KBAEBS_Priv_Customer_ID", NA))
    
    msg_str = "\n".join(msg)
    self.logger.info(msg_str)
    print msg_str
    return
