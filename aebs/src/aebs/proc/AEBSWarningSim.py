"""
Calculations for simplified AEBS algorithms with the following three-phase
cascade, illustrated as an acceleration-time function:

 a ^
   |
   +--------*****************------------------------------------------> t
   |              t_w       *
   |                        *
   |                        *
   |                    a_p ***********************
   |                                   t_p        *
   |                                              *
   |                                              *
   |                                          a_e *******************

"""

import numpy
import scipy.integrate

from measparser import signalproc


def calcAEBSDeceleration(dx_obj, vx_obj, stat, vx_ego, t_w=0.6, t_p=0.8, a_p=3.0, a_max=10.0, v_red=0, d_e=2.5, vx_ego_min=2, vx_oncoming_tolerance=1.0):
  """
  Calculate the necessary decceleration a_e for the given object with the three-phase cascade to avoid the accident.

  :Parameters:
    dx_obj : numpy.ndarray
      Relative distance values of the actual obstacle. [m]
    vx_obj : numpy.ndarray
      Relative speed values of the actual obstacle. [m/s]
    vx_ego : numpy.ndarray
      Ego vehicle speed. [m/s]
    stat : numpy.ndarray
      Object is stationary flag [-]
    t_w : float
      Duration of (acoustical, visual etc.) {W}arning phase. [s]
    t_p : float
      Duration of {P}artial braking phase. [s]
    a_p : float 
      Deceleration in the {P}artial braking period. Positive value means negative acceleration. [m/s^2]
    a_max : float
      Maximum allowed deceleration (during the emergency braking). [m/s^2]
    v_red : float
      Minimum required speed reduction (during the whole intervention). [m/s]
      SET TO NONE IF YOU WANT AVOIDANCE FOR STATIONARY VEHICLES!! 
      SET TO ZERO IF YOU WANT KB AEBS LOGIC: avoidance till 50 km/h, then mitigation - 35km/h reduction at 80 km/h
    d_e : float
      Security distance between the obstacle and the ego vehicle at the end of the {E}mergency braking phase. [m]
    vx_ego_min : float
      Minimal ego vehicle speed for calculation. [m/s]
    vx_oncoming_tolerance: float
      Tolerance speed of oncoming filtering [m/s]
  
  :ReturnType: numpy.ndarray
  :Return:
    Required deceleration in the emergency braking phase to avoid collision. [m/s^2]
  """
  
  regu_viol = numpy.zeros(dx_obj.shape, dtype=numpy.bool)  # Flag signalling if the regulation has been violated with the parameters
  regu_viol[:] = False
  
  if ((t_p < 0.8) or ((t_w + t_p) < 1.4) or (a_p >= 4.0) ):
    regu_viol[:] = True
  
  s_w = -vx_obj * t_w
  s_p = -vx_obj * t_p - (a_p * (t_p ** 2.0) / 2.0)
    
  TTC_em = (dx_obj - s_w - s_p) / (-vx_obj - a_p * t_p)   # TTC at the beginning of emergency braking
  TTC_em = numpy.where(TTC_em < 0.0, 0.0, TTC_em)
  TTC_em = numpy.where(TTC_em > 10.0, 10.0, TTC_em)
  
  if v_red == None :                                 # Separating Avoidance and Mitigation by speed reduction parameter
    s_e =  dx_obj - d_e - s_w - s_p                  # remaining distance available for emergency braking
    a_e =(-vx_obj - a_p * t_p) ** 2.0 / (2.0 * s_e)  # required deceleration in the emergency braking phase
  
  elif v_red == 0:                                   # KB AEBS cascade with mitigation and avoidance based on relative speed: 
    mitigate = numpy.where(numpy.logical_and(stat, vx_ego > 50/3.6), True, False)  # Mitigation for stationary objects when ego speed is bigger than 50 km/h
    v_red_KB = numpy.where(mitigate, (50/3.6 - (vx_ego - 50/3.6) / 2), vx_ego)     # Mitigation speed reduction calculated from a look-up table
    s_e =  numpy.where(mitigate,                     # remaining distance available for emergency braking
                      dx_obj - s_w - s_p,            # Mitigation
                      dx_obj - d_e - s_w - s_p )     # Avoidance   
                      
    a_e =  numpy.where(mitigate,                     # required deceleration in the emergency braking phase
                  ((-vx_obj - a_p * t_p) ** 2.0 - (-vx_obj - v_red_KB) ** 2.0) / (2.0 * s_e),   # Mitigation
                  (-vx_obj - a_p * t_p) ** 2.0 / (2.0 * s_e) )                                  # Avoidance   
   
  else:                                              # Mitigation: 
    mitigate = numpy.where(numpy.logical_and(stat, vx_ego > v_red), True, False)  # for stationary objects when speed is high enough
    s_e =  numpy.where(mitigate,                     # remaining distance available for emergency braking
                      dx_obj - s_w - s_p,            # Mitigation
                      dx_obj - d_e - s_w - s_p )     # Avoidance   
                      
    a_e =  numpy.where(mitigate,                     # required deceleration in the emergency braking phase
                  ((-vx_obj - a_p * t_p) ** 2.0 - (-vx_obj - v_red) ** 2.0) / (2.0 * s_e),   # Mitigation
                  (-vx_obj - a_p * t_p) ** 2.0 / (2.0 * s_e) )                               # Avoidance   
                  
  a_e = numpy.where(s_e > 0.0,   a_e, a_max)       # mark unhandleable situations (collision already in warning phase)
  a_e = numpy.where(a_e < a_max, a_e, a_max)       # mark unhandleable situations (unrealizable brake request)
  a_e = numpy.where(numpy.logical_and(dx_obj > 0.0, vx_obj < 0.0), a_e, 0.0)  # ignore vx>0 and dx<0
  
  if vx_ego is not None:
    a_e = numpy.where(vx_ego > vx_ego_min, a_e, 0.0)  # ignore slow-speed situations
    a_e = numpy.where(-1 * vx_obj < vx_ego + vx_oncoming_tolerance, a_e, 0.0)  # ignore oncoming situations
  
  TTC_em = numpy.where(a_e > 1.0, TTC_em, 0.0)
  regu_viol = numpy.where(TTC_em > 3.0, True, regu_viol)
  
  return a_e, regu_viol,TTC_em

def calcAEBSActivity(a_e, a_e_threshold=5.0):
  """
  :Parameters:
    a_e : numpy.ndarray
      Required deceleration in the emergency braking phase to avoid collision. [m/s^2]
    a_e_threshold: float
      Deceleration threshold which causes warning. [m/s^2]
  
  :ReturnType: numpy.ndarray
  :Return:
    Boolean values indicating the AEBS acitivity.
  """
  activity = (a_e >= a_e_threshold)
  return activity


def calcAEBSSpeedReduction(dx_obj, vx_ego, t_w=0.6, t_p=0.8, a_p=3.0, a_e=5.0):
  """
  Calculate the possible speed reduction for stationary obstacles with the
  three-phase cascade, and indicate whether collision occurred.
  
  TODO: Extend the algorithm for moving objects.
  
  :Parameters:
    dx_obj : float
      Relative distance value of the actual obstacle. [m]
    vx_ego : float
      Ego vehicle speed. [m/s]
    t_w : float
      Duration of (acoustical, visual etc.) {W}arning phase. [s]
    t_p : float
      Duration of {P}artial braking phase. [s]
    a_p : float 
      Deceleration in the {P}artial braking period.
      Positive value means negative acceleration. [m/s^2]
    a_e : float
      Deceleration in the {E}mergency braking period.
      Positive value means negative acceleration. [m/s^2]
  
  :ReturnType: tuple
  :Return:
    Possible speed reduction [m/s] and collision flag [-].
  """
  assert dx_obj >= 0.0 and vx_ego >= 0.0 and t_w >= 0.0 and t_p >= 0.0 and \
         a_p > 0.0 and a_e > 0.0, 'invalid parameter'
  dx_obj_w = dx_obj - vx_ego * t_w
  if dx_obj_w > 0.0:
    # entering into the partial braking phase
    dx_obj_p = dx_obj_w - vx_ego * t_p + ((a_p * t_p**2) / 2.0)
    if dx_obj_p > 0.0:
      # no collision in the partial braking phase
      vx_ego_p = vx_ego - a_p * t_p
      if vx_ego_p > 0.0:
        # entering into the emergency braking phase
        if vx_ego_p**2 - 2.0 * a_e * dx_obj_p >= 0:
          # collision in the emergency braking phase
          time2collision = \
            (-vx_ego_p + numpy.sqrt(vx_ego_p**2 - 2.0 * a_e * dx_obj_p)) / -a_e
          vx_ego_e = vx_ego_p - a_e * time2collision
          vx_ego_reduction = vx_ego - vx_ego_e
        else:
          # stopped in the emergency braking phase
          vx_ego_reduction = vx_ego
      else:
        # stopped in the partial braking phase
        vx_ego_reduction = vx_ego
    else:
      # collision in the partial braking phase
      time2collision = \
        (-vx_ego + numpy.sqrt(vx_ego**2 - 2.0 * a_p * dx_obj_w)) / -a_p
      vx_ego_reduction = a_p * time2collision
  else:
    # collision in the warning phase
    vx_ego_reduction = 0.0
  collision = vx_ego_reduction < vx_ego
  return vx_ego_reduction, collision


def aebsAccelProfile(t, t_w=0.6, t_p=0.8, a_p=-3.0, a_e=-5.5):
  if t < t_w:
    a = 0.0
  elif t < t_w + t_p:
    a = a_p
  else:
    a = a_e
  return a

def calcSpeedReduction(dx_obj, vx_obj, vx_ego, a_func=aebsAccelProfile,
                       length=20.0, step=0.01, drawplot=False):
  """
  Calculate the possible speed reduction with a function-given cascade.
  
  :Parameters:
    dx_obj : float
      Relative distance value of the actual obstacle. [m]
    vx_obj : float
      Object's relative speed. [m/s]
    vx_ego : float
      Ego vehicle speed. [m/s]
    a_func : callable
      Function of acceleration profile versus time. Accepts one parameter, 
      time as float and returns acceleration as float
    length : float
      Length in seconds while the cascade should be investigated
      Default value is 20.0s
    step : float
      Step of numeric integration, this has influence on the accuracy
      Default value is 0.01s
  """
  t = numpy.arange(0.0, length, step)
  vect_afunc = numpy.vectorize(a_func)
  a = vect_afunc(t)
  
  vx_obj_abs = vx_obj + vx_ego
  
  v_e = vx_ego + scipy.integrate.cumtrapz(a, dx=step, initial=0)
  v = v_e - vx_obj_abs
  v = numpy.where(v < 0.0, 0.0, v)
  stopindex = numpy.searchsorted(-v, 0.0) - 1
  v_e = numpy.where(v == 0, vx_obj_abs, v_e)
  
  d = dx_obj - scipy.integrate.cumtrapz(v, dx=step, initial=0) 
  d = numpy.where(d < 0.0, 0.0, d)
  colindex = numpy.searchsorted(-d, 0.0) - 1
  
  vx_ego_reduction = vx_ego - v_e[colindex]
  collision = colindex < stopindex
  
  if drawplot:  
    import pylab
    fig = pylab.figure()
    ax1 = fig.add_subplot(411)
    ax1.set_ylabel("a [m/ss]")
    ax1.plot(t, a)
    ax = fig.add_subplot(412, sharex=ax1)
    ax.set_ylabel("v [m/s]")
    ax.plot(t, v_e)
    ax.axhline(vx_obj_abs, color="g")
    if colindex < stopindex:
      ax.plot([t[colindex]],[v_e[colindex]], "ro")
      ax.annotate('Collision! vreduc = %5.2f km/h' %
                  ((vx_ego - v_e[colindex]) * 3.6),
                  xy=(t[colindex], v_e[colindex]),  xycoords='data',
                  xytext=(5, 10), textcoords='offset points')
    else:                    
      ax.plot([t[stopindex]],[v_e[stopindex]], "go")
      ax.annotate('Obj speed reached! vreduc = %5.2f km/h' %
                  ((vx_ego - v_e[colindex]) * 3.6), 
                  xy=(t[stopindex], v_e[stopindex]),  xycoords='data',
                  xytext=(5, 10), textcoords='offset points')
    ax = fig.add_subplot(413, sharex=ax1)
    ax.set_ylabel("drel [m]")
    ax.plot(t, d)
    ax.plot([t[stopindex]],[d[stopindex]], "go")
    ax.annotate('distance = %5.2f m' % (d[stopindex]),
                xy=(t[stopindex], d[stopindex]),  xycoords='data',
                xytext=(5, 10), textcoords='offset points')
    ax = fig.add_subplot(414, sharex=ax1)
    with numpy.errstate(divide='ignore', invalid='ignore'):
      ttc = numpy.where(d > 0.0, d/v, 0.0)
    ttc[ttc.argmin():] = 0.0
    ax.set_ylabel("ttc [s]")
    ax.plot(t, ttc)
    pylab.show()
  
  return vx_ego_reduction, collision


def calcDriverActive(
  Time, GPPos, pBrake, BPAct, alpSteeringWheel, DirIndL, DirIndR,
  DMTGPPosMin = 20.0, 
  DMTAbsMinEngGPPosGradient = 50.0,
  DMTAbsMinDisEngGPPosGradient = -100.0,
  DMTpdtBrake = 10.0,
  DMTalpDtSteeringWheelMax = 1.22):
  """
  DMT: Driver Monitoring calculates the Driver active flag based on readings of
  the different actuators of the ego vehicle.
  
  :Parameters:
    Time : ndarray
      time base for all signals [s]
    GPPos : ndarray
      Accelerator pedal position, [%]
    pBrake : ndarray
      Brake pedal position [%]
    BPAct : ndarray
      Brake pedal active flag, bool
    alpSteeringWheel : ndarray
      Steering wheel angle, rad
    DirIndL : ndarray
      Indicator left, bool
    DirIndR : ndarray
      Indicator right, bool
    
    DMTGPPosMin : float
      Minimal Accelerator pedal position
    DMTAbsMinEngGPPosGradient : float
      Minimal gradient for engaging accelerator pedal
    DMTAbsMinDisEngGPPosGradient : float
      Minimal gradient for disengaging accelerator pedal
    DMTpdtBrake : float
      Minimal gradient for brakes
    DMTalpDtSteeringWheelMax : float
      Minimal gradient for steering wheel
      
  :ReturnType: tupple of numpy.ndarrays
  :Return:
    DriverActive : Driver activity flag
    DriverActiveGP, DriverActiveBrake, DriverActiveSteering, DriverActiveDirInd :
    Activity flags for sub-activities
  """
  # derivates of actuator signals
  GPdtPos = signalproc.backwardderiv(GPPos, Time)
  pDtBrake = signalproc.backwardderiv(pBrake, Time)
  alpDtSteeringWheel =  signalproc.backwardderiv(alpSteeringWheel, Time)
  
  # calculation of driver activity
  DriverActiveGP = (
    (GPPos > DMTGPPosMin) & 
    (
      (GPdtPos > DMTAbsMinEngGPPosGradient) | 
      (GPdtPos < DMTAbsMinDisEngGPPosGradient)
    ))
  DriverActiveBrake = ((BPAct == 1) & (pDtBrake > DMTpdtBrake)) 
  DriverActiveSteering = \
    numpy.absolute(alpDtSteeringWheel) > DMTalpDtSteeringWheelMax
  DriverActiveDirInd = (
    (signalproc.backwarddiff(DirIndL) > 0) | 
    (signalproc.backwarddiff(DirIndR) > 0))
  DriverActive = numpy.asarray(
    (
      DriverActiveGP | 
      DriverActiveBrake | 
      DriverActiveSteering | 
      DriverActiveDirInd), 
    dtype=numpy.int32)
  
  # timer to hold driver active flag
  Indices = numpy.arange(len(Time))
  Endmask = signalproc.backwarddiff(DriverActive) < 0
  Falltimes = Time[Endmask]
  Fallindices = Indices[Endmask]
  Endindices = numpy.searchsorted(Time, Falltimes + 5.0)
  for Fall, End in zip(Fallindices, Endindices):
    if End > len(DriverActive) - 1:
      DriverActive[Fall : -1] = 1
    else:
      DriverActive[Fall : End] = 1

  return DriverActive, DriverActiveGP, DriverActiveBrake, \
         DriverActiveSteering, DriverActiveDirInd