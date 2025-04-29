"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for lib_dataio\measparser\SignalSource.py
(Regression Test for Kbtools SignalSource Interface)
'''

''' 
to do:
1) getSignal optional parameters: Tmin=t_start, Tmax=t_stop, ScaleTime = sig['t']


'''


# python standard imports
import unittest
import shutil
import os
import time
import numpy as np


# KB specific imports
import measparser

# ------------------------------------------------------------
# test data 

# measurement file

# path to original location of test data
testdata_dir_src  = r'..\..\..\..\..\testdata'

# file with test data (mdf format)
testdata_FileName = r'CVR3_B1_2011-02-10_16-53_020.mdf'

# test oracle (expected results) for test data

# for use with getSignals (old school)
test_oracle1 = {
     'sig1':{'device':"MRR1plus-0-0", 'signal':"evi.General_TC.vxvRef",  'len':269,   'idx':10, 'time_at_idx':5.5123406e+000, 'value_at_idx':1.4804688e+001},
     'sig2':{'device':"MRR1plus-0-0", 'signal':"evi.General_T20.vxvRef", 'len':1500 , 'idx':10, 'time_at_idx':4.7470251e+000, 'value_at_idx':1.4226563e+001},
     }

# for use with SignalGroups
test_oracle2 = {
     'sig1':{'device':"MRR1plus", 'signal':"evi.General_TC.vxvRef",  'len':269,   'idx':10, 'time_at_idx':5.5123406e+000, 'value_at_idx':1.4804688e+001},
     'sig2':{'device':"MRR1plus", 'signal':"evi.General_T20.vxvRef", 'len':1500 , 'idx':10, 'time_at_idx':4.7470251e+000, 'value_at_idx':1.4226563e+001},
     'sig3':{'device':"VBOX_1",   'signal':"Time_Since_Midnight",    'len':3000 , 'idx':10, 'time_at_idx':4.6448700e+000, 'value_at_idx':5.7203220e+004},
     }


#========================================================================================
# helper functions
def create_local_copy_of_testdata(testdata_dir_dest):
  # create a local copy of the testdata, because we want to keep the testdata dictiornary untouched
  
  if not os.path.isdir(testdata_dir_dest):
    os.makedirs(testdata_dir_dest) 
  shutil.copyfile(os.path.join(testdata_dir_src,testdata_FileName),os.path.join(testdata_dir_dest,testdata_FileName))

def delete_dir(PathName): 
  # delete directory 
  if os.path.isdir(PathName):
    shutil.rmtree(PathName)
  if os.path.isdir(PathName):
    # remove was not successful
    return False
  return True

#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' load measurement data and extract signals using getSignal (old school) + read for a second time ''' 
    
    # select test oracle
    test_oracle = test_oracle1
    
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    
    print "test_TC001"
    print 
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir
    self.assertTrue(delete_dir(local_testdata_dir))
      
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)
      
    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
    FullPathFileName = os.path.join(local_testdata_dir, testdata_FileName)
    print "FullPathFileName:" , FullPathFileName
    print
      
    tic = time.clock()
    
    Source = measparser.cSignalSource(FullPathFileName)
      
    # TC Task
    Time1, Value1 = Source.getSignal(test_oracle['sig1']['device'], test_oracle['sig1']['signal'])

    # T20 Task
    Time2, Value2 = Source.getSignal(test_oracle['sig2']['device'], test_oracle['sig2']['signal'])
    
    toc = time.clock()

    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print

    tic = time.clock()
    # create backup directory
    Source.save()
    toc = time.clock()
    print "Source.save() -> elapsed time: ", toc-tic
    print
    
    
    # report the results       
    print "test_oracle['sig1']['device']       = %s" % test_oracle['sig1']['device']
    print "test_oracle['sig1']['signal']       = %s" % test_oracle['sig1']['signal']
    print "test_oracle['sig1']['len']          = %d" % len(Time1)
    print "test_oracle['sig1']['idx']          = %d" % test_oracle['sig1']['idx']
    print "test_oracle['sig1']['time_at_idx']  = %10.7e" % Time1[test_oracle['sig1']['idx']]
    print "test_oracle['sig1']['value_at_idx'] = %10.7e" % Value1[test_oracle['sig1']['idx']]
    print
      
    print "test_oracle['sig2']['device']       = %s" % test_oracle['sig2']['device']
    print "test_oracle['sig2']['signal']       = %s" % test_oracle['sig2']['signal']
    print "test_oracle['sig2']['len']          = %d" % len(Time2)
    print "test_oracle['sig2']['idx']          = %d" % test_oracle['sig2']['idx']
    print "test_oracle['sig2']['time_at_idx']  = %10.7e" % Time2[test_oracle['sig2']['idx']]
    print "test_oracle['sig2']['value_at_idx'] = %10.7e" % Value2[test_oracle['sig2']['idx']]
    print
      
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
     
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # Backup directory
    if not os.path.exists(os.path.join(local_testdata_dir,'Backup')):                            Test_passed = False
    
    
    # ----------------------------------------------------
    # read for the second time
    print "read for the second time"
    print
    
    # destroy references,  todo check if destructors are called
    Source = None
    Time1  = None
    Value1 = None 
    Time2  = None
    Value2 = None 
    
    tic = time.clock()

    Source = measparser.cSignalSource(FullPathFileName)
      
    # TC Task
    Time1, Value1 = Source.getSignal(test_oracle['sig1']['device'], test_oracle['sig1']['signal'])

    # T20 Task
    Time2, Value2 = Source.getSignal(test_oracle['sig2']['device'], test_oracle['sig2']['signal'])

    toc = time.clock()
    
    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print
          
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
     
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # Backup directory
    if not os.path.exists(os.path.join(local_testdata_dir,'Backup')):                            Test_passed = False
    
    # report results
    self.assertTrue(Test_passed) 
    print "test_TC001 successful"
    print

  #------------------------------------------------------------------------  
  def test_TC002(self): 
    ''' different local directory, load measurement data and extract signals using getSignal (old school) ''' 

    test_oracle = test_oracle1
  
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir = r'MyNpyHomeDir'
    
    print "test_TC002"
    print 
    
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir and MyNpyHomeDir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))
          
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)
      
    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
    

    FullPathFileName = os.path.join(local_testdata_dir, testdata_FileName)
    print "FullPathFileName:" , FullPathFileName
    print
    
    tic = time.clock()

    Source = measparser.cSignalSource(FullPathFileName, MyNpyHomeDir)
      
    # TC Task
    Time1, Value1 = Source.getSignal(test_oracle['sig1']['device'], test_oracle['sig1']['signal'])

    # T20 Task
    Time2, Value2 = Source.getSignal(test_oracle['sig2']['device'], test_oracle['sig2']['signal'])

    toc = time.clock()

    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print
    
    tic = time.clock()
    # create backup directory
    Source.save()
    toc = time.clock()
    print "Source.save() -> elapsed time: ", toc-tic
    print


    # report the results       
    print "test_oracle['sig1']['device']       = %s" % test_oracle['sig1']['device']
    print "test_oracle['sig1']['signal']       = %s" % test_oracle['sig1']['signal']
    print "test_oracle['sig1']['len']          = %d" % len(Time1)
    print "test_oracle['sig1']['idx']          = %d" % test_oracle['sig1']['idx']
    print "test_oracle['sig1']['time_at_idx']  = %10.7e" % Time1[test_oracle['sig1']['idx']]
    print "test_oracle['sig1']['value_at_idx'] = %10.7e" % Value1[test_oracle['sig1']['idx']]
    print
      
    print "test_oracle['sig2']['device']       = %s" % test_oracle['sig2']['device']
    print "test_oracle['sig2']['signal']       = %s" % test_oracle['sig2']['signal']
    print "test_oracle['sig2']['len']          = %d" % len(Time2)
    print "test_oracle['sig2']['idx']          = %d" % test_oracle['sig2']['idx']
    print "test_oracle['sig2']['time_at_idx']  = %10.7e" % Time2[test_oracle['sig2']['idx']]
    print "test_oracle['sig2']['value_at_idx'] = %10.7e" % Value2[test_oracle['sig2']['idx']]
    print
    
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
     
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # Backup directory
    if os.path.exists(os.path.join(local_testdata_dir,'Backup')):                                Test_passed = False
    if not os.path.exists(os.path.join(MyNpyHomeDir,testdata_FileName)):                         Test_passed = False

    # ----------------------------------------------------
    # read for the second time
    print "read for the second time"
    print
    
    # destroy references,  todo check if destructors are called
    Source = None
    Time1  = None
    Value1 = None 
    Time2  = None
    Value2 = None 
    
    tic = time.clock()

    Source = measparser.cSignalSource(FullPathFileName, MyNpyHomeDir)
      
    # TC Task
    Time1, Value1 = Source.getSignal(test_oracle['sig1']['device'], test_oracle['sig1']['signal'])

    # T20 Task
    Time2, Value2 = Source.getSignal(test_oracle['sig2']['device'], test_oracle['sig2']['signal'])

    toc = time.clock()
    
    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print
    
      
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
     
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # Backup directory
    if os.path.exists(os.path.join(local_testdata_dir,'Backup')):                                Test_passed = False
    if not os.path.exists(os.path.join(MyNpyHomeDir,testdata_FileName)):                         Test_passed = False

    
    # report results
    self.assertTrue(Test_passed) 
    print "test_TC002 successful"
    print

  #------------------------------------------------------------------------  
  def test_TC003(self): 
    ''' Signal groups with local backup directory  ''' 

    test_oracle = test_oracle2
  
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir = r'MyNpyHomeDir'
    
    print "test_TC003"
    print
  
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir and MyNpyHomeDir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))

      
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)
      
    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
      
    FullPathFileName = os.path.join(local_testdata_dir, testdata_FileName)
    print "FullPathFileName:" , FullPathFileName
    print

    SignalGroups = [{"sig1_alias": (test_oracle['sig1']['device'], test_oracle['sig1']['signal']),
                     "sig2_alias": (test_oracle['sig2']['device'], test_oracle['sig2']['signal']),
                     "sig3_alias": (test_oracle['sig3']['device'], test_oracle['sig3']['signal'])},]
    
    print "SignalGroups", SignalGroups
    print
    
    tic = time.clock()
    
    Source = measparser.cSignalSource(FullPathFileName, MyNpyHomeDir)
    
    Group = Source.selectSignalGroup(SignalGroups)
     
    # TC Task
    Time1, Value1 = Source.getSignalFromSignalGroup(Group, "sig1_alias") 
    
    # T20 Task
    Time2, Value2 = Source.getSignalFromSignalGroup(Group, "sig2_alias") 

    # Signal from CAN message
    Time3, Value3 = Source.getSignalFromSignalGroup(Group, "sig3_alias") 
    
    toc = time.clock()
    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print

    tic = time.clock()
    # create backup directory
    Source.save()
    toc = time.clock()
    print "Source.save() -> elapsed time: ", toc-tic
    print

    
    # report the results       
    print "test_oracle['sig1']['device']       = %s" % test_oracle['sig1']['device']
    print "test_oracle['sig1']['signal']       = %s" % test_oracle['sig1']['signal']
    print "test_oracle['sig1']['len']          = %d" % len(Time1)
    print "test_oracle['sig1']['idx']          = %d" % test_oracle['sig1']['idx']
    print "test_oracle['sig1']['time_at_idx']  = %10.7e" % Time1[test_oracle['sig1']['idx']]
    print "test_oracle['sig1']['value_at_idx'] = %10.7e" % Value1[test_oracle['sig1']['idx']]
    print
      
    print "test_oracle['sig2']['device']       = %s" % test_oracle['sig2']['device']
    print "test_oracle['sig2']['signal']       = %s" % test_oracle['sig2']['signal']
    print "test_oracle['sig2']['len']          = %d" % len(Time2)
    print "test_oracle['sig2']['idx']          = %d" % test_oracle['sig2']['idx']
    print "test_oracle['sig2']['time_at_idx']  = %10.7e" % Time2[test_oracle['sig2']['idx']]
    print "test_oracle['sig2']['value_at_idx'] = %10.7e" % Value2[test_oracle['sig2']['idx']]
    print

    print "test_oracle['sig3']['device']       = %s" % test_oracle['sig3']['device']
    print "test_oracle['sig3']['signal']       = %s" % test_oracle['sig3']['signal']
    print "test_oracle['sig3']['len']          = %d" % len(Time3)
    print "test_oracle['sig3']['idx']          = %d" % test_oracle['sig3']['idx']
    print "test_oracle['sig3']['time_at_idx']  = %10.7e" % Time3[test_oracle['sig3']['idx']]
    print "test_oracle['sig3']['value_at_idx'] = %10.7e" % Value3[test_oracle['sig3']['idx']]
    print
      
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
     
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # sig3 
    if not len(Time3)  == test_oracle['sig3']['len']:                                            Test_passed = False
    if not len(Value3) == test_oracle['sig3']['len']:                                            Test_passed = False
    if not abs(Time3[test_oracle['sig3']['idx']]  - test_oracle['sig3']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value3[test_oracle['sig3']['idx']] - test_oracle['sig3']['value_at_idx'])<tol:    Test_passed = False

    # Backup directory
    if os.path.exists(os.path.join(local_testdata_dir,'Backup')):                                Test_passed = False
    if not os.path.exists(os.path.join(MyNpyHomeDir,testdata_FileName)):                         Test_passed = False
      
    # report results
    self.assertTrue(Test_passed) 
    print "test_TC003 successful"

  #------------------------------------------------------------------------  
  def test_TC004(self): 
    ''' Signal groups with no availabe CAN signals , local backup directory  ''' 
    
    ''' trx_range will only be send if track is available
        in test data measurement only tr0_range to tr4_range are transmitted on CAN
        
        len(tr0_range)       = 750
        len(tr1_range)       = 472
        len(tr2_range)       = 244
        len(tr3_range)       = 179
        len(tr4_range)       = 158
    '''

    expected_track_length = { 0: 750, 1: 472, 2: 244, 3: 179, 4: 158, 
                              5: 0, 6: 0, 7:0, 8:0, 9:0}
    
    #test_oracle = test_oracle2
  
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir = r'MyNpyHomeDir'
    
    print "test_TC004"
    print
  
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir and MyNpyHomeDir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))

      
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)
      
    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
      
    FullPathFileName = os.path.join(local_testdata_dir, testdata_FileName)
    print "FullPathFileName:" , FullPathFileName
    print

    SignalGroups1 = [{"tr0_range": ("Tracks", "tr0_range"),
                      "tr1_range": ("Tracks", "tr1_range"),
                      "tr2_range": ("Tracks", "tr2_range"),
                      "tr3_range": ("Tracks", "tr3_range"),
                      "tr4_range": ("Tracks", "tr4_range"),
                      "tr5_range": ("Tracks", "tr5_range"),
                      "tr6_range": ("Tracks", "tr6_range"),
                      "tr7_range": ("Tracks", "tr7_range"),
                      "tr8_range": ("Tracks", "tr8_range"),
                      "tr9_range": ("Tracks", "tr9_range"),
                    },]
                    
    SignalGroups2 = [{"tr0_range": ("Tracks", "tr0_range"),
                      "tr1_range": ("Tracks", "tr1_range"),
                      "tr2_range": ("Tracks", "tr2_range"),
                      "tr3_range": ("Tracks", "tr3_range"),
                      "tr4_range": ("Tracks", "tr4_range"),
                    },]
  
    if 1:
      # this is currently not working
      SignalGroups = SignalGroups1
      max_N_tracks = 10
    else:
      # this is working
      SignalGroups = SignalGroups2
      max_N_tracks = 5
    
    
                    
    '''
    SignalGroups = [{"sig1_alias": (test_oracle['sig1']['device'], test_oracle['sig1']['signal']),
                     "sig2_alias": (test_oracle['sig2']['device'], test_oracle['sig2']['signal']),
                     "sig3_alias": (test_oracle['sig3']['device'], test_oracle['sig3']['signal'])},]
    '''
    
    
    print "SignalGroups", SignalGroups
    print
    
    tic = time.clock()
    
    Source = measparser.cSignalSource(FullPathFileName, MyNpyHomeDir)
    
    #Group = Source.selectSignalGroup(SignalGroups)
    #Group = Source.filterSignalGroups(SignalGroups)
    Group = Source.selectFilteredSignalGroup(SignalGroups)
    print "Group", Group
    
    
    Time = {}
    Value = {}
    for k in xrange(max_N_tracks):
      try:
        Time[k], Value[k] = Source.getSignalFromSignalGroup(Group, "tr%d_range"%k) 
      except:
        Time[k]  = np.array([])
        Value[k] = np.array([])
      
    toc = time.clock()
    print "2 signals read from SignalSource -> elapsed time: ", toc-tic
    print

    tic = time.clock()
    # create backup directory
    Source.save()
    toc = time.clock()
    print "Source.save() -> elapsed time: ", toc-tic
    print

    
    # report the results       
    for k in xrange(max_N_tracks):
      print "len(tr%d_range)       = %d" % (k,len(Time[k]))
      
    
    # --------------------------------------------------------------------------------------
    # step3: check results
    Test_passed = True
    tol = 1e-6
    
    for k in xrange(max_N_tracks):
      if not len(Time[k])  == expected_track_length[k]:        Test_passed = False
    
    ''' 
    # sig1
    if not len(Time1)  == test_oracle['sig1']['len']:                                            Test_passed = False
    if not len(Value1) == test_oracle['sig1']['len']:                                            Test_passed = False
    if not abs(Time1[test_oracle['sig1']['idx']]  - test_oracle['sig1']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value1[test_oracle['sig1']['idx']] - test_oracle['sig1']['value_at_idx'])<tol:    Test_passed = False

    # sig2 
    if not len(Time2)  == test_oracle['sig2']['len']:                                            Test_passed = False
    if not len(Value2) == test_oracle['sig2']['len']:                                            Test_passed = False
    if not abs(Time2[test_oracle['sig2']['idx']]  - test_oracle['sig2']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value2[test_oracle['sig2']['idx']] - test_oracle['sig2']['value_at_idx'])<tol:    Test_passed = False
      
    # sig3 
    if not len(Time3)  == test_oracle['sig3']['len']:                                            Test_passed = False
    if not len(Value3) == test_oracle['sig3']['len']:                                            Test_passed = False
    if not abs(Time3[test_oracle['sig3']['idx']]  - test_oracle['sig3']['time_at_idx'])<tol:     Test_passed = False
    if not abs(Value3[test_oracle['sig3']['idx']] - test_oracle['sig3']['value_at_idx'])<tol:    Test_passed = False

    '''
    
    # Backup directory
    if os.path.exists(os.path.join(local_testdata_dir,'Backup')):                                Test_passed = False
    if not os.path.exists(os.path.join(MyNpyHomeDir,testdata_FileName)):                         Test_passed = False
      
    # report results
    self.assertTrue(Test_passed) 
    print "test_TC003 successful"

    
      
      
      

#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for SignalSource'
  
  # run unittest
  unittest.main()
  
  



  
