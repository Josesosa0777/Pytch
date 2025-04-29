import kbtools_user 
import numpy

def calcASFaAvoid(ego, obs, par ):
  """
  ASF: Calculate the necessary emergency decceleration for the given object 
  
  :Parameters:
    ego['vx']   = ego Speed, m/s
    ego['ax']   = ego Acceleration, m/ss
    
    obs['dx']   =  x distance, m
    obs['vRel'] =  relative speed in x direction, m/s
    obs['aRel'] =  relative acceleration in x direction, m/ss
       
    par['tWarn']                =   prewarning time, s
    par['tPrediction']          =   partial braking time, s
    par['P_aStdPartialBraking'] =   partial braking acceleration SIGNED!!!, m/ss
    par['P_aEmergencyBrake']    =   emergency braking acceleration SIGNED!!!, m/ss
    par['P_aGradientBrake']     =   pressure build-up gardient, m/sss
    par['dxSecure']             =   Security distance between the obstacle and the ego vehicle, m
   
  
  :ReturnType: numpy.ndarray
  :Return:
    aAvoidancePredicted : Required deceleration in the emergency braking phase to avoid collision. [m/s^2]
    Situation : classification of valid inputs and the possible dynamic situation
    CollisionOccuredTillTPredict : flag signalling if collision occured till partial braking time
    
  """
  # AEBS ASF
  myCalcAEBS = kbtools_user.cCalcAEBS()
  dxSecure = par['dxSecure']  
  aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = myCalcAEBS.cpr_CalcaAvoidancePredictedModelbased(ego, obs, dxSecure, par)
  aAvoidancePredicted = numpy.where((obs["dx"] == 0.0) & (obs["vRel"] == 0.0), 0.0, aAvoidancePredicted)
  aAvoidancePredicted = numpy.where(aAvoidancePredicted < -10.0, -10.0, aAvoidancePredicted)
  return aAvoidancePredicted,Situation,CollisionOccuredTillTPredict

def calcASF_aYAvoid(ego, obs, par):
  """
  ASF: Calculate the necessary lateral acceleration for the evasive maneouvre 
  
  :Parameters:
    ego['vx']   = ego Speed, m/s
    ego['ax']   = ego Acceleration, m/ss
    
    obs['dx']   =  x distance, m
    obs['vRel'] =  relative speed in x direction, m/s
    obs['aRel'] =  relative acceleration in x direction, m/ss
    obs['dy']   =  y distance, m
    obs['vy']   =  relative speed in y direction, m/s
    obs['MotionClassification'] = 3 if stationary, 1 if moving
    
    par['dyminComfortSwingOutMO'] = Minimal lateral distance to the obstacle to execute a comfortable swing out for moving obstacles, m
    par['dyminComfortSwingOutSO'] = Minimal lateral distance to the obstacle to execute a comfortable swing out for stationary obstacles, m
    
  
  :ReturnType: dict with numpy.ndarray
  :Return:
    l_DSOayReqComfortSwingOutLeft_f : Required lateral acceleration for the evasion to the left [m/s^2]
    l_DSOayReqComfortSwingOutRight_f : Required lateral acceleration for the evasion to the right [m/s^2]
    l_ComfortSwingOutLeftPhysicallyPossible_b : Determinates if the driving task is physically possible considering the vehicle's clearance circle
    l_ComfortSwingOutRightPhysicallyPossible_b : Determinates if the driving task is physically possible considering the vehicle's clearance circle
    
  """
  # AEBS ASF
  myCalcAEBS = kbtools_user.cCalcAEBS()
  dyminComfortSwingOutMO_f  =   par['dyminComfortSwingOutMO']
  dyminComfortSwingOutSO_f  =   par['dyminComfortSwingOutSO']
  out_ayAvoid = myCalcAEBS.dso_CalcaAvoidance(ego, obs, dyminComfortSwingOutMO_f, dyminComfortSwingOutSO_f)
  
  return out_ayAvoid
  
  
def calcASFActivity(ego, obs, par):
  """
  ASF: Calculates if ASF would give a warning for the given situation
  
  :Parameters:
    ego['vx']   = ego Speed, m/s
    ego['ax']   = ego Acceleration, m/ss
    
    obs['dx']   =  x distance, m
    obs['vRel'] =  relative speed in x direction, m/s
    obs['aRel'] =  relative acceleration in x direction, m/ss
    obs['dy']   =  y distance, m
    obs['vy']   =  relative speed in y direction, m/s
    obs['MotionClassification'] = 3 if stationary, 1 if moving
       
    par['tWarn']                =   prewarning time, s
    par['tPrediction']          =   partial braking time, s
    par['P_aStdPartialBraking'] =   partial braking acceleration SIGNED!!!, m/ss
    par['P_aEmergencyBrake']    =   emergency braking acceleration SIGNED!!!, m/ss
    par['P_aGradientBrake']     =   pressure build-up gardient, m/sss
    par['dxSecure']             =   Security distance between the obstacle and the ego vehicle, m
    par['dyminComfortSwingOutMO'] = Minimal lateral distance to the obstacle to execute a comfortable swing out for moving obstacles, m
    par['dyminComfortSwingOutSO'] = Minimal lateral distance to the obstacle to execute a comfortable swing out for stationary obstacles, m
    par['P_aComfortSwingOut']     = Lateral acceleration threshold for the comfortable swing out
   
  
  :ReturnType: numpy.ndarray
  :Return:
    ASFactivity : ASF AEBS activity flag
    
  """
  
  aAvoidancePredicted,Situation,CollisionOccuredTillTPredict = calcASFaAvoid(ego, obs, par )
  
  out_ayAvoid = calcASF_aYAvoid(ego, obs, par)
  
  a_e_threshold = par['P_aEmergencyBrake']
  
  
  
  ASFactivity = numpy.where( (aAvoidancePredicted <= a_e_threshold) &  
                                             (-out_ayAvoid['l_DSOayReqComfortSwingOutRight_f'] > par['P_aComfortSwingOut'] )  &
                                             ( out_ayAvoid['l_DSOayReqComfortSwingOutLeft_f']  > par['P_aComfortSwingOut'] )  &
                                             (ego['BPact'] == 0 ) &
                                             (ego['GPPos'] < 90.0 ) &
                                             (ego['vx'] > 2.0 )
                                              ,    True, False)
  return ASFactivity
