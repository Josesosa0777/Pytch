"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

import os

def delete_files(path,ExtList):
  FileNameList = os.listdir(path)
  for FileName in FileNameList:
    #print FileName  
    FileNameNoExt, Ext = os.path.splitext(FileName)
    #print Ext
    if Ext in ExtList:
      os.remove(os.path.join(path, FileName))

if __name__ == '__main__':
  path = 'my_report'
  delete_files(path,['.tex','.eps','.ps','.aux','.dvi','.bat','.sty','.log','.out','.toc'])
 
