"""
:Organization: Knorr-Bremse SfN GmbH Budapest, Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' run batch server - clone of server_server.m '''

import kbtools

#===================================================================================================  
if __name__ == "__main__":
  
  # root path where the Batch Server is located
  PathName_root = r'C:\KBData\Python_batch_process'
  
  # init the Batch Server
  myBatchServer = kbtools.cBatchServer(PathName_root)
  
  # run Batch Server - stop by control-C
  myBatchServer.run()
