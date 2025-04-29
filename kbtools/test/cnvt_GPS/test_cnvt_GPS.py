"""
  
  Test case for cnvt_GPS

  Ulrich Guecker 2011-11-26
  
"""

'''
Unittest for dataeval\lib\kbtools\cnvt_GPS.py

    disp(' N 66 3.048'' E 017 53.220')
    disp(' UTM 33W E 630733 N 7328583')
    P(1).lat.D = 66;
    P(1).lat.M = 3.048;
    P(1).lat.sign = 1;  % north = pos
    P(1).lon.D = 17;
    P(1).lon.M = 53.220;
    P(1).lon.sign = 1;  % east = pos
    
    disp(' N 36 35.203'' W 05 4.052')
    disp(' UTM 30S W 315036 N 4051017')
    P(1).lat.D = 36;
    P(1).lat.M = 35.203;
    P(1).lat.sign = 1;  % north = pos
    P(1).lon.D = 5;
    P(1).lon.M = 4.052;
    P(1).lon.sign = -1;  % east = pos


'''

import unittest
import os

import numpy as np

import kbtools


#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self):
    ''' topic:            conversion different degree formats: D2DM and DM2D
        expected results: correct conversions
    '''

    print "test_TC001 - start"
    Test_passed = True
    
    # D (Grad):  N 48.1489027  E 011.8490660
    # DM (Grad, Dezimalminuten):   N 48 08.93416'  E 011 50.94396'
    # DMS (Grad, Minuten, Dezimalsekunden):  N 48 08' 56.050''  E 011 50' 56.637''

  
    # -----------------------------      
    lat_deg= 48.1489027 
    lon_deg= 11.8490660
    
    print lat_deg
    print "test D2DM()"
    [Grad,Dezimalminuten,Vorzeichen] = kbtools.cCnvtGPS.D2DM(lat_deg)
    print "D=<%2.0f>"%Grad,"M=<%08.5f>"%Dezimalminuten,"S=%d"%Vorzeichen

    if not ( "48" == ("%2.0f"%Grad)):                    
        Test_passed = False   
        print "Grad failed"
    if not ( "08.93416"  == ("%08.5f"%Dezimalminuten)):  
        Test_passed = False   
        print "Dezimalminuten failed"
    if not ( 0.0 < Vorzeichen):                          
        Test_passed = False   
        print "Vorzeichen failed"

    # -----------------------------      
    print "test D2DM()"
    Grad = kbtools.cCnvtGPS.DM2D(Grad,Dezimalminuten,Vorzeichen)
    print "<%10.7f>"%Grad
    if not ( "48.1489027" == "%10.7f"%Grad):  
        Test_passed = False
        print "Grad failed"
      
      
    # D (Grad):  N 48.1489027  E 011.8490660
    # DM (Grad, Dezimalminuten):   N 48 08.93416'  E 011 50.94396'
    # DMS (Grad, Minuten, Dezimalsekunden):  N 48 08' 56.050''  E 011 50' 56.637''
    lat_deg= 48.1489027 
    lon_deg= 11.8490660
 
    print kbtools.cCnvtGPS.sprint_LatLon(lat_deg,lon_deg) 
      
    # -----------------------------      
    # report results
    self.assertTrue(Test_passed) 

    print "test_TC001 - end"
    
  #------------------------------------------------------------------------  
  def test_TC002(self):
    ''' topic:            conversion LatLon2UTMxy and UTMxyToLatLon
        expected results: correct conversions
    '''
    
    print "test_TC002 - start"

    Test_passed = True
    
    
    print(' N 66 3.048'' E 017 53.220')
    print(' UTM 33W E 630733 N 7328583')

    # scalar
    lat_deg_org =  kbtools.cCnvtGPS.DM2D(66.0,3.048,1)   # north = pos
    lon_deg_org =  kbtools.cCnvtGPS.DM2D(17.0,53.220,1)  # east = pos
    print "lat = <%6.5f>"%lat_deg_org
    print "lon = <%7.5f>"%lon_deg_org

    x, y, common_zone = kbtools.cCnvtGPS.LatLon2UTMxy(lat_deg_org,lon_deg_org)
    print "common_zone = %d"%common_zone
    print "x = <%6.0f>"%x
    print "y = <%7.0f>"%y
       
    if not ( "33" == ("%d"%common_zone)):                    
        Test_passed = False   
        print "common_zone failed"
    if not ( "630733" == ("%6.0f"%x)):                    
        Test_passed = False   
        print "x failed"
    if not ( "7328583" == ("%7.0f"%y)):                    
        Test_passed = False   
        print "y failed"

    southhemi = 0  
    lat_deg_calc, lon_deg_calc = kbtools.cCnvtGPS.UTMxyToLatLon(x,y,common_zone,southhemi)
    print "lat = <%6.5f>"%lat_deg_calc
    print "lon = <%7.5f>"%lon_deg_calc
    if not ( "66.05080" == ( "%6.5f"%lat_deg_calc)):                    
        Test_passed = False   
        print "lat_deg_calc failed"
    if not ( "17.88700" == ( "%7.5f"%lon_deg_calc)):                    
        Test_passed = False   
        print "lon_deg_calc failed"
     
           
    # ----------------------------------------------------------- 
    # vector
    lat_deg =  np.array([kbtools.cCnvtGPS.DM2D(66.0,3.048,1),kbtools.cCnvtGPS.DM2D(66.0,3.048,1)])   # north = pos
    lon_deg =  np.array([kbtools.cCnvtGPS.DM2D(17.0,53.220,1),kbtools.cCnvtGPS.DM2D(17.0,53.220,1)])  # east = pos
    x, y, common_zone = kbtools.cCnvtGPS.LatLon2UTMxy(lat_deg,lon_deg)
    print x, y, common_zone
    # implicit tested
  
   
      
    # -----------------------------      
    # report results
    self.assertTrue(Test_passed) 
    
    print "test_TC002 - end"
  #------------------------------------------------------------------------  
  def test_TC003(self):
    ''' topic:            sprint_LatLon(lat_deg,lon_deg)
        expected results: correct conversions
    '''

    print "test_TC003 - start"
    Test_passed = True
    
    # D (Grad):  N 48.1489027  E 011.8490660
    # DM (Grad, Dezimalminuten):   N 48 08.93416'  E 011 50.94396'
    # DMS (Grad, Minuten, Dezimalsekunden):  N 48 08' 56.050''  E 011 50' 56.637''

  
    lat_deg= 48.1489027 
    lon_deg= 11.8490660
   
    s= kbtools.cCnvtGPS.sprint_LatLon(lat_deg,lon_deg) 
     
    print "s=<%s>"%s 
    if not ( "N 48 08.934 E 011 50.944" == s):                    
        Test_passed = False      
      
    # -----------------------------      
    # report results
    self.assertTrue(Test_passed) 
  
    print "test_TC003 - end"
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for cnvt_GPS'
  unittest.main()
  
  #test1()
  #raw_input("Press Enter to Exit")
  



  
