from collections import namedtuple

import numpy as np

__version__ = '1.2.1.12' # corresponds to CVR3_CUBAS project checkpoint

FLOAT32_0 = np.float32(0.0)
FLOAT32_1 = np.float32(1.0)
UINT32_0  = np.uint32(0)

Param = namedtuple('Param', ['value', 'min', 'max', 'unit', 'norm', 'comment'])

# default parameters of association algorithm (generated from padfus_s.xml)
defparams = dict(
# paramname                                =      (value , min, max  , unit , norm           , comment                                                                                                       ),
  alpAsoProbPsiLowerLimit                  = Param(0.0   , 0.0, 0.5  , 'rad', 'N_alpSW_ul'   , 'psi lower limit for association probabilty'                                                                  ),
  alpAsoProbPsiUpperLimit                  = Param(0.05  , 0.0, 0.5  , 'rad', 'N_alpSW_ul'   , 'psi upper limit for association probabilty'                                                                  ),
  dAsoProbDxLowerLimit                     = Param(5.0   , 0.0, 255.0, 'm'  , 'N_dSW_ub'     , 'dx lower limit for association probabilty'                                                                   ),
  dAsoProbDxUpperLimit                     = Param(12.0  , 0.0, 255.0, 'm'  , 'N_dSW_ub'     , 'dx upper limit for association probabilty'                                                                   ),
  dExtFusObjMaxDx                          = Param(60.0  , 0.0, 255.0, 'm'  , 'N_dSW_ub'     , 'maximum dx of priority region for extended fusion objects'                                                   ),
  dExtFusObjMinDx                          = Param(5.0   , 0.0, 255.0, 'm'  , 'N_dSW_ub'     , 'minimum dx of priority region for extended fusion objects'                                                   ),
  fak2AsoFiltDecreaseConst                 = Param(0.98  , 0.0, 1.0  , '-'  , 'N_fak2UW_uw'  , 'association filter constant for increasing values'                                                           ),
  fak2AsoFiltIncreaseConst                 = Param(0.85  , 0.0, 1.0  , '-'  , 'N_fak2UW_uw'  , 'association filter constant for increasing values'                                                           ),
  fak2AsoProbDxLowerLrrVidLowerErrorFactor = Param(0.05  , 0.0, 1.0  , '-'  , 'N_fak2UW_uw'  , 'LRR dx lower error factor for LRR smaller VID'                                                               ),
  fak2AsoProbDxUpperLrrVidLowerErrorFactor = Param(0.0625, 0.0, 1.0  , '-'  , 'N_fak2UW_uw'  , 'LRR dx upper error factor for LRR smaller VID'                                                               ),
  invTAsoProbInvTtcIpcLowerLimit           = Param(0.3   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) lower limit for association probabilty'                     ),
  invTAsoProbInvTtcIpcLowerLimitDx         = Param(0.6   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) lower limit for association probabilty for low distances'   ),
  invTAsoProbInvTtcIpcLowerLimitVx         = Param(4.0   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) lower limit for association probabilty for minimum vx error'),
  invTAsoProbInvTtcIpcUpperLimit           = Param(0.4   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) upper limit for association probabilty'                     ),
  invTAsoProbInvTtcIpcUpperLimitDx         = Param(0.8   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) upper limit for association probabilty for low distances'   ),
  invTAsoProbInvTtcIpcUpperLimitVx         = Param(6.0   , 0.0, 128  , '1/s', 'N_invTSW_uw'  , 'inverse time to collision (image plane crossing) upper limit for association probabilty for minimum vx error'),
  occDeltaDxLimit                          = Param(25.0  , 0.0, 255.0, 'm'  , 'N_dSW_ub'     , 'occlusion detection dx gate'                                                                                 ),
  occWExistLimit                           = Param(0.99  , 0.0, 1.0  , '-'  , 'N_wUW_ul'     , 'occlusion detection wExist limit'                                                                            ),
  occWObstacleLimit                        = Param(0.5   , 0.0, 1.0  , '-'  , 'N_prob1UW_uw' , 'occlusion detection wObstacle Limit'                                                                         ),
  prob1AsoProbInit                         = Param(0.35  , 0.0, 1.0  , '-'  , 'N_prob1UW_uw' , 'association probability initialization value'                                                                ),
  prob1AsoProbLimit                        = Param(0.5   , 0.0, 1.0  , '-'  , 'N_prob1UW_uw' , 'association probability limit'                                                                               ),
  wBestAssoLimit                           = Param(0.99  , 0.0, 1.0  , '-'  , 'N_wUW_ul'     , 'upper limit forperfect association probabilities'                                                            ),
)

# norming constants from norm.h
norms = dict(
  N_dSW_ub     = np.float32(2**7),
  N_invTSW_uw  = np.float32(2**10),
  N_fak2UW_uw  = np.float32(2**15),
  N_prob1UW_uw = np.float32(2**15),
  N_alpSW_ul   = np.float32(2**16),
  N_wUW_ul     = np.float32(2**16),
)

# float <-> fix point conversion functions
def fixMultiply(a, b, norm, fixtype=np.uint32):
  return fixtype( (a * b) / fixtype(norm) )

def float2fixWithoutRounding(value, norm, fixtype=np.uint32):
  return fixtype( value * norm )

def float2fix(value, norm, fixtype=np.uint32):
  return fixtype( value * norm + np.float32(0.5) )

def fix2float(value, norm, floattype=np.float32):
  return floattype(value) / norm

# parameter norming functions
def normParam(value, norm):
  return fix2float( float2fix(np.float32(value), norm), norm )

def normDefParams(pars):
  """
  :Parameters:
    pars : dict
      { paramname<str> : param<Param> }
  """
  return dict( [(name, normParam(par.value, norms[par.norm])) for name,par in pars.iteritems()] )

def normParams(pars):
  """
  :Parameters:
    pars : dict
      { paramname<str> : value<float> }
  """
  return dict( [(name, normParam(value, norms[defparams[name].norm])) for name,value in pars.iteritems()] )

def checkInputParams(pars):
  """
  :Parameters:
    pars : dict
      { paramname<str> : value<float> }
  """
  for name, value in pars.iteritems():
    assert name in defparams, "Error: invalid parameter name '%s'!" %name
    defpar = defparams[name]
    assert value >= defpar.min and value <= defpar.max, "Error: '%s=%s' is outside range [%s,%s]!"\
      %(name, value, defpar.min, defpar.max)
  return

# storage class definitions
Cvr3fusParams = namedtuple('Cvr3fusParams', defparams.iterkeys())
Cvr3fusTransf = namedtuple('Cvr3fusTransf', 'dLongOffsetObjToVidCoordSys dMountOffsetVid')
AssoMeasures  = namedtuple('AssoMeasures' , 'angle dx invttc counter occlusion occluders')

defpars = Cvr3fusParams( **normDefParams(defparams) )

# association algorithm functions
def calcCurrentAssoProb(radarTracks, videoTracks, masks, params, transf):
  # create storage arrays
  angleAssoProb   = np.zeros_like(masks, dtype=np.float32)
  dxAssoProb      = np.zeros_like(masks, dtype=np.float32)
  invTtcAssoProb  = np.zeros_like(masks, dtype=np.float32)
  # vectorized calculations
  for i, radar in radarTracks.iteritems():
      for j, video in videoTracks.iteritems():
          mask = masks[:,i,j]
          if np.any(mask):
            angleAssoProb[mask,i,j] = calcAngleAssoProb(radar['dx'][mask],
                                                        radar['angle'][mask],
                                                        video['alpRightEdge'][mask],
                                                        video['alpLeftEdge'][mask],
                                                        params,
                                                        transf)
            dxAssoProb[mask,i,j] = calcDxAssoProb(radar['dx'][mask],
                                                  video['dx'][mask],
                                                  params)
            invTtcAssoProb[mask,i,j] = calcInvTtcIpcAssoProb(radar['dx'][mask],
                                                             radar['invttc'][mask],
                                                             video['invttc'][mask],
                                                             params,
                                                             transf)
  # check if calculated probabilities are in [0,1] range
  assert np.all( (angleAssoProb   >= FLOAT32_0) | (angleAssoProb   <= FLOAT32_1) )
  assert np.all( (dxAssoProb      >= FLOAT32_0) | (dxAssoProb      <= FLOAT32_1) )
  assert np.all( (invTtcAssoProb  >= FLOAT32_0) | (invTtcAssoProb  <= FLOAT32_1) )
  # calculate temporal current association probability needed for counter association
  angleAssoProb_uint32 = float2fixWithoutRounding( angleAssoProb, norms['N_prob1UW_uw'] )
  dxAssoProb_uint32    = float2fixWithoutRounding( dxAssoProb   , norms['N_prob1UW_uw'] )
  currentAssoProb_uint32 = fixMultiply( angleAssoProb_uint32, dxAssoProb_uint32, norms['N_prob1UW_uw'] )
  # mark unused arrays for deletion
  del dxAssoProb_uint32
  # create storage arrays
  counterAssoProb = np.zeros_like(masks, dtype=np.float32)
  occlusion       = np.zeros_like(masks)
  occluders       = np.empty_like(masks, dtype=np.uint8)
  # time loop
  N = masks.shape[0]
  for n in xrange(N):
    # calculate occlusion
    occlusion_n, occluder_n = calcOcclusion(radarTracks, angleAssoProb_uint32[n], n, params)
    # consider occlusion
    currentAssoProb_uint32[n][occlusion_n] = 0
    # calculate (and consider) counter asso prob
    counter_n = calcCounterAssoProb(masks[n], currentAssoProb_uint32[n], params)
    # save partial results
    occlusion[n,...] = occlusion_n
    occluders[n,...] = occluder_n
    counterAssoProb[n,...] = counter_n
  # update current association probability
  invTtcAssoProb_uint32  = float2fixWithoutRounding( invTtcAssoProb, norms['N_prob1UW_uw'] )
  currentAssoProb_uint32 = fixMultiply( currentAssoProb_uint32, invTtcAssoProb_uint32, norms['N_prob1UW_uw'] )
  # pack result
  measures = AssoMeasures(angle=angleAssoProb, dx=dxAssoProb, invttc=invTtcAssoProb,
                          counter=counterAssoProb, occlusion=occlusion, occluders=occluders)
  return currentAssoProb_uint32, measures

def calcAngleAssoProb(t_dxLrr_f, t_phiLrr_f, t_phiVidRight_f, t_phiVidLeft_f, params, transf):
  # params
  t_LowerPsi_f = params.alpAsoProbPsiLowerLimit
  t_UpperPsi_f = params.alpAsoProbPsiUpperLimit
  # transf
  t_dxLrrVid_f = transf.dLongOffsetObjToVidCoordSys
  # set lrr object dx-dy to camera coordinate system
  t_dxLrr_f = t_dxLrr_f + t_dxLrrVid_f
  # if lrr angle lies inside video angles, the distance is set to zero
  # else the distance is related to the closer object edge angle
  t_DeltaPsi_f = np.where(t_phiLrr_f > t_phiVidLeft_f,
                          t_phiLrr_f - t_phiVidLeft_f, # lrr angle left of left video edge angle
                          np.where(t_phiLrr_f < t_phiVidRight_f,
                                   t_phiVidRight_f - t_phiLrr_f, # lrr angle right of right video edge angle
                                   FLOAT32_0, # lrr angle between left and right video edge angles
                                  )
                         )
  # the angle association gates are decreased with higher distances
  t_UpperPsi_f = t_UpperPsi_f / t_dxLrr_f
  # norming delta_Psi to [0,1]
  t_DeltaPsiNormed_f = (t_UpperPsi_f - t_DeltaPsi_f) / (t_UpperPsi_f - t_LowerPsi_f)
  t_DeltaPsiNormed_f = np.maximum( FLOAT32_0, t_DeltaPsiNormed_f )
  t_DeltaPsiNormed_f = np.minimum( FLOAT32_1, t_DeltaPsiNormed_f )
  return t_DeltaPsiNormed_f

def calcDxAssoProb(t_dxLrr_f, t_dxVid_f, params):
  # params
  t_LowerDx_f     = params.dAsoProbDxLowerLimit
  t_UpperDx_f     = params.dAsoProbDxUpperLimit
  t_loLrrFacLow_f = params.fak2AsoProbDxLowerLrrVidLowerErrorFactor
  t_upLrrFacLow_f = params.fak2AsoProbDxUpperLrrVidLowerErrorFactor
  t_dxMaxVid_f    = params.dExtFusObjMaxDx
  #  new much mor simple version from italy test 
  t_LowerDx_f = t_LowerDx_f + (t_loLrrFacLow_f*t_dxLrr_f) #  5+1/20 dx means 6  at 30 and 9  at 80 
  t_UpperDx_f = t_UpperDx_f + (t_upLrrFacLow_f*t_dxLrr_f) #  8+1/16 dx means 10 at 30 and 13 at 80 
  #  calculate dx absolute distance 
  t_DeltaDx_f  = np.abs(t_dxLrr_f - t_dxVid_f)
  #  norming delta_invTtc to [0,1] 
  t_DeltaDxNormed_f = (t_UpperDx_f - t_DeltaDx_f) / (t_UpperDx_f - t_LowerDx_f)
  t_DeltaDxNormed_f = np.maximum( FLOAT32_0, t_DeltaDxNormed_f )
  t_DeltaDxNormed_f = np.minimum( FLOAT32_1, t_DeltaDxNormed_f )
  #  decrease the dx association probability for object farer away than the specified video view range 
  #  these objects often has correlated wrong dx values which produces a lot of wrong associations 
  #  this operation also could be done for ambiguous situations in respect to the angle but so it's a 
  #  much more simple and a safe solution
  t_DeltaDxNormed_f = np.where( t_dxLrr_f > t_dxMaxVid_f,
                                t_DeltaDxNormed_f * t_dxMaxVid_f / ( t_dxMaxVid_f + ((t_dxLrr_f-t_dxMaxVid_f)*(t_dxLrr_f-t_dxMaxVid_f)) ),
                                t_DeltaDxNormed_f )
  return t_DeltaDxNormed_f

def calcInvTtcIpcAssoProb(t_dxLrr_f, t_invTtcLrr_f, t_InvTtcVid_f, params, transf):
  # params
  t_LowerInvTtc_f   = params.invTAsoProbInvTtcIpcLowerLimit #  approx.  10 m/s at 60 m 
  t_UpperInvTtc_f   = params.invTAsoProbInvTtcIpcUpperLimit #  approx.   5 m/s at 60 m 
  t_LowerInvTtcDx_f = params.invTAsoProbInvTtcIpcLowerLimitDx
  t_UpperInvTtcDx_f = params.invTAsoProbInvTtcIpcUpperLimitDx
  t_LowerInvTtcVx_f = params.invTAsoProbInvTtcIpcLowerLimitVx
  t_UpperInvTtcVx_f = params.invTAsoProbInvTtcIpcUpperLimitVx
  # transf
  t_dxLrrVid_f = transf.dLongOffsetObjToVidCoordSys
  #  set lrr object dx to camera coordinate system
  t_dxLrr_f = t_dxLrr_f + t_dxLrrVid_f
  # temp mask
  maskDxValid = t_dxLrr_f > FLOAT32_0
  #  vx error not smaller than a limit (about3 m/s) and big at low distances (about 10 m) 
  t_LowerInvTtc_f = np.where( maskDxValid,
                              np.minimum( np.maximum(t_LowerInvTtc_f, t_LowerInvTtcVx_f/t_dxLrr_f), t_LowerInvTtcDx_f ),
                              t_LowerInvTtc_f )
  t_UpperInvTtc_f = np.where( maskDxValid,
                              np.minimum( np.maximum(t_UpperInvTtc_f, t_UpperInvTtcVx_f/t_dxLrr_f), t_UpperInvTtcDx_f ),
                              t_UpperInvTtc_f )
  #  calculate inverse ttc absolute distance 
  t_DeltaInvTtc_f = np.abs(t_invTtcLrr_f - t_InvTtcVid_f)
  #  norming delta_invTtc to [0,1] 
  t_DeltaInvTtcNormed_f = (t_UpperInvTtc_f - t_DeltaInvTtc_f) / (t_UpperInvTtc_f - t_LowerInvTtc_f)
  t_DeltaInvTtcNormed_f = np.maximum( FLOAT32_0, t_DeltaInvTtcNormed_f )
  t_DeltaInvTtcNormed_f = np.minimum( FLOAT32_1, t_DeltaInvTtcNormed_f )
  return t_DeltaInvTtcNormed_f

def calcCounterAssoProb(mask, currentAssoProb_uint32, params):
  # initialize output
  counterAssoProb = np.zeros_like(currentAssoProb_uint32, dtype=np.float32)
  # params
  prob1AsoProbLimit_uint32 = float2fixWithoutRounding(params.prob1AsoProbLimit, norms['N_prob1UW_uw'])
  # object loop
  rows, cols = mask.shape
  for i in xrange(rows):
      for j in xrange(cols):
          if mask[i,j]:
            # lrr and vid object are both valid
            # initialize counter for associatable objects
            t_AssoCnt_ub = 0
            if currentAssoProb_uint32[i,j] > 0:
              #  LRR and VID objects have an association probability related to the angle 
              #  count all VID objects which have an association probability to the LRR object 
              t_AssoCnt_ub += np.sum( currentAssoProb_uint32[i,:] > 0 )
              #  count all LRR objects which have an association probability to the VID object 
              t_AssoCnt_ub += np.sum( currentAssoProb_uint32[:,j] >= prob1AsoProbLimit_uint32) # FIXME: asymmetric comparison
#               t_AssoCnt_ub += np.sum( currentAssoProb_uint32[:,j] > 0 ) # FIXED: asymmetric comparison
              #  The counter for associatable objects has two entries for the the lrr/vid 
              #  combination, one from scanning the row and one from scanning a column.
              #  So decrement it once.
              if t_AssoCnt_ub > 1:
                #  decrement counter once, at least its value left is 1 
                t_AssoCnt_ub -= 1
                #  norming associatable object counter 
                t_CntNormed_f = FLOAT32_1 / np.float32(t_AssoCnt_ub)
              else:
                #  error, must at least be 2 
                t_CntNormed_f = FLOAT32_1
                # DEBUG
                # sys.stderr.write('Error: counter value is %d, should be at least 2!\n' %t_AssoCnt_ub)
            else:
              #  not associated in angle [[and dx]], so return zero 
              #  norming associatable object counter 
              t_CntNormed_f = FLOAT32_1
            # save result
            counterAssoProb[i,j] = t_CntNormed_f
            t_CntNormed_uw = float2fixWithoutRounding( t_CntNormed_f, norms['N_prob1UW_uw'] )
            # BUG: input array is modified inside loop (see the original algorithm)
            currentAssoProb_uint32[i,j] = fixMultiply( currentAssoProb_uint32[i,j], t_CntNormed_uw, norms['N_prob1UW_uw'] )
  return counterAssoProb

def calcOcclusion(radarTracks, angleAssoProb_uint32, n, params, LRR_INVALID_INDEX=255):
  """ radarTracks: OrderedDict
  """
  MAX_NO_RADAR_OBJ = len(radarTracks)
  # initialize output
  occlusion = np.zeros_like(angleAssoProb_uint32, dtype=np.bool)
  occluder  = np.empty_like(angleAssoProb_uint32, dtype=np.uint8)
  occluder.fill(LRR_INVALID_INDEX)
  # params
  t_wExistLimit_f    = params.occWExistLimit
  t_wObstacleLimit_f = params.occWObstacleLimit
  t_deltaDxLimit_f   = params.occDeltaDxLimit
  #  calculate occlusion (angle nearly equal, dx close to another dx)
  cols = angleAssoProb_uint32.shape[1]
  for j in xrange(cols):
      # skip occlusion calculation if no object angle matches
      if not np.any(angleAssoProb_uint32[:,j] > 0):
        continue
      #  search the lrr object index with dx minimum of a mobile object 
      t_MobileMinDxIdx_ub = LRR_INVALID_INDEX
      for i, radar in radarTracks.iteritems():
          # skip radar object if not present
          if not radar:
            continue
          #  for all lrr objects 
          #  get wExist and wObstacle and mobile state 
          t_wExist_f     = radar['existProb'][n]
          t_wObstacle_f  = radar['obstacleProb'][n]
          t_Classified_b = not radar['notClassified_b'][n]
          t_Mobile_b     = not radar['stationary_b'][n] and t_Classified_b

          if t_wExist_f > t_wExistLimit_f and (t_Mobile_b or t_wObstacle_f > t_wObstacleLimit_f):
            # occlusion is only evaluated if the occluding object has a very high wExist
            # or has any safe mobile state; otherwise ground reflexes may occlude real objects 
            # additionally it is evaluated, that the object is classified as obstacle 
            if angleAssoProb_uint32[i,j] > 0:
              #  if the angle is nearly the same 
              if t_MobileMinDxIdx_ub < MAX_NO_RADAR_OBJ:
                #  if index found 
                if radar['dx'][n] < radarTracks[t_MobileMinDxIdx_ub]['dx'][n]:
                  #  if dx is smaller, new minimum found 
                    t_MobileMinDxIdx_ub = i
              else:
                #  minimum index not set so far, so initialize it 
                t_MobileMinDxIdx_ub = i
      #  search the lrr object index with dx minimum of a stationary object 
      t_StatMinDxIdx_ub = LRR_INVALID_INDEX
      if t_MobileMinDxIdx_ub >= MAX_NO_RADAR_OBJ:
        #  search only for stationary objects to be occlusion objects if no mobile object could be associated 
        for i, radar in radarTracks.iteritems():
            # skip radar object if not present
            if not radar:
              continue
            #  for all lrr objects 
            #  get wExist and stationary state 
            t_wExist_f  = radar['existProb'][n]
            t_Stat_b    = radar['stationary_b'][n]
            if t_wExist_f > t_wExistLimit_f and t_Stat_b:
              #  occlusion is only evaluated if the occluding object has a very high wExist 
              if angleAssoProb_uint32[i,j] > 0:
                #  if the angle is nearly the same 
                if t_StatMinDxIdx_ub < MAX_NO_RADAR_OBJ:
                  #  if index found 
                  if radar['dx'][n] < radarTracks[t_StatMinDxIdx_ub]['dx'][n]:
                    #  new minimum found 
                    t_StatMinDxIdx_ub = i
                else:
                  #  minimum index not set so far, so initialize it 
                  t_StatMinDxIdx_ub = i
      #  now reset the association probability to zero if an object is occluded 
      if t_MobileMinDxIdx_ub < MAX_NO_RADAR_OBJ or t_StatMinDxIdx_ub < MAX_NO_RADAR_OBJ:
        # save occluding radar object
        occluderIdx = min(t_MobileMinDxIdx_ub, t_StatMinDxIdx_ub)
        #  if an mobile or stationary object object was found that could be associated to the current video object 
        for i, radar in radarTracks.iteritems():
            # skip radar object if not present
            if not radar:
              continue
            #  for all lrr objects 
            if angleAssoProb_uint32[i,j] > 0:
              #  if the angle is nearly the same 
              if i != t_MobileMinDxIdx_ub and  i != t_StatMinDxIdx_ub:
                #  object is not the found closest and so it may be occluded 
                #  now decide if a mobile object is the occluding object and so may occlude every other object 
                #  or if a stationary object is the occluding object and so may occlude only other staionary objects 
                t_Stat_b = radar['stationary_b'][n]
                if t_MobileMinDxIdx_ub < MAX_NO_RADAR_OBJ or  (t_StatMinDxIdx_ub < MAX_NO_RADAR_OBJ and t_Stat_b):
                  #  decision is made positively 
                  #  at this point only one of the indices is set valid and so smaller than LRR_INVALID_INDEX 
                  #  which is the maximum value; so the minimum of both indices is the set one
                  t_deltaDx_f  = radar['dx'][n] - radarTracks[occluderIdx]['dx'][n]
                  if t_deltaDx_f < t_deltaDxLimit_f:
                    #  objects are very dx close 
                    #  set data temporarily to association probability 
                    occlusion[i,j] = True
                    occluder[i,j] = occluderIdx
  return occlusion, occluder

def calcFilterAssoProb(currentAssoProb_uint32, filteredAssoProbInit, radarTracks, videoTracks, masks, params):
  """ radarTracks, videoTracks: OrderedDict
  """
  assert currentAssoProb_uint32.shape == masks.shape
  N,rows,cols = masks.shape
  assert len(radarTracks), len(videoTracks) == filteredAssoProbInit.shape == (rows,cols)

  # init filtered probabilities
  filteredAssoProb_uint32 = np.zeros_like(currentAssoProb_uint32)
  # params
  t_wBestAssoLimit_f    = params.wBestAssoLimit
  t_IncreaseWeightPar_f = params.fak2AsoFiltIncreaseConst
  t_DecreaseWeightPar_f = params.fak2AsoFiltDecreaseConst
  t_dxMinVid_f          = params.dExtFusObjMinDx
  t_prob1AsoProbInit_ul = float2fixWithoutRounding( params.prob1AsoProbInit, norms['N_prob1UW_uw'] )

  # initial state
  filteredAssoProb_uint32[0,...] = float2fixWithoutRounding( filteredAssoProbInit, norms['N_prob1UW_uw'] )

  # time loop from 2nd time step
  for n in xrange(1,N):

      # object loop
      for i, radar in radarTracks.iteritems():
          # skip radar object if not present
          if not radar:
            continue
          t_dxLrr_f      = radar['dx'][n]
          t_LrrStopped_b = radar['stopped_b'][n]
          t_LrrHist_b    = radar['historical_b'][n]
          t_LrrMeas_b    = radar['measured_b'][n]

          for j, video in videoTracks.iteritems():

              if masks[n,i,j]:
                #  lrr and vid object are both valid 
                t_VidHist_b = video['historical_b'][n]
                if t_LrrHist_b and t_VidHist_b:
                  #  both objects are historical, filter value has been initialized before 
                  t_VidMeas_b = video['measured_b'][n]
                  if t_LrrMeas_b and t_VidMeas_b:
                    #  both objects are measured, otherwise no change of association probability 
                    t_CurrentAssoProb_f  = fix2float( currentAssoProb_uint32[n,i,j],    norms['N_prob1UW_uw'] )
                    t_FilteredAssoProb_f = fix2float( filteredAssoProb_uint32[n-1,i,j], norms['N_prob1UW_uw'] )
                    #  initialially set the filter constants to its parameter values 
                    t_IncreaseWeight_f = t_IncreaseWeightPar_f
                    t_DecreaseWeight_f = t_DecreaseWeightPar_f
                    #  now set the filter constants adapted to special situations 
                    #  First: very close range: video dx may not be correct or unambiguous, so 
                    #  try to hold old associations and associate new objects slowly
                    #  Second: associations to stopped objects are hold also, by this 
                    #  the association probability to farer stopped objects may not increase
                    #  relatively to the old associated object; it is limited if the association fits well
                    if t_dxLrr_f < t_dxMinVid_f or (t_CurrentAssoProb_f < t_wBestAssoLimit_f and t_LrrStopped_b):
                      #  freeze association; later freeze may be melt partially a little bit 
                      t_IncreaseWeight_f = FLOAT32_1
                      t_DecreaseWeight_f = FLOAT32_1
                    #  filter data asymmetrically 
                    if t_CurrentAssoProb_f > t_FilteredAssoProb_f:
                      #  current association probability is greater, increase faster 
                      t_FilteredAssoProb_f = t_IncreaseWeight_f * t_FilteredAssoProb_f + (FLOAT32_1-t_IncreaseWeight_f) * t_CurrentAssoProb_f
                    else:
                      #  current association probability is lower, increase slower 
                      t_FilteredAssoProb_f = t_DecreaseWeight_f * t_FilteredAssoProb_f + (FLOAT32_1-t_DecreaseWeight_f)* t_CurrentAssoProb_f
                    t_FilteredAssoProb_uint32 = float2fix(t_FilteredAssoProb_f, norms['N_prob1UW_uw'])
                  else:
                    #  do nothing 
                    #  one object was not measured, so let association probability unchanged 
                    t_FilteredAssoProb_uint32 = filteredAssoProb_uint32[n-1,i,j]
                else:
                  #  one or both objects are new, filter value has to be initialized with current value limited by a maximum 
                  t_FilteredAssoProb_uint32 = min(currentAssoProb_uint32[n,i,j], t_prob1AsoProbInit_ul)
              else:
                #  lrr or vid object is not valid 
                #  initialize filtered association probability 
                t_FilteredAssoProb_uint32 = UINT32_0

              #  set new filtered value
              filteredAssoProb_uint32[n,i,j] = t_FilteredAssoProb_uint32
              del t_FilteredAssoProb_uint32 # safety

  # convert to float representation
  filteredAssoProb = fix2float( filteredAssoProb_uint32, norms['N_prob1UW_uw'] )
  return filteredAssoProb
