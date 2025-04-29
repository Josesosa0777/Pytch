"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\svf.py
'''

import numpy as np
#import matplotlib.pyplot as plt

import unittest
#import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
     
    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: svf_1o
            expected results:  
        '''
    
        t              = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
        x              = np.array([0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        T=0.3
        f_x2_expected  = np.array([ 0., 0.16666667, 0.47222222,  0.69907407,  0.83719136,  0.91448045,  0.95586848,  0.97747699,  0.98858608,  0.99424224,  0.83043752,  0.52632422,  0.30019727,  0.16244369,  0.08533686,  0.0440401,   0.02247728,  0.01139105,  0.00574633,  0.0028901,   0.00145069])   
        df_x2_expected = np.array([ 0., 3.33333333, 2.77777778, 1.75925926, 1.00308642, 0.54269547, 0.28506516, 0.14710505, 0.07507668, 0.03804639, -3.31414079, -2.76812505, -1.75441408, -1.00065756, -0.54147895, -0.2844562,  -0.14680034, -0.07492425,  -0.03797015, -0.01915442, -0.00963366])
    
        df_x2, f_x2 = kbtools.svf_1o(t,x, T=T)
        
        print "f_x2          ",f_x2
        print "f_x2_expected ",f_x2_expected
        print "df_x2         ",df_x2
        print "df_x2_expected",df_x2_expected
    
        for x1,x2 in zip(f_x2,f_x2_expected):
            print x1,x2
            self.assertAlmostEqual(x1, x2, places=5, msg="")

        for x1,x2 in zip(df_x2,df_x2_expected):
            print x1,x2
            self.assertAlmostEqual(x1, x2, places=5, msg="")

    #------------------------------------------------------------------------  
    def test_TC002(self):
        ''' topic: svf_1o
            expected results:  
        '''
    
        t              = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
        x              = np.array([0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0])
        valid          = np.array([0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0])
        
        T=0.3
        f_x2_expected  = np.array([ 0., 1., 1., 1., 1., 1., 1., 1., 1., 1., 0., 0., 1., 0.83333333,  0.69444444,  0.77314815,  0.86188272,  0.92271091,  0.95861197,  0.97839149,  0. ])
        df_x2_expected = np.array([ 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,-3.33333333,  0.55555556,  1.01851852,  0.75617284,  0.46039095,  0.25763032,  0.13796011,  0. ])
        
        df_x2, f_x2 = kbtools.svf_1o(t,x, T=T, valid=valid)
        
        print "f_x2          ",f_x2
        print "f_x2_expected ",f_x2_expected
        print "df_x2         ",df_x2
        print "df_x2_expected",df_x2_expected
    
        for x1,x2 in zip(f_x2,f_x2_expected):
            print x1,x2
            self.assertAlmostEqual(x1, x2, places=5, msg="")

        for x1,x2 in zip(df_x2,df_x2_expected):
            print x1,x2
            self.assertAlmostEqual(x1, x2, places=5, msg="")
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
    print 'unittest for LPF_butter'
    unittest.main()
  



  
