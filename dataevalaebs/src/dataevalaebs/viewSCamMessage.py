import datavis
import interface
import measparser

SCAM_OBS_NUM = 10

signalTemplates = {
#  signal name     message name           axis num
  'ID'         : ('Obstacle_%02d_Data_A', 1),
  'Pos_X'      : ('Obstacle_%02d_Data_A', 2),
  'Pos_Y'      : ('Obstacle_%02d_Data_A', 2),
  'Vel_X'      : ('Obstacle_%02d_Data_A', 2),
  'POS_X_STD'  : ('Obstacle_%02d_Data_C', 3),
  'POS_Y_STD'  : ('Obstacle_%02d_Data_C', 3),
  'VEL_X_STD'  : ('Obstacle_%02d_Data_C', 3),
  'Status'     : ('Obstacle_%02d_Data_A', 4),
  'Valid'      : ('Obstacle_%02d_Data_A', 4),
  'Replaced'   : ('Obstacle_%02d_Data_C', 4),
  'Age'        : ('Obstacle_%02d_Data_B', 5),
  'Confidence' : ('Obstacle_%02d_Data_B', 5),
}
groupLen = len(signalTemplates)
maxAxesNum = max( [axisNum for _,axisNum in signalTemplates.itervalues()] )

signalGroups = []
for i in xrange(1, SCAM_OBS_NUM+1):
  signalGroup = {}
  for signalName, (messageNameTemplate, _) in signalTemplates.iteritems():
    messageName = messageNameTemplate %i
    signalGroup[signalName] = (messageName, signalName)
  signalGroups.append(signalGroup)

class cParameter(interface.iParameter):
  def __init__(self, messageNum):
    self.messageNum = messageNum
    self.genKeys()
    pass
# instantiation of module parameters
Obstacle_01 = cParameter(1)
Obstacle_02 = cParameter(2)
Obstacle_03 = cParameter(3)
Obstacle_04 = cParameter(4)
Obstacle_05 = cParameter(5)
Obstacle_06 = cParameter(6)
Obstacle_07 = cParameter(7)
Obstacle_08 = cParameter(8)
Obstacle_09 = cParameter(9)
Obstacle_10 = cParameter(10)

class cView(interface.iView):

  def check(self):
    groups, errors = interface.Source._filterSignalGroups(signalGroups)
    measparser.signalgroup.check_onevalid(groups, errors, groupLen)
    return groups, errors
    
  def fill(self, groups, errors):
    return groups, errors

  def view(cls, param, groups, errors):
    group = groups[param.messageNum-1]
    if len(group) != groupLen:
      message = measparser.signalgroup.str_errors( [errors[param.messageNum-1],] )
      print message
    else:
      PN = datavis.cPlotNavigator(title='S-Cam Obstacle_%02d message' %param.messageNum)
      # prepare axes
      axes = {}
      for i in xrange(1, maxAxesNum+1):
        axes[i] = PN.addAxis()
      for signalName, (_, axisNum) in signalTemplates.iteritems():
        ax = axes[axisNum]
        # get signal and phys unit
        t, signal = interface.Source.getSignalFromSignalGroup(group, signalName)
        physUnit = interface.Source.getPhysicalUnitFromSignalGroup(group, signalName)
        # plot signal
        PN.addSignal2Axis(ax, '%s [%s]' %(signalName, physUnit), t, signal)
      interface.Sync.addClient(PN)
    return

