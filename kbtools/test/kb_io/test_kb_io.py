"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\kb_io.py
'''

import numpy as np
import matplotlib.pyplot as plt

import unittest
import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self):
    ''' topic: ugdiff
        expected results:  constant sampling rate
    '''
    BatchFileName = "postproc_pngs_from_avi.bat"
    iSnapshotFromVideofile = kbtools.CSnapshotFromVideofile(BatchFileName)
    verbose = True
    iSnapshotFromVideofile.setVerbose(verbose)
    #FullPathFileName = r'E:\Measure1\DAS\EnduranceRun\EnduranceRun_HMCbus\2015-03-17_test\HMC_Bus__2015-03-17_22-10-07.MF4'
    FullPathFileName = r'.\measurement\M1SH10__2015-01-09_08-25-38.MF4'

    t_event_Multimedia = 1.0
    
    PngFileName = "mypng.png"
    iSnapshotFromVideofile.take_snapshot_ffmpeg(FullPathFileName, t_event_Multimedia, PngFileName = PngFileName)
    
    # batch file specified -> only batch file is created
    kbtools.SetBatchFileName_for_take_snapshot_from_videofile('my_batch.bat')
    kbtools.take_snapshot_from_videofile(FullPathFileName, t_event_Multimedia, PngFileName = 'LDW.png', verbose=True)

    # no batch file specified -> only png is created
    kbtools.SetBatchFileName_for_take_snapshot_from_videofile(None)
    kbtools.take_snapshot_from_videofile(FullPathFileName, t_event_Multimedia, PngFileName = 'LDW.png', verbose=True)

    
    #print "iSnapshotFromVideofile.BatchFileName", iSnapshotFromVideofile.BatchFileName
   
    
     
  #------------------------------------------------------------------------  
  def no_test_TC002(self):
    ''' topic: ugdiff
        expected results:  constant sampling rate
    '''
    
    
    t           = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0])
    u           = np.array([0.0, 0.1, 0.2, 0.4, 0.4, 0.2,   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0])
    y1_expected = np.array([0.0, 1.0, 1.0, 2.0, 0.0,-2.0,-2.0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0])   
    
    y1 = kbtools.ugdiff(t,u,verfahren=1)
        
    print "y1         ",y1
    print "y1_expected",y1_expected
    
    self.assertEqual(y1.tolist(), y1_expected.tolist(),msg="")
    
  #------------------------------------------------------------------------  
  def no_test_TC003(self):
    ''' topic: ugdiff
        expected results:  not equidistant sampling time
    '''
    
    
    t           = np.array([0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.4,   1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
    u           = np.array([0.0, 0.2, 0.4, 0.4, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.2,   0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    y1_expected = np.array([0.0, 1.0, 2.0, 0.0,-2.0,-2.0, 0.0, 0.0, 0.0, 0.0, 3.0, -12.0, 0.0, 0.0, 0.0, 0.0, 0.0])   
    
    y1 = kbtools.ugdiff(t,u,verfahren=1)
        
    print "y1         ",y1
    print "y1_expected",y1_expected
    for x1,x2 in zip(y1,y1_expected):
        print x1,x2
        self.assertAlmostEqual(x1, x2, places=5, msg="")
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for kb_io'
  unittest.main()
  



  
