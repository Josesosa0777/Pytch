import sys

import numpy

import datavis
import measparser
import interface

DefParam = interface.NullParam

Xdefault = numpy.array((0, 30, 80, 250))

def default(Y0, Y123, X=Xdefault):
  Y = numpy.array([Y0, 
                   Y123, 
                   Y123, 
                   Y123])
  return Y, X

def rlc(Y0, Y123, O123, X=Xdefault):
  Y = numpy.array([Y0, 
                   Y123 + O123, 
                   Y123 + O123, 
                   Y123 + O123])
  return Y, X

def po(Y0, Y123, O1, O23, O123, X=Xdefault):  
  Y = numpy.array([Y0, 
                   Y123 + O1  + O123, 
                   Y123 + O23 + O123, 
                   Y123 + O23 + O123])
  return Y, X

def steer(Y0, Y123, O0123, X=Xdefault):
  Y = numpy.array([Y0   + O0123, 
                   Y123 + O0123, 
                   Y123 + O0123, 
                   Y123 + O0123])
  return Y, X

def maxRlcPo(Y0, Y123, Opo1, Opo23, Opo123, Orlc123, X=Xdefault):
  O1  = numpy.sign(Opo123) * max(abs(Opo1  + Opo123), abs(Orlc123))
  O23 = numpy.sign(Opo123) * max(abs(Opo23 + Opo123), abs(Orlc123))
  Y = numpy.array([Y0, 
                   Y123 + O1, 
                   Y123 + O23, 
                   Y123 + O23])
  return Y, X

Lines = [{'Right0':    ('ECU',      'padsit_par_a.ROADRSOEgoLaneRightPolyA0'),
          'Right1':    ('ECU',      'padsit_par_a.ROADRSOLeftLaneRightPolyA0'),
          'Right2':    ('ECU',      'padsit_par_a.ROADRSOUncorrLeftLaneRightPolyA'),
          'Left0':     ('ECU',      'padsit_par_a.ROADRSOEgoLaneLeftPolyA0'),
          'Left1':     ('ECU',      'padsit_par_a.ROADRSORightLaneLeftPolyA0'),
          'Left2':     ('ECU',      'padsit_par_a.ROADRSOUncorrRightLaneLeftPolyA'),
          'CurveLane': ('ECU',      'evi.MovementData_T20.kapCurvTraj'),
          'CurveEgo':  ('ECU',      'dcp.kapCourse')},
         
         {'Right0':    ('MRR1plus', 'padsit_x_par_a.PCCCROADRSOEgoLaneLeftPolyA0'),
          'Right1':    ('MRR1plus', 'padsit_x_par_a.PCCCROADRSORightLaneLeftPolyA0'),
          'Right2':    ('MRR1plus', 'padsit_x_par_a.PCCCROADRSOUncorrRightLaneLeftPolyA0'),
          'Left0':     ('MRR1plus', 'padsit_x_par_a.PCCCROADRSOEgoLaneRightPolyA0'),
          'Left1':     ('MRR1plus', 'padsit_x_par_a.PCCCROADRSOLeftLaneRightPolyA0'),
          'Left2':     ('MRR1plus', 'padsit_x_par_a.PCCCROADRSOUncorrLeftLaneRightPolyA0'),
          'CurveLane': ('MRR1plus', 'evi.MovementData_T20.kapCurvTraj'),
          'CurveEgo':  ('MRR1plus', 'dcp.kapCourse')},

         {'Right0':    ('RadarFC', 'padsit_x_par_a.PCCCROADRSOEgoLaneLeftPolyA0'),
          'Right1':    ('RadarFC', 'padsit_x_par_a.PCCCROADRSORightLaneLeftPolyA0'),
          'Right2':    ('RadarFC', 'padsit_x_par_a.PCCCROADRSOUncorrRightLaneLeftPolyA0'),
          'Left0':     ('RadarFC', 'padsit_x_par_a.PCCCROADRSOEgoLaneRightPolyA0'),
          'Left1':     ('RadarFC', 'padsit_x_par_a.PCCCROADRSOLeftLaneRightPolyA0'),
          'Left2':     ('RadarFC', 'padsit_x_par_a.PCCCROADRSOUncorrLeftLaneRightPolyA0'),
          'CurveLane': ('RadarFC', 'evi.MovementData_T20.kapCurvTraj'),
          'CurveEgo':  ('RadarFC', 'dcp.kapCourse')}]
          
Offsets = [{'WidthMinHalf':        ('ECU', 'ats.Course_TC.dyLaneWidthMinHalf'),
            'AdaptDefMinPO':       ('ECU', 'ats.Course_TC.dyLCAdaptDefMinPO'),
            'AdaptDefMaxPO':       ('ECU', 'ats.Course_TC.dyLCAdaptDefMaxPO'),
            'WidthAdaptPO':        ('ECU', 'ats.Course_TC.dyLaneWidthAdaptPO'),
            'WidthInitHalfLeft':   ('ECU', 'ats.Course_TC.dyLaneWidthInitHalfL'),
            'WidthInitHalfRight':  ('ECU', 'ats.Course_TC.dyLaneWidthInitHalfR'),
            'WidthAdaptRLCLeft':   ('ECU', 'ats.Course_TC.dyLaneWidthAdaptRLCLeft'),
            'WidthAdaptRLCRight':  ('ECU', 'ats.Course_TC.dyLaneWidthAdaptRLCRight'),
            'WidthSteerAdaptLeft': ('ECU', 'ats.Course_TC.dyLaneWidthSteerAdaptLeft'),
            'WidthSteerAdaptRight':('ECU', 'ats.Course_TC.dyLaneWidthSteerAdaptRight')}]
  
class cTrackNavigator(interface.iView):
  @classmethod
  def view(cls, Param=DefParam):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)
    
    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)
    
    try:
      Params = interface.Source.selectSignalGroup(Lines)
    except measparser.signalgroup.SignalGroupError, Error:
      print >> sys.stderr, 'Tracks are not added to the TrackNavigator'
      print >> sys.stderr, Error.message
    else:
      Tracks = (('Ego',  'CurveEgo',  (('c', ('Left0', 'Right0')),)),
                ('Lane', 'CurveLane', (('r', ('Left0', 'Right0')),
                                       ('g', ('Left1', 'Right1')),
                                       ('b', ('Left2', 'Right2')))))
      for TrackName, CurveAlias, Lanes in Tracks:
        TrackTime, Curve = interface.Source.getSignalFromSignalGroup(Params, CurveAlias)
        with numpy.errstate(divide='ignore'):
          R = numpy.reciprocal(Curve)
        for Color, Aliases in Lanes:
          for Alias in Aliases:
            Track = TN.addTrack(TrackName, TrackTime, color=Color)
            Time, Value = interface.Source.getSignalFromSignalGroup(Params, Alias)
            FuncName = Track.addFunc(datavis.TrackNavigator.circle, LengthMax=TN.LengthMax)
            Track.addParam(FuncName, 'R',      TrackTime,  R)    
            Track.addParam(FuncName, 'Offset', Time,       Value)  
      
      try:
        Params = interface.Source.selectSignalGroup(Offsets)
      except measparser.signalgroup.SignalGroupError, Error:
        print >> sys.stderr, 'Lanes are not added to the TrackNavigator'
        print >> sys.stderr, Error.message
      else:
        FuncsLeft =  ((rlc,      (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfLeft'), 
                                  ('O123',    'WidthAdaptRLCLeft'))),

                      (po,       (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfLeft'), 
                                  ('O1',      'AdaptDefMinPO'), 
                                  ('O23',     'AdaptDefMaxPO'), 
                                  ('O123',    'WidthAdaptPO'))),

                      (steer,    (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfLeft'), 
                                  ('O0123',   'WidthSteerAdaptLeft'))),

                      (maxRlcPo, (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfLeft'), 
                                  ('Opo1',    'AdaptDefMinPO'), 
                                  ('Opo23',   'AdaptDefMaxPO'), 
                                  ('Opo123',  'WidthAdaptPO'), 
                                  ('Orlc123', 'WidthAdaptRLCLeft'))),

                      (default,  (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfLeft'))))
                                   
        FuncsRight = ((rlc,      (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfRight'), 
                                  ('O123',    'WidthAdaptRLCRight'))),
                                  
                      (po,       (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfRight'), 
                                  ('O1',      'AdaptDefMinPO'), 
                                  ('O23',     'AdaptDefMaxPO'), 
                                  ('O123',    'WidthAdaptPO'))),

                      (steer,    (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfRight'), 
                                  ('O0123',   'WidthSteerAdaptRight'))),

                      (maxRlcPo, (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfRight'), 
                                  ('Opo1',    'AdaptDefMinPO'), 
                                  ('Opo23',   'AdaptDefMaxPO'), 
                                  ('Opo123',  'WidthAdaptPO'), 
                                  ('Orlc123', 'WidthAdaptRLCLeft'))),

                      (default,  (('Y0',      'WidthMinHalf'), 
                                  ('Y123',    'WidthInitHalfRight'))))

        GainsLeft  = {'AdaptDefMinPO':         0.5, 
                      'AdaptDefMaxPO':         0.5}
        GainsRight = {'AdaptDefMinPO':        -0.5, 
                      'AdaptDefMaxPO':        -0.5, 
                      'WidthMinHalf':         -1, 
                      'WidthInitHalfLeft':    -1, 
                      'WidthAdaptRLCLeft':    -1, 
                      'WidthAdaptPO':         -1, 
                      'WidthSteerAdaptLeft':  -1, 
                      'WidthInitHalfRight':   -1, 
                      'WidthAdaptRLCRight':   -1, 
                      'WidthSteerAdaptRight': -1}
        
        X = numpy.array((0, 30, 80, 250))
        TrackTime, Value = interface.Source.getSignalFromSignalGroup(Params, 'WidthMinHalf')
        for Funcs, Gains in ((FuncsLeft, GainsLeft), (FuncsRight, GainsRight)):
          Track = TN.addTrack('EgoLane', TrackTime, color='m')
          for func, Aliases in Funcs:
            FuncName = Track.addFunc(func, X=X)
            for ParName, Alias in Aliases:
              Time, Value = interface.Source.getSignalFromSignalGroup(Params, Alias, Gains)
              Track.addParam(FuncName, ParName, Time, Value)
    
    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(Status)
      for Object in Objects:
        TN.addObject(Time, Object)

    interface.Sync.addClient(TN)
    pass
    
