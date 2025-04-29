"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for util_DAS\kbtoolsuser\src\kbtools_user\ProcFLC20.py
'''

import numpy as np
import matplotlib.pyplot as plt

import unittest
import os

import kbtools
import kbtools_user

MatHomeDir = r'.\matlab_tmp'

# ==========================================================
def load_FLR20_sig(FullPathFileName,Vehicle=None,verbose=True):
    print "load_FLR20_sig"
    
    # get list of CANalyzer dbc files to use for data conversion
    myMetaData = kbtools_user.cMetaDataIO(VehicleName=Vehicle,verbose = verbose)
    dbc_list = myMetaData.GetMetaData(category='dbc_list')

    # get source
    Source = kbtools.load_Source(FullPathFileName,MatHomeDir = MatHomeDir,dbc_list=dbc_list,verbose=verbose)
   
    
    # ------------------------------------------------------
    FLR20_sig = None
    if Source is not None:
 
        # load signals for FLR20 in one dictionary,
        FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
        
        # ----------------------------------------------------------------        
        # addtional signals                
        #
        #FLR20_sig["Time_XBRAccDemand"],FLR20_sig["XBRAccDemand"] = kbtools.GetSignal(Source, "XBR", "ExtlAccelerationDemand")
               
        # ----------------------------------------------------------------        
        Source.save() # create backup directory
        print "   FLR20_sig loaded"  
        return FLR20_sig
    else:
        print "%s doesn't exist"%FullPathFileName
        return 
  

#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  
  
    #------------------------------------------------------------------------  
    def _abstract_test_case_CFLC20FusionMsgArray(self,TestCaseName,FullPathFileName,ExpectedResults):

        self.FLR20_sig = load_FLR20_sig(FullPathFileName)
    
        t_head   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        cnt_head = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Video_Data_General_A"]
        t_tail   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        cnt_tail = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Next_Left_B"]

        videopacket = kbtools_user.CFLC20FusionMsgArray(t_head, cnt_head, t_tail, cnt_tail)
    
        #t_videopacket = videopacket.t_head
        
        t_SamplingIntervals, SamplingIntervals = videopacket.getSamplingIntervals()    
    
        t_BxInfo, Bendix_Info3_delay = videopacket.calc_delay(self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"],self.FLR20_sig["FLC20_CAN"]["Frame_ID"], self.FLR20_sig["FLC20_CAN"]["Time_LNVU_Frame_Id_LSB"],self.FLR20_sig["FLC20_CAN"]["LNVU_Frame_Id_LSB"]) 
   
        print "t_BxInfo", t_BxInfo
         
        if ExpectedResults['t_BxInfo'] is None:
            self.assertIsNone(t_BxInfo,msg="%s"%TestCaseName)
        else:
            self.assertIsNotNone(t_BxInfo,msg="%s"%TestCaseName)
        
    
    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: CFLC20FusionMsgArray
            expected results:  good case
        '''
        TestCaseName = "good case"
    
        FullPathFileName = r'\\corp.knorr-bremse.com\str\measure1\DAS\EnduranceRun\EnduranceRun_M1SH8\2015-05-04\Ford_M1SH8__2015-05-04_22-10-29.mf4'  # okay
        ExpectedResults = {'t_BxInfo' : not None}
     
        self._abstract_test_case_CFLC20FusionMsgArray(TestCaseName,FullPathFileName,ExpectedResults)
    
    #------------------------------------------------------------------------  
    def test_TC002(self):
        ''' topic: CFLC20FusionMsgArray
            expected results:  issue case
        '''
        TestCaseName = "issue case"
        FullPathFileName = r'\\corp.knorr-bremse.com\str\measure1\DAS\EnduranceRun\EnduranceRun_M1SH8\2015-05-04\Ford_M1SH8__2015-05-04_23-06-10.mf4'  # issue
        ExpectedResults = {'t_BxInfo' : None}   # currently be very conservative -> in the future try to get more out of it
     
        self._abstract_test_case_CFLC20FusionMsgArray(TestCaseName,FullPathFileName,ExpectedResults)
    
   
    
    
    
  
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for timer'
  unittest.main()
  



  
