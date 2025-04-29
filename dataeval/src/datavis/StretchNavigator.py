"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import math
import copy

import numpy
import matplotlib as mpl
if mpl.get_backend() != 'Qt4Agg':
  mpl.use('Qt4Agg')
  mpl.rcParams['backend.qt4']='PySide'
  
from TrackNavigator import cTrackNavigator
from PlotNavigator import QT_KEYS_TO_STRING

class cStretchNavigator(cTrackNavigator):
  '''
  Birdview of ego_vehicle and detected Objects.
  Creating Positions into Future or Past with given time distance is possible.
  ego_vehicle has KeyCode 20.
  '''
  def __init__(self, Source, Title="",FgNr= None, ScreenWidth=150, steps=5, stepwidth=0.4):
    cTrackNavigator.__init__(self, Title,FgNr)
                
    self.ScreenWidth = ScreenWidth
    """
    type: float
      width (height) of subplot
    """
    self.Source = Source
    
    self.steps=steps
    self.steps_last=steps
    """
    type: int
      steps into past
    """
    self.steps_future=3
    self.steps_future_last=3
    """
    type: int
      steps into future
    """
    self.stepwidth=stepwidth
    """
    type: float
      time distance between 2 steps
    """
    self.coloroffset = min(1./self.steps_future, 1./self.steps)
    """
    type: float
      coloroffset between 2 steps to make future/past visible.
    """
    self.dynamic_resize=False
    """
    type: bool
      Automatic Zoom based on ego_vehicle speed On/Off
    """
    self.tracksmoving=True
    """
    type: bool
      moving with ego_vehicle On/Off
      On: ego_vehicle always on (X=0,Y=0). Track is moving.
      Off: Camera stationary on world-coordinates. Tracks is not moving. Ego_vehicle is moving
    """
    self.X=0
    self.Y=0
    """
    type: float
      X,Y coordinate of ego_vehicle at last timestamp where self.trackmoving had been True
    """
    self.Button1pressed = False
    """
    type: bool
      LMB (Left Mouse Button) pressed or not
    """
    self.Button3pressed = False
    """
    type: bool
      RMB (Reft Mouse Button) pressed or not
    """
    self.KeyShiftpressed = False
    """
    type: bool
      Shift key pressed or not
    """
    self.scaletime = None
    """
    type: <ndarray>
      time all objects are scaled on
    """
    self.data = None
    """
    type: list of objects [{"dx":<ndarray>,},]
    """
    
    #Make ParameterLabel with refresh function to show actual Parameters
    self.ParameterLabel = self.fig.text(0.81, 0.5, '', bbox=dict(facecolor='w', pad=10))
    self.refresh_ParameterLabel = lambda: self.ParameterLabel.set_text(' Press F1 for HELP\n steps_past: %d\n steps_future: %d\n stepwidth: %0.1f [sec]\n movingTrack: %s\n autoZoom: %s'%(self.steps,self.steps_future,self.stepwidth,str(self.tracksmoving),str(self.dynamic_resize)))
    self.refresh_ParameterLabel()

    #mouse event handlers
    self.fig.canvas.mpl_connect('scroll_event', self.onFigureScroll)
    self.fig.canvas.mpl_connect('button_press_event', self.onButtonPress)
    self.fig.canvas.mpl_connect('button_release_event', self.onButtonRelease)
    
    #help label
    self.help_font=mpl.font_manager.FontProperties('monospace', 'normal', 'normal', 'normal', 'normal', 'small')
    """
    type: FontProperties
    Font for the help
    """
    self.help = self.fig.text(0.1,0.5,
    'Keyboard shortcuts:\n\n'
    'F1                  Show/hide this help screen\n'
    'h                   Show/Hide legend\n'
    'd                   Dynamic resize on/off\n'
    'm                   Moving track on/off\n'
    'Space               Start/stop playback if a VideoNavigator is attached\n'
    'Timesteps:\n\n'
    '   LeftMouseButton+Scroll      add/remove past\n'
    '   Shift+up/down\n'
    '   RightMouseButton+Scroll     add/remove future\n'
    '   Shift+left/right\n\n'
    '   Shift+End                   Toggle timesteps on/off'
    'Change timestep distance:\n\n'
    '   y/z                         +-0.1 seconds\n'
    'Zoom in:\n\n'
    '   Scroll\n'
    '   +/-\n'
    '\n\nRecommended VN Mode:'
    '   Synchronized (r/s)'
    '   Deactivated Labels (l)'
    , visible=False, fontproperties=self.help_font, bbox=dict(facecolor='LightYellow', pad=20))
    """
    type: Text
    Online help text
    """
    #TODO: Update help text above

    #print ("\n\n\nFunctions:\n -MouseScroll: Zoom in/out\n -MouseButton+Scroll: Add Timesteps (Left,Past/Right,Future)\n -z/y: Change Stepwidth +-=0.1 seconds\n -m: Change CameraMode (stationary/moving)\n -d: Change ZoomMode (dynamicResice based on vehicle-speed on/off \n  (High Performance, recommended))\n -No:1-0: See Groups")
    #print "Recommended VN Mode: with activated r-mode without labels\n\n"
    
  def egolane(self, Coeff, Defaults = None):
    """
    Returns ego_vehicle Track as line2d (X,Y-coordinates as lists)
    """

    Index = Coeff
    if self.tracksmoving:
        try:
            offset_x = numpy.zeros(len(self.ego_vehicle["dx"])-2*self.steps,dtype=float)
            offset_y = numpy.zeros(len(self.ego_vehicle["dy"])-2*self.steps,dtype=float)
            offset_x.fill(self.ego_vehicle["dx"][Index])
            offset_y.fill(self.ego_vehicle["dy"][Index])
            x = self.ego_vehicle["dx"][self.steps:len(self.ego_vehicle["dx"])-self.steps]-offset_x
            y = self.ego_vehicle["dy"][self.steps:len(self.ego_vehicle["dx"])-self.steps]-offset_y
            self.Y = self.ego_vehicle["dx"][Index]
            self.X = -self.ego_vehicle["dy"][Index]
        except IndexError:
            pass
        return -y,x
    else:
        try:
            x = self.ego_vehicle["dx"][self.steps:len(self.ego_vehicle["dx"])-self.steps]
            y = self.ego_vehicle["dy"][self.steps:len(self.ego_vehicle["dx"])-self.steps]
            self.X=0
            self.Y=0
        except IndexError:
            pass
        return -y,x
  
  def onButtonPress(self, event):
      """
      Event handler for mouse button press event.

      :Return: None
      """
      
      if event.button == 1:
        self.Button1pressed=True
      if event.button == 3:
        self.Button3pressed=True
      return
          
  def onButtonRelease(self, event):
      """
      Event handler for mouse button release event.

      :Return: None
      """
      
      if event.button == 1:
        self.Button1pressed=False
      if event.button == 3:
        self.Button3pressed=False
      return

          
  def onFigureScroll(self, event):
    """
    Event handler for mouse scroll event.

    :Return: None
    """
    if self.Button1pressed or self.Button3pressed:
        if self.Button1pressed:
          self.steps = max(self.steps+int(event.step),1)
        elif self.Button3pressed:
          self.steps_future = max(self.steps_future+int(event.step),1)
        else:
          pass
        for object in self.Objects:
              last = len(object) - 1
              len_last = len(object[last])
              while self.steps+self.steps_future+1>len_last:
                Point, = self.SP.plot(0, 0, 'o')
                object[last].append(Point)
                len_last = len(object[last])-1
              for Point in object[last][self.steps+self.steps_future-1:]:
                Point.set_visible(False)

        self.coloroffset = min(1./self.steps_future, 1./self.steps)#range(0,1)
        
        #print "step:%s , steps_future:%s , stepwidth:%s"%(self.steps, self.steps_future, self.stepwidth)
        self.refresh_ParameterLabel()
    else:
        if event.step>0:
          for i in xrange(abs(int(event.step))):
            self.ScreenWidth = max(self.ScreenWidth-self.ScreenWidth/5,20)
        else:
          for i in xrange(abs(int(event.step))):
            self.ScreenWidth += self.ScreenWidth/5
        self.resize()
    
    self.seekWindow()
    pass
  
  def keyPressEvent(self, event):
    if event.key() in QT_KEYS_TO_STRING:
      event.keysm = QT_KEYS_TO_STRING[event.key()]
    else:
      event.keysm = event.text()
    self.onFigureKeyPress(event)
    return
  
  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Shift:
      self.KeyShiftpressed = False
    return
  
  def addObject(self, Time, Object):
    """
    :Parameters:
      Time : numpy.ndarray
      Object : dict
        {'dx':<numpy.ndarray>, 'dy':<numpy.ndarray>, 'label':<str>, 
         'type':<numpy.ndarray or int>, 
         'color':<numpy.ndarray or (Red<uint8>, Green<uint8>, Blue<uint8>)>}
    """
    dY = self.fitSize(Time, Object['dx'])
    dX = self.fitSize(Time, Object['dy'])
    Color = self.fitSize(Time, Object['color'])
    Type = self.fitSize(Time, Object['type'])
    Label = self.fitSize(Time, Object['label'])
    
    for type in numpy.unique(Type):
      Mask = Type == type
      type = type if type in self.Markers else 0
      Type[Mask] = type
    
    MyObject = [Time]
    MyObject.append(-dX)
    MyObject.append(dY)
    MyObject.append(Color/255.0)
    MyObject.append(Type)
    MyObject.append(Label)
    Points = []
    for x in xrange(self.steps+self.steps_future-1):
      Point, = self.SP.plot(0, 0, 'o')
      Points.append(Point)
    MyObject.append(Points)
    self.Objects.append(MyObject)
    pass
  
  def onFigureKeyPress(self, event):
    """
    Event handler for key press event.
    CONVENTION: Numbers and capital letters are reserved for enabling/disabling groups.

    :Return: None
    """
    if event.keysm == ' ':
      # synchronizable interface callback
      if self.playing:
        self.onPause(self.time)
      else:
        self.onPlay(self.time)
    elif event.keysm == 'h':
      # pressing 'h' toggles legends on/off
      for Axe in self.fig.axes:
        Legend = Axe.get_legend()
        if Legend:
          Legend.set_visible(not Legend.get_visible())
      self.seekWindow()
    elif event.keysm == '-':
      self.ScreenWidth += self.ScreenWidth/5
      self.resize()
    elif event.keysm == '+':
      self.ScreenWidth = max(self.ScreenWidth-self.ScreenWidth/5,20)
      self.resize()
    elif event.keysm == 'd':
      self.dynamic_resize = not self.dynamic_resize
      self.tracksmoving = True
      self.refresh_ParameterLabel()
      self.seekWindow()
    elif event.keysm == 'm':
      self.tracksmoving = not self.tracksmoving
      if self.tracksmoving:
          self.SP.set_xlim(-self.ScreenWidth/2,self.ScreenWidth/2)
          self.SP.set_ylim(-self.ScreenWidth/2,self.ScreenWidth/2)
      else:
          self.SP.set_xlim(float(self.X)-self.ScreenWidth/2,float(self.X)+self.ScreenWidth/2)
          self.SP.set_ylim(float(self.Y)-self.ScreenWidth/2,float(self.Y)+self.ScreenWidth/2)
      self.refresh_ParameterLabel()
      self.seekWindow()
    elif event.keysm == 'z':
      self.stepwidth += 0.1
      self.refresh_ParameterLabel()
      self.seekWindow()
    elif event.keysm == 'y':
      self.stepwidth = max(self.stepwidth-0.1,0.1)
      self.refresh_ParameterLabel()
      self.seekWindow()
    elif event.keysm == 'F1':
      self.help.set_visible(not self.help.get_visible())
      bx = self.help.get_window_extent()
      bx = bx.inverse_transformed(self.fig.transFigure)
      self.help.set_position(((1-bx.width)/2.,(1-bx.height)/2.))
      self.seekWindow()
    elif event.keysm == 'shift':
      self.KeyShiftpressed = True
    elif self.KeyShiftpressed:
      if event.keysm == 'up':
        self.steps = self.steps+1
      elif event.keysm == 'down':
        self.steps = max(self.steps-1,1)
      elif event.keysm == 'right':
        self.steps_future = self.steps_future+1
      elif event.keysm == 'left':
        self.steps_future = max(self.steps_future-1,1)
      elif event.keysm == 'end':
        if self.steps_future!=1 or self.steps!=1:
          self.steps_future_last=self.steps_future
          self.steps_last=self.steps
          self.steps_future=1
          self.steps=1
        else:
          self.steps_future=self.steps_future_last
          self.steps=self.steps_last
      elif event.keysm in self.KeyCodes:
        self.onSelectGroup(self.KeyCodes[event.keysm])

      for object in self.Objects:
              last = len(object)-1
              len_last = len(object[last])
              while self.steps+self.steps_future+1>len_last:
                Point, = self.SP.plot(0, 0, 'o')
                object[last].append(Point)
                len_last = len(object[last])-1
              for Point in object[last][self.steps+self.steps_future-1:]:
                Point.set_visible(False)

      self.coloroffset = min(1./self.steps_future, 1./self.steps)#range(0,1)

      #print "step:%s , steps_future:%s , stepwidth:%s"%(self.steps, self.steps_future, self.stepwidth)
    elif event.key in self.KeyCodes:
      self.onSelectGroup(self.KeyCodes[event.key])
    self.refresh_ParameterLabel()
    self.seekWindow()
    pass
  
  def resize(self, width_half=None, heigh_half=None,show=True):
    """
    Resizes Subplot (self.fig.SP)
    
    :Return: None
    """

    if not width_half or not heigh_half:
        width_half=self.ScreenWidth
        heigh_half=self.ScreenWidth
    low_x,high_x = self.SP.get_xlim()
    x_cent = (low_x+high_x)/2
    low_y,high_y = self.SP.get_ylim()
    y_cent = (low_y+high_y)/2
    self.SP.set_xlim(x_cent-width_half, x_cent+heigh_half)
    self.SP.set_ylim(y_cent-width_half, y_cent+heigh_half)
    self.Traj  = numpy.arange(-width_half, heigh_half, 0.1)
    if show:
        self.seekWindow()
    return
  
  
  def dynamic_resizing(self, TimeStamp):
    """
    dynamic_resizing function. Called on each timestep by seek() function if self.dynamic_resize==True
    
    :Return: None
    """

    Index = max(self.scaletime.searchsorted(TimeStamp, side='right')-1, 0)
    self.ScreenWidth=max(self.ego_vehicle["dv"][Index]*15,20)
    self.resize(show=False)
    
  
  def seek(self, TimeStamp):

    self.time = TimeStamp
    self.times = []
    """
    type: list
      Times appended in order: [most_past_to_actualTimestamp,most_future_to_actualTimestamp, actualTimestamp]
    """

    for i in xrange(1,self.steps):
      self.times.append(self.time - ((self.steps-i)*self.stepwidth))
    for i in xrange(1,self.steps_future):
      self.times.append(self.time + ((self.steps_future-i)*self.stepwidth))
    self.times.append(self.time)

    if self.dynamic_resize:
      self.dynamic_resizing(TimeStamp)

    for FuncName, Tracks in  self.Tracks.iteritems():
      for Track in Tracks.Tracks:
        Index = max(Track.Time.searchsorted(TimeStamp, side='right')-1, 0)
        if FuncName[0] == 'egolane':
          func = Track.Funcs[FuncName[0]]
          X, Y = func(self, Index )
          Track.Line.set_xdata(X)
          Track.Line.set_ydata(Y)
        else:
          Track()
    for Time, X, Y, Color, Type, Label, Points in self.Objects:
       for x in xrange(len(self.times)):
          T = self.times[x]
          Point = Points[x]
          try:
            Index = max(Time.searchsorted(T, side='right')-1, 0)
          except IndexError:
            break
          ActType = Type[Index]
          if ActType in self.Invisibles:
            Point.set_visible(False)
          else:
            Point.set_visible(True)
            Point.set_xdata(X[Index]-self.X)
            Point.set_ydata(Y[Index]-self.Y)
            color = numpy.array([0.,0.,0.])
            if not x==len(self.times)-1:
                if x<self.steps-1:
                    for rgb in xrange(3):
                       color[rgb]=min(max(Color[Index][rgb]+(self.steps-x)*self.coloroffset,0.),1.)
                else:
                    for rgb in xrange(3):
                       color[rgb]=min(max(Color[Index][rgb]+(self.steps+self.steps_future-x)*self.coloroffset,0.),1.)
                Point.set_mfc(color)
                Point.set_mec(color)
                if ActType in self.Markers:
                  Point.set(**self.Markers[ActType])   
            else:
                Point.set_mfc(Color[Index])
                Point.set_mec(Color[Index])
                if ActType in self.Markers:
                  Point.set(**self.Markers[ActType])

    self.fig.canvas.draw()
    pass

  def onMotion(self, event):
    # while realtime playback is on this function should be disabled, as causes performance issues
    if not self.playing and self.showObjInfo:
      if event.inaxes == self.SP:
        ObjsUnderCursor = []
        for Index, Obj in self.iterActualObjects():
          Time, X, Y, Color, Type, Label, Points   = Obj
          ActType = Type[Index]
          if ActType not in self.Invisibles:
            Dx, Dy = Points[1].get_transform().transform([X[Index], Y[Index]])
            Dist = math.sqrt((Dx - event.x)**2 + (Dy - event.y)**2)
            if Dist < 10:
              ObjsUnderCursor.append("%s\ndx=%.2f dy=%.2f" %
                ( (Label if isinstance(Label, basestring) else Label[Index]),
                  Y[Index],
                  X[Index]))
        if ObjsUnderCursor:
          self.ObjInfo.xy = (event.xdata, event.ydata)
          self.ObjInfo.set_text(("\n%s\n" % ("-" * 16)).join(ObjsUnderCursor))
          self.ObjInfo.set_visible(True)
          self.seekWindow()
    return

  def seekWindow(self):
    self.seek(self.time)
    return

  def fitSize(self, Time, Param):
      """
      Extend the constans `Param` to fit to `Time` in shape.

      :Parameters:
        Time : numpy.ndarray
        Param : float
      :ReturnType: numpy.ndarray    
      :Exeptions:
        ValueError : if `Param` is numpy.ndarray and its size does not fit to `Time`
      """    
      if not isinstance(Param, numpy.ndarray):
        Param = numpy.array([Param])
        Param = Param.repeat(Time.size, 0)
      elif Param.shape[0] != Time.shape[0]:
        raise ValueError, 'The size of the Param not fits to the Time'
      return Param

  def addego_vehicle(self, scaletime, ego_vehicle_speed_DevSig, ego_vehicle_yawrate_DevSig):
    """
    :Parameters:
      ego_vehicle_speed_DevSig:
        type: Signal (time <ndarray>, value <ndarray>)
           vehicle speed on wich trajectorie is based on
      ego_vehicle_yawrate_DevSig:
        type: Signal (time <ndarray>, value <ndarray>)
           vehicle yawrate on wich trajectorie is base on
    """
    self.scaletime = scaletime
    scaletime, ego_vehicle = self.getVehicleCoordinates(ego_vehicle_speed_DevSig=ego_vehicle_speed_DevSig, ego_vehicle_yawrate_DevSig=ego_vehicle_yawrate_DevSig)
  
  def addObjects(self, data):
    """
    :Parameters:
      time: <ndarray>
        scaletime of all objects in data
      data: list
        list ob dicts representing objects
    """
    if self.scaletime==None:
      print 'Please add ego vehicle bevore other Objects with addego_vehicle()-method'
      raise ValueError
    data2 = copy.deepcopy(data)
    scaletime, x_vecs, data = self.getSensorObjects_asCoordinates(data2)
    for x in xrange(len(data2)):
      data[x]["dx"] = x_vecs[x][0]
      data[x]["dy"] = x_vecs[x][1]
      self.addObject(self.scaletime, data2[x])
      
  def getVehicleCoordinates(self, ego_vehicle_speed_DevSig, ego_vehicle_yawrate_DevSig):
      """
      Return worldcoordinates of ego_vehicle based on integration of yawrate
      
      :Return: self.scaletime: <ndarray>, self.ego_vehicle: dict([["dx",value<ndarray>],])
      """
      scaletime, v       = self.Source.getSignal(ego_vehicle_speed_DevSig[0],ego_vehicle_speed_DevSig[1], ScaleTime = self.scaletime)
      scaletime, yawrate = self.Source.getSignal(ego_vehicle_yawrate_DevSig[0], ego_vehicle_yawrate_DevSig[1], ScaleTime=self.scaletime)

      
      len_time=len(self.scaletime)
      
      # yawrate=-numpy.pi*yawrate/180
      
      x_vec_ego=numpy.zeros((2,len_time))#coordinates of own vehicle (x,y) on map
      phi_ego=numpy.zeros(len_time)
      actual_phi=0.
      for i in xrange(1,len_time):
        delta_t=self.scaletime[i]-self.scaletime[i-1]
        actual_phi+=delta_t*yawrate[i]
        phi_ego[i]=actual_phi
        x_vec_ego[0,i]=x_vec_ego[0,i-1]+delta_t*v[i]*numpy.cos(actual_phi)
        x_vec_ego[1,i]=x_vec_ego[1,i-1]+delta_t*v[i]*numpy.sin(actual_phi)

      r_ego=numpy.zeros(len_time)
      theta_ego=numpy.zeros(len_time)
      for i in xrange(len_time):
        r_ego[i]=math.sqrt(x_vec_ego[0][i]**2+x_vec_ego[1][i]**2)
        theta_ego[i]=numpy.arctan2(x_vec_ego[1][i],x_vec_ego[0][i])

      #Create ego_vehicle
      self.ego_vehicle = {}
      self.ego_vehicle["label"]="ego"
      self.ego_vehicle["type"]=20
      dummy = numpy.zeros(len_time)
      w = numpy.reshape(numpy.repeat(dummy<1, 3),(-1,3))
      self.ego_vehicle["color"] = numpy.where(w,[0,0,0],[0,0,0])
      self.ego_vehicle["dx"] = x_vec_ego[0]
      self.ego_vehicle["dy"] = x_vec_ego[1]
      self.ego_vehicle["phi_ego"] = phi_ego
      self.ego_vehicle["r_ego"] = r_ego
      self.ego_vehicle["theta_ego"] = theta_ego
      self.ego_vehicle["dv"] = v
      self.ego_vehicle["yawrate"] = yawrate
        
      return self.scaletime, self.ego_vehicle

  def getSensorObjects_asCoordinates(self, data):
    """
    Gets Objects/ego_vehicle worldcoodinates based on integration of yawrate.
    
    Return: scaletime <ndarray>, x_vec_ego <ndarray>, theta_ego <ndarray>, r_ego <ndarray>, x_vecs <ndarray>, data <list>
    """

    data_filtered={}
    x_vecs=[]
    

    self.data = copy.deepcopy(data)

    len_time=len(self.scaletime)
    
    for o in xrange(len(data)):
        x_vec=numpy.zeros((2,len_time))#first row: x-world-coordinate, second row:y-world-coordinate
        r_theta_vec=numpy.zeros((2,len_time))# first(radius),second(angle) row: polar-coordinates of ego_vehicle position in world
        r_theta_vec_egocoor=numpy.zeros((2,len_time)) # radius and angle of ego vehicle
        #rotation
        for i in xrange(len_time):
          r_theta_vec_egocoor[0][i] = math.sqrt(data[o]["dx"][i]**2+data[o]["dy"][i]**2) # tmp radius
          r_theta_vec_egocoor[1][i] = self.ego_vehicle["phi_ego"][i]+numpy.arctan2(data[o]["dy"][i],data[o]["dx"][i])# tmp angle
        #translation
        for i in xrange(len_time):
          x_vec[0][i]=self.ego_vehicle["dx"][i]+numpy.cos(r_theta_vec_egocoor[1][i])*r_theta_vec_egocoor[0][i]
          x_vec[1][i]=self.ego_vehicle["dy"][i]+numpy.sin(r_theta_vec_egocoor[1][i])*r_theta_vec_egocoor[0][i]
        for i in xrange(len_time):
          r_theta_vec[1][i]=numpy.arctan2(x_vec[1][i],x_vec[0][i]) # angle in world coordinates
          r_theta_vec[0][i]=math.sqrt(x_vec[1][i]**2+x_vec[0][i]**2) # radius in world coordinates

        x_vecs.append(x_vec)

    return self.scaletime, x_vecs, data
  
  def start(self):
    self.addObject(self.scaletime, self.ego_vehicle) # has to be put in as last object for good vision in plot
    self.timesteps=numpy.arange(len(self.scaletime))
    self.addTrack('egolane', self.timesteps)
    for Tracks in  self.Tracks.itervalues():
      Tracks.setFuncName('egolane')
      for Track in Tracks.Tracks:
        Track.addFunc(self.egolane.im_func, FuncName='egolane')

    self.resize()
    self.seek(0.0)
    self.addToolBar(QtCore.Qt.BottomToolBarArea, self.Toolbar)
    self.setCentralWidget(self.Canvas)
    self.show()
    pass

if __name__ == '__main__':
  import sys
  import optparse
  from argparse import ArgumentParser

  import numpy
  from PySide import QtGui, QtCore

  from interface.manager import Manager
  from config.helper import procConfigFile
  from config.View import cLoad

  app = QtGui.QApplication([])
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('view', args)
  Config = cLoad(name)
  Config.init(args)

  t = numpy.arange(0, 3001, 1)
  y = numpy.sin(t)
  z = numpy.cos(t)



  manager = Manager()
  Config.load(manager)
  Source = manager.get_source('main')
  parser = optparse.OptionParser()
  parser.add_option('-p', '--hold-navigator', 
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  opts, args = parser.parse_args() 

  Source.loadParser()
  '''deviceNames = Source.Parser.iterDeviceNames()
  for deviceName in deviceNames:
    print deviceName
  signalNames = Source.Parser.iterSignalNames('RadarFC-t10---RadarFC')
  for signalName in signalNames:
    print signalName'''
  SN = cStretchNavigator(Source)

  SN.addego_vehicle(t, ('RadarFC-t10---RadarFC', 'id2Idx.IdxOld.i31'),
                       ('RadarFC-t10---RadarFC', 'id2Idx.IdxOld.i30'))
  SN.start()
  SN.seek(200.0)
  sys.exit(app.exec_())