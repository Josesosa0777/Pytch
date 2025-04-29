'''
   
   cCalcAEBS
   
   class for calculating features to trigger AEBS warning and intervention cascade
   
   Ulrich Guecker  2012-02-23
   

'''

#  COPYRIGHT:
#  Robert Bosch GmbH reserves all rights even in the event of industrial
#  property. We reserve all rights of disposal such as copying and passing
#  on to third parties.


import numpy as np
import math


# ==========================================================================================
class cCalcAEBS():
    # calculate features to trigger AEBS warning and intervention cascade
    
    
    # threshold for detecting oncoming traffic
    threshold_vObstacle_oncoming = -1.0
    
    # ==========================================================================================
    def __init__(self):
        self.dso_init()
        pass
        
    # ==========================================================================================
    @staticmethod
    def length(x):
        # return length of scalar and vector
        # scalar can be float, int or array of length 1
        if isinstance(x,(float,int)):
            return 1        # scalar
        else:
            return len(x)   # vector

    # ==========================================================================================
    def CalcPredictedValuesBrakeDelay(self,pub,t_aTarget_f,t_aGradient_f,t_predict_f):
        # [pub] = CalcPredictedValuesBrakeDelay(pub,t_aTarget_f,t_aGradient_f)
        #
        # assumption: constant acceleration gradient
        #
        # input:
        #   pub['l_vEgo_f']
        #   pub['l_aEgo_f']
        #   pub['l_dxvObstacle_f']
        #   pub['l_vRelObstacle_f']
        #   pub['l_aRelObstacle_f'] 
        #   pub['l_vObstacle_f'] 
        #   pub['l_aObstacle_f']
        #   t_aTarget_f               - absolute acceleration of obstacle
        #   t_aGradient_f             - gradient for building up accelerations
        #   t_predict_f               - prediction horizont
        #
        # output:
        #   pub['l_vEgoPredicted_f'] 
        #   pub['l_aEgoPredicted_f']
        #   pub['l_dxvObstaclePredicted_f']
        #   pub['l_vRelObstaclePredicted_f'] 
        #   pub['l_aRelObstaclePredicted_f']
        #   t_predict_f              - remaining prediction time
      
        # --------------------------------------------------------------------
        # Ego vehicle acceleration will be considered to be constant if
        #    acceleration gradient is given as 0 or positive value
        # OR target acceleration is the same or bigger than current acceleration
        if (   (t_aGradient_f >= 0.0) or (t_aTarget_f >= pub['l_aEgo_f'])  ):
            # Calculate temporary delta values
            t_deltaAego_f = 0.0
            t_deltaArel_f = 0.0

            # Calculate predicted duration of ramp
            t_tDuration_f = t_predict_f

            # Set input values to limits in case they differ
            t_aGradient_f = 0.0
            t_aTarget_f = pub['l_aEgo_f']
        else:
            # Calculate temporary delta values
            t_deltaAego_f = t_aTarget_f - pub['l_aEgo_f']
            t_deltaArel_f = - t_deltaAego_f

            # Calculate predicted duration of ramp
            t_tDuration_f = t_deltaAego_f/t_aGradient_f

            # Check if predicted duration of ramp is bigger than the available
            # prediction time
            if (   (t_tDuration_f > t_predict_f) and (t_predict_f > 0.0) ):
                # Adjust gradient so it won't take longer to ramp than the prediction
                # time
                t_aGradient_f = t_deltaAego_f / t_predict_f
                # Adjust predicted duration of ramp
                t_tDuration_f = t_predict_f
    
        # --------------------------------------------------------------------
        # Ego vehicle calculation
        t_vDiffEgo_f = (0.5 * t_deltaAego_f * t_tDuration_f) + (pub['l_aEgo_f'] * t_tDuration_f)

        t_dxDiffEgo_f = ((  t_deltaAego_f * t_tDuration_f * t_tDuration_f) / 6) + \
                        ((pub['l_aEgo_f'] * t_tDuration_f * t_tDuration_f) / 2) + \
                          pub['l_vEgo_f'] * t_tDuration_f

        # Determination of the predicted ego velocity
        pub['l_vEgoPredicted_f'] = pub['l_vEgo_f'] + t_vDiffEgo_f;
 
        # Determination of the predicted ego acceleration
        pub['l_aEgoPredicted_f'] = pub['l_aEgo_f'] + t_deltaAego_f;

        # Update prediction time
        t_predict_f = np.max(t_predict_f - t_tDuration_f,0);

        # --------------------------------------------------------------------
        # Obstacle/ target vehicle prediction
        # will the obstacle come to a stop before tPredictionTime is over?

        if (pub['l_aObstacle_f'] >= 0.0):
            t_tObstStopped_f = t_tDuration_f + 1  # only has to be greater than t_tDuration_f
        else:
            t_tObstStopped_f = - pub['l_vObstacle_f'] / pub['l_aObstacle_f']


        if (t_tObstStopped_f >= t_tDuration_f ):
            # Calculate changes in target vehicle motion
            t_vDiffObst_f = pub['l_aObstacle_f'] * t_tDuration_f

            t_dxDiffObst_f = 0.5 * pub['l_aObstacle_f'] * t_tDuration_f * t_tDuration_f + \
                                   pub['l_vObstacle_f'] * t_tDuration_f

            # Determination of the predicted relative velocity
            pub['l_vRelObstaclePredicted_f'] = pub['l_vRelObstacle_f'] + t_vDiffObst_f - t_vDiffEgo_f

            # Determination of the predicted relative acceleration
            pub['l_aRelObstaclePredicted_f'] = pub['l_aRelObstacle_f'] + t_deltaArel_f
    
        else:
            # Calculate changes in target vehicle motion
            t_dxDiffObst_f = 0.5 * pub['l_aObstacle_f'] * t_tObstStopped_f * t_tObstStopped_f + \
                                   pub['l_vObstacle_f'] * t_tObstStopped_f

            # Determination of the predicted relative velocity
            pub['l_vRelObstaclePredicted_f'] = - pub['l_vEgoPredicted_f']

            # Determination of the predicted relative acceleration
            pub['l_aRelObstaclePredicted_f'] = - pub['l_aEgoPredicted_f']
    
        # --------------------------------------------------------------------
        # Determination of the predicted longitudinal distance
        pub['l_dxvObstaclePredicted_f'] = pub['l_dxvObstacle_f'] + t_dxDiffObst_f - t_dxDiffEgo_f

        return (pub,t_predict_f)      
            
    # ==========================================================================================
    def cpr_CalcaAvoidance_SingleStep(self, ego, obs, t_dxSecure_f):
        # input: 
        #   ego['vx']    : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']    : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']    : [m]     current distance from ego vehicle to obstacle
        #   obs['vRel']  : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel']  : [m/s^2] current relative acceleration =  0;
        #   t_dxSecure_f : [m]     final safety distance to obstacle
    
        #  COPYRIGHT:
        #  Robert Bosch GmbH reserves all rights even in the event of industrial
        #  property. We reserve all rights of disposal such as copying and passing
        #  on to third parties.

        # Reset of aAvoid status flags to default values
        l_UndefinedaAvoidResult_b                 = 0
        l_UndefinedaAvoidDueToOncomingObstacle_b  = 0
        l_UndefinedaAvoidDueToWrongdxSecure_b     = 0
        
        t_Situation_ub = -1
        
        

        # Get the position, velocity and acceleration of the given obstacle
        # relative to the given ego vehicle
        t_dxvObstacle_f  = obs['dx']
        t_vRelObstacle_f = obs['vRel']
        t_aRelObstacle_f = obs['aRel']

        #  Get the velocity and acceleration of the given ego vehicle
        t_vxvEgo_f = ego['vx']
        t_axvEgo_f = ego['ax']

        # ***********************************************************
        # Start: Internal Determination if obstacle is "oncoming" 
        # *********************************************************** 
        # Determination of absolute obstacle velocity
        # vObstacle = vxvEgo + vRelObstacle
        t_vObstacle_f = t_vxvEgo_f + t_vRelObstacle_f


        # catch if we don't have an obstacle 
        if 0.0 == t_dxvObstacle_f:
            t_aAvoidance_f = 0;  
            t_Situation_ub = -1;
            return (t_aAvoidance_f,t_Situation_ub,l_UndefinedaAvoidDueToWrongdxSecure_b)

        #  absolute obstacle velocity is negativ 
        if t_vObstacle_f < cCalcAEBS.threshold_vObstacle_oncoming:
            # Set internal Determination flag on TRUE
            t_oncomingInternal_b = 1
        else:
            # Set internal Determination flag on FALSE
            t_oncomingInternal_b = 0
  
        # *********************************************************
        # End: Internal Determination if obstacle is "oncoming" 
        # *********************************************************

        # 00548    if(
        # 00549      (t_obs_pc->GetRelMotionDirection() == ONCOMING)
        # 00550      ||
        # 00551      (t_oncomingInternal_b == TRUE)
        # 00552    )

        if t_oncomingInternal_b:
            # Set flag oncoming to TRUE
            t_oncoming_b = 1
        else:
            # Set flag oncoming to FALSE
            t_oncoming_b = 0
            
        
        # -------------------------------------------------------------------------
        # Initialise failure flag to FALSE
        t_Failure_b = 0

        # Determination of absolute obstacle acceleration
        # aObstacle = axvEgo + aRel
        t_aObstacle_f =  t_axvEgo_f + t_aRelObstacle_f

        # Determination of vRelSquareObstacle
        # vRelSquareObstacle = vRelObstacle * vRelObstacle
        t_vRelSquareObstacle_f = t_vRelObstacle_f * t_vRelObstacle_f


        # dxSecure is not plausible
        if t_dxvObstacle_f <= t_dxSecure_f:
            # Set dxSecure to zero to avoid wrong results
            t_dxSecure_f = 0

            # Set status info for interpretation of aAvoid result
            l_UndefinedaAvoidResult_b                 = 1
            l_UndefinedaAvoidDueToWrongdxSecure_b     = 1
       
        # Calculation of distance to obstacle reduced by dxSecure 
        t_dObstReduced_f = t_dxvObstacle_f - t_dxSecure_f

        # -------------------------------------------------------------------------
        # Classification of valid inputs and the possible dynamic situations
        CN_vRelNegaObsNeg_ub = 1
        CN_vRelPosaObsNeg_ub = 2
        CN_vRelNegaObsPos_ub = 3
        CN_vRelPosaObsPos_ub = 4
        CN_InvalidInput_ub   = 5

        # Check if obstacle is not classified as oncoming obstacle
        if not t_oncoming_b:
            # Determination of dynamic situation

            # Relative velocity to obstacle ?
            if t_vRelObstacle_f < 0.0:
                # Relative velocity to obstacle is negative
      
                # Acceleration of obstacle ?
                if t_aObstacle_f < 0.0:
                    # Acceleration of obstacle is negative
                    t_Situation_ub = CN_vRelNegaObsNeg_ub
                else:
                    # Acceleration of obstacle is zeor or positive
                    t_Situation_ub = CN_vRelNegaObsPos_ub
       
            else:  
                # Relative velocity to obstacle is zero or positive
    
                # Acceleration of obstacle ? 
                if t_aObstacle_f < 0.0:
                    # Acceleration of obstacle is negative
                    t_Situation_ub = CN_vRelPosaObsNeg_ub
                else:
                    # Acceleration of obstacle is zero or positive
                    t_Situation_ub = CN_vRelPosaObsPos_ub
    
 
        else:
            # Invalid input values
            t_Situation_ub = CN_InvalidInput_ub

            # Set status info for interpretation of aAvoid result
            l_UndefinedaAvoidResult_b                 = 1
            l_UndefinedaAvoidDueToOncomingObstacle_b  = 1

        # -------------------------------------------------------------------------
        # Calculate the avoidance acceleration in dependency of the situation 
        # classification
        if CN_vRelNegaObsNeg_ub == t_Situation_ub:
            # vRel is negative and aObstacle is negative 
            # ************************************************************************
            # *                                                                      *
            # * formula:                                                             *
            # *           dxvObstacle - dxSecure                                     *
            # * tz = -2 * ----------------------                                     *
            # *              vRelObstacle                                            *
            # *                                                                      *
            # *                   -vObstacle                                         *
            # * tObstacleStop = -------------                                        *
            # *                   aObstacle                                          *
            # *                                                                      *
            # * if tz < tObstacleStop                                                *
            # *                                                                      *
            # *                                     vRelObstacle^2                   *
            # *    aAvoidance = aObstacle - 0.5 * ----------------------             *
            # *                                   dxvObstacle - dxSecure             *
            # *                                                                      *
            # * else                                                                 *
            # *                                                                      *
            # *                                  vxvRef^2                            *
            # *    aAvoidance =  -------------------------------------------         *
            # *                   vObstacle^2                                        *
            # *                   ------------ - 2 * (dxvObstacle - dxSecure)        *
            # *                    aObstacle                                         *
            # *                                                                      *
            # *    (with the need to verify the result)                              *
            # *                                                                      *
            # ************************************************************************

            # Determination of tObstacleStop
            t_tObstacleStop_f = -t_vObstacle_f/t_aObstacle_f
  
            # Determination of tz                                                 
            t_tz_f = -2.0*t_dObstReduced_f/t_vRelObstacle_f
  
            if t_tz_f < t_tObstacleStop_f:
                # tz is smaller than tObstacleStop                                   
                # Determination of aAvoidance  (tz < tObstacleStop )               
                t_aAvoidance_f = t_aObstacle_f - 0.5*t_vRelSquareObstacle_f/t_dObstReduced_f
            else:
                # tz is greater or equal than tObstacleStop
                # Determination of aAvoidance  (tz >= tObstacleStop )
                t_aAvoidance_f = t_vxvEgo_f**2.0/(t_vObstacle_f**2.0/t_aObstacle_f - 2.0 * t_dObstReduced_f)

            # *********************************************************************
            # *                                                                   *          
            # * Verification if result is correct in the following cases:         *
            # *                                                                   *
            # * a.) when aRelObstacletoaAvoidance > 0 and vSquare >= 0            *
            # *                                                                   *
            # *       test if  tSolution2 > tObstacleStop                         *
            # *                                                                   *
            # *                        -vRelObstacle - Sqrt(vSquare)              *
            # *          tSolution2 = ------------------------------              *
            # *                         aRelObstacletoaAvoidance                  *
            # *                                                                   *
            # *                                                                   *
            # * b.) when aRelObstacletoaAvoidance == 0                            *
            # *                                                                   *
            # *       test if  t12 > tObstacleStop                                *
            # *                                                                   *
            # *                   dxvObstacle                                     *
            # *          t12 = -----------------                                  *
            # *                 - vRelObstacle                                    *
            # *                                                                   *
            # *  If cases a and b lare not fullfield calculate aAvoid with:       *
            # *                                                                   *
            # *                                     vRelObstacle^2                *
            # *    aAvoidance = aObstacle - 0.5 * ----------------------          *
            # *                                   dxvObstacle - dxSecure          *
            # *                                                                   *
            # *********************************************************************

            # aRelObstacletoaAvoidance = aObstacle   - aAvoidance
            t_aRelObstacletoaAvoidance_f = t_aObstacle_f - t_aAvoidance_f
    
            # vSquare=vRelSquareObstacle-2*aRelObstacletoaAvoidance*dxvObstacle */
            t_vSquare_f = t_vRelSquareObstacle_f - 2.0*t_aRelObstacletoaAvoidance_f*t_dxvObstacle_f
    
            if t_aRelObstacletoaAvoidance_f == 0.0:
                # Determination of t12
                t_t12_f = - t_dxvObstacle_f / t_vRelObstacle_f
       
                if t_t12_f > t_tObstacleStop_f:
                    # Solution is correct failure flag remains on FALSE
                    pass
                else:
                    # Solution is not correct - Set failure flag to TRUE
                    t_Failure_b = 1
      
    
            if (t_aRelObstacletoaAvoidance_f>0.0) and (t_vSquare_f>=0.0):
                # *             -vRelObstacle - Sqrt(vSquare)   
                # * tSolution2= -----------------------------
                # *              aRelObstacletoaAvoidance
                t_tSolution2_f = (-t_vRelObstacle_f - math.sqrt(t_vSquare_f))/t_aRelObstacletoaAvoidance_f
      
                if t_tSolution2_f > t_tObstacleStop_f:
                    # Solution is correct failure flag remains on FALSE
                    pass
                else:
                    # Solution is not correct - Set failure flag                
                    t_Failure_b = 1
      
            # In case of not successful verification the aAvoid will be
            # calculated as in case CN_vRelNegaObsPos_ub
            if t_Failure_b:
                t_aAvoidance_f = t_aObstacle_f - 0.5 * t_vRelSquareObstacle_f/t_dObstReduced_f
        
        #...................................................................................
        elif CN_vRelPosaObsNeg_ub == t_Situation_ub:    
            # vRel is positive and aObstacle is negative
            # *********************************************************************
            # *                                                                   *
            # * formula:                                                          *
            # *                                  vxvRef^2                         *
            # *    aAvoidance =  -------------------------------------------      *
            # *                   vObstacle^2                                     *
            # *                   ------------ - 2 * (dxvObstacle - dxSecure)     *
            # *                    aObstacle                                      *
            # *                                                                   *
            # *********************************************************************
            t_aAvoidance_f = t_vxvEgo_f**2.0/(t_vObstacle_f**2.0/t_aObstacle_f-2.0*t_dObstReduced_f);
    
        #...................................................................................
        elif CN_vRelNegaObsPos_ub == t_Situation_ub:    
            # vRel is negative and aObstacle is positive
            # *********************************************************************
            # *                                                                   *
            # * formula:                                                          *
            # *                                     vRelObstacle^2                *
            # *    aAvoidance = aObstacle - 0.5 * ----------------------          *
            # *                                   dxvObstacle - dxSecure          *
            # *                                                                   *
            # *********************************************************************
            t_aAvoidance_f = t_aObstacle_f - 0.5 * t_vRelSquareObstacle_f/t_dObstReduced_f;

        #...................................................................................
        elif CN_vRelPosaObsPos_ub == t_Situation_ub:    
            # vRel is positive and aObstacle is positive 
            # ******************************************************************
            # *                                                                *
            # * formula:                                                       *
            # * aAvoidance = 0                                                 *
            # *                                                                *
            # ******************************************************************
            t_aAvoidance_f = 0.0;
  
        #...................................................................................
        else: 
            # CN_InvalidInput_ub
            # Invalid input value
            t_aAvoidance_f = 0.0;

        return (t_aAvoidance_f,t_Situation_ub,l_UndefinedaAvoidDueToWrongdxSecure_b)

    # ==========================================================================================
    def cpr_CalcaAvoidance(self, ego, obs, dxSecure):  
        # calculate required constant acceleration to avoid the collision 
        # based on the sitution given by
        #   ego['vx']   : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']   : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']   : [m]     current distance from ego vehicle to obstacle
        #   obs['vRel'] : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel'] : [m/s^2] current relative acceleration
        #   dxSecure    : [m]     final safety distance to obstacle
  
    
        # get maximal length of input arguments
        N_ego_vx    = cCalcAEBS.length(ego['vx'])
        N_ego_ax    = cCalcAEBS.length(ego['ax'])
        N_obs_dx    = cCalcAEBS.length(obs['dx'])
        N_obs_vRel  = cCalcAEBS.length(obs['vRel'])
        N_obs_aRel  = cCalcAEBS.length(obs['aRel'])
        N_dxSecure  = cCalcAEBS.length(dxSecure)
        N = np.max([N_ego_vx,N_ego_ax,N_obs_dx,N_obs_vRel,N_obs_aRel,N_dxSecure])
     
        # bring input argument to same length     
        if N_ego_vx == 1:
            ego['vx'] = ego['vx']*np.ones(N)
      
        if N_ego_ax == 1:
            ego['ax'] = ego['ax']*np.ones(N)

        if N_obs_dx == 1:
            obs['dx'] = obs['dx']*np.ones(N)

        if N_obs_vRel == 1:
            obs['vRel'] = obs['vRel']*np.ones(N)

        if N_obs_aRel == 1:
            obs['aRel'] = obs['aRel']*np.ones(N)

        if N_dxSecure == 1:
            dxSecure = dxSecure*np.ones(N)

        # output signals
        aAvoidance                        = np.zeros(N)
        Situation                         = np.zeros(N)
        UndefinedaAvoidDueToWrongdxSecure = np.zeros(N)

        # loop over single steps
        for k in xrange(N):
            l_ego = {}
            l_ego['vx']   = ego['vx'][k] 
            l_ego['ax']   = ego['ax'][k] 
      
            l_obs = {}
            l_obs['dx']    = obs['dx'][k]
            l_obs['vRel']  = obs['vRel'][k] 
            l_obs['aRel']  = obs['aRel'][k] 


            l_dxSecure = dxSecure[k]
  
            [t_aAvoidance,t_Situation,l_UndefinedaAvoidDueToWrongdxSecure_b] = self.cpr_CalcaAvoidance_SingleStep(l_ego, l_obs, l_dxSecure);
 
            # register single step values
            aAvoidance[k]                        = t_aAvoidance;
            Situation[k]                         = t_Situation;
            UndefinedaAvoidDueToWrongdxSecure[k] = l_UndefinedaAvoidDueToWrongdxSecure_b
       
        # return results 
        return aAvoidance,Situation,UndefinedaAvoidDueToWrongdxSecure   

    # ==========================================================================================
    def cpr_CalcaAvoidancePredictedModelbased_SingleStep(self, ego, obs, par):
      # [aAvoidancePredicted,Situation,CollisionOccuredTillTPredict,EgoStoppedSafelyDuringTPredict] = ...
      #      cpr_CalcaAvoidancePredictedModelbased_SingleStep(ego, obs, dxSecure,tPrediction,P_aStdPartialBraking,P_aEmergencyBrake,P_aGradientBrake)
      #
      #  Calculates the avoidance acceleration to an object after following a
      #  certain intervention model in dependency of a safety distance and a 
      #  prediction time. 
      #
      #  ego         - ego vehicle state
      #  obs         - obstacle state
      #  par         - parameters
      #    dxSecure    - Distance from the obstacle at which the relative velocity has to be nil
      #    tWarn       - acoustic warning before partial braking
      #    tPrediction          - Prediction time
      #    P_aStdPartialBraking - acceleration partial braking  phase
      #    P_aEmergencyBrake    - acceleration emergency braking phase
      #    P_aGradientBrake     - pressure build up gradient

      # parameters
      t_dxSecure_f         = par['dxSecure']
      t_tWarn_f            = par['tWarn']
      t_tPrediction_f      = par['tPrediction']
      P_aStdPartialBraking = par['P_aStdPartialBraking']
      P_aEmergencyBrake    = par['P_aEmergencyBrake']
      P_aGradientBrake     = par['P_aGradientBrake']
      
      # ----------------------------
      pub = {}
      internal = {}
      
      t_axvEgoLimit_f = 16.0 # SWORD_MAX
      t_Situation_ub = 0


      # Initialisation
      t_aAvoidancePredictedExt_f = 0

      #-------------------------------------------
      # Flags
      
      pub['l_CollisionOccuredTillPredictionTime_b'] = 0
      pub['l_VehiclesStoppedWithoutCollisionTillPredictionTime_b'] = 0

      # Reset of aAvoid status flags to default values 
      pub['l_UndefinedaAvoidResult_b']                 = 0
      pub['l_UndefinedaAvoidDueToOncomingObstacle_b']  = 0
      pub['l_UndefinedaAvoidDueToWrongdxSecure_b']     = 0
 
      # -------------------------------------------
      # predicted values
      pub['l_vEgoPredicted_f']         = 0

      pub['l_vRelObstaclePredicted_f'] = 0
      pub['l_aRelObstaclePredicted_f'] = 0

      pub['l_dxvObstaclePredicted_f']  = 0


      #-------------------------------------------
      # current values
      pub['l_vEgo_f']         = 0
      pub['l_aEgo_f']         = 0

      pub['l_dxvObstacle_f']  = 0
      pub['l_vRelObstacle_f'] = 0
      pub['l_aRelObstacle_f'] = 0

      pub['l_vObstacle_f']    = 0
      pub['l_aObstacle_f']    = 0



      # Mapping of input signals
      pub['l_vEgo_f'] = ego['vx']                # absolute (relative to ground)
      pub['l_aEgo_f'] = ego['ax']                # absolute (relative to ground)

      pub['l_dxvObstacle_f']  = obs['dx']        # relative to EGO
      pub['l_vRelObstacle_f'] = obs['vRel']      # relative to EGO
      pub['l_aRelObstacle_f'] = obs['aRel']      # relative to EGO

      pub['l_vObstacle_f'] = pub['l_vEgo_f'] + pub['l_vRelObstacle_f']   # absolute (relative to ground)
      pub['l_aObstacle_f'] = pub['l_aEgo_f'] + pub['l_aRelObstacle_f']   # absolute (relative to ground)

      # ==========================================================================
      # axvEgoLimit
      # To reduce the false activation rate, the ego-acceleration will be
      # limited in the prediction to maximal aEgoLimit. 
      # Thus the aAvoidance will be smaller in cases where the ego driver is 
      # accelerating.                                                        
      # The obstacle's absolute acceleration is still the real one. But one  
      # consequence of this hypothesis is that the relative acceleration must
      # be corrected by the limitation value of the ego acceleration.
      if pub['l_aEgo_f'] > t_axvEgoLimit_f:
          # The egovelocity is limited and consequently set to axvEgoLimit for 
          # the rest of the prediction.
          pub['l_aEgo_f'] = t_axvEgoLimit_f

          # As a consequence the relative acceleration must be set addapted
          # (aRel = aAbsObs - axvEgoLimit)
          pub['l_aRelObstacle_f'] = pub['l_aObstacle_f'] - t_axvEgoLimit_f;
 
      # ==========================================================================
      # Determination of the predicted aAvoidance to follow object

      # Brake action delay: first stage

      # Phase 1: acoustic warning phase
      #          acceleration: no
      #          duration: t_tWarn_f
      pub,t_tPredictionRemaining_f = self.CalcPredictedValuesBrakeDelay(pub,pub['l_aEgo_f'],0.0,t_tWarn_f)

      pub['l_aEgo_f']         = pub['l_aEgoPredicted_f']
      pub['l_dxvObstacle_f']  = pub['l_dxvObstaclePredicted_f']
      pub['l_vRelObstacle_f'] = pub['l_vRelObstaclePredicted_f']
      pub['l_vEgo_f']         = pub['l_vEgoPredicted_f']
      pub['l_aRelObstacle_f'] = pub['l_aRelObstaclePredicted_f']
      pub['l_vObstacle_f']    = pub['l_vEgo_f'] + pub['l_vRelObstacle_f']
      pub['l_aObstacle_f']    = pub['l_aEgo_f'] + pub['l_aRelObstacle_f']

      # Phase 2: partial braking
      #          acceleration:       P_aStdPartialBraking
      #          built up gradient:  P_aGradientBrake
      #          duration:           t_tPrediction_f
      
      # Phase 2.1: build up
      pub,t_tPredictionRemaining_f = self.CalcPredictedValuesBrakeDelay(pub,P_aStdPartialBraking,P_aGradientBrake,t_tPrediction_f)

      pub['l_aEgo_f']         = pub['l_aEgoPredicted_f']
      pub['l_dxvObstacle_f']  = pub['l_dxvObstaclePredicted_f']
      pub['l_vRelObstacle_f'] = pub['l_vRelObstaclePredicted_f']
      pub['l_vEgo_f']         = pub['l_vEgoPredicted_f']
      pub['l_aRelObstacle_f'] = pub['l_aRelObstaclePredicted_f']
      pub['l_vObstacle_f']    = pub['l_vEgo_f'] + pub['l_vRelObstacle_f']
      pub['l_aObstacle_f']    = pub['l_aEgo_f'] + pub['l_aRelObstacle_f']

      # Phase 2.2: constant acceleration
      pub,t_tPredictionRemaining_f = self.CalcPredictedValuesBrakeDelay(pub,pub['l_aEgo_f'],0,t_tPredictionRemaining_f)


      pub['l_dxvObstacle_f']  = pub['l_dxvObstaclePredicted_f'] 
      pub['l_vRelObstacle_f'] = pub['l_vRelObstaclePredicted_f']
      pub['l_vEgo_f']         = pub['l_vEgoPredicted_f']
      pub['l_aEgo_f']         = pub['l_aEgoPredicted_f']
      pub['l_aRelObstacle_f'] = pub['l_aRelObstaclePredicted_f']
      pub['l_vObstacle_f']    = pub['l_vEgo_f'] + pub['l_vRelObstacle_f']
      pub['l_aObstacle_f']    = pub['l_aEgo_f'] + pub['l_aRelObstacle_f']

      #----------------------------------------------------------------------  
      # report internal variables
      internal['after_level3'] = {}
      internal['after_level3']['time_elapsed']     = t_tWarn_f+t_tPrediction_f
      internal['after_level3']['l_dxvObstacle_f']  = pub['l_dxvObstacle_f']
      internal['after_level3']['l_vRelObstacle_f'] = pub['l_vRelObstacle_f']
      internal['after_level3']['l_vEgo_f']         = pub['l_vEgo_f']
      #----------------------------------------------------------------------  
        
      # Phase 3: emergency braking
      #          acceleration:       P_aEmergencyBrake
      #          built up gradient:  P_aGradientBrake
      #          duration:           ?
      pub,t_tPredictionRemaining_f = self.CalcPredictedValuesBrakeDelay(pub,P_aEmergencyBrake,P_aGradientBrake,0);

      pub['l_aEgo_f'] = pub['l_aEgoPredicted_f']

      # Determination of the predicted avoidance velocity
      # Calculation of aAvoidance based on virtual data   

      # virtual ego vehicle  
      t_virtego ={}
      t_virtego['vx'] = pub['l_vEgoPredicted_f']
      t_virtego['ax'] = pub['l_aEgo_f']

      # virtual obstacle
      t_virtobs = {}
      t_virtobs['dx']   = pub['l_dxvObstaclePredicted_f']
      t_virtobs['vRel'] = pub['l_vRelObstaclePredicted_f']
      t_virtobs['aRel'] = pub['l_aRelObstaclePredicted_f']

      # Calculation of aAvoidance based on t_dxSecure_sw
      # Stufe 5

      if t_virtobs['dx'] >= t_dxSecure_f:
          # No crash within prediction time
          t_aAvoidancePredictedExt_f,t_Situation_ub,l_UndefinedaAvoidDueToWrongdxSecure_b = self.cpr_CalcaAvoidance_SingleStep(t_virtego, t_virtobs, t_dxSecure_f)
      else:
          # Crash occured within prediction time
          # => aAvoid = -10m/s^2
          t_aAvoidancePredictedExt_f = -10.0
      

      # -----------------------------------------------------------------------------------  
      # ***********************************************************
      # Internal Determination if obstacle is "oncoming" 
      # ***********************************************************
      # absolute obstacle velocity is negativ
      if pub['l_vObstacle_f'] < cCalcAEBS.threshold_vObstacle_oncoming:
          t_oncomingInternal_b = 1
      else:
          t_oncomingInternal_b = 0
      
      # Oncoming obstacle  
      # if( (t_obs_pc->GetRelMotionDirection() == ONCOMING)  
      #    || (t_oncomingInternal_b == TRUE))

        
      if(t_oncomingInternal_b):
          t_aAvoidancePredictedExt_f = 0.0
          # Reset static markers to false
          pub['l_CollisionOccuredTillPredictionTime_b'] = 0
          pub['l_VehiclesStoppedWithoutCollisionTillPredictionTime_b'] = 0

          # Set status info for interpretation of aAvoid result
          pub['l_UndefinedaAvoidResult_b']                = 1
          pub['l_UndefinedaAvoidDueToOncomingObstacle_b'] = 1


      CollisionOccuredTillTPredict = pub['l_CollisionOccuredTillPredictionTime_b']
      aAvoidancePredicted = t_aAvoidancePredictedExt_f
      Situation = t_Situation_ub

      return (aAvoidancePredicted,Situation,CollisionOccuredTillTPredict,internal)

    # ==========================================================================================
    def cpr_CalcaAvoidancePredictedModelbased(self, ego, obs, dxSecure, par):
        # calculate required constant acceleration to avoid the collision 
        # based on the sitution given by
        #   ego['vx']   : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']   : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']   : [m]     current distance from ego vehicle to obstacle
        #   obs['vRel'] : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel'] : [m/s^2] current relative acceleration =  0;
        #   dxSecure    : [m]     final safety distance to obstacle  (can also be a vector)
        #   par         : dict    parameters
        #    tWarn                - acoustic warning before partial braking
        #    tPrediction          - Prediction time
        #    P_aStdPartialBraking - acceleration partial braking  phase
        #    P_aEmergencyBrake    - acceleration emergency braking phase
        #    P_aGradientBrake     - pressure build up gradient

    
        # get maximal length of input arguments
        N_ego_vx    = cCalcAEBS.length(ego['vx'])
        N_ego_ax    = cCalcAEBS.length(ego['ax'])
        N_obs_dx    = cCalcAEBS.length(obs['dx'])
        N_obs_vRel  = cCalcAEBS.length(obs['vRel'])
        N_obs_aRel  = cCalcAEBS.length(obs['aRel'])
        N_dxSecure  = cCalcAEBS.length(dxSecure)
        N = np.max([N_ego_vx,N_ego_ax,N_obs_dx,N_obs_vRel,N_obs_aRel,N_dxSecure])
     
        # bring input argument to same length     
        if N_ego_vx == 1:
            ego['vx'] = ego['vx']*np.ones(N)
      
        if N_ego_ax == 1:
            ego['ax'] = ego['ax']*np.ones(N)

        if N_obs_dx == 1:
            obs['dx'] = obs['dx']*np.ones(N)

        if N_obs_vRel == 1:
            obs['vRel'] = obs['vRel']*np.ones(N)

        if N_obs_aRel == 1:
            obs['aRel'] = obs['aRel']*np.ones(N)

        if N_dxSecure == 1:
            dxSecure = dxSecure*np.ones(N)

        # output signals
        aAvoidancePredicted          = np.zeros(N)
        Situation                    = np.zeros(N)
        CollisionOccuredTillTPredict = np.zeros(N)

        # loop over single steps
        for k in xrange(N):
            l_ego = {}
            l_ego['vx']    = ego['vx'][k] 
            l_ego['ax']    = ego['ax'][k] 
      
            l_obs = {}
            l_obs['dx']    = obs['dx'][k]
            l_obs['vRel']  = obs['vRel'][k] 
            l_obs['aRel']  = obs['aRel'][k] 

            par['dxSecure'] = dxSecure[k]
  
            t_aAvoidancePredicted,t_Situation,t_CollisionOccuredTillTPredict,t_internal = self.cpr_CalcaAvoidancePredictedModelbased_SingleStep(l_ego, l_obs, par)
 
            # register single step values
            aAvoidancePredicted[k]          = t_aAvoidancePredicted
            Situation[k]                    = t_Situation
            CollisionOccuredTillTPredict[k] = t_CollisionOccuredTillTPredict
       
        # return results 
        return aAvoidancePredicted,Situation,CollisionOccuredTillTPredict   

    # ==========================================================================================
    # dso_CalcaAvoidance.m
    #    def dso_init(self):
    #    def dso_CalcaAvoidance(self, ego, obs,dyminComfortSwingOutMO_f,dyminComfortSwingOutSO_f):
    #    def dso_CalcaAvoidance_SingleStep(self, ego, obs, t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f):
    #    def dso_CalcaAvoidanceMOParable(self, ego, obs, t_dyminComfortSwingOut_f):
    #    def dso_CalcaAvoidanceSOCircle(self, ego, obs, t_dminComfortSwingOut_f):
    #    def dso_calcIfLeftSOPhysicallyPossible_B(self, t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f):
    #    def dso_calcIfRightSOPhysicallyPossible_B(self, t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f):

    # ==========================================================================================
    def dso_init(self):
      # function [pub] = init()

      # --------------------------------------------------
      # parameters
  
      # radius of the turning clearance circle 5.5 m          
      P_DSOdxClearanceCircle_f = 5.5
      self.l_DSOdxTwoClearanceCircle_f = 2*P_DSOdxClearanceCircle_f;
 
    # ==========================================================================================
    def dso_CalcaAvoidance(self, ego, obs,dyminComfortSwingOutMO_f,dyminComfortSwingOutSO_f):
        # function [out] = dso_CalcaAvoidance(ego, obs,dyminComfortSwingOutMO_f,dyminComfortSwingOutSO_f)
        # [out] = dso_CalcaAvoidance(ego, obs, dyminComfortSwingOutMO_f, dyminComfortSwingOutSO_f)
        #
        # input
        #   ego['vx']   : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']   : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']   : [m]     current longitudinal distance from ego vehicle to obstacle
        #   obs['vRel'] : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel'] : [m/s^2] current relative acceleration =  0;
        #   obs['dy']   : [m]     current lateral distance ego vehicle to obstacle
        #   obs['vy']   : [m/s]   current lateral speed of obstacle
        #   obs['MotionClassification'] :   NOT_CLASSIFIED = 0
        #                                   MOVING         = 1
        #                                   STOPPED        = 2
        #                                   STATIONARY     = 3
        #
        #   dyminComfortSwingOutMO_f
        #     Minimal lateral distance to the obstacle to execute a comfortable
        #     swing out for moving and stopped obstacles (e.g. 3 m)
        #   dyminComfortSwingOutSO_f
        #     Minimal lateral distance to the obstacle to execute a comfortable
        #     swing out for standing obstacles (e.g. 3 m)
        # 
        # return
        #   l_DSOayReqComfortSwingOutLeft_f             :  CalcAyAvoidanceLeft
        #   l_DSOayReqComfortSwingOutRight_f            :  CalcAyAvoidanceRight
        #   l_ComfortSwingOutLeftPhysicallyPossible_b   : 
        #   l_ComfortSwingOutRightPhysicallyPossible_b  :
        #      Determinates if the driving task is physically possible, 
        #      considering the vehicle's clearance circle. 

        
       
        # get maximal length of input arguments
        N_ego_vx    = cCalcAEBS.length(ego['vx'])
        N_ego_ax    = cCalcAEBS.length(ego['ax'])
        N_obs_dx    = cCalcAEBS.length(obs['dx'])
        N_obs_dy    = cCalcAEBS.length(obs['dy'])
        N_obs_vRel  = cCalcAEBS.length(obs['vRel'])
        N_obs_vy    = cCalcAEBS.length(obs['vy'])
        N_obs_aRel  = cCalcAEBS.length(obs['aRel'])
        N_MC        = cCalcAEBS.length(obs['MotionClassification'])
        N = np.max([N_ego_vx,N_ego_ax,N_obs_dx,N_obs_dy,N_obs_vRel,N_obs_vy,N_obs_aRel,N_MC])
     
        # bring input argument to same length     
        if N_ego_vx == 1:
            ego['vx'] = ego['vx']*np.ones(N)
      
        if N_ego_ax == 1:
            ego['ax'] = ego['ax']*np.ones(N)

        if N_obs_dx == 1:
            obs['dx'] = obs['dx']*np.ones(N)
            
        if N_obs_dy == 1:
            obs['dy'] = obs['dy']*np.ones(N)

        if N_obs_vRel == 1:
            obs['vRel'] = obs['vRel']*np.ones(N)

        if N_obs_vy == 1:
            obs['vy'] = obs['vy']*np.ones(N)
            
        if N_obs_aRel == 1:
            obs['aRel'] = obs['aRel']*np.ones(N)
            
        if N_MC  == 1:
            obs['MotionClassification'] = obs['MotionClassification']*np.ones(N)


        # output signals
        out = {}
        out['l_DSOayReqComfortSwingOutRight_f']           = np.zeros(N)
        out['l_DSOayReqComfortSwingOutLeft_f']            = np.zeros(N)
  
        out['l_ComfortSwingOutLeftPhysicallyPossible_b']  = np.zeros(N)
        out['l_ComfortSwingOutRightPhysicallyPossible_b'] = np.zeros(N)


        # loop over single steps
        for k in xrange(N):
            l_ego = {}
            l_ego['vx']    = ego['vx'][k] 
            l_ego['ax']    = ego['ax'][k] 
      
            l_obs = {}
            l_obs['dx']    = obs['dx'][k]
            l_obs['dy']    = obs['dy'][k]
            l_obs['vRel']  = obs['vRel'][k] 
            l_obs['vy']    = obs['vy'][k]
            l_obs['aRel']  = obs['aRel'][k] 

            l_obs['MotionClassification'] =  obs['MotionClassification'][k] 
            
            t_out = self.dso_CalcaAvoidance_SingleStep(l_ego, l_obs, dyminComfortSwingOutMO_f,dyminComfortSwingOutSO_f)
  
            # register single step values
            out['l_DSOayReqComfortSwingOutRight_f'][k]           = t_out['l_DSOayReqComfortSwingOutRight_f'] 
            out['l_DSOayReqComfortSwingOutLeft_f'][k]            = t_out['l_DSOayReqComfortSwingOutLeft_f']
            out['l_ComfortSwingOutLeftPhysicallyPossible_b'][k]  = t_out['l_ComfortSwingOutLeftPhysicallyPossible_b']
            out['l_ComfortSwingOutRightPhysicallyPossible_b'][k] = t_out['l_ComfortSwingOutRightPhysicallyPossible_b']
            
            
        # return results 
        return out
        
    # ==========================================================================================
    def dso_CalcaAvoidance_SingleStep(self, ego, obs, t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f):
        # function [pub] = dso_CalcaAvoidance_SingleStep(ego, obs, t_dyminComfortSwingOutMO_f, t_dyminComfortSwingOutSO_f)    
        #
        # The function dso_CalcaAvoidance() determines the necessary acceleration 
        # to pass the given obsatcle by the left and by the right 
        # t_dyminComfortSwingOutMO_sw
        #   dymin by comfortable swing out for moving and stopped obstacles (KA)
        # t_dyminComfortSwingOutSO_sw       
        #   dymin by comfortable swing out for standing obstacles (KA)

        # Choice of the driving task model depending on the type of the obstacle
        # - Circular trajectories will be used for stationary obstacles
        # - A parabolic trajectory will be used by moving targets
        #  
        #  see asf_int.h
        NOT_CLASSIFIED = 0
        MOVING         = 1
        STOPPED        = 2
        STATIONARY     = 3

      
        # if (STATIONARY == obs['MotionClassification']):
            # out = self.dso_CalcaAvoidanceSOCircle(ego, obs, t_dyminComfortSwingOutSO_f)
        # else:
        out = self.dso_CalcaAvoidanceMOParable(ego,obs, t_dyminComfortSwingOutMO_f)
  
        return out
    
    # ==========================================================================================
    def dso_CalcaAvoidanceMOParable(self, ego, obs, t_dyminComfortSwingOut_f):
      # function [pub] = dso_CalcaAvoidanceMOParable(pub, ego, obs, t_dyminComfortSwingOut_f)   

      SWORD_MIN = -16.0  # -2^15;
      SWORD_MAX =  16.0  # 2^15-1;

      # Initialisation of global variables
      out = {}
      out['l_DSOayReqComfortSwingOutRight_f'] = 0
      out['l_DSOayReqComfortSwingOutLeft_f']  = 0
  
      out['l_ComfortSwingOutLeftPhysicallyPossible_b']  = 1
      out['l_ComfortSwingOutRightPhysicallyPossible_b'] = 1

      # Get the position, velocity and acceleration of the given obstacle
      # relative to the given ego vehicle
      t_dxvObstacle_f  = obs['dx']
      t_dyvObstacle_f  = obs['dy']
      t_vRelObstacle_f = obs['vRel'] 
      t_vyvObstacle_f  = obs['vy'] 
      t_aRelObstacle_f = obs['aRel']
  
      # Modelling of the comfortables swing-out manoeuvre                                                            */
      #  Time to execute the swing-out: tmax = ttc                                                                            */
      #  lateral acceleration to execute the comfortable swing-out                                    */
      #  ayneeded = -2(+-dymin-vy.tmax-dy)/(tmax?)                                                                                       */
      if ((t_vRelObstacle_f > 0) or (t_dxvObstacle_f <0)):
        # l_DSODrivingTaskPlausible_b = 0;
        # /* Do nothing */
        pass
      else:
        # Determination of the time available for the maneuver.       
        # This time corresponds to the ttc to the obstacle. 
        # timeAvailableForSwingOut = ttc(obstacle)
        t_timeAvailableForSwingOut_f = self.ctc_CalcTtc_single_step(ego,obs)
    
        t_temp20_f = t_timeAvailableForSwingOut_f**2;
    
        # temp12 = vy*tmax + dy 
        t_temp12_f = t_vyvObstacle_f*t_timeAvailableForSwingOut_f + t_dyvObstacle_f;
    
        # temp10 = dymin - (vy*tmax + dy )
        t_temp10_f = t_dyminComfortSwingOut_f - t_temp12_f

        # temp11 = dymin + (vy*tmax + dy )
        t_temp11_f = t_dyminComfortSwingOut_f - t_temp12_f

        # An: modified to access the two different accelerations (left / right SO)
        # Abfangen, division by 0 
        if (0.0 == t_temp20_f):
          out['l_DSOayReqComfortSwingOutRight_f'] = SWORD_MIN
        else:
          # temp15 = (dymin - (vy*tmax + dy )) / tmax^2 
          t_temp15_f = t_temp10_f/t_temp20_f
      
          # ayneeded = -2(+dymin-vy.tmax-dy)/(tmax^2)
          t_temp31_f = -2.0*t_temp15_f
      
          if (t_temp31_f <= SWORD_MIN):
            out['l_DSOayReqComfortSwingOutRight_f'] = SWORD_MIN
          else:
            if(t_temp31_f >= SWORD_MAX):
              out['l_DSOayReqComfortSwingOutRight_f'] = SWORD_MAX
            else:
              out['l_DSOayReqComfortSwingOutRight_f'] = t_temp31_f


        # temp12 = -(dymin + (vy*tmax + dy ))
        t_temp12_f = -t_temp11_f;
    
        # Abfangen, division by 0 
        if (0.0 == t_temp20_f):
          out['l_DSOayReqComfortSwingOutLeft_f'] = SWORD_MAX
        else:
          # ayneeded = 2(-dymin-vy.tmax-dy)/(tmax?)
          # 
          # temp15 = 2*(-dymin - (vy*tmax + dy )) / tmax^2
          t_temp15_f = t_temp12_f/t_temp20_f

          # ayneeded = -2(-dymin - (vy*tmax + dy )) / tmax^2
          t_temp31_f = -2.0*t_temp15_f
      
          if (t_temp31_f <= SWORD_MIN):
            out['l_DSOayReqComfortSwingOutLeft_f'] = SWORD_MIN
          else:
            if(t_temp31_f >= SWORD_MAX):
              out['l_DSOayReqComfortSwingOutLeft_f'] = SWORD_MAX
            else:
              out['l_DSOayReqComfortSwingOutLeft_f'] = t_temp31_f
            
          
        
      return out
   
    # ==========================================================================================
    def dso_CalcaAvoidanceSOCircle(self, ego, obs, t_dminComfortSwingOut_f):
      # function [pub] = dso_CalcaAvoidanceSOCircle(pub, ego, obs, t_dminComfortSwingOut_f) 

      UWORD_MAX = 500.0   # 2^16-1
      SWORD_MAX =  16.0   #  2^15-1
      SWORD_MIN = -16.0   # -2^15
      NULL_SW = 0.0
  
  
      # Initialisation of the pointer to the ego vehicle
      #
      # Initialisation of global variables
      out = {}
      out['l_DSOayReqComfortSwingOutRight_f'] = 0
      out['l_DSOayReqComfortSwingOutLeft_f'] = 0

      out['l_ComfortSwingOutLeftPhysicallyPossible_b'] = 1
      out['l_ComfortSwingOutRightPhysicallyPossible_b'] = 1
  
      # Initialisation of the object relative attributes
      t_dxvObstacle_f  = obs['dx']
      t_dyvObstacle_f  = obs['dy']
      t_vxEgo_f = ego['vx']
  
  
      # Observance of the clearance circle
      # 
      out['l_ComfortSwingOutLeftPhysicallyPossible_b']  = self.dso_calcIfLeftSOPhysicallyPossible_B(t_dxvObstacle_f,t_dyvObstacle_f,t_dminComfortSwingOut_f)
      out['l_ComfortSwingOutRightPhysicallyPossible_b'] = self.dso_calcIfRightSOPhysicallyPossible_B(t_dxvObstacle_f,t_dyvObstacle_f,t_dminComfortSwingOut_f)
  
      # Determination of the radius of the circular trajectory that enables to
      # avoid the target by steering, considering a minimal distance of 
      # dmin = t_dyminComfortSwingOut_sw 
      # 
      # R = (dx^2+dy^2-dmin^2)/(2*(dmin+/-dy))
      # the corresponding lateral acceleration is given by:
      # ay = +/- Vx^2/R = +/- 2*Vx^2*(dmin+/-dy)/(dx^2+dy^2-dmin^2)
      # (sign depending on the chosen side (left / right steering maneuvre)
      # 
  
      # t_dxSquare_uw = dx^2
      t_dxSquare_f = t_dxvObstacle_f**2
   
      # t_dySquare_uw = dy^2 
      t_dySquare_f = t_dyvObstacle_f**2
  
      # t_dminSquare_uw = dmin^2
      t_dminSquare_f = t_dminComfortSwingOut_f**2

      # t_vxegoSquare_sw = vego^2 
      t_vxegoSquare_f = t_vxEgo_f**2
  
      # t_temp20_uw = dx^2 + dy^2 
      t_temp20_f = t_dxSquare_f + t_dySquare_f
  
      # In a few cases, depending of the parameter values and of the distance 
      # to the obstacle the maneuvre isn't possible any more (the obstacle is 
      # already to close): 
  
      # The solution is only valid if the obstacle is still at a 
      # sufficient distance 
      #  if (   (t_dminSquare_f  <= t_temp20_f) ... original -> division by zero
      if (   (t_dminSquare_f  < t_temp20_f) and (t_dxvObstacle_f > 0)):
        # t_temp21_uw = t_temp20_uw - dmin^2 = dx^2 + dy^2 - dmin^2 
        t_temp21_f = t_temp20_f - t_dminSquare_f
     
        # -------------------------------------------------------------
        # Determination of the radius of the circular trajectory for a 
        # left swing out maneuver 
     
        # t_temp10_sw = dmin + dy 
        t_temp10_f = t_dminComfortSwingOut_f + t_dyvObstacle_f;

        # the left swing out maneuvre makes only sense if the obstacle 
        # is not situated too far right 
        # (the ego driver can otherwise avoid the collision by driving  
        # straight forward.)
     
        # if dmin + dy > 0
        if (t_temp10_f > 0):
          # t_temp22_uw = 2*(dmin + dy) 
          t_temp22_f = 2*t_temp10_f
      
          # 1/R = (2*(dmin + dy))/(dx^2+dy^2-dmin^2)
          t_dInverseRadius_f = t_temp22_f/t_temp21_f
       
          # modification of the calculation strategy to avoid norming and 
          # precision problems 
       
          # if required t_dInverseRadius_f > UWORD_MAX 
          if (t_dInverseRadius_f >= UWORD_MAX):
            # R = (dx^2+dy^2-dmin^2)/(2*(dmin + dy))
            t_dRadius_f = t_temp21_f/t_temp22_f
         
            #t_temp22_uw = Vego^2/R > 0
            t_temp22_f = t_vxegoSquare_f/t_dRadius_f
          else:
            # t_temp22_uw = Vego^2*1/R > 0 
            t_temp22_f = t_vxegoSquare_f * t_dInverseRadius_f
          
       
          # ay = Vego^2/R
          # Set ay to SWORD_MAX if ay >= SWORD_MAX 
       
          # The potential loss of information is functionally not relevant. 
          out['l_DSOayReqComfortSwingOutLeft_f']= min(t_temp22_f,SWORD_MAX);
       
        else:
          # there is no need for a left swing out maneuvre, 
          # the obstacle can be avoided by driving straight forward.
      
          # set the required lateral acceleration for a left SO maneuvre to 0.
          out['l_DSOayReqComfortSwingOutLeft_f']= NULL_SW
       
        


        # ----------------------------------------------------
        # Determination of the radius of the circular trajectory for 
        # a right swing out maneuver

        # t_temp10_sw = dmin - dy 
        t_temp10_f = t_dminComfortSwingOut_f - t_dyvObstacle_f
     
        # the right swing out maneuvre makes only sense if the obstacle 
        # is not situated too far left 
        # (the ego driver can otherwise avoid the collision by driving 
        # straight forward.)
     
        # if dmin - dy > 0 
        if (t_temp10_f > 0):
          # t_temp22_uw = 2*(dmin - dy ) 
          t_temp22_f = 2.0*t_temp10_f

          # 1/R = (2*(dmin - dy))/(dx^2+dy^2-dmin^2)
          t_dInverseRadius_f = t_temp22_f/t_temp21_f
       
          # modification of the calculation strategy to avoid norming and 
          # precision problems 
       
          # if required t_dInverseRadius_f > UWORD_MAX 
          if (t_dInverseRadius_f == UWORD_MAX):
            # R = (dx^2+dy^2-dmin^2)/(2*(dmin - dy))
            t_dRadius_f = t_temp21_f/t_temp22_f
        
            # t_temp22_uw = Vego^2/R > 0 
            t_temp22_f = t_vxegoSquare_sw/t_dRadius_uw
          else:
            # t_temp22_uw = Vego^2*1/R > 0 
            t_temp22_f = t_vxegoSquare_f*t_dInverseRadius_f
          

          # Set t_temp21_uw to SWORD_MAX if t_temp22_uw >= SWORD_MAX, 
          # else to t_temp22_uw 
      
          # The potential loss of information is functionally not relevant. 
          t_temp21_f = min(t_temp22_f,SWORD_MAX)
       
          # ay = -Vego^2/R 
          out['l_DSOayReqComfortSwingOutRight_f'] = -t_temp21_f
       
        else:
          # there is no need for a right swing out maneuvre, the obstacle 
          # can be avoided by driving straight forward.                                                                                                 */
          # set the required lateral acceleration for a right SO
          # maneuvre to 0.               
          out['l_DSOayReqComfortSwingOutRight_f'] = 0;
        

      else:
        # invalid situation
        # mark both swing out maneuvres as physically not possible. 
        out['l_ComfortSwingOutLeftPhysicallyPossible_b'] = 0;
        out['l_ComfortSwingOutRightPhysicallyPossible_b'] = 0;
      
  
      if (not out['l_ComfortSwingOutLeftPhysicallyPossible_b']):
        # set the required lateral acceleration for a left SO maneuvre 
        # to its maximal value.
        out['l_DSOayReqComfortSwingOutLeft_f']= SWORD_MIN
      
  
      if (not out['l_ComfortSwingOutRightPhysicallyPossible_b']):
        # set the required lateral acceleration for a right SO maneuvre 
        # to its maximal value.
        out['l_DSOayReqComfortSwingOutRight_f'] = SWORD_MAX
      
      return out

    # ==========================================================================================
    def dso_calcIfLeftSOPhysicallyPossible_B(self, t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f):
      # function [t_LeftSOPossible_b] = dso_calcIfLeftSOPhysicallyPossible_B(pub,t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f)

      #  This function determines if a a left SO is physically possible, 
      #  considering the radius of the vehicle clearance circle.
      #  INPUTS:
      #    t_dxvObstacle_f    present dx distance to the obstacle
      #    t_dyvObstacle_f    present dy distance to the obstacle
      #    t_dyminSwingOut_f  dymin distance when passing the obstacle
      #  RETURN:
      #    t_LeftSOPossible_b  1: left SO physically possible
      #                        0: left SO physically impossible

      # initialisation of t_LeftSOPossible_b to TRUE 
      t_LeftSOPossible_b = 1
  
      # Determination of the minimal distance needed to execute a swing out 
      # according to the radius of the vehicle clearance circle.
  
      # dmin = sqrt(rmin?-(rmin-(dymin + dy0))?)
      #      = sqrt((dymin + dy0)*(2*rmin-(dymin + dy0)))
      #        with    rmin:           clearance radius  
      #               dymin:  minimal dy to CO to execute a swing out        
  
      # t_dyEffectiveLeftSO_sw = dymin + dy0 
      t_dyEffectiveLeftSO_f = t_dyminSwingOut_f + t_dyvObstacle_f
  
      # temp10 = dxTwoClearanceCircle - dyEffectiveLeftSO = 2*rmin - (dymin + dy0)                                   */
      t_temp10_f = self.l_DSOdxTwoClearanceCircle_f - t_dyEffectiveLeftSO_f
  
      if ((t_temp10_f < 0) or (t_dyEffectiveLeftSO_f <0)):
        # dmin = sqrt(dymin*(2*rmin-(dymin +/- dy0)))
        # The case where (dymin +/- dy0)*(2*rmin - (dymin +/- dy0)) <0 makes 
        # physically no sense  
        # no manoeuvre needed to avoid the obstacle and pass him by dymin 
        # set t_dxminNeededComfortLeftSO_sw to 0 
        t_dxminNeededLeftSO_f = 0.0
      else:
        # temp40 = (dymin + dy0)*(2*rmin - (dymin + dy0)) = (dymin + dy0)*temp10
        t_temp40_f = t_dyEffectiveLeftSO_f*t_temp10_f
    
        # dxmin = sqrt((dymin + dy0)*(2*rmin-(dymin + dy0))) = sqrt(temp40)
        t_dxminNeededLeftSO_f = math.sqrt(t_temp40_f)
  

      # The driving task is not possible anymore considering the given
      # vehicle clearance circle if the present distance to the potential
      # collision object is already lower than the minimal distance physically
      # needed to execute a swing out
      # In the first version this minimal distance is only calculated once,
      # considering the comfort bounds.
  
      # if dx < dxminNeeded
      if (t_dxvObstacle_f < t_dxminNeededLeftSO_f):
        # DrivingTaskPhysicallyPossible = False
        t_LeftSOPossible_b = 0.0
 
  
      return t_LeftSOPossible_b
   
    # ==========================================================================================
    def dso_calcIfRightSOPhysicallyPossible_B(self, t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f):
      # function [t_RightSOPossible_b] = dso_calcIfRightSOPhysicallyPossible_B(pub,t_dxvObstacle_f,t_dyvObstacle_f, t_dyminSwingOut_f)
      # This function determines if a a right SO is physically possible, 
      # considering the radius of the vehicle clearance circle.
      # INPUTS:
      #   t_dxvObstacle_sw                present dx distance to the obstacle
      #   t_dyvObstacle_sw                present dy distance to the obstacle
      #   t_dyminSwingOut_sw              dymin distance when passing the obstacle
      # RETURN:
      #   t_RightSOPossible_b             1: right SO physically possible
      #                                   0: right SO physically impossible

      # initialisation of t_RightSOPossible_b to TRUE 
      t_RightSOPossible_b = 1

      # Determination of the minimal distance needed to execute a 
      # right swing out   
      # according to the radius of the vehicle clearance circle.                                    
  
  
      # dmin = sqrt(rmin^2-(rmin-(dymin - dy0))^2)
      #      = sqrt((dymin - dy0)*(2*rmin-(dymin - dy0)))
      #        with    rmin:           clearance radius
      #                dymin:  minimal dy to CO to execute a swing out
                 
  
      # t_dyEffectiveRightSO_sw = dymin - dy0 
      t_dyEffectiveRightSO_f = t_dyminSwingOut_f - t_dyvObstacle_f
  
      # temp10 = dxTwoClearanceCircle - dyEffectiveLeftSO = 2*rmin - (dymin - dy0)                                   
      t_temp10_f = self.l_DSOdxTwoClearanceCircle_f - t_dyEffectiveRightSO_f
  
      if ((t_temp10_f < 0) or (t_dyEffectiveRightSO_f <0)):
        #  dmin = sqrt(dymin*(2*rmin-(dymin - dy0)))
        #  The case where (dymin - dy0)*(2*rmin - (dymin - dy0)) <0 makes 
        #  physically no sense 
        #  no manoeuvre needed to avoid the obstacle and pass him by dymin 
        #  set t_dxminNeededComfortRightSO_sw to 0 
        t_dxminNeededRightSO_f = 0.0
      else:
        # temp40 = (dymin - dy0)*(2*rmin - (dymin - dy0)) = (dymin -
        # dy0)*temp10
        t_temp40_f = t_dyEffectiveRightSO_f*t_temp10_f

        # dxmin = sqrt((dymin - dy0)*(2*rmin-(dymin - dy0))) = sqrt(temp40)
        t_dxminNeededRightSO_f = math.sqrt(t_temp40_f)
      

      # The driving task is not possible anymore considering the given
      # vehicle clearance circle if the present distance to the potential
      # collision object is already lower than the minimal distance physically
      # needed to execute a swing out
      # In the first version this minimal distance is only calculated once,
      # considering the comfort bounds.
      # if dx < dxminNeeded
      # 
      if (t_dxvObstacle_f < t_dxminNeededRightSO_f):
        # DrivingTaskPhysicallyPossible = False
        t_RightSOPossible_b = 0.0
      
      return t_RightSOPossible_b
   
   
    # ==========================================================================================
    # ctc_CalcTtc.m
    #    def ctc_CalcTtc(self, ego, obs):
    #    def ctc_CalcTtc_single_step(self, ego, obs):
    #    def SolveEquation(self, t_a_f, t_v_f, t_d_f):
    #    def CalcTStop(self, t_aabs_f, t_vabs_f):
    # ==========================================================================================
    def ctc_CalcTtc(self, ego, obs):
        # calculate time to collision
        #   ego['vx']   : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']   : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']   : [m]     current distance from ego vehicle to obstacle
        #   obs['vRel'] : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel'] : [m/s^2] current relative acceleration =  0;

    
        # get maximal length of input arguments
        N_ego_vx    = cCalcAEBS.length(ego['vx'])
        N_ego_ax    = cCalcAEBS.length(ego['ax'])
        N_obs_dx    = cCalcAEBS.length(obs['dx'])
        N_obs_vRel  = cCalcAEBS.length(obs['vRel'])
        N_obs_aRel  = cCalcAEBS.length(obs['aRel'])
        N = np.max([N_ego_vx,N_ego_ax,N_obs_dx,N_obs_vRel,N_obs_aRel])
     
        # bring input argument to same length     
        if N_ego_vx == 1:
            ego['vx'] = ego['vx']*np.ones(N)
      
        if N_ego_ax == 1:
            ego['ax'] = ego['ax']*np.ones(N)

        if N_obs_dx == 1:
            obs['dx'] = obs['dx']*np.ones(N)

        if N_obs_vRel == 1:
            obs['vRel'] = obs['vRel']*np.ones(N)

        if N_obs_aRel == 1:
            obs['aRel'] = obs['aRel']*np.ones(N)


        # output signals
        ttc         = np.zeros(N)

        # loop over single steps
        for k in xrange(N):
            l_ego = {}
            l_ego['vx']    = ego['vx'][k] 
            l_ego['ax']    = ego['ax'][k] 
      
            l_obs = {}
            l_obs['dx']    = obs['dx'][k]
            l_obs['vRel']  = obs['vRel'][k] 
            l_obs['aRel']  = obs['aRel'][k] 

            t_ttc = self.ctc_CalcTtc_single_step(l_ego, l_obs)
  
            # register single step values
            ttc[k]          = t_ttc
       
        # return results 
        return ttc

    # ==========================================================================================
    def ctc_CalcTtc_single_step(self, ego, obs):
      # function [t_ttc_f] = ctc_CalcTtc_single_step(ego,obs)
      # maximal possible time value for current implementation
      UWORD_MAX_for_time = 32 # Sekunden # 2^16/2^11

      # -----------------------------------------------------------------------
      # copy input signals
      t_dxvObstacle_f  = obs['dx']    # distance to the obstacle 
      t_vRelObstacle_f = obs['vRel']  # relative velocity to the obstacle
      t_aRelObstacle_f = obs['aRel']  # relative acceleration to the obstacle 
  
      t_vEgo_f         = ego['vx']    # ego-velocity  
      t_vObstacle_f    = t_vEgo_f + t_vRelObstacle_f   # absolute obstacle velocity  
  
      t_aEgo_f         = ego['ax']    # ego-acceleration
      t_aObstacle_f    = t_aEgo_f + t_aRelObstacle_f   # absolute obstacle acceleration 
  
      # -----------------------------------------------------------------------
      # The calculation of the Ttc is based on the asumption that the
      # relative acceleration remains constant during the prediction time.
      # dx(t) = 0.5*arel*t^2 + vrel*t + dx
      # The ttc is the solution of the equation dx(ttc) = 0
      # Depending on the situation, this equation has one, two, or 
      # zero valid solution:
  
      # dxvObstacle is an invalid start position
      if (t_dxvObstacle_f <= 0):
        # set the ttc value to zero
        t_ttc_f = 0.0
      else:
        t_ttc_f = self.SolveEquation(t_aRelObstacle_f, t_vRelObstacle_f, t_dxvObstacle_f)
      
      #print 't_ttc_f: (1) ', t_ttc_f

      # Determination of the stopping time of both vehicles: 
      t_tEgoStop_f      = self.CalcTStop(t_aEgo_f,     t_vEgo_f)
      t_tObstacleStop_f = self.CalcTStop(t_aObstacle_f,t_vObstacle_f)

      # Verification of the validity of the solution
      # ttc < min(tegostop,tobsstop) --> valid solution
      # ttc >= min(tegostop,tobsstop) --> verification necessary
      # the determined ttc value is greater than the ego / obstacle */
      # stop time.
  
      if (  (t_ttc_f > t_tEgoStop_f) or(t_ttc_f > t_tObstacleStop_f)):
        # t_tEgoStop_uw = min(tegostop,tobsstop) 
        # (the ego vehicle comes first to a stop)
        if (t_tEgoStop_f <= t_tObstacleStop_f):
          # the ego vehicle comes first to a stop. 
          # This doesn't mean that the situation is not critical any more. 
          # Collisions with oncoming traffic can occur after t_tEgoStop_uw.
          # the equation of the distance between ego and obstacle becomes
          # for 0 <= t <= tobsstop :
          # dx(t) = 0.5*aobs*t^2 + vobs*t + dx + 0.5*vego^2/aego
          #       = 0.5*(aobs)*t^2 + (vobs)*t + (0.5*vego^2/aego + dxo)
      
          # t_temp4_sw = 0.5*vego^2/aego
      
          #  the case aego == 0 and vego != 0 is not possible 
          # (tegostop = UWORD_max  handled in the if branch. 
          #  The only case that can occur is aego == 0 and vego == 0. 
          # In this case, the ego vehicle already stands, t_temp4_sw = 0
          if (t_aEgo_f == 0):
            # t_temp4_sw = 0
            t_temp4_f = 0
          else:
            # temp2 = 0.5 * vego * vego [m?/s?]           
            t_temp2_f = 0.5 * t_vEgo_f**2.0
        
            # temp4 = temp2 / aego [m] 
            t_temp4_f = t_temp2_f/t_aEgo_f
     
      
          # temp3 = (0.5*vobs^2/aobs+dxo) = dxo + temp4
          t_temp3_f = t_dxvObstacle_f + t_temp4_f;
      
          # research of the solution of this equation:
          t_ttc_f = self.SolveEquation(t_aObstacle_f,t_vObstacle_f,t_temp3_f)
      
      
          # Verification of the validity of the solution
          # if ttc <= tobsstop, the solution is valid
          # otherwise, we have to check if the end-distance bewteen the 2
          # stopped vehicles is greater 0
          # if ttc >= tegostop and ttc <= tobsstop 
          if (  (t_ttc_f >= t_tEgoStop_f) and (t_ttc_f <= t_tObstacleStop_f)):
            # the solution is valid, the obstacle collides with the stopped 
            # ego vehicle. 
            pass
          else:
            # both vehicles have come to a stop
            # tbd is a verification necessary ?dx0 >= 0, 
            # no ttc value found < tegosto
        
            #  dx >= 0 till tegostop, there is no risk of collision 
            #  set the ttc value to its maximal value
            t_ttc_f = UWORD_MAX_for_time
            
          #print 't_ttc_f: (2) ', t_ttc_f
  
        else:
          # the equation of the distance between ego and obstacle becomes
          # for 0 <= t <= tegostop:
          # dx(t) = -0.5*vobs^2/aobs + dx0 -(0.5*aego*t^2 + vego*t)
          #       = 0.5*(-aego)*t^2 + (-vego)*t + (-0.5*vobs^2/aobs+dxo)
          #       
      
          #  t_temp4_sw = 0.5*vobs^2/aobs
      
          # the case aoH == 0 and voH != 0 is not possible (tobsstop =
          # UWORD_max handled in the if branch. 
          # The only case that can occur is aoH == 0 and voH == 0. 
          # In this case, the obstacle already stands, t_temp4_sw = 0
          if (t_aObstacle_f == 0):
            # t_temp4_sw = 0   
            t_temp4_f = 0
          else:
            # temp1 = 0.5 * voH [m/s]                                    
            t_temp1_f = 0.5*t_vObstacle_f
        
            # temp2 = temp1 * voH = 0.5 * voH * voH [m?/s?]           
            t_temp2_f = t_temp1_f * t_vObstacle_f
        
            # temp4 = temp2 / aoH [m]
       
            # The use of a standard dSW norm can lead to a loss of precision
            # in case of a high velocity of the target     and dstop > 256m.
            # This will be accepted in a first time since such    
            # situations lead to high ttc values, which are less relevant.
            # --> to be changed if higher precision needed.
            t_temp4_f = t_temp2_f/t_aObstacle_f
      
      
          # temp3 = (-0.5*vobs^2/aobs+dxo) = dxo - temp4
          t_temp3_f = t_dxvObstacle_f - t_temp4_f
      
          # t_temp1_sw = -aego 
          t_temp1_f = -t_aEgo_f
      
          # t_temp2_sw = -vego
          t_temp2_f = -t_vEgo_f
          
          # research of the solution of this equation:
          t_ttc_f = self.SolveEquation(t_temp1_f,t_temp2_f,t_temp3_f)
      
          # Verification of the validity of the solution
          # if ttc <= tegostop, the solution is valid
          # otherwise, we have to check if the end-distance bewteen the 2
          # stopped vehicles is greater 0
      
          # if ttc >= tobsstop and ttc <= tegostop 
          if (  (t_ttc_f >= t_tObstacleStop_f) and (t_ttc_f <= t_tEgoStop_f)):
            # the solution is valid, the ego vehicle collides with the stopped
            # obstacle.
            pass
          else:
            # both vehicles have come to a stop
            # tbd is a verification necessary ?dx0 >= 0, 
            # no ttc value found < tegosto
        
            # dx >= 0 till tegostop, there is no risk of collision 
            # set the ttc value to its maximal value
            t_ttc_f = UWORD_MAX_for_time
            
          #print 't_ttc_f: (3) ', t_ttc_f

      
  
      #print 't_ttc_f: ', t_ttc_f
      return t_ttc_f
  
    # ==========================================================================================
    def SolveEquation(self, t_a_f, t_v_f, t_d_f):
      # function [t_ttc_f] = SolveEquation(t_a_f, t_v_f, t_d_f)
      # determination of the ttc given the equation d(t) = 0.5*a*t^2 + v*t + d

      #print "SolveEquation -start"
      
      UWORD_MAX_for_time = 32.0 # Sekunden # 2^16/2^11 

      # absolute value of the relative acceleration
      t_temp1_f = abs(t_a_f)
  
      # modified: to avoid precision's problems 
      # if (aRelObstacle == 0) replaced by if (|aRelObstacle| < 0.1) 
      if (t_temp1_f <= 0.1):
        # the equation of the relative distance between the obstacles 
        # can be simplified:
        #  dx(t) = v*t + d
        if ((t_v_f >= 0) and (t_d_f >= 0)):
          # set the ttc value to its maximal value
          t_ttc_f = UWORD_MAX_for_time
        else:
          if ((t_v_f <= 0) and (t_d_f <= 0)):
            # set the ttc value to its maximal value
            t_ttc_f = 0.0
          else:
            # ttc = -dx/vrel
            # the checks dx >0 and vrel < 0 have already been performed 
        
            # t_temp1_uw = abs(dx)
            t_temp1_f = abs(t_d_f)
        
            # t_temp2_uw = abs(vrel)
            t_temp2_f = abs(t_v_f)
        
            # ttc = abs(dx)/abs(vrel)
            t_ttc_f = t_temp1_f/t_temp2_f
         
      else:
        # the relative acceleration between the obstacles is not nil
        # delta = v*v -2*a*d
        # delta < 0: ttc = oo
        # delta = 0: ttc = -v/a
        # delta > 0: ttc = (-v +/- sqrt(delta))/a
        # 
        # /**************************/
        # /* Determination of delta */
        # /**************************/
    
        # The calculation will be performed with SL (instead of SW)
        # to avoid a loss of information.
    
        # Determination of vRelObstacle^2
        # temp1 = vRelObstacle * vRelObstacle 
        t_temp1_f = t_v_f**2.0
    
        # Using a MUL_SLUWUB_SL macro with the Norm              
        # N_logA32SWMuldSW2vvSL_ub and the Normal SW value of the
        # acceleration is equivalent to multiplying it with 2. 
    
        # UmNormierung A32
        t_temp2_f = t_a_f
    
        # temp2_sl = temp2_sw * dxvObstacle = 2*aRelObstacle*dxvObstacle
        t_temp2_f = 2.0*t_temp2_f * t_d_f
    
        # delta = vRelObstacle^2-2*aRelObstacle*dxvObstacle
        t_delta_f = t_temp1_f - t_temp2_f
    
    
        if (t_delta_f > 0):
          # the initial equation admits two solutions
          #  ttc1/2 = (-v -+ sqrt(delta))/a
          #  the only interesting solution is the lowest positive one 
          #  that is to say ttc = (-v +- sqrt(delta))/a
          #  In 2 cases both values are negative: The sign of the
          #  distance between the object and the ego vehicle remains
          #  constant (same sign as d).
          if ((t_d_f > 0) and (t_v_f > 0) and (t_a_f > 0)):
            # set the ttc value to its maximal value
            t_ttc_f = UWORD_MAX_for_time
          else:
            if ((t_d_f < 0) and (t_v_f < 0) and (t_a_f < 0)):
              # set the ttc value to its maximal value
              t_ttc_f = 0.0
            else:
              # temp1 = sqrt(delta)
              # Using of constant for shift factor                 
              t_temp1_f = math.sqrt(t_delta_f)
          
              if (t_d_f > 0):
                # temp3 = -vrel - sqrt(delta)
                t_temp2_f = -t_v_f - t_temp1_f
              else:
                # temp3 = -vrel + sqrt(delta)
                t_temp2_f = -t_v_f + t_temp1_f
                
              # temp1 = abs(-vrel +- sqrt(delta))
              t_temp1_f = abs(t_temp2_f)
          
              # temp4 = abs(aRel)
              t_temp2_f = abs(t_a_f)
          
              # t_ttc_uw = abs(-vRel +- sqrt(delta) / aRel)
              t_ttc_f = t_temp1_f/t_temp2_f
        
      
        else:
          if (t_delta_f == 0):
            # ttc = -v / a 
            # dx > 0 so that arel > 0, the sign of ttc depends on 
            # the sign of vrel:
            # vrel >= 0, no valid positive ttc value, ttc = oo          
            # vrel < 0, ttc = -v / a > 0
            if (t_v_f >= 0):
              # set the ttc value to its maximal value
              t_ttc_f = UWORD_MAX_for_time
            else:
              # t_temp1_uw = -vrel > 0
              t_temp1_f = -t_v_f

              # t_temp2_uw = arel > 0 
              t_temp2_f = -t_a_f
          
              # ttc = -vrel / arel > 0
              t_ttc_f = t_temp1_f/t_temp2_f
            
          else: 
            # t_delta_sl < NULL_SL
            # the distance between the 2 vehicles will allways          
            # positive (dx(0) > 0) so that ttc = oo
            # set the ttc value to its maximal value
            t_ttc_f = UWORD_MAX_for_time
      
      #print "SolveEquation", t_ttc_f
      return t_ttc_f
    
    # ==========================================================================================
    def CalcTStop(self, t_aabs_f, t_vabs_f):
        # function [t_tStop_f] = CalcTStop(t_aabs_f, t_vabs_f)
        # determination of the stopping time of the vehicle described by the   
        # the absolute acceleration aabs and the absolute velocity vabs                        
  
        # Determination of the delay required by the vehicle to stop
        # aabs = 0 and vabs = 0: the vehicle has already stopped, t = 0
        # aabs = 0 and vabs != 0: t = UWORD_MAX
        # if vabs.aabs <0: t=-vabs/aabs
        # else: t = UWORD_MAX (the vehicle is accelerating)
  
        UWORD_MAX_for_time = 32.0 # Sekunden  2^16/2^11

        if (t_aabs_f == 0):
            # vehicle already stopped
            if (t_vabs_f == 0):
                 # Set tStop to zero
                 t_tStop_f = 0
            else:
                 # the vehicle is driving constantly and will not stop
                 t_tStop_f = UWORD_MAX_for_time
        else:
            # no better precision needed by little values of aabs
            # the vehicle is decelerating and will come to a stop
            if (((t_vabs_f < 0) and (t_aabs_f > 0)) or ((t_vabs_f >= 0) and (t_aabs_f < 0))):
               # temp1 = abs(vabs) >= 0
               t_temp1_f = abs(t_vabs_f)
       
               # temp2 = abs(aabs) > 0
               t_temp2_f = abs(t_aabs_f)

               # the vehicle is decelerating and will come to a stop
               # t_tStop_uw = abs(v/a)
               t_tStop_f = t_temp1_f/t_temp2_f
            else:
               # the vehicle is accelerating and will not stop
               t_tStop_f = UWORD_MAX_for_time
       
        #print 't_tStop_f: ', t_tStop_f
        return t_tStop_f

    # ==========================================================================================
    def CalcPredictedObjectMotion(self,t_ego,t_obs,t_tPredict_f,t_axvPredictEnd_f,t_aDtVeh_f):
        # [ego, obs] = CalcPredictedObjectMotion(ego,obs,t_tPredict_f,t_axvPredictEnd_f,t_aDtVeh_f)
        #
        # assumption: constant acceleration gradient
        #
        # input:
        #   ego['vx']   - ego vehicle speed 
        #   ego['ax']   - ego vehicle acceleration
        #   obs['dx']   - distance obstacle to ego vehicle
        #   obs['vRel'] - obstacle speed relative to ego vehicle
        #   obs['aRel'] - obstacle acceleration relative to ego vehicle
        #   t_tPredict_f      - prediction time (horizont)
        #   t_axvPredictEnd_f - acceleration ego vehicle shall reach at 
        #   t_aDtVeh_f        - acceleration gradient
        #
        # output:
        #   ego['vx']   - ego vehicle speed 
        #   ego['ax']   - ego vehicle acceleration
        #   obs['dx']   - distance obstacle to ego vehicle
        #   obs['vRel'] - obstacle speed relative to ego vehicle
        #   obs['aRel'] - obstacle acceleration relative to ego vehicle
        #   t_tRemain_f - remaining prediction time
      

        # temporary variables 
   
        # Duration of acceleration ramp
        # UWORD t_tDuration_uw;
   
        # Time within which the TO will come to standstill
        # UWORD t_tObstStopped_uw;

        # Difference distance to TO cause by ego vehicle motion
        # SWORD t_dxDeltaEgo_sw;

        # Difference distance to TO cause by TO motion
        # SWORD t_dxDeltaObs_sw;

        # Velocity difference ego vehicle
        # SWORD t_vxvDeltaEgo_sw;

        # Velocity difference target object
        # SWORD t_vxvDeltaObs_sw;

        # Acceleration difference ego vehicle
        # SWORD t_axvDeltaEgo_sw;

        # Difference relative acceleration
        # SWORD t_axvDeltaRel_sw;

        # Remaining time
        # UWORD t_tRemain_uw;

        # Target vehicle stops within cascade
        # BOOL  t_TargetStopsWithinPrediction_b;

        # Ego vehicle speed at end of prediction time
        # SWORD t_vxvEgoPredicted_sw;

        # Ego vehicle acceleration at end of prediction time
        # SWORD t_axvEgoPredicted_sw;

        # Distance to TO at end of prediction time
        # SWORD t_dxvRelPredicted_sw;

        # Relative velocity to TO at end of prediction time
        # SWORD t_vxvRelPredicted_sw;

        # Relative accelaeration to TO at end of prediction time
        # SWORD t_axvRelPredicted_sw;

        # Temporary variables for calculations
        # SWORD t_temp1_sw;
        # SWORD t_temp2_sw;
        # UWORD t_temp3_uw;
        # SLONG t_temp4_sl;

        # end temporary variables
   
   
        ego = {}
        ego['vx'] = t_ego['vx']
        ego['ax'] = t_ego['ax']
        
        obs = {}
        obs['dx'] =               t_obs['dx'] 
        obs['vx'] = t_ego['vx'] + t_obs['vRel'] 
        obs['ax'] = t_ego['ax'] + t_obs['aRel'] 
        #print "  obs['ax']", obs['ax']
        #print "t_axvPredictEnd_f",t_axvPredictEnd_f
        #print "t_aDtVeh_f", t_aDtVeh_f
        
        
        # Ego vehicle acceleration will be considered to be constant if
        # acceleration gradient is given as 0 or positive value
        # OR target acceleration is the same or bigger than current acceleration
        if (   (t_aDtVeh_f >= 0.0) or (t_axvPredictEnd_f >= ego["ax"]  )):
            #print "if path"
            # Calculate temporary delta values
            t_axvDeltaEgo_f = 0.0
            t_axvDeltaRel_f = 0.0

            # No acceleration ramp => duration is prediction time
            t_tDuration_f = t_tPredict_f
        else:
            #print "else path"
            # Calculate temporary delta values
            t_axvDeltaEgo_f =  t_axvPredictEnd_f-ego["ax"]
            t_axvDeltaRel_f = -t_axvDeltaEgo_f

            # Calculate predicted duration of ramp
            # Math function DIV_SWSWUB_UW not available, therefore
            # DIV_SWSWUB_SW used and then variable casted to UW.
            # Value should not be negative, anyhow, and 15s enough
            t_temp1_f = t_axvDeltaEgo_f/t_aDtVeh_f
            t_tDuration_f = np.max([0.0,t_temp1_f])

            # Check if predicted duration of ramp is bigger than the available
            # prediction time and prediction time is limited (NULL = unlimited)
            if (   (t_tDuration_f > t_tPredict_f) and (t_tPredict_f > 0.0)  ):
                # Adjust predicted duration of ramp
                t_tDuration_uw = t_tPredict_uw
            
        #print "t_tDuration_f", t_tDuration_f
        #print "t_axvDeltaEgo_f", t_axvDeltaEgo_f
        #print "t_axvDeltaRel_f", t_axvDeltaRel_f
    
        #***************************
        #* Ego vehicle calculation *
        #***************************

        # Calculate velocity difference of ego vehicle
        # vDiffEgo = (0.5 * deltaAego * tDuration) + (aEgo * tDuration)
        t_vxvDeltaEgo_f = 0.5*(t_axvDeltaEgo_f * t_tDuration_f) +  ego["ax"]*t_tDuration_f
        
         
        # Calculate velocity difference of ego vehicle
        # dxDiffEgo = ((deltaAego * tDuration * tDuration) / 6) + ...
        #             ((aEgo * tDuration * tDuration) / 2) + ...
        #               vEgo * tDuration;                                     
        t_dxDeltaEgo_f =  (t_axvDeltaEgo_f/6.0 + ego["ax"]/2.0)*t_tDuration_f*t_tDuration_f + ego["vx"]*t_tDuration_f

        # Set predicted ego vehicle velocity
        t_vxvEgoPredicted_f = ego["vx"] + t_vxvDeltaEgo_f

        # Set predicted ego vehicle acceleration
        t_axvEgoPredicted_f = ego["ax"] + t_axvDeltaEgo_f

        #print "t_vxvEgoPredicted_f", t_vxvEgoPredicted_f
        #print "t_axvEgoPredicted_f", t_axvEgoPredicted_f
        
        #*****************************
        #* Target vehicle prediction *
        #*****************************

        # Check if target object stops before the prediction time ends 
        if (obs["ax"] >= 0.0):
            # Target vehicle accelerating => it can't come to standstill
            t_TargetStopsWithinPrediction_b = False
        else:
            # Target vehicle decelerating => calculate stopping time
            # t_tObstStopped_f = - pub.l_vObstacle_f / pub.l_aObstacle_f;
            # Math function DIV_SWSWUB_UW not available, therefore 
            # DIV_SWSWUB_SW used and then variable casted to UW.
            # Value should not be negative, anyhow, and 15s enough
            t_tObstStopped_f = np.max([0.0,-obs["vx"]/obs["ax"]])
            #print "t_tObstStopped_f", t_tObstStopped_f
            # Check if stopping time is smaller than prediction time
            if (t_tObstStopped_f >= t_tDuration_f):
                t_TargetStopsWithinPrediction_b = False
            else:
                t_TargetStopsWithinPrediction_b = True
         
        #print "t_TargetStopsWithinPrediction_b", t_TargetStopsWithinPrediction_b

        
        if (not t_TargetStopsWithinPrediction_b):
            # Calculate changes in target vehicle motion 
            t_vxvDeltaObs_f = obs["ax"] * t_tDuration_f

            # dxDiffObst = 0.5 * aObstacle * tDuration * tDuration +  vObstacle * tDuration;                        
            t_dxDeltaObs_f = 0.5* obs["ax"]*t_tDuration_f*t_tDuration_f + obs["vx"]*t_tDuration_f
  
            # Calculate predicted relative velocity 
            t_vxvRelPredicted_f = (obs["vx"]-ego["vx"]) + t_vxvDeltaObs_f - t_vxvDeltaEgo_f;
            #t_vxvRelPredicted_f = obs["vx"] + t_vxvDeltaObs_f - t_vxvDeltaEgo_f;
             
            # Calculate predicted relative acceleration
            t_axvRelPredicted_f = (obs["ax"]-ego["ax"]) + t_axvDeltaRel_f
            #print "hi"
            #t_axvRelPredicted_f = obs["ax"] + t_axvDeltaRel_f
  
        else:
            # Calculate changes in target vehicle motion 
            # dxDiffObst = 0.5 * aObstacle * tObstStopped * tObstStopped + vObstacle * tObstStopped;
            t_dxDeltaObs_f = 0.5*obs["ax"]*t_tObstStopped_f*t_tObstStopped_f + obs["vx"]*t_tObstStopped_f
            
            # Calculate predicted relative velocity
            t_vxvRelPredicted_f = -t_vxvEgoPredicted_f

            # Calculate predicted relative acceleration
            t_axvRelPredicted_f = -t_axvEgoPredicted_f
     
        # Calculate predicted distance
        # dxvObstaclePredicted = dxvObstacle + dxDiffObst - dxDiffEgo;
        t_dxvRelPredicted_f = obs["dx"] + t_dxDeltaObs_f - t_dxDeltaEgo_f
     
 
        # Set output values

        # virtual ego vehicle
        ego["vx"] = t_vxvEgoPredicted_f
        ego["ax"] = t_axvEgoPredicted_f

        # virtual obstacle
        obs["dx"] = t_dxvRelPredicted_f
        obs["vx"] = ego["vx"] + t_vxvRelPredicted_f
        obs["ax"] = ego["ax"] + t_axvRelPredicted_f
        
        #print "   t_axvRelPredicted_f", t_axvRelPredicted_f
        #print "   obs['ax']", obs['ax']
        
        # Calculate remaining prediction time
        if (t_tPredict_f > t_tDuration_f):
            t_tRemain_f = t_tPredict_f - t_tDuration_f
        else:
            t_tRemain_f = 0.0


        t_ego['vx'] = ego['vx']
        t_ego['ax'] = ego['ax']
        
        
        t_obs['dx']    =             obs['dx']
        t_obs['vRel']  = obs['vx'] - ego['vx']
        t_obs['aRel']  = obs['ax'] - ego['ax']

        return t_tRemain_f;
    
    # ==========================================================================================
    def cpr_CalcaAvoidancePredictedCascade_SingleStep(self, ego, obs, par):
      verbatim = False    

      # [aAvoidancePredicted,Situation,CollisionOccuredTillTPredict,EgoStoppedSafelyDuringTPredict] = ...
      #      cpr_CalcaAvoidancePredictedModelbased_SingleStep(ego, obs, dxSecure,tPrediction,P_aStdPartialBraking,P_aEmergencyBrake,P_aGradientBrake)
      #
      #SWORD Cpr::CalcaAvoidancePredictedCascade(UBYTE t_handleEgo_ub,         UBYTE t_handleObs_ub,
      #                                    UWORD t_tWarn_uw,             UWORD t_tPartBraking_uw,
      #                                    UWORD t_tBrakeDelay1_uw,      UWORD t_tBrakeDelay2_uw,
      #                                    SWORD t_axvPartialBraking_sw, SWORD t_axvFullBraking_sw,
      #                                    SWORD t_dxSecure_sw)
      
      
      
      #  Calculates the avoidance acceleration to an object after following a
      #  certain intervention model in dependency of a safety distance and a 
      #  prediction time. 
      #
      #  ego         - ego vehicle state
      #  obs         - obstacle state
      #  par         - parameters
      #    dxSecure    - Distance from the obstacle at which the relative velocity has to be nil
      #    tWarn       - acoustic warning before partial braking
      #    tPrediction          - Prediction time
      #    P_aStdPartialBraking - acceleration partial braking  phase
      #    P_aEmergencyBrake    - acceleration emergency braking phase
      #    P_aGradientBrake     - pressure build up gradient

      # parameters
    
      t_dxSecure_f          = par['dxSecure'] 
      t_tWarn_f             = par['tWarn']
      t_tPartBraking_f      = par['tPartBraking']
      t_tBrakeDelay1_f      = par['tBrakeDelay1']
      t_tBrakeDelay2_f      = par['tBrakeDelay2']
      t_axvPartialBraking_f = par['axvPartialBraking']
      t_axvFullBraking_f    = par['axvFullBraking']
      
      

    
      #
      # temporary variables
      #

      # Avoidance acceleration */
      # SWORD t_aAvoid_sw;

      # Acceleration fo full brake interventions */
      # SWORD t_axvFullBrkInterv_sw;

      # Remaining time
      # UWORD t_tRemain_uw;

      # Pointer to PSS obstacle
      # Obstasf* t_obs_pc;

      # Pointer to egovehicle
      # Egveasf* t_ego_pc;

      # Pointer to PSS obstacle
      # Viobasf* t_virtobs_pc

      # Pointer to egovehicle
      # Viegasf* t_virtego_pc

      # 
      # end temporary variables
      # 

      # Initialisation of the pointer to the virtual obstacle
      # t_virtobs_pc = envrasf->GetVirtObs();

      # Initialisation of the pointer to the virtual ego vehicle */
      # t_virtego_pc = envrasf->GetVirtEgo();


      # conversion of the obstacle's handle into an object's pointer
      # t_obs_pc = Obstasf::ConvertHandleToPointer(t_handleObs_ub);

      # conversion of the ego handle into an ego pointer
      # t_ego_pc = (Egveasf*)Obstasf::ConvertHandleToPointer(t_handleEgo_ub);


      # Initialize virtual pbjects 
      # t_virtobs_pc->InitVirtobs(t_obs_pc);
      # t_virtego_pc->InitVirtego(t_ego_pc);

      t_virtego_pc = {}
      t_virtego_pc['vx'] = ego['vx']
      t_virtego_pc['ax'] = ego['ax']
      
      t_virtobs_pc = {}
      t_virtobs_pc['dx']   = obs['dx'] 
      t_virtobs_pc['vRel'] = obs['vRel'] 
      t_virtobs_pc['aRel'] = obs['aRel'] 

      
      

      # Make sure acceleration for full braking is less than for partial braking */
      if (t_axvFullBraking_f < t_axvPartialBraking_f):
        # Full braking stronger than partial braking 
        # => Use given full braking parameter
        t_axvFullBrkInterv_f = t_axvFullBraking_f
      else:
        # Full braking not stronger than partial braking
        # => Use partial braking value also for full braking
        t_axvFullBrkInterv_f = t_axvPartialBraking_f
   
      if verbatim:
        print "Start"
        print "  t_virtego_pc['vx']", t_virtego_pc["vx"]
        print "  t_virtego_pc['ax']", t_virtego_pc["ax"]
      
        print "  t_virtobs_pc['dx']", t_virtobs_pc["dx"]
        print "  t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
        print "  t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
        print "  t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
        print "  t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]


      # Predict object (ego and TO) motion during warning cascade

      # Step 1: Warning time
      # Vehicle motion assumed to continue with constant acceleration
      # => Maximum prediction time: tWarn
      #    Ego acceleration after prediction: Current virtual acceleration 
      #    Acceleration gradient: NULL
      t_tRemain_uw = self.CalcPredictedObjectMotion(t_virtego_pc,t_virtobs_pc,t_tWarn_f,t_virtego_pc["ax"],0.0)
      
      if verbatim:
        print "nach step1:"
        print "  t_virtego_pc['vx']", t_virtego_pc["vx"]
        print "  t_virtego_pc['ax']", t_virtego_pc["ax"]
      
        print "  t_virtobs_pc['dx']", t_virtobs_pc["dx"]
        print "  t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
        print "  t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
        print "  t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
        print "  t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]
      
      

      # Step 2: Brake system reaction delay
      # Brake system assumed to react with a delay on brake request
      # => Maximum prediction time: t_tBrakeDelay1_uw
      #    Ego acceleration after prediction: Current virtual acceleration
      #    Acceleration gradient: NULL
      t_tRemain_uw = self.CalcPredictedObjectMotion(t_virtego_pc,t_virtobs_pc,t_tBrakeDelay1_f,t_virtego_pc["ax"],0.0)

      if verbatim:
        print "nach step2:"
        print "  t_virtego_pc['vx']", t_virtego_pc["vx"]
        print "  t_virtego_pc['ax']", t_virtego_pc["ax"]
      
        print "  t_virtobs_pc['dx']", t_virtobs_pc["dx"]
        print "  t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
        print "  t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
        print "  t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
        print "  t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]


      # Step 2a: Set ego acceleration to partial braking 
      t_virtobs_pc["ax"] = t_virtobs_pc["aRel"]+t_virtego_pc["ax"]
      t_virtego_pc["ax"] = t_axvPartialBraking_f
      t_virtobs_pc["aRel"] = t_virtobs_pc["ax"] - t_virtego_pc["ax"]
      
      
      # Step 3: Partial braking
      # Vehicle assumed to decelerate constantly with value of partial
      # braking acceleration
      # => Maximum prediction time: t_tPartBraking_uw - t_tBrakeDelay1_uw
      #    Ego acceleration after prediction: axvPartialBraking
      #    Acceleration gradient: NULL
      t_tRemain_uw = self.CalcPredictedObjectMotion(t_virtego_pc,t_virtobs_pc,t_tPartBraking_f-t_tBrakeDelay1_f,t_axvPartialBraking_f,0.0)
      if verbatim:
        print "nach step3:"
        print "  t_virtego_pc['vx']", t_virtego_pc["vx"]
        print "  t_virtego_pc['ax']", t_virtego_pc["ax"]
       
        print "  t_virtobs_pc['dx']", t_virtobs_pc["dx"]
        print "  t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
        print "  t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
        print "  t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
        print "  t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]


      # Step 4: Brake system ramping to full braking acceleration
      # Brake system assumed to react with a delay on changed brake request
      # => Maximum prediction time: t_tBrakeDelay2_uw
      #    Ego acceleration after prediction: axvPartialBraking
      #    Acceleration gradient: NULL
      t_tRemain_uw = self.CalcPredictedObjectMotion(t_virtego_pc,t_virtobs_pc,t_tBrakeDelay2_f,t_axvPartialBraking_f,0.0);
      if verbatim:
        print "nach step4:"
        print "  t_virtego_pc['vx']", t_virtego_pc["vx"]
        print "  t_virtego_pc['ax']", t_virtego_pc["ax"]
      
        print "  t_virtobs_pc['dx']", t_virtobs_pc["dx"]
        print "  t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
        print "  t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
        print "  t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
        print "  t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]


      # Step 5: Full braking
      # Calculate necessary avoidance acceleration after steps 1 to 4
      if (t_virtobs_pc["dx"] >= t_dxSecure_f):
        # Calculate avoidance acceleration only if distance to target does
        # not get below dxSecure within prediction time                    */
        
        if verbatim:
          print "t_virtego_pc['vx']", t_virtego_pc["vx"]
          print "t_virtego_pc['ax']", t_virtego_pc["ax"]
      
          print "t_virtobs_pc['dx']", t_virtobs_pc["dx"]
          print "t_virtobs_pc['vRel']", t_virtobs_pc["vRel"]
          print "t_virtobs_pc['aRel']", t_virtobs_pc["aRel"]
          print "t_virtobs_pc['vx']", t_virtobs_pc["vRel"]+t_virtego_pc["vx"]
          print "t_virtobs_pc['ax']", t_virtobs_pc["aRel"]+t_virtego_pc["ax"]
      
        t_aAvoidance_f,t_Situation_ub,l_UndefinedaAvoidDueToWrongdxSecure_b = self.cpr_CalcaAvoidance_SingleStep(t_virtego_pc, t_virtobs_pc, t_dxSecure_f);
      else:
        # Crash occurs within prediction time
        # => request minimum acceleration (maximum deceleration)
        t_aAvoidance_f = -16.0
        t_Situation_ub = -1
        l_UndefinedaAvoidDueToWrongdxSecure_b = False
        # Comment: Maybe it's better to use a parameter here to set the value
        # to a defined (physical) deceleration insted of SWORD_MIN...
    
      # limit t_aAvoidance_f to resonable values
      t_aAvoidance_f = np.clip(t_aAvoidance_f,-16.0, 1.0)
     
      return t_aAvoidance_f,t_Situation_ub,l_UndefinedaAvoidDueToWrongdxSecure_b 
     
       # ==========================================================================================
    def cpr_CalcaAvoidancePredictedCascade(self, ego, obs, dxSecure, par):
        # calculate required constant acceleration to avoid the collision 
        # based on the sitution given by
        #   ego['vx']   : [m/s]   current ego vehicle speed in longitudinal direction     
        #   ego['ax']   : [m/s^2] current ego vehicle acceleration in longitudinal direction 
        #   obs['dx']   : [m]     current distance from ego vehicle to obstacle
        #   obs['vRel'] : [m/s]   current relative speed between ego vehicle and obstacle
        #   obs['aRel'] : [m/s^2] current relative acceleration =  0;
        #   dxSecure    : [m]     final safety distance to obstacle  (can also be a vector)
        #   par         : dict    parameters
        #     tWarn             - time between prewarning and first brake intervention
        #     tPartBraking      - time of partial praking
        #     tBrakeDelay1      - Delay of the brake system to realize the requested deceleration at first request
        #     tBrakeDelay2      - Delay of the brake system to realize the requested deceleration at request changes
        #     axvPartialBraking - Deceleration by reaction time gain standard
        #     axvFullBraking    - Deceleration by reaction time gain extenden
      
      
    
        # get maximal length of input arguments
        N_ego_vx    = cCalcAEBS.length(ego['vx'])
        N_ego_ax    = cCalcAEBS.length(ego['ax'])
        N_obs_dx    = cCalcAEBS.length(obs['dx'])
        N_obs_vRel  = cCalcAEBS.length(obs['vRel'])
        N_obs_aRel  = cCalcAEBS.length(obs['aRel'])
        N_dxSecure  = cCalcAEBS.length(dxSecure)
        N = np.max([N_ego_vx,N_ego_ax,N_obs_dx,N_obs_vRel,N_obs_aRel,N_dxSecure])
     
        # bring input argument to same length     
        if N_ego_vx == 1:
            ego['vx'] = ego['vx']*np.ones(N)
      
        if N_ego_ax == 1:
            ego['ax'] = ego['ax']*np.ones(N)

        if N_obs_dx == 1:
            obs['dx'] = obs['dx']*np.ones(N)

        if N_obs_vRel == 1:
            obs['vRel'] = obs['vRel']*np.ones(N)

        if N_obs_aRel == 1:
            obs['aRel'] = obs['aRel']*np.ones(N)

        if N_dxSecure == 1:
            dxSecure = dxSecure*np.ones(N)

        # output signals
        aAvoidancePredicted          = np.zeros(N)
        Situation                    = np.zeros(N)
        CollisionOccuredTillTPredict = np.zeros(N)

        # loop over single steps
        for k in xrange(N):
            l_ego = {}
            l_ego['vx']    = ego['vx'][k] 
            l_ego['ax']    = ego['ax'][k] 
      
            l_obs = {}
            l_obs['dx']    = obs['dx'][k]
            l_obs['vRel']  = obs['vRel'][k] 
            l_obs['aRel']  = obs['aRel'][k] 

            par['dxSecure'] = dxSecure[k]
  
            t_aAvoidancePredicted,t_Situation,t_CollisionOccuredTillTPredict = self.cpr_CalcaAvoidancePredictedCascade_SingleStep(l_ego, l_obs, par)
 
            # register single step values
            aAvoidancePredicted[k]          = t_aAvoidancePredicted
            Situation[k]                    = t_Situation
            CollisionOccuredTillTPredict[k] = t_CollisionOccuredTillTPredict
       
        # return results 
        return aAvoidancePredicted,Situation,CollisionOccuredTillTPredict   
   

# ==========================================================================================

  
  

