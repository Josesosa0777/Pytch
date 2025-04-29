"""
  
  Test case for CalcAEBS

  Ulrich Guecker 2012-02-27
  
  test_TC001 .. 06   : cpr_CalcaAvoidancePredictedModelbased.m, CalcPredictedValuesBrakeDelay.m, cpr_CalcaAvoidance.m  
  test_TC011 .. 18   : dso_CalcaAvoidance.m
  test_TC021 .. 24   : ctc_CalcTtc.m
  test_TC025 .. 26   : CalcPredictedObjectMotion, cpr_CalcaAvoidancePredictedCascade_SingleStep, cpr_CalcaAvoidancePredictedCascade
  
  Test
"""


import unittest
import os

import numpy as np

import kbtools
import kbtools_user




#========================================================================================
class cTestCalcAEBS(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self):
      ''' topic:            cCalcAEBS.length
          expected results: correct length
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      # int 
      if not 1  == kbtools_user.cCalcAEBS.length(0):                               Test_passed = False

      # float 
      if not 1  == kbtools_user.cCalcAEBS.length(0.0):                             Test_passed = False

      # array 
      if not 6  == kbtools_user.cCalcAEBS.length(np.array([30,29,28,27,26,25])):   Test_passed = False
      
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC002(self):
      ''' topic:            cCalcAEBS.CalcPredictedValuesBrakeDelay
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test CalcPredictedValuesBrakeDelay()"
    
      # input
      pub = {}
      pub['l_vEgo_f']         = 20.0
      pub['l_aEgo_f']         = 0.0
      pub['l_dxvObstacle_f']  = 100.0
      pub['l_vRelObstacle_f'] = -pub['l_vEgo_f'] 
      pub['l_aRelObstacle_f'] = 0.0
      pub['l_vObstacle_f']    = pub['l_vEgo_f'] + pub['l_vRelObstacle_f']   # absolute (relative to ground)
      pub['l_aObstacle_f']    = pub['l_aEgo_f'] + pub['l_aRelObstacle_f']   # absolute (relative to ground)
    
        
      t_aTarget_f = 0.0
      t_aGradient_f = -10.0
      t_predict_f = 1.0
            
 
      pub,t_predict_f = myCalcAEBS.CalcPredictedValuesBrakeDelay(pub,t_aTarget_f,t_aGradient_f,t_predict_f)

      # output:
      print "vEgoPredicted",         pub['l_vEgoPredicted_f']
      print "aEgoPredicted",         pub['l_aEgoPredicted_f']
      print "dxvObstaclePredicted",  pub['l_dxvObstaclePredicted_f']
      print "vRelObstaclePredicted", pub['l_vRelObstaclePredicted_f'] 
      print "aRelObstaclePredicted", pub['l_aRelObstaclePredicted_f']
      print "t_predict_f",           t_predict_f

  
      if not  20.0  == pub['l_vEgoPredicted_f']:          Test_passed = False
      if not   0.0  == pub['l_aEgoPredicted_f']:          Test_passed = False
      if not  80.0  == pub['l_dxvObstaclePredicted_f']:   Test_passed = False
      if not -20.0  == pub['l_vRelObstaclePredicted_f']:  Test_passed = False 
      if not   0.0  == pub['l_aRelObstaclePredicted_f']:  Test_passed = False
      if not   0.0  == t_predict_f:                       Test_passed = False
      
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #=========================================================================
  def test_TC003_cpr_CalcaAvoidance_SingleStep(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidance_SingleStep
          expected results: 
      '''

      print "==================================================================="
      print "test cpr_CalcaAvoidance_SingleStep()"
      
      #---------------------------------------------------------------------------------------------        
      #               ego        |  obstacle          |  parameter |  expected results
      #               vx     ax  |  dx    vRel   aRel | 'dx secure', 'aAvoidance' 'Situation' 'UndefinedaAvoidDueToWrongdxSecure'
      par_list = [ [ 20.24, -3.0, 64.88, -20.24,  3.0,     2.5,        -3.28,           3,            0],
                   [ 15.71, -3.0, 25.27,  -3.53, 1.79,     2.5,        -1.47,           1,            0], 
                   [ 14.50, -3.0, 11.96, -12.15, 0.26,     2.5,       -10.04,           1,            0],
                   [ 14.50, -3.0, 12.54, -10.31, 3.05,     2.5,        -5.24,           3,            0]
                 ]

      Test_passed = True
      for par in par_list:
        if not self.abstract_cpr_CalcaAvoidance_SingleStep(par):
          Test_passed = False
         
      self.assertTrue(Test_passed)
  #-------------------------------------------------------------------------------------  
  def abstract_cpr_CalcaAvoidance_SingleStep(self, test_par):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidance_SingleStep
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "  abstract_cpr_CalcaAvoidance_SingleStep()"
         
      # ego vehicle 
      ego ={}
      ego['vx']   = test_par[0]
      ego['ax']   = test_par[1] 

      # obstacle
      obs = {}
      obs['dx']   = test_par[2]
      obs['vRel'] = test_par[3]    # stationary obstacle
      obs['aRel'] = test_par[4]

      # final safety distance to obstacle
      dxSecure    = test_par[5]
      
      # expected results
      aAvoidance_expected                        = test_par[6]
      Situation_expected                         = test_par[7]
      UndefinedaAvoidDueToWrongdxSecure_expected = test_par[8]
      
      
      print "  ego['vx']", ego["vx"]
      print "  ego['ax']", ego["ax"]
      print "  obs['dx']", obs["dx"]
      print "  obs['vRel']", obs["vRel"]
      print "  obs['aRel']", obs["aRel"]
      print "  dxSecure", dxSecure
      
      

      # method to test
      aAvoidance,Situation,UndefinedaAvoidDueToWrongdxSecure = myCalcAEBS.cpr_CalcaAvoidance_SingleStep(ego, obs, dxSecure)
 
      # results
      print "    aAvoidance %3.2f (expected: %3.2f)"%(aAvoidance, aAvoidance_expected)
      print "    Situation  %d    (expected: %d)"%(Situation, Situation_expected)
      print "    UndefinedaAvoidDueToWrongdxSecure %d (expected: %d)"%(UndefinedaAvoidDueToWrongdxSecure,UndefinedaAvoidDueToWrongdxSecure_expected)

      
      if not abs(aAvoidance_expected - aAvoidance) < 0.01:  Test_passed = False
      if not Situation_expected  == Situation: Test_passed = False
      if not UndefinedaAvoidDueToWrongdxSecure_expected == UndefinedaAvoidDueToWrongdxSecure:   Test_passed = False
      
      print "      Test_passed", Test_passed
      print "\n"
      # -----------------------------      
      # report results
      return Test_passed

  #------------------------------------------------------------------------  
  def test_TC004(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidance
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test cpr_CalcaAvoidance()"
  
      # ego vehicle
      ego ={}
      ego['vx']   = 50/3.6 
      ego['ax']   =  0;

      # obstacle
      obs = {}
      obs['dx']   = np.array([30,29,28,27,26,25])
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0;

      # final safety distance to obstacle
      dxSecure =2.5

      # method to test
      aAvoidance,Situation,UndefinedaAvoidDueToWrongdxSecure = myCalcAEBS.cpr_CalcaAvoidance(ego, obs, dxSecure)
  
      # results
      print "aAvoidance", aAvoidance
      print "Situation", Situation
      print "UndefinedaAvoidDueToWrongdxSecure", UndefinedaAvoidDueToWrongdxSecure

  
      
      if not abs(-3.50729517396 - aAvoidance[0]) < 0.001:  Test_passed = False
      if not 3  == Situation[0]:                           Test_passed = False
      if not 0  == UndefinedaAvoidDueToWrongdxSecure[0]:   Test_passed = False
      
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
     
      
  #------------------------------------------------------------------------  
  def test_TC005(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidancePredictedModelbased_SingleStep
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test cpr_CalcaAvoidancePredictedModelbased_SingleStep()"

      # ego vehicle
      ego ={}
      ego['vx']   = 60/3.6
      ego['ax']   =  0;

      # obstacle
      obs = {}
      obs['dx']   = 50.0
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0;

      # parameters
      par = {}
      par['dxSecure']             = 2.5  # final safety distance to obstacle
      par['tWarn']                = 0.8
      par['tPrediction']          = 1.2
      par['P_aStdPartialBraking'] = -3.0
      par['P_aEmergencyBrake']    = -5.0
      par['P_aGradientBrake']     = -10.0
  
      # test methods
      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict,internal = myCalcAEBS.cpr_CalcaAvoidancePredictedModelbased_SingleStep(ego, obs, par)
    
      print "aAvoidancePredicted", aAvoidancePredicted
      print "Situation", Situation
      print "CollisionOccuredTillTPredict", CollisionOccuredTillTPredict
      
      if not abs(-6.12474224635 - aAvoidancePredicted) < 0.001:  Test_passed = False
      if not 3  == Situation:                                    Test_passed = False
      if not 0  == CollisionOccuredTillTPredict:                 Test_passed = False
      
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
      
  #------------------------------------------------------------------------  
  def test_TC006(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidancePredictedModelbased
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test cpr_CalcaAvoidancePredictedModelbased()"

      ego ={}
      ego['vx']   = 50/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = np.array([50,49,48,47,46,45])
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0.0;

      dxSecure = 2.5   # final safety distance to obstacle (can be also a vector)

      # parameters
      par = {}
      par['tWarn']                = 0.8
      par['tPrediction']          = 1.2
      par['P_aStdPartialBraking'] = -3.0
      par['P_aEmergencyBrake']    = -5.5
      par['P_aGradientBrake']     = -10.0
  
      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedModelbased(ego, obs, dxSecure, par)
  
      print "aAvoidancePredicted", aAvoidancePredicted
      print "Situation", Situation
      print "CollisionOccuredTillTPredict", CollisionOccuredTillTPredict
 
      
      if not abs(-2.48727688 - aAvoidancePredicted[0]) < 0.001:  Test_passed = False
      if not 3  == Situation[0]:                                 Test_passed = False
      if not 0  == CollisionOccuredTillTPredict[0]:              Test_passed = False
      
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC011(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidance - MOVING
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidance MOVING"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = np.array([50,40,30,20,10,5])
      obs['dy']   =  1.0
      obs['vRel'] =  -ego['vx'];
      obs['vy']   = 0.0
      obs['aRel'] =  0.0;
    
      NOT_CLASSIFIED = 0
      MOVING         = 1
      STOPPED        = 2
      STATIONARY     = 3

      
      obs['MotionClassification'] = MOVING

    
      t_dyminComfortSwingOutMO_f = 2.5
      t_dyminComfortSwingOutSO_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidance(ego, obs,  t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f)
    
      print "out ", out
     
      # expected results
      out_ER =  {'l_DSOayReqComfortSwingOutLeft_f': np.array([  0.23148148,   0.36168981,   0.64300412,   1.44675926,  5.78703704,  16.        ]), 
                 'l_ComfortSwingOutLeftPhysicallyPossible_b': np.array([ 1.,  1.,  1.,  1.,  1.,  1.]), 
                 'l_DSOayReqComfortSwingOutRight_f': np.array([ -0.23148148,  -0.36168981,  -0.64300412,  -1.44675926, -5.78703704, -16.        ]), 
                 'l_ComfortSwingOutRightPhysicallyPossible_b': np.array([ 1.,  1.,  1.,  1.,  1.,  1.])}
      
      for key in out.keys():
        if not (abs(out_ER[key] - out[key]) < 0.001).all():  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
     


      
  #------------------------------------------------------------------------  
  def test_TC012(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidance - STATIONARY
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidance STATIONARY"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = np.array([50,40,30,20,10,5])
      obs['dy']   =  1.0
      obs['vRel'] =  -ego['vx'];
      obs['vy']   = 0.0
      obs['aRel'] =  0.0;
    
      NOT_CLASSIFIED = 0
      MOVING         = 1
      STOPPED        = 2
      STATIONARY     = 3

      
      obs['MotionClassification'] = STATIONARY

    
      t_dyminComfortSwingOutMO_f = 2.5
      t_dyminComfortSwingOutSO_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidance(ego, obs,  t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f)
    
      print "out ", out
     
      # expected results
      out_ER =  {'l_DSOayReqComfortSwingOutLeft_f': np.array([  0.5412601 , 0.84672121,   1.50914629,   3.42066787,  14.25127854, -16.  ]), 
                 'l_ComfortSwingOutLeftPhysicallyPossible_b': np.array([ 1.,  1.,  1.,  1.,  1.,  0.]), 
                 'l_DSOayReqComfortSwingOutRight_f': np.array([ -0.5412601 , -0.84672121,  -1.50914629,  -3.42066787, -14.25127854, -16. ]), 
                 'l_ComfortSwingOutRightPhysicallyPossible_b': np.array([ 1.,  1.,  1.,  1.,  1.,  1.])}
      
      for key in out.keys():
        if not (abs(out_ER[key] - out[key]) < 0.001).all():  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
     
  
      
  #------------------------------------------------------------------------  
  def test_TC013(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidance_SingleStep - MOVING
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidance_SingleStep - MOVING"
      ego ={}
      ego['vx']   = 80.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = 40.0
      obs['dy']   =  1.0
      obs['vRel'] =  -ego['vx'];
      obs['vy']   = 0.0
      obs['aRel'] =  0.0;
    
      NOT_CLASSIFIED = 0
      MOVING         = 1
      STOPPED        = 2
      STATIONARY     = 3

      
      obs['MotionClassification'] = MOVING

    
      t_dyminComfortSwingOutMO_f = 2.5
      t_dyminComfortSwingOutSO_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidance_SingleStep(ego, obs,  t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f)
    
      print "out ", out
     
      # expected results
      out_ER =  {'l_DSOayReqComfortSwingOutLeft_f': 0.92592592592592582, 
                 'l_ComfortSwingOutLeftPhysicallyPossible_b': 1, 
                 'l_DSOayReqComfortSwingOutRight_f': -0.92592592592592582, 
                 'l_ComfortSwingOutRightPhysicallyPossible_b': 1}
      
      for key in out.keys():
        if not abs(out_ER[key] - out[key]) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
     
  #------------------------------------------------------------------------  
  def test_TC014(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidance_SingleStep - STATIONARY
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidance_SingleStep - STATIONARY"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = 40.0
      obs['dy']   =  1.0
      obs['vRel'] =  -ego['vx'];
      obs['vy']   = 0.0
      obs['aRel'] =  0.0;
    
      NOT_CLASSIFIED = 0
      MOVING         = 1
      STOPPED        = 2
      STATIONARY     = 3

      
      obs['MotionClassification'] = STATIONARY

    
      t_dyminComfortSwingOutMO_f = 2.5
      t_dyminComfortSwingOutSO_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidance_SingleStep(ego, obs,  t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f)
    
      print "out ", out
     
      # expected results
      out_ER =  {'l_DSOayReqComfortSwingOutLeft_f': 0.84672120518909455, 
                 'l_ComfortSwingOutLeftPhysicallyPossible_b': 1, 
                 'l_DSOayReqComfortSwingOutRight_f': -0.84672120518909455, 
                 'l_ComfortSwingOutRightPhysicallyPossible_b': 1}
      
      for key in out.keys():
        if not abs(out_ER[key] - out[key]) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
     
      
  #------------------------------------------------------------------------  
  def test_TC015(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidanceMOParable
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidanceMOParable"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = 40.0
      obs['dy']   =  1.0
      obs['vRel'] =  -ego['vx'];
      obs['vy']   = 0.0
      obs['aRel'] =  0.0;

    
      t_dyminComfortSwingOut_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidanceMOParable(ego, obs, t_dyminComfortSwingOut_f)
    
      print "out ", out
     
      # expected results
      out_ER =  {'l_DSOayReqComfortSwingOutLeft_f'           : 0.36168981481481483, 
                 'l_ComfortSwingOutLeftPhysicallyPossible_b' : 1, 
                 'l_DSOayReqComfortSwingOutRight_f'          : -0.36168981481481483, 
                 'l_ComfortSwingOutRightPhysicallyPossible_b': 1}
      
      for key in out.keys():
        if not abs(out_ER[key] - out[key]) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC016(self):
      ''' topic:            cCalcAEBS.dso_CalcaAvoidanceSOCircle
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_CalcaAvoidanceSOCircle"
      ego ={}
      ego['vx']   = 50.0/3.6
    

      obs = {}
      obs['dx']   = 50.0
      obs['dy']   =  1.0
    
      t_dminComfortSwingOut_f = 2.5
  
      out = myCalcAEBS.dso_CalcaAvoidanceSOCircle(ego, obs, t_dminComfortSwingOut_f)
    
      print "out ", out

      # expected results
      out_ER = {'l_DSOayReqComfortSwingOutLeft_f'           : 0.54126010300643701,
                'l_ComfortSwingOutLeftPhysicallyPossible_b' : 1, 
                'l_DSOayReqComfortSwingOutRight_f'          : -0.54126010300643701, 
                'l_ComfortSwingOutRightPhysicallyPossible_b': 1}
      
      for key in out.keys():
        if not abs(out_ER[key] - out[key]) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
      

  #------------------------------------------------------------------------  
  def test_TC017(self):
      ''' topic:            cCalcAEBS.dso_calcIfLeftSOPhysicallyPossible_B
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_calcIfLeftSOPhysicallyPossible_B"
      t_dxvObstacle_f = 50.0
      t_dyvObstacle_f = 1.0
      t_dyminSwingOut_f = 1.0
  
      t_LeftSOPossible_b = myCalcAEBS.dso_calcIfLeftSOPhysicallyPossible_B( t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f)
    
      print "t_LeftSOPossible_b ", t_LeftSOPossible_b
     
      if not abs(1 - t_LeftSOPossible_b) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC018(self):
      ''' topic:            cCalcAEBS.dso_calcIfRightSOPhysicallyPossible_B
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test dso_calcIfRightSOPhysicallyPossible_B"
      t_dxvObstacle_f = 50.0
      t_dyvObstacle_f = 1.0
      t_dyminSwingOut_f = 1.0
  
      t_RightSOPossible_b = myCalcAEBS.dso_calcIfRightSOPhysicallyPossible_B( t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f)
    
      print "t_RightSOPossible_b ", t_RightSOPossible_b
     
      if not abs(1 - t_RightSOPossible_b) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

   
  #------------------------------------------------------------------------  
  def test_TC021(self):
      ''' topic:            cCalcAEBS.ctc_CalcTtc
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test ctc_CalcTtc"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = np.array([50,49,48,47,46,45])
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0.0;
  
      t_ttc_f = myCalcAEBS.ctc_CalcTtc(ego, obs)
    
      print "ttc ", t_ttc_f
     
      if not (abs(np.array([ 3.6, 3.528, 3.456, 3.384, 3.312,  3.24 ]) - t_ttc_f) < 0.001).all():  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
   

  #------------------------------------------------------------------------  
  def test_TC022(self):
      ''' topic:            cCalcAEBS.ctc_CalcTtc_single_step
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test ctc_CalcTtc_single_step"
      ego ={}
      ego['vx']   = 50.0/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = 40.0
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0.0;
  
      t_ttc_f = myCalcAEBS.ctc_CalcTtc_single_step(ego, obs)
    
      print "ttc ", t_ttc_f
     
      if not abs(2.88 - t_ttc_f) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC023(self):
      ''' topic:            cCalcAEBS.SolveEquation
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test SolveEquation"
 
      t_a_f = -3.0
      t_v_f = 21.0
      t_d_f = 30.0
    
      t_ttc_f = myCalcAEBS.SolveEquation(t_a_f, t_v_f, t_d_f)
   
      print "t_ttc_f ", t_ttc_f
     
      if not abs(15.3066238629 - t_ttc_f) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 
      
  #------------------------------------------------------------------------  
  def test_TC024(self):
      ''' topic:            cCalcAEBS.CalcTStop
          expected results: 
      '''
      
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test CalcTStop"

      t_vabs_f = 21.0
      t_aabs_f = -3.0
  
      t_tStop_f = myCalcAEBS.CalcTStop(t_aabs_f, t_vabs_f)
   
      print "tStop", t_tStop_f
    
      if not abs(7.0 - t_tStop_f) < 0.001:  Test_passed = False
     
      # -----------------------------      
      # report results
      self.assertTrue(Test_passed) 

  #=========================================================================
  def test_TC025_CalcPredictedObjectMotion(self):
      ''' topic:            cCalcAEBS.CalcPredictedObjectMotion
          expected results: 
      '''

      
      print "==================================================================="
      print "test CalcPredictedObjectMotion()"
                      
      # --------------------------------------------------------------------------------------------------------
      #               ego              |  obstacle              |
      #               'vx'       'ax'   'dx'     'vx'      'ax'  't_tPredict_f' 't_axvPredictEnd_f' 't_aDtVeh_f'      
      par_list = [ 
             [ 80.0/3.6,   0.0,   100.0,     0.0,    0.0,      0.6,            0.0,             0.0],
             [ 80.0/3.6,   0.0,    86.67,    0.0,    0.0,      0.35,           0.0,             0.0],
             [ 80.0/3.6,  -3.0,    78.89,    0.0,    0.0,  0.8-0.35,          -3.0,             0.0],
             [    20.87,  -3.0,    69.19,    0.0,    0.0,      0.21,          -3.0,             0.0],
             #  [ 20.24       ,-3.0          , 64.87345,  -20.24,       3.0,  ] 
             
             
             [    18.54,  -0.9,    32.32,  14.13,  -1.21,      0.6,            0.0,             0.0],
             [    18.0,   -0.9,    29.62,  13.40,  -1.21,      0.35,           0.0,             0.0],
             [    17.685, -3.0,    27.99,  12.97,  -1.21,   0.8-0.35,         -3.0,             0.0],
             [    16.335, -3.0,    26.05,  12.43,  -1.21,      0.21,         -3.0,             0.0],
             #  [ 15.705       ,-3.0          , 25.269,  -3.5291,       1.79,  ] 
             
             [    16.69, -0.22  , 31.85 , 16.69-12.57421875, -0.22+0.26611328125, 0.6,            0.0,             0.0],
             [    16.558,-0.22  , 24.35 , 4.14,              0.04611328125,  0.35, 0.0,0.0],
             [    16.481,-3.0  , 20.02 , 4.16,              0.04611328125, 0.8-0.35,          -3.0,             0.0],
             [    15.131,-3.0  , 14.78 , 4.18,  0.04611328125, 0.21,         -3.0,             0.0],
             #[    14.501, -3.0, 12.5474567979,  -10.3113162109, 3.04611328125, 0]

           ] 

                 

      Test_passed = True
      for par in par_list:
        if not self.abstract_CalcPredictedObjectMotion(par):
          Test_passed = False
         
      self.assertTrue(Test_passed)
  #-------------------------------------------------------------------------------------  
  def abstract_CalcPredictedObjectMotion(self, test_par):
      ''' topic:            cCalcAEBS.CalcPredictedObjectMotion
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "  abstract CalcPredictedObjectMotion()"

      
      
      # ego vehicle
      ego ={}
      ego['vx']         = test_par[0]
      ego['ax']         = test_par[1]

      # obstacle
      obs = {}
      obs['dx']         = test_par[2]
      obs['vx']         = test_par[3]
      obs['ax']         = test_par[4]
      
      # parameter
      t_tPredict_f      = test_par[5]
      t_axvPredictEnd_f = test_par[6]
      t_aDtVeh_f        = test_par[7]
      
      
      
      # test oracle
      obs['vRel'] =  obs['vx'] - ego['vx']
      obs['aRel'] =  obs['ax'] - ego['ax']
      
      
      t = t_tPredict_f
      ego_p =  {}
      
      ego_p['ax'] =     ego['ax']
      ego_p['vx'] =     ego['ax']*t    + ego['vx']
      ego_p['sx'] = 0.5*ego['ax']*t**2 + ego['vx']*t
      
      obs_a = obs['aRel'] + ego['ax']
      obs_v = obs['vRel'] + ego['vx']
      obs_s = obs['dx'] 
      
      obs_p = {}
      obs_p['ax'] =     obs_a
      obs_p['vx'] =     obs_a*t    + obs_v
      obs_p['sx'] = 0.5*obs_a*t**2 + obs_v*t + obs_s
      
      obs_p['aRel'] = obs_p['ax']- ego_p['ax']
      obs_p['vRel'] = obs_p['vx']- ego_p['vx']
      obs_p['dx']   = obs_p['sx']- ego_p['sx']
      
      
      print "  ego['vx']", ego["vx"]
      print "  ego['ax']", ego["ax"]
      
      print "  obs['dx']", obs["dx"]
      print "  obs['vx']", obs["vRel"]+ego["vx"]
      print "  obs['ax']", obs["aRel"]+ego["ax"]
      print "  obs['vRel']", obs["vRel"]
      print "  obs['aRel']", obs["aRel"]
      
   
      
      # test methods
      t_tRemain_f = myCalcAEBS.CalcPredictedObjectMotion(ego, obs, t_tPredict_f,t_axvPredictEnd_f,t_aDtVeh_f)
    
       
      print "  t_tRemain_f", t_tRemain_f
      print "  ego['vx']", ego["vx"], ego_p['vx']
      print "  ego['ax']", ego["ax"], ego_p['ax']
      
      print "  obs['dx']", obs["dx"], obs_p['dx']
      print "  obs['vx']", obs["vRel"]+ego["vx"]
      print "  obs['ax']", obs["aRel"]+ego["ax"]
      print "  obs['vRel']", obs["vRel"], obs_p['vRel']
      print "  obs['aRel']", obs["aRel"], obs_p['aRel']
      
      
      
          
      #if not abs(0.0 - t_tRemain_f) < 0.001:  Test_passed = False
      
      if not abs(ego["vx"] - ego_p['vx']) < 0.001:  Test_passed = False
      if not abs(ego["ax"] - ego_p['ax']) < 0.001:  Test_passed = False
      
      if not abs(obs["dx"] - obs_p['dx']) < 0.001:  Test_passed = False
      if not abs(obs["vRel"] - obs_p['vRel']) < 0.001:  Test_passed = False
      if not abs(obs["aRel"] - obs_p['aRel']) < 0.001:  Test_passed = False
      
      
      # -----------------------------      
      # report results
      print "      Test_passed", Test_passed
      print " "
      return Test_passed

  
  #=========================================================================
  def test_TC026_cpr_CalcaAvoidancePredictedCascade_SingleStep(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidancePredictedCascade_SingleStep
          expected results: 
      '''

      
      print "==================================================================="
      print "test cpr_CalcaAvoidancePredictedCascade_SingleStep()"
      

      #---------------------------------------------------------------------------------------------        
      #               ego        |  obstacle          |  parameter |  expected results
      #               vx     ax  |  dx    vRel   aRel | 'dx secure', 'aAvoidancePredicted' 'Situation' 'CollisionOccuredTillTPredict'
      par_list = [ [ 18.53515625, -0.87646484375, 32.3203125, -4.4140625, -2.11328125,     -3.54, 1, 0],
                   [ 16.69140625, -0.220703125  , 31.859375 ,-12.57421875, 0.26611328125, -5.24, 3,0],
                   [ 80.0/3.6   , 0.0           ,100.0,      -80.0/3.6,      0.0,          -3.2845168184, 3,0] 
                ]

      Test_passed = True
      for par in par_list:
        if not self.abstract_cpr_CalcaAvoidancePredictedCascade_SingleStep(par):
          Test_passed = False
         
      self.assertTrue(Test_passed)
  #-------------------------------------------------------------------------------------  
  def abstract_cpr_CalcaAvoidancePredictedCascade_SingleStep(self, test_par):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidancePredictedCascade_SingleStep
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test cpr_CalcaAvoidancePredictedCascade_SingleStep()"

      # ego vehicle
      ego ={}
      ego['vx']   = test_par[0]
      ego['ax']   = test_par[1]

      # obstacle
      obs = {}
      obs['dx']   =  test_par[2]
      obs['vRel'] =  test_par[3]
      obs['aRel'] =  test_par[4]

      # expected results
      aAvoidancePredicted_expected          = test_par[5]
      Situation_expected                    = test_par[6]
      CollisionOccuredTillTPredict_expected = test_par[7]
      
      
      print "  ego['vx']", ego["vx"]
      print "  ego['ax']", ego["ax"]
      print "  obs['dx']", obs["dx"]
      print "  obs['vRel']", obs["vRel"]
      print "  obs['aRel']", obs["aRel"]
        
    
     
      
      # parameters
      par = {}
      par['dxSecure']             = 2.5   # final safety distance to obstacle
      par['tWarn']                = 0.6   # time between prewarning and first brake intervention
      par['tPartBraking']         = 0.8   # time of partial praking
      par['tBrakeDelay1']         = 0.35  # Delay of the brake system to realize the requested deceleration at first request
      par['tBrakeDelay2']         = 0.21  # Delay of the brake system to realize the requested deceleration at request changes
      par['axvPartialBraking']    = -3.0  # Deceleration by reaction time gain standard
      par['axvFullBraking']       = -5.0  # Deceleration by reaction time gain extenden
      
  
      # test methods
      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedCascade_SingleStep(ego, obs, par)
 
      # results
      print "    aAvoidance %3.2f (expected: %3.2f)"%(aAvoidancePredicted, aAvoidancePredicted_expected)
      print "    Situation  %d    (expected: %d)"%(Situation, Situation_expected)
      print "    CollisionOccuredTillTPredict %d (expected: %d)"%(CollisionOccuredTillTPredict,CollisionOccuredTillTPredict_expected)
 
      
      
      if not abs(aAvoidancePredicted_expected - aAvoidancePredicted) < 0.01:  Test_passed = False
      if not Situation_expected  == Situation:                                    Test_passed = False
      if not CollisionOccuredTillTPredict_expected  == CollisionOccuredTillTPredict:     Test_passed = False
      
      # -----------------------------      
      # report results
      print "      Test_passed", Test_passed
      print " "
      return Test_passed
 
  #------------------------------------------------------------------------  
  def test_TC027_cpr_CalcaAvoidancePredictedCascade(self):
      ''' topic:            cCalcAEBS.cpr_CalcaAvoidancePredictedCascade
          expected results: 
      '''
      Test_passed = True

      myCalcAEBS = kbtools_user.cCalcAEBS()
  
      print "test cpr_CalcaAvoidancePredictedCascade()"

      ego ={}
      ego['vx']   = 50/3.6
      ego['ax']   =  0.0;

      obs = {}
      obs['dx']   = np.array([50,49,48,47,46,45])
      obs['vRel'] =  -ego['vx'];
      obs['aRel'] =  0.0;

      dxSecure = 2.5   # final safety distance to obstacle (can be also a vector)

      # parameters
      par = {}
      par['dxSecure']             = 2.5   # final safety distance to obstacle
      par['tWarn']                = 0.6   # time between prewarning and first brake intervention
      par['tPartBraking']         = 0.8   # time of partial praking
      par['tBrakeDelay1']         = 0.35  # Delay of the brake system to realize the requested deceleration at first request
      par['tBrakeDelay2']         = 0.21  # Delay of the brake system to realize the requested deceleration at request changes
      par['axvPartialBraking']    = -3.0  # Deceleration by reaction time gain standard
      par['axvFullBraking']       = -5.0  # Deceleration by reaction time gain extenden
  
      aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedCascade(ego, obs, dxSecure, par)
  
      print "aAvoidancePredicted", aAvoidancePredicted
      print "Situation", Situation
      print "CollisionOccuredTillTPredict", CollisionOccuredTillTPredict
 
      
      if not abs(-2.48727688 - aAvoidancePredicted[0]) < 0.001:  Test_passed = False
      if not 3  == Situation[0]:                                 Test_passed = False
      if not 0  == CollisionOccuredTillTPredict[0]:              Test_passed = False
      
      # -----------------------------      
      # report results
      print Test_passed
      #self.assertTrue(Test_passed) 

 
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for CalcAEBS'
  unittest.main()
  
  #test1()
  #raw_input("Press Enter to Exit")
  



  
