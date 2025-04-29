'''
   
   data source: VBOX
   
   GPS
   
   Ulrich Guecker 2012-03-15

'''


import pickle
import numpy as np
import pylab as pl



# KB specific imports
import measparser
import kbtools

# --------------------------------------------------------------------------------------------
class cDataVBOX():

  # required number of satellites
  min_number_sats = 5

  # -------------------------------------------------------------------------------------------
  @staticmethod
  def load_VBOX_from_Source(Source, PickleFilename=None):
  
    VBOX = None
    SignalGroups_VBOX_1 = [{"Latitude"           : ("VBOX_1", "Latitude"),
                            "Sats"               : ("VBOX_1", "Sats"),
                            "Time_Since_Midnight": ("VBOX_1", "Time_Since_Midnight"),
                           },]
    SignalGroups_VBOX_2 = [{"Longitude"          : ("VBOX_2", "Longitude"),
                            "Heading"            : ("VBOX_2", "Heading"),
                            "Velocity_Kmh"       : ("VBOX_2", "Velocity_Kmh"),
                           },]
    dt = 0.01  # cycle time of VBOX_1 and VBOX_2 message       
    # -------------------------------------
    VBOX_1 = {}
    t_VBOX_1 = None
    FilteredGroups_VBOX_1 = Source.filterSignalGroups(SignalGroups_VBOX_1, Verbose=True)
    for Original, Filtered in zip(SignalGroups_VBOX_1, FilteredGroups_VBOX_1):
      for Alias, (DevName, SignalName) in Original.iteritems():
        if Alias in Filtered:
          t_VBOX_1, VBOX_1[Alias] = Source.getSignalFromSignalGroup(Filtered, Alias)
        else:
           print "Warning: Signal %s not available"%Alias
           return None

    # -------------------------------------
    VBOX_2 = {} 
    t_VBOX_2 = None    
    FilteredGroups_VBOX_2 = Source.filterSignalGroups(SignalGroups_VBOX_2, Verbose=True)
    for Original, Filtered in zip(SignalGroups_VBOX_2, FilteredGroups_VBOX_2):
      for Alias, (DevName, SignalName) in Original.iteritems():
        if Alias in Filtered:
          t_VBOX_2, VBOX_2[Alias] = Source.getSignalFromSignalGroup(Filtered, Alias)
        else:
           print "Warning: Signal %s not available"%Alias
           return None

           FilteredGroups_VBOX_2 = Source.filterSignalGroups(SignalGroups_VBOX_2, Verbose=True)
   
    t1 = t_VBOX_1
    t2 = t_VBOX_2
   
    #if not len(t1) == len(t2):
    #  print "different length error"
   
    
    if 0 < t2[0] - t1[0] < 2*dt:
      # correct
      start_idx1 = 0
      start_idx2 = 0
    elif t2[0] - t1[0] < 0:
      start_idx1 = 0
      start_idx2 = 1
    else:
      start_idx1 = 1
      start_idx2 = 0

     
    if 0 < t2[-1] - t1[-1] < 2*dt:
      # correct
      stop_idx1 = -1
      stop_idx2 = -1
    elif t2[-1] - t1[-1] < 0:
      stop_idx1 = -2
      stop_idx2 = -1
    else:
      stop_idx1 = -1
      stop_idx2 = -2
  
    out_t1 = t1[start_idx1:stop_idx1]
    out_t2 = t2[start_idx2:stop_idx2]
    
    # check
    if not len(out_t1) == len(out_t2):
      print "length error"
    

    if not np.logical_and(0.0<(out_t2-out_t1),(out_t2-out_t1)<0.2).all():
      print "dt error"
    
    VBOX = {}
    VBOX['t_VBOX'] = out_t1
    for signal in VBOX_1.keys():
      VBOX[signal] = VBOX_1[signal][start_idx1:stop_idx1]
    for signal in VBOX_2.keys():
      VBOX[signal] = VBOX_2[signal][start_idx2:stop_idx2]
    
    
    # Adjustment
    VBOX['Longitude']     = -VBOX['Longitude']/60.0     
    VBOX['Latitude']      = VBOX['Latitude']/60.0   
    
    
    # determine sections with not enough satellites
    VBOX['not_enough_Sats'] = cDataVBOX.determine_sections_with_not_enough_satellites(VBOX)
    
    # save if filename given
    if VBOX and PickleFilename:
      output = open(PickleFilename, 'wb')
      pickle.dump(VBOX, output,-1)     # -1: using the highest protocol available
      output.close()

    return VBOX
    
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def load_VBOX_from_picklefile(FileName,sig={},timebase=None):
    #-----------------------------------------------------------
    # load ego vehicle data from file (pickle)
    pkl_file = open(FileName, 'rb')
    VBOX     = pickle.load(pkl_file)
    pkl_file.close()
    
    return VBOX
    
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def determine_sections_with_not_enough_satellites(sig):
    # -------------------------------------------------------
    # determine sections with not enough satellites
    # -> bridges over Autobahn
    not_enough_Sats =[]
    list = kbtools.scan4handles(sig['Sats']<cDataVBOX.min_number_sats)
    for start_idx, stop_idx in list:
      new_start_idx = max(start_idx-1,0)
      new_stop_idx  = min(stop_idx+1, len(sig['Sats'])-1)
      #print start_idx, stop_idx, new_start_idx , new_stop_idx
      #print  sig['Latitude'][start_idx-1], sig['Longitude'][start_idx-1]
      #print  sig['Latitude'][stop_idx+1], sig['Longitude'][stop_idx+1]
      lat_vec = np.zeros(2)
      lon_vec = np.zeros(2)
      lat_vec[0] = sig['Latitude'][new_start_idx]
      lon_vec[0] = sig['Longitude'][new_start_idx]
      lat_vec[1] = sig['Latitude'][new_stop_idx]
      lon_vec[1] = sig['Longitude'][new_stop_idx]
        
      not_enough_Sats.append((lon_vec,lat_vec))
    
    return not_enough_Sats

  
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def plot_LatLon_vs_Time(sig, FigNr=200): 
    
    fig=pl.figure(FigNr);   
    fig.clear()
    fig.suptitle('VBOX')

    sp=fig.add_subplot(311)
    sp.grid()
    sp.plot(sig['t_VBOX'],sig['Sats'],'b-')
    #sp.set_xlabel('Time')
    sp.set_ylabel('No of Sats')
    
    sp=fig.add_subplot(312)
    sp.grid()
    sp.plot(sig['t_VBOX'],sig['Latitude'],'b-')
    #sp.set_xlabel('Time')
    sp.set_ylabel('Latitude [deg]')

    sp=fig.add_subplot(313)
    sp.grid()
    sp.plot(sig['t_VBOX'],sig['Longitude'],'b-')
    sp.set_xlabel('Time')
    sp.set_ylabel('Longitude [deg]')

    #sp.set_ylim(48.9,49.0)
    #sp.set_xlim(9.2,9.3)
 
    
    fig.show()

  # -------------------------------------------------------------------------------------------
  @staticmethod
  def plot_LatLon(sig, FigNr=200, clearFigure = True, show_not_enough_Sats = True): 
    
     
    # ------------------------------------------
    # only plot section with enough number of satellites
    Mask = sig['Sats']>=cDataVBOX.min_number_sats 
    
    #print "len(Mask):", len(Mask)
    #print "len(sig['t_VBOX']):", len(sig['t_VBOX'])
    
    
    time = sig['t_VBOX'][Mask]
    lon  = sig['Longitude'][Mask]
    lat  = sig['Latitude'][Mask]

       
    # determine reactangular bounds    
    min_lat = np.min(lat)
    max_lat = np.max(lat)
    d_lat = max_lat - min_lat
    
    min_lon = np.min(lon)
    max_lon = np.max(lon)
    d_lon = max_lon - min_lon
    
    
    fig=pl.figure(FigNr)
    
    if clearFigure: 
      fig.clear()
      
    fig.suptitle('VBOX - Latitude/Longitude')

    sp=fig.add_subplot(111,aspect='equal')
    sp.grid()
    sp.plot(lon,lat,'b-')
    sp.set_xlabel('Longitude [degree]')
    sp.set_ylabel('Latitude [degree]')
    #sp.set_ylim(min_lat-0.1*d_lat, max_lat+0.1*d_lat)
    #sp.set_xlim(min_lon-0.1*d_lon, max_lon+0.1*d_lon)
    
    #sp.set_ylim(48.9,49.0)
    #sp.set_xlim(9.2,9.3)
 
    # time markings
    cDataVBOX.TimeMarkings(sp,time,lon,lat)
 
    # section with not enough satellites
    if show_not_enough_Sats:
      for lon_vec,lat_vec in sig['not_enough_Sats']:
        sp.plot(lon_vec,lat_vec,'rx-')
 
 
    fig.show()
    return fig, sp

  # -------------------------------------------------------------------------------------------
  @staticmethod
  def TimeMarkings(sp,t,x,y,n=10): 
    # --------------------------------------
    # Zeitmarkierungen  
  
    if len(t)>2:
      idx = range(1,len(t),int(len(t)/n))
      t = t[idx]
      x = x[idx]
      y = y[idx]

    for k in xrange(len(t)):
      sp.plot(x[k],y[k],'bx');
      sp.text(x[k],y[k],' %3.0f s'%t[k])
   
  
    
  # -------------------------------------------------------------------------------------------
  @staticmethod
  def LatLon2UTMxy(sig): 
  
    Mask = sig['Sats']>cDataVBOX.min_number_sats
    sig['UTM_x'],sig['UTM_y'], common_zone = kbtools.cCnvtGPS.LatLon2UTMxy(sig['Latitude'][Mask] ,sig['Longitude'][Mask])
    Heading = sig['Heading'][Mask] 
    return sig
  
    # -------------------------------------------------------------------------------------------
  @staticmethod
  def plot_UTMxy(sig, FigNr=200): 
    
    
    # ------------------------------------------
    # only plot section with enough number of satellites
    Mask = sig['Sats']>=cDataVBOX.min_number_sats 
    time = sig['t_VBOX'][Mask]
    lon  = sig['Longitude'][Mask]
    lat  = sig['Latitude'][Mask]
    UTM_x, UTM_y, common_zone= kbtools.cCnvtGPS.LatLon2UTMxy(lat,lon)

          
    # determine reactangular bounds    
    min_UTM_y = np.min(UTM_y)
    max_UTM_y = np.max(UTM_y)
    d_UTM_y = max_UTM_y - min_UTM_y
    
    min_UTM_x = np.min(UTM_x)
    max_UTM_x = np.max(UTM_x)
    d_UTM_x = max_UTM_x - min_UTM_x
    
    
    fig=pl.figure(FigNr);   
    fig.clear()
    fig.suptitle('VBOX - UTM')

    sp=fig.add_subplot(111)
    sp.grid()
    sp.plot(UTM_x,UTM_y,'b-')
    sp.set_xlabel('UTM_x [m]')
    sp.set_ylabel('UTM_y [m]')
    sp.set_ylim(min_UTM_y-0.1*d_UTM_y, max_UTM_y+0.1*d_UTM_y)
    sp.set_xlim(min_UTM_x-0.1*d_UTM_x, max_UTM_x+0.1*d_UTM_x)
    
    #sp.set_ylim(48.9,49.0)
    #sp.set_xlim(9.2,9.3)
 
    # time markings
    cDataVBOX.TimeMarkings(sp,time,UTM_x,UTM_y)
 
    # section with not enough satellites
    for lon_vec,lat_vec in sig['not_enough_Sats']:
      UTM_x_vec, UTM_y_vec, common_zone = kbtools.cCnvtGPS.LatLon2UTMxy(lat_vec,lon_vec)
      sp.plot(UTM_x_vec,UTM_y_vec,'rx-')
 
 
    fig.show()
