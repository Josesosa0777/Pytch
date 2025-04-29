#!C:\Python27\python.exe
"""
python update_batch.py batch_file report_dir

Search old style report file in batch_file and save them under `report_dir`.
"""

import xml.dom.minidom
import os
import sys
import shutil
import tempfile

batch_file = sys.argv[1]
report_dir = sys.argv[2]

if not os.path.exists(report_dir):
  os.makedirs(report_dir)

batch = xml.dom.minidom.parse(batch_file)
root = batch.firstChild
for node in root.childNodes:
  if node.nodeName == 'Report':
    path = node.getAttribute('ReportPath')
    if os.path.exists(path):
      report_base = os.path.basename(path)
      report_path = os.path.join(report_dir, report_base)
      if os.path.exists(report_path):
        report_base = report_base.split('.')[0]
        desc, report_path = tempfile.mkstemp(prefix=report_base, suffix='.xml', dir=report_dir)
      
      report = xml.dom.minidom.parse(path)
      header = report.firstChild
      if header.hasAttribute('TimeKey'):
        time_key = header.getAttribute('TimeKey')
        time_path = os.path.join(path, '..', '..', 'Times', time_key+'.npy')
        time_path = os.path.abspath(time_path)
        header.removeAttribute('TimeKey')
        open(path, 'w').write(report.toprettyxml())
      else:
        time_path, ext = os.path.splitext(path)
        time_path += '.npy'
      report_time_path, ext = os.path.splitext(report_path)
      report_time_path += '.npy'
      shutil.copyfile(time_path, report_time_path)
      shutil.move(path, report_path)
      node.setAttribute('ReportPath', report_path)
    else:
      root.removeChild(node)
open(batch_file, 'w').write(batch.toprettyxml())
