'''

   cnvt_GPS
   
   conversion and presentation of GPS signals from VBOX
   
   - UTM (Universal Transverse Mercator) projection -  x and y coordinates 
   - latitude/longitude
   
   methods:
   1) Latitude/Longitude-infomation -> UTM grid information
       x, y, common_zone = kbtools.cCnvtGPS.LatLon2UTMxy(lat_deg,lon_deg)
   2) UTM grid information -> Latitude/Longitude-infomation
      lat_deg, lon_deg = kbtools.cCnvtGPS.UTMxyToLatLon(x,y,common_zone,southhemi)
   
'''

# imports
import sys
import os
import pickle
import numpy as np
import pylab as pl
import scipy


'''
  if    isfield(in,'Sats_VBOX') ...
     && isfield(in,'Latitude_VBOX') ...
     && isfield(in,'Longitude_VBOX') ...
     && isfield(in,'t') 
  
    % Use only data with more then 3 satelite
    idx = find(in.Sats_VBOX>3);

    if ~isempty(idx)
      % Zeitachse
      in.t_VBOX = in.t(idx);    
    
      % GPS_distance
      in.GPS_distance_VBOX = s(idx);
    
      % VBOX : 
      %   tmp_Latitude  : North being positiv
      %   tmp_Longitude : West being positiv
      %   convention for conversion 
      %   Negative numbers indicate West
      in.Longitude_VBOX = -in.Longitude_VBOX;
    
      % VBOX:
      % Position recorded in minutes and not degree --> division with 60
      in.Longitude_VBOX = in.Longitude_VBOX / 60;
      in.Latitude_VBOX  = in.Latitude_VBOX / 60;            
    
      in.Latitude_Grad_VBOX    = in.Latitude_VBOX;
      in.Longitude_Grad_VBOX   = in.Longitude_VBOX;
'''




def main():

  Latitude_VBOX  = np.array([50.1, 50.2, 50.3, 50.4, 50.5])
  Longitude_VBOX = np.array([7.1, 7.2, 7.3, 7.4, 7.5])


  pos = {}
  # Latitude DDMM.M
  pos['Latitude']  = np.sign(Latitude_VBOX)*(np.floor(abs(Latitude_VBOX))*100.0 + (abs(Latitude_VBOX)-np.floor(abs(Latitude_VBOX)))*60.0);
 
  # Longitude DDMM.M
  pos['Longitude'] = np.sign(Longitude_VBOX)*(np.floor(abs(Longitude_VBOX))*100.0 + (abs(Longitude_VBOX)-np.floor(abs(Longitude_VBOX)))*60);
               
  print pos['Latitude']  
  print pos['Longitude']  
  
  '''  
      % convert to UTM WGS84 grid
      [in.x_UTM_km_VBOX,in.y_UTM_km_VBOX] = cnvt_GPS('GPS2UTMxy',pos);
      in.x_UTM_km_VBOX = in.x_UTM_km_VBOX/1000;
      in.y_UTM_km_VBOX = in.y_UTM_km_VBOX/1000;
  '''    
  
def test3(): 

  P = {}
 
  zone = 33;
  southhemi = 0;
  
  switch = 2
  if 1 == switch:
    print(' N 66 3.048'' E 017 53.220')
    print(' UTM 33W E 630733 N 7328583')
    
    P['lat.D']    = 66;
    P['lat.M']    = 3.048;
    P['lat.sign'] = 1;  # north = pos
    P['lon.D']    = 17;
    P['lon.M']    = 53.220;
    P['lon.sign'] = 1;  # east = pos
    
  if 2 == switch:
    print(' N 36 35.203'' W 05 4.052')
    print(' UTM 30S W 315036 N 4051017')
    P['lat.D']    = 36;
    P['lat.M']    = 35.203;
    P['lat.sign'] = 1;  # north = pos
    P['lon.D']    = 5;
    P['lon.M']    = 4.052;
    P['lon.sign'] = -1; # east = pos
  
    
  zone = np.floor((P['lon.sign']*P['lon.D']+183.0)/6.0);
  print zone
 
  """
  for P_tmp in P:
    print P_tmp
    if P_tmp['lat.sign'] >= 0:
      N_S = 'N';
    else:
      N_S = 'S';
    
    if P_tmp['lon.sign'] >= 0:
      W_E = 'E';
    else:
      W_E = 'W';
    
    print "%c %d %5.3f', %c %d %5.3f'" % (N_S,P['lat.D'],P['lat.M'],W_E,P['lon.D'],P['lon.M'])
  end
  """

#==================================================================================


#=========================================================================
def preproc_GPS_mouse(inp):
    '''
        in: N_Sat, 
            N_S (north = 0 or south != 0), 
            Latitude (DDMM.M), 
            W_E (west = 0 or east != 0), 
            Longitude (DDMM.M) 
        out : Longitude [D.DDDDDD]
              Latitude  [D.DDDDDD]
          
    '''
    
    out = {}
    
    required_signals = ['N_Sat', 'N_S', 'Latitude', 'W_E', 'Longitude']
    
    for signal in required_signals:
        if not (signal in inp):
            print "%s not include"%signal
            return out
  
   
    
    #  Negative numbers indicate West and South

    #  inp['N_S'][idx] : north = 0 or south != 0
    Latitude_Sign = np.where(inp['N_S'],-1,1)
    
    # Latitude DDMM.M
    Latitude_DDMM_M  = Latitude_Sign*inp['Latitude']
  
    # in.W_E(idx) : west = 0 or east != 0 
    Longitude_Sign = np.where(inp['W_E'],1,-1) 
    
    # Longitude DDMM.M
    Longitude_DDMM_M = Longitude_Sign*inp['Longitude']
  
    
    # --------------------------------------------------------------
    # inp['UTC'] -> in.t_UTC_GPS (UTC info from satelites)
    '''
    UTC = inp['UTC']    
    sec_t  = np.fmod(np.fix(UTC),100.0)+(UTC-np.fix(UTC)); 
    min_t  = np.fmod(np.fix(UTC/100.0),100.0);
    hour_t = np.fmod(np.fix(UTC/10000.0),100.0);
    t_UTC_GPS =  (((sec_t/60) + min_t)/60 + hour_t)/24;
    out['t_UTC_GPS'] = t_UTC_GPS.astype(np.float64)
    '''
  
    
    # convert to Lat Lon to degree with fraction of degree
    P ={}
    P['lat'] = {}
    P['lon'] = {}
    
    # Breitengrad
    P['lat']['D']    = np.floor(np.fabs(Latitude_DDMM_M)/100.0);
    P['lat']['M']    = np.fabs(Latitude_DDMM_M)-np.floor(np.fabs(Latitude_DDMM_M)/100.0)*100.0;
    P['lat']['sign'] = np.sign(Latitude_DDMM_M);
  
    # Laengengrad 
    P['lon']['D']    = np.floor(np.fabs(Longitude_DDMM_M)/100.0);
    P['lon']['M']    = np.fabs(Longitude_DDMM_M)-np.floor(np.fabs(Longitude_DDMM_M)/100.0)*100.0;
    P['lon']['sign'] = np.sign(Longitude_DDMM_M);
  
    out = {}
    
    out['Longitude'] = P['lon']['sign']*(P['lon']['D']+P['lon']['M']/60.0);
    out['Latitude']  = P['lat']['sign']*(P['lat']['D']+P['lat']['M']/60.0);
    out['N_Sat']     = inp['N_Sat']
    
    
    
    # Use only data with more then 3 satelite
    #idx = np.logical_and(inp['N_Sat']>3,inp['N_Sat']<25)
    #out['Longitude_Grad'][~idx] = np.nan
    #out['Latitude_Grad'][~idx] = np.nan
    
    return out
# ==========================================================


  

  
  
#==================================================================================
class cCnvtGPS():
  #--------------------------------------------------  
  def __init__(self):       # constructor
    self.get_const()
  
  
  #--------------------------------------------------  
  def get_const(self):
    # Ellipsoid model constants (actual values here are for WGS84) 
    self.const_sm_a           = 6378137.0;
    self.const_sm_b           = 6356752.314;
    self.const_sm_EccSquared  = 6.69437999013e-03;
    self.const_UTMScaleFactor = 0.9996;

  # --------------------------------------------------  
  # DeToRad
  # Converts degrees to radians.
  #
  def DegToRad (self,deg):
    return (deg / 180.0 * np.pi);
  
  #--------------------------------------------------  
  # RadToDeg
  # Converts radians to degrees.
  def RadToDeg (self,rad):
    return (rad / np.pi * 180.0);
  
  
  # --------------------------------------------------  
  # D (Grad):  N 48.1489027  E 011.8490660
  # DM (Grad, Dezimalminuten):   N 48 08.93416'  E 011 50.94396'
  # DMS (Grad, Minuten, Dezimalsekunden):  N 48 08' 56.050''  E 011 50' 56.637''
  @staticmethod
  def D2DM(Grad_in):
    Vorzeichen = np.sign(Grad_in);
    Grad = np.floor(abs(Grad_in));
    Dezimalminuten = (abs(Grad_in)-Grad)*60.0;
    #out = sprintf('N %d %08.5f''',Grad,Dezimalminuten);
    #disp(out)
    return [Grad,Dezimalminuten,Vorzeichen]

  @staticmethod
  def DM2D(Grad,Dezimalminuten,Vorzeichen):
    # Negative numbers indicate West longitudes and South latitudes  
    # north = 0  or south != 0
    # east  = 0  or west  != 0 
    Grad = Vorzeichen*(Grad + Dezimalminuten/60);
  
    #out = sprintf('N %08.5f',Grad);
    #disp(out)
    return Grad  

  @staticmethod
  def sprint_LatLon(lat_deg,lon_deg):
    [lat_D,lat_M,lat_sign] = cCnvtGPS.D2DM(lat_deg)
    [lon_D,lon_M,lon_sign] = cCnvtGPS.D2DM(lon_deg)
  
    # Laengen und Breitengrad
    if lat_sign<0:
      s_N_S = 'S';  
    else:
      s_N_S = 'N';   
     
    if lon_sign<0:
      s_W_E = 'W';  
    else:
      s_W_E = 'E';  
      
    return "%s %02d %06.3f %s %03d %06.3f"%(s_N_S,lat_D,lat_M,s_W_E,lon_D,lon_M)
 
  #--------------------------------------------------
  # convert latitude/longitude to UTM (Universal Transverse Mercator) projection -  x and y coordinates 
  # input: latitude/longitude in degree D
  # output: x and y coordinates  + zone
  @staticmethod
  def LatLon2UTMxy(lat_deg,lon_deg):  

    myCnvtGPS = cCnvtGPS()
 
    # step1: determine common_zone
    zone = np.floor((lon_deg+180)/6)+1;
    common_zone = np.median(zone);
  
    # step2: convert
    lat_rad = myCnvtGPS.DegToRad(lat_deg)
    lon_rad = myCnvtGPS.DegToRad(lon_deg)
    x, y = myCnvtGPS.LatLonZoneToUTMXY(lat_rad,lon_rad, common_zone);
  
    return x, y, common_zone
    
  #--------------------------------------------------
  # convert latitude/longitude to UTM (Universal Transverse Mercator) projection -  x and y coordinates 
  # output: x and y coordinates  + zone + southhemi
  # input: latitude/longitude in degree D
  @staticmethod
  def UTMxyToLatLon(x,y,zone,southhemi):  
    myCnvtGPS = cCnvtGPS()
   
    lat_rad,lon_rad = myCnvtGPS.UTMXYZoneToLatLon (x, y, zone, southhemi)
    lat_deg = myCnvtGPS.RadToDeg(lat_rad)
    lon_deg = myCnvtGPS.RadToDeg(lon_rad)
    
    return lat_deg, lon_deg 
 
  #--------------------------------------------------  
  # ArcLengthOfMeridian
  #
  # Computes the ellipsoidal distance from the equator to a point at a
  # given latitude.
  #
  # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
  # GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
  #
  # Inputs:
  #     phi - Latitude of the point, in radians.
  #
  # Globals:
  #     sm_a - Ellipsoid model major axis.
  #     sm_b - Ellipsoid model minor axis. 
  #
  # Returns:
  #     The ellipsoidal distance of the point from the equator, in meters.
  #
  def ArcLengthOfMeridian (self, phi):
        
    # Precalculate n 
    n = (self.const_sm_a - self.const_sm_b) / (self.const_sm_a + self.const_sm_b)

    # Precalculate alpha 
    alpha = ((self.const_sm_a + self.const_sm_b) / 2.0) * (1.0 + (n**2.0/4.0) + (n**4.0/64.0))

    # Precalculate beta 
    beta = (-3.0 * n / 2.0) + (9.0 * n**3.0/16.0) + (-3.0 * n**5.0/32.0)

    # Precalculate gamma 
    gamma = (15.0 * n**2.0/16.0) + (-15.0 * n**4.0/32.0)
    
    # Precalculate delta 
    delta = (-35.0 * n**3.0/48.0) + (105.0 * n**5.0/256.0)
    
    # Precalculate epsilon 
    epsilon = (315.0 * n**4.0 / 512.0)
    
    #  Now calculate the sum of the series and return 
    result = alpha * (phi + (beta    * np.sin (2.0 * phi))
                          + (gamma   * np.sin (4.0 * phi))
                          + (delta   * np.sin (6.0 * phi))
                          + (epsilon * np.sin (8.0 * phi)))
    
    return result
  #--------------------------------------------------  
  # UTMCentralMeridian
  #
  # Determines the central meridian for the given UTM zone.
  #
  # Inputs:
  #     zone - An integer value designating the UTM zone, range [1,60].
  #
  # Returns:
  #   The central meridian for the given UTM zone, in radians, or zero
  #   if the UTM zone parameter is outside the range [1,60].
  #   Range of the central meridian is the radian equivalent of [-177,+177].
  #
  #
  def UTMCentralMeridian (self, zone):
    cmeridian = self.DegToRad (-183.0 + (zone * 6.0))
    return cmeridian
    
  #--------------------------------------------------  
  # FootpointLatitude
  #
  # Computes the footpoint latitude for use in converting transverse
  # Mercator coordinates to ellipsoidal coordinates.
  #
  # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
  #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
  #
  # Inputs:
  #   y - The UTM northing coordinate, in meters.
  #
  # Returns:
  #   The footpoint latitude, in radians.
  #
  #
  def  FootpointLatitude (self, y):
       
    # Precalculate n (Eq. 10.18) */
    n = (self.const_sm_a - self.const_sm_b) / (self.const_sm_a + self.const_sm_b)
        	
    #  Precalculate alpha_ (Eq. 10.22) 
    # (Same as alpha in Eq. 10.17) 
    alpha_ = ((self.const_sm_a + self.const_sm_b) / 2.0) * (1.0 + n**2.0/4.0 + n**4.0/64.0)
        
    # Precalculate y_ (Eq. 10.23) 
    y_ = y / alpha_
        
    # Precalculate beta_ (Eq. 10.22) 
    beta_ = (3.0 * n / 2.0) + (-27.0 * n**3.0/32.0) + (269.0 * n**5.0/512.0)
        
    # Precalculate gamma_ (Eq. 10.22) 
    gamma_ = (21.0 * n**2.0/16.0) + (-55.0 * n**4.0/32.0)
        	
    # Precalculate delta_ (Eq. 10.22) 
    delta_ = (151.0 * n**3.0/96.0) + (-417.0 * n**5.0/128.0)
        	
    # Precalculate epsilon_ (Eq. 10.22) 
    epsilon_ = (1097.0 * n**4.0/512.0)
        	
    # Now calculate the sum of the series (Eq. 10.21) 
    result = (y_ + (beta_    * np.sin (2.0 * y_))
                 + (gamma_   * np.sin (4.0 * y_))
                 + (delta_   * np.sin (6.0 * y_))
                 + (epsilon_ * np.sin (8.0 * y_)))
                
    return result
      
  #--------------------------------------------------  
  # MapLatLonToXY
  #
  # Converts a latitude/longitude pair to x and y coordinates in the
  # Transverse Mercator projection.  Note that Transverse Mercator is not
  # the same as UTM; a scale factor is required to convert between them.
  #
  # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
  # GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
  #
  # Inputs:
  #   phi - Latitude of the point, in radians.
  #   my_lambda - Longitude of the point, in radians.
  #   lambda0 - Longitude of the central meridian to be used, in radians.
  #
  # Outputs:
  #    xy - A 2-element array containing the x and y coordinates
  #        of the computed point.
  #
  # Returns:
  #   The function does not return a value.
  #
  def MapLatLonToXY (self, phi, my_lambda, lambda0):
  
    # Precalculate ep2 
    ep2 = (self.const_sm_a**2.0  - self.const_sm_b**2.0) / self.const_sm_b**2.0
    
    # Precalculate nu2 
    nu2 = ep2 * np.cos(phi)**2.0
    
    # Precalculate N 
    N = self.const_sm_a**2 / (self.const_sm_b * np.sqrt(1.0 + nu2))
    
    # Precalculate t 
    t = np.tan(phi)
    t2 = t * t
    tmp = t2**3 - t**6 # ????

    # Precalculate l 
    l = my_lambda - lambda0
    
    # Precalculate coefficients for l**n in the equations below
    # so a normal human being can read the expressions for easting
    # and northing
    # -- l**1 and l**2 have coefficients of 1.0 */
    l3coef = 1.0 - t2 + nu2
    l4coef = 5.0 - t2 + 9.0 * nu2 + 4.0 * (nu2 * nu2)
    l5coef = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 - 58.0 * t2 * nu2
    l6coef = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2  - 330.0 * t2 * nu2
    l7coef = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)
    l8coef = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)
    
    # Calculate easting (x) 
    x = (   N          *  np.cos (phi) * l 
         + (N / 6.0    * (np.cos(phi))**3.0 * l3coef * (l**3.0))
         + (N / 120.0  * (np.cos(phi))**5.0 * l5coef * (l**5.0))
         + (N / 5040.0 * (np.cos(phi))**7.0 * l7coef * (l**7.0)))
    
    # Calculate northing (y) 
    y = (self.ArcLengthOfMeridian (phi)
        + (t /     2.0 * N * (np.cos(phi))**2.0 *          l**2.0)
        + (t /    24.0 * N * (np.cos(phi))**4.0 * l4coef * l**4.0)
        + (t /   720.0 * N * (np.cos(phi))**6.0 * l6coef * l**6.0)
        + (t / 40320.0 * N * (np.cos(phi))**8.0 * l8coef * l**8.0))
    
    return x,y
    
  #--------------------------------------------------  
  # MapXYToLatLon
  #
  # Converts x and y coordinates in the Transverse Mercator projection to
  # a latitude/longitude pair.  Note that Transverse Mercator is not
  # the same as UTM; a scale factor is required to convert between them.
  #
  # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
  #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
  #
  # Inputs:
  #   x - The easting of the point, in meters.
  #   y - The northing of the point, in meters.
  #   lambda0 - Longitude of the central meridian to be used, in radians.
  #
  # Outputs:
  #   philambda - A 2-element containing the latitude and longitude
  #               in radians.
  #
  # Returns:
  #   The function does not return a value.
  #
  # Remarks:
  #   The local variables Nf, nuf2, tf, and tf2 serve the same purpose as
  #   N, nu2, t, and t2 in MapLatLonToXY, but they are computed with respect
  #   to the footpoint latitude phif. 
  #
  #  x1frac, x2frac, x2poly, x3poly, etc. are to enhance readability and
  #   to optimize computations.
  def MapXYToLatLon (self, x, y, lambda0):   # , philambda
   	
    # Get the value of phif, the footpoint latitude. 
    phif = self.FootpointLatitude (y)
        	
    # Precalculate ep2 
    ep2 = (self.const_sm_a**2.0 - self.const_sm_b**2.0) / (self.const_sm_b**2.0)
        	
    # Precalculate cos (phif) 
    cf = np.cos(phif)
        	
    # Precalculate nuf2 
    nuf2 = ep2 * cf**2.0
        	
    # Precalculate Nf and initialize Nfpow 
    Nf = self.const_sm_a**2.0 / (self.const_sm_b * np.sqrt (1.0 + nuf2))
    Nfpow = Nf
        	
    # Precalculate tf 
    tf = np.tan (phif)
    tf2 = tf * tf
    tf4 = tf2 * tf2
        
    # Precalculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude. 
    x1frac = 1.0 / (Nfpow * cf)
        
    Nfpow = Nfpow*Nf    # now equals Nf**2) 
    x2frac = tf / (2.0 * Nfpow)
        
    Nfpow = Nfpow *Nf   # now equals Nf**3) 
    x3frac = 1.0 / (6.0 * Nfpow * cf)
        
    Nfpow = Nfpow*Nf    # now equals Nf**4) 
    x4frac = tf / (24.0 * Nfpow)
        
    Nfpow = Nfpow*Nf    # now equals Nf**5) 
    x5frac = 1.0 / (120.0 * Nfpow * cf)
        
    Nfpow = Nfpow*Nf    # now equals Nf**6) 
    x6frac = tf / (720.0 * Nfpow)
        
    Nfpow = Nfpow*Nf    # now equals Nf**7) 
    x7frac = 1.0 / (5040.0 * Nfpow * cf)
        
    Nfpow = Nfpow*Nf    # now equals Nf**8) 
    x8frac = tf / (40320.0 * Nfpow)
        
    # Precalculate polynomial coefficients for x**n.
    # -- x**1 does not have a polynomial coefficient. 
    x2poly = -1.0 - nuf2
    x3poly = -1.0 - 2.0 * tf2 - nuf2
    x4poly = 5.0+ 3.0*tf2 + 6.0*nuf2 - 6.0*tf2*nuf2 - 3.0*(nuf2 *nuf2) - 9.0*tf2*(nuf2*nuf2)
    x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2
    x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2
    x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)
    x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575.0 * (tf4 * tf2)
        	
    #  Calculate latitude 
    latitude =   ( phif + x2frac * x2poly * (x * x)
                       + x4frac * x4poly * x**4.0
                       + x6frac * x6poly * x**6.0
                       + x8frac * x8poly * x**8.0)
        	
    #  Calculate longitude 
    longitude = (lambda0 + x1frac * x
                        + x3frac * x3poly * x**3.0
                        + x5frac * x5poly * x**5.0
        	            + x7frac * x7poly * x**7.0)
    return latitude, longitude


  #--------------------------------------------------  
  # LatLonToUTMXY
  #
  # Converts a latitude/longitude pair to x and y coordinates in the
  # Universal Transverse Mercator projection.
  #
  # Inputs:
  #   lat - Latitude of the point, in radians.
  #   lon - Longitude of the point, in radians.
  #   zone - UTM zone to be used for calculating values for x and y.
  #          If zone is less than 1 or greater than 60, the routine
  #          will determine the appropriate zone from the value of lon.
  #
  # Outputs:
  #   xy - A 2-element array where the UTM x and y values will be stored.
  #
  # Returns:
  #   The UTM zone used for calculating the values of x and y.
  #
  def LatLonZoneToUTMXY (self, lat, lon, zone):
    x, y = self.MapLatLonToXY (lat, lon, self.UTMCentralMeridian (zone))

    # Adjust easting and northing for UTM system. 
    x = x * self.const_UTMScaleFactor + 500000.0;
    y = y * self.const_UTMScaleFactor;
    
    if isinstance(y,float):
      #print "scalar"
      if (y < 0.0):
        y = y + 10000000.0
    else:
      #print "array"
      Mask = y < 0.0
      y[Mask] = y[Mask] + 10000000.0
    
    return x,y  
    
  #--------------------------------------------------  
  # UTMXYToLatLon
  #
  # Converts x and y coordinates in the Universal Transverse Mercator
  # projection to a latitude/longitude pair.
  #
  # Inputs:
  # x - The easting of the point, in meters.
  # y - The northing of the point, in meters.
  # zone - The UTM zone in which the point lies.
  # southhemi - True if the point is in the southern hemisphere;
  #               false otherwise.
  #
  # Outputs:
  # latlon - A 2-element array containing the latitude and
  #            longitude of the point, in radians.
  #
  # Returns:
  # The function does not return a value.
  #
  def UTMXYZoneToLatLon (self, x, y, zone, southhemi):
      
    x = x- 500000.0;
    x = x / self.const_UTMScaleFactor;
        
    # If in southern hemisphere, adjust y accordingly. 
    # !!!!!!!
    if (southhemi):
      y = y -10000000.0;
        
    y = y/ self.const_UTMScaleFactor;
        
    cmeridian = self.UTMCentralMeridian (zone)
    lat,lon =  self.MapXYToLatLon (x, y, cmeridian)
        
    return  [lat,lon]

    
  
#=================================================================================

  
 