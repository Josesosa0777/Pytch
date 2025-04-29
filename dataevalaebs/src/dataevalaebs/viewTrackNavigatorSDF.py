""" Bird-eye view visualization of position and velocity uncertainty of tracked objects
"""

import numpy as np

import datavis
import interface
import asso.interface
from fusutils.matrixop import errorEllipseDiag2x2

ELLIPSE_POINT_NUM = 20

kwargsPos = dict(Label='position uncertainty', color='b', marker='')
kwargsVel = dict(Label='velocity uncertainty', color='g', marker='')

posTracks = 'posTracks'
velTracks = 'velTracks'

class cParameter(interface.iParameter):
  def __init__(self, trackNameList, kwargsList):
    self.trackNameList = trackNameList
    self.kwargsList = kwargsList
    self.genKeys()
    pass
# instantiation of module parameters
POSITION_ERR_ELLIPSE = cParameter( (posTracks,         ), (kwargsPos,         ) )
VELOCITY_ERR_ELLIPSE = cParameter( (velTracks,         ), (kwargsVel,         ) )
BOTH_ERR_ELLIPSES    = cParameter( (posTracks,velTracks), (kwargsPos,kwargsVel) )
NO_ERR_ELLIPSES      = cParameter( None, None )

errorMessage = 'Warning: object error ellipses are not added to TrackNavigator (%s)'

class cView(interface.iView):
  def view(self, viewParam):
    TN = datavis.cTrackNavigator()
    TN.addGroups(interface.Groups)
    TN.setLegend(interface.Legends)
    
    for GroupName, (LeftAngle, RightAngle, kwargs) in interface.ViewAngles.iteritems():
      TN.setViewAngle(LeftAngle, RightAngle, GroupName, **kwargs)
    
    for Status in interface.Objects.get_selected_by_parent(interface.iFill):
      Time, Objects = interface.Objects.fill(Status)
      for Object in Objects:
        TN.addObject(Time, Object)
          
    # error ellipses
    if viewParam!=NO_ERR_ELLIPSES:
      try:
        assoObj = interface.assoObj
        if not isinstance(assoObj, asso.interface.AssoObject):
          raise ValueError('invalid association object: %s' %assoObj)
        maxObjNum = assoObj.K + assoObj.L
        for trackName, kwargs in zip(viewParam.trackNameList, viewParam.kwargsList):
          # get track attribute
          if trackName == velTracks:
            if assoObj.M < 4:
              print 'Warning: velocity error ellipses skipped (states are not available)!'
              continue
            ptsNum = ELLIPSE_POINT_NUM + 3
            slicer = slice(2,4)
          else:
            ptsNum = ELLIPSE_POINT_NUM
            slicer = slice(0,2)
          # allocate arrays
          xdata = np.zeros(shape=(assoObj.N, ptsNum, maxObjNum), dtype=np.float32) 
          xdata += np.NaN # filling with NaNs in place
          ydata = np.copy(xdata)
          # loop through the tracks
          objCnt = 0
          for sensorName, objNum2track in assoObj.tracks.iteritems():
            if objNum2track is None:
              break
            for i, (x,P) in objNum2track.iteritems():
              mask = assoObj.masks[sensorName][i]
              if not np.any(mask):
                continue
              # default ellipse offset is around states
              offset = x[mask,:2]
              if trackName == velTracks:
                # get object position
                pos_x = x[mask, 0]
                pos_y = x[mask, 1]
                vel_x = x[mask, 2]
                vel_y = x[mask, 3]
                # set velocity vector
                xdata[mask,-2,objCnt] = pos_x
                ydata[mask,-2,objCnt] = pos_y
                xdata[mask,-1,objCnt] = pos_x + vel_x
                ydata[mask,-1,objCnt] = pos_y + vel_y
                # set velocity error ellipse offset
                vel_offset = x[mask,2:]
                offset += vel_offset
              # calculate ellipses
              pts = errorEllipseDiag2x2(P[mask,slicer,slicer], numPoints=ELLIPSE_POINT_NUM, offset=offset)
              # store ellipse points
              xdata[mask,:ELLIPSE_POINT_NUM,objCnt] = pts[...,0]
              ydata[mask,:ELLIPSE_POINT_NUM,objCnt] = pts[...,1]
              objCnt+=1
          else:
            # add error ellipses to TN
            TN.addDataset(assoObj.scaleTime, xdata, ydata, **kwargs)
      except ValueError, error:
        print errorMessage %error.message
      except AttributeError, error:
        print errorMessage %error.message
    
    interface.Sync.addClient(TN)
    return
