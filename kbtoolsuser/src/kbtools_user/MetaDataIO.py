'''
   Class to organize Meta Data of measurments

   Ulrich Guecker

   2014-10-01
'''

'''
todo:
  

'''

import os
import time
import numpy as np
import pylab as pl

import kbtools
import kbtools_user

#=================================================================================
def create_dbc_list():
    '''
       create a list of CANalyzer databasefiles for converting blf files to Matlab Binary
       
       under construction
    '''

    # list of dbc to be used for conversion
    DbcPathName = r"C:\KBData\DAS_eval\dbc"
    dbc_list = []
    
    # J1939
    #dbc_list.append(r'J1939_DAS_Ford.dbc')
    #dbc_list.append(r'J1939_DAS_ug_special.dbc')
    dbc_list.append(r'J1939_DAS.dbc')
    
    # private CAN
    #  a) Radar
    dbc_list.append(r'A087MB_V3.3draft_MH1.dbc')
    dbc_list.append(r'AC100_SMess_MKS 1.29.dbc')
    #  b) Camera
    dbc_list.append(r'Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc')
    dbc_list.append(r'Bendix_Info3.dbc')

    # Measurement Devices
    # OxTS
    dbc_list.append(r'OxTS_dbc\RTRangeLane.dbc')
    dbc_list.append(r'OxTS_dbc\rt3kfull_kph.dbc')
    dbc_list.append(r'OxTS_dbc\RTrange_kph.dbc')
    
    # Racelogic
    dbc_list.append(r'VBOX3iSL_ADAS_VCI_x.dbc')
    dbc_list.append(r'VBOX3i_LDWS_VCI_LatVel_mps.dbc')
   
    # -------------------------------------------------------------
    # add path    
    dbc_list = [ os.path.join(DbcPathName,dbc) for dbc in dbc_list]
   
    # remove non existing dbc files
    print "non existing dbc file: ", [ dbc for dbc in dbc_list if not os.path.exists(dbc)]
    dbc_list = [ dbc for dbc in dbc_list if os.path.exists(dbc)]
   
    return dbc_list

#=================================================================================
def create_dbc_list_MAN_GV():
    '''
       create a list of CANalyzer databasefiles for converting blf files to Matlab Binary
       
       under construction
    '''

    # list of dbc to be used for conversion
    DbcPathName = r"C:\KBData\DAS_eval\dbc"
    
    # list of tuples (CAN_Channel, dbc filename)
    dbc_list = []
    
    # J1939
    dbc_list.append((4, r'J1939_DAS.dbc'))
    
    # private CAN
    #  a) Radar
    dbc_list.append((2, r'A087MB_V3.3draft_MH1.dbc'))
    dbc_list.append((2, r'AC100_SMess_MKS 1.29.dbc'))
    #  b) Camera
    dbc_list.append((2, r'Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc'))
    dbc_list.append((2, r'Bendix_Info3.dbc'))
   
    # -------------------------------------------------------------
    # add path  
    dbc_list = [ "%d;%s"%(CAN_channel,os.path.join(DbcPathName,dbc)) for (CAN_channel, dbc) in dbc_list]
    
    print "create_dbc_list_MAN_GV", dbc_list
   
    # remove non existing dbc files
    print "non existing dbc file: ", [ element for element in dbc_list if not os.path.exists(element.split(';')[1])]
    dbc_list = [ element for element in dbc_list if os.path.exists(element.split(';')[1])]
   
    dbc_list = convert_DbcList(dbc_list) 
   
    print "dbc_list", dbc_list
    return dbc_list

# ===========================================================================
def convert_DbcList(DbcList):    
    
    if DbcList:
        DbcList_new = []
        for dbc_cfg in DbcList:
            dbc_new = {}
            dbc_cfg = dbc_cfg.split(';')
            if len(dbc_cfg)>1:
                dbc_new['CAN_Channel'] = int(dbc_cfg[0])
                dbc_new['dbc_file']    = dbc_cfg[1]
            else:
                dbc_new['dbc_file']    = dbc_cfg[0]
            DbcList_new.append(dbc_new)
        
        DbcList = DbcList_new
    print DbcList
    return DbcList
    
# ===========================================================================
class cFLC20CalibData(object):

    def __init__(self, VehicleName, verbose=False):
    
        self.verbose = verbose

        if self.verbose:
            print "VehicleName", VehicleName
    
   
        # -----------------------------------------------------
        # hard coded parameters
        #   leftWheel               : absolute distance from camera to outer edge of left wheel  
        #   rightWheel              : absolute distance from camera to outer edge of right wheel
        #                              Remark: Both leftWheel and rightWheel are positive values
        #   corridor_outer_boundary : todo
        #   warning_line_tlc        : todo 
        #   dx_camera_to_front_axle : longitudinal distance from camera to front axle (required by Burcu) 
    
        if VehicleName == "DE_DV1":
            # Dennis Eagle Development Vehicle 1
            
            leftWheel  = 110 # [m] 
            rightWheel = 110 # [m] 

            corridor_outer_boundary = 40 # cm  todo check
            warning_line_tlc = 0   # cm todo check
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m] todo check 
    
        elif VehicleName == "Ford_H566PP":
            # Ford H566PP
            
            leftWheel  = 127 # [m]
            rightWheel = 107 # [m]
            leftWheel  = 130 # [m]
            rightWheel = 108 # [m]
        
            corridor_outer_boundary = 40 # cm
            warning_line_tlc = 0   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m] Ford 
            
        elif VehicleName == "Ford_M1SH8":
            # Ford_M1SH8
            leftWheel  = 124 # [m]
            rightWheel = 110 # [m]
        
            corridor_outer_boundary = 40 # cm
            warning_line_tlc = 0   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m] Ford  todo
            
        elif VehicleName == "Ford_M1SH9":
            # Ford_M1SH9
            leftWheel  = 124 # [m]
            rightWheel = 110 # [m]
        
            corridor_outer_boundary = 40 # cm
            warning_line_tlc = 0   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m] Ford  todo

        elif VehicleName == "Ford_M1SH10":
            # Ford_M1SH10
            
            leftWheel  = 122 # [m]
            rightWheel = 110 # [m]
        
            corridor_outer_boundary = 40 # cm
            warning_line_tlc = 0   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m] Ford  todo
           
        elif VehicleName == "Karsan_JEST_Minibus":
            # Karsan 
            #leftWheel  =  110   # [cm]
            #rightWheel =   92   # [cm]
            
            leftWheel  =  93   # [cm]
            rightWheel =  111   # [cm]
        
            corridor_outer_boundary = 50 # cm
            warning_line_tlc        = -10   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
        
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.0  # [m]  

        elif VehicleName == "Karsan_MPXL_Midibus":
            leftWheel  =  115   # [cm]
            rightWheel =  115   # [cm]
        
            corridor_outer_boundary = 50 # cm
            warning_line_tlc        = -10   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.0  # [m]  
                     
        elif VehicleName == "HMC_Bus":
            # HMC_Bus 
            leftWheel  =  107   # [cm]
            rightWheel =  129   # [cm]
                    
            corridor_outer_boundary = 50 # cm
            warning_line_tlc        = -10   # cm
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
        
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.0  # [m] 
            
        elif VehicleName == "MAN_06xB365":
            # MAN_06xB365   
            # todo: fill in specific data; currently dummy data
            leftWheel  = 110 # [m] 
            rightWheel = 110 # [m] 

            corridor_outer_boundary = 40 # cm  
            warning_line_tlc = 0   # cm 
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m]  
    
        elif VehicleName == "MAN_GV":
            # MAN_GV   
            # todo: fill in specific data; currently dummy data
            leftWheel  = 110 # [m] 
            rightWheel = 110 # [m] 

            corridor_outer_boundary = 40 # cm  
            warning_line_tlc = 0   # cm 
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m]  
            
        else:
            # dummy
            leftWheel  = 110 # [m] 
            rightWheel = 110 # [m] 

            corridor_outer_boundary = 40 # cm  
            warning_line_tlc = 0   # cm 
            warn_margin_left        =  15 # cm Distance from marking inner edge to nominal warning location on left side; positive towards outside of marking
            warn_margin_right       =  15 # cm Distance from marking inner edge to nominal warning location on right side; positive towards outside of marking        
            
            # longitudinal distance from camera to front axle
            dx_camera_to_front_axle = 1.292  # [m]  

    
        if self.verbose:
            print "leftWheel               ",leftWheel
            print "rightWheel              ",rightWheel
            print "corridor_outer_boundary ", corridor_outer_boundary
            print "warn_margin_left        ", warn_margin_left
            print "warn_margin_right       ", warn_margin_right
            print "dx_camera_to_front_axle ", dx_camera_to_front_axle
            

            
        CalibData = {}
        CalibData["leftWheel"]               = leftWheel
        CalibData["rightWheel"]              = rightWheel
        CalibData["corridor_outer_boundary"] = corridor_outer_boundary
        CalibData["warning_line_tlc"]        = warning_line_tlc
        CalibData["warn_margin_left"]        = warn_margin_left
        CalibData["warn_margin_right"]       = warn_margin_right
        CalibData["dx_camera_to_front_axle"] = dx_camera_to_front_axle
        
        self.CalibData = CalibData
        
    # -----------------------------------------------------
    def GetData(self):
        return self.CalibData
        
# ===========================================================================
class cTestTrackData(object):

    def __init__(self, FullFileName, verbose=False):

        print "FullFileName", FullFileName
    
        width_lane_marking_left = 23  # cm
        width_lane_marking_right = 12  # cm

        TestTrackData = {}
        TestTrackData["width_lane_marking_left"]               = width_lane_marking_left
        TestTrackData["width_lane_marking_right"]              = width_lane_marking_right
        
        
        self.TestTrackData = TestTrackData
        
    # -----------------------------------------------------
    def GetData(self):
        return self.TestTrackData
 
# ===========================================================================
class cMetaDataIO(object):

    def __init__(self,VehicleName, verbose=False):
        self.VehicleName = VehicleName
        self.verbose = verbose
        
        
    def GetMetaData(self,category='FLC20CalibData'):
        if category=='FLC20CalibData':
            FLC20CalibData = cFLC20CalibData(self.VehicleName,verbose=self.verbose)
            return FLC20CalibData.GetData()
        elif category=='TestTrackData':
            TestTrackData = cTestTrackData(self.VehicleName, verbose=self.verbose)
            return TestTrackData.GetData()
        elif category=='dbc_list':
            if self.VehicleName == "MAN_GV":
                return create_dbc_list_MAN_GV()
            else:
                return create_dbc_list()
        else:
            return None
    
# ===========================================================================
if __name__ == "__main__":
   
    myMetaData = cMetaDataIO('Ford_H566PP',verbose=True)
    CalibData = myMetaData.GetMetaData(category='FLC20CalibData')
    
    print CalibData
    
            