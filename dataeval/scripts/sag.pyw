"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
Synchronizer application generator.
"""
__docformat__ = "restructuredtext en"

import sys
import Tkinter as tk

import dmw
import interface

argv = '-c selectGroup'.split()
if len(sys.argv) > 1:
  argv.extend(sys.argv[1:])
Config, Measurements = interface.parseArgv(argv)
root = tk.Tk()
root.title('mort')

ButtonWidth = 10
Frame = tk.Frame(root)
Frame.pack()
ViewControl = dmw.ViewControlFrame.cViewControlFrame(Frame, Config, ButtonWidth)
ViewControl.pack()
dmw.GeneralSectionFrame.cGeneralSectionFrame(Frame, Config).pack()
dmw.SyncAppEditor.cSyncAppEditor(Frame, Config, ViewControl.Control, ButtonWidth).pack()

raw_input("Press Enter to exit\n")
Config.save()
