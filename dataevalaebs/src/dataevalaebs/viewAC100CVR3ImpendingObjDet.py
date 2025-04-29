import datavis
import interface
import numpy

FUS_OBJ_NUM = 32
N_AC100_TR = 10

CVR3Color = 'g'
AC100Color1 = 'b'
AC100Color2 = 'c'
AC100Color3 = 'm'

CVR3SignalTemplates = ('dxv'          ,
                       'dyv'          ,
                       'vxv'          ,
                       'vyv'          ,
                       'wExistProb'   ,
                       'wGroundReflex',
                       'wObstacle'    ,
                       'vVarYv'       ,
                       'CntAlive'     ,
                       'b.b.Stand_b'  ,
                       'b.b.Drive_b'  ,
                       'Handle'
                       )

CVR3DeviceName = 'MRR1plus'

AC100SignalTemplates = ('range'                 ,
                        'uncorrected_angle'     ,
                        'power'                 ,
                        'credibility'           ,
                        'internal_track_index'  ,
                        'track_selection_status',
                        'CW_track'              ,
                        'acc_track_info'
                        )

CVR3SignalGroups = {}
AC100SignalGroups = {}

for index in xrange(FUS_OBJ_NUM):
  for signaltemplate in CVR3SignalTemplates:
    CVR3SignalGroups['fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate)] = (CVR3DeviceName, 'fus.ObjData_TC.FusObj.i%s.%s' % (index, signaltemplate))
CVR3SignalGroups = [CVR3SignalGroups, ]

for index in xrange(FUS_OBJ_NUM):
  for signaltemplate in AC100SignalTemplates:
    AC100SignalGroups['tr%s_%s' % (index, signaltemplate)] = ('Tracks', 'tr%s_%s' % (index, signaltemplate))
AC100SignalGroups['cm_collision_warning'] = ('General_radar_status', 'cm_collision_warning')
AC100SignalGroups['cm_deceleration_demand'] = ('General_radar_status', 'cm_deceleration_demand')
AC100SignalGroups = [AC100SignalGroups, ]

VehVelSignalGroups = [{'evi.General_T20.vxvRef': ('MRR1plus', 'evi.General_T20.vxvRef'),
                       }, ]

# module parameter class creation
class cParameter(interface.iParameter):
  def __init__(self, CVR3idx, AC100idx, ObjStance):
    self.CVR3idx = CVR3idx # CVR3 FUS object ID
    self.AC100idx = AC100idx # AC100 "outer" track index
    self.ObjStance = ObjStance
    self.genKeys()
    pass
  
# instantiation of module parameters
StatCVR3ObjID00 = cParameter(0, 0, 'Stationary')
StatCVR3ObjID01 = cParameter(1, 0, 'Stationary')
StatCVR3ObjID02 = cParameter(2, 0, 'Stationary')
StatCVR3ObjID03 = cParameter(3, 0, 'Stationary')
StatCVR3ObjID04 = cParameter(4, 0, 'Stationary')
StatCVR3ObjID05 = cParameter(5, 0, 'Stationary')
StatCVR3ObjID06 = cParameter(6, 0, 'Stationary')
StatCVR3ObjID07 = cParameter(7, 0, 'Stationary')
StatCVR3ObjID08 = cParameter(8, 0, 'Stationary')
StatCVR3ObjID09 = cParameter(9, 0, 'Stationary')
StatCVR3ObjID10 = cParameter(10, 0, 'Stationary')
StatCVR3ObjID11 = cParameter(11, 0, 'Stationary')
StatCVR3ObjID12 = cParameter(12, 0, 'Stationary')
StatCVR3ObjID13 = cParameter(13, 0, 'Stationary')
StatCVR3ObjID14 = cParameter(14, 0, 'Stationary')
StatCVR3ObjID15 = cParameter(15, 0, 'Stationary')
StatCVR3ObjID16 = cParameter(16, 0, 'Stationary')
StatCVR3ObjID17 = cParameter(17, 0, 'Stationary')
StatCVR3ObjID18 = cParameter(18, 0, 'Stationary')
StatCVR3ObjID19 = cParameter(19, 0, 'Stationary')
StatCVR3ObjID20 = cParameter(20, 0, 'Stationary')
StatCVR3ObjID21 = cParameter(21, 0, 'Stationary')
StatCVR3ObjID22 = cParameter(22, 0, 'Stationary')
StatCVR3ObjID23 = cParameter(23, 0, 'Stationary')
StatCVR3ObjID24 = cParameter(24, 0, 'Stationary')
StatCVR3ObjID25 = cParameter(25, 0, 'Stationary')
StatCVR3ObjID26 = cParameter(26, 0, 'Stationary')
StatCVR3ObjID27 = cParameter(27, 0, 'Stationary')
StatCVR3ObjID28 = cParameter(28, 0, 'Stationary')
StatCVR3ObjID29 = cParameter(29, 0, 'Stationary')
StatCVR3ObjID30 = cParameter(30, 0, 'Stationary')
StatCVR3ObjID31 = cParameter(31, 0, 'Stationary')
MovCVR3ObjID00 = cParameter(0, 0, 'Moving')
MovCVR3ObjID01 = cParameter(1, 0, 'Moving')
MovCVR3ObjID02 = cParameter(2, 0, 'Moving')
MovCVR3ObjID03 = cParameter(3, 0, 'Moving')
MovCVR3ObjID04 = cParameter(4, 0, 'Moving')
MovCVR3ObjID05 = cParameter(5, 0, 'Moving')
MovCVR3ObjID06 = cParameter(6, 0, 'Moving')
MovCVR3ObjID07 = cParameter(7, 0, 'Moving')
MovCVR3ObjID08 = cParameter(8, 0, 'Moving')
MovCVR3ObjID09 = cParameter(9, 0, 'Moving')
MovCVR3ObjID10 = cParameter(10, 0, 'Moving')
MovCVR3ObjID11 = cParameter(11, 0, 'Moving')
MovCVR3ObjID12 = cParameter(12, 0, 'Moving')
MovCVR3ObjID13 = cParameter(13, 0, 'Moving')
MovCVR3ObjID14 = cParameter(14, 0, 'Moving')
MovCVR3ObjID15 = cParameter(15, 0, 'Moving')
MovCVR3ObjID16 = cParameter(16, 0, 'Moving')
MovCVR3ObjID17 = cParameter(17, 0, 'Moving')
MovCVR3ObjID18 = cParameter(18, 0, 'Moving')
MovCVR3ObjID19 = cParameter(19, 0, 'Moving')
MovCVR3ObjID20 = cParameter(20, 0, 'Moving')
MovCVR3ObjID21 = cParameter(21, 0, 'Moving')
MovCVR3ObjID22 = cParameter(22, 0, 'Moving')
MovCVR3ObjID23 = cParameter(23, 0, 'Moving')
MovCVR3ObjID24 = cParameter(24, 0, 'Moving')
MovCVR3ObjID25 = cParameter(25, 0, 'Moving')
MovCVR3ObjID26 = cParameter(26, 0, 'Moving')
MovCVR3ObjID27 = cParameter(27, 0, 'Moving')
MovCVR3ObjID28 = cParameter(28, 0, 'Moving')
MovCVR3ObjID29 = cParameter(29, 0, 'Moving')
MovCVR3ObjID30 = cParameter(30, 0, 'Moving')
MovCVR3ObjID31 = cParameter(31, 0, 'Moving')

class cView(interface.iView):
  
  def check(self):
    CVR3Groups = interface.Source.filterSignalGroups(CVR3SignalGroups)
    AC100Groups = interface.Source.filterSignalGroups(AC100SignalGroups)
    VehVeloGroups = interface.Source.filterSignalGroups(VehVelSignalGroups)
    return CVR3Groups, AC100Groups, VehVeloGroups
  
  def fill(self, CVR3Groups, AC100Groups, VehVeloGroups):
    return CVR3Groups, AC100Groups, VehVeloGroups
  
  @classmethod
  def view(cls, Param, CVR3Groups, AC100Groups, VehVeloGroups):
    
    Client = datavis.cPlotNavigator(title='Use case evaluation (%s obstacle) - %s' % (Param.ObjStance, interface.Source.BackupParser.Measurement), figureNr=None)
    interface.Sync.addClient(Client)
    
    # vehicle speed ------------------------------------------------------------
    Axis = Client.addAxis()
    Time, Value = interface.Source.getSignalFromSignalGroup(VehVeloGroups[0], 'evi.General_T20.vxvRef')
    Client.addSignal2Axis(Axis, 'evi.General_T20.vxvRef', Time, Value * 3.6, unit='kph', color='k')
    
    # various CVR3 signals -----------------------------------------------------
    CVR3Data = {}
    for signaltemplate in CVR3SignalTemplates:
      CVR3Time, CVR3Data[signaltemplate] = interface.Source.getSignalFromSignalGroup(CVR3Groups[0], 'fus.ObjData_TC.FusObj.i%s.%s' % (Param.CVR3idx, signaltemplate))
    
    # various AC100 signals ----------------------------------------------------
    AC100Data = {}
    AC100TrackValue = {}
    for signaltemplate in AC100SignalTemplates:
      try:
        AC100TrackTime, AC100TrackValue[signaltemplate] = interface.Source.getSignalFromSignalGroup(AC100Groups[0], 'tr%s_%s' % (Param.AC100idx, signaltemplate))
      except KeyError:
        pass
          
    AC100CMData = {}
    for signaltemplate in ('collision_warning', 'deceleration_demand'):
      try:
        AC100CMTime, AC100CMData[signaltemplate] = interface.Source.getSignalFromSignalGroup(AC100Groups[0], 'cm_%s' % signaltemplate)
      except KeyError:
        pass

    AngleRad = numpy.radians(AC100TrackValue['uncorrected_angle'])
    AC100Data['dx'] = AC100TrackValue['range'] * numpy.cos(AngleRad)
    AC100Data['dy'] = -AC100TrackValue['range'] * numpy.sin(AngleRad)
    AC100Data['power'] = AC100TrackValue['power']
    AC100Data['credibility'] = AC100TrackValue['credibility'] / float(2 ** 6 - 1)
    AC100Data['internal_track_index'] = AC100TrackValue['internal_track_index']
    AC100Data['track_selection_status'] = AC100TrackValue['track_selection_status']
    AC100Data['CW_track'] = AC100TrackValue['CW_track']
    AC100Data['acc_track_info'] = AC100TrackValue['acc_track_info']
    AC100Data['collision_warning'] = AC100CMData['collision_warning']
    AC100Data['deceleration_demand'] = AC100CMData['deceleration_demand']
    
    # create plots for comparison and evaluation -------------------------------
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'dxv'), CVR3Time, CVR3Data['dxv'], unit='m', color=CVR3Color)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'dx'), AC100TrackTime, AC100Data['dx'], unit='m', color=AC100Color1)
    
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'dyv'), CVR3Time, CVR3Data['dyv'], unit='m', color=CVR3Color)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'dy'), AC100TrackTime, AC100Data['dy'], unit='m', color=AC100Color1)
    
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'wObstacle'), CVR3Time, CVR3Data['wObstacle'], unit='-', color=CVR3Color)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'acc_track_info'), AC100TrackTime, AC100Data['acc_track_info'], unit='-', color=AC100Color1)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'CW_track'), AC100TrackTime, AC100Data['CW_track'], unit='-', color=AC100Color2)
    
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'existance_probability'), CVR3Time, CVR3Data['wExistProb'], unit='-', color=CVR3Color)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'credibility'), AC100TrackTime, AC100Data['credibility'], unit='-', color=AC100Color1)
    
    Axis = Client.addAxis()
    PlotAC100LeftLane = (AC100Data['track_selection_status'] & (2 ** 0)) > 0
    PlotAC100RightLane = (AC100Data['track_selection_status'] & (2 ** 1)) > 0
    PlotAC100InLane = (AC100Data['track_selection_status'] & (2 ** 2)) > 0
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'track_selection_status is LeftLane'), AC100TrackTime, PlotAC100LeftLane, unit='-', color=AC100Color3)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'track_selection_status is RightLane'), AC100TrackTime, PlotAC100RightLane, unit='-', color=AC100Color2)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'track_selection_status is InLane'), AC100TrackTime, PlotAC100InLane, unit='-', color=AC100Color1)
    
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'cm_collision_warning'), AC100CMTime, AC100Data['collision_warning'], unit='-', color=AC100Color1)
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'cm_deceleration_demand'), AC100CMTime, AC100Data['deceleration_demand'], unit='-', color=AC100Color2)
    
    Axis = Client.addAxis()
    if Param.ObjStance == 'Stationary':
      Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'b.b.Stand_b'), CVR3Time, CVR3Data['b.b.Stand_b'], unit='-', color=CVR3Color)
      PlotAC100Stat = (AC100Data['track_selection_status'] & (2 ** 4)) > 0
      Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'track_selection_status is STATIONARY'), AC100TrackTime, PlotAC100Stat, unit='-', color=AC100Color1)
    elif Param.ObjStance == 'Moving':
      Client.addSignal2Axis(Axis, 'FUS_%s_%s' % (Param.CVR3idx, 'b.b.Drive_b'), CVR3Time, CVR3Data['b.b.Drive_b'], unit='-', color=CVR3Color)
      PlotAC100Mov = (AC100Data['track_selection_status'] & (2 ** 3)) > 0
      Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'track_selection_status is MOVING'), AC100TrackTime, PlotAC100Mov, unit='-', color=AC100Color1)
      
    Axis = Client.addAxis()
    Client.addSignal2Axis(Axis, 'AC100_%s_%s' % (Param.AC100idx, 'internal_track_index'), AC100TrackTime, AC100Data['internal_track_index'], unit='-', color=AC100Color1)
