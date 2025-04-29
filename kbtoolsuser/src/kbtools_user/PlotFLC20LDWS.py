'''
   Class to create different kinds of plots for LDWS on FLC20

   Ulrich Guecker

   2014-10-29 COneSide
   2014-10-15 cPlotFLC20LDWSBase
   2014-09-03
'''

'''
todo:
  - read in vehicle application parameter  (currently they are hard coded and selected by vehicle name
  - explain corridor_outer_boundary, warning_line_tlc in _GetVehicleParameters()
  - todo caluculate road curvature based only on J1939 signls
  - todo select correct vehicle speed from J1939

    

'''

import os
import time
import numpy as np
import pylab as pl
import sys, traceback
import scipy 


import kbtools
import kbtools_user

# ===========================================================================
def fit_line(t_LDW_Right_start, t_Right_C0, Right_C0, N=5):
    '''
       lateral speed : straight line fit to previous points
    '''
    
    idx_t_LDW_Right = np.argwhere(t_Right_C0>t_LDW_Right_start)[0]
    print "idx_t_LDW_Right", idx_t_LDW_Right
 
    x = t_Right_C0[idx_t_LDW_Right-N:idx_t_LDW_Right]
    y = Right_C0[idx_t_LDW_Right-N:idx_t_LDW_Right]
    print x,y
    try:
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)
    except ValueError:
        slope     = None
        intercept = None
        r_value   = None
        p_value   = None
        std_err   = None
           
    print slope, intercept, r_value, p_value, std_err 
        
    return slope, intercept, x, y

# ==========================================================
# ==========================================================
class COneSide(object):
    '''
       signal data structure for one side (left or right)
    '''
    
    def __init__(self, side):
        
        self.side = side
        
        self.FileName = None
        self.LDW_okay           = None
        self.t_LDW_start        = None
        self.Wheel              = None
        self.width_lane_marking = None
        
        
        self.t_LaneDepartImminent = None
        self.LaneDepartImminent   = None
        
        self.Time_OxTS_LinePosLateral     = None
        self.OxTS_LinePosLateral          = None
        self.Time_OxTS_LineVelLateral     = None
        self.OxTS_LineVelLateral_smoothed = None
        
            
        self.Time_VBOX_Range_t       = None
        self.VBOX_Range_t            = None
        self.Time_VBOX_Lat_Spd_t     = None
        self.VBOX_Lat_Spd_t_smoothed = None
        
                
        self.t_C0 = None
        self.C0   = None
        self.lateral_speed = None
        
        # values at rising edge of lane departure imminent warning
        self.C0_at_t_LDW                           = None
        self.C0_wheel_at_t_LDW                     = None
        self.C0_wheel_filtered_at_t_LDW            = None
        self.lateral_speed_at_t_LDW                = None
        self.FrontAxleSpeed_at_t_LDW               = None
        self.YawRate_at_t_LDW                      = None
        self.ay_calc_at_t_LDW                      = None
        self.OxTS_LinePosLateral_at_t_LDW          = None
        self.OxTS_LineVelLateral_smoothed_at_t_LDW = None
        self.VBOX_Range_t_at_t_LDW                 = None
        self.VBOX_Lat_Spd_t_smoothed_at_t_LDW      = None
        self.VBOX_Velocity_kmh_at_t_LDW            = None
            
        
# ==========================================================
class cPlotFLC20LDWSBase(object):
 
    # ==========================================================
    def __init__(self, FLR20_sig, t_event, xlim=None, PngFolder = r".\png", VehicleName=None, show_figures=False, cfg={} ,verbose=False):
    
        if verbose:
            print "cPlotFLC20LDWSBase()"
    
        self.FullFileName = None
        # -------------------------------------------
        # parameters
        self.input_mode = None
        if isinstance(FLR20_sig, dict):
            self.input_mode = "FLR20_sig"
            self.FLR20_sig    = FLR20_sig
            self.FullFileName = self.FLR20_sig['FileName']
            
            # ------------------------------------------------------------------
            # FileName of measurement 
            if 'FileName' in self.FLR20_sig:
                # FileName is basename without file extension
                FileName = os.path.basename(self.FLR20_sig['FileName'])
                (prefix, sep, suffix) = FileName.rpartition('.') # strip off file extension
                self.FileName = prefix
            else:
                self.FileName = ''
            self.xlim         = xlim    

        elif isinstance(FLR20_sig, kbtools.CSimOL_MatlabBinInterface):
            self.input_mode = "SilLDWS_C"
            SilLDWS_C = FLR20_sig
            print "CSimOL_MatlabBinInterface detected"
            self.sim_input        = SilLDWS_C.matdata_input
            self.sim_output       = SilLDWS_C.matdata_output
            self.expected_results = SilLDWS_C.matdata_expected_results
            self.sim_parameters   = SilLDWS_C.matdata_parameters
            self.FileName         = SilLDWS_C.BaseName   # BaseName@t_start
            
            
            self.Description      = SilLDWS_C.Description
            self.xlim             = SilLDWS_C.xlim
            self.FLR20_sig        = SilLDWS_C.FLR20_sig 
        else:
            print "FLR20_sig not correct"
            raise
       
        self.t_event      = t_event
              
        self.PngFolder    = PngFolder
        self.VehicleName  = VehicleName
        self.show_figures = show_figures
        #self.cfg          = cfg
        self.verbose      = verbose

        # ---------------------------------------------
        # define pre and post trigger
        self.pre_trigger = 5.0       # 2.0
        self.post_trigger = 6.0
        
        # ---------------------------------------------
        # set plot origin to t_event and adjust xlim 
        if self.t_event is None:
            self.t_ref = 0.0
            print "self.t_event is None"
        else:
            self.t_ref = self.t_event
        
        if (self.t_ref is not None) and (self.xlim is not None):
            
            use_pre_and_post_trigger = False
            if abs(self.t_ref - self.xlim[0]) < 0.1:
                use_pre_and_post_trigger = True
                
            if use_pre_and_post_trigger:
                self.xlim_default = (self.xlim[0]-self.pre_trigger-self.t_ref, self.xlim[1]+self.post_trigger-self.t_ref)
            else:
                self.xlim_default = (self.xlim[0]-self.t_ref, self.xlim[1]-self.t_ref)
        else:
            self.xlim_default = self.xlim
            
        self.xlim_to_use(self.xlim_default)
       
       
        # -------------------------------------------
        # internal switches 
        
        # select lateral speed 
        self.lateral_speed_selection = 'Measurement'    # 'Heading' 'TimeDerivative' 'Measurement'
        #self.lateral_speed_selection = 'Heading'
        
        
        # ---------------------------------------------
        self.show_C0 = 1                       # distance := C0 - Wheel
        
        self.show_C0_wheel = 0                 # distance := C0_wheel  (BendixInfo)
        if 'show_C0_wheel' in cfg:
            if cfg['show_C0_wheel']:
                self.show_C0_wheel = 1                 # distance := C0_wheel  (BendixInfo)
            
        
             

        self.do_fitted_5_points_line = False
        
        # ---------------------------------------------
        self.customer_version = False                
        if 'customer_version' in cfg:
            if cfg['customer_version']:
                self.customer_version = True                 

        # ---------------------------------------------
        self.VBOX_Range_Lt_Offset = 0.0
        self.VBOX_Range_Rt_Offset = 0.0
        
        if 'VBOX_Range_Lt_Offset' in cfg:
            self.VBOX_Range_Lt_Offset = cfg['VBOX_Range_Lt_Offset']
        if 'VBOX_Range_Rt_Offset' in cfg:
            self.VBOX_Range_Rt_Offset = cfg['VBOX_Range_Rt_Offset']
        print "VBOX_Range_Lt_Offset", self.VBOX_Range_Lt_Offset
        print "VBOX_Range_Rt_Offset", self.VBOX_Range_Rt_Offset
        
        # ---------------------------------------------
        self.VBOX_Range_Lt_ref_edge = 'inner'     # 'inner' | 'outer' edge of the lane marking
        self.VBOX_Range_Rt_ref_edge = 'inner'     # 'inner' | 'outer' edge of the lane marking
        
        if 'VBOX_Range_Lt_ref_edge' in cfg:
            self.VBOX_Range_Lt_ref_edge = cfg['VBOX_Range_Lt_ref_edge']
        if 'VBOX_Range_Rt_ref_edge' in cfg:
            self.VBOX_Range_Rt_ref_edge = cfg['VBOX_Range_Rt_ref_edge']
        print "VBOX_Range_Lt_ref_edge",self.VBOX_Range_Lt_ref_edge
        print "VBOX_Range_Rt_ref_edge",self.VBOX_Range_Rt_ref_edge
    
        # ------------------------------------------------------------------
        # calculate vehicle specific parameters
        self._GetVehicleParameters(self.VehicleName)
        self._GetTestTrackData(self.FullFileName)
        
        # ------------------------------------------------------------------
        # preprocess signals  (do not change sequence)
        self._get_Lane_Departure_Warning_Signals()
        self._get_Road_curvature()
        self._get_actual_vehicle_speed()
        self._get_lane_info()
        self._get_lateral_speed()
        self._get_Ford_Oxford_Measurement_Equipment()
        self._get_VBOX_LDWS_VCI()
        self._get_LDW_event_attributes() 
        
        
        # ------------------------------------------------------------------
        # close up range for x-axis
        self.xlim_closeup = self.xlim
        if self.LDW_Right_okay:
            self.xlim_closeup = (self.t_LDW_Right_start-self.t_ref-self.pre_trigger, self.t_LDW_Right_stop-self.t_ref+self.post_trigger)
        elif self.LDW_Left_okay:
            self.xlim_closeup  = (self.t_LDW_Left_start-self.t_ref-self.pre_trigger, self.t_LDW_Left_stop-self.t_ref+self.post_trigger)
        else:
            self.xlim_closeup  = (-5.0,5.0)       
            
        # -------------------------------------------------------------------
        #  current plot 
        self.PlotName = None  # specific name of the png file
        self.fig      = None       # figure to show and save as png to disk

        
        if self.verbose:
            print "cPlotFLC20LDWSBase() - end"
            print "   xlim", self.xlim
            print "   t_ref", self.t_ref
            print "   xlim_default", self.xlim_default
            print "   xlim_closeup", self.xlim_closeup
   
    # --------------------------------------------------------------------------------------------------------
    def GetList(self,side):
        if side == 'left':
           return self.left
        if side == 'right':
           return self.right
        
    # --------------------------------------------------------------------------------------------------------
    def xlim_to_use(self, xlim):
        '''
           set xlim for the next figure
        '''
        self._xlim_to_use = xlim
          
    # --------------------------------------------------------------------------------------------------------
    def set_xlim(self, ax):
        '''
        
        '''
        ax.grid()
        if self._xlim_to_use:
            ax.set_xlim(self._xlim_to_use)
            
            
    # --------------------------------------------------------------------------------------------------------
    def set_description(self, ax, ylabel, yrange):
        '''
           set description of subplot
        '''
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if yrange is not None:
            ax.set_ylim(yrange[0],yrange[1])          
        ax.legend()
        self.set_xlim(ax)
        
    # --------------------------------------------------------------------------------------------------------
    def mark_point(self, ax, t,x, LineStyle='',FmtStr='%3.1f'  ):
        ax.plot(t,x,LineStyle)              # Marker
        ax.text(t,x,FmtStr%(x,))       # Label
    
    #=================================================================================
    def start_fig(self,PlotName="noname", FigNr=100):
        '''
           create a current figure to put subplots in 
           set PlotName and create a subtitle
        '''
        self.PlotName = PlotName  # specific name of the png file
        
        
        fig = pl.figure(FigNr)  
        fig.clf()
        
        if self.input_mode == "FLR20_sig":
            fig.suptitle("LDWS %s(%s@%.2fs)"%(PlotName,os.path.join(self.PngFolder,self.FileName),self.t_event))
        elif self.input_mode == "SilLDWS_C":
            fig.suptitle("%s (%s) %s"%(self.PlotName,self.FileName,self.Description))
    
        self.fig = fig            # figure to show and save as png to disk
        return fig
      

    #=================================================================================
    def show_and_save_figure(self):
        '''
           show current figire and create a png
        '''        
            
        if self.PlotName is None or self.fig is None:
            print "error show_and_save_figure"
            return
            
            
        if self.show_figures:
            self.fig.show()
            
        if self.input_mode == "FLR20_sig":
            kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName, self.t_event)
        
        elif self.input_mode == "SilLDWS_C":
            # self.FileName already contains @<t_event>
            kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName)
            
        # reset    
        self.PlotName = None  
        self.fig      = None  
        self.xlim_to_use(self.xlim_default)
   
    #=================================================================================
    def _GetTestTrackData(self, FullFileName):
    
        print "_GetTestTrackData(%s)"%FullFileName
    
        try:        
            myMetaData = kbtools_user.cMetaDataIO(FullFileName,verbose = self.verbose)
            TestTrackData = myMetaData.GetMetaData(category='TestTrackData')

            self.width_lane_marking_left  = TestTrackData["width_lane_marking_left"]/100.0   
            self.width_lane_marking_right = TestTrackData["width_lane_marking_right"]/100.0 

        except:    
            self.width_lane_marking_left  = None  
            self.width_lane_marking_right = None  
            
        # LM lane marking
        self.width_lane_marking_left = 0.23
        self.width_lane_marking_right = 0.12    
            
        print  "width_lane_marking_left",  self.width_lane_marking_left
        print  "width_lane_marking_right",  self.width_lane_marking_right

        
        
        
   
    #=================================================================================
    def _GetVehicleParameters(self, VehicleName):
        '''
            select and calculate the vehicle specific parameters
        
        '''
    
    
        if self.verbose:
            print "VehicleName", VehicleName
    
        # -----------------------------------------------------
        # hard coded parameters
        #   leftWheel              : absolute distance from camera to outer edge of left wheel  
        #   rightWheel             : absolute distance from camera to outer edge of right wheel
        #                             Remark: Both leftWheel and rightWheel are positive values
        #   corridor_outer_boundary : todo
        #   warning_line_tlc        : todo 
        #   dx_camera_to_front_axle : longitudinal distance from camera to front axle
    
    
        myMetaData = kbtools_user.cMetaDataIO(VehicleName,verbose = self.verbose)
        CalibData = myMetaData.GetMetaData(category='FLC20CalibData')
        
       
        leftWheel               = CalibData["leftWheel"] 
        rightWheel              = CalibData["rightWheel"]              
        corridor_outer_boundary = CalibData["corridor_outer_boundary"]
        warning_line_tlc        = CalibData["warning_line_tlc"] 
        warn_margin_left        = CalibData["warn_margin_left"]
        warn_margin_right       = CalibData["warn_margin_right"]  
        
        
        dx_camera_to_front_axle = CalibData["dx_camera_to_front_axle"]

    
        if self.verbose:
            print "leftWheel               ",leftWheel
            print "rightWheel              ",rightWheel
            print "corridor_outer_boundary ", corridor_outer_boundary
            print "warning_line_tlc        ", warning_line_tlc
            print "warn_margin_left        ", warn_margin_left
            print "warn_margin_right       ", warn_margin_right
            print "dx_camera_to_front_axle ", dx_camera_to_front_axle

            
        # ---------------------------------------
        # vehicle parameter from simulation
        '''
        try:
            self.VehicleWidth = self.sim_output['EOLDistToLtWheel'][0] + self.sim_output['EOLDistToRtWheel'][0]
            self.VehicleWidthHalf = self.vehicle_width/2.0
        except:
            self.VehicleWidth = 0.0   
            self.VehicleWidthHalf = 0.0
        ''' 
            
            
    
        self.VehicleWidth = (rightWheel+leftWheel)/100.0
        self.VehicleWidthHalf = self.VehicleWidth/2.0
        
        
        self.WheelRight       =  self.VehicleWidthHalf
        self.WheelLeft        = -self.VehicleWidthHalf
                
        #self.WheelRight       =  (rightWheel)/100.0
        #self.WheelLeft        = -(leftWheel)/100.0

        
        #WarningLine_Right =   VehicleWidthHalf+warning_line_tlc/100.0
        #WarningLine_Left  = -(VehicleWidthHalf+warning_line_tlc/100.0)
    
        #self.WarningLineRight =  warning_line_tlc/100.0 
        #self.WarningLineLeft  = -warning_line_tlc/100.0 
        
        self.WarningLineRight = -warn_margin_right/100.0 
        self.WarningLineLeft  =  warn_margin_left/100.0 
        
      
    
        self.corridor_outer_boundary = corridor_outer_boundary

        self.dx_camera_to_front_axle = dx_camera_to_front_axle 
 
    # ===========================================================================
    def _get_Road_curvature(self):
        '''
           Road curvature
        '''   
        
        # todo caluculate road curvature based only on J1939 signls
        try:
            self.t_road_curvature = self.FLR20_sig['General']['Time']                           # FLR20 A087  !!!
            self.road_curvature   = self.FLR20_sig['General']['estimated_road_curvature']       # FLR20 A087  !!!
        except:
            self.t_road_curvature = None
            self.road_curvature   = None
            
    # ===========================================================================
    def _get_actual_vehicle_speed(self):
        '''
           actual vehicle speed
        '''
        
        # todo select correct vehicle speed
        try:
            self.t_actual_vehicle_speed = self.FLR20_sig['General']['Time']
            self.actual_vehicle_speed   = self.FLR20_sig['General']['actual_vehicle_speed']
        except:
            try: 
                self.t_actual_vehicle_speed = self.FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
                self.actual_vehicle_speed   = self.FLR20_sig['J1939']["WheelbasedVehSpd"]/3.6  # km/h -> m/s
            except:
                self.t_actual_vehicle_speed = None
                self.actual_vehicle_speed   = None
 
        # ------------------------------------------------------
        try:   
            self.t_FrontAxleSpeed = self.FLR20_sig["J1939"]["Time_MeanSpdFA"]
            self.FrontAxleSpeed   = self.FLR20_sig["J1939"]["MeanSpdFA"]/3.6  # km/h -> m/s
        except:
            try:
                self.t_FrontAxleSpeed = self.FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
                self.FrontAxleSpeed   = self.FLR20_sig['J1939']["WheelbasedVehSpd"]/3.6  # km/h -> m/s      
            except:
                try:
                    self.t_FrontAxleSpeed = self.sim_input['t']
                    self.FrontAxleSpeed   = self.sim_input['FrontAxleSpeed']/3.6  # km/h -> m/s 
                except:   
                    self.t_FrontAxleSpeed = None
                    self.FrontAxleSpeed   = None  
                             
        # ---------------------------------------------------------
        if self.input_mode == "FLR20_sig":
            self.Time_YawRate = self.FLR20_sig['J1939']["Time_YawRate"]       
            self.YawRate      = self.FLR20_sig['J1939']["YawRate"]
        elif self.input_mode == "SilLDWS_C":
            try:
                self.Time_YawRate = self.sim_input['Time_YawRate']      
                self.YawRate      = self.sim_input['YawRate'] 
            except:
                self.Time_YawRate = None     
                self.YawRate      = None
        else:
            self.Time_YawRate = None     
            self.YawRate      = None
        
        # ---------------------------------------------------------
        if self.input_mode == "FLR20_sig":
            try: 
                self.Time_VBOX_Velocity_kmh = self.FLR20_sig["VBOX_IMU"]["Time_Velocity_kmh"]
                self.VBOX_Velocity_kmh      = self.FLR20_sig["VBOX_IMU"]["Velocity_kmh"]
            except:
                self.Time_VBOX_Velocity_kmh = None
                self.VBOX_Velocity_kmh      = None
        elif self.input_mode == "SilLDWS_C":
            try: 
                self.Time_VBOX_Velocity_kmh = self.sim_input["Time_VBOX_Velocity_kmh"]
                self.VBOX_Velocity_kmh      = self.sim_input["VBOX_Velocity_kmh"]
            except:
                self.Time_VBOX_Velocity_kmh = None
                self.VBOX_Velocity_kmh      = None
        else: 
            self.Time_VBOX_Velocity_kmh = None
            self.VBOX_Velocity_kmh      = None
        
        # calculate some signals
        # lateral acceleration ay=wz*v   wz=yawrate; v:vehicle speed
        if (self.Time_YawRate is not None) and (self.t_FrontAxleSpeed is not None):
            self.Time_ay_calc = self.Time_YawRate
            self.ay_calc = self.YawRate * kbtools.resample(self.t_FrontAxleSpeed, self.FrontAxleSpeed, self.Time_YawRate, method='zoh')
        else:
            self.Time_ay_calc = None
            self.ay_calc = None
            
         
         
        

    # ===========================================================================
    def _get_lane_info(self):
        '''
           lane information
        '''

        # ===========================================================================
        # lane tracking status
        if self.input_mode == "FLR20_sig":
            self.t_LDW_Left_Tracking   = self.FLR20_sig["J1939"]["Time_LaneTrackingStatusLeft"]
            self.LDW_Left_Tracking     = self.FLR20_sig["J1939"]["LaneTrackingStatusLeft"]
            self.t_LDW_Right_Tracking  = self.FLR20_sig["J1939"]["Time_LaneTrackingStatusRight"]
            self.LDW_Right_Tracking    = self.FLR20_sig["J1939"]["LaneTrackingStatusRight"]

        elif self.input_mode == "SilLDWS_C":
            self.t_LDW_Left_Tracking   = self.sim_input['t']
            self.LDW_Left_Tracking     = self.sim_input['LDW_Left_Tracking']
            self.t_LDW_Right_Tracking  = self.sim_input['t']
            self.LDW_Right_Tracking    = self.sim_input['LDW_Right_Tracking']

        else:
            self.t_LDW_Left_Tracking   = None
            self.LDW_Left_Tracking     = None
    
            self.t_LDW_Right_Tracking  = None
            self.LDW_Right_Tracking    = None
            
            
        # ===========================================================================
        # line crossing
        if self.input_mode == "FLR20_sig":
            self.t_Lane_Crossing_Left  = self.FLR20_sig["FLC20_CAN"]["Time_Me_Line_Changed_Left"]
            self.Lane_Crossing_Left    = self.FLR20_sig["FLC20_CAN"]["Me_Line_Changed_Left"]
            self.t_Lane_Crossing_Right = self.FLR20_sig["FLC20_CAN"]["Time_Me_Line_Changed_Right"]
            self.Lane_Crossing_Right   = self.FLR20_sig["FLC20_CAN"]["Me_Line_Changed_Right"]

        elif self.input_mode == "SilLDWS_C":
            self.t_Lane_Crossing_Left  = self.sim_input['t']
            self.Lane_Crossing_Left    = self.sim_input['Left_Lane_Crossing']
            self.t_Lane_Crossing_Right = self.sim_input['t']
            self.Lane_Crossing_Right   = self.sim_input['Right_Lane_Crossing']

        else:
            self.t_Lane_Crossing_Left  = None
            self.Lane_Crossing_Left    = None
            self.t_Lane_Crossing_Right = None
            self.Lane_Crossing_Right   = None
            
        # ===========================================================================
        # view range
        if self.input_mode == "FLR20_sig":
            self.t_View_Range_Left  = self.FLR20_sig["FLC20_CAN"]["Time_View_Range_Left"]
            self.View_Range_Left    = self.FLR20_sig["FLC20_CAN"]["View_Range_Left"]
            self.t_View_Range_Right = self.FLR20_sig["FLC20_CAN"]["Time_View_Range_Right"]
            self.View_Range_Right   = self.FLR20_sig["FLC20_CAN"]["View_Range_Right"]

        elif self.input_mode == "SilLDWS_C":
            self.t_View_Range_Left  = self.sim_input['t']
            self.View_Range_Left    = self.sim_input['View_Range_Left']
            self.t_View_Range_Right = self.sim_input['t']
            self.View_Range_Right   = self.sim_input['View_Range_Right']

        else:
            self.t_View_Range_Left  = None
            self.View_Range_Left    = None
            self.t_View_Range_Right = None
            self.View_Range_Right   = None
            
        
        # ===========================================================================
        # detected lines left right (polynomial coefficients)
        if self.input_mode == "FLR20_sig":
    
            self.t_Left_C0  = self.FLR20_sig['FLC20_CAN']["Time_C0_Left"]
            self.Left_C0    = self.FLR20_sig['FLC20_CAN']["C0_Left"]  
            self.Left_C1    = self.FLR20_sig['FLC20_CAN']["C1_Left"]  
            self.Left_C2    = self.FLR20_sig['FLC20_CAN']["C2_Left"]  
            self.Left_C3    = self.FLR20_sig['FLC20_CAN']["C3_Left"]  
    
            self.t_Right_C0 = self.FLR20_sig['FLC20_CAN']["Time_C0_Right"]
            self.Right_C0   = self.FLR20_sig['FLC20_CAN']["C0_Right"] 
            self.Right_C1   = self.FLR20_sig['FLC20_CAN']["C1_Right"] 
            self.Right_C2   = self.FLR20_sig['FLC20_CAN']["C2_Right"] 
            self.Right_C3   = self.FLR20_sig['FLC20_CAN']["C3_Right"] 
    
        elif self.input_mode == "SilLDWS_C":
        
            self.t_Left_C0  = self.sim_input['t']
            self.Left_C0    = self.sim_input['Left_C0']  
            self.Left_C1    = self.sim_input['Left_C1']  
            self.Left_C2    = self.sim_input['Left_C2']  
            self.Left_C3    = self.sim_input['Left_C3'] 
    
            self.t_Right_C0 = self.sim_input['t']
            self.Right_C0   = self.sim_input['Right_C0']
            self.Right_C1   = self.sim_input['Right_C1']
            self.Right_C2   = self.sim_input['Right_C2'] 
            self.Right_C3   = self.sim_input['Right_C3'] 

        else:
        
            self.t_Left_C0  = None
            self.Left_C0    = None  
            self.Left_C1    = None  
            self.Left_C2    = None  
            self.Left_C3    = None 
    
            self.t_Right_C0 = None
            self.Right_C0   = None 
            self.Right_C1   = None
            self.Right_C2   = None 
            self.Right_C3   = None 
    
        # ===========================================================================
        # distance left right from wheel to line  
        #  Application\pcanmsg.c
        if self.input_mode == "FLR20_sig":

            # Bendix Info 1 - direct from Mobileye 
            self.t_C0_left_wheel  = self.FLR20_sig['FLC20_CAN']["Time_C0_left_wheel"]
            self.C0_left_wheel    = self.FLR20_sig['FLC20_CAN']["C0_left_wheel"]    #  positive to the right
    
            self.t_C0_right_wheel = self.FLR20_sig['FLC20_CAN']["Time_C0_right_wheel"]
            self.C0_right_wheel   = self.FLR20_sig['FLC20_CAN']["C0_right_wheel"]  #  positive to the right
            
            # Bendix Info 2 - after filter
            self.t_C0_left_wheel_filtered  = self.FLR20_sig['FLC20_CAN']["Time_C0_left_wheel_Left_B"]
            self.C0_left_wheel_filtered    = self.FLR20_sig['FLC20_CAN']["C0_left_wheel_Left_B"]   #  positive to the right
    
            self.t_C0_right_wheel_filtered = self.FLR20_sig['FLC20_CAN']["Time_C0_right_wheel_Right_B"]
            self.C0_right_wheel_filtered   = self.FLR20_sig['FLC20_CAN']["C0_right_wheel_Right_B"] #  positive to the right
            
        elif self.input_mode == "SilLDWS_C":

            self.t_C0_left_wheel  = self.sim_output['t']
            self.C0_left_wheel    = self.sim_output['Left_C0'] + self.VehicleWidthHalf  #  positive to the right
    
            self.t_C0_right_wheel = self.sim_output['t']
            self.C0_right_wheel   = self.sim_output['Right_C0'] - self.VehicleWidthHalf #  positive to the right

            self.t_C0_left_wheel_filtered  = self.sim_output['t']
            self.C0_left_wheel_filtered    = -(self.sim_output['BX_laneOffset_Left'] - self.VehicleWidthHalf) #  positive to the right
            
            self.t_C0_right_wheel_filtered = self.sim_output['t']
            self.C0_right_wheel_filtered   = self.sim_output['BX_laneOffset_Right'] - self.VehicleWidthHalf #  positive to the right
        
        else:
            self.t_C0_left_wheel  = None
            self.C0_left_wheel    = None
    
            self.t_C0_right_wheel = None
            self.C0_right_wheel   = None

        
    # ===========================================================================
    def _get_lateral_speed(self):
        '''
           lateral_speed
        '''
        
      
        #if self.input_mode == "FLR20_sig":
        if True:

            # --------------------------------------------------------
            # lateral speed: numerical differentiation of C0_left/right    (f:filtered; d:differentiated)
            try:
                T = 0.25
                self.fd_Right_C0, self.f_Right_C0 = kbtools.svf_1o(self.t_Right_C0, self.Right_C0,T)
                self.fd_Left_C0, self.f_Left_C0   = kbtools.svf_1o(self.t_Left_C0, self.Left_C0,T)
            except:
                print "warning - exception in lateral speed: numerical differentiation of C0_left/right "
                self.fd_Right_C0 = None
                self.f_Right_C0  = None
                self.fd_Left_C0  = None
                self.f_Left_C0   = None
            # --------------------------------------------------------
            # C1 heading * vehicle speed   
            try: 
                self.vy_Right = self.Right_C1 * kbtools.resample(self.t_FrontAxleSpeed, self.FrontAxleSpeed, self.t_Right_C0, method='zoh')
                self.vy_Left  = self.Left_C1  * kbtools.resample(self.t_FrontAxleSpeed, self.FrontAxleSpeed, self.t_Left_C0, method='zoh')
            except:
                print "warning - exception in C1 heading * vehicle speed  "
                self.vy_Right = None       
                self.vy_Left = None
                
            # measurement
            try:
                self.Lateral_Velocity_Right_B = kbtools.resample(self.FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Right_B"],self.FLR20_sig['FLC20_CAN']["Lateral_Velocity_Right_B"],self.t_Right_C0)
                self.Lateral_Velocity_Left_B  = kbtools.resample(self.FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Left_B"], self.FLR20_sig['FLC20_CAN']["Lateral_Velocity_Left_B"],self.t_Left_C0)
                
                self.Lateral_Velocity_Right_B = -self.Lateral_Velocity_Right_B/100.0
                self.Lateral_Velocity_Left_B  = self.Lateral_Velocity_Left_B/100.0
                
            except:
                self.Lateral_Velocity_Right_B = None       
                self.Lateral_Velocity_Left_B  = None
            
            # check if Lateral_Velocity_Left_B and Lateral_Velocity_Right_B are reliable
            if self.lateral_speed_selection == 'Measurement':
                if (self.Lateral_Velocity_Right_B is not None) and (self.Lateral_Velocity_Right_B is not None):
                    x = self.Lateral_Velocity_Right_B 
                    y = self.Lateral_Velocity_Left_B
                    if np.all(x==x[0]) and np.all(y==y[0]):
                        print "Lateral_Velocity_Left_B and Lateral_Velocity_Right_B looks suspicious (stuck on values) -> switch to alternative"
                        self.lateral_speed_selection = 'Heading'
                else:
                    print "Lateral_Velocity_Left_B or Lateral_Velocity_Right_B is not available -> switch to alternative"
                    self.lateral_speed_selection = 'Heading'
            
            # --------------------------------------------------------
            # select  
            if self.lateral_speed_selection == 'TimeDerivative':
                self.lateral_speed_Right = self.fd_Right_C0
                self.lateral_speed_Left  = self.fd_Left_C0
            elif self.lateral_speed_selection == 'Heading':
                self.lateral_speed_Right = self.vy_Right
                self.lateral_speed_Left  = self.vy_Left
            elif self.lateral_speed_selection == 'Measurement':
                self.lateral_speed_Right = self.Lateral_Velocity_Right_B
                self.lateral_speed_Left  = self.Lateral_Velocity_Left_B
                
        if self.input_mode == "SilLDWS_C":
            # t_Right_C0 nicht ganz korrekt
            self.lateral_speed_Right  = -self.sim_output['BX_Lateral_Velocity_Right']
            self.lateral_speed_Left   = self.sim_output['BX_Lateral_Velocity_Left']
     

    # ===========================================================================
    def _get_VBOX_LDWS_VCI(self):

    
        if self.input_mode == "FLR20_sig":

            try:
                self.Time_Range_Lt = self.FLR20_sig["VBOX_LDWS_VCI"]["Time_Range_Lt"]  
                self.Range_Lt      = self.FLR20_sig["VBOX_LDWS_VCI"]["Range_Lt"]  + self.WheelLeft + self.VBOX_Range_Lt_Offset
                self.Time_Range_Rt = self.FLR20_sig["VBOX_LDWS_VCI"]["Time_Range_Rt"]  
                #self.Range_Rt      = self.FLR20_sig["VBOX_LDWS_VCI"]["Range_Rt"]  + self.WheelRight - 0.35
                self.Range_Rt      = self.FLR20_sig["VBOX_LDWS_VCI"]["Range_Rt"]  + self.WheelRight + self.VBOX_Range_Rt_Offset
                
                if self.VBOX_Range_Lt_ref_edge == 'outer':
                    self.Range_Lt += self.width_lane_marking_left
                if self.VBOX_Range_Rt_ref_edge == 'outer':
                    self.Range_Rt -= self.width_lane_marking_right        
                
            except:
                self.Time_Range_Lt = None 
                self.Range_Lt      = None 
                self.Time_Range_Rt = None  
                self.Range_Rt      = None   
            
            try:
                self.Time_Lat_Spd_Lt = self.FLR20_sig["VBOX_LDWS_VCI"]["Time_Lat_Spd_Lt"]  
                self.Lat_Spd_Lt      = self.FLR20_sig["VBOX_LDWS_VCI"]["Lat_Spd_Lt"]  
                self.Time_Lat_Spd_Rt = self.FLR20_sig["VBOX_LDWS_VCI"]["Time_Lat_Spd_Rt"]  
                self.Lat_Spd_Rt      = self.FLR20_sig["VBOX_LDWS_VCI"]["Lat_Spd_Rt"]  
            except:
                self.Time_Lat_Spd_Lt = None 
                self.Lat_Spd_Lt      = None 
                self.Time_Lat_Spd_Rt = None  
                self.Lat_Spd_Rt      = None   
        
        elif self.input_mode == "SilLDWS_C":
            try:
                self.Time_Range_Lt = self.sim_input["Time_Range_Lt"]  
                self.Range_Lt      = self.sim_input["Range_Lt"]  + self.WheelLeft 
                self.Time_Range_Rt = self.sim_input["Time_Range_Rt"]  
                self.Range_Rt      = self.sim_input["Range_Rt"]  + self.WheelRight
            except:
                self.Time_Range_Lt = None 
                self.Range_Lt      = None 
                self.Time_Range_Rt = None  
                self.Range_Rt      = None   
            
            try:
                self.Time_Lat_Spd_Lt = self.sim_input["Time_Lat_Spd_Lt"]  
                self.Lat_Spd_Lt      = self.sim_input["Lat_Spd_Lt"]  
                self.Time_Lat_Spd_Rt = self.sim_input["Time_Lat_Spd_Rt"]  
                self.Lat_Spd_Rt      = self.sim_input["Lat_Spd_Rt"]  
            except:
                self.Time_Lat_Spd_Lt = None 
                self.Lat_Spd_Lt      = None 
                self.Time_Lat_Spd_Rt = None  
                self.Lat_Spd_Rt      = None   
                
                
        
        
        # filter lateral speed signal
        f_g = 1.0
        self.Lat_Spd_Lt_smoothed = None
        self.Lat_Spd_Rt_smoothed = None
        if self.Time_Lat_Spd_Lt is not None:
            self.Lat_Spd_Lt_smoothed = kbtools.smooth_filter(self.Time_Lat_Spd_Lt, self.Lat_Spd_Lt,f_g = f_g, filtertype = 'acausal', valid = np.fabs(self.Lat_Spd_Lt)< 2.0)
                    
        if self.Time_Lat_Spd_Rt is not None:
            self.Lat_Spd_Rt_smoothed = kbtools.smooth_filter(self.Time_Lat_Spd_Rt, self.Lat_Spd_Rt,f_g = f_g, filtertype = 'acausal', valid = np.fabs(self.Lat_Spd_Rt)< 2.0)        
          
        

    # ===========================================================================
    def _get_Ford_Oxford_Measurement_Equipment(self):
        # Ford Oxford Measurement Equipment
        print "_get_Ford_Oxford_Measurement_Equipment() - start"
    
    
        #Oxford
        FLC20_delay = 0.0
        
        #FLC20_delay = 0.3
        #FLC20_delay = 0.2
        #FLC20_delay = 0.1
        
        if self.input_mode == "FLR20_sig":

            try: 
                #Time_RightLinePosLateral = FLR20_sig["Time_RightLinePosLateral"]+FLC20_delay
                #RightLinePosLateral = FLR20_sig["RightLinePosLateral"] 
    
                #Time_LeftLinePosLateral = FLR20_sig["Time_LeftLinePosLateral"]+FLC20_delay
                #LeftLinePosLateral = FLR20_sig["LeftLinePosLateral"] 

                # distance wheel to lane markings 
                self.Time_RightFromCPosLateral = self.FLR20_sig["OxTS"]["Time_RightFromCPosLateral"]+FLC20_delay
                self.RightFromCPosLateral      = self.FLR20_sig["OxTS"]["RightFromCPosLateral"]
                self.Time_LeftFromBPosLateral  = self.FLR20_sig["OxTS"]["Time_LeftFromBPosLateral"]+FLC20_delay
                self.LeftFromBPosLateral       = self.FLR20_sig["OxTS"]["LeftFromBPosLateral"]
     
                # distance center of vehicle to lane marking
                self.Time_RightLinePosLateral = self.FLR20_sig["OxTS"]["Time_RightFromCPosLateral"]+FLC20_delay
                self.RightLinePosLateral      = self.FLR20_sig["OxTS"]["RightFromCPosLateral"] + self.WheelRight 
                self.Time_LeftLinePosLateral  = self.FLR20_sig["OxTS"]["Time_LeftFromBPosLateral"]+FLC20_delay
                self.LeftLinePosLateral       = self.FLR20_sig["OxTS"]["LeftFromBPosLateral"] + self.WheelLeft
     
                # lateral velocity
                self.Time_RightLineVelLateral = self.FLR20_sig["OxTS"]["Time_RightLineVelLateral"]+FLC20_delay
                self.RightLineVelLateral      = self.FLR20_sig["OxTS"]["RightLineVelLateral"] 
                self.Time_LeftLineVelLateral  = self.FLR20_sig["OxTS"]["Time_LeftLineVelLateral"]+FLC20_delay
                self.LeftLineVelLateral       = self.FLR20_sig["OxTS"]["LeftLineVelLateral"] 

                # lateral acceleration of host vehicle                
                self.Time_OxTS_host_AccelLateral = self.FLR20_sig["OxTS"]["Time_AccelLateral"]
                self.OxTS_host_AccelLateral      = self.FLR20_sig["OxTS"]["AccelLateral"]

                
            except Exception, e:
                print "OxTS not available",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"

                self.Time_RightLinePosLateral = None
                self.RightLinePosLateral = None
                self.Time_LeftLinePosLateral = None
                self.LeftLinePosLateral = None

                self.Time_RightLineVelLateral = None
                self.RightLineVelLateral = None 
                self.Time_LeftLineVelLateral = None
                self.LeftLineVelLateral = None 

                # lateral acceleration of host vehicle                
                self.Time_OxTS_host_AccelLateral = None
                self.OxTS_host_AccelLateral      = None 
    
            
        elif self.input_mode == "SilLDWS_C":
          
            try:      
                self.Time_RightLinePosLateral = self.sim_input['Time_RightLinePosLateral']+FLC20_delay
                self.RightLinePosLateral      = self.sim_input['RightLinePosLateral'] + self.WheelRight 
                self.Time_LeftLinePosLateral  = self.sim_input['Time_LeftLinePosLateral']+FLC20_delay
                self.LeftLinePosLateral       = self.sim_input['LeftLinePosLateral'] + self.WheelLeft

             
                # lateral velocity
                self.Time_RightLineVelLateral = self.sim_input['Time_RightLineVelLateral']+FLC20_delay
                self.RightLineVelLateral      = self.sim_input['RightLineVelLateral'] 
                self.Time_LeftLineVelLateral  = self.sim_input['Time_LeftLineVelLateral']+FLC20_delay
                self.LeftLineVelLateral       = self.sim_input['LeftLineVelLateral'] 

                # lateral acceleration of host vehicle                
                self.Time_OxTS_host_AccelLateral = None
                self.OxTS_host_AccelLateral      = None 
                
            except Exception, e:
                print "OxTS not available",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"

                self.Time_RightLinePosLateral = None
                self.RightLinePosLateral = None
                self.Time_LeftLinePosLateral = None
                self.LeftLinePosLateral = None

                self.Time_RightLineVelLateral = None
                self.RightLineVelLateral = None 
                self.Time_LeftLineVelLateral = None
                self.LeftLineVelLateral = None 
        
                # lateral acceleration of host vehicle                
                self.Time_OxTS_host_AccelLateral = None
                self.OxTS_host_AccelLateral      = None 


        # filter lateral speed signal
        f_g = 2.5    # Hz
        self.LeftLineVelLateral_smoothed = None
        self.RightLineVelLateral_smoothed = None
            
        if self.Time_LeftLineVelLateral is not None:
            self.LeftLineVelLateral_smoothed = kbtools.smooth_filter(self.Time_LeftLineVelLateral, self.LeftLineVelLateral,f_g = f_g,  filtertype = 'acausal', valid = np.fabs(self.LeftLineVelLateral)< 2.0)
        if self.Time_RightLineVelLateral is not None:
            self.RightLineVelLateral_smoothed = kbtools.smooth_filter(self.Time_RightLineVelLateral, self.RightLineVelLateral,f_g = f_g,  filtertype = 'acausal', valid = np.fabs(self.RightLineVelLateral)< 2.0)        

        
        # filter lateral acceleration signal
        self.OxTS_host_AccelLateral_smoothed = None
        f_g = 2.5    # Hz
        if self.Time_OxTS_host_AccelLateral is not None:
           self.OxTS_host_AccelLateral_smoothed = kbtools.smooth_filter(self.Time_OxTS_host_AccelLateral, self.OxTS_host_AccelLateral ,f_g = f_g, filtertype = 'acausal', valid = np.fabs(self.OxTS_host_AccelLateral)< 10.0)
      

      
            
            
        print "_get_Ford_Oxford_Measurement_Equipment() - end"

        
    #=================================================================================
    def _get_Lane_Departure_Warning_Signals(self):
        '''
            Lane Departure Warning Signals 
        '''
        
        if self.input_mode == "FLR20_sig":

            # LNVU LDW before suppressiom 
            self.t_WARN_isWarningRight     = self.FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningRight"]
            self.WARN_isWarningRight       = self.FLR20_sig['FLC20_CAN']["LNVU_isWarningRight"]
            self.t_WARN_isWarningLeft      = self.FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningLeft"]
            self.WARN_isWarningLeft        = self.FLR20_sig['FLC20_CAN']["LNVU_isWarningLeft"]
             
            # J1939
            # warning condition present - after suppressors
            self.t_LaneDepartImminentRight = self.FLR20_sig["J1939"]["Time_LaneDepartImminentRight"]
            self.LaneDepartImminentRight   = self.FLR20_sig["J1939"]["LaneDepartImminentRight"]
            self.t_LaneDepartImminentLeft  = self.FLR20_sig["J1939"]["Time_LaneDepartImminentLeft"]
            self.LaneDepartImminentLeft    = self.FLR20_sig["J1939"]["LaneDepartImminentLeft"] 

            # J1939
            # request for an acoustical warning
            self.t_AcousticalWarningRight  = self.FLR20_sig["J1939"]["Time_AcousticalWarningRight"]
            self.AcousticalWarningRight    = self.FLR20_sig["J1939"]["AcousticalWarningRight"]
            self.t_AcousticalWarningLeft   = self.FLR20_sig["J1939"]["Time_AcousticalWarningLeft"]
            self.AcousticalWarningLeft     = self.FLR20_sig["J1939"]["AcousticalWarningLeft"] 

            # J1939
            # request for an optical warning
            self.t_OpticalWarningRight     = self.FLR20_sig["J1939"]["Time_OpticalWarningRight"]
            self.OpticalWarningRight       = self.FLR20_sig["J1939"]["OpticalWarningRight"]
            self.t_OpticalWarningLeft      = self.FLR20_sig["J1939"]["Time_OpticalWarningLeft"]
            self.OpticalWarningLeft        = self.FLR20_sig["J1939"]["OpticalWarningLeft"] 
            
            # 1939 - StateOfLDWS
            self.t_StateOfLDWS             = self.FLR20_sig["J1939"]["Time_StateOfLDWS"]
            self.StateOfLDWS               = self.FLR20_sig["J1939"]["StateOfLDWS"] 
            
            # 1939 - LDW_Buzzer
            self.t_LDW_Buzzer             = self.FLR20_sig["J1939"]["Time_LDW_Buzzer"]
            self.LDW_Buzzer               = self.FLR20_sig["J1939"]["LDW_Buzzer"] 
            
            
            
        elif self.input_mode == "SilLDWS_C":
            # LNVU output
            self.t_WARN_isWarningRight     = self.sim_output['t']
            self.WARN_isWarningRight       = self.sim_output['WARN_isWarningRight']
            self.t_WARN_isWarningLeft      = self.sim_output['t']
            self.WARN_isWarningLeft        = self.sim_output['WARN_isWarningLeft']

            # before suppression
            self.t_LaneDepartImminentRight = self.sim_output['t']
            self.LaneDepartImminentRight   = self.sim_output['KB_LDW_Imminent_State_Right']
            self.t_LaneDepartImminentLeft  = self.sim_output['t']
            self.LaneDepartImminentLeft    = self.sim_output['KB_LDW_Imminent_State_Left']
            
            # after suppresion 
            self.t_AcousticalWarningRight  = self.sim_output['t']
            self.AcousticalWarningRight    = self.sim_output['KB_LDW_Acoustical_State_Right']
            self.t_AcousticalWarningLeft   = self.sim_output['t']
            self.AcousticalWarningLeft     = self.sim_output['KB_LDW_Acoustical_State_Left'] 

            self.t_OpticalWarningRight     = self.sim_output['t']
            self.OpticalWarningRight       = self.sim_output['KB_LDW_Optical_State_Right']
            self.t_OpticalWarningLeft      = self.sim_output['t']
            self.OpticalWarningLeft        = self.sim_output['KB_LDW_Optical_State_Left'] 
     

            # StateOfLDWS
            self.t_StateOfLDWS             = self.sim_output['t'] 
            self.StateOfLDWS               = self.sim_output['KB_System_State'] 
            
            # 1939 - LDW_Buzzer
            self.t_LDW_Buzzer             = None
            self.LDW_Buzzer               = None 


        if self.FLR20_sig is not None and 'FLC20_CAN' in self.FLR20_sig:
            # -------------------------------------------------------------------
            # Bendix Info (Debug Message)
            # warning condition present -  before suppressors
            self.t_ME_LDW_LaneDeparture_Left  = self.FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Left"]
            self.ME_LDW_LaneDeparture_Left    = self.FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Left"]
            self.t_ME_LDW_LaneDeparture_Right = self.FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Right"]
            self.ME_LDW_LaneDeparture_Right   = self.FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Right"]
        
            # Bendix Info (Debug Message)
            # warning condition present - after suppressors   
            self.t_LDW_LaneDeparture_Left     = self.FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Left"]
            self.LDW_LaneDeparture_Left       = self.FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Left"]
            self.t_LDW_LaneDeparture_Right    = self.FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Right"]
            self.LDW_LaneDeparture_Right      = self.FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Right"]
     
        else:
            # -------------------------------------------------------------------
            # Bendix Info (Debug Message)
            # warning condition present -  before suppressors
            try:
                self.t_ME_LDW_LaneDeparture_Left  = self.sim_input['t']
                self.ME_LDW_LaneDeparture_Left    = self.sim_input['ME_LDW_LaneDeparture_Left']
                self.t_ME_LDW_LaneDeparture_Right = self.sim_input['t']
                self.ME_LDW_LaneDeparture_Right   = self.sim_input['ME_LDW_LaneDeparture_Right']
            except:
                self.t_ME_LDW_LaneDeparture_Left  = None
                self.ME_LDW_LaneDeparture_Left    = None
                self.t_ME_LDW_LaneDeparture_Right = None
                self.ME_LDW_LaneDeparture_Right   = None
            
        
            # Bendix Info (Debug Message)
            # warning condition present - after suppressors   
            self.t_LDW_LaneDeparture_Left     = None
            self.LDW_LaneDeparture_Left       = None
            self.t_LDW_LaneDeparture_Right    = None
            self.LDW_LaneDeparture_Right      = None


    #=================================================================================
    def _checkXPresentAtEvent(self, t, x, t_event, delta_t=1.0):
        '''
           check if x is 1 in the interval [t_event-delta_t, t_event+delta_t]
        '''
        if (t is not None) and (x is not None) and (t_event is not None) :
            return np.any(x[np.logical_and(t>=(t_event-delta_t),t<=(t_event+delta_t))]> 0.5)
        else:
            return None
        

    #=================================================================================
    def _get_LDW_event_attributes(self):
        '''
            LDW event attributes
        
        '''
     
        print "_get_LDW_event_attributes()"
     
        # ===========================================================================
        # start and stop of LDWs
        
        # --------------------------------------------------------
        delta_t = 1.0
        print "t_event",self.t_event 

        self.t_LDW_Left  = None
        self.LDW_Left    = None
        self.t_LDW_Right = None
        self.LDW_Right   = None
       
        # ----------------------------------------       
        # LNVU 
        LDW_Left_LNVU_present  = self._checkXPresentAtEvent(self.t_WARN_isWarningLeft,self.WARN_isWarningLeft,self.t_event,delta_t=delta_t)
        LDW_Right_LNVU_present = self._checkXPresentAtEvent(self.t_WARN_isWarningRight,self.WARN_isWarningRight,self.t_event,delta_t=delta_t)
                    
        # ----------------------------------------       
        # ME
        LDW_Left_ME_present  = self._checkXPresentAtEvent(self.t_ME_LDW_LaneDeparture_Left,self.ME_LDW_LaneDeparture_Left,self.t_event,delta_t=delta_t)
        LDW_Right_ME_present = self._checkXPresentAtEvent(self.t_ME_LDW_LaneDeparture_Right,self.ME_LDW_LaneDeparture_Right,self.t_event,delta_t=delta_t)
       
        # ----------------------------------------       
        # LD Imminent
        LDW_Left_Imminent_present  = self._checkXPresentAtEvent(self.t_LaneDepartImminentLeft,self.LaneDepartImminentLeft,self.t_event,delta_t=delta_t)
        LDW_Right_Imminent_present = self._checkXPresentAtEvent(self.t_LaneDepartImminentRight,self.LaneDepartImminentRight,self.t_event,delta_t=delta_t)
               
        LDW_Left_present = LDW_Left_LNVU_present or LDW_Left_ME_present or LDW_Left_Imminent_present
        LDW_Right_present = LDW_Right_LNVU_present or LDW_Right_ME_present or LDW_Right_Imminent_present
        
        print "LDW_Left_present", LDW_Left_present
        print "LDW_Right_present", LDW_Right_present

        # ----------------------------------------       
        # select t_LDW_Left,LDW_Left
        
        if LDW_Left_Imminent_present:
            self.t_LDW_Left  = self.t_LaneDepartImminentLeft
            self.LDW_Left    = self.LaneDepartImminentLeft
        elif LDW_Left_LNVU_present:
            self.t_LDW_Left  = self.t_WARN_isWarningLeft 
            self.LDW_Left    = self.WARN_isWarningLeft 
        elif LDW_Left_ME_present:
            self.t_LDW_Left  = self.t_ME_LDW_LaneDeparture_Left 
            self.LDW_Left    = self.ME_LDW_LaneDeparture_Left 
        
        # ----------------------------------------       
        # select t_LDW_Right, LDW_Right
        if LDW_Right_Imminent_present:
            self.t_LDW_Right = self.t_LaneDepartImminentRight 
            self.LDW_Right   = self.LaneDepartImminentRight
        elif LDW_Right_LNVU_present:
            self.t_LDW_Right = self.t_WARN_isWarningRight
            self.LDW_Right   = self.WARN_isWarningRight
        elif LDW_Right_ME_present:
            self.t_LDW_Right = self.t_ME_LDW_LaneDeparture_Right
            self.LDW_Right   = self.ME_LDW_LaneDeparture_Right

        
        
        # --------------------------------------------------------
        # Left 
        if LDW_Left_present:
        
            # ------------------------
            # start
            
            self.t_LDW_Left_start = self.t_event
            self.t_LDW_Left_start = kbtools.GetTRisingEdge(self.t_LDW_Left,self.LDW_Left,(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
        
            self.Left_C0_at_t_LDW_Left            = kbtools.GetPreviousSample(self.t_Left_C0,self.Left_C0,self.t_LDW_Left_start)
            self.lateral_speed_Left_at_t_LDW_Left = kbtools.GetPreviousSample(self.t_Left_C0,self.lateral_speed_Left,self.t_LDW_Left_start)
            self.C0_left_wheel_at_t_LDW_Left      = kbtools.GetPreviousSample(self.t_C0_left_wheel,self.C0_left_wheel,self.t_LDW_Left_start)
            self.C0_left_wheel_filtered_at_t_LDW_Left = kbtools.GetPreviousSample(self.t_C0_left_wheel_filtered, self.C0_left_wheel_filtered, self.t_LDW_Left_start)

            # vehicle speed
            self.FrontAxleSpeed_at_t_LDW_Left = kbtools.GetPreviousSample(self.t_FrontAxleSpeed,self.FrontAxleSpeed,self.t_LDW_Left_start)

            # yaw rate  
            self.YawRate_at_t_LDW_Left = kbtools.GetPreviousSample(self.Time_YawRate,self.YawRate,self.t_LDW_Left_start)
            
            # lateral acceleration 
            self.ay_calc_at_t_LDW_Left = kbtools.GetPreviousSample(self.Time_ay_calc,self.ay_calc,self.t_LDW_Left_start)
                        
            # Racelogic VBOX            
            self.Range_Lt_at_t_LDW_Left             = kbtools.GetPreviousSample(self.Time_Range_Lt,         self.Range_Lt,            self.t_LDW_Left_start)
            self.Lat_Spd_Lt_smoothed_at_t_LDW_Left  = kbtools.GetPreviousSample(self.Time_Lat_Spd_Lt,       self.Lat_Spd_Lt_smoothed, self.t_LDW_Left_start)
            self.VBOX_Velocity_kmh_at_t_LDW_Left    = kbtools.GetPreviousSample(self.Time_VBOX_Velocity_kmh,self.VBOX_Velocity_kmh,   self.t_LDW_Left_start)
            
            # OxTS
            self.LeftLinePosLateral_at_t_LDW_Left           = kbtools.GetPreviousSample(self.Time_LeftLinePosLateral, self.LeftLinePosLateral,          self.t_LDW_Left_start)
            self.LeftLineVelLateral_smoothed_at_t_LDW_Left  = kbtools.GetPreviousSample(self.Time_LeftLineVelLateral, self.LeftLineVelLateral_smoothed, self.t_LDW_Left_start)
            self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Left = kbtools.GetPreviousSample(self.Time_OxTS_host_AccelLateral, self.OxTS_host_AccelLateral_smoothed, self.t_LDW_Left_start)


            
                      
            
       
            print "Left_C0_at_t_LDW_Left", self.Left_C0_at_t_LDW_Left
            print "lateral_speed_Left_at_t_LDW_Left", self.lateral_speed_Left_at_t_LDW_Left
            print "C0_left_wheel_at_t_LDW_Left", self.C0_left_wheel_at_t_LDW_Left
            print "C0_left_wheel_filtered_at_t_LDW_Left", self.C0_left_wheel_filtered_at_t_LDW_Left
            print "FrontAxleSpeed_at_t_LDW_Left", self.FrontAxleSpeed_at_t_LDW_Left
            print "YawRate_at_t_LDW_Left", self.YawRate_at_t_LDW_Left
            print "ay_calc_at_t_LDW_Left", self.ay_calc_at_t_LDW_Left
            print "Range_Lt_at_t_LDW_Left", self.Range_Lt_at_t_LDW_Left             
            print "Lat_Spd_Lt_smoothed_at_t_LDW_Left", self.Lat_Spd_Lt_smoothed_at_t_LDW_Left
            print "VBOX_Velocity_kmh_at_t_LDW_Left", self.VBOX_Velocity_kmh_at_t_LDW_Left  
            print "LeftLinePosLateral_at_t_LDW_Left", self.LeftLinePosLateral_at_t_LDW_Left   
            print "LeftLineVelLateral_smoothed_at_t_LDW_Left", self.LeftLineVelLateral_smoothed_at_t_LDW_Left
            print "OxTS_host_AccelLateral_smoothed_at_t_LDW_Left", self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Left

            
        
            # ------------------------
            # stop 
            self.t_LDW_Left_stop = kbtools.GetTStop(self.t_LDW_Left,self.LDW_Left,self.t_LDW_Left_start)
            print "t_LDW_Left_stop", self.t_LDW_Left_stop
            self.Left_C0_at_t_LDW_Left_stop             = kbtools.GetPreviousSample(self.t_Left_C0,self.Left_C0,self.t_LDW_Left_stop)
            self.lateral_speed_Left_at_t_LDW_Left_stop  = kbtools.GetPreviousSample(self.t_Left_C0,self.lateral_speed_Left,self.t_LDW_Left_stop)
            self.C0_left_wheel_at_t_LDW_Left_stop       = kbtools.GetPreviousSample(self.t_C0_left_wheel,self.C0_left_wheel,self.t_LDW_Left_stop)

            print "Left_C0_at_t_LDW_Left_stop", self.Left_C0_at_t_LDW_Left_stop
            print "lateral_speed_Left_at_t_LDW_Left_stop", self.lateral_speed_Left_at_t_LDW_Left_stop
            print "C0_left_wheel_at_t_LDW_Left_stop", self.C0_left_wheel_at_t_LDW_Left_stop
                
        else:
            print "Left not found"
            self.t_LDW_Left_start = None
            self.Left_C0_at_t_LDW_Left = None
            self.C0_left_wheel_at_t_LDW_Left = None
            self.C0_left_wheel_filtered_at_t_LDW_Left = None
            self.lateral_speed_Left_at_t_LDW_Left = None
            self.FrontAxleSpeed_at_t_LDW_Left = None
            self.YawRate_at_t_LDW_Left = None
            self.ay_calc_at_t_LDW_Left = None
            

            
            # Racelogic
            self.Range_Lt_at_t_LDW_Left             = None
            self.Lat_Spd_Lt_smoothed_at_t_LDW_Left  = None
            self.VBOX_Velocity_kmh_at_t_LDW_Left    = None
            
            
            # OxTS
            self.LeftLinePosLateral_at_t_LDW_Left           = None
            self.LeftLineVelLateral_smoothed_at_t_LDW_Left  = None
            self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Left = None
        
    
            # stop 
            self.t_LDW_Left_stop = None
            self.Left_C0_at_t_LDW_Left_stop = None
            self.C0_left_wheel_at_t_LDW_Left_stop = None
            self.lateral_speed_Left_at_t_LDW_Left_stop  = None
        
        # todo - make more comprehensive
        self.LDW_Left_okay = False
        if self.t_LDW_Left_start is not None and self.Left_C0_at_t_LDW_Left is not None:
            self.LDW_Left_okay = True
        
        # --------------------------------------------
        sig = COneSide('left')
       
        sig.FileName            = self.FileName
        sig.LDW_okay            = self.LDW_Left_okay
        sig.t_LDW_start         = self.t_LDW_Left_start
        sig.Wheel               = self.WheelLeft
        sig.width_lane_marking  = self.width_lane_marking_left
          
         
        sig.t_LaneDepartImminent = self.t_LaneDepartImminentLeft
        sig.LaneDepartImminent   = self.LaneDepartImminentLeft
        
        sig.Time_OxTS_LinePosLateral     = self.Time_LeftLinePosLateral
        sig.OxTS_LinePosLateral          = self.LeftLinePosLateral
        sig.Time_OxTS_LineVelLateral     = self.Time_LeftLineVelLateral
        sig.OxTS_LineVelLateral_smoothed = self.LeftLineVelLateral_smoothed
                   
        sig.Time_VBOX_Range_t        = self.Time_Range_Lt
        sig.VBOX_Range_t             = self.Range_Lt
        sig.Time_VBOX_Lat_Spd_t      = self.Time_Lat_Spd_Lt
        sig.VBOX_Lat_Spd_t_smoothed = self.Lat_Spd_Lt_smoothed
               
        sig.t_C0          = self.t_Left_C0
        sig.C0            = self.Left_C0
        sig.lateral_speed = self.lateral_speed_Left
            
        sig.C0_at_t_LDW                           = self.Left_C0_at_t_LDW_Left
        sig.C0_wheel_at_t_LDW                     = self.C0_left_wheel_at_t_LDW_Left 
        sig.C0_wheel_filtered_at_t_LDW            = self.C0_left_wheel_filtered_at_t_LDW_Left
        sig.lateral_speed_at_t_LDW                = self.lateral_speed_Left_at_t_LDW_Left
        sig.OxTS_LinePosLateral_at_t_LDW          = self.LeftLinePosLateral_at_t_LDW_Left
        sig.OxTS_LineVelLateral_smoothed_at_t_LDW = self.LeftLineVelLateral_smoothed_at_t_LDW_Left
        sig.OxTS_host_AccelLateral_smoothed_at_t_LDW = self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Left
        sig.VBOX_Range_t_at_t_LDW                 = self.Range_Lt_at_t_LDW_Left
        sig.VBOX_Lat_Spd_t_smoothed_at_t_LDW      = self.Lat_Spd_Lt_smoothed_at_t_LDW_Left
        sig.VBOX_Velocity_kmh_at_t_LDW            = self.VBOX_Velocity_kmh_at_t_LDW_Left
        sig.FrontAxleSpeed_at_t_LDW               = self.FrontAxleSpeed_at_t_LDW_Left
        sig.YawRate_at_t_LDW                      = self.YawRate_at_t_LDW_Left
        sig.ay_calc_at_t_LDW                      = self.ay_calc_at_t_LDW_Left
             
        self.left = sig
        
        # --------------------------------------------------------
        # Right 
        if LDW_Right_present:
            # start
            self.t_LDW_Right_start = self.t_event
            self.t_LDW_Right_start = kbtools.GetTRisingEdge(self.t_LDW_Right,self.LDW_Right,(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
        
            self.Right_C0_at_t_LDW_Right            = kbtools.GetPreviousSample(self.t_Right_C0,self.Right_C0,self.t_LDW_Right_start)
            self.lateral_speed_Right_at_t_LDW_Right = kbtools.GetPreviousSample(self.t_Right_C0,self.lateral_speed_Right,self.t_LDW_Right_start)
            self.C0_right_wheel_at_t_LDW_Right      = kbtools.GetPreviousSample(self.t_C0_right_wheel,self.C0_right_wheel,self.t_LDW_Right_start)
            self.C0_right_wheel_filtered_at_t_LDW_Right = kbtools.GetPreviousSample(self.t_C0_right_wheel_filtered, self.C0_right_wheel_filtered, self.t_LDW_Right_start)

            # vehicle speed
            self.FrontAxleSpeed_at_t_LDW_Right      = kbtools.GetPreviousSample(self.t_FrontAxleSpeed,self.FrontAxleSpeed,self.t_LDW_Right_start)
            
            # yaw rate
            self.YawRate_at_t_LDW_Right             = kbtools.GetPreviousSample(self.Time_YawRate,self.YawRate,self.t_LDW_Right_start)

            # lateral acceleration 
            self.ay_calc_at_t_LDW_Right             = kbtools.GetPreviousSample(self.Time_ay_calc,self.ay_calc,self.t_LDW_Right_start)

            
            # Racelogic VBOX            
            self.Range_Rt_at_t_LDW_Right            = kbtools.GetPreviousSample(self.Time_Range_Rt,         self.Range_Rt,            self.t_LDW_Right_start)
            self.Lat_Spd_Rt_smoothed_at_t_LDW_Right = kbtools.GetPreviousSample(self.Time_Lat_Spd_Rt,       self.Lat_Spd_Rt_smoothed, self.t_LDW_Right_start)
            self.VBOX_Velocity_kmh_at_t_LDW_Right   = kbtools.GetPreviousSample(self.Time_VBOX_Velocity_kmh,self.VBOX_Velocity_kmh,   self.t_LDW_Right_start)

            # OxTS
            self.RightLinePosLateral_at_t_LDW_Right          = kbtools.GetPreviousSample(self.Time_RightLinePosLateral, self.RightLinePosLateral,          self.t_LDW_Right_start)
            self.RightLineVelLateral_smoothed_at_t_LDW_Right = kbtools.GetPreviousSample(self.Time_RightLineVelLateral, self.RightLineVelLateral_smoothed, self.t_LDW_Right_start)
            self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Right = kbtools.GetPreviousSample(self.Time_OxTS_host_AccelLateral, self.OxTS_host_AccelLateral_smoothed, self.t_LDW_Right_start)


            

            print "Right_C0_at_t_LDW_Right", self.Right_C0_at_t_LDW_Right
            print "lateral_speed_Right_at_t_LDW_Right", self.lateral_speed_Right_at_t_LDW_Right
            print "C0_right_wheel_at_t_LDW_Right", self.C0_right_wheel_at_t_LDW_Right
            print "C0_right_wheel_filtered_at_t_LDW_Right", self.C0_right_wheel_filtered_at_t_LDW_Right 
            print "FrontAxleSpeed_at_t_LDW_Right", self.FrontAxleSpeed_at_t_LDW_Right
            print "YawRate_at_t_LDW_Right",self.YawRate_at_t_LDW_Right
            print "ay_calc_at_t_LDW_Right",self.ay_calc_at_t_LDW_Right
            print "Range_Rt_at_t_LDW_Right", self.Range_Rt_at_t_LDW_Right 
            print "Lat_Spd_Rt_smoothed_at_t_LDW_Right", self.Lat_Spd_Rt_smoothed_at_t_LDW_Right 
            print "VBOX_Velocity_kmh_at_t_LDW_Right", self.VBOX_Velocity_kmh_at_t_LDW_Right
            print "RightLinePosLateral_at_t_LDW_Right", self.RightLinePosLateral_at_t_LDW_Right   
            print "RightLineVelLateral_smoothed_at_t_LDW_Right", self.RightLineVelLateral_smoothed_at_t_LDW_Right 
            print "OxTS_host_AccelLateral_smoothed_at_t_LDW_Right", self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Right 
        
        
            # stop 
            self.t_LDW_Right_stop = kbtools.GetTStop(self.t_LDW_Right,self.LDW_Right,self.t_LDW_Right_start)
            print "t_LDW_Right_stop", self.t_LDW_Right_stop
            self.Right_C0_at_t_LDW_Right_stop             = kbtools.GetPreviousSample(self.t_Right_C0,self.Right_C0,self.t_LDW_Right_stop)
            self.lateral_speed_Right_at_t_LDW_Right_stop  = kbtools.GetPreviousSample(self.t_Right_C0,self.lateral_speed_Right,self.t_LDW_Right_stop)
            self.C0_right_wheel_at_t_LDW_Right_stop       = kbtools.GetPreviousSample(self.t_C0_right_wheel,self.C0_right_wheel,self.t_LDW_Right_stop)

            print "Right_C0_at_t_LDW_Right_stop", self.Right_C0_at_t_LDW_Right_stop
            print "lateral_speed_Right_at_t_LDW_Right_stop",self.lateral_speed_Right_at_t_LDW_Right_stop
            print "C0_right_wheel_at_t_LDW_Right_stop", self.C0_right_wheel_at_t_LDW_Right_stop
 
        
        else:
            print "Right not found"
            self.t_LDW_Right_start = None
            self.Right_C0_at_t_LDW_Right = None
            self.C0_right_wheel_at_t_LDW_Right = None
            self.C0_right_wheel_filtered_at_t_LDW_Right = None
            self.lateral_speed_Right_at_t_LDW_Right = None
            self.FrontAxleSpeed_at_t_LDW_Right = None
            self.YawRate_at_t_LDW_Right = None
            self.ay_calc_at_t_LDW_Right = None
            
            # Racelogic VBOX 
            self.Range_Rt_at_t_LDW_Right            = None
            self.Lat_Spd_Rt_smoothed_at_t_LDW_Right = None
            self.VBOX_Velocity_kmh_at_t_LDW_Right   = None
            
            # OxTS
            self.RightLinePosLateral_at_t_LDW_Right          = None
            self.RightLineVelLateral_smoothed_at_t_LDW_Right = None
            self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Right = None
            
            

            # stop 
            self.t_LDW_Right_stop = None
            self.Right_C0_at_t_LDW_Right_stop     = None
            self.C0_right_wheel_at_t_LDW_Right_stop = None
            self.lateral_speed_Right_at_t_LDW_Right_stop  = None
        
        # todo - make more comprehensive
        self.LDW_Right_okay = False
        if self.t_LDW_Right_start is not None and self.Right_C0_at_t_LDW_Right is not None:
            self.LDW_Right_okay = True
            
        # --------------------------------------------
        sig = COneSide('right')
       
        sig.FileName            = self.FileName
        sig.LDW_okay            = self.LDW_Right_okay
        sig.t_LDW_start         = self.t_LDW_Right_start
        sig.Wheel               = self.WheelRight
        sig.width_lane_marking  = self.width_lane_marking_right
         
        
        sig.t_LaneDepartImminent = self.t_LaneDepartImminentRight
        sig.LaneDepartImminent   = self.LaneDepartImminentRight
        
        sig.Time_OxTS_LinePosLateral     = self.Time_RightLinePosLateral
        sig.OxTS_LinePosLateral          = self.RightLinePosLateral
        sig.Time_OxTS_LineVelLateral     = self.Time_RightLineVelLateral
        sig.OxTS_LineVelLateral_smoothed = self.RightLineVelLateral_smoothed
                   
        sig.Time_VBOX_Range_t        = self.Time_Range_Rt
        sig.VBOX_Range_t             = self.Range_Rt
        sig.Time_VBOX_Lat_Spd_t      = self.Time_Lat_Spd_Rt
        sig.VBOX_Lat_Spd_t_smoothed = self.Lat_Spd_Rt_smoothed
               
        sig.t_C0          = self.t_Right_C0
        sig.C0            = self.Right_C0
        sig.lateral_speed = self.lateral_speed_Right
            
        sig.C0_at_t_LDW                           = self.Right_C0_at_t_LDW_Right
        sig.C0_wheel_at_t_LDW                    = self.C0_right_wheel_at_t_LDW_Right
        sig.C0_wheel_filtered_at_t_LDW           = self.C0_right_wheel_filtered_at_t_LDW_Right
        sig.lateral_speed_at_t_LDW                = self.lateral_speed_Right_at_t_LDW_Right
        sig.OxTS_LinePosLateral_at_t_LDW          = self.RightLinePosLateral_at_t_LDW_Right
        sig.OxTS_LineVelLateral_smoothed_at_t_LDW = self.RightLineVelLateral_smoothed_at_t_LDW_Right
        sig.OxTS_host_AccelLateral_smoothed_at_t_LDW = self.OxTS_host_AccelLateral_smoothed_at_t_LDW_Right 
        sig.VBOX_Range_t_at_t_LDW                 = self.Range_Rt_at_t_LDW_Right
        sig.VBOX_Lat_Spd_t_smoothed_at_t_LDW      = self.Lat_Spd_Rt_smoothed_at_t_LDW_Right
        sig.VBOX_Velocity_kmh_at_t_LDW            = self.VBOX_Velocity_kmh_at_t_LDW_Right
        sig.FrontAxleSpeed_at_t_LDW               = self.FrontAxleSpeed_at_t_LDW_Right
        sig.YawRate_at_t_LDW                      = self.YawRate_at_t_LDW_Right
        sig.ay_calc_at_t_LDW                      = self.ay_calc_at_t_LDW_Right
        
        self.right = sig
 
        print "LDW_Left_okay", self.LDW_Left_okay
        print "  t_LDW_Left_start", self.t_LDW_Left_start, self.Left_C0_at_t_LDW_Left,self.lateral_speed_Left_at_t_LDW_Left
        print "  t_LDW_Left_stop", self.t_LDW_Left_stop, self.Left_C0_at_t_LDW_Left_stop,self.lateral_speed_Left_at_t_LDW_Left_stop
        print "LDW_Right_okay", self.LDW_Right_okay
        print "  t_LDW_Right_start", self.t_LDW_Right_start, self.Right_C0_at_t_LDW_Right,self.lateral_speed_Right_at_t_LDW_Right
        print "  t_LDW_Right_stop", self.t_LDW_Right_stop, self.Right_C0_at_t_LDW_Right_stop,self.lateral_speed_Right_at_t_LDW_Right_stop
  
  
    # =========================================================================================================================          
    def plot_1_C0_Filter(self,FigNr = 500, PlotName = 'plot_1.2_C0_Filter'):
         
         
        if self.verbose:
           print PlotName
    
        self.xlim_to_use(self.xlim_closeup)
 
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=200)      
     
        # ------------------------------------------------------
        # C0 Left
        ax = fig.add_subplot(311)
        ax.set_title('Left Side')
        if self.t_C0_left_wheel is not None:
            ax.plot(self.t_C0_left_wheel-self.t_ref,          self.C0_left_wheel,            'b',  label='C0_left_wheel' )
        if self.t_C0_left_wheel_filtered is not None:
            ax.plot(self.t_C0_left_wheel_filtered-self.t_ref, self.C0_left_wheel_filtered,   'r',  label='filtered' )
        self.set_description(ax,'[m]',(-1.5,1.5) ) 
       
        # ------------------------------------------------------
        # C0 Right
        ax = fig.add_subplot(312)
        ax.set_title('Right Side')
        if self.t_C0_right_wheel is not None:
            ax.plot(self.t_C0_right_wheel-self.t_ref,          self.C0_right_wheel,            'b',  label='C0_right_wheel' )
        if self.t_C0_right_wheel_filtered is not None:
            ax.plot(self.t_C0_right_wheel_filtered-self.t_ref, self.C0_right_wheel_filtered,   'r',  label='filtered' )
        self.set_description(ax,'[m]',(-1.5,1.5)  ) 

        # ------------------------------------------------------
        # error 
        ax = fig.add_subplot(313)
        ax.set_title('error both sides')
        
        if (self.t_C0_left_wheel is not None) and (self.C0_left_wheel_filtered is not None):
            C0_left_wheel_filtered  = kbtools.resample(self.t_C0_left_wheel_filtered,  self.C0_left_wheel_filtered, self.t_C0_left_wheel) 
            ax.plot(self.t_C0_left_wheel-self.t_ref,  self.C0_left_wheel-C0_left_wheel_filtered,   'b',  label='Left' )
        if (self.t_C0_right_wheel is not None) and (self.C0_right_wheel_filtered is not None):
            C0_right_wheel_filtered = kbtools.resample(self.t_C0_right_wheel_filtered, self.C0_right_wheel_filtered,self.t_C0_right_wheel) 
            ax.plot(self.t_C0_right_wheel-self.t_ref, self.C0_right_wheel-C0_right_wheel_filtered,  'r',  label='Right' )
      
        self.set_description(ax,'[m]',(-0.15,0.15)) 
       
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()


  
    # ===========================================================================
    def plot_2_lateral_position(self, PlotName = 'plot_2_lateral_position',xlim=None,yzoom=False):
        
        if self.verbose:
           print PlotName
    
    
        if xlim is not None:
            PlotName = PlotName + '_zoom'
            self.xlim_to_use(xlim)
            local_xlim = xlim
        else:
            self.xlim_to_use(self.xlim_default)
            # plot range:  pre_trigger .. t_ref .. post_trigger
            local_xlim = self.xlim_closeup

        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=200)
 
        # --------------------------------------------------------
        ax = fig.add_subplot(111)
    
        # ----------------------------------------
        # right wheel
      
        if self.LDW_Right_okay:
        
            if self.FrontAxleSpeed_at_t_LDW_Right is not None:
                ax.set_title('Right side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Right*3.6,))
            else:
                ax.set_title('Right side')

            
 
            # lines
            ax.plot(self.t_Right_C0-self.t_ref, self.Right_C0,'bx-',label='C0')
            
            if self.Time_RightLinePosLateral is not None:
                ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral,'m',label='OxTS')

            if self.Time_Range_Rt is not None:
                ax.plot(self.Time_Range_Rt-self.t_ref, self.Range_Rt,'c',label='VBOX_LDWS_VCI')
    
 
            # fitted 5 points line 
            if self.do_fitted_5_points_line:
                slope, intercept,x,y = fit_line(self.t_LDW_Right_start, self.t_Right_C0, self.Right_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Right_start-t_ref, Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s"%(Right_C0_at_t_LDW_Right,slope))

            # ------------------------------
            # position of when lane marking is touched
            ax.hlines(self.WheelRight,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")
     
            
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Right_at_t_LDW_Right*tlc_0)
            ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Right_C0_at_t_LDW_Right,self.lateral_speed_Right_at_t_LDW_Right,self.Right_C0_at_t_LDW_Right-delta_distance))

            
            # stop
            ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,'ms')
            ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,"  %5.2f m"%self.Right_C0_at_t_LDW_Right_stop)
  
            # ------------------------------
            if yzoom:
               ax.set_ylim(self.Right_C0_at_t_LDW_Right-0.1, self.Right_C0_at_t_LDW_Right+0.1)
            else:
               ax.set_ylim(-1.0, 3.5)
               
       
            ax.set_xlim(local_xlim)
    
            ax.legend()
            ax.set_ylabel('outside lane <-- lateral position right [m] --> inside lane')
            
        if self.LDW_Left_okay:
        
            if self.FrontAxleSpeed_at_t_LDW_Left is not None:
                ax.set_title('Left side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Left*3.6,))
            else:
                ax.set_title('Left side')
        
            
            # lines
            ax.plot(self.t_Left_C0-self.t_ref, self.Left_C0,'bx-',label='C0')
            # filtered signals
            #ax.plot(t_Left_C0-t_ref, f_Left_C0,'kx-')
            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.Time_LeftLinePosLateral-self.t_ref, self.LeftLinePosLateral,'c',label='OxTS')

            if self.Time_Range_Lt is not None:
                ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt,'c',label='VBOX_LDWS_VCI')

                
            if self.do_fitted_5_points_line:    
                slope, intercept,x,y = fit_line(self.t_LDW_Left_start, self.t_Left_C0, self.Left_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Left_start-t_ref, Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s"%(Left_C0_at_t_LDW_Left,slope))

            # ------------------------------
            ax.hlines(self.WheelLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")

 
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Left_at_t_LDW_Left*tlc_0)
            ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Left_C0_at_t_LDW_Left,self.lateral_speed_Left_at_t_LDW_Left,self.Left_C0_at_t_LDW_Left+delta_distance))
  
            # stop
            ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,'ms')
            ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,"  %5.2f m"%self.Left_C0_at_t_LDW_Left_stop)
  
            # ------------------------------
            #ax.set_ylim((np.min(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop),np.max(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop)))
            ax.set_ylim(-3.5, 1.0)
            ax.set_xlim(local_xlim)
 
            ax.legend()
            ax.set_ylabel('inside lane <- lateral position left [m] -> outside lane')
   
  
  
        ax.grid()
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
        
    # ===========================================================================
    def plot_2_lateral_position_wheel(self, PlotName = 'plot_2_lateral_position_wheel',xlim=None,yzoom=False):
        
        if self.verbose:
           print PlotName
    
    
        if xlim is not None:
            PlotName = PlotName + '_zoom'
            self.xlim_to_use(xlim)
            local_xlim = xlim
        else:
            self.xlim_to_use(self.xlim_default)
            # plot range:  pre_trigger .. t_ref .. post_trigger
            local_xlim = self.xlim_closeup

        t_LDW_start = None    
        if self.t_LDW_Left_start is not None:
            t_LDW_start = self.t_LDW_Left_start
        if self.t_LDW_Right_start is not None:
            t_LDW_start = self.t_LDW_Right_start
            
        C0_left_wheel_at_t_LDW           = kbtools.GetPreviousSample(self.t_C0_left_wheel,           self.C0_left_wheel,           t_LDW_start)
        C0_left_wheel_filtered_at_t_LDW  = kbtools.GetPreviousSample(self.t_C0_left_wheel_filtered,  self.C0_left_wheel_filtered,  t_LDW_start)
        LeftFromBPosLateral_at_t_LDW     = kbtools.GetPreviousSample(self.Time_LeftFromBPosLateral,  self.LeftFromBPosLateral,     t_LDW_start)
       
        C0_right_wheel_at_t_LDW          = kbtools.GetPreviousSample(self.t_C0_right_wheel,          self.C0_right_wheel,          t_LDW_start)
        C0_right_wheel_filtered_at_t_LDW = kbtools.GetPreviousSample(self.t_C0_right_wheel_filtered, self.C0_right_wheel_filtered, t_LDW_start)
        RightFromCPosLateral_at_t_LDW    = kbtools.GetPreviousSample(self.Time_RightFromCPosLateral, self.RightFromCPosLateral,    t_LDW_start)
       
  
            
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=200)
 
        # --------------------------------------------------------
        ax = fig.add_subplot(211)
        # lines
        if self.Time_RightFromCPosLateral is not None:
            ax.plot(self.Time_RightFromCPosLateral-self.t_ref, self.RightFromCPosLateral,'c',label='OxTS  %5.2f m'%RightFromCPosLateral_at_t_LDW)
        ax.plot(self.t_C0_right_wheel-self.t_ref, self.C0_right_wheel,'b',label='C0_right_wheel  %5.2f m'%C0_right_wheel_at_t_LDW)
        ax.plot(self.t_C0_right_wheel_filtered-self.t_ref, self.C0_right_wheel_filtered,'r',label='C0_right_wheel_filtered  %5.2f m'%C0_right_wheel_filtered_at_t_LDW)
            

        #if self.Time_Range_Rt is not None:
        #    ax.plot(self.Time_Range_Rt-self.t_ref, self.Range_Rt,'c',label='VBOX_LDWS_VCI')
  
        if C0_right_wheel_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, C0_right_wheel_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, C0_right_wheel_at_t_LDW,"  %5.2f m"%C0_right_wheel_at_t_LDW)
        if C0_right_wheel_filtered_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, C0_right_wheel_filtered_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, C0_right_wheel_filtered_at_t_LDW,"  %5.2f m"%C0_right_wheel_filtered_at_t_LDW)
        if RightFromCPosLateral_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, RightFromCPosLateral_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, RightFromCPosLateral_at_t_LDW,"  %5.2f m"%RightFromCPosLateral_at_t_LDW)

        
        if self.LDW_Right_okay:
            ax.set_ylim(-0.5, 0.5)
        else:
            ax.set_ylim(-0.5+C0_right_wheel_at_t_LDW, 0.5+C0_right_wheel_at_t_LDW)
               
        ax.set_xlim(local_xlim)
    
        ax.legend()
        ax.set_ylabel('outside lane <-- lateral position right [m] --> inside lane')
        ax.grid()
        
        # --------------------------------------------------------
        ax = fig.add_subplot(212)
       
        # lines
        if self.Time_LeftFromBPosLateral is not None:
            ax.plot(self.Time_LeftFromBPosLateral-self.t_ref, self.LeftFromBPosLateral,'c',label='OxTS  %5.2f m'%LeftFromBPosLateral_at_t_LDW)
        ax.plot(self.t_C0_left_wheel-self.t_ref, self.C0_left_wheel,'b',label='C0_left_wheel  %5.2f m'%C0_left_wheel_at_t_LDW)
        ax.plot(self.t_C0_left_wheel_filtered-self.t_ref, self.C0_left_wheel_filtered,'r',label='C0_left_wheel_filtered  %5.2f m'%C0_left_wheel_filtered_at_t_LDW)

        #if self.Time_Range_Lt is not None:
        #    ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt,'c',label='VBOX_LDWS_VCI')

        if C0_left_wheel_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, C0_left_wheel_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, C0_left_wheel_at_t_LDW,"  %5.2f m"%C0_left_wheel_at_t_LDW)
        if C0_left_wheel_filtered_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, C0_left_wheel_filtered_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, C0_left_wheel_filtered_at_t_LDW,"  %5.2f m"%C0_left_wheel_filtered_at_t_LDW)
        if LeftFromBPosLateral_at_t_LDW is not None:
            ax.plot(t_LDW_start-self.t_ref, LeftFromBPosLateral_at_t_LDW,'ms')
            ax.text(t_LDW_start-self.t_ref, LeftFromBPosLateral_at_t_LDW,"  %5.2f m"%LeftFromBPosLateral_at_t_LDW)

        
        
        if self.LDW_Left_okay:
            ax.set_ylim(-0.5, 0.5)
        else:
            ax.set_ylim(-0.5+C0_left_wheel_at_t_LDW, 0.5+C0_left_wheel_at_t_LDW)

        ax.set_xlim(local_xlim)
 
        ax.legend()
        ax.set_ylabel('inside lane <- lateral position left [m] -> outside lane')
   
  
  
        ax.grid()
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

        
        return
        # ----------------------------------------
        # right wheel
      
        if self.LDW_Right_okay:
        
            if self.FrontAxleSpeed_at_t_LDW_Right is not None:
                ax.set_title('Right side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Right*3.6,))
            else:
                ax.set_title('Right side')

    
 
            # fitted 5 points line 
            if self.do_fitted_5_points_line:
                slope, intercept,x,y = fit_line(self.t_LDW_Right_start, self.t_Right_C0, self.Right_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Right_start-t_ref, Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s"%(Right_C0_at_t_LDW_Right,slope))

            # ------------------------------
            # position of when lane marking is touched
            ax.hlines(self.WheelRight,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")
     
            
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Right_at_t_LDW_Right*tlc_0)
            ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Right_C0_at_t_LDW_Right,self.lateral_speed_Right_at_t_LDW_Right,self.Right_C0_at_t_LDW_Right-delta_distance))

            
            # stop
            ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,'ms')
            ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,"  %5.2f m"%self.Right_C0_at_t_LDW_Right_stop)
  
            # ------------------------------
            if yzoom:
               ax.set_ylim(self.Right_C0_at_t_LDW_Right-0.1, self.Right_C0_at_t_LDW_Right+0.1)
            else:
               ax.set_ylim(-1.0, 3.5)
               
       
            ax.set_xlim(local_xlim)
    
            ax.legend()
            ax.set_ylabel('outside lane <-- lateral position right [m] --> inside lane')
            
        if self.LDW_Left_okay:
        
            if self.FrontAxleSpeed_at_t_LDW_Left is not None:
                ax.set_title('Left side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Left*3.6,))
            else:
                ax.set_title('Left side')
        
                
            # lines
            ax.plot(self.t_C0_left_wheel-self.t_ref, self.C0_left_wheel,'b',label='C0_left_wheel')
            ax.plot(self.t_C0_left_wheel_filtered-self.t_ref, self.C0_left_wheel_filtered,'r',label='C0_left_wheel_filtered')
            # filtered signals
            #ax.plot(t_Left_C0-t_ref, f_Left_C0,'kx-')
            if self.Time_LeftFromBPosLateral is not None:
                ax.plot(self.Time_LeftFromBPosLateral-self.t_ref, self.LeftFromBPosLateral,'c',label='OxTS')

            #if self.Time_Range_Lt is not None:
            #    ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt,'c',label='VBOX_LDWS_VCI')

                
            if self.do_fitted_5_points_line:    
                slope, intercept,x,y = fit_line(self.t_LDW_Left_start, self.t_Left_C0, self.Left_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Left_start-t_ref, Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s"%(Left_C0_at_t_LDW_Left,slope))

            # ------------------------------
            ax.hlines(self.WheelLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")

 
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Left_at_t_LDW_Left*tlc_0)
            ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Left_C0_at_t_LDW_Left,self.lateral_speed_Left_at_t_LDW_Left,self.Left_C0_at_t_LDW_Left+delta_distance))
  
            # stop
            ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,'ms')
            ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,"  %5.2f m"%self.Left_C0_at_t_LDW_Left_stop)
  
            # ------------------------------
            #ax.set_ylim((np.min(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop),np.max(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop)))
            ax.set_ylim(-3.5, 1.0)
            ax.set_xlim(local_xlim)
 
            ax.legend()
            ax.set_ylabel('inside lane <- lateral position left [m] -> outside lane')
   
  
  
        ax.grid()
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

    # ===========================================================================
    def plot_2_lane(self,PlotName = 'plot_2_lane',customer_version=False,xlim=None):
        
        if self.verbose:
            print "plot_2_lane()"
           
        if not customer_version:
            PlotName = PlotName + '_internal'
    
        if xlim is not None:
            PlotName = PlotName + '_zoom'
            self.xlim_to_use(xlim)
            local_xlim = xlim
        else:
            self.xlim_to_use(self.xlim_default)
            # plot range:  pre_trigger .. t_ref .. post_trigger
            local_xlim = self.xlim_closeup
            

        warn_zone_inner = 0.0
        warn_zone_outer = self.corridor_outer_boundary/100.0

        #reset_zone_inner = -0.02
        #reset_zone_outer =  0.15

        reset_zone_inner = -0.15
        reset_zone_outer =  0.02
        
        if customer_version:
            x_mark = ''
        else:
            x_mark = 'x-'
        
        # --------------------------------------------------------
        if self.LDW_Right_okay:
            PlotName = PlotName + '_right'
            fig = self.start_fig(PlotName, FigNr=210)
            
            ax = fig.add_subplot(311)
            if self.FrontAxleSpeed_at_t_LDW_Right is not None:
                ax.set_title('Right side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Right*3.6,))
            else:
                ax.set_title('Right side')

            

            # --------------------------------
            # lines
            # OxTS - Ford
            if self.Time_RightLinePosLateral is not None:
                ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral-self.WheelRight,'r', label='OxTS (%5.2f m)'%(self.RightLinePosLateral_at_t_LDW_Right-self.WheelRight,))
            # Racelogic
            if self.Time_Range_Rt is not None:
                ax.plot(self.Time_Range_Rt-self.t_ref, self.Range_Rt-self.WheelRight,'r',label='VBOX_LDWS_VCI (%5.2f m)'%(self.Range_Rt_at_t_LDW_Right-self.WheelRight,))
            if customer_version or self.show_C0:
                ax.plot(self.t_Right_C0-self.t_ref,    self.Right_C0-self.WheelRight,'b'+x_mark,label='FLC20 C0 (%5.2f m)'%(self.Right_C0_at_t_LDW_Right-self.WheelRight,))
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_C0_right_wheel-self.t_ref, self.C0_right_wheel,'m'+x_mark,label='FLC20 C0 wheel')
 
 
 
            # --------------------------------
            # zones 
            ax.hlines(-warn_zone_outer,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.hlines(-warn_zone_inner,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(-warn_zone_inner,warn_zone_inner-warn_zone_outer),alpha=.1, facecolors='red')
  
            if 0:
                ax.hlines(-reset_zone_outer,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.hlines(-reset_zone_inner,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(-reset_zone_inner,reset_zone_inner-reset_zone_outer),alpha=.1, facecolors='blue')

            # --------------------------------
            # Warning Line
            ax.hlines(self.WarningLineRight,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineRight)
       
            # ----------------------------------        
            # marker + text
        
            # start: Right_C0-WheelRight
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,'md')
                #ax.text(t_LDW_Right_start-t_ref, Right_C0_at_t_LDW_Right+right_wheel,"  %5.2f m @ %3.2f m/s"%(Right_C0_at_t_LDW_Right+right_wheel,slope))
                actual_TLC = (self.Right_C0_at_t_LDW_Right-self.WheelRight-self.WarningLineRight)/(-self.lateral_speed_Right_at_t_LDW_Right)
                if customer_version:
                    ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,"  %5.2f m"%(self.Right_C0_at_t_LDW_Right-self.WheelRight,))
                else:
                    ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.Right_C0_at_t_LDW_Right-self.WheelRight,abs(self.lateral_speed_Right_at_t_LDW_Right),actual_TLC))

            if not customer_version and self.show_C0_wheel:
                # start: C0_right_wheel
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.C0_right_wheel_at_t_LDW_Right,'md')
                actual_TLC = (self.C0_right_wheel_at_t_LDW_Right-self.WarningLineRight)/(-self.lateral_speed_Right_at_t_LDW_Right)
                ax.text(self.t_LDW_Right_start-self.t_ref, self.C0_right_wheel_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.C0_right_wheel_at_t_LDW_Right,abs(self.lateral_speed_Right_at_t_LDW_Right),actual_TLC))
             
            # stop: Right_C0_at_t_LDW_Right_stop-WarningLine_Right      
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,'ms')
                ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,"  %5.2f m"%(self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,))

            if not customer_version and self.show_C0_wheel:
                # stop: C0_right_wheel_at_t_LDW_Right_stop
                ax.plot(self.t_LDW_Right_stop-self.t_ref, self.C0_right_wheel_at_t_LDW_Right_stop,'ms')
                ax.text(self.t_LDW_Right_stop-self.t_ref, self.C0_right_wheel_at_t_LDW_Right_stop,"  %5.2f m"%(self.C0_right_wheel_at_t_LDW_Right_stop,))
  
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(self.Right_C0_at_t_LDW_Right-self.WheelRight-0.1,ylim_local[0]),max(self.Right_C0_at_t_LDW_Right-self.WheelRight+0.1,ylim_local[1]))

  
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

            if (not customer_version) or (self.Time_RightLinePosLateral is not None) or (self.Time_Range_Rt is not None):
                ax.legend()
        
            ax.set_ylabel('outer <--right line [m] --> inner')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(312)
    
            # lines
            if self.Time_RightLineVelLateral is not None:
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'y', label='OxTS (raw)')
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral_smoothed,'r', label='OxTS (%3.2f m/s)'%(self.RightLineVelLateral_smoothed_at_t_LDW_Right,))
            
            if self.Time_Lat_Spd_Rt is not None:
                ax.plot(self.Time_Lat_Spd_Rt-self.t_ref, self.Lat_Spd_Rt_smoothed,'r',label='VBOX_LDWS_VCI (%3.2f m/s)'%(self.Lat_Spd_Rt_smoothed_at_t_LDW_Right,))
               
                
            ax.plot(self.t_Right_C0-self.t_ref, self.lateral_speed_Right,'b',label='FLC20 (%3.2f m/s)'%(self.lateral_speed_Right_at_t_LDW_Right,))
           
            # marker + text
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,'md')
            ax.text(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,"%3.2f m/s"%self.lateral_speed_Right_at_t_LDW_Right)
   
            #ax.plot(t_LDW_Left_start-t_ref, lateral_speed_Left_at_t_LDW_Left,'md')
            #ax.text(t_LDW_Left_start-t_ref, lateral_speed_Left_at_t_LDW_Left,"%3.2f m/s"%lateral_speed_Left_at_t_LDW_Left)
            ax.set_ylabel('lateral speed [m/s]')
            if (not customer_version) or (self.Time_RightLineVelLateral is not None) or (self.Time_Lat_Spd_Rt is not None):
                ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-2.1, 2.1)
            ax.grid()        
        
            # --------------------------------------------------------
            # warnings + tracking
            ax = fig.add_subplot(313)
            
            
            
            if customer_version:
                if self.t_WARN_isWarningRight is not None:
                    ax.plot(self.t_WARN_isWarningRight-self.t_ref,    self.WARN_isWarningRight       +6.0,'m', label='LD w/o supp.')
                ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight   +4.0,'b', label='LD Imminent')
                ax.plot(self.t_AcousticalWarningRight-self.t_ref,     self.AcousticalWarningRight    +2.0,'r', label='AcousticalWarning')
                ax.plot(self.t_LDW_Right_Tracking-self.t_ref,         self.LDW_Right_Tracking            ,'k', label='Tracking ')
                ax.set_ylim(-0.1, 7.1)
                ax.legend()
                #ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,9)) 
                ax.set_yticklabels(['Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LD w/o supp. - On'])
            
            else:
                ax.plot(self.t_ME_LDW_LaneDeparture_Right-self.t_ref, self.ME_LDW_LaneDeparture_Right+10.0,'r', label='ME LD (w/o supp) (+10)')
                if self.t_WARN_isWarningRight is not None:
                    ax.plot(self.t_WARN_isWarningRight-self.t_ref,        self.WARN_isWarningRight       + 8.0,'k', label='LNVU LD (w/o supp) (+8)')
                if self.t_LaneDepartImminentRight is not None:
                    ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight   + 6.0,'b', label='LD Imminent (+6)')
                if self.t_AcousticalWarningRight is not None:
                    ax.plot(self.t_AcousticalWarningRight-self.t_ref,     self.AcousticalWarningRight    + 4.0,'m', label='AcousticalWarning (+4)')
                if self.t_LDW_Right_Tracking is not None:
                    ax.plot(self.t_LDW_Right_Tracking-self.t_ref,         self.LDW_Right_Tracking        + 2.0,'c', label='Tracking (+2)')
                if self.t_Lane_Crossing_Right is not None:
                    ax.plot(self.t_Lane_Crossing_Right-self.t_ref,       self.Lane_Crossing_Right,          'r', label='Crossing Right')
                if self.t_Lane_Crossing_Left is not None:
                    ax.plot(self.t_Lane_Crossing_Left-self.t_ref,        self.Lane_Crossing_Left,           'b', label='Crossing Left')
        
                ax.set_ylim(-0.1, 12.1)
                ax.legend()
                ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,13)) 
                ax.set_yticklabels(['Off','Crossing - On','Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LNVU LD - On','Off','ME LD - On'])

            
 
            ax.grid()
            ax.set_xlim(local_xlim)

            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
    
        # --------------------------------------------------------
        if self.LDW_Left_okay:
        
            PlotName = PlotName + '_left'
            fig = self.start_fig(PlotName, FigNr=211)

            ax = fig.add_subplot(311)
            if self.FrontAxleSpeed_at_t_LDW_Left is not None:
                ax.set_title('Left side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Left*3.6,))
            else:
                ax.set_title('Left side')

            

            # --------------------------------------------------        
            # lines
            # OxTS Ford
            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.Time_LeftLinePosLateral-self.t_ref, self.LeftLinePosLateral-self.WheelLeft,'r',label='OxTS (%5.2f m)'%(self.LeftLinePosLateral_at_t_LDW_Left-self.WheelLeft,))
            # Racelogic    
            if self.Time_Range_Lt is not None:
                ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt-self.WheelLeft,'r',label='VBOX_LDWS_VCI (%5.2f m)'%(self.Range_Lt_at_t_LDW_Left-self.WheelLeft,))
            if customer_version or self.show_C0:
                ax.plot(self.t_Left_C0-self.t_ref,       self.Left_C0-self.WheelLeft,'b'+x_mark,label='FLC20 C0 (%5.2f m)'%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,))
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_C0_left_wheel-self.t_ref, self.C0_left_wheel,         'm'+x_mark,label='FLC20 C0 wheel')
 

        
            # --------------------------------
            # zones 
 
            ax.hlines(warn_zone_outer,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.hlines(warn_zone_inner,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(warn_zone_inner,warn_zone_outer-warn_zone_inner),alpha=.1, facecolors='red')
  
            if 0:
                ax.hlines(reset_zone_outer,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.hlines(reset_zone_inner,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(reset_zone_inner,reset_zone_outer-reset_zone_inner),alpha=.1, facecolors='blue')
 
            # ----------------------------------------
            # Warning Line
            ax.hlines(self.WarningLineLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineLeft)

            # ----------------------------------------
            # marker + text
            # start: Left_C0_at_t_LDW_Left+left_wheel
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,'md')
                #ax.text(t_LDW_Left_start-t_ref, Left_C0_at_t_LDW_Left+left_wheel,"  %5.2f m @ %3.2f m/s"%(Left_C0_at_t_LDW_Left+left_wheel,slope))
                print "Left_C0_at_t_LDW_Left",self.Left_C0_at_t_LDW_Left
                print "WheelLeft", self.WheelLeft
                print "WarningLineLeft", self.WarningLineLeft
                actual_TLC = (self.Left_C0_at_t_LDW_Left-self.WheelLeft-self.WarningLineLeft)/self.lateral_speed_Left_at_t_LDW_Left  
                if customer_version:                
                    ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,"  %5.2f m"%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,))
                else:
                    ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,"  %5.2f m @ %3.2f m/s (TLC %3.2f s)"%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,self.lateral_speed_Left_at_t_LDW_Left,np.abs(actual_TLC)))

            # start: C0_left_wheel
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.C0_left_wheel_at_t_LDW_Left,'md')
                actual_TLC = (self.C0_left_wheel_at_t_LDW_Left+self.WarningLineLeft)/abs(self.lateral_speed_Left_at_t_LDW_Left)
                ax.text(self.t_LDW_Left_start-self.t_ref, self.C0_left_wheel_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.C0_left_wheel_at_t_LDW_Left,abs(self.lateral_speed_Left_at_t_LDW_Left),actual_TLC))

        
            # stop: Left_C0_at_t_LDW_Left_stop-WheelLeft
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,'ms')
                ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,"  %5.2f m"%(self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,))
  
            # stop: C0_left_wheel_at_t_LDW_Left_stop
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_LDW_Left_stop-self.t_ref, self.C0_left_wheel_at_t_LDW_Left_stop,'ms')
                ax.text(self.t_LDW_Left_stop-self.t_ref, self.C0_left_wheel_at_t_LDW_Left_stop,"  %5.2f m"%(self.C0_left_wheel_at_t_LDW_Left_stop,))

  
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(self.Left_C0_at_t_LDW_Left-self.WheelLeft-0.1,ylim_local[0]),max(self.Left_C0_at_t_LDW_Left-self.WheelLeft+0.1,ylim_local[1]))
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

        
            if (not customer_version) or (self.Time_LeftLinePosLateral is not None) or (self.Time_Range_Lt is not None):
                ax.legend()
  
            ax.set_ylabel('inner <- left line [m] -> outer')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(312)
    
            # lines
            if self.Time_RightLineVelLateral is not None:
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral,         'y',label='OxTS (raw)')
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral_smoothed,'r',label='OxTS (%3.2f m/s)'%(self.LeftLineVelLateral_smoothed_at_t_LDW_Left,))
        
            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.Time_Lat_Spd_Lt-self.t_ref, self.Lat_Spd_Lt_smoothed,'r',label='VBOX_LDWS_VCI (%3.2f m/s)'%(self.Lat_Spd_Lt_smoothed_at_t_LDW_Left,))

            ax.plot(self.t_Left_C0-self.t_ref, self.lateral_speed_Left,'b',label='FLC20 (%3.2f m/s)'%(self.lateral_speed_Left_at_t_LDW_Left,))
 
        
        
            # marker + text
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,'md')
            ax.text(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,"%3.2f m/s"%self.lateral_speed_Left_at_t_LDW_Left)
            ax.set_ylabel('lateral speed [m/s]')
            if (not customer_version) or (self.Time_RightLineVelLateral is not None) or (self.Time_Lat_Spd_Lt is not None):
                ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-2.1, 2.1)
            ax.grid()        

            # --------------------------------------------------------
            # warnings + tracking
            ax = fig.add_subplot(313)
            
            if customer_version:
                if self.t_WARN_isWarningLeft is not None:
                    ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       +6.0,'m', label='LD w/o supp.')
                ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   +4.0,'b', label='LD Imminent')
                ax.plot(self.t_AcousticalWarningLeft-self.t_ref,     self.AcousticalWarningLeft    +2.0,'r', label='AcousticalWarning')
                ax.plot(self.t_LDW_Left_Tracking-self.t_ref,         self.LDW_Left_Tracking            ,'k', label='Tracking ')
                ax.set_ylim(-0.1, 7.1)
                ax.legend()
                #ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,9)) 
                ax.set_yticklabels(['Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LD w/o supp. - On'])
            
            else:
                ax.plot(self.t_ME_LDW_LaneDeparture_Left-self.t_ref, self.ME_LDW_LaneDeparture_Left+10.0,'r', label='ME LD (w/o supp) (+10)')
                if self.t_WARN_isWarningLeft is not None:
                    ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       + 8.0,'k', label='LNVU LD (w/o supp) (+8)')
                if self.t_LaneDepartImminentLeft is not None:
                    ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   + 6.0,'b', label='LD Imminent (+6)')
                if self.t_AcousticalWarningLeft is not None:
                    ax.plot(self.t_AcousticalWarningLeft-self.t_ref,     self.AcousticalWarningLeft    + 4.0,'m', label='AcousticalWarning (+4)')
                if self.t_LDW_Left_Tracking is not None:
                    ax.plot(self.t_LDW_Left_Tracking-self.t_ref,         self.LDW_Left_Tracking        + 2.0,'c', label='Tracking (+2)')
                if self.t_Lane_Crossing_Right is not None:
                    ax.plot(self.t_Lane_Crossing_Right-self.t_ref,       self.Lane_Crossing_Right,          'r', label='Crossing Right')
                if self.t_Lane_Crossing_Left is not None:
                    ax.plot(self.t_Lane_Crossing_Left-self.t_ref,        self.Lane_Crossing_Left,           'b', label='Crossing Left')
        
                ax.set_ylim(-0.1, 12.1)
                ax.legend()
                ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,13)) 
                ax.set_yticklabels(['Off','Crossing - On','Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LNVU LD - On','Off','ME LD - On'])


            ax.grid()
            ax.set_xlim(local_xlim)
         
            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
            
            
    # ===========================================================================
    def plot_2_lane_homologation(self,PlotName = 'plot_2_lane_homologation',show_internal_signals = False):
        
        if self.verbose:
            print "plot_2_lane_homologation()"
            
        self.plot_2_lane_homologation_one_side(self.left,  PlotName = PlotName, show_internal_signals=show_internal_signals)
        self.plot_2_lane_homologation_one_side(self.right, PlotName = PlotName, show_internal_signals=show_internal_signals)
            
    # ===========================================================================
    def plot_2_lane_homologation_one_side(self,sig, PlotName = 'plot_2_lane_homologation',show_internal_signals = False):
               
        
        if sig.LDW_okay:

            # 
            #  Settings 
            #
                    
            # --------------------------------------------------------
            # homologation requirement: warning has to be issued before this line
            latest_warning_line = 0.3  # [m]
        
            # --------------------------------------------------------
            # local setting for x axis scaling
            local_xlim = self.xlim_closeup
            
            # --------------------------------------------------------
            x_mark = ''
            x_mark = 'x-'
            
            # --------------------------------------------------------
            # PlotName 

            # depending on side
            if sig.side == 'left':            
                PlotName = PlotName + '_left'
            elif sig.side == 'right':            
                PlotName = PlotName + '_right'

            if show_internal_signals:
                 PlotName = PlotName + '_internal'

                
            # --------------------------------------------------------
            # sign depending on side 
            if sig.side == 'left':            
                sign = +1.0
            elif sig.side == 'right':            
                sign = -1.0

                
            # --------------------------------------------------------
            fig = self.start_fig(PlotName, FigNr=211)

            
            
            # --------------------------------------------------------
            # LaneDepartImminent
            ax = fig.add_subplot(411)
            if sig.side == 'left':            
                ax.set_title('Left side')
            elif sig.side == 'right':            
                ax.set_title('Right side')
            
            ax.plot(sig.t_LaneDepartImminent-self.t_ref,    sig.LaneDepartImminent,'b', label='Lane Departure Imminent')
            ax.set_ylim(-0.1, 1.1)
            ax.legend()
            ax.set_yticks(np.arange(0,2)) 
            ax.set_yticklabels(['Off','On'])
            
            ax.grid()
            ax.set_xlim(local_xlim)
            
            
            # --------------------------------------------------        
            # position
           
            ax = fig.add_subplot(412)
                  
            # --------------------------------------------------        
            # lines
            # OxTS Ford
            if sig.Time_OxTS_LinePosLateral is not None:
                ax.plot(sig.Time_OxTS_LinePosLateral-self.t_ref, sig.OxTS_LinePosLateral-sig.Wheel-sign*sig.width_lane_marking,'b',label='OxTS (%5.2f m)'%(sig.OxTS_LinePosLateral_at_t_LDW-sig.Wheel-sign*sig.width_lane_marking,))
            # Racelogic    
            if sig.Time_VBOX_Range_t is not None:
                ax.plot(sig.Time_VBOX_Range_t-self.t_ref,        sig.VBOX_Range_t-sig.Wheel-sign*sig.width_lane_marking,       'b',label='VBOX (reference)(%5.2f m)'%(sig.VBOX_Range_t_at_t_LDW-sig.Wheel-sign*sig.width_lane_marking,))
            # FLC20    
            if show_internal_signals:
                ax.plot(sig.t_C0-self.t_ref,                     sig.C0-sig.Wheel-sign*sig.width_lane_marking,   'c'+x_mark,  label='FLC20 (internal) (%5.2f m)'%(sig.C0_at_t_LDW -sig.Wheel-sign*sig.width_lane_marking,))
                    
            # --------------------------------
            # zones 
            ax.hlines(sign*latest_warning_line,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed', label="Latest Warning Line %3.2f m"%(sign*latest_warning_line,))

 
            warn_zone_outer = 0.0
            warn_zone_inner = -sign*sig.width_lane_marking
            ax.hlines(warn_zone_outer,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.hlines(warn_zone_inner,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(warn_zone_inner,warn_zone_outer-warn_zone_inner),alpha=.3, facecolors='grey')
  
            ax.text(local_xlim[0]+0.05*(local_xlim[1]-local_xlim[0]),0.65*(warn_zone_outer+warn_zone_inner),"%s lane marking (width=%3.2f m)"%(sig.side, sig.width_lane_marking,))

            # ----------------------------------------
            # Warning Line
            #ax.hlines(self.WarningLineLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineLeft)

            # ----------------------------------------
            # marker + text
            # OxTS Ford
            if sig.Time_OxTS_LinePosLateral is not None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.OxTS_LinePosLateral_at_t_LDW-sig.Wheel-sign*sig.width_lane_marking,'md',"  %5.2f m")
            # Racelogic 
            if sig.Time_VBOX_Range_t is not None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.VBOX_Range_t_at_t_LDW-sig.Wheel-sign*sig.width_lane_marking,'md',"  %5.2f m")
            # FLC20    
            if show_internal_signals:    
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.C0_at_t_LDW-sig.Wheel-sign*sig.width_lane_marking,'md',"  %5.2f m")
            
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(sig.C0_at_t_LDW-sig.Wheel-0.1,ylim_local[0]),max(sig.C0_at_t_LDW-sig.Wheel+0.1,ylim_local[1]))
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

            ax.legend()
  
            if sig.side == 'left':            
                ax.set_ylabel('inner <- position [m] -> outer')
            elif sig.side == 'right':            
                ax.set_ylabel('outer <- position [m] -> inner')
            
            
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(413)

            # line            
            # OxTS
            if sig.Time_OxTS_LineVelLateral is not None:
                ax.plot(sig.Time_OxTS_LineVelLateral-self.t_ref, sig.OxTS_LineVelLateral_smoothed,'b',label='OxTS (%3.2f m/s)'%(sig.OxTS_LineVelLateral_smoothed_at_t_LDW))

            # Racelogic                
            if sig.Time_VBOX_Lat_Spd_t is not None:
                ax.plot(sig.Time_VBOX_Lat_Spd_t-self.t_ref, sig.VBOX_Lat_Spd_t_smoothed,'b',label='VBOX (reference) (%3.2f m/s)'%(sig.VBOX_Lat_Spd_t_smoothed_at_t_LDW,))
            
            # FLC20            
            if show_internal_signals:
                ax.plot(sig.t_C0-self.t_ref, sig.lateral_speed,'c',label='FLC20 (internal) (%3.2f m/s)'%(sig.lateral_speed_at_t_LDW,))


           
            # marker + text
            # OxTS
            if sig.Time_OxTS_LineVelLateral is not None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.OxTS_LineVelLateral_smoothed_at_t_LDW,'md',"   %3.2f m/s")

            # Racelogic   
            if sig.Time_VBOX_Lat_Spd_t is not None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.VBOX_Lat_Spd_t_smoothed_at_t_LDW,'md',"   %3.2f m/s")

            # FLC20            
            if show_internal_signals:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.lateral_speed_at_t_LDW,'md',"   %3.2f m/s")
               
        
            
            ax.set_ylabel('lateral speed [m/s]')
            ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-1.3, 1.3)
            ax.grid()        

           
         

            # --------------------------------------------------------
            # 
            ax = fig.add_subplot(414)
            
            # line     
            # Racelogic VBox            
            if self.Time_VBOX_Velocity_kmh is not None:
                ax.plot(self.Time_VBOX_Velocity_kmh-self.t_ref,    self.VBOX_Velocity_kmh,'b', label='VBOX (reference) (%3.2f km/h)'%(sig.VBOX_Velocity_kmh_at_t_LDW,))
            # J1939
            if show_internal_signals or self.Time_VBOX_Velocity_kmh is None:
                if self.FrontAxleSpeed is not None:
                    ax.plot(self.t_FrontAxleSpeed-self.t_ref,          self.FrontAxleSpeed*3.6,'c', label='J1939 (%3.2f km/h)'%(sig.FrontAxleSpeed_at_t_LDW*3.6,))
            
             
            # marker + text
            # Racelogic VBox    
            if self.Time_VBOX_Velocity_kmh is not None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.VBOX_Velocity_kmh_at_t_LDW,'md',"   %3.2f km/h")
            # J1939
            if show_internal_signals or self.Time_VBOX_Velocity_kmh is None:
                self.mark_point(ax,sig.t_LDW_start-self.t_ref,sig.FrontAxleSpeed_at_t_LDW*3.6,'md',"   %3.2f km/h")
        
            
            ax.set_ylim(-0.1, 90.1)
            ax.legend()
            
            
            ax.grid()
            ax.set_xlim(local_xlim)
            ax.set_ylabel('vehicle speed [km/h]')
         
            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
            
    # ===========================================================================
    def plot_2_lane_homologation_old(self,PlotName = 'plot_2_lane_homologation'):
        
        if self.verbose:
            print "plot_2_lane_homologation()"
      
        # LM lane marking
        width_LM_left = 0.23
        width_LM_right = 0.12
        
        latest_warning_line = 0.3
        
        x_mark = ''
        
        show_internal_signals = False
        
        # --------------------------------------------------------
        if self.LDW_Right_okay:
        
            self.Range_Rt_at_t_LDW_Right          = kbtools.GetPreviousSample(self.Time_Range_Rt,         self.Range_Rt,         self.t_LDW_Right_start)
            self.Lat_Spd_Rt_smoothed_at_t_LDW_Right        = kbtools.GetPreviousSample(self.Time_Lat_Spd_Rt,       self.Lat_Spd_Rt_smoothed,       self.t_LDW_Right_start)
            self.VBOX_Velocity_kmh_at_t_LDW_Right = kbtools.GetPreviousSample(self.Time_VBOX_Velocity_kmh,self.VBOX_Velocity_kmh,self.t_LDW_Right_start)
        
            local_xlim = self.xlim_closeup
              
            PlotName = PlotName + '_right'
            fig = self.start_fig(PlotName, FigNr=211)

            
            
            # --------------------------------------------------------
            # warnings 
            ax = fig.add_subplot(411)
            ax.set_title('Right side')
            
            ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight,'b', label='Lane Departure Imminent')
            ax.set_ylim(-0.1, 1.1)
            ax.legend()
            ax.set_yticks(np.arange(0,2)) 
            ax.set_yticklabels(['Off','On'])
            
            ax.grid()
            ax.set_xlim(local_xlim)
            
            
            # --------------------------------------------------        
           
            ax = fig.add_subplot(412)
                  
            # --------------------------------------------------        
            # lines
            # OxTS Ford
            if self.Time_RightLinePosLateral is not None:
                ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral-self.WheelRight+width_LM_right,'b',label='OxTS')
            # Racelogic    
            if self.Time_Range_Rt is not None:
                ax.plot(self.Time_Range_Rt-self.t_ref, self.Range_Rt-self.WheelRight+width_LM_right,'b',label='VBOX (reference)')
                
            if show_internal_signals:
                ax.plot(self.t_Right_C0-self.t_ref,       self.Right_C0-self.WheelLeft+width_LM_right,'c'+x_mark,label='FLC20 (internal)')
            
        
            # --------------------------------
            # zones 
            ax.hlines(-latest_warning_line,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed', label="Latest Warning Line %3.2f m"%(-latest_warning_line,))

 
            warn_zone_outer = 0.0
            warn_zone_inner = width_LM_right
            ax.hlines(warn_zone_outer,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.hlines(warn_zone_inner,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(warn_zone_inner,warn_zone_outer-warn_zone_inner),alpha=.3, facecolors='grey')
  
            ax.text(local_xlim[0]+0.05*(local_xlim[1]-local_xlim[0]),0.3*(warn_zone_outer+warn_zone_inner),"right lane marking (width=%3.2f m)"%(width_LM_right,))

 
            
            # ----------------------------------------
            # Warning Line
            #ax.hlines(self.WarningLineLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineLeft)

            # ----------------------------------------
            # marker + text
            # start: Left_C0_at_t_LDW_Left+left_wheel
            if self.Time_Range_Rt is not None:
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.Range_Rt_at_t_LDW_Right-self.WheelRight+width_LM_right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, self.Range_Rt_at_t_LDW_Right-self.WheelRight+width_LM_right,"  %5.2f m"%(self.Range_Rt_at_t_LDW_Right-self.WheelRight+width_LM_right,))
             
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(self.Right_C0_at_t_LDW_Right-self.WheelRight-0.1,ylim_local[0]),max(self.Right_C0_at_t_LDW_Right-self.WheelRight+0.1,ylim_local[1]))
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

            ax.legend()
  
            ax.set_ylabel('inner <- position [m] -> outer')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(413)
    
            # lines
            if self.Time_RightLineVelLateral is not None:
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'b',label='OxTS')
        
            if self.Time_Lat_Spd_Rt is not None:
                ax.plot(self.Time_Lat_Spd_Rt-self.t_ref, self.Lat_Spd_Rt_smoothed,'b',label='VBOX (reference)')
                
            if show_internal_signals:
                ax.plot(self.t_Right_C0-self.t_ref, self.lateral_speed_Right,'c',label='FLC20 (internal)')
 
        
            # marker + text
            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.Lat_Spd_Rt_smoothed_at_t_LDW_Right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, self.Lat_Spd_Rt_smoothed_at_t_LDW_Right,"%3.2f m/s"%self.Lat_Spd_Rt_smoothed_at_t_LDW_Right)
            
            ax.set_ylabel('lateral speed [m/s]')
            ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-1.3, 1.3)
            ax.grid()        

           
         

            # --------------------------------------------------------
            # VBOX_Velocity_kmh 
            ax = fig.add_subplot(414)
                       
            if self.Time_VBOX_Velocity_kmh is not None:
                ax.plot(self.Time_VBOX_Velocity_kmh-self.t_ref,    self.VBOX_Velocity_kmh,'b', label='VBOX (reference)')
                
            if show_internal_signals:
                if self.FrontAxleSpeed is not None:
                    ax.plot(self.t_FrontAxleSpeed-self.t_ref,          self.FrontAxleSpeed*3.6,'c', label='J1939')
           
           
            if self.Time_VBOX_Velocity_kmh is not None:
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.VBOX_Velocity_kmh_at_t_LDW_Right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, self.VBOX_Velocity_kmh_at_t_LDW_Right,"%3.2f km/h"%self.VBOX_Velocity_kmh_at_t_LDW_Right)
   
            
            
            ax.set_ylim(-0.1, 80.1)
            ax.legend()
            
            
            ax.grid()
            ax.set_xlim(local_xlim)
            ax.set_ylabel('vehicle speed [km/h]')
         
            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
            
        # --------------------------------------------------------
        if self.LDW_Left_okay:
        
        
            local_xlim = self.xlim_closeup
              
            PlotName = PlotName + '_left'
            fig = self.start_fig(PlotName, FigNr=211)

            
            
            # --------------------------------------------------------
            # LaneDepartImminent
            ax = fig.add_subplot(411)
            ax.set_title('Left side')
            
            ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft,'b', label='Lane Departure Imminent')
            ax.set_ylim(-0.1, 1.1)
            ax.legend()
            ax.set_yticks(np.arange(0,2)) 
            ax.set_yticklabels(['Off','On'])
            
            ax.grid()
            ax.set_xlim(local_xlim)
            
            
            # --------------------------------------------------        
            # position
           
            ax = fig.add_subplot(412)
                  
            # --------------------------------------------------        
            # lines
            # OxTS Ford
            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.Time_LeftLinePosLateral-self.t_ref, self.LeftLinePosLateral-self.WheelLeft-width_LM_left,'b',label='OxTS')
            # Racelogic    
            if self.Time_Range_Lt is not None:
                ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt-self.WheelLeft-width_LM_left,'b',label='VBOX (reference)')
            # FLC20    
            if show_internal_signals:
                ax.plot(self.t_Left_C0-self.t_ref,       self.Left_C0-self.WheelLeft-width_LM_left,'c'+x_mark,label='FLC20 (internal)')
            
        
            # --------------------------------
            # zones 
            ax.hlines(latest_warning_line,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed', label="Latest Warning Line %3.2f m"%latest_warning_line)

 
            warn_zone_outer = 0.0
            warn_zone_inner = -width_LM_left
            ax.hlines(warn_zone_outer,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.hlines(warn_zone_inner,local_xlim[0],local_xlim[1],colors='k',linestyles='solid')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(warn_zone_inner,warn_zone_outer-warn_zone_inner),alpha=.3, facecolors='grey')
  
            ax.text(local_xlim[0]+0.05*(local_xlim[1]-local_xlim[0]),0.65*(warn_zone_outer+warn_zone_inner),"left lane marking (width=%3.2f m)"%(width_LM_left,))

            # ----------------------------------------
            # Warning Line
            #ax.hlines(self.WarningLineLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineLeft)

            # ----------------------------------------
            # marker + text
            # OxTS Ford
            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.LeftLinePosLateral_at_t_LDW_Left-self.WheelLeft-width_LM_left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.LeftLinePosLateral_at_t_LDW_Left-self.WheelLeft-width_LM_left,"  %5.2f m"%(self.LeftLinePosLateral_at_t_LDW_Left-self.WheelLeft-width_LM_left,))
            # Racelogic 
            if self.Time_Range_Lt is not None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.Range_Lt_at_t_LDW_Left-self.WheelLeft-width_LM_left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.Range_Lt_at_t_LDW_Left-self.WheelLeft-width_LM_left,"  %5.2f m"%(self.Range_Lt_at_t_LDW_Left-self.WheelLeft-width_LM_left,))
             
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(self.Left_C0_at_t_LDW_Left-self.WheelLeft-0.1,ylim_local[0]),max(self.Left_C0_at_t_LDW_Left-self.WheelLeft+0.1,ylim_local[1]))
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

            ax.legend()
  
            ax.set_ylabel('inner <- position [m] -> outer')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(413)

            # line            
            # OxTS
            if self.Time_LeftLineVelLateral is not None:
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral_smoothed,'b',label='OxTS')

            # Racelogic                
            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.Time_Lat_Spd_Lt-self.t_ref, self.Lat_Spd_Lt_smoothed,'b',label='VBOX (reference)')
            
            # FLC20            
            if show_internal_signals:
                ax.plot(self.t_Left_C0-self.t_ref, self.lateral_speed_Left,'c',label='FLC20 (internal)')


           
            # marker + text
            # OxTS
            if self.Time_LeftLineVelLateral is not None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.LeftLineVelLateral_smoothed_at_t_LDW_Left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.LeftLineVelLateral_smoothed_at_t_LDW_Left,"%3.2f m/s"%self.LeftLineVelLateral_smoothed_at_t_LDW_Left)

            # Racelogic   
            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.Lat_Spd_Lt_smoothed_at_t_LDW_Left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.Lat_Spd_Lt_smoothed_at_t_LDW_Left,"%3.2f m/s"%self.Lat_Spd_Lt_smoothed_at_t_LDW_Left)
               
        
            
            ax.set_ylabel('lateral speed [m/s]')
            ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-1.3, 1.3)
            ax.grid()        

           
         

            # --------------------------------------------------------
            # 
            ax = fig.add_subplot(414)
            
            # line     
            # Racelogic VBox            
            if self.Time_VBOX_Velocity_kmh is not None:
                ax.plot(self.Time_VBOX_Velocity_kmh-self.t_ref,    self.VBOX_Velocity_kmh,'b', label='VBOX (reference)')
            # J1939
            if show_internal_signals or self.Time_VBOX_Velocity_kmh is None:
                if self.FrontAxleSpeed is not None:
                    ax.plot(self.t_FrontAxleSpeed-self.t_ref,          self.FrontAxleSpeed*3.6,'c', label='J1939')
            
             
            # marker + text
            # Racelogic VBox    
            if self.Time_VBOX_Velocity_kmh is not None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.VBOX_Velocity_kmh_at_t_LDW_Left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.VBOX_Velocity_kmh_at_t_LDW_Left,"%3.2f km/h"%self.VBOX_Velocity_kmh_at_t_LDW_Left)
            # J1939
            if show_internal_signals or self.Time_VBOX_Velocity_kmh is None:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.FrontAxleSpeed_at_t_LDW_Left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, self.FrontAxleSpeed_at_t_LDW_Left,"%3.2f km/h"%self.FrontAxleSpeed_at_t_LDW_Left*3.6)
            
            
            ax.set_ylim(-0.1, 90.1)
            ax.legend()
            
            
            ax.grid()
            ax.set_xlim(local_xlim)
            ax.set_ylabel('vehicle speed [km/h]')
         
            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
                        
    # ===========================================================================
    def plot_3_warnings(self, PlotName = 'plot_3_warnings'):
        
        if self.verbose:
            print "plot_3_warnings()"

        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=300)
        
        
        local_xlim = self.xlim_closeup
        
        
        # ------------------------------------------------------
        # LDWS State
        ax = fig.add_subplot(311)
        ax.plot(self.t_StateOfLDWS-self.t_ref , self.StateOfLDWS          ,'b', label='LDWS State')
        ax.set_ylabel('State')
        ax.legend()
        ax.set_ylim(-0.1, 15.1)
        ax.set_yticks(range(16))   
        label1 = ['Not ready (0)','Temp. not avail. (1)','Deact. by driver (2)','Ready (3)']
        label2 = ['Driver override (4)','Warning (5)','(6)','(7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)
        ax.set_xlim(local_xlim)
        ax.grid()
        
        # --------------------------------------------------------
        # Right side
        ax = fig.add_subplot(312)
        ax.set_title('Right side')

        if self.t_ME_LDW_LaneDeparture_Right is not None:
            ax.plot(self.t_ME_LDW_LaneDeparture_Right-self.t_ref, self.ME_LDW_LaneDeparture_Right+8,'rx-', label = 'ME')
            #ax.plot(self.t_LDW_LaneDeparture_Right-self.t_ref,    self.LDW_LaneDeparture_Right+6,   'bx-', label = 'intern')

        if self.t_WARN_isWarningRight is not None:
            ax.plot(self.t_WARN_isWarningRight-self.t_ref,    self.WARN_isWarningRight+6,   'bx-', label = 'LNVU')
            
         
        ax.plot(self.t_LaneDepartImminentRight-self.t_ref,        self.LaneDepartImminentRight+4,   'mx-', label = 'FLI1 Imm')
        ax.plot(self.t_AcousticalWarningRight-self.t_ref,         self.AcousticalWarningRight+2,    'kx-', label = 'FLI1 Aco')
        ax.plot(self.t_OpticalWarningRight-self.t_ref,            self.OpticalWarningRight,         'yx-', label = 'FLI1 Opt')

        ax.set_ylabel('right')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On','Off','On'])

        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
   
        ax.grid()

        # --------------------------------------------------------
        # Left side
        ax = fig.add_subplot(313)
        ax.set_title('Left side')

        
        if self.t_ME_LDW_LaneDeparture_Left is not None:
            ax.plot(self.t_ME_LDW_LaneDeparture_Left-self.t_ref, self.ME_LDW_LaneDeparture_Left+8,'rx-', label = 'ME')
            #ax.plot(self.t_LDW_LaneDeparture_Left-self.t_ref,    self.LDW_LaneDeparture_Left+6,   'bx-', label = 'intern')

        if self.t_WARN_isWarningLeft is not None:
            ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft+6,   'bx-', label = 'LNVU')

        ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,        self.LaneDepartImminentLeft+4,   'mx-', label = 'FLI1 Imm')
        ax.plot(self.t_AcousticalWarningLeft-self.t_ref,         self.AcousticalWarningLeft+2,    'kx-', label = 'FLI1 Aco')
        ax.plot(self.t_OpticalWarningLeft-self.t_ref,            self.OpticalWarningLeft,         'yx-', label = 'FLI1 Opt')
        
        ax.set_ylabel('left')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On','Off','On'])

        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
     
        
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
        
    # ===========================================================================
    def plot_3_warnings_old(self, PlotName = 'plot_3_warnings'):
        
        if self.verbose:
            print "plot_3_warnings()"

        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=300)
        
        
        local_xlim = self.xlim_closeup
        
        # --------------------------------------------------------
        # Right side
        ax = fig.add_subplot(211)
        ax.set_title('Right side')

        if self.t_ME_LDW_LaneDeparture_Right is not None:
            ax.plot(self.t_ME_LDW_LaneDeparture_Right-self.t_ref, self.ME_LDW_LaneDeparture_Right+8,'rx-', label = 'ME')
            ax.plot(self.t_LDW_LaneDeparture_Right-self.t_ref,    self.LDW_LaneDeparture_Right+6,   'bx-', label = 'intern')
         
        ax.plot(self.t_LaneDepartImminentRight-self.t_ref,        self.LaneDepartImminentRight+4,   'mx-', label = 'FLI1 Imm')
        ax.plot(self.t_AcousticalWarningRight-self.t_ref,         self.AcousticalWarningRight+2,    'kx-', label = 'FLI1 Aco')
        ax.plot(self.t_OpticalWarningRight-self.t_ref,            self.OpticalWarningRight,         'yx-', label = 'FLI1 Opt')

        ax.set_ylabel('right')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On','Off','On'])

        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
   
        ax.grid()

        # --------------------------------------------------------
        # Left side
        ax = fig.add_subplot(212)
        ax.set_title('Left side')

        if self.t_ME_LDW_LaneDeparture_Left is not None:
            ax.plot(self.t_ME_LDW_LaneDeparture_Left-self.t_ref, self.ME_LDW_LaneDeparture_Left+8,'rx-', label = 'ME')
            ax.plot(self.t_LDW_LaneDeparture_Left-self.t_ref,    self.LDW_LaneDeparture_Left+6,   'bx-', label = 'intern')

        ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,        self.LaneDepartImminentLeft+4,   'mx-', label = 'FLI1 Imm')
        ax.plot(self.t_AcousticalWarningLeft-self.t_ref,         self.AcousticalWarningLeft+2,    'kx-', label = 'FLI1 Aco')
        ax.plot(self.t_OpticalWarningLeft-self.t_ref,            self.OpticalWarningLeft,         'yx-', label = 'FLI1 Opt')
        
        ax.set_ylabel('left')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On','Off','On'])

        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
     
        
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
        
    
    # ===========================================================================
    def plot_4_lanes(self, PlotName = 'plot_4_lanes'):
        
        if self.verbose:
            print "plot_4_lanes()"
    
        if (self.t_Right_C0 is None) or (self.t_Left_C0 is None):
            return
    
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=400)
        
        local_xlim = self.xlim_closeup

        # --------------------------------------------------------
        # tracking
        ax = fig.add_subplot(711)
    
        if self.t_Lane_Crossing_Right is not None:
            ax.plot(self.t_Lane_Crossing_Right-self.t_ref,        self.Lane_Crossing_Right+6.0,'r',  label='Crossing Right (+6)')
        if self.t_Lane_Crossing_Left is not None:
            ax.plot(self.t_Lane_Crossing_Left-self.t_ref,         self.Lane_Crossing_Left+4.0, 'b',  label='Crossing Left  (+4)')

        ax.plot(self.t_LDW_Right_Tracking-self.t_ref,         self.LDW_Right_Tracking+2.0, 'r',  label='Tracking Right (+2)')
        ax.plot(self.t_LDW_Left_Tracking-self.t_ref,          self.LDW_Left_Tracking,      'b',  label='Tracking Left')
      
        ax.set_ylim(-0.1, 8.1)
        ax.legend()
        ax.set_ylabel('Flags')
        ax.set_yticks(np.arange(0,9)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On'])

        ax.grid()
        ax.set_xlim(local_xlim)
  
        # --------------------------------------------------------
        ax = fig.add_subplot(712)
        ax.plot(self.t_Right_C0-self.t_ref, self.Right_C0,'r',label='C0 right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C0, 'b',label='C0 left')
        ax.set_ylabel('[m]')
        ax.legend()
        ax.set_ylim(-5.1, 5.1)
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        ax = fig.add_subplot(713)
        ax.plot(self.t_Right_C0-self.t_ref, self.Right_C1,'r',label='C1 right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C1, 'b',label='C1 left')
        ax.set_ylabel('[rad]')
        ax.legend()
        ax.set_ylim(-0.2, 0.2)
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
    
        ax = fig.add_subplot(714)
        ax.plot(self.t_Right_C0-self.t_ref, self.Right_C2,'r',label='C2 right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C2, 'b',label='C2 left')
        ax.set_ylabel('[rad/s]')
        ax.legend()
        ax.set_ylim(-0.005, 0.005)
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        ax = fig.add_subplot(715)
        ax.plot(self.t_Right_C0-self.t_ref, self.Right_C3,'r',label='C3 right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C3, 'b',label='C3 left')
        ax.set_ylabel('[rad/s$^2$]')
        ax.legend()
        ax.set_ylim(-0.00002, 0.00002)
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ------------------------------------------------------
        # View range
        ax = fig.add_subplot(716)
        ax.plot(self.t_View_Range_Right-self.t_ref, self.View_Range_Right,'r',label='View_Range right')
        ax.plot(self.t_View_Range_Left-self.t_ref,  self.View_Range_Left, 'b',label='View_Range left')
        ax.set_ylabel('[m]')
        ax.legend()
        ax.set_ylim(-5.0, 105.0)
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
    
      
    
        # ------------------------------------------------------
        # yaw rate
        ax = fig.add_subplot(717)
        if self.Time_YawRate is not None:
            ax.plot(self.Time_YawRate-self.t_ref, self.YawRate, 'b',label='yaw rate')
        ax.set_ylabel('[rad/s]')
        ax.legend()
        ax.set_ylim(-0.3, 0.3)
        ax.set_xlim(local_xlim)
        ax.grid()

        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
        
     # ===========================================================================
    def plot_5_lateral_speed(self, PlotName = 'plot_5_lateral_speed'):
  
        if self.verbose:
            print "plot_5_lateral_speed()"
  
        if (self.t_Right_C0 is None) or (self.t_Left_C0 is None):
            return

       

        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=500)
        
        local_xlim = self.xlim_closeup
    
        ax = fig.add_subplot(211)
        ax.set_title('Right side')

        #ax.plot(self.t_Right_C0-self.t_ref, self.fd_Right_C0,'rx-',label='dC0/dt (calc.)')
        #ax.plot(self.t_Right_C0-self.t_ref, self.vy_Right,   'bx-',label='C1*v (calc.)')
        if self.Lateral_Velocity_Right_B is not None:
            ax.plot(self.t_Right_C0-self.t_ref, self.Lateral_Velocity_Right_B,   'b',label='FLC20')
        
        if self.Time_RightLineVelLateral is not None:  
            ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'r',label='OxTS')
          
        if self.Time_Lat_Spd_Rt is not None:
            ax.plot(self.Time_Lat_Spd_Rt-self.t_ref, self.Lat_Spd_Rt_smoothed,'r',label='VBOX_LDWS_VCI')
                    
    
        ax.set_ylabel('[m/s] Right')
        ax.legend()
        ax.set_ylim(-2.1, 2.1)
        ax.set_xlim(local_xlim)
        #ax.set_xlim((self.t_event-self.t_ref-2.0,self.t_event-self.t_ref+2.0))
        ax.grid()

        # -------------------------------------------------------------- 
        ax = fig.add_subplot(212)
        ax.set_title('Left side')

        #ax.plot(self.t_Left_C0-self.t_ref, self.fd_Left_C0,'rx-',label='dC0/dt')
        #ax.plot(self.t_Left_C0-self.t_ref, self.vy_Left,   'bx-',label='C1*v')
        
        if self.Lateral_Velocity_Left_B is not None:
            ax.plot(self.t_Left_C0-self.t_ref, self.Lateral_Velocity_Left_B,   'b',label='FLC20')

        if self.Time_LeftLineVelLateral is not None:
            ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral,'r', label='OxTS')

        if self.Time_Lat_Spd_Lt is not None:
            ax.plot(self.Time_Lat_Spd_Lt-self.t_ref, self.Lat_Spd_Lt_smoothed,'r',label='VBOX_LDWS_VCI')
                       

        ax.set_ylabel('[m/s] Left')
        ax.legend()
        
        ax.set_ylim(-2.1, 2.1)
        ax.set_xlim(local_xlim)
        #ax.set_xlim((self.t_event-self.t_ref-2.0,self.t_event-self.t_ref+2.0))
        ax.grid()
    
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
    
       
    # ===========================================================================
    def plot_9_error_handler(self, PlotName = 'plot_9_error_handler'):
        
        if self.verbose:
            print "plot_9_error_handler()"

        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=300)
        
        
        local_xlim = self.xlim_closeup
        
        
        # ------------------------------------------------------
        # LDWS State
        ax = fig.add_subplot(211)
        ax.plot(self.t_StateOfLDWS-self.t_ref , self.StateOfLDWS          ,'b', label='LDWS State')
        ax.set_ylabel('State')
        ax.legend()
        ax.set_ylim(-0.1, 15.1)
        ax.set_yticks(range(16))   
        label1 = ['Not ready (0)','Temp. not avail. (1)','Deact. by driver (2)','Ready (3)']
        label2 = ['Driver override (4)','Warning (5)','(6)','(7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)
        ax.set_xlim(local_xlim)
        ax.grid()
        
        
        # --------------------------------------------------------
        # LDW_Buzzer
        ax = fig.add_subplot(212)
        ax.set_title('Inputs')

        if self.t_LDW_Buzzer is not None:
            ax.plot(self.t_LDW_Buzzer-self.t_ref, self.LDW_Buzzer,'r-', label = 'LDW_Buzzer')
            
        ax.set_ylabel('flags')
        ax.legend()
        ax.set_ylim(-0.1, 4.1)
        ax.set_yticks(np.arange(0,4)) 
        ax.set_yticklabels(['Not operational','Fully operational','Error','Not available'])
        
        #ax.set_xlim((t_event-1.0,t_event+1.0))
        ax.set_xlim(local_xlim)
   
        ax.grid()

     
        
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()


   
# ==================================================================================================================================================
# ==================================================================================================================================================
# ==================================================================================================================================================
class cPlotFLC20LDWS(cPlotFLC20LDWSBase):

   
    # ==========================================================
    def __init__(self, FLR20_sig, t_event, xlim=None, PngFolder = r".\png", VehicleName=None, show_figures=False, cfg={} ,verbose=False):
        '''
            FLR20_sig    : a) dictionary with measured signals 
                           b) CSimOL_MatlabBinInterface instance
            t_event      : start of lane departure warning
            xlim         : plot range for x x-axis
            PngFolder    : destination folder for created png files
            VehicleName  : vehicle name used to select vehicle specific parameters like distances to left and right wheel
                           ["Ford_H566PP","Karsan_JEST_Minibus"]
            show_figures : switch to enable that matplotlib figures ared displayed
            verbose      : print debug messages
        '''
    
        if verbose:    # self.verbose is not yet available
            print "cPlotFLC20LDWS.__init__() - start"
            
        cPlotFLC20LDWSBase.__init__(self,FLR20_sig=FLR20_sig, t_event=t_event, xlim=xlim, PngFolder = PngFolder, VehicleName=VehicleName, show_figures=show_figures, cfg=cfg ,verbose=verbose)
        
        if self.verbose:
            print "cPlotFLC20LDWS.__init__() - end"
        
            
        
 
    #=================================================================================
    def PlotAll(self,enable_png_extract = True,OffsetList=None, mode='standard', test_mode_f = False):
        
        if self.verbose:
            print "cPlotFLC20LDWS.PlotAll() - start"
        # ----------------------------------------------------------------------------------- 
        # extract frames from video
        
        if enable_png_extract:
            if self.verbose:
                print "---------------------------------------"
                print "extract frames from video:"
            FullPathFileName = self.FLR20_sig['FileName_org']
            if OffsetList is None:
                OffsetList = [-4.0,-3.5,-3.0,-2.5,-2.0,-1.5, -1.0, -0.5, 0.0, +0.5, +1.0, +1.5, +2.0, +2.5] 
            kbtools_user.CreateVideoSnapshots(FullPathFileName,self.FLR20_sig, self.t_event, OffsetList = OffsetList, PngFolder = self.PngFolder,verbose=self.verbose)
                    
        # ----------------------------------------------------------------------------------- 
        # plot
        if test_mode_f:
            self.plot_1_C0_Filter()
            self.plot_2_lane_homologation(show_internal_signals = True)
            self.plot_2_lane_homologation(show_internal_signals = False)
            self.plot_2_lane(customer_version=False)
            self.plot_2_lateral_position()
            self.plot_2_lateral_position_wheel()
            return

        if mode == "standard":
            self.plot_1_ego_vehicle()
            self.plot_7_CAN_Delay()
            #self.plot_1_overview()
            self.plot_2_lane(customer_version=False)
            #self.plot_2_lane(customer_version=True)
            #self.plot_2_lane_homologation(show_internal_signals = True)
            #self.plot_2_lane_homologation(show_internal_signals = False)
            self.plot_2_lateral_position()
            #self.plot_2_lateral_position_wheel()
            #self.plot_3_warnings()
            #self.plot_4_lanes()
            self.plot_5_lateral_speed()
            #self.plot_6_driver()
            self.plot_6_suppressors()
            self.plot_6_Suppr_HIGH_STEERING_RATE()
            self.plot_6_AccelLateral()
            #self.plot_7_TLC()
            #self.plot_8_View_Range()
            #self.plot_9_error_handler()
            #self.plot_2_lateral_position_at_front_axle_position()
        elif mode == "extended":
            self.plot_1_ego_vehicle()
            self.plot_7_CAN_Delay()
            #self.plot_1_overview()
            self.plot_2_lane(customer_version=False)
            #self.plot_2_lane(customer_version=True)
            #self.plot_2_lane_homologation(show_internal_signals = True)
            #self.plot_2_lane_homologation(show_internal_signals = False)
            self.plot_2_lateral_position()
            #self.plot_2_lateral_position_wheel()
            #self.plot_3_warnings()
            #self.plot_4_lanes()
            self.plot_5_lateral_speed()
            self.plot_6_driver()
            self.plot_6_suppressors()
            #self.plot_6_Suppr_HIGH_STEERING_RATE()
            #self.plot_6_AccelLateral()
            #self.plot_7_TLC()
            #self.plot_8_View_Range()
            #self.plot_9_error_handler()
            #self.plot_2_lateral_position_at_front_axle_position()
        elif mode == "Homologation":
            self.plot_2_lane_homologation(show_internal_signals = True)
            self.plot_2_lane_homologation(show_internal_signals = False)
            self.plot_2_lane(customer_version=False)
            self.plot_2_lateral_position()
        elif mode == "details":
            self.plot_1_C0_Filter()   # understand how big the delay introduced by filtering

 

        if self.verbose:
            print "cPlotFLC20LDWS.PlotAll() - end"
     

   
    # ===========================================================================
    def plot_1_overview(self, PlotName = 'plot_1_overview'):
 
        if self.verbose:
            print "plot_1_overview()"

        
        if self.t_ME_LDW_LaneDeparture_Right is not None:
            # chose a local plot range for x-axis
            local_xlim = (self.t_ME_LDW_LaneDeparture_Right[0]-self.t_ref,self.t_ME_LDW_LaneDeparture_Right[-1]-self.t_ref)
        
            # avoid that legend hide interesting part of measurement
            if (self.t_ref-self.t_ME_LDW_LaneDeparture_Right[0])>0.7*(self.t_ME_LDW_LaneDeparture_Right[-1]-self.t_ME_LDW_LaneDeparture_Right[0]):
                local_xlim = (local_xlim[0],local_xlim[1]+0.3*(local_xlim[1]-local_xlim[0]))
        elif self.t_ME_LDW_LaneDeparture_Left is not None:
            # chose a local plot range for x-axis
            local_xlim = (self.t_ME_LDW_LaneDeparture_Left[0]-self.t_ref,self.t_ME_LDW_LaneDeparture_Left[-1]-self.t_ref)
        
            # avoid that legend hide interesting part of measurement
            if (self.t_ref-self.t_ME_LDW_LaneDeparture_Left[0])>0.7*(self.t_ME_LDW_LaneDeparture_Left[-1]-self.t_ME_LDW_LaneDeparture_Left[0]):
                local_xlim = (local_xlim[0],local_xlim[1]+0.3*(local_xlim[1]-local_xlim[0]))
        else:
            return
    
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=100)
        

        # --------------------------------------------------------
        # warnings imminent
        ax = fig.add_subplot(611)
    
        ax.plot(self.t_ME_LDW_LaneDeparture_Right-self.t_ref, self.ME_LDW_LaneDeparture_Right+2.0,'c', label='right w/o supp (+2)')
        ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight+2.0,   'r', label='right imminent (+2)')

        ax.plot(self.t_ME_LDW_LaneDeparture_Left-self.t_ref,  self.ME_LDW_LaneDeparture_Left,     'm', label='left w/o supp')
        ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,     self.LaneDepartImminentLeft,        'b', label='left imminent')
    
        # marker + text
        if self.t_LDW_Right_start is not None:
            ax.plot(self.t_LDW_Right_start-self.t_ref, 3.0,'md')
            ax.text(self.t_LDW_Right_start-self.t_ref, 3.05,"%3.2f s"%self.t_LDW_Right_start)
        if self.t_LDW_Left_start is not None:
            ax.plot(self.t_LDW_Left_start-self.t_ref, 1.0,'md')
            ax.text(self.t_LDW_Left_start-self.t_ref, 1.05,"%3.2f s"%self.t_LDW_Left_start)
   
        ax.set_ylim(-0.1, 4.1)
        ax.legend()
        ax.set_ylabel('LD warnings')
        ax.set_yticks(np.arange(0,5)) 
        ax.set_yticklabels(['Off','On','Off','On'])


        ax.grid()
        ax.set_xlim(local_xlim)
    
        
        # --------------------------------------------------------
        # tracking
        ax = fig.add_subplot(612)
   
        ax.plot(self.t_LDW_Right_Tracking-self.t_ref, self.LDW_Right_Tracking+2.0,'r',label='right (+2)')
        ax.plot(self.t_LDW_Left_Tracking-self.t_ref,  self.LDW_Left_Tracking,     'b',label='left')
      
        ax.set_ylim(-0.1, 4.1)
        ax.legend()
        ax.set_ylabel('Tracking')
        ax.set_yticks(np.arange(0,5)) 
        ax.set_yticklabels(['Off','On','Off','On'])

        ax.grid()
        ax.set_xlim(local_xlim)
        
        # -------------------------------------
        # lateral position
        ax = fig.add_subplot(613)
    
        # lines
        ax.plot(self.t_Right_C0-self.t_ref, self.Right_C0, 'r',label='right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C0,  'b',label='left')
    
        if self.Time_RightLinePosLateral is not None:
            ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral,'m', label='OxTS right')
        if self.Time_LeftLinePosLateral is not None:
            ax.plot(self.Time_LeftLinePosLateral-self.t_ref,  self.LeftLinePosLateral, 'c', label='OxTS left')

        # marker + text
        if self.LDW_Right_okay:
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,'md')
            ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,"%3.2f m"%self.Right_C0_at_t_LDW_Right)
            ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,'md')
            ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,"%3.2f m"%self.Right_C0_at_t_LDW_Right_stop)
        if self.LDW_Left_okay:
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,'md')
            ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,"%3.2f m"%self.Left_C0_at_t_LDW_Left)
            ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,'md')
            ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,"%3.2f m"%self.Left_C0_at_t_LDW_Left_stop)

        ax.set_ylabel('lateral \n position \n [m]')

        ax.legend()
        ax.set_ylim(-3.0, 3.0)
    
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # -------------------------------------
        # lateral speed
        ax = fig.add_subplot(614)
    
        # lines
        ax.plot(self.t_Right_C0-self.t_ref, self.lateral_speed_Right, 'r', label='right')
        ax.plot(self.t_Left_C0-self.t_ref,  self.lateral_speed_Left,  'b', label='left')
 
        if self.Time_RightLineVelLateral is not None:
            ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'m',label='OxTS right')
        if self.Time_LeftLineVelLateral is not None:
            ax.plot(self.Time_LeftLineVelLateral-self.t_ref,  self.LeftLineVelLateral, 'c',label='OxTS left')
           

        # marker + text
        if self.LDW_Right_okay:
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,'md')
            ax.text(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,"%3.2f m/s"%self.lateral_speed_Right_at_t_LDW_Right)
        if self.LDW_Left_okay:
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,'md')
            ax.text(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,"%3.2f m/s"%self.lateral_speed_Left_at_t_LDW_Left)
        ax.set_ylabel('lateral \n speed \n [m/s]')
        ax.legend()

        ax.set_xlim(local_xlim)
        ax.set_ylim(-2.1, 2.1)
        ax.grid()

        # -------------------------------------
        # road_curvature
        '''
        ax = fig.add_subplot(715)
        road_curvature_at_t_event = road_curvature[t_road_curvature>=t_event][0]
    
        # lines  
        ax.plot(t_road_curvature-t_ref, road_curvature,'r')
    
        # points
        ax.plot(t_event-t_ref, road_curvature_at_t_event,'md')
    
        # text
        if abs(road_curvature_at_t_event) < 1500.0:
            ax.text(t_event-t_ref, road_curvature_at_t_event,"%4.0f m"%road_curvature_at_t_event)
        else:
            ax.text(t_event-t_ref, 0.0,"%4.0f m"%road_curvature_at_t_event)
    
        ax.set_xlim(local_xlim)
        ax.set_ylim(-1500.0, 1500.0)
        ax.grid()
        ax.set_ylabel('curve radius [m]')
        ax.set_xlabel('time [s]')
        '''    
    
    
        # ---------------------------------------------
        t_BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]
        #BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr"]
        
        ax = fig.add_subplot(615)
        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_SYSTEM_DISABLED"] +8.0,'k', label='SYSTEM_DISABLED (+8)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_LOW_SPEED"]       +6.0,'b', label='LOW_SPEED (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_TURN_SIGNAL"]     +4.0,'r', label='TURN_SIGNAL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HAZARD_LIGHTS"]   +2.0,'g', label='HAZARD_LIGHTS (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_CONSTRUCTION_ZONE"],   'y', label='CONSTRUCTION_ZONE')
          
        ax.set_ylabel('Suppr. I')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On','Off','On'])

        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ---------------------------------------------
        ax = fig.add_subplot(616)
        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_DECEL"]    +6.0,'b', label='HIGH_DECEL (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_LATVEL"]   +4.0,'r', label='HIGH_LATVEL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_CURVATURE"]+2.0,'g', label='HIGH_CURVATURE (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'y', label='HIGH_STEERING_RATE')

        ax.set_ylabel('Suppr. II')
        ax.legend()
        ax.set_ylim(-0.1, 8.1)
        ax.set_yticks(np.arange(0,9)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On'])

        ax.set_xlim(local_xlim)
        ax.grid()
        
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
    
       
    # ===========================================================================
    def plot_1_ego_vehicle(self, PlotName = 'plot_1_ego_vehicle'):
    
        if self.verbose:
            print "plot_1_ego_vehicle()"

        fig = self.start_fig(PlotName, FigNr=200)
  
        local_xlim = self.xlim_closeup

  
        # ------------------------------------------------------
        t_v_ego, v_ego                   = kbtools_user.cDataAC100.get_v_ego(self.FLR20_sig) 
        t_SteerWhlAngle, SteerWhlAngle   = kbtools_user.cDataAC100.get_SteerWhlAngle(self.FLR20_sig)
        t_yawrate, yawrate               = kbtools_user.cDataAC100.get_yawrate(self.FLR20_sig)
        t_road_curvature, road_curvature = kbtools_user.cDataAC100.get_road_curvature(self.FLR20_sig)

        # ------------------------------------------------------
        v_ego_at_t_ref          = kbtools.GetPreviousSample(t_v_ego, v_ego,self.t_ref)   
        SteerWhlAngle_at_t_ref  = kbtools.GetPreviousSample(t_SteerWhlAngle,SteerWhlAngle,self.t_ref) 
        yawrate_at_t_ref        = kbtools.GetPreviousSample(t_yawrate,yawrate,self.t_ref) 
        road_curvature_at_t_ref = kbtools.GetPreviousSample(t_road_curvature,road_curvature,self.t_ref) 

        # ---------------------------------------------
        ax = fig.add_subplot(411)
        print "t_v_ego", t_v_ego
        if t_v_ego is not None:
            ax.plot(t_v_ego-self.t_ref, v_ego,'b',label='Ego velocity  (%5.1f km/h)'%(v_ego_at_t_ref))
       
            ax.plot(0.0,v_ego_at_t_ref,'dm')
            ax.text(0.0,v_ego_at_t_ref,"  %5.1f km/h "%(v_ego_at_t_ref))
      
        ax.set_ylabel('[km/h]')
        ax.legend()
        ax.set_ylim(0.0, 110.0)
        ax.set_xlim(local_xlim)
        ax.grid()

    
        # ---------------------------------------------
        ax = fig.add_subplot(412)
        if t_SteerWhlAngle is not None:
            ax.plot(t_SteerWhlAngle-self.t_ref, SteerWhlAngle,'b',label='SteerWhlAngle (%5.1f degree)'%(SteerWhlAngle_at_t_ref))
        
            ax.plot(0.0,SteerWhlAngle_at_t_ref,'dm')
            ax.text(0.0,SteerWhlAngle_at_t_ref,"  %5.1f degree "%(SteerWhlAngle_at_t_ref))
     
        ax.set_ylabel('[degree]')
        ax.legend()
        #ax.set_ylim(-100.1, 100.1)
        
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ---------------------------------------------
        ax = fig.add_subplot(413)
        if t_yawrate is not None:
            ax.plot(t_yawrate-self.t_ref, yawrate,'b',label='yawrate (%5.3f rad/s)'%(yawrate_at_t_ref))
        
            ax.plot(0.0,yawrate_at_t_ref,'dm')
            ax.text(0.0,yawrate_at_t_ref,"  %5.3f rad/s "%(yawrate_at_t_ref))

       
        ax.set_ylabel('[rad/s]')
        ax.legend()
        ax.set_ylim(-0.3, 0.3)
        
        ax.set_xlim(local_xlim)
        ax.grid()
        
        # ---------------------------------------------
        ax = fig.add_subplot(414)
        if t_road_curvature is not None:
            ax.plot(t_road_curvature-self.t_ref, road_curvature,'b',label='road_curvature (%5.0f m)'%(road_curvature_at_t_ref))
        
            ax.plot(0.0,road_curvature_at_t_ref,'dm')
            ax.text(0.0,road_curvature_at_t_ref,"  %5.0f m"%(road_curvature_at_t_ref))

       
        ax.set_ylabel('[rad/s]')
        ax.legend()
        ax.set_ylim(-1500.0, 1500.0)
        
        ax.set_xlim(local_xlim)
        ax.grid()
        
        
 
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
      
    # ===========================================================================
    def plot_7_CAN_Delay(self, PlotName = 'plot_7_CAN_Delay'): 

    
        if self.verbose:
            print "plot_7_CAN_Delay()"

        Time_CAN_Delay = self.FLR20_sig['FLC20_CAN']["Time_CAN_Delay"]
        CAN_Delay          = self.FLR20_sig['FLC20_CAN']["CAN_Delay"]               
  
            
            
        # ---------------------------------------------------------------------
        # VideoPackts:
        # First packet: Video_Data_General_A    - FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        # Last packet:  Video_Lane_Next_Left_B  - FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        t_head   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        cnt_head = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Video_Data_General_A"]

        t_tail   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        cnt_tail = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Next_Left_B"]

   
        if (Time_CAN_Delay is None):
            if self.verbose:
                print "Time_CAN_Delay is None"
            return
        if (t_head is None):
            if self.verbose:
                print "t_head is None"
            return
        if (t_tail is None):
            if self.verbose:
                print "t_tail is None"
            return
   
  
        local_xlim = self.xlim_closeup

        
        CAN_Delay_at_t_ref = kbtools.GetPreviousSample(Time_CAN_Delay, CAN_Delay,self.t_ref)   
        
        t_start = local_xlim[0]+self.t_ref
        t_stop  = local_xlim[1]+self.t_ref
        idx = np.argwhere(np.logical_and(t_start<=Time_CAN_Delay,Time_CAN_Delay<t_stop))
        tmp_Time_CAN_Delay = Time_CAN_Delay[idx]
        tmp_CAN_Delay = CAN_Delay[idx]
        
        t_max_CAN_Delay = tmp_Time_CAN_Delay[np.argmax(tmp_CAN_Delay)]
        max_CAN_Delay = np.max(tmp_CAN_Delay)
        
        t_min_CAN_Delay = tmp_Time_CAN_Delay[np.argmin(tmp_CAN_Delay)]
        min_CAN_Delay = np.min(tmp_CAN_Delay)
        
        mean_CAN_Delay = np.mean(tmp_CAN_Delay)
 
        # ================================================================= 
        fig = self.start_fig(PlotName, FigNr=200)
  
        # ---------------------------------------------
        ax = fig.add_subplot(311)
        ax.plot(Time_CAN_Delay-self.t_ref, CAN_Delay,'bx-',label='CAN_Delay  (%5.3f s) mean=%5.3f s, min/max= %5.3f s/%5.3f s'%(CAN_Delay_at_t_ref,mean_CAN_Delay,min_CAN_Delay,max_CAN_Delay))
       
        ax.plot(0.0,CAN_Delay_at_t_ref,'dm')
        ax.text(0.0,CAN_Delay_at_t_ref,"  %5.3f s "%(CAN_Delay_at_t_ref))
      
        ax.plot(t_max_CAN_Delay-self.t_ref,max_CAN_Delay,'dm')
        ax.text(t_max_CAN_Delay-self.t_ref,max_CAN_Delay,"  %5.3f s "%(max_CAN_Delay))
      
        ax.plot(t_min_CAN_Delay-self.t_ref,min_CAN_Delay,'dm')
        ax.text(t_min_CAN_Delay-self.t_ref,min_CAN_Delay,"  %5.3f s "%(min_CAN_Delay))
      
        ax.hlines(mean_CAN_Delay,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="mean_CAN_Delay(%5.3f s)"%mean_CAN_Delay)
      
      
        ax.set_ylabel('[s]')
        ax.legend()
        ax.set_ylim(0.0, 0.4)
        ax.set_xlim(local_xlim)
        ax.grid()
 
          
        if self.verbose:
            print "plot_7_CAN_Delay - VideoPackts: "        

        
       
        videopacket = kbtools_user.CFLC20FusionMsgArray(t_head, cnt_head, t_tail, cnt_tail)
        #t_videopacket = videopacket.t_head
        
        t_SamplingIntervals, SamplingIntervals = videopacket.getSamplingIntervals()
        
        
        SamplingInterval_at_t_ref = kbtools.GetPreviousSample(t_SamplingIntervals, SamplingIntervals,self.t_ref)   
        
        t_start = local_xlim[0]+self.t_ref
        t_stop  = local_xlim[1]+self.t_ref
        idx = np.argwhere(np.logical_and(t_start<=t_SamplingIntervals,t_SamplingIntervals<t_stop))
        tmp_t_SamplingIntervals = t_SamplingIntervals[idx]
        tmp_SamplingIntervals = SamplingIntervals[idx]
        
        t_max_SamplingInterval = tmp_t_SamplingIntervals[np.argmax(tmp_SamplingIntervals)]
        max_SamplingInterval = np.max(tmp_SamplingIntervals)
        
        t_min_SamplingInterval = tmp_t_SamplingIntervals[np.argmin(tmp_SamplingIntervals)]
        min_SamplingInterval = np.min(tmp_SamplingIntervals)
        
        mean_SamplingInterval = np.mean(tmp_SamplingIntervals)

         
        ax = fig.add_subplot(312)
        ax.plot(t_SamplingIntervals-self.t_ref, SamplingIntervals,'bx-',label='SamplingInterval  (%5.3f s) mean=%5.3f s, min/max= %5.3f s/%5.3f s'%(SamplingInterval_at_t_ref,mean_SamplingInterval,min_SamplingInterval,max_SamplingInterval))
       
        ax.plot(0.0,SamplingInterval_at_t_ref,'dm')
        ax.text(0.0,SamplingInterval_at_t_ref,"  %5.3f s "%(SamplingInterval_at_t_ref))
      
        ax.plot(t_max_SamplingInterval-self.t_ref,max_SamplingInterval,'dm')
        ax.text(t_max_SamplingInterval-self.t_ref,max_SamplingInterval,"  %5.3f s "%(max_SamplingInterval))
      
        ax.plot(t_min_SamplingInterval-self.t_ref,min_SamplingInterval,'dm')
        ax.text(t_min_SamplingInterval-self.t_ref,min_SamplingInterval,"  %5.3f s "%(min_SamplingInterval))
      
        ax.hlines(mean_SamplingInterval,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="mean_SamplingInterval(%5.3f s)"%mean_SamplingInterval)
      
      
        ax.set_ylabel('[s]')
        ax.legend()
        ax.set_ylim(0.0, 0.15)
        ax.set_xlim(local_xlim)
        ax.grid()

        # ----------------------------------------------------------------------------        
        t_BxInfo, Bendix_Info3_delay = videopacket.calc_delay(self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"],self.FLR20_sig["FLC20_CAN"]["Frame_ID"], self.FLR20_sig["FLC20_CAN"]["Time_LNVU_Frame_Id_LSB"],self.FLR20_sig["FLC20_CAN"]["LNVU_Frame_Id_LSB"]) 
        ax = fig.add_subplot(313)
        if t_BxInfo is not None:
            ax.plot(t_BxInfo-self.t_ref, Bendix_Info3_delay,'bx-',label='Bendix_Info3_delay')
        
        '''
        COMPARE_LNVU_isWarningLeft  = videopacket.sync(self.FLR20_sig["FLC20_CAN"]["Time_LNVU_isWarningLeft"] ,self.FLR20_sig["FLC20_CAN"]["LNVU_isWarningLeft"])
        
        ax.plot(videopacket.t_head-self.t_ref, COMPARE_LNVU_isWarningLeft,'rx-',label='videopacket.t_head')
        ax.plot(t_BxInfo-self.t_ref, COMPARE_LNVU_isWarningLeft,'bx-',label='Bendix_Info3_delay')
        
        '''   
        
       
        '''
        ax.plot(0.0,SamplingInterval_at_t_ref,'dm')
        ax.text(0.0,SamplingInterval_at_t_ref,"  %5.3f s "%(SamplingInterval_at_t_ref))
      
        ax.plot(t_max_SamplingInterval-self.t_ref,max_SamplingInterval,'dm')
        ax.text(t_max_SamplingInterval-self.t_ref,max_SamplingInterval,"  %5.3f s "%(max_SamplingInterval))
      
        ax.plot(t_min_SamplingInterval-self.t_ref,min_SamplingInterval,'dm')
        ax.text(t_min_SamplingInterval-self.t_ref,min_SamplingInterval,"  %5.3f s "%(min_SamplingInterval))
      
        ax.hlines(mean_SamplingInterval,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="mean_SamplingInterval(%5.3f s)"%mean_SamplingInterval)
        '''
      
        ax.set_ylabel('[lags]')
        ax.legend()
        ax.set_ylim(0.0, 3.0)
        ax.set_xlim(local_xlim)
        ax.grid()

 
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

        #======================================================================
        fig = self.start_fig(PlotName+'_1', FigNr=201)

        
        Left_C0  = videopacket.sync(self.FLR20_sig['FLC20_CAN']["Time_C0_Left"] ,self.FLR20_sig['FLC20_CAN']["C0_Left"])
        Right_C0  = videopacket.sync(self.FLR20_sig['FLC20_CAN']["Time_C0_Right"] ,self.FLR20_sig['FLC20_CAN']["C0_Right"])
        t_videopacket = videopacket.t_head
        
        t_delay  = videopacket.sync(self.FLR20_sig['FLC20_CAN']["Time_CAN_Delay"] ,self.FLR20_sig['FLC20_CAN']["CAN_Delay"])
       
                     

           
        # ----------------------------------------------------------------------------        
        ax = fig.add_subplot(211)
        if Left_C0 is not None:
            ax.plot(t_videopacket-self.t_ref, Left_C0,'bx-',label='Left_C0')
            ax.plot(t_videopacket-t_delay-self.t_ref, Left_C0,'rx-',label='Left_C0 corr.')
        
      
        ax.set_ylabel('[m]')
        ax.legend()
        #ax.set_ylim(0.0, 3.0)
        ax.set_xlim(local_xlim)
        ax.grid()
        
        # ----------------------------------------------------------------------------        
        ax = fig.add_subplot(212)
        if Right_C0 is not None:
            ax.plot(t_videopacket-self.t_ref, Right_C0,'bx-',label='Right_C0')
            ax.plot(t_videopacket-t_delay-self.t_ref, Right_C0,'rx-',label='Right_C0 corr.')
        
      
        ax.set_ylabel('[m]')
        ax.legend()
        #ax.set_ylim(0.0, 3.0)
        ax.set_xlim(local_xlim)
        ax.grid()

        ax.set_xlabel('time [s]')
        
        # -------------------------------------
        self.show_and_save_figure()
    
    # ===========================================================================
    def plot_6_driver(self, PlotName = 'plot_6_driver'):
    
        if self.verbose:
            print "plot_6_driver()"

        fig = self.start_fig(PlotName, FigNr=200)
  
        local_xlim = self.xlim_closeup

  
        t_DirIndL_b = self.FLR20_sig["J1939"]["Time_DirIndL_b"]
        DirIndL_b = self.FLR20_sig["J1939"]["DirIndL_b"]
        t_DirIndR_b = self.FLR20_sig["J1939"]["Time_DirIndR_b"]
        DirIndR_b = self.FLR20_sig["J1939"]["DirIndR_b"]
 
        #t_TurnSigSw = self.FLR20_sig["J1939"]["Time_TurnSigSw"]
        #TurnSigSw = self.FLR20_sig["J1939"]["TurnSigSw"]
 
        t_HazardLightSw = self.FLR20_sig["J1939"]["Time_HazardLightSw"]
        HazardLightSw = self.FLR20_sig["J1939"]["HazardLightSw"]
    
        ax = fig.add_subplot(411)
        if t_DirIndL_b is not None:
            ax.plot(t_DirIndL_b-self.t_ref,     DirIndL_b,    'rx-',label='DirIndL_b')
        if t_DirIndR_b is not None:
            ax.plot(t_DirIndR_b-self.t_ref,     DirIndR_b,    'bx-',label='DirIndR_b')
        if t_HazardLightSw is not None:
            ax.plot(t_HazardLightSw-self.t_ref, HazardLightSw,'mx-',label='HazardLightSw')
        
      
        ax.set_ylabel('[Flags]')
        ax.legend()
        ax.set_ylim(-0.1, 1.1)
        ax.set_yticks(np.arange(0,2)) 
        ax.set_yticklabels(['Off','On'])

        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
    
    
        # ---------------------------------------------
        t_SteerWhlAngle, SteerWhlAngle   = kbtools_user.cDataAC100.get_SteerWhlAngle(self.FLR20_sig)
        
    
        ax = fig.add_subplot(412)
        if t_SteerWhlAngle is not None:
            ax.plot(t_SteerWhlAngle-self.t_ref, SteerWhlAngle,'b', label= 'SteerWhlAngle')
       
        ax.set_ylabel('[degree]')
        ax.legend()
        #ax.set_ylim(-1.1, 1.1)
        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ---------------------------------------------
        t_BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]
        BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr"]
        # ax.plot(t_BX_LDW_Suppr-t_ref, BX_LDW_Suppr,'bx-')
       
        ax = fig.add_subplot(413)
        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_SYSTEM_DISABLED"] +8.0,'k',label='SYSTEM_DISABLED (+8)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_LOW_SPEED"]       +6.0,'b',label='LOW_SPEED (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_TURN_SIGNAL"]     +4.0,'r',label='TURN_SIGNAL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HAZARD_LIGHTS"]   +2.0,'g',label='HAZARD_LIGHTS (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_CONSTRUCTION_ZONE"],   'y',label='CONSTRUCTION_ZONE')
          
        ax.set_ylabel('BX_LDW_Suppr I')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ---------------------------------------------
        ax = fig.add_subplot(414)
  

        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_DECEL"]    +6.0,'b',label='HIGH_DECEL (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_LATVEL"]   +4.0,'r',label='HIGH_LATVEL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_CURVATURE"]+2.0,'g',label='HIGH_CURVATURE (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'y',label='HIGH_STEERING_RATE')
            
        ax.set_ylabel('BX_LDW_Suppr II')
        ax.legend()
        ax.set_ylim(-0.1, 8.1)
        ax.set_xlim(local_xlim)
        ax.grid()
 
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

    # ===========================================================================
    def plot_6_suppressors(self, PlotName = 'plot_6_suppressors'):
    
        if self.verbose:
            print "plot_6_suppressors()"

        fig = self.start_fig(PlotName, FigNr=200)
  
        local_xlim = self.xlim_closeup
   
        ax = fig.add_subplot(311)
        if self.t_WARN_isWarningRight is not None:
            ax.plot(self.t_WARN_isWarningRight-self.t_ref,       self.WARN_isWarningRight      +8.0,'r', label='LD w/o supp. right')
        if self.t_LaneDepartImminentRight is not None:
            ax.plot(self.t_LaneDepartImminentRight-self.t_ref,   self.LaneDepartImminentRight  +6.0,'m', label='LD Imminent right')
        if self.t_WARN_isWarningLeft is not None:
            ax.plot(self.t_WARN_isWarningLeft-self.t_ref,        self.WARN_isWarningLeft       +4.0,'b', label='LD w/o supp. left')
        if self.t_LaneDepartImminentLeft is not None:
            ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   +2.0,'c', label='LD Imminent left')
        try:
            ax.plot(self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr"]>0,'k',label='any suppr.')
        except:
            pass         
        
        ax.set_ylim(-0.1, 7.1)
        ax.legend()
        #ax.set_ylabel('flags')
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','Suppr. - On','Off','LD Imminent - On (left)','Off','LD w/o supp. - On (left)','Off','LD Imminent - On (right)','Off','LD w/o supp. - On (right)'])
        ax.set_xlim(local_xlim)
        ax.grid()
    
    
        # ---------------------------------------------
        try:
            t_BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]
            BX_LDW_Suppr = self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr"]
            # ax.plot(t_BX_LDW_Suppr-t_ref, BX_LDW_Suppr,'bx-')
        except:
            t_BX_LDW_Suppr = None    
            BX_LDW_Suppr = None
            
        ax = fig.add_subplot(312)
        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_SYSTEM_DISABLED"] +8.0,'k',label='SYSTEM_DISABLED (+8)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_LOW_SPEED"]       +6.0,'b',label='LOW_SPEED (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_TURN_SIGNAL"]     +4.0,'r',label='TURN_SIGNAL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HAZARD_LIGHTS"]   +2.0,'g',label='HAZARD_LIGHTS (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_CONSTRUCTION_ZONE"],   'y',label='CONSTRUCTION_ZONE')
          
        ax.set_ylabel('BX_LDW_Suppr I')
        ax.legend()
        ax.set_ylim(-0.1, 10.1)
        ax.set_xlim(local_xlim)
        ax.grid()
    
        # ---------------------------------------------
        ax = fig.add_subplot(313)
  

        if t_BX_LDW_Suppr is not None:
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_DECEL"]    +6.0,'b',label='HIGH_DECEL (+6)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_LATVEL"]   +4.0,'r',label='HIGH_LATVEL (+4)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_CURVATURE"]+2.0,'g',label='HIGH_CURVATURE (+2)')
            ax.plot(t_BX_LDW_Suppr-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'y',label='HIGH_STEERING_RATE')
            
        ax.set_ylabel('BX_LDW_Suppr II')
        ax.legend()
        ax.set_ylim(-0.1, 8.1)
        ax.set_xlim(local_xlim)
        ax.grid()
 
        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

    # ===========================================================================
    def plot_6_Suppr_HIGH_STEERING_RATE(self, PlotName = 'plot_6_Suppr_HIGH_STEERING_RATE'):
    
        if self.verbose:
            print "plot_6_Suppr_HIGH_STEERING_RATE()"
    
        self.xlim_to_use(self.xlim_closeup)    
        print "self._xlim_to_use", self._xlim_to_use
            
        # ---------------------------------------------------
        t_SteerWhlAngle = self.FLR20_sig["J1939"]["Time_SteerWhlAngle"]
        SteerWhlAngle   = self.FLR20_sig["J1939"]["SteerWhlAngle"]
              
        T_detrend = 1.0
        LPF_SteerWhlAngle = kbtools.pt1_filter(t_SteerWhlAngle, SteerWhlAngle,T_detrend)
        
        
        HPF_SteerWhlAngle = SteerWhlAngle- LPF_SteerWhlAngle

        Gradient_SteerWhlAngle = kbtools.ugdiff(t_SteerWhlAngle, SteerWhlAngle, verfahren=1)  # Backwarddifferenz 
        
        Delta_threshold = 20.0
        Gradient_threshold = 40.0
        
        Delta_flag    = np.fabs(HPF_SteerWhlAngle)>(Delta_threshold*np.pi/180.0)
        Gradient_flag = np.fabs(Gradient_SteerWhlAngle)>(Gradient_threshold*np.pi/180.0)
        
        Combined_flag = np.logical_and(Delta_flag, Gradient_flag)
        
        T_monostable_multivibrator = 3.0
        Supp_flag = kbtools.monostable_multivibrator(t_SteerWhlAngle,Combined_flag,T_monostable_multivibrator)
            
            
        # --------------------------------------------------    
        fig = self.start_fig(PlotName, FigNr=200)
  
        local_xlim = self.xlim_closeup
    
        ax = fig.add_subplot(511)
        if self.t_WARN_isWarningRight is not None:
            ax.plot(self.t_WARN_isWarningRight-self.t_ref,   self.WARN_isWarningRight      +8.0,'r', label='LD w/o supp. right')
        ax.plot(self.t_LaneDepartImminentRight-self.t_ref,   self.LaneDepartImminentRight  +6.0,'m', label='LD Imminent right')
        if self.t_WARN_isWarningLeft is not None:
            ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       +4.0,'b', label='LD w/o supp. left')
        ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   +2.0,'c', label='LD Imminent left')
        try:
            ax.plot(self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'k',label='HIGH_STEERING_RATE')
        except:
            pass
        
        ax.set_ylim(-0.1, 9.1)
        ax.legend()
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','Suppr. - On','Off','LD Imminent - On (left)','Off','LD w/o supp. - On (left)','Off','LD Imminent - On (right)','Off','LD w/o supp. - On (right)'])
        ax.set_xlim(local_xlim)
        ax.grid()

        # ---------------------------------------------
        # Steering_Wheel_Angle_Input
        ax = fig.add_subplot(512)
        ax.plot(t_SteerWhlAngle-self.t_ref, SteerWhlAngle*180.0/np.pi,'r',label='J1939_SteerWhlAngle' )
        ax.plot(t_SteerWhlAngle-self.t_ref, HPF_SteerWhlAngle*180.0/np.pi,'b',label='Delta' )
        
        ax.hlines(Delta_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label="Delta_threshold(%3.0f)"%Delta_threshold)
        ax.hlines(-Delta_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label=None)
     
        ax.set_ylabel('[degree]')
        ax.legend()
        ax.set_ylim(-110.0,110.0)
        ax.set_xlim(local_xlim)
        ax.grid()
        
         
        # ------------------------------------------------------
        # angle rate
        ax = fig.add_subplot(513)
        ax.plot(t_SteerWhlAngle-self.t_ref, Gradient_SteerWhlAngle*180.0/np.pi,'b',label='gradient' )
        ax.hlines(Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label="Gradient_threshold (%3.0f)"%Gradient_threshold)
        ax.hlines(-Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label=None)
              
        ax.set_ylabel('[degree/s]')
        ax.legend()
        ax.set_ylim(-250.0,250.0)
        ax.set_xlim(local_xlim)
        ax.grid()

              

        # ------------------------------------------------------
        # DEBUG_HighSteerAngleRate
        ax = fig.add_subplot(514)
        
              
        ax.plot(t_SteerWhlAngle-self.t_ref, Delta_flag    +6.0,'b', label='Delta_flag (+4)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Gradient_flag +4.0,'r', label='Gradient_flag (+2)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Combined_flag +2.0,'g', label='Combined_flag (+2)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Supp_flag,'k',          label='Supp_flag' )
        try:
            ax.plot(self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'m',label='HIGH_STEERING_RATE')
        except:
            pass        
            
        ax.legend()
        ax.set_ylim(-0.1, 7.1 )

        ax.set_yticks(np.arange(0,9)) 
        ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On'])


        ax.set_xlim(local_xlim)
        ax.grid()
        
        # ------------------------------------------------------
        # DEBUG_HighSteerAngleRate
        t_yawrate = self.FLR20_sig['J1939']['Time_YawRate']
        yawrate   = self.FLR20_sig['J1939']["YawRate"] 

        t_v_ego = self.FLR20_sig['J1939']["Time_MeanSpdFA"]
        v_ego   = self.FLR20_sig['J1939']["MeanSpdFA"]

        try:
            t_ay = t_yawrate
            v_ego2    = kbtools.resample(t_v_ego, v_ego, t_ay, method='zoh')
            yawrate2  = kbtools.resample(t_yawrate, yawrate, t_ay, method='zoh')
            ay = (v_ego2/3.6) * yawrate2  # Unit 'm/s^2'
        except:
            t_ay = None
            ay = None


        ax = fig.add_subplot(515)
        if self.FLR20_sig["OxTS"]["Time_AccelLateral"] is not None:
            ax.plot(self.FLR20_sig["OxTS"]["Time_AccelLateral"]-self.t_ref, self.FLR20_sig["OxTS"]["AccelLateral"],'b',label='OxTS' )
        if t_ay is not None:
            ax.plot(t_ay-self.t_ref, -ay,'r',label='-v*yaw rate' )
        ax.plot(self.FLR20_sig['J1939']['Time_LatAccel']-self.t_ref, -self.FLR20_sig['J1939']['LatAccel'],'k',label='-VDC2 ay' )
        #ax.hlines(Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label="Gradient_threshold (%3.0f)"%Gradient_threshold)
        #ax.hlines(-Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label=None)
              
              
        ax.set_ylabel('[m/s$^2$]')
        ax.legend()
        #ax.set_ylim(-250.0,250.0)
        ax.set_xlim(local_xlim)
        ax.grid()

        

            
        ax.set_xlabel('time [s]')
  
        # -------------------------------------
        self.show_and_save_figure()
    # ===========================================================================
    def plot_6_AccelLateral(self, PlotName = 'plot_6_AccelLateral'):
    
        if self.verbose:
            print "plot_6_AccelLateral()"

        self.xlim_to_use(self.xlim_closeup)    
            
        # ---------------------------------------------------
        t_SteerWhlAngle = self.FLR20_sig["J1939"]["Time_SteerWhlAngle"]
        SteerWhlAngle   = self.FLR20_sig["J1939"]["SteerWhlAngle"]*180.0/np.pi

        Gradient_SteerWhlAngle = kbtools.ugdiff(t_SteerWhlAngle, SteerWhlAngle, verfahren=1)  # Backwarddifferenz 

        # ay from yaw rate
        t_yawrate = self.FLR20_sig['J1939']['Time_YawRate']
        yawrate   = self.FLR20_sig['J1939']["YawRate"] 

        t_v_ego = self.FLR20_sig['J1939']["Time_MeanSpdFA"]
        v_ego   = self.FLR20_sig['J1939']["MeanSpdFA"]
        
        try:
            t_ay = t_yawrate
            v_ego2    = kbtools.resample(t_v_ego, v_ego, t_ay, method='zoh')
            yawrate2  = kbtools.resample(t_yawrate, yawrate, t_ay, method='zoh')
            ay = (v_ego2/3.6) * yawrate2  # Unit 'm/s^2'
        except:
            t_ay = None
            ay = None
        
        # ---------------------------------------------------
        t_LDW_start = None
        Time_LineVelLateral = None
        LineVelLateral = None
        if self.t_LDW_Left_start is not None:
            t_LDW_start = self.t_LDW_Left_start 
            Time_LineVelLateral = self.Time_LeftLineVelLateral
            LineVelLateral = self.LeftLineVelLateral_smoothed
            
        elif self.t_LDW_Right_start is not None:
            t_LDW_start = self.t_LDW_Right_start
            Time_LineVelLateral = self.Time_RightLineVelLateral
            LineVelLateral = self.RightLineVelLateral_smoothed
            
        OxTS_host_AccelLateral_smoothed_at_t_LDW_start = kbtools.GetPreviousSample(self.Time_OxTS_host_AccelLateral,self.OxTS_host_AccelLateral_smoothed,t_LDW_start)
        SteerWhlAngle_at_t_LDW_start                   = kbtools.GetPreviousSample(t_SteerWhlAngle,SteerWhlAngle,t_LDW_start)
        Gradient_SteerWhlAngle_at_t_LDW_start          = kbtools.GetPreviousSample(t_SteerWhlAngle,Gradient_SteerWhlAngle,t_LDW_start)
        LineVelLateral_at_t_LDW_start                  = kbtools.GetPreviousSample(Time_LineVelLateral,LineVelLateral,t_LDW_start)
        
         

    
    
        # --------------------------------------------------    
        fig = self.start_fig(PlotName, FigNr=200)
  
        local_xlim = self.xlim_closeup
    
        ax = fig.add_subplot(511)
        if self.t_WARN_isWarningRight is not None:
            ax.plot(self.t_WARN_isWarningRight-self.t_ref,   self.WARN_isWarningRight      +8.0,'r', label='LD w/o supp. right')
        ax.plot(self.t_LaneDepartImminentRight-self.t_ref,   self.LaneDepartImminentRight  +6.0,'m', label='LD Imminent right')
        if self.t_WARN_isWarningLeft is not None:
            ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       +4.0,'b', label='LD w/o supp. left')
        ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   +2.0,'c', label='LD Imminent left')
        try:
            ax.plot(self.FLR20_sig["FLC20_CAN"]["Time_BX_LDW_Suppr"]-self.t_ref, self.FLR20_sig["FLC20_CAN"]["BX_LDW_Suppr_HIGH_STEERING_RATE"],'k',label='HIGH_STEERING_RATE')
        except:
            pass 
            
        
        ax.set_ylim(-0.1, 9.1)
        ax.legend()
        ax.set_yticks(np.arange(0,11)) 
        ax.set_yticklabels(['Off','Suppr. - On','Off','LD Imminent - On (left)','Off','LD w/o supp. - On (left)','Off','LD Imminent - On (right)','Off','LD w/o supp. - On (right)'])
        ax.set_xlim(local_xlim)
        ax.grid()

        # ---------------------------------------------
        # Steering_Wheel_Angle_Input
        ax = fig.add_subplot(512)
        ax.plot(t_SteerWhlAngle-self.t_ref, SteerWhlAngle,'r',label='J1939_SteerWhlAngle (%5.1f)'%(SteerWhlAngle_at_t_LDW_start,) )
        if (t_LDW_start is not None) and (not np.isnan(SteerWhlAngle_at_t_LDW_start)):    
            ax.plot(t_LDW_start-self.t_ref, SteerWhlAngle_at_t_LDW_start,'ms')
            ax.text(t_LDW_start-self.t_ref, SteerWhlAngle_at_t_LDW_start,"  %5.1f degree/s"%(SteerWhlAngle_at_t_LDW_start,))
       
        ax.set_ylabel('[degree]')
        ax.legend()
        ax.set_ylim(-110.0,110.0)
        ax.set_xlim(local_xlim)
        ax.grid()
       
        # ------------------------------------------------------
        # angular rate
        ax = fig.add_subplot(513)
        ax.plot(t_SteerWhlAngle-self.t_ref, Gradient_SteerWhlAngle,'b',label='gradient J1939SteerWhlAngle (%5.1f)'%(Gradient_SteerWhlAngle_at_t_LDW_start,) )
        if (t_LDW_start is not None) and (not np.isnan(Gradient_SteerWhlAngle_at_t_LDW_start)):
            ax.plot(t_LDW_start-self.t_ref, Gradient_SteerWhlAngle_at_t_LDW_start,'ms')
            ax.text(t_LDW_start-self.t_ref, Gradient_SteerWhlAngle_at_t_LDW_start,"  %5.1f degree/s"%(Gradient_SteerWhlAngle_at_t_LDW_start,))
              
        ax.set_ylabel('[degree/s]')
        ax.legend()
        ax.set_ylim(-250.0,250.0)
        ax.set_xlim(local_xlim)
        ax.grid()

        
        
        # ------------------------------------------------------
        # lateral velocity to the line
        ax = fig.add_subplot(514)
        if Time_LineVelLateral is not None:
            ax.plot(Time_LineVelLateral-self.t_ref, LineVelLateral,'b',label='OxTS LineVelLateral (%5.2f)'%(LineVelLateral_at_t_LDW_start,) )
            if t_LDW_start is not None:
                ax.plot(t_LDW_start-self.t_ref, LineVelLateral_at_t_LDW_start,'ms')
                ax.text(t_LDW_start-self.t_ref, LineVelLateral_at_t_LDW_start,"  %5.2f m/s"%(LineVelLateral_at_t_LDW_start,))
              
        ax.set_ylabel('[m/s]')
        ax.legend()
        ax.set_ylim(-2.1,2.1)
        ax.set_xlim(local_xlim)
        ax.grid()
        
        # ------------------------------------------------------
        # lateral acceleration


        ax = fig.add_subplot(515)
        #ax.plot(self.FLR20_sig["OxTS"]["Time_AccelLateral"]-self.t_ref, self.FLR20_sig["OxTS"]["AccelLateral"],'b',label='OxTS' )
        #ax.plot(self.FLR20_sig["OxTS"]["Time_AccelLateral"]-self.t_ref, OxTS_AccelLateral_smoothed,'r',label='OxTS' )
        if self.Time_OxTS_host_AccelLateral is not None:
            ax.plot(self.Time_OxTS_host_AccelLateral-self.t_ref, self.OxTS_host_AccelLateral,'b',label='OxTS' )
            ax.plot(self.Time_OxTS_host_AccelLateral-self.t_ref, self.OxTS_host_AccelLateral_smoothed,'r',label='OxTS smoothed (%5.1f)'%(OxTS_host_AccelLateral_smoothed_at_t_LDW_start,) )
            if t_LDW_start is not None:
                ax.plot(t_LDW_start-self.t_ref, OxTS_host_AccelLateral_smoothed_at_t_LDW_start,'ms')
                ax.text(t_LDW_start-self.t_ref, OxTS_host_AccelLateral_smoothed_at_t_LDW_start,"  %5.1f m/s$^2$"%(OxTS_host_AccelLateral_smoothed_at_t_LDW_start,))
        if t_ay is not None:
            ax.plot(t_ay-self.t_ref, -ay,'c',label='-v*yaw rate' )
        ax.plot(self.FLR20_sig['J1939']['Time_LatAccel']-self.t_ref, -self.FLR20_sig['J1939']['LatAccel'],'m',label='-VDC2 ay' )

             
        ax.set_ylabel('[m/s$^2$]')
        ax.legend()
        #ax.set_ylim(-250.0,250.0)
        ax.set_xlim(local_xlim)
        ax.grid()
            
        ax.set_xlabel('time [s]')
  
        # -------------------------------------
        self.show_and_save_figure()
    # ===========================================================================
    def plot_7_TLC(self,PlotName = 'plot_7_TLC'):

        if self.verbose:
            print "plot_7_TLC()"
        
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=700)
             
        local_xlim = self.xlim_closeup
     
        t_TLC_Left  = self.FLR20_sig['FLC20_CAN']["Time_TLC_Left"]
        TLC_Left    = self.FLR20_sig['FLC20_CAN']["TLC_Left"]  
        t_TLC_Right  = self.FLR20_sig['FLC20_CAN']["Time_TLC_Right"]
        TLC_Right    = self.FLR20_sig['FLC20_CAN']["TLC_Right"]  
  
        t_BX_TLC_Left  = self.FLR20_sig['FLC20_CAN']["Time_BX_TLC_Left"]
        BX_TLC_Left    = self.FLR20_sig['FLC20_CAN']["BX_TLC_Left"]  
        t_BX_TLC_Right  = self.FLR20_sig['FLC20_CAN']["Time_BX_TLC_Right"]
        BX_TLC_Right    = self.FLR20_sig['FLC20_CAN']["BX_TLC_Right"]  
   
   
     
        ax = fig.add_subplot(211)
        if t_TLC_Right is not None:
            ax.plot(t_TLC_Right-self.t_ref,    TLC_Right,   'rx-',  label= 'TLC_Right')
        if t_TLC_Left is not None:
            ax.plot(t_TLC_Left-self.t_ref,     TLC_Left,    'bx-',  label= 'TLC_Left')
        if t_BX_TLC_Right is not None:
            ax.plot(t_BX_TLC_Right-self.t_ref, BX_TLC_Right,'mx-',  label= 'BX_TLC_Right')
        if t_BX_TLC_Left is not None:
            ax.plot(t_BX_TLC_Left-self.t_ref,  BX_TLC_Left, 'kx-',  label= 'BX_TLC_Left')

        TLC_threshold = 0.3         
        if local_xlim is not None:
            ax.hlines(TLC_threshold,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label='TLC_threshold')

        
        
        ax.set_ylabel('Time-to-line-crossing [s]')
        ax.legend()
        ax.set_ylim(-0.1, 2.1)
        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        #---------------------------------------------------    
        t_Line_Width_Left   = self.FLR20_sig['FLC20_CAN']["Time_Line_Width_Left"]
        Line_Width_Left     = self.FLR20_sig['FLC20_CAN']["Line_Width_Left"]  
        t_Line_Width_Right  = self.FLR20_sig['FLC20_CAN']["Time_Line_Width_Right"]
        Line_Width_Right    = self.FLR20_sig['FLC20_CAN']["Line_Width_Right"]  

        ax = fig.add_subplot(212)
        if t_Line_Width_Right is not None:
            ax.plot(t_Line_Width_Right-self.t_ref, Line_Width_Right,'rx-',label='Line_Width_Right')
        if t_Line_Width_Left is not None:
            ax.plot(t_Line_Width_Left-self.t_ref,  Line_Width_Left, 'bx-',label='Line_Width_Left')
        
        ax.set_ylabel('[m]')
        ax.legend()
        #ax.set_ylim(-0.1, 1.1)
        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()
        
    # ===========================================================================
    def plot_8_View_Range(self,PlotName = 'plot_8_View_Range'):

        if self.verbose:
            print "plot_8_View_Range()"
        
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=700)
             
        local_xlim = self.xlim_closeup
     
       
        t_View_Range_Right  = self.FLR20_sig['FLC20_CAN']["Time_View_Range_Right"]
        View_Range_Right    = self.FLR20_sig['FLC20_CAN']["View_Range_Right"]  
     
        t_View_Range_Left  = self.FLR20_sig['FLC20_CAN']["Time_View_Range_Left"]
        View_Range_Left    = self.FLR20_sig['FLC20_CAN']["View_Range_Left"]  
     
        ax = fig.add_subplot(211)
        if t_View_Range_Right is not None:
            ax.plot(t_View_Range_Right-self.t_ref,    View_Range_Right,   'rx-',  label= 'Right')
        if t_View_Range_Left is not None:
            ax.plot(t_View_Range_Left-self.t_ref,     View_Range_Left,    'bx-',  label= 'Left')

       
        
        ax.set_ylabel('View_Range [s]')
        ax.legend()
        #ax.set_ylim(-0.1, 2.1)
        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        #---------------------------------------------------    
        t_Line_Width_Left   = self.FLR20_sig['FLC20_CAN']["Time_Line_Width_Left"]
        Line_Width_Left     = self.FLR20_sig['FLC20_CAN']["Line_Width_Left"]  
        t_Line_Width_Right  = self.FLR20_sig['FLC20_CAN']["Time_Line_Width_Right"]
        Line_Width_Right    = self.FLR20_sig['FLC20_CAN']["Line_Width_Right"]  

        ax = fig.add_subplot(212)
        if t_Line_Width_Right is not None:
            ax.plot(t_Line_Width_Right-self.t_ref, Line_Width_Right,'rx-',label='Line_Width_Right')
        if t_Line_Width_Left is not None:
            ax.plot(t_Line_Width_Left-self.t_ref,  Line_Width_Left, 'bx-',label='Line_Width_Left')
        
        ax.set_ylabel('[m]')
        ax.legend()
        #ax.set_ylim(-0.1, 1.1)
        #ax.set_xlim((t_event-t_ref-1.0,t_event-t_ref+1.0))
        ax.set_xlim(local_xlim)
        ax.grid()

        ax.set_xlabel('time [s]')
    
        # -------------------------------------
        self.show_and_save_figure()

    # ===========================================================================
    def plot_2_lateral_position_at_front_axle_position(self):
        if self.verbose:
            print "plot_2_lateral_position_at_front_axle_position()"

        PlotName = 'plot_2_lateral_position_at_front_axle_position'
    
        
        # --------------------------------------------------------
        fig = self.start_fig(PlotName, FigNr=701)

        # ===============================================  
        # right wheel
        if self.LDW_Right_okay:
        
            ax = fig.add_subplot(311)
    
            dy = -self.dx_camera_to_front_axle*np.tan(self.Right_C1)
            
    
            ax.set_title('Right side')

            local_xlim = self.xlim_closeup
 
            # lines
            ax.plot(self.t_Right_C0-self.t_ref, self.Right_C0,'bx-',label='C0')
            ax.plot(self.t_Right_C0-self.t_ref, self.Right_C0+dy,'rx-',label='C0 front axle')
            
            
            if self.Time_RightLinePosLateral is not None:
                ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral,'m',label='OxTS')
 
            # fitted 5 points line 
            if self.do_fitted_5_points_line:
                slope, intercept,x,y = fit_line(self.t_LDW_Right_start, self.t_Right_C0, self.Right_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Right_start-t_ref, Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s"%(Right_C0_at_t_LDW_Right,slope))

            # ------------------------------
            # position of when lane marking is touched
            ax.hlines(self.WheelRight,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")
     
            
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Right_at_t_LDW_Right*tlc_0)
            ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Right_C0_at_t_LDW_Right,self.lateral_speed_Right_at_t_LDW_Right,self.Right_C0_at_t_LDW_Right-delta_distance))

            
            # stop
            ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,'ms')
            ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop,"  %5.2f m"%self.Right_C0_at_t_LDW_Right_stop)
  
            # ------------------------------
            ax.set_ylim(-1.0, 3.5)
       
            ax.set_xlim(local_xlim)
    
            ax.legend()
            ax.set_ylabel('outside <-- lateral position right [m] --> inside')
            ax.grid()

            # -------------------------------------
            ax = fig.add_subplot(312)
            ax.plot(self.t_Right_C0-self.t_ref, self.Right_C1,'bx-',label='C1 right')
            ax.set_ylabel('[rad]')
            ax.legend()
            ax.set_xlim(local_xlim)
            ax.grid()
            
            # -------------------------------------
            ax = fig.add_subplot(313)
            ax.plot(self.t_Right_C0-self.t_ref, dy ,'bx-',label='dy')
            ax.set_ylabel('[m]')
            ax.legend()
            ax.set_xlim(local_xlim)
            ax.grid()

            ax.set_xlabel('time [s]')

            
        # ===============================================  
        # left wheel 
        if self.LDW_Left_okay:

            ax = fig.add_subplot(311)
            ax.set_title('Left side')
        
            local_xlim = self.xlim_closeup
            
            dy = -self.dx_camera_to_front_axle*np.tan(self.Left_C1)

            
            # lines
            ax.plot(self.t_Left_C0-self.t_ref, self.Left_C0,'bx-',label='C0')
            ax.plot(self.t_Left_C0-self.t_ref, self.Left_C0+dy,'rx-',label='C0 front axle')

            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.Time_LeftLinePosLateral-self.t_ref, self.LeftLinePosLateral,'c',label='OxTS')
                
            if self.do_fitted_5_points_line:    
                slope, intercept,x,y = fit_line(self.t_LDW_Left_start, self.t_Left_C0, self.Left_C0)
                ax.plot(x-self.t_ref,y,'rx-')
                ax.plot(x-self.t_ref,slope*x+intercept,'rx-')
                #ax.text(t_LDW_Left_start-t_ref, Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s"%(Left_C0_at_t_LDW_Left,slope))

            # ------------------------------
            ax.hlines(self.WheelLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="lane marking")

 
            # ------------------------------
            # marker + text
        
            # start
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,'md')
            tlc_0 = 0.3
            delta_distance = np.abs(self.lateral_speed_Left_at_t_LDW_Left*tlc_0)
            ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s %3.2fm"%(self.Left_C0_at_t_LDW_Left,self.lateral_speed_Left_at_t_LDW_Left,self.Left_C0_at_t_LDW_Left+delta_distance))
  
            # stop
            ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,'ms')
            ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop,"  %5.2f m"%self.Left_C0_at_t_LDW_Left_stop)
  
            # ------------------------------
            #ax.set_ylim((np.min(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop),np.max(Left_C0_at_t_LDW_Left,Left_C0_at_t_LDW_Left_stop)))
            ax.set_ylim(-3.5, 1.0)
            ax.set_xlim(local_xlim)
 
            ax.legend()
            ax.set_ylabel('inside <- lateral position left [m] -> outside')
            ax.grid()

            # -------------------------------------
            ax = fig.add_subplot(312)
            ax.plot(self.t_Left_C0-self.t_ref,  self.Left_C1, 'bx-',label='C1 left')
            ax.set_ylabel('[rad]')
            ax.legend()
            ax.set_xlim(local_xlim)
            ax.grid()

            # -------------------------------------
            ax = fig.add_subplot(313)
            ax.plot(self.t_Left_C0-self.t_ref,  dy, 'bx-',label='dy')
            ax.set_ylabel('[m]')
            ax.legend()
            ax.set_xlim(local_xlim)
            ax.grid()

            ax.set_xlabel('time [s]')
            
        # -------------------------------------
        self.show_and_save_figure()

        

     
#=================================================================================
#=================================================================================
class cPlotFLC20LDWSSim(cPlotFLC20LDWSBase):
    '''
       plots for simulation
    '''
   
    def __init__(self, SilLDWS_C,PngFolder = r".\png", t_start = None, VehicleName='', cfg={}, show_figures=False, verbose=False):
        print "cPlotFLC20LDWSSim()"
        
        #  1. SilLDWS_C    
        if isinstance(SilLDWS_C, kbtools.CSimOL_MatlabBinInterface):
            print "CSimOL_MatlabBinInterface detected"
            self.SilLDWS_C        = SilLDWS_C
            self.sim_input        = SilLDWS_C.matdata_input
            self.sim_parameters   = SilLDWS_C.matdata_parameters
            self.sim_output       = SilLDWS_C.matdata_output
            self.expected_results = SilLDWS_C.matdata_expected_results
            self.FileName         = SilLDWS_C.BaseName
            self.Description      = SilLDWS_C.Description
            self.xlim             = SilLDWS_C.xlim
            self.FLR20_sig        = SilLDWS_C.FLR20_sig 
        else:
            print "CSimOL_MatlabBinInterface not given"
            raise
                   
         
        # 2. PngFolder
        self.PngFolder = PngFolder
        print "PngFolder: ",self.PngFolder
        if not os.path.exists(self.PngFolder):
            os.makedirs(self.PngFolder)
            print " -> created"
        
        # 3. t_start
        self.t_start = t_start
        
        # 4. VehicleName
        self.VehicleName = VehicleName
        
        # 5. cfg
        self.cfg = cfg
        
        # 6. show_figures
        self.show_figures   = show_figures
       
        # 7. verbose
        self.verbose = verbose

        print "xlim", self.xlim
        cPlotFLC20LDWSBase.__init__(self,self.SilLDWS_C, self.t_start, xlim=self.xlim, PngFolder = self.PngFolder, VehicleName=self.VehicleName,cfg=self.cfg, show_figures=self.show_figures,verbose=self.verbose)
      
                
        # ---------------------------------------
        # t_ref is set in base class
        if self.t_ref is not None:
            tmp_t_ref = self.t_ref
        else:
            tmp_t_ref = 0.0
            
        self.sim_input['t_rel']  = self.sim_input['t']-tmp_t_ref
        self.sim_output['t_rel'] = self.sim_output['t']-tmp_t_ref
               

        if 't_videopacket' in self.sim_input:
            self.sim_input['t_rel_videopacket'] = self.sim_input['t_videopacket'] - tmp_t_ref
        
        if ('t_BxInfo' in self.sim_input) and (self.sim_input['t_BxInfo'] is not None):
            print "self.sim_input['t_BxInfo']", self.sim_input['t_BxInfo']
            print "tmp_t_ref", tmp_t_ref
            self.sim_input['t_rel_BxInfo'] = self.sim_input['t_BxInfo'] - tmp_t_ref
        else:
            self.sim_input['t_rel_BxInfo'] = None
                

        # -------------------------------------------------------------------
        #  reference to instance of CPlotLDWS (purpose re use)
        self._PlotLDWS = None
        
        print "self.FileName", self.FileName
   
    # --------------------------------------------------------------------------------------------------------
    def GetPlotLDWS(self):
    
        if self._PlotLDWS is None:
            self._PlotLDWS = kbtools_user.cPlotFLC20LDWS(self.SilLDWS_C, self.t_start, xlim=self.xlim, PngFolder = self.PngFolder, VehicleName=self.VehicleName,cfg=self.cfg, show_figures=self.show_figures,verbose=self.verbose)

        return self._PlotLDWS
        
    PlotLDWS = property(GetPlotLDWS)
    
    #=================================================================================
    def PlotAll(self,enable_png_extract = True,OffsetList=None, mode='standard', test_mode_f = False):
        
        print "PlotAll() - start"
        try:
           print "LDW_SUPPR_BX_0X80_LNVU_ENABLE", self.sim_parameters['LDW_SUPPR_BX_0X80_LNVU_ENABLE']
           LNVU_not_ME_flag = self.sim_parameters['LDW_SUPPR_BX_0X80_LNVU_ENABLE']
        except:
           LNVU_not_ME_flag = True
        # ----------------------------------------------------------------------------------- 
        # extract frames from video
        
        if enable_png_extract:
            if self.verbose:
                print "---------------------------------------"
                print "extract frames from video:"
            FullPathFileName = self.FLR20_sig['FileName_org']
            if OffsetList is None:
                OffsetList = [-4.0,-3.5,-3.0,-2.5,-2.0,-1.5, -1.0, -0.5, 0.0, +0.5, +1.0, +1.5, +2.0, +2.5] 
            kbtools_user.CreateVideoSnapshots(FullPathFileName,self.FLR20_sig, self.t_event, OffsetList = OffsetList, PngFolder = self.PngFolder,verbose=self.verbose)
                    
        # ----------------------------------------------------------------------------------- 
        # plot
        if test_mode_f:
            self.plot_LDWS_supp_HIGH_STEERING_RATE()
            self.plot_LDWS_supp_HIGH_STEERING_RATE_rapid_prototyping()
            return
    
            self.plot_LDWS_cmp_SIM_vs_Truck_2()
            self.plot_LDWS_C0_Filter()
            self.plot_LDWS_UpdateVehicleData_1()
            #self.plot_LDWS_outputs_2(customer_version=False,xlim=(-0.2,0.2))
            self.plot_LDWS_outputs_2(customer_version=False)
            #self.plot_LDWS_outputs_3(xlim=(-0.2,0.2),yzoom=True)
            self.plot_LDWS_outputs_4_homologation()
            #self.plot_LDWS_cmp_ME_LNVU_TLC(xlim=(-0.2,0.2))
            #self.plot_LDWS_cmp_ME_LNVU_Distance(xlim=(-0.2,0.2))
            return

        if mode == "standard":
            #self.plot_LDWS_cmp_ME_LNVU_outputs()  #  not currently the focus; 
            self.plot_LDWS_inputs_1()
            self.plot_LDWS_inputs_2()
            self.plot_LDWS_inputs_3()
            self.plot_LDWS_outputs_1()
            self.plot_LDWS_outputs_2(customer_version=True)
            self.plot_LDWS_outputs_2(customer_version=False)
            self.plot_LDWS_outputs_3()
        
            #self.plot_LDWS_Lateral_Velocity_details()      # calculation of lateral velocity
            #self.plot_LDWS_UpdateVehicleData_1()           # C0 filtering
        
            self.plot_LDWS_cmp_SIM_vs_Truck_1(LNVU_not_ME_flag=LNVU_not_ME_flag)
            self.plot_LDWS_cmp_SIM_vs_Truck_2()
            self.plot_LDWS_cmp_SIM_vs_Truck_3(LNVU_not_ME_flag=LNVU_not_ME_flag)
                
            self.plot_LDWS_supp_LOW_SPEED()
            self.plot_LDWS_supp_TURN_SIGNAL()
            self.plot_LDWS_supp_HIGH_DECEL()
            self.plot_LDWS_supp_HIGH_LATVEL()
            self.plot_LDWS_supp_HIGH_LATVEL2()
            self.plot_LDWS_supp_HIGH_STEERING_RATE()
            self.plot_LDWS_supp_HIGH_STEERING_RATE_rapid_prototyping()
    
            #self.plot_LDWS_cmp_ME_LNVU_TLC()
            #self.plot_LDWS_cmp_ME_LNVU_Distance()
            #self.plot_LDWS_asymm()
       
            #self.plot_LDWS_videopacket_sync()
        
            #self.plot_LDWS_Set_BX_LDW_LaneDeparture()
            #self.plot_LDWS_DetermineWarningAlarm()
        elif mode == "Homologation":
            pass
               
        print "PlotAll() - end"
    # --------------------------------------------------------------------------------------------------------
    def plot_isWarning(self, ax):
       
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']+6.0,        'r',label='Sim - isWarnLeft (+6)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']+4.0,'m',label='Sim - ImminentLeft (+4)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']+2.0,       'b',label='Sim - isWarnRight (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right'],   'c',label='Sim - ImminentRight ' )
        self.set_description(ax,'Warning',(-0.1, 8.1) ) 
    
    # --------------------------------------------------------------------------------------------------------
    def plot_suppress1(self, ax, source):
     
        if source == 'FLC':
            t            = self.sim_input['t_rel']
            BX_LDW_Suppr = self.sim_input['BX_LDW_Suppr']
        elif source == 'SIM':
            t            = self.sim_output['t_rel']
            BX_LDW_Suppr = self.sim_output['BX_Warning_Suppression']
        else:
            return
    
        a = BX_LDW_Suppr.astype(int)
        ax.plot(t, (np.bitwise_and(a,0x0001)>0) +6.0,'m',label='ALARM_QUIET_TIME (+6)')   # BX_LDW_Suppr_ALARM_QUIET_TIME
        ax.plot(t, (np.bitwise_and(a,0x0002)>0) +4.0,'k',label='SYSTEM_DISABLED (+4)')    # BX_LDW_Suppr_SYSTEM_DISABLED
        ax.plot(t, (np.bitwise_and(a,0x0004)>0) +2.0,'b',label='LOW_SPEED (+2)')          # BX_LDW_Suppr_LOW_SPEED
        ax.plot(t, (np.bitwise_and(a,0x0008)>0) +0.0,'r',label='TURN_SIGNAL ')            # BX_LDW_Suppr_TURN_SIGNAL
        self.set_description(ax, 'Suppr 1 \n %s'%source,(-0.1, 8.1))

    # --------------------------------------------------------------------------------------------------------
    def plot_suppress2(self, ax, source):
     
        if source == 'FLC':
            t            = self.sim_input['t_rel']
            BX_LDW_Suppr = self.sim_input['BX_LDW_Suppr']
        elif source == 'SIM':
            t            = self.sim_output['t_rel']
            BX_LDW_Suppr = self.sim_output['BX_Warning_Suppression']
        else:
            return
    
        a = BX_LDW_Suppr.astype(int)
        ax.plot(t, (np.bitwise_and(a,0x0010)>0) +6.0,'m',label='HAZARD_LIGHTS (+6)')   # BX_LDW_Suppr_HAZARD_LIGHTS
        ax.plot(t, (np.bitwise_and(a,0x0020)>0) +4.0,'k',label='HIGH_DECEL (+4)')      # BX_LDW_Suppr_HIGH_DECEL
        ax.plot(t, (np.bitwise_and(a,0x0040)>0) +2.0,'b',label='HIGH_LATVEL (+2)')     # BX_LDW_Suppr_HIGH_LATVEL
        ax.plot(t, (np.bitwise_and(a,0x0080)>0) +0.0,'r',label='BRAKE_PRESSED ')       # BX_LDW_Suppr_BRAKE_PRESSED
        self.set_description(ax, 'Suppr 2 \n %s'%source,(-0.1, 8.1))
       
    # --------------------------------------------------------------------------------------------------------
    def plot_suppress3(self, ax, source):
     
        if source == 'FLC':
            t            = self.sim_input['t_rel']
            BX_LDW_Suppr = self.sim_input['BX_LDW_Suppr']
        elif source == 'SIM':
            t            = self.sim_output['t_rel']
            BX_LDW_Suppr = self.sim_output['BX_Warning_Suppression']
        else:
            return
    
        a = BX_LDW_Suppr.astype(int)
        ax.plot(t, (np.bitwise_and(a,0x0100)>0) +6.0,'m',label='HIGH_CURVATURE (+6)')   # BX_LDW_Suppr_HIGH_CURVATURE
        ax.plot(t, (np.bitwise_and(a,0x0200)>0) +4.0,'k',label='HIGH_STEERING_RATE (+4)')   # BX_LDW_Suppr_HIGH_STEERING_RATE
        ax.plot(t, (np.bitwise_and(a,0x0400)>0) +2.0,'b',label='CONSTRUCTION_ZONE (+2)')   # BX_LDW_Suppr_CONSTRUCTION_ZONE
        ax.plot(t, (np.bitwise_and(a,0x0800)>0) +0.0,'r',label='ACC_ALERT_ACTIVE ')   # BX_LDW_Suppr_ACC_ALERT_ACTIVE
        #ax.plot(t, (np.bitwise_and(a,0x1000)>0) +2.0,'c',label='ALARM_MAX_DURATION (+2)')   # WS_ALARM_MAX_DURATION
        #ax.plot(t, (np.bitwise_and(a,0x2000)>0) +0.0,'r',label='INNER_RESET ')   # WS_INNER_RESET
        self.set_description(ax, 'Suppr 3 \n %s'%source,(-0.1, 8.1))
       
    # --------------------------------------------------------------------------------------------------------
    def plot_suppress4(self, ax, source):
     
        if source == 'FLC':
            t            = self.sim_input['t_rel']
            BX_LDW_Suppr = self.sim_input['BX_LDW_Suppr']
        elif source == 'SIM':
            t            = self.sim_output['t_rel']
            BX_LDW_Suppr = self.sim_output['BX_Warning_Suppression']
        else:
            return
    
        a = BX_LDW_Suppr.astype(int)
        ax.plot(t, (np.bitwise_and(a,0x1000)>0) +6.0,'m',label='ALARM_MAX_DURATION (+6)')   # WS_ALARM_MAX_DURATION
        ax.plot(t, (np.bitwise_and(a,0x2000)>0) +4.0,'k',label='INNER_RESET (+4)')          # WS_INNER_RESET
        ax.plot(t, (np.bitwise_and(a,0x4000)>0) +2.0,'b',label='MIN_LANE_WIDTH (+2)')       # WS_MIN_LANE_WIDTH
        ax.plot(t, (np.bitwise_and(a,0x8000)>0) +0.0,'r',label='OUTER_RESET ')              # WS_OUTER_RESET
        self.set_description(ax, 'Suppr 4 \n %s'%source,(-0.1, 8.1))
     

       
       
    # --------------------------------------------------------------------------------------------------------
    def calc_RefTLC_Left(self):
        t_Left_C0    = self.sim_input["Time_C0_Left"]
        Left_C0      = self.sim_input["C0_Left"]
        Left_C1      = self.sim_input["C1_Left"]
       
        vRef_Left  =  kbtools.resample( self.sim_input['t'],  self.sim_input['FrontAxleSpeed']/3.6,t_Left_C0) 
        
        RefTLC_Left  = (-Left_C0-self.VehicleWidthHalf+0.15)/(Left_C1*vRef_Left)
        
        return t_Left_C0- self.t_ref,RefTLC_Left
        
    # --------------------------------------------------------------------------------------------------------
    def calc_RefTLC_Right(self):
    
        t_Right_C0   = self.sim_input["Time_C0_Right"]
        Right_C0     = self.sim_input["C0_Right"]
        Right_C1     = self.sim_input["C1_Right"]
    
        vRef_Right =  kbtools.resample( self.sim_input['t'],  self.sim_input['FrontAxleSpeed']/3.6,t_Right_C0) 
        
        RefTLC_Right = (-Right_C0-self.VehicleWidthHalf+0.15)/(Right_C1*vRef_Right)
        
        return t_Right_C0- self.t_ref, RefTLC_Right
    
    # =========================================================================================================================  
    # =========================================================================================================================          
    def plot_LDWS_cmp_ME_LNVU_outputs(self,FigNr = 100):
        '''
           compare Mobileye and LNVU outputs
        
        '''
    
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_1_cmp_ME_LNVU_outputs", FigNr)

        # ------------------------------------------------------
        # Warnings Left
        ax = fig.add_subplot(211)
        ax.set_title('Left side')
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']     +6.0,'b', label='FLC - ME Warn (+6)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']           +4.0,'m', label='SIM - LNVU isWarn (+4)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']   +2.0,'r', label='SIM - Imminent (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Left']     ,'k', label='SIM - Acoustical')
        ax.set_yticks([0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0])        
        ax.set_yticklabels(['Off','SIM - Acoustical-On','Off','SIM - Imminent-On','Off','SIM - LNVU isWarn-On','Off','FLC - ME Warn-On'])
        self.set_description(ax,'',(-0.1,8.1))
        
        # ------------------------------------------------------
        # Warnings Right
        ax = fig.add_subplot(212)
        ax.set_title('Right side')
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']      +6.0,'b', label='FLC - ME Warn (+6)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']            +4.0,'m', label='SIM - LNVU isWarn (+4)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']    +2.0,'r', label='SIM - Imminent (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Right']      ,'k', label='SIM - Acoustical')
        ax.set_yticks([0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0])        
        ax.set_yticklabels(['Off','SIM - Acoustical-On','Off','SIM - Imminent-On','Off','SIM - LNVU isWarn-On','Off','FLC - ME Warn-On'])
        self.set_description(ax,'',(-0.1,8.1))
       
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
        
    # =========================================================================================================================  
    def plot_LDWS_inputs_1(self,FigNr = 210):
            
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_2.1_inputs", FigNr)
    
        # ------------------------------------------------------
        # offsets C0
        ax = fig.add_subplot(411)
        ax.plot(self.sim_input['t_rel'], self.sim_input['Left_C0'], 'b',label='Left_C0')
        ax.plot(self.sim_input['t_rel'], self.sim_input['Right_C0'],'r',label='Right_C0')
        
        self.set_description(ax,'[m]',(-5.1,5.1))

        
        # ------------------------------------------------------
        # heading angle C1
        ax = fig.add_subplot(412)
        ax.plot(self.sim_input['t_rel'], self.sim_input['Left_C1'],'b', label='Left_C1')
        ax.plot(self.sim_input['t_rel'], self.sim_input['Right_C1'],'r',label='Right_C1')
        
        self.set_description(ax,'[rad]',(-0.2,0.2))

        # ------------------------------------------------------
        # ME Warnings, Lane Tracking, Lane Crossing
        ax = fig.add_subplot(413)
    
        ax.plot(self.sim_input['t_rel'], self.sim_input['ME_LDW_LaneDeparture_Left']  +10.0,'b', label='ME Warn Left(+10)')
        ax.plot(self.sim_input['t_rel'], self.sim_input['ME_LDW_LaneDeparture_Right']  +8.0,'r', label='ME Warn Right(+8)')

        ax.plot(self.sim_input['t_rel'], self.sim_input['LDW_Left_Tracking']           +6.0,'b', label='Tracking Left(+6)')
        ax.plot(self.sim_input['t_rel'], self.sim_input['LDW_Right_Tracking']          +4.0,'r', label='Tracking Right(+4)')
     
        ax.plot(self.sim_input['t_rel'], self.sim_input['Left_Lane_Crossing']          +2.0,'b', label='Crossing Left(+2)')
        ax.plot(self.sim_input['t_rel'], self.sim_input['Right_Lane_Crossing']             ,'r', label='Crossing Right')
        
        ax.set_yticks([0.0,1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0,11.0])  
        label1 = ['Off','Crossing Right-On','Off','Crossing Left-On']
        label2 = ['Off','Tracking Right-On','Off','Tracking Left-On']
        label3 = ['Off','ME warn Right-On' ,'Off','ME warn Left-On']
        ax.set_yticklabels(label1+label2+label3)
        self.set_description(ax,'',(-0.1,12.1))

   
        
        # ------------------------------------------------------
        # Lane Quality
        ax = fig.add_subplot(414)
    
        ax.plot(self.sim_input['t_rel'], self.sim_input['Lane_Left_Quality'], 'b',label='Lane Left Quality')
        ax.plot(self.sim_input['t_rel'], self.sim_input['Lane_Right_Quality'],'r',label='Lane Right Quality')
    
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['No','Low','Medium','High'])
    
        self.set_description(ax,'',(-0.1,3.1))
 
   
        ax.set_xlabel('time [s]')
       
             
        # ------------------------------------------------------
        self.show_and_save_figure()


    # =========================================================================================================================  
    def plot_LDWS_inputs_2(self,FigNr = 220):
            
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_2.2_inputs", FigNr)
    
        # ------------------------------------------------------
        # SensorStatus
        ax = fig.add_subplot(211)
        ax.plot(self.sim_input['t_rel'], self.sim_input['SensorStatus'],'b', label='SensorStatus')
        ax.set_yticks(range(16))   
        label1 = ['Fully Operational (0)','Warming up / Initializing (1)','Partially Blocked (2)','Blocked (3)']
        label2 = ['(4)','(5)','(6)','(7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)
        self.set_description(ax,None,(-0.1,15.1))
        
        
        # ------------------------------------------------------
        # LDWS State
        ax = fig.add_subplot(212)
        
        try:         
            ax.plot(self.sim_input['Time_J1939_StateOfLDWS']-self.t_ref, self.sim_input['J1939_StateOfLDWS'],'bx', label='FLC - KB_System_State')
        except:
            pass
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_System_State'],'r', label='SIM - KB_System_State')
        
        ax.set_yticks(range(16))   
        label1 = ['Not ready (0)','Temp. not avail. (1)','Deact. by driver (2)','Ready (3)']
        label2 = ['Driver override (4)','Warning (5)','(6)','(7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)
        self.set_description(ax,None,(-0.1,15.1))

        ax.set_xlabel('time [s]')
        
        # ------------------------------------------------------
        self.show_and_save_figure()
        
      
 
    # ========================================================================================================================= 
    def plot_LDWS_inputs_3(self,FigNr = 230):
        print "plot_LDWS_inputs_3"
        #self.PlotLDWS.plot_4_lanes(PlotName = "LDWS_2.3_inputs")
        self.plot_4_lanes(PlotName = "LDWS_2.3_inputs")
  
    # ========================================================================================================================= 
    def plot_LDWS_C0_Filter(self,FigNr = 312,customer_version=False,xlim=None):
        print "plot_LDWS_C0_Filter"
        self.plot_1_C0_Filter(PlotName = "LDWS_1.1_C0_Filter")
            
    # ========================================================================================================================= 
    def plot_LDWS_outputs_1(self,FigNr = 311):
    
    
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_3.1_outputs", FigNr)
 
        # ------------------------------------------------------
        # LDW_Enabled_State
        ax = fig.add_subplot(411)
        ax.plot(self.sim_output['t_rel'], self.sim_output['Bendix_LDW_Enabled_State'],'b', label='SIM - Bendix_LDW_Enabled_State')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Enabled_State']    ,'r', label='SIM - KB_LDW_Enabled_State')
        ax.set_yticks([0.0,1.0])        
        ax.set_yticklabels(['Disabled','Enabled'])
        self.set_description(ax,'[-]',(-0.1,1.1))
 
        # ------------------------------------------------------
        # State
        ax = fig.add_subplot(412)
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_System_State']         ,'r', label='SIM - KB_System_State')
        try:         
            ax.plot(self.sim_input['Time_J1939_StateOfLDWS']-self.t_ref, self.sim_input['J1939_StateOfLDWS'],'bx', label='FLC - KB_System_State')
        except:
            pass
        ax.set_yticks(range(16))   
        label1 = ['Not ready (0)','Temp. not avail. (1)','Deact. by driver (2)','Ready (3)']
        label2 = ['Driver override (4)','Warning (5)','(6)','(7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)
        self.set_description(ax,'State',(-0.1,15.1))

         
          
        # ------------------------------------------------------
        # Left
        ax = fig.add_subplot(413)
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']   +10.0,'k', label='FLC - ME LD' )
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       +8.0,'y', label='FLC - Imm'  )
 
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       +2.0,'c', label='FLC - Imminent')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']  +2.0,'b', label='SIM - Imminent')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningLeft']        +0.0,'m', label='FLC - Acoustical')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Left']+0.0,'r', label='SIM - Acoustical')
        
        #ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Optical_State_Left']   +2.0,'r', label='SIM - KB Optical')
        
        #ax.plot(self.sim_output['t_rel'], self.sim_output['Bendix_LDW_Left']                 ,'c', label='SIM - BX LDW' )
  
        #ax.set_yticks(range(12))   
        #label1 = ['Off','BX LDW - On']
        #label2 = ['Off','KB Acoustical - On','Off','KB Optical - On','Off','KB Imminent - On']
        #label3 = ['Off','Imm - On','Off','ME LD - On']
        ax.set_yticks(range(4))   
        label1 = ['Off','Acoustical - On']
        label2 = ['Off','Imminent - On']
        label3 = []
        
        ax.set_yticklabels(label1+label2+label3)

        #self.set_description(ax,'Left',(-0.1,12.1))
        self.set_description(ax,'Left',(-0.1,3.1))

        # ------------------------------------------------------
        # Right
        ax = fig.add_subplot(414)
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']   +10.0,'k', label='FLC - ME LD' )
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       +8.0,'y', label='FLC - Imm'  )
 
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       +2.0,'c', label='FLC - Imminent(+2)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']  +2.0,'b', label='SIM - Imminent')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningRight']        +0.0,'m', label='FLC - Acoustical' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Right']+0.0,'r', label='SIM - Acoustical')
        #ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Optical_State_Right']   +4.0,'r', label='SIM - KB Optical')
        
        #ax.plot(self.sim_output['t_rel'], self.sim_output['Bendix_LDW_Right']                 ,'c', label='SIM - BX LDW' )
  
        #ax.set_yticks(range(12))   
        #label1 = ['Off','BX LDW - On']
        #label2 = ['Off','KB Acoustical - On','Off','KB Optical - On','Off','KB Imminent - On']
        #label3 = ['Off','Imm - On','Off','ME LD - On']
        ax.set_yticks(range(4))   
        label1 = ['Off','Acoustical - On']
        label2 = ['Off','Imminent - On']
        label3 = []
        
        ax.set_yticklabels(label1+label2+label3)

        #self.set_description(ax,'Right',(-0.1,12.1))
        self.set_description(ax,'Right',(-0.1,3.1))

        # ------------------------------------------------------
        # Lateral_Velocity
        #ax = fig.add_subplot(515)
        #ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Left'],'b',  label='vy left')
        #ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Right'],'r', label='vy right')
        
        #self.set_description(ax,'[m/s]',(-1.1,1.1))

        ax.set_xlabel('time [s]')
        
        # ------------------------------------------------------
        self.show_and_save_figure()
    # ========================================================================================================================= 
    def plot_LDWS_outputs_2(self,FigNr = 312,customer_version=False,xlim=None):
        print "plot_LDWS_outputs_2"
        #self.PlotLDWS.plot_2_lane(PlotName = "LDWS_3.2_outputs",customer_version=customer_version)
        self.plot_2_lane(PlotName = "LDWS_3.2_outputs",customer_version=customer_version,xlim=xlim)
       
    # ========================================================================================================================= 
    def plot_LDWS_outputs_3(self,FigNr = 313,xlim=None,yzoom=False):
        print "plot_LDWS_outputs_3"
        #self.PlotLDWS.plot_2_lateral_position(PlotName = "LDWS_3.3_outputs")
        self.plot_2_lateral_position(PlotName = "LDWS_3.3_outputs",xlim=xlim,yzoom=yzoom)
 
    # ========================================================================================================================= 
    def plot_LDWS_outputs_4_homologation(self,FigNr = 314):
        print "plot_LDWS_outputs_4_homologation"
        self.plot_2_lane_homologation(PlotName = "LDWS_3.4_outputs_homologation")
 
 
 
    #=================================================================================
    def plot_LDWS_Lateral_Velocity_details(self,FigNr = 410):
            
        t_Left_C0    = self.sim_input["Time_C0_Left"] - self.t_ref
        Left_C0      = self.sim_input["C0_Left"]
        Left_C1      = self.sim_input["C1_Left"]
    
        t_Right_C0   = self.sim_input["Time_C0_Right"] - self.t_ref
        Right_C0     = self.sim_input["C0_Right"]
        Right_C1     = self.sim_input["C1_Right"]
    
        vRef_Left  =  kbtools.resample( self.sim_input['t_rel'],  self.sim_input['FrontAxleSpeed']/3.6,t_Left_C0) 
        vRef_Right =  kbtools.resample( self.sim_input['t_rel'],  self.sim_input['FrontAxleSpeed']/3.6,t_Right_C0) 
   
        # --------------------------------------------------------
        # numerical differentiation of C0_left/right    
        T = 1.0
        fd_Left_C0, f_Left_C0   = kbtools.svf_1o(t_Left_C0, Left_C0,T)
        fd_Right_C0, f_Right_C0 = kbtools.svf_1o(t_Right_C0, Right_C0,T)
         

         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_4.1_Lateral_Velocity_details", FigNr)


        # ------------------------------------------------------
        # offsets C1
        ax = fig.add_subplot(311)
        ax.plot(self.sim_input['t_rel'], self.sim_input['Left_C0'],'b-',  label='Left_C0 (resampled)' )
        ax.plot(self.sim_input['t_rel'], self.sim_input['Right_C0'],'r-', label='Right_C0 (resampled)' )
        
        ax.plot(t_Left_C0,  Left_C0,'m-',  label='Left_C0' )
        ax.plot(t_Right_C0, Right_C0,'k-', label='Right_C0' )
      
        self.set_description(ax,'[m]',(-5.1,5.1))

        # ------------------------------------------------------
        # Lateral_Velocity - heading C1 * vehicle speed
        ax = fig.add_subplot(312)
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Left'],'b-',  label='SIM - vy left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Right'],'r-', label='SIM - vy right' )
  
        ax.plot(t_Left_C0,     Left_C1*vRef_Left,'m-', label='Left_C1 * v')
        ax.plot(t_Right_C0, -Right_C1*vRef_Right,'k-', label='Right_C1 * v')
        
        self.set_description(ax,'[m/s]',(-1.1,1.1))

        # ------------------------------------------------------
        # Lateral_Velocity - d/dt C0
        ax = fig.add_subplot(313)
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Left'] ,'b-', label='SIM - vy left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Right'],'r-', label='SIM - vy right' )
     
        ax.plot(t_Left_C0,    fd_Left_C0,'m-', label='d/dt C0 left' )
        ax.plot(t_Right_C0, -fd_Right_C0,'k-', label='d/dt C0 right' )
      
        self.set_description(ax,'[m/s]',(-1.1,1.1))
              
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
        
    # =========================================================================================================================          
    def plot_LDWS_UpdateVehicleData_1(self,FigNr = 500):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_5.1_UpdateVehicleData", FigNr)
      
        # ------------------------------------------------------
        # C0 Left
        ax = fig.add_subplot(311)
        ax.set_title('Left Side')
        ax.plot(self.sim_input['t_rel'],  -self.sim_input['Left_C0'],      'b',  label='-Left_C0' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_laneOffset_Left'],   'r',  label='BX_laneOffset_Left' )
        self.set_description(ax,'[m]',(-0.1,3.1) ) 
       
        # ------------------------------------------------------
        # C0 Right
        ax = fig.add_subplot(312)
        ax.set_title('Right Side')
        ax.plot(self.sim_input['t_rel'],  self.sim_input['Right_C0'],      'b',  label='Right_C0' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_laneOffset_Right'],  'r',  label='BX_laneOffset_Right' )
        self.set_description(ax,'[m]',(-0.1,3.1)  ) 

        # ------------------------------------------------------
        # error 
        ax = fig.add_subplot(313)
        ax.set_title('error both sides')
        # we are not clean - self.sim_input and self.sim_output could have different length
        try:
            ax.plot(self.sim_output['t_rel'], -self.sim_input['Left_C0']- self.sim_output['BX_laneOffset_Left'],   'b',  label='Left' )
        except:
            pass
        try:
            ax.plot(self.sim_output['t_rel'], self.sim_input['Right_C0']- self.sim_output['BX_laneOffset_Right'],  'r',  label='Right' )
        except:
            pass
        self.set_description(ax,'[m]',(-0.1,0.1)  ) 
       
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()

        

        
    # =========================================================================================================================          
    def plot_LDWS_cmp_SIM_vs_Truck_1(self,FigNr = 160,LNVU_not_ME_flag = True):
         
        
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_6.1_cmp_SIM_vs_FLC", FigNr)
 
        # ------------------------------------------------------
        # Warnings left
        ax = fig.add_subplot(211)
        if LNVU_not_ME_flag:
            if self.sim_input['Time_LNVU_isWarningLeft'] is not None:
                ax.plot(self.sim_input['Time_LNVU_isWarningLeft']-self.t_ref,  self.sim_input['LNVU_isWarningLeft']+ 6.0,'b', label='FLC - isWarn (+6)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']          + 6.0,'r', label='Sim - isWarn (+6)')
        else:
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    + 6.0,'b', label='FLC - ME Warn (+6)')
            
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       + 4.0,'b', label='FLC - Imminent(+4)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']  + 4.0,'r', label='Sim - Imminent (+4)')
       
        ax.plot(self.sim_input['t_rel'],  (self.sim_input['BX_LDW_Suppr']>0)             + 2.0,'b', label='FLC - supp. active (+2)')
        ax.plot(self.sim_output['t_rel'], (self.sim_output['BX_Warning_Suppression']>0)  + 2.0,'r', label='Sim - supp. active (+2)')
        

        #ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Left']  + 2.0,'m', label='Sim - BX_LDW_LaneDeparture (+2)')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningLeft']             ,'b', label='FLC - Acoustical')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Left']     ,'r', label='Sim - Acoustical')
        ax.set_yticklabels(['0','Off','On','Off','On','Off','On','Off','On'])
        self.set_description(ax,'Left',(-0.1,8.1) ) 
        
        
        # ------------------------------------------------------
        # Warnings right
        ax = fig.add_subplot(212)
        if LNVU_not_ME_flag:
            if self.sim_input['Time_LNVU_isWarningRight'] is not None:
                ax.plot(self.sim_input['Time_LNVU_isWarningRight']-self.t_ref,  self.sim_input['LNVU_isWarningRight']+ 6.0,'b', label='FLC - isWarn (+6)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']          + 6.0,'r', label='Sim - isWarn (+6)')
        else:
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    + 6.0,'b', label='FLC - ME Warn (+6)' )
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       + 4.0,'b', label='FLC - Imminent(+4)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']  + 4.0,'r', label='Sim - Imminent (+4)' )

        ax.plot(self.sim_input['t_rel'],  (self.sim_input['BX_LDW_Suppr']>0)              + 2.0,'b', label='FLC - supp. active (+2)' )
        ax.plot(self.sim_output['t_rel'], (self.sim_output['BX_Warning_Suppression']>0)   + 2.0,'r', label='Sim - supp. active (+2)' )
        
        #ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Right']  + 2.0,'m', label='Sim - BX_LDW_LaneDeparture (+2)')

        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningRight']             ,'b', label='FLC - Acoustical' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Right']     ,'r', label='Sim - Acoustical' )
        ax.set_yticklabels(['0','Off','On','Off','On','Off','On','Off','On'])
        self.set_description(ax,'Right',(-0.1,8.1) ) 
  

        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
    
    
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cmp_SIM_vs_Truck_2(self,FigNr = 161):
         
       
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_6.2_cmp_SIM_vs_FLC", FigNr)
       
       
        # ------------------------------------------------------
        # Suppression 
        ax = fig.add_subplot(711)
        ax.plot(self.sim_input['t_rel'],  (self.sim_input['BX_LDW_Suppr']>0)           ,'b', label='FLC - supp. active' )
        ax.plot(self.sim_output['t_rel'], (self.sim_output['BX_Warning_Suppression']>0),'r', label='Sim - supp. active' )
        ax.set_yticklabels(['0','Off','On','Off'])
        self.set_description(ax,'Overall',(-0.1,2.1) ) 
 
        
        # ------------------------------------------------------
        # BX_Warning_Suppression
        ax = fig.add_subplot(712)
        self.plot_suppress1(ax,'FLC')
        ax = fig.add_subplot(713)
        self.plot_suppress1(ax,'SIM')

        ax = fig.add_subplot(714)
        self.plot_suppress2(ax,'FLC')
        ax = fig.add_subplot(715)
        self.plot_suppress2(ax,'SIM')
        
        ax = fig.add_subplot(716)
        self.plot_suppress3(ax,'FLC')
        ax = fig.add_subplot(717)
        self.plot_suppress3(ax,'SIM')

    
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
        
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cmp_SIM_vs_Truck_3(self,FigNr = 60, LNVU_not_ME_flag = True):
           
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_6.3_cmp_SIM_vs_FLC", FigNr)
           
        # ------------------------------------------------------
        # Warnings left
        ax = fig.add_subplot(611)
        if LNVU_not_ME_flag:
            if self.sim_input['Time_LNVU_isWarningLeft'] is not None:
                ax.plot(self.sim_input['Time_LNVU_isWarningLeft']-self.t_ref,  self.sim_input['LNVU_isWarningLeft']+ 4.0,'b', label='FLC - isWarn (+4)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']          + 4.0,'r', label='Sim - isWarn (+4)')
        else:
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    + 4.0,'b', label='FLC - ME Warn (+4)')
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    +4.0,'k', label='ME Warn (+4)')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       +2.0,'b', label='FLC - Imminent(+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']  +2.0,'r', label='Sim - Imminent (+2)')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningLeft']            ,'b', label='FLC - Acoustical')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Left']    ,'r', label='Sim - Acoustical')
        ax.set_yticklabels(['0','Off','On','Off','On','Off','On'])
        self.set_description(ax,'Left',(-0.1,6.1)) 
        
       
        
        # ------------------------------------------------------
        # Warnings
        ax = fig.add_subplot(612)
        if LNVU_not_ME_flag:
            if self.sim_input['Time_LNVU_isWarningRight'] is not None:
                ax.plot(self.sim_input['Time_LNVU_isWarningRight']-self.t_ref,  self.sim_input['LNVU_isWarningRight']+ 4.0,'b', label='FLC - isWarn (+4)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']          + 4.0,'r', label='Sim - isWarn (+4)')
        else:
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    + 4.0,'b', label='FLC - ME Warn (+4)' )
        #ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    +4.0,'k', label='ME Warn (+4)')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       +2.0,'b', label='FLC - Imminent(+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']  +2.0,'r', label='Sim - Imminent (+2)')
        
        ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningRight']            ,'b', label='FLC - Acoustical')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Right']    ,'r', label='Sim - Acoustical')
        ax.set_yticklabels(['0','Off','On','Off','On','Off','On'])
        self.set_description(ax,'Right',(-0.1,6.1)) 
    
    
        # ------------------------------------------------------
        # BX_Warning_Suppression
        mode = 'SIM'
        mode = 'FLC'
        ax = fig.add_subplot(613)
        self.plot_suppress1(ax,mode)

        ax = fig.add_subplot(614)
        self.plot_suppress2(ax,mode)
        
        ax = fig.add_subplot(615)
        self.plot_suppress3(ax,mode)
    
        ax = fig.add_subplot(616)
        self.plot_suppress4(ax,mode)
    
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
    
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_LOW_SPEED(self,FigNr = 173):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.3_supp_LOW_SPEED", FigNr)
      
       
        # ------------------------------------------------------
        ax = fig.add_subplot(411)
        self.plot_isWarning(ax)

        # ------------------------------------------------------
        # Vehicle Speed
        ax = fig.add_subplot(412)
        ax.plot(self.sim_input['t_rel'], self.sim_input['FrontAxleSpeed'],'b', label='FrontAxleSpeed')
        #ax.set_ylim(-0.1,100.1) 
        self.set_description(ax,'[km/h]',None) 
 
        # ------------------------------------------------------
        # AtWarningSpeed
        ax = fig.add_subplot(413)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_AtWarningSpeed'],'r', label='AtWarningSpeed')
        ax.set_yticks([0.0,1.0])        
        ax.set_yticklabels(['Off','On'])
        self.set_description(ax,'[-]',(-0.1,1.1)) 
       
          
        # ------------------------------------------------------
        # BX_LDW_Suppr_LOW_SPEED
        ax = fig.add_subplot(414)
        ax.plot(self.sim_input['t_rel'],  (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0004)>0),'b',label='FLC')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0004)>0),'r',label='Sim')
        
        #ax.plot(self.sim_input['t_rel_videopacket'], (np.bitwise_and(self.sim_input['COMPARE_BX_LDW_Suppr'].astype(int),0x0004)>0)*0.7,'yx-',label='FLC20 raw')
        #ax.plot(self.sim_input['t_rel_BxInfo'], (np.bitwise_and(self.sim_input['COMPARE_BX_LDW_Suppr'].astype(int),0x0004)>0)*0.7+0.1,'cx-',label='FLC20 cor')
        #ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay']*0.5,'mx-',label='delay')
        
        ax.set_yticks([0.0,1.0])        
        ax.set_yticklabels(['Off','On'])
        self.set_description(ax,'supp. LOW SPEED',(-0.1, 1.1)) 

     
        ax.set_xlabel('time [s]')
 

        # ------------------------------------------------------
        self.show_and_save_figure()
       

    
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_TURN_SIGNAL(self,FigNr = 174):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.4_supp_TURN_SIGNAL", FigNr)
        
        # ------------------------------------------------------
        ax = fig.add_subplot(311)
        self.plot_isWarning(ax)
          
        # ------------------------------------------------------
        # TurnSigSw 
        ax = fig.add_subplot(312)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['TurnSigSw'],'b',label='TurnSigSw' )
        self.set_description(ax,'',(-0.1,4.1)) 
                
 
        # ------------------------------------------------------
        # BX_LDW_Suppr_TURN_SIGNAL
        ax = fig.add_subplot(313)
        ax.plot(self.sim_input['t_rel'], (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0008)>0) +2.0,'b',label='Truck')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0008)>0),'r',label='Sim') 
        self.set_description(ax,'supp. TURN_SIGNAL',(-0.1, 4.1)) 
                      

        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
    

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_HIGH_DECEL(self,FigNr = 176):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.6_supp_HIGH_DECEL", FigNr)
      
       
        # ------------------------------------------------------
        ax = fig.add_subplot(511)
        self.plot_isWarning(ax)

        # ------------------------------------------------------
        # Vehicle Speed
        ax = fig.add_subplot(512)
        ax.plot(self.sim_input['t_rel'], self.sim_input['FrontAxleSpeed'],'b', label='FrontAxleSpeed')
        #ax.set_ylim(-0.1,100.1) 
        self.set_description(ax,'[km/h]',None) 
 
    

        # ------------------------------------------------------
        # Decel
        ax = fig.add_subplot(513)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_acceleration'],'r', label='Sim raw acc.')
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_acceleration_filtered'],'b',label='Sim filt. acc.' )
        self.set_description(ax,'[m/s$^2$]',None) 
      
          
        # ------------------------------------------------------
        # BX_LDW_Suppr_HIGH_DECEL
        ax = fig.add_subplot(514)
        ax.plot(self.sim_input['t_rel'], (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0020)>0) +2.0,'b',label='Truck')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0020)>0),'r',label='Sim') 
        self.set_description(ax,'supp. HIGH_DECEL',(-0.1, 4.1)) 

     
        # ------------------------------------------------------
        # Decel
        ax = fig.add_subplot(515)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['BrakePedalStatus']        +4.0,'k',label='BrakePedalStatus')
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BrakePedalPressed']+2.0,'r',label='BrakePedalPressed (+2)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighDeceleration'],'b',label='HighDeceleration' )
        self.set_description(ax,'flags',(-1.1,6.1)) 
 
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_HIGH_LATVEL(self,FigNr = 177):
         
       
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.7_supp_HIGH_LATVEL", FigNr)
     
        # ------------------------------------------------------
        ax = fig.add_subplot(511)
        self.plot_isWarning(ax)
       
        # ------------------------------------------------------
        # offsets
        ax = fig.add_subplot(512)
        ax.plot(self.sim_input['t_rel'], self.sim_input['Left_C0'],'b',label='Left_C0' )
        ax.plot(self.sim_input['t_rel'], self.sim_input['Right_C0'],'r',label='Right_C0' )
        self.set_description(ax,'[m]',None) 

        # ------------------------------------------------------
        # Lateral_Velocity
        ax = fig.add_subplot(513)
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Left'],'b',label='vy left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Right'],'r',label='vy right' )
        self.set_description(ax,'[m/s]',(-1.1,1.1)) 
      
        # ------------------------------------------------------
        # Decel
        ax = fig.add_subplot(514)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Right']+2.0,'r',label='Right (+2)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Left'],'b',label='Left' )
        self.set_description(ax,'HighLateralVelocity',(-0.1,4.1)) 

          
        # ------------------------------------------------------
        # BX_LDW_Suppr_HIGH_LATVEL
        ax = fig.add_subplot(515)
        ax.plot(self.sim_input['t_rel'], (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0040)>0) +2.0,'b',label='Truck')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0040)>0),'r',label='Sim') 
        self.set_description(ax,'supp. HIGH_LATVEL',(-0.1, 4.1)) 
   
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_HIGH_LATVEL2(self,PlotName = "LDWS_9.7b_supp_HIGH_LATVEL", FigNr = 178):
         
       
        # --------------------------------------------------------
        if self.LDW_Right_okay:
            PlotName = PlotName + '_right'
            fig = self.start_fig(PlotName, FigNr)
                       
            ax = fig.add_subplot(211)
            if self.FrontAxleSpeed_at_t_LDW_Right is not None:
                ax.set_title('Right side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Right*3.6,))
            else:
                ax.set_title('Right side')
                
            local_xlim = self.xlim_closeup
            local_xlim = (-1.0,2.0)
            
            self.xlim_to_use(local_xlim)
            
            t_lateral_speed_Right = self.sim_output['t']
            lateral_speed_Right   = -self.sim_output['BX_Lateral_Velocity_Right']
            
            #t_lateral_speed_Right = self.t_Right_C0
            # lateral_speed_Right = self.lateral_speed_Right
            
            delta_t = 1.0
            t_LDW_Right_start = kbtools.GetTRisingEdge(self.t_LDW_Right,self.LDW_Right,(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
            t_supp_start = kbtools.GetTRisingEdge(self.sim_output['t'],self.sim_output['DEBUG_HighLateralVelocity_Right'],(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
      
            
            lateral_speed_Right_at_t_LDW_Right = kbtools.GetPreviousSample(t_lateral_speed_Right,lateral_speed_Right,t_LDW_Right_start,shift=0)
            lateral_speed_Right_at_t_supp_start = kbtools.GetPreviousSample(t_lateral_speed_Right,lateral_speed_Right,t_supp_start,shift=0)
            
            
                       
            # ------------------------------------------------------
            # Lateral_Velocity
            if self.Time_RightLineVelLateral is not None:
                f_RightLineVelLateral = kbtools.smooth_filter(self.Time_RightLineVelLateral, self.RightLineVelLateral, filtertype = 'acausal', valid = np.fabs(self.RightLineVelLateral)< 2.0)
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'c', label='OxTS')
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, f_RightLineVelLateral,'r',label='filtered OxTS')

            if self.Time_Lat_Spd_Rt is not None:
                ax.plot(self.Time_Lat_Spd_Rt-self.t_ref, self.Lat_Spd_Rt_smoothed,'c',label='VBOX_LDWS_VCI')

            ax.plot(t_lateral_speed_Right-self.t_ref, lateral_speed_Right,'b',label='FLC20' )
            
            # ------------------------------
            print "t_LDW_Right_start", t_LDW_Right_start
            print "t_supp_start", t_supp_start
            print "lateral_speed_Right_at_t_LDW_Right", lateral_speed_Right_at_t_LDW_Right
            print "lateral_speed_Right_at_t_supp_start", lateral_speed_Right_at_t_supp_start
            
            warning_is_suppressed = False
            if (t_LDW_Right_start is not None) and (t_supp_start is not None):
                if round(t_LDW_Right_start,2) >= round(t_supp_start,2):
                    warning_is_suppressed = True 
                    
            
            # marker + text
            if t_LDW_Right_start is not None:
                if warning_is_suppressed:
                    label = 'LD Warning suppressed'
                else:
                    label = 'LD Warning issued'
                
                ax.plot(self.t_LDW_Right-self.t_ref, self.LDW_Right*lateral_speed_Right_at_t_LDW_Right,'b--',label=label)
                ax.plot(self.t_LDW_Right_start-self.t_ref, lateral_speed_Right_at_t_LDW_Right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, lateral_speed_Right_at_t_LDW_Right*1.05,"warning @ %3.2f m/s"%lateral_speed_Right_at_t_LDW_Right)
            else:
                ax.plot(self.t_LDW_Left-self.t_ref, self.LDW_Left*0.0,'b--',label='no LD Warning')

                
            if t_supp_start is not None:
                ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Right']*lateral_speed_Right_at_t_supp_start,'r--',label='suppression')
                ax.plot(t_supp_start-self.t_ref, lateral_speed_Right_at_t_supp_start,'cd')
                ax.text(t_supp_start-self.t_ref, lateral_speed_Right_at_t_supp_start*1.10,"suppression @ %3.2f m/s"%lateral_speed_Right_at_t_supp_start)
            else:
                ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Right']*0.0,'r--',label='no suppression')
           
            # ------------------------------
            # threshold
            #ax.hlines(-self.sim_parameters['max_lat_vel']/10.0,local_xlim[0],local_xlim[1],colors='m',linewidth=2, linestyles='dashed',label="threshold (%3.1f m/s)"%(self.sim_parameters['max_lat_vel']/10.0,))
            ax.hlines(-self.sim_parameters['MAX_LAT_VEL'],local_xlim[0],local_xlim[1],colors='m',linewidth=2, linestyles='dashed',label="threshold (%3.1f m/s)"%(self.sim_parameters['MAX_LAT_VEL'],))
                    
            self.set_description(ax,'[m/s]',(-1.6,0.1))  
            
            # --------
            ax = fig.add_subplot(212)
                
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    + 6.0,'b', label='Truck - int Warn (+6)')
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    + 6.0,'r', label='Sim - int Warn (+6)')
            #ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']          + 6.0,'r', label='Sim - isWarnLeft (+6)')
            
            ax.plot(self.sim_input['t_rel'],  (self.sim_input['BX_LDW_Suppr']>0)             + 4.0,'b', label='Truck - supp. active (+4)')
            ax.plot(self.sim_output['t_rel'], (self.sim_output['BX_Warning_Suppression']>0)  + 4.0,'r', label='Sim - supp. active (+4)')
        
            ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       + 2.0,'b', label='Truck - Imminent(+2)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']  + 2.0,'r', label='Sim - Imminent (+2)')

            ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningRight']             ,'b', label='Truck - Acoustical')
            ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Right']     ,'r', label='Sim - Acoustical')
  
            
            ax.set_yticks(np.arange(0,7)) 
            ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On'])
 
            self.set_description(ax,'',(-0.1,8.1))  
            
                
    
            ax.set_xlabel('time [s] (t_ref=%3.2f s)'%self.t_ref)
 
            self.show_and_save_figure()
    
            
        # --------------------------------------------------------
        if self.LDW_Left_okay:
        
            PlotName = PlotName + '_left'
            fig = self.start_fig(PlotName, FigNr)

            ax = fig.add_subplot(211)
            if self.FrontAxleSpeed_at_t_LDW_Left is not None:
                ax.set_title('Left side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Left*3.6,))
            else:
                ax.set_title('Left side')

            local_xlim = self.xlim_closeup
            local_xlim = (-1.0,2.0)
            
            self.xlim_to_use(local_xlim)
            
            t_lateral_speed_Left = self.sim_output['t']
            lateral_speed_Left   = self.sim_output['BX_Lateral_Velocity_Left']
            
            #t_lateral_speed_Left = self.t_Left_C0
            # lateral_speed_Left = self.lateral_speed_Left
            
            delta_t = 1.0
            t_LDW_Left_start = kbtools.GetTRisingEdge(self.t_LDW_Left,self.LDW_Left,(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
            t_supp_start = kbtools.GetTRisingEdge(self.sim_output['t'],self.sim_output['DEBUG_HighLateralVelocity_Left'],(self.t_event-delta_t),(self.t_event+delta_t),shift=0)
      
            
            lateral_speed_Left_at_t_LDW_Left = kbtools.GetPreviousSample(t_lateral_speed_Left,lateral_speed_Left,t_LDW_Left_start,shift=0)
            lateral_speed_Left_at_t_supp_start = kbtools.GetPreviousSample(t_lateral_speed_Left,lateral_speed_Left,t_supp_start,shift=0)
            
                       
            # ------------------------------------------------------
            # Lateral_Velocity
            if self.Time_LeftLineVelLateral is not None:
                f_LeftLineVelLateral = kbtools.smooth_filter(self.Time_LeftLineVelLateral, self.LeftLineVelLateral, filtertype = 'acausal', valid = np.fabs(self.LeftLineVelLateral)< 2.0)
            
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral,'c', label='OxTS')
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, f_LeftLineVelLateral,'r',label='filtered OxTS')

            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.Time_Lat_Spd_Lt-self.t_ref, self.Lat_Spd_Lt_smoothed,'c',label='VBOX_LDWS_VCI')

            ax.plot(t_lateral_speed_Left-self.t_ref, lateral_speed_Left,'b',label='FLC20' )
            
            # ------------------------------
            print "t_LDW_Left_start", t_LDW_Left_start
            print "t_supp_start", t_supp_start
            
            warning_is_suppressed = False
            if (t_LDW_Left_start is not None) and (t_supp_start is not None):
                if round(t_LDW_Left_start,2) >= round(t_supp_start,2):
                    warning_is_suppressed = True 
                    
            
            # marker + text
            if t_LDW_Left_start is not None:
                if warning_is_suppressed:
                    label = 'LD Warning suppressed'
                else:
                    label = 'LD Warning issued'
                
                ax.plot(self.t_LDW_Left-self.t_ref, self.LDW_Left*lateral_speed_Left_at_t_LDW_Left,'b--',label=label)
                ax.plot(self.t_LDW_Left_start-self.t_ref, lateral_speed_Left_at_t_LDW_Left,'md')
                ax.text(self.t_LDW_Left_start-self.t_ref, lateral_speed_Left_at_t_LDW_Left*1.05,"warning @ %3.2f m/s"%lateral_speed_Left_at_t_LDW_Left)
            else:
                ax.plot(self.t_LDW_Left-self.t_ref, self.LDW_Left*0.0,'b--',label='no LD Warning')

                
            if t_supp_start is not None:
                ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Left']*lateral_speed_Left_at_t_supp_start,'r--',label='suppression')
                ax.plot(t_supp_start-self.t_ref, lateral_speed_Left_at_t_supp_start,'cd')
                ax.text(t_supp_start-self.t_ref, lateral_speed_Left_at_t_supp_start*1.10,"suppression @ %3.2f m/s"%lateral_speed_Left_at_t_supp_start)
            else:
                ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighLateralVelocity_Left']*0.0,'r--',label='no suppression')
           
            # ------------------------------
            # threshold
            #ax.hlines(self.sim_parameters['max_lat_vel']/10.0,local_xlim[0],local_xlim[1],colors='m',linewidth=2, linestyles='dashed',label="threshold (%3.1f m/s)"%(self.sim_parameters['max_lat_vel']/10.0,))
            ax.hlines(self.sim_parameters['MAX_LAT_VEL'],local_xlim[0],local_xlim[1],colors='m',linewidth=2, linestyles='dashed',label="threshold (%3.1f m/s)"%(self.sim_parameters['MAX_LAT_VEL'],))
          
            self.set_description(ax,'[m/s]',(-0.1,1.6))  
                
            # --------
            ax = fig.add_subplot(212)
                
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    + 6.0,'b', label='Truck - int Warn (+6)')
            ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    + 6.0,'r', label='Sim - int Warn (+6)')
            #ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']          + 6.0,'r', label='Sim - isWarnLeft (+6)')
            
            ax.plot(self.sim_input['t_rel'],  (self.sim_input['BX_LDW_Suppr']>0)             + 4.0,'b', label='Truck - supp. active (+4)')
            ax.plot(self.sim_output['t_rel'], (self.sim_output['BX_Warning_Suppression']>0)  + 4.0,'r', label='Sim - supp. active (+4)')
        
            ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       + 2.0,'b', label='Truck - Imminent(+2)')
            ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']  + 2.0,'r', label='Sim - Imminent (+2)')

            ax.plot(self.sim_input['t_rel'],  self.sim_input['AcousticalWarningLeft']             ,'b', label='Truck - Acoustical')
            ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Acoustical_State_Left']     ,'r', label='Sim - Acoustical')
  
            
            ax.set_yticks(np.arange(0,7)) 
            ax.set_yticklabels(['Off','On','Off','On','Off','On','Off','On'])
 
            self.set_description(ax,'',(-0.1,8.1))  

                
            ax.set_xlabel('time [s] (t_ref=%3.2f s)'%self.t_ref)

            self.show_and_save_figure()

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_HIGH_STEERING_RATE(self,FigNr = 180):
        
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.A_supp_HIGH_STEERING_RATE", FigNr)
        
        # ------------------------------------------------------
        ax = fig.add_subplot(511)
        self.plot_isWarning(ax)

        # ------------------------------------------------------
        # Steering_Wheel_Angle_Input
        ax = fig.add_subplot(512)
        ax.plot(self.sim_input['t_rel'], self.sim_input['Steering_Wheel_Angle_Input']*180.0/np.pi,'b',label='Steering_Wheel_Angle_Input' )
        #ax.plot(self.sim_input['Time_J1939_SteerWhlAngle']-self.t_ref, self.sim_input['J1939_SteerWhlAngle']*180.0/np.pi,'r',label='J1939_SteerWhlAngle' )
        
        self.set_description(ax,'[degree]',None) 

        # ------------------------------------------------------
        # angle rate
        ax = fig.add_subplot(513)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_angle_rate']*180.0/np.pi,'r',label='Sim - raw angle rate' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_angle_rate_filtered']*180.0/np.pi,'b',label='Sim - filt. angle rate' )
              
        T = 0.25
        fd_J1939_SteerWhlAngle, f_J1939_SteerWhlAngle = kbtools.svf_1o(self.sim_input['Time_J1939_SteerWhlAngle'], self.sim_input['J1939_SteerWhlAngle'],T)
        ax.plot(self.sim_input['Time_J1939_SteerWhlAngle']-self.t_ref, -fd_J1939_SteerWhlAngle*180.0/np.pi,'m-',label='(-1)*filt. angle rate' )
        

        self.set_description(ax,'[degree/s]',(-100.0,100.0)) 
        

        # ------------------------------------------------------
        # DEBUG_HighSteerAngleRate
        ax = fig.add_subplot(514)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_HighSteerAngleRate'],'r',label='Sim - HighSteerAngleRate' )
        self.set_description(ax,'flag',(-0.1,1.1) ) 
     
        # ------------------------------------------------------
        # BX_LDW_Suppr_HIGH_STEERING_RATE
        ax = fig.add_subplot(515)
        
        ax.plot(self.sim_input['t_rel'], (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0200)>0) +2.0,'b',label='Truck')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0200)>0),'r',label='Sim') 
        self.set_description(ax,'supp. HIGH_STEERING_RATE',(-0.1, 4.1) ) 
       
        ax.set_xlabel('time [s]')
      
        self.show_and_save_figure()

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_supp_HIGH_STEERING_RATE_rapid_prototyping(self,FigNr = 181):
        
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_9.A_supp_HIGH_STEERING_RATE_rapid_prototyping", FigNr)
        
        
        t_SteerWhlAngle = self.sim_input['Time_J1939_SteerWhlAngle']      
        SteerWhlAngle   = self.sim_input['J1939_SteerWhlAngle']      
              
              
        T = 1.0
        LPF_SteerWhlAngle = kbtools.pt1_filter(t_SteerWhlAngle, SteerWhlAngle,T)
        
        
        HPF_SteerWhlAngle = SteerWhlAngle- LPF_SteerWhlAngle

        Gradient_SteerWhlAngle = kbtools.ugdiff(t_SteerWhlAngle, SteerWhlAngle, verfahren=1)
        
        Delta_threshold = 20.0
        Gradient_threshold = 40.0
        
        Delta_flag    = np.fabs(HPF_SteerWhlAngle)>(Delta_threshold*np.pi/180.0)
        Gradient_flag = np.fabs(Gradient_SteerWhlAngle)>(Gradient_threshold*np.pi/180.0)
        
        Combined_flag = np.logical_and(Delta_flag, Gradient_flag)
        
        T_monostable_multivibrator = 1.5
        Supp_flag = kbtools.monostable_multivibrator(t_SteerWhlAngle,Combined_flag,T_monostable_multivibrator)
        
        # ------------------------------------------------------
        ax = fig.add_subplot(511)
        self.plot_isWarning(ax)

        # ------------------------------------------------------
        # Lateral velocity
        ax = fig.add_subplot(512)
        if self.sim_input['Time_RightLineVelLateral'] is not None:
            ax.plot(self.sim_input['Time_RightLineVelLateral']-self.t_ref, self.sim_input['RightLineVelLateral'],'r',label='OxTS right' )
        if self.sim_input['Time_LeftLineVelLateral'] is not None:
           ax.plot(self.sim_input['Time_LeftLineVelLateral']-self.t_ref, self.sim_input['LeftLineVelLateral'],'b',label='OxTS left' )
     
        ax.plot(self.sim_output['t_rel'], -self.sim_output['BX_Lateral_Velocity_Right'],'m',label='FLC20 right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_Lateral_Velocity_Left'],'c',label='FLC20 left' )
             
        self.set_description(ax,'[m/s]',(-2.1,2.1)) 

        # ------------------------------------------------------
        # Lateral velocity
        #ax = fig.add_subplot(613)
        #ax.plot(self.sim_input['Time_YawRate']-self.t_ref, self.sim_input['YawRate'],'r',label='J1939 YawRate' )
             
        #self.set_description(ax,'[rad/s]',None ) 

             
            
        
        # ------------------------------------------------------
        # Steering_Wheel_Angle_Input
        ax = fig.add_subplot(513)
        #ax.plot(self.sim_input['t_rel'], self.sim_input['Steering_Wheel_Angle_Input']*180.0/np.pi,'b',label='Steering_Wheel_Angle_Input' )
        ax.plot(self.sim_input['Time_J1939_SteerWhlAngle']-self.t_ref, self.sim_input['J1939_SteerWhlAngle']*180.0/np.pi,'r',label='J1939_SteerWhlAngle' )
        ax.plot(t_SteerWhlAngle-self.t_ref, HPF_SteerWhlAngle*180.0/np.pi,'b',label='Delta' )
        
        ax.hlines(Delta_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label="Delta_threshold")
        ax.hlines(-Delta_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label=None)
     
        
        self.set_description(ax,'[degree]',(-110.0,110.0)) 

        # ------------------------------------------------------
        # angle rate
        ax = fig.add_subplot(514)
        ax.plot(self.sim_output['t_rel'], -self.sim_output['DEBUG_angle_rate']*180.0/np.pi,'r',label='Sim - raw angle rate' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Gradient_SteerWhlAngle*180.0/np.pi,'b',label='gradient' )
        ax.hlines(Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label="Gradient_threshold")
        ax.hlines(-Gradient_threshold,self._xlim_to_use[0],self._xlim_to_use[1],colors='k',linestyles='dashed',label=None)
              
        self.set_description(ax,'[degree/s]',(-250.0,250.0)) 
        

        # ------------------------------------------------------
        # DEBUG_HighSteerAngleRate
        ax = fig.add_subplot(515)
        
              
        ax.plot(t_SteerWhlAngle-self.t_ref, Delta_flag    +6.0,'b', label='Delta_flag (+4)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Gradient_flag +4.0,'r', label='Gradient_flag (+2)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Combined_flag +2.0,'g', label='Combined_flag (+2)' )
        ax.plot(t_SteerWhlAngle-self.t_ref, Supp_flag,'k',          label='Supp_flag' )
        
        
        
        self.set_description(ax,'flags',(-0.1, 8.1 ) )
            
        ax.set_xlabel('time [s]')
      
        self.show_and_save_figure()


    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cmp_ME_LNVU_TLC_new(self,FigNr = 180, xlim=None):
         
        # Time Based        
        
        if xlim is not None:
            self.xlim_to_use(xlim)
        else:
            self.xlim_to_use(self.xlim_default)

        
        
        t_Left_C0,  RefTLC_Left  = self.calc_RefTLC_Left()
        t_Right_C0, RefTLC_Right = self.calc_RefTLC_Right()
        
        # return (uint8_t)(((WarnNow[BX_RIGHT] << 1) & 0x02) | (WarnNow[BX_LEFT] & 0x01));
        DEBUG_WarnNowLeft  = np.bitwise_and(self.sim_output['DEBUG_WarnNow'].astype(int),0x1)>0
        DEBUG_WarnNowRight = np.bitwise_and(self.sim_output['DEBUG_WarnNow'].astype(int),0x2)>0
        
        
        '''         
           
            F["Time_LNVU_AlgoState"],F["LNVU_AlgoState"]           = kbtools.GetSignal(Source, "Bendix_Info3", "LNVU_AlgoState")

            F["Time_TLC_thresh_right_ms"],F["TLC_thresh_right_ms"] = kbtools.GetSignal(Source, "Bendix_Info3", "TLC_thresh_right_ms")
            F["Time_TLC_thresh_left_ms"], F["TLC_thresh_left_ms"]  = kbtools.GetSignal(Source, "Bendix_Info3", "TLC_thresh_left_ms")

            F["Time_D_margin_right_mm"], F["D_margin_right_mm"]    = kbtools.GetSignal(Source, "Bendix_Info3", "D_margin_right_mm")
            F["Time_D_margin_left_mm"], F["D_margin_left_mm"]      = kbtools.GetSignal(Source, "Bendix_Info3", "D_margin_left_mm")

        '''
 
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_A.1_cmp_ME_LNVU_TLC", FigNr)
    
       
        # ------------------------------------------------------
        # Warnings Left
        ax = fig.add_subplot(611)
        ax.plot(self.sim_input['t_rel'],              self.sim_input['ME_LDW_LaneDeparture_Left']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'],             self.sim_output['WARN_isWarningLeft'],          'rx-',label='SIM - isWarn')
        ax.plot(self.sim_input['t_rel_BxInfo'],       self.sim_input['COMPARE_LNVU_isWarningLeft'],   'bx-',label='FLC - isWarn')
        #ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay'],           'mx-',label='delay')
        
        self.set_description(ax,'Left',(-0.1, 4.1) ) 

        # ------------------------------------------------------
        # TLC  DEBUG_BX_Warn_TLC_Left
        ax = fig.add_subplot(612)
        #ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_Warn_TLC_Left'], 'r',label='DEBUG_BX_Warn_TLC_Left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TimeToLC_left'],    'g',label='DEBUG_TimeToLC_left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLC_thresh_left'],  'b',label='DEBUG_TLC_thresh_left' )        
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft'],     'm',label='WARN_isWarningLeft' )
        ax.plot(self.sim_output['t_rel'], DEBUG_WarnNowLeft,     'c',label='DEBUG_WarnNowLeft' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLCreset_left'],     'k',label='DEBUG_TLCreset_left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_min_TLC'],     'y',label='DEBUG_min_TLC' )
        self.set_description(ax,'Left [s]',(-0.2,1.1))

        print "self.sim_output['DEBUG_min_TLC']", self.sim_output['DEBUG_min_TLC']
        
        # ------------------------------------------------------
        # Warnings Right
        ax = fig.add_subplot(613)
        ax.plot(self.sim_input['t_rel'],        self.sim_input['ME_LDW_LaneDeparture_Right']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'],       self.sim_output['WARN_isWarningRight'],          'r',label='SIM - isWarn ')
        ax.plot(self.sim_input['t_rel_BxInfo'], self.sim_input['COMPARE_LNVU_isWarningRight'],   'bx-',label='FLC - isWarn')
        #ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay'],           'mx-',label='delay')
        self.set_description(ax,'Right',(-0.1, 4.1) )
        
        # ------------------------------------------------------
        # TLC DEBUG_BX_Warn_TLC_Right
        ax = fig.add_subplot(614)
        #ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_Warn_TLC_Right'],'r',label='DEBUG_BX_Warn_TLC_Right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TimeToLC_right'],    'g',label='DEBUG_TimeToLC_right' )
        #ax.plot(t_Right_C0, RefTLC_Right, 'g',label='RefTLC_Right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLC_thresh_right'], 'b',label='DEBUG_TLC_thresh_right' )    
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight'],    'm',label='WARN_isWarningRight' )
        ax.plot(self.sim_output['t_rel'], DEBUG_WarnNowRight,     'c',label='DEBUG_WarnNowRight' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLCreset_right'],     'k',label='DEBUG_TLCreset_right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_min_TLC'],     'y',label='DEBUG_min_TLC' )
        self.set_description(ax,'Right [s]',(-0.2,1.1))
           
        # ------------------------------------------------------
        # DEBUG_space
        ax = fig.add_subplot(615)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_space'],         'r',label='SIM - space')
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_Space']/1000.0 ,'b',label='FLC - space ')
        self.set_description(ax,'[m]',(-0.1, 3.5) )
     
        # ------------------------------------------------------
        # DEBUG_TimeBased_flag
        ax = fig.add_subplot(616)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_TimeBased_flag'],      'r',label='SIM - TimeBased_flag' )
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_LNVU_TimeBased_flag'],'b',label='FLC - DEBUG_TimeBased_flag')
        self.set_description(ax,'[flag]',(-0.1,1.1))

        '''        
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Left, DEBUG_cut_margin_mm_Right
        ax = fig.add_subplot(514)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Left']          ,'r' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Right']          ,'b' )
        #ax.set_ylim(-0.1,4.1) 
        ax.set_ylabel('m')
        ax.legend(('DEBUG_cut_margin_mm_Left','DEBUG_cut_margin_mm_Right'))
        self.set_xlim(ax)
        '''
     
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
        
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cmp_ME_LNVU_TLC(self,FigNr = 180, xlim=None):
         
        # Time Based        
        
        if xlim is not None:
            self.xlim_to_use(xlim)
        else:
            self.xlim_to_use(self.xlim_default)

        
        
        t_Left_C0,  RefTLC_Left  = self.calc_RefTLC_Left()
        t_Right_C0, RefTLC_Right = self.calc_RefTLC_Right()
        

        '''         
           
            F["Time_LNVU_AlgoState"],F["LNVU_AlgoState"]           = kbtools.GetSignal(Source, "Bendix_Info3", "LNVU_AlgoState")

            F["Time_TLC_thresh_right_ms"],F["TLC_thresh_right_ms"] = kbtools.GetSignal(Source, "Bendix_Info3", "TLC_thresh_right_ms")
            F["Time_TLC_thresh_left_ms"], F["TLC_thresh_left_ms"]  = kbtools.GetSignal(Source, "Bendix_Info3", "TLC_thresh_left_ms")

            F["Time_D_margin_right_mm"], F["D_margin_right_mm"]    = kbtools.GetSignal(Source, "Bendix_Info3", "D_margin_right_mm")
            F["Time_D_margin_left_mm"], F["D_margin_left_mm"]      = kbtools.GetSignal(Source, "Bendix_Info3", "D_margin_left_mm")

        '''
 
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_A.1_cmp_ME_LNVU_TLC", FigNr)
    
       
        # ------------------------------------------------------
        # Warnings Left
        ax = fig.add_subplot(611)
        ax.plot(self.sim_input['t_rel'],              self.sim_input['ME_LDW_LaneDeparture_Left']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'],             self.sim_output['WARN_isWarningLeft'],          'rx-',label='SIM - isWarn')
        ax.plot(self.sim_input['t_rel_BxInfo'],       self.sim_input['COMPARE_LNVU_isWarningLeft'],   'bx-',label='FLC - isWarn')
        #ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay'],           'mx-',label='delay')
        
        self.set_description(ax,'Left',(-0.1, 4.1) ) 

        # ------------------------------------------------------
        # TLC  DEBUG_BX_Warn_TLC_Left
        ax = fig.add_subplot(612)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_Warn_TLC_Left'], 'r',label='DEBUG_BX_Warn_TLC_Left' )
        ax.plot(t_Left_C0, RefTLC_Left, 'g',label='RefTLC_Left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLC_thresh_left'],  'b',label='DEBUG_TLC_thresh_left' )        
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft'],     'm',label='WARN_isWarningLeft' )
        self.set_description(ax,'Left [s]',(-0.1,1.1))

        # ------------------------------------------------------
        # Warnings Right
        ax = fig.add_subplot(613)
        ax.plot(self.sim_input['t_rel'],        self.sim_input['ME_LDW_LaneDeparture_Right']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'],       self.sim_output['WARN_isWarningRight'],          'r',label='SIM - isWarn ')
        ax.plot(self.sim_input['t_rel_BxInfo'], self.sim_input['COMPARE_LNVU_isWarningRight'],   'bx-',label='FLC - isWarn')
        #ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay'],           'mx-',label='delay')
        self.set_description(ax,'Right',(-0.1, 4.1) )
        
        # ------------------------------------------------------
        # TLC DEBUG_BX_Warn_TLC_Right
        ax = fig.add_subplot(614)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_Warn_TLC_Right'],'r',label='DEBUG_BX_Warn_TLC_Right' )
        ax.plot(t_Right_C0, RefTLC_Right, 'g',label='RefTLC_Right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLC_thresh_right'], 'b',label='DEBUG_TLC_thresh_right' )    
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight'],    'm',label='WARN_isWarningRight' )
        self.set_description(ax,'Right [s]',(-0.1,1.1))
           
        # ------------------------------------------------------
        # DEBUG_space
        ax = fig.add_subplot(615)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_space'],         'r',label='SIM - space')
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_Space']/1000.0 ,'b',label='FLC - space ')
        self.set_description(ax,'[m]',(-0.1, 3.5) )
     
        # ------------------------------------------------------
        # DEBUG_TimeBased_flag
        ax = fig.add_subplot(616)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_TimeBased_flag'],      'r',label='SIM - TimeBased_flag' )
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_LNVU_TimeBased_flag'],'b',label='FLC - DEBUG_TimeBased_flag')
        self.set_description(ax,'[flag]',(-0.1,1.1))

        '''        
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Left, DEBUG_cut_margin_mm_Right
        ax = fig.add_subplot(514)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Left']          ,'r' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Right']          ,'b' )
        #ax.set_ylim(-0.1,4.1) 
        ax.set_ylabel('m')
        ax.legend(('DEBUG_cut_margin_mm_Left','DEBUG_cut_margin_mm_Right'))
        self.set_xlim(ax)
        '''
     
        ax.set_xlabel('time [s]')

        # ------------------------------------------------------
        self.show_and_save_figure()
        
    # ===========================================================================
    def plot_2_lane_TLC(self,PlotName = 'plot_2_lane_TLC',customer_version=False,xlim=None):
        
        if self.verbose:
            print "plot_2_lane_TLC()"
            print "input_mode", self.input_mode
           
        if not customer_version:
            PlotName = PlotName + '_internal'
    
        if xlim is not None:
            PlotName = PlotName + '_zoom'
            self.xlim_to_use(xlim)
            local_xlim = xlim
        else:
            self.xlim_to_use(self.xlim_default)
            # plot range:  pre_trigger .. t_ref .. post_trigger
            local_xlim = self.xlim_closeup
            

        local_xlim = (-1.5,0.5)    
            
        warn_zone_inner = 0.0
        warn_zone_outer = self.corridor_outer_boundary/100.0

        #reset_zone_inner = -0.02
        #reset_zone_outer =  0.15

        reset_zone_inner = -0.15
        reset_zone_outer =  0.02
        
        if customer_version:
            x_mark = ''
        else:
            x_mark = 'x-'
            x_mark = ''
        
        diff_t = np.diff(self.sim_input['t_videopacket'])
        t_abst_delta = diff_t.max()-diff_t.min()
        t_abst = np.mean(diff_t)
        print "t_videopacket mean,max,min", t_abst, diff_t.max(), diff_t.min(), t_abst_delta
        
        
        # --------------------------------------------------------
        if self.LDW_Right_okay:
            PlotName = PlotName + '_right'
            fig = self.start_fig(PlotName, FigNr=210)
            
            ax = fig.add_subplot(411)
            if self.FrontAxleSpeed_at_t_LDW_Right is not None:
                ax.set_title('Right side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Right*3.6,))
            else:
                ax.set_title('Right side')

            

            # --------------------------------
            # lines
            # OxTS - Ford
            if self.Time_RightLinePosLateral is not None:
                ax.plot(self.Time_RightLinePosLateral-self.t_ref, self.RightLinePosLateral-self.WheelRight,'r', label='OxTS (%5.2f m)'%(self.RightLinePosLateral_at_t_LDW_Right-self.WheelRight,))
            # Racelogic
            if self.Time_Range_Rt is not None:
                ax.plot(self.Time_Range_Rt-self.t_ref, self.Range_Rt-self.WheelRight,'r',label='VBOX_LDWS_VCI (%5.2f m)'%(self.Range_Rt_at_t_LDW_Right-self.WheelRight,))
            if customer_version or self.show_C0:
                ax.plot(self.t_Right_C0-self.t_ref,    self.Right_C0-self.WheelRight,'b'+x_mark,label='FLC20 C0 (%5.2f m)'%(self.Right_C0_at_t_LDW_Right-self.WheelRight,))
                VehicleWidth = (self.sim_parameters['EOLDistToRtWheel'] + self.sim_parameters['EOLDistToLtWheel'])/100.0
                VehicleWidthHalf = VehicleWidth/2.0
                print "VehicleWidthHalf", VehicleWidthHalf
                
                # simulated outputs are delay by one cycle (0.005)
                BX_laneOffset_Right_samples = kbtools.resample(self.sim_output['t']-0.01, self.sim_output['BX_laneOffset_Right'],self.sim_input['t_videopacket'])
                
                ax.plot(self.sim_output['t_rel'], self.sim_output['BX_laneOffset_Right']-VehicleWidthHalf,'m',label='BX_laneOffset_Right')
                ax.plot(self.sim_input['t_rel_videopacket'], BX_laneOffset_Right_samples-VehicleWidthHalf,'x-')
                # 
                ax.plot( self.FLR20_sig['FLC20_CAN']["Time_C0_Right"]-self.t_ref, self.FLR20_sig['FLC20_CAN']["C0_Right"]-self.WheelRight,'yx-')
 
                t_BX_laneOffset_Right_samples_around, BX_laneOffset_Right_samples_around = kbtools.GetSampleAround(self.sim_input['t_videopacket'],BX_laneOffset_Right_samples,self.t_LDW_Right_start, shift=-2)       
                
                print "t_LDW_Right_start", self.t_LDW_Right_start
                print "t_BX_laneOffset_Right_samples_around, BX_laneOffset_Right_samples_around", t_BX_laneOffset_Right_samples_around, BX_laneOffset_Right_samples_around
                print "t_BX_laneOffset_Right_samples_around", t_BX_laneOffset_Right_samples_around[1] - t_BX_laneOffset_Right_samples_around[0]
                print "BX_laneOffset_Right_samples_around", BX_laneOffset_Right_samples_around[1] - BX_laneOffset_Right_samples_around[0]
                
                for k in [0,1]:
                    ax.plot(t_BX_laneOffset_Right_samples_around[k]-self.t_ref, BX_laneOffset_Right_samples_around[k]-VehicleWidthHalf,'rd')
                    ax.text(t_BX_laneOffset_Right_samples_around[k]-self.t_ref, BX_laneOffset_Right_samples_around[k]-VehicleWidthHalf,"%3.2f m"%(BX_laneOffset_Right_samples_around[k]-VehicleWidthHalf,))
   
           
           

            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_C0_right_wheel-self.t_ref, self.C0_right_wheel,'m'+x_mark,label='FLC20 C0 wheel')
                
               
 
 
            # --------------------------------
            # zones 
            #ax.hlines(-warn_zone_outer,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            #ax.hlines(-warn_zone_inner,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            #ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(-warn_zone_inner,warn_zone_inner-warn_zone_outer),alpha=.1, facecolors='red')
  
            if 0:
                ax.hlines(-reset_zone_outer,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.hlines(-reset_zone_inner,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(-reset_zone_inner,reset_zone_inner-reset_zone_outer),alpha=.1, facecolors='blue')

            # --------------------------------
            # Warning Line
            print "WARN_MARGIN_RIGHT", self.sim_parameters['WARN_MARGIN_RIGHT'] 
            self.WarningLineRight = -self.sim_parameters['WARN_MARGIN_RIGHT']
            
            ax.hlines(self.WarningLineRight,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineRight)
              
            TLC_shift = self.sim_output['BX_Lateral_Velocity_Right']*self.sim_output['DEBUG_TLC_thresh_right']+self.WarningLineRight
       
            TLC_shift_at_t_LDW_Right = kbtools.GetPreviousSample(self.sim_output['t'],TLC_shift,self.t_LDW_Right_start)
           
       
            ax.plot(self.sim_output['t_rel'], TLC_shift,'r',label="TLC_shift %3.2f m"%TLC_shift_at_t_LDW_Right)
            if TLC_shift_at_t_LDW_Right is not None:
                ax.plot(self.t_LDW_Right_start-self.t_ref, TLC_shift_at_t_LDW_Right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, TLC_shift_at_t_LDW_Right,"%3.2f m"%TLC_shift_at_t_LDW_Right)
   
       
       
            # ----------------------------------        
            # marker + text
        
            # start: Right_C0-WheelRight
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,'md')
                #ax.text(t_LDW_Right_start-t_ref, Right_C0_at_t_LDW_Right+right_wheel,"  %5.2f m @ %3.2f m/s"%(Right_C0_at_t_LDW_Right+right_wheel,slope))
                actual_TLC = (self.Right_C0_at_t_LDW_Right-self.WheelRight-self.WarningLineRight)/(-self.lateral_speed_Right_at_t_LDW_Right)
                if customer_version:
                    ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,"  %5.2f m"%(self.Right_C0_at_t_LDW_Right-self.WheelRight,))
                else:
                    ax.text(self.t_LDW_Right_start-self.t_ref, self.Right_C0_at_t_LDW_Right-self.WheelRight,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.Right_C0_at_t_LDW_Right-self.WheelRight,abs(self.lateral_speed_Right_at_t_LDW_Right),actual_TLC))

            if not customer_version and self.show_C0_wheel:
                # start: C0_right_wheel
                ax.plot(self.t_LDW_Right_start-self.t_ref, self.C0_right_wheel_at_t_LDW_Right,'md')
                actual_TLC = (self.C0_right_wheel_at_t_LDW_Right-self.WarningLineRight)/(-self.lateral_speed_Right_at_t_LDW_Right)
                ax.text(self.t_LDW_Right_start-self.t_ref, self.C0_right_wheel_at_t_LDW_Right,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.C0_right_wheel_at_t_LDW_Right,abs(self.lateral_speed_Right_at_t_LDW_Right),actual_TLC))
             
            # stop: Right_C0_at_t_LDW_Right_stop-WarningLine_Right      
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,'ms')
                ax.text(self.t_LDW_Right_stop-self.t_ref, self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,"  %5.2f m"%(self.Right_C0_at_t_LDW_Right_stop-self.WheelRight,))

            if not customer_version and self.show_C0_wheel:
                # stop: C0_right_wheel_at_t_LDW_Right_stop
                ax.plot(self.t_LDW_Right_stop-self.t_ref, self.C0_right_wheel_at_t_LDW_Right_stop,'ms')
                ax.text(self.t_LDW_Right_stop-self.t_ref, self.C0_right_wheel_at_t_LDW_Right_stop,"  %5.2f m"%(self.C0_right_wheel_at_t_LDW_Right_stop,))
  
            ylim_local = (-0.1+self.WarningLineRight, self.WarningLineRight + 0.1)
            ylim_local = (min(self.Right_C0_at_t_LDW_Right-self.WheelRight-0.1,ylim_local[0]),max(self.Right_C0_at_t_LDW_Right-self.WheelRight+0.1,ylim_local[1]))

  
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

            if (not customer_version) or (self.Time_RightLinePosLateral is not None) or (self.Time_Range_Rt is not None):
                ax.legend()
        
            ax.set_ylabel('outer <--right line [m] --> inner')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(412)
    
            # lines
            if self.Time_RightLineVelLateral is not None:
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral,'y', label='OxTS (raw)')
                ax.plot(self.Time_RightLineVelLateral-self.t_ref, self.RightLineVelLateral_smoothed,'r', label='OxTS (%3.2f m/s)'%(self.RightLineVelLateral_smoothed_at_t_LDW_Right,))
            
            if self.Time_Lat_Spd_Rt is not None:
                ax.plot(self.Time_Lat_Spd_Rt-self.t_ref, self.Lat_Spd_Rt_smoothed,'r',label='VBOX_LDWS_VCI (%3.2f m/s)'%(self.Lat_Spd_Rt_smoothed_at_t_LDW_Right,))
               
                
            ax.plot(self.t_Right_C0-self.t_ref, self.lateral_speed_Right,'b',label='FLC20 (%3.2f m/s)'%(self.lateral_speed_Right_at_t_LDW_Right,))
           
            # marker + text
            ax.plot(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,'md')
            ax.text(self.t_LDW_Right_start-self.t_ref, self.lateral_speed_Right_at_t_LDW_Right,"%3.2f m/s"%self.lateral_speed_Right_at_t_LDW_Right)
   
            #ax.plot(t_LDW_Left_start-t_ref, lateral_speed_Left_at_t_LDW_Left,'md')
            #ax.text(t_LDW_Left_start-t_ref, lateral_speed_Left_at_t_LDW_Left,"%3.2f m/s"%lateral_speed_Left_at_t_LDW_Left)
            ax.set_ylabel('lateral speed [m/s]')
            if (not customer_version) or (self.Time_RightLineVelLateral is not None) or (self.Time_Lat_Spd_Rt is not None):
                ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-2.1, 2.1)
            ax.grid()        
        
        
            # ------------------------------------------------------
            # TLC DEBUG_BX_Warn_TLC_Right
            ax = fig.add_subplot(413)
            
            DEBUG_BX_Warn_TLC_Right_at_t_LDW_Right = kbtools.GetPreviousSample(self.sim_output['t'],self.sim_output['DEBUG_BX_Warn_TLC_Right'],self.t_LDW_Right_start)
           
            
            ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_Warn_TLC_Right'],'r',label='DEBUG_BX_Warn_TLC_Right' )
            ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_TLC_thresh_right'], 'b',label='DEBUG_TLC_thresh_right' )    
            #ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight'],    'm',label='WARN_isWarningRight' )
            
            if DEBUG_BX_Warn_TLC_Right_at_t_LDW_Right is not None:
                ax.plot(self.t_LDW_Right_start-self.t_ref, DEBUG_BX_Warn_TLC_Right_at_t_LDW_Right,'md')
                ax.text(self.t_LDW_Right_start-self.t_ref, DEBUG_BX_Warn_TLC_Right_at_t_LDW_Right,"%3.2f s"%DEBUG_BX_Warn_TLC_Right_at_t_LDW_Right)
   
            
            ax.set_xlim(local_xlim)
            ax.set_ylim(-0.1,0.3)
            ax.grid()  
            ax.legend()
                 
        
            # --------------------------------------------------------
            # warnings + tracking
            ax = fig.add_subplot(414)
            
            
            
            if customer_version:
                if self.t_WARN_isWarningRight is not None:
                    ax.plot(self.t_WARN_isWarningRight-self.t_ref,    self.WARN_isWarningRight       +6.0,'m', label='LD w/o supp.')
                ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight   +4.0,'b', label='LD Imminent')
                ax.plot(self.t_AcousticalWarningRight-self.t_ref,     self.AcousticalWarningRight    +2.0,'r', label='AcousticalWarning')
                ax.plot(self.t_LDW_Right_Tracking-self.t_ref,         self.LDW_Right_Tracking            ,'k', label='Tracking ')
                ax.set_ylim(-0.1, 7.1)
                ax.legend()
                #ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,9)) 
                ax.set_yticklabels(['Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LD w/o supp. - On'])
            
            else:
                ax.plot(self.t_ME_LDW_LaneDeparture_Right-self.t_ref, self.ME_LDW_LaneDeparture_Right+10.0,'r', label='ME LD (w/o supp) (+10)')
                if self.t_WARN_isWarningRight is not None:
                    ax.plot(self.t_WARN_isWarningRight-self.t_ref,        self.WARN_isWarningRight       + 8.0,'k', label='LNVU LD (w/o supp) (+8)')
                ax.plot(self.t_LaneDepartImminentRight-self.t_ref,    self.LaneDepartImminentRight   + 6.0,'b', label='LD Imminent (+6)')
                ax.plot(self.t_AcousticalWarningRight-self.t_ref,     self.AcousticalWarningRight    + 4.0,'m', label='AcousticalWarning (+4)')
                ax.plot(self.t_LDW_Right_Tracking-self.t_ref,         self.LDW_Right_Tracking        + 2.0,'c', label='Tracking (+2)')
                if self.t_Lane_Crossing_Right is not None:
                    ax.plot(self.t_Lane_Crossing_Right-self.t_ref,       self.Lane_Crossing_Right,          'r', label='Crossing Right')
                if self.t_Lane_Crossing_Left is not None:
                    ax.plot(self.t_Lane_Crossing_Left-self.t_ref,        self.Lane_Crossing_Left,           'b', label='Crossing Left')
        
                ax.set_ylim(-0.1, 12.1)
                ax.legend()
                ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,13)) 
                ax.set_yticklabels(['Off','Crossing - On','Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LNVU LD - On','Off','ME LD - On'])

            
 
            ax.grid()
            ax.set_xlim(local_xlim)

            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
    
        # --------------------------------------------------------
        if self.LDW_Left_okay:
        
            PlotName = PlotName + '_left'
            fig = self.start_fig(PlotName, FigNr=211)

            ax = fig.add_subplot(311)
            if self.FrontAxleSpeed_at_t_LDW_Left is not None:
                ax.set_title('Left side (v_ego = %3.1f km/h)'%(self.FrontAxleSpeed_at_t_LDW_Left*3.6,))
            else:
                ax.set_title('Left side')

            

            # --------------------------------------------------        
            # lines
            # OxTS Ford
            if self.Time_LeftLinePosLateral is not None:
                ax.plot(self.Time_LeftLinePosLateral-self.t_ref, self.LeftLinePosLateral-self.WheelLeft,'r',label='OxTS (%5.2f m)'%(self.LeftLinePosLateral_at_t_LDW_Left-self.WheelLeft,))
            # Racelogic    
            if self.Time_Range_Lt is not None:
                ax.plot(self.Time_Range_Lt-self.t_ref, self.Range_Lt-self.WheelLeft,'r',label='VBOX_LDWS_VCI (%5.2f m)'%(self.Range_Lt_at_t_LDW_Left-self.WheelLeft,))
            if customer_version or self.show_C0:
                ax.plot(self.t_Left_C0-self.t_ref,       self.Left_C0-self.WheelLeft,'b'+x_mark,label='FLC20 C0 (%5.2f m)'%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,))
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_C0_left_wheel-self.t_ref, self.C0_left_wheel,         'm'+x_mark,label='FLC20 C0 wheel')
 

        
            # --------------------------------
            # zones 
 
            ax.hlines(warn_zone_outer,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.hlines(warn_zone_inner,local_xlim[0],local_xlim[1],colors='r',linestyles='dashed')
            ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(warn_zone_inner,warn_zone_outer-warn_zone_inner),alpha=.1, facecolors='red')
  
            if 0:
                ax.hlines(reset_zone_outer,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.hlines(reset_zone_inner,local_xlim[0],local_xlim[1],colors='b',linestyles='dashed')
                ax.broken_barh([(local_xlim[0], local_xlim[1]-local_xlim[0])],(reset_zone_inner,reset_zone_outer-reset_zone_inner),alpha=.1, facecolors='blue')
 
            # ----------------------------------------
            # Warning Line
            ax.hlines(self.WarningLineLeft,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed', label="WarningLine %3.2f m"%self.WarningLineLeft)

            # ----------------------------------------
            # marker + text
            # start: Left_C0_at_t_LDW_Left+left_wheel
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,'md')
                #ax.text(t_LDW_Left_start-t_ref, Left_C0_at_t_LDW_Left+left_wheel,"  %5.2f m @ %3.2f m/s"%(Left_C0_at_t_LDW_Left+left_wheel,slope))
                print "Left_C0_at_t_LDW_Left",self.Left_C0_at_t_LDW_Left
                print "WheelLeft", self.WheelLeft
                print "WarningLineLeft", self.WarningLineLeft
                actual_TLC = (self.Left_C0_at_t_LDW_Left-self.WheelLeft-self.WarningLineLeft)/self.lateral_speed_Left_at_t_LDW_Left  
                if customer_version:                
                    ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,"  %5.2f m"%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,))
                else:
                    ax.text(self.t_LDW_Left_start-self.t_ref, self.Left_C0_at_t_LDW_Left-self.WheelLeft,"  %5.2f m @ %3.2f m/s (TLC %3.2f s)"%(self.Left_C0_at_t_LDW_Left-self.WheelLeft,self.lateral_speed_Left_at_t_LDW_Left,np.abs(actual_TLC)))

            # start: C0_left_wheel
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_LDW_Left_start-self.t_ref, self.C0_left_wheel_at_t_LDW_Left,'md')
                actual_TLC = (self.C0_left_wheel_at_t_LDW_Left+self.WarningLineLeft)/abs(self.lateral_speed_Left_at_t_LDW_Left)
                ax.text(self.t_LDW_Left_start-self.t_ref, self.C0_left_wheel_at_t_LDW_Left,"  %5.2f m @ %3.2f m/s (TLC= %3.2f s)"%(self.C0_left_wheel_at_t_LDW_Left,abs(self.lateral_speed_Left_at_t_LDW_Left),actual_TLC))

        
            # stop: Left_C0_at_t_LDW_Left_stop-WheelLeft
            if customer_version or self.show_C0:
                ax.plot(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,'ms')
                ax.text(self.t_LDW_Left_stop-self.t_ref,  self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,"  %5.2f m"%(self.Left_C0_at_t_LDW_Left_stop-self.WheelLeft,))
  
            # stop: C0_left_wheel_at_t_LDW_Left_stop
            if not customer_version and self.show_C0_wheel:
                ax.plot(self.t_LDW_Left_stop-self.t_ref, self.C0_left_wheel_at_t_LDW_Left_stop,'ms')
                ax.text(self.t_LDW_Left_stop-self.t_ref, self.C0_left_wheel_at_t_LDW_Left_stop,"  %5.2f m"%(self.C0_left_wheel_at_t_LDW_Left_stop,))

  
            ylim_local = (-0.6, 0.6)
            ylim_local = (min(self.Left_C0_at_t_LDW_Left-self.WheelLeft-0.1,ylim_local[0]),max(self.Left_C0_at_t_LDW_Left-self.WheelLeft+0.1,ylim_local[1]))
            ax.set_ylim(ylim_local)
            ax.set_xlim(local_xlim)

        
            if (not customer_version) or (self.Time_LeftLinePosLateral is not None) or (self.Time_Range_Lt is not None):
                ax.legend()
  
            ax.set_ylabel('inner <- left line [m] -> outer')
   
            ax.grid()
        
            # -------------------------------------
            # lateral speed
            ax = fig.add_subplot(312)
    
            # lines
            if self.Time_RightLineVelLateral is not None:
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral,         'y',label='OxTS (raw)')
                ax.plot(self.Time_LeftLineVelLateral-self.t_ref, self.LeftLineVelLateral_smoothed,'r',label='OxTS (%3.2f m/s)'%(self.LeftLineVelLateral_smoothed_at_t_LDW_Left,))
        
            if self.Time_Lat_Spd_Lt is not None:
                ax.plot(self.Time_Lat_Spd_Lt-self.t_ref, self.Lat_Spd_Lt_smoothed,'r',label='VBOX_LDWS_VCI (%3.2f m/s)'%(self.Lat_Spd_Lt_smoothed_at_t_LDW_Left,))

            ax.plot(self.t_Left_C0-self.t_ref, self.lateral_speed_Left,'b',label='FLC20 (%3.2f m/s)'%(self.lateral_speed_Left_at_t_LDW_Left,))
 
        
        
            # marker + text
            ax.plot(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,'md')
            ax.text(self.t_LDW_Left_start-self.t_ref, self.lateral_speed_Left_at_t_LDW_Left,"%3.2f m/s"%self.lateral_speed_Left_at_t_LDW_Left)
            ax.set_ylabel('lateral speed [m/s]')
            if (not customer_version) or (self.Time_RightLineVelLateral is not None) or (self.Time_Lat_Spd_Lt is not None):
                ax.legend()
        
            ax.set_xlim(local_xlim)
            ax.set_ylim(-2.1, 2.1)
            ax.grid()        

            # --------------------------------------------------------
            # warnings + tracking
            ax = fig.add_subplot(313)
            
            if customer_version:
                if self.t_WARN_isWarningLeft is not None:
                    ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       +6.0,'m', label='LD w/o supp.')
                ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   +4.0,'b', label='LD Imminent')
                ax.plot(self.t_AcousticalWarningLeft-self.t_ref,     self.AcousticalWarningLeft    +2.0,'r', label='AcousticalWarning')
                ax.plot(self.t_LDW_Left_Tracking-self.t_ref,         self.LDW_Left_Tracking            ,'k', label='Tracking ')
                ax.set_ylim(-0.1, 7.1)
                ax.legend()
                #ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,9)) 
                ax.set_yticklabels(['Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LD w/o supp. - On'])
            
            else:
                ax.plot(self.t_ME_LDW_LaneDeparture_Left-self.t_ref, self.ME_LDW_LaneDeparture_Left+10.0,'r', label='ME LD (w/o supp) (+10)')
                if self.t_WARN_isWarningLeft is not None:
                    ax.plot(self.t_WARN_isWarningLeft-self.t_ref,    self.WARN_isWarningLeft       + 8.0,'k', label='LNVU LD (w/o supp) (+8)')
                ax.plot(self.t_LaneDepartImminentLeft-self.t_ref,    self.LaneDepartImminentLeft   + 6.0,'b', label='LD Imminent (+6)')
                ax.plot(self.t_AcousticalWarningLeft-self.t_ref,     self.AcousticalWarningLeft    + 4.0,'m', label='AcousticalWarning (+4)')
                ax.plot(self.t_LDW_Left_Tracking-self.t_ref,         self.LDW_Left_Tracking        + 2.0,'c', label='Tracking (+2)')
                if self.t_Lane_Crossing_Right is not None:
                    ax.plot(self.t_Lane_Crossing_Right-self.t_ref,       self.Lane_Crossing_Right,          'r', label='Crossing Right')
                if self.t_Lane_Crossing_Left is not None:
                    ax.plot(self.t_Lane_Crossing_Left-self.t_ref,        self.Lane_Crossing_Left,           'b', label='Crossing Left')
        
                ax.set_ylim(-0.1, 12.1)
                ax.legend()
                ax.set_ylabel('flags')
                ax.set_yticks(np.arange(0,13)) 
                ax.set_yticklabels(['Off','Crossing - On','Off','Tracking - On','Off','Acoust. Warn. - On','Off','LD Imminent - On','Off','LNVU LD - On','Off','ME LD - On'])


            ax.grid()
            ax.set_xlim(local_xlim)
         
            ax.set_xlabel('time [s]')
            
            self.show_and_save_figure()
    
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cut_margin(self,FigNr = 187, xlim=None):
        
        #   Distance based 
             
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_A.7_cut_margin", FigNr)
    
        if xlim is not None:
            self.xlim_to_use(xlim)
        else:
            self.xlim_to_use(self.xlim_default)
            
    
      
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Left
        ax = fig.add_subplot(211)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Left'], 'r',label='DEBUG_cut_margin_mm_Left' )
        self.set_description(ax,'Left [m]', None) 
       
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Right
        ax = fig.add_subplot(212)
           
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Right'],'r',label='DEBUG_cut_margin_mm_Right' )
        self.set_description(ax,'Right [m]', None ) # (-0.3,0.3)
                 
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
  
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_cmp_ME_LNVU_Distance(self,FigNr = 181, xlim=None):
        
        #   Distance based 
             
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_A.2_cmp_ME_LNVU_Distance", FigNr)
    
        if xlim is not None:
            self.xlim_to_use(xlim)
        else:
            self.xlim_to_use(self.xlim_default)
            
    
            
       
        # ------------------------------------------------------
        # Warnings Left
        ax = fig.add_subplot(611)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']          ,'r',label='isWarn ')
        ax.plot(self.sim_input['t_rel_BxInfo'], self.sim_input['COMPARE_LNVU_isWarningLeft'],   'bx-',label='FLC - isWarn')
        self.set_description(ax,'Left',(-0.1, 4.1) ) 
    
        
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Left
        ax = fig.add_subplot(612)
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_laneOffset_Left']-self.VehicleWidthHalf,          'k',label='BX_laneOffset_Left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Left'], 'r',label='DEBUG_cut_margin_mm_Left' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_D_margin_left'],      'b',label='DEBUG_D_margin_left' )        
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']*0.1,   'm',label='WARN_isWarningLeft' )
        self.set_description(ax,'Left [m]', (-0.3,0.3)) 

          
        # ------------------------------------------------------
        # Warnings Right
        ax = fig.add_subplot(613)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']+2.0,'b',label='ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']          ,'r',label='isWarn ')
        ax.plot(self.sim_input['t_rel_BxInfo'], self.sim_input['COMPARE_LNVU_isWarningRight'],   'bx-',label='FLC - isWarn')
        self.set_description(ax,'Right',(-0.1, 4.1) )
        
        # ------------------------------------------------------
        # DEBUG_cut_margin_mm_Right
        ax = fig.add_subplot(614)
           
        ax.plot(self.sim_output['t_rel'], self.sim_output['BX_laneOffset_Right']-self.VehicleWidthHalf,'k',label='BX_laneOffset_Right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_cut_margin_mm_Right'],'r',label='DEBUG_cut_margin_mm_Right' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_D_margin_right'],     'b',label='DEBUG_D_margin_right' )    
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']*0.1,  'm',label='WARN_isWarningRight' )
        self.set_description(ax,'Right [m]', (-0.3,0.3) ) # (-0.3,0.3)


        # ------------------------------------------------------
        # DEBUG_space
        ax = fig.add_subplot(615)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_space'],         'r',label='SIM - space')
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_Space']/1000.0 ,'b',label='FLC - space ')
        self.set_description(ax,'[m]',(-0.1, 3.5) )
     
        # ------------------------------------------------------
        # DEBUG_TimeBased_flag
        ax = fig.add_subplot(616)
        ax.plot(self.sim_output['t_rel'],        self.sim_output['DEBUG_TimeBased_flag'],      'r',label='SIM - TimeBased_flag' )
        ax.plot(self.sim_input['t_rel_BxInfo'],  self.sim_input['COMPARE_LNVU_TimeBased_flag'],'b',label='FLC - DEBUG_TimeBased_flag')
        self.set_description(ax,'[flag]',(-0.1,1.1))
                 
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_asymm(self,FigNr = 200):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_B_StartOfWarningZone_Right", FigNr)
      
        # ------------------------------------------------------
        # Decel
        ax = fig.add_subplot(111)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_ME_StartOfWarningZone_Right'],'r',label='DEBUG_ME_StartOfWarningZone_Right' )
        self.set_description(ax,'flag',None ) 
       
        ax.set_xlabel('time [s]')
        self.show_and_save_figure()
 
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_Frame_ID(self,FigNr = 201):
         
        '''
        print 'self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"]', self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"][10:20]
        print 'self.FLR20_sig["FLC20_CAN"]["Frame_ID"]', self.FLR20_sig["FLC20_CAN"]["Frame_ID"][10:20]
        print 'self.FLR20_sig["Bendix_Info3"]["Time_LNVU_Frame_Id_LSB"]', self.FLR20_sig["Bendix_Info3"]["Time_LNVU_Frame_Id_LSB"][10:20]
        print 'self.FLR20_sig["Bendix_Info3"]["LNVU_Frame_Id_LSB"]', self.FLR20_sig["Bendix_Info3"]["LNVU_Frame_Id_LSB"][10:20]
        '''

        #d = Ccalc_delay(self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"],self.FLR20_sig["FLC20_CAN"]["Frame_ID"], self.FLR20_sig["Bendix_Info3"]["Time_LNVU_Frame_Id_LSB"],self.FLR20_sig["Bendix_Info3"]["LNVU_Frame_Id_LSB"]) 
        t_head   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        cnt_head = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Video_Data_General_A"]

        t_tail   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        cnt_tail = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Next_Left_B"]

        videopacket = kbtools_user.CFLC20FusionMsgArray(t_head, cnt_head, t_tail, cnt_tail)

       
        t_BxInfo, Bendix_Info3_delay = videopacket.calc_delay(self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"],self.FLR20_sig["FLC20_CAN"]["Frame_ID"], self.FLR20_sig["FLC20_CAN"]["Time_LNVU_Frame_Id_LSB"],self.FLR20_sig["FLC20_CAN"]["LNVU_Frame_Id_LSB"]) 

       
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_C.1_Frame_ID", FigNr)
        
        # ------------------------------------------------------
        # Frame ID
        ax = fig.add_subplot(311)
        ax.plot(d.t1,d.x1,'bx-',label=r'Frame_Id mod 4')
        ax.plot(d.t2,d.x2,'rx-',label='LNVU_Frame_Id')
        self.set_description(ax,'flag',(-0.1,3.1) ) 

        # ------------------------------------------------------
        # burst length
        ax = fig.add_subplot(312)
        ax.plot(d.t1,d.dt*1000,'bx-',label=r'burst length')
        self.set_description(ax,'flag',(8,12) ) 

        # ------------------------------------------------------
        # delay
        ax = fig.add_subplot(313)
        ax.plot(d.t1,d.delay, 'rx-',label='delay')
        self.set_description(ax,'flag',(-1.1,3.1) ) 
     
        ax.set_xlabel('time [s]')
        self.show_and_save_figure()

    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_videopacket_sync(self,FigNr = 202):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_C.2_videopacket_sync", FigNr)
      
       
        # ------------------------------------------------------
        ax = fig.add_subplot(211)
        ax.plot(self.sim_input['t_rel_videopacket'],  self.sim_input['Bendix_Info3_delay'],'mx-',label='delay')
        self.set_description(ax,'[delay]',(-0.1, 5.1)) 
        
          
        # ------------------------------------------------------
        # BX_LDW_Suppr_LOW_SPEED
        ax = fig.add_subplot(212)
        #ax.plot(self.sim_input['t_rel'],  (np.bitwise_and(self.sim_input['BX_LDW_Suppr'].astype(int),0x0004)>0),'b',label='Truck')   
        ax.plot(self.sim_output['t_rel'], (np.bitwise_and(self.sim_output['BX_Warning_Suppression'].astype(int),0x0004)>0),'rx-',label='Sim')
        
        ax.plot(self.sim_input['t_rel_videopacket'], (np.bitwise_and(self.sim_input['COMPARE_BX_LDW_Suppr'].astype(int),0x0004)>0)*0.7,'bx-',label='FLC20 raw')
        ax.plot(self.sim_input['t_rel_BxInfo'],      (np.bitwise_and(self.sim_input['COMPARE_BX_LDW_Suppr'].astype(int),0x0004)>0)*0.7,'cx-',label='FLC20 cor')
        
        ax.set_yticks([0.0,1.0])        
        ax.set_yticklabels(['Off','On'])
        self.set_description(ax,'supp. LOW SPEED',(-0.1, 1.1)) 

     
        ax.set_xlabel('time [s]')
 

        # ------------------------------------------------------
        self.show_and_save_figure()
       
            
        
        
        
        
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_Set_BX_LDW_LaneDeparture(self,FigNr = 890):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_Set_BX_LDW_LaneDeparture", FigNr)
 
        ax = fig.add_subplot(411)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Left']    + 2.0,'b', label='Truck - ME Warn (+2)')
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningLeft']          + 2.0,'r', label='Sim - isWarnLeft (+2)')
        ax.plot(self.sim_input['t_rel'],  self.sim_input['Left_Lane_Crossing']           ,'k', label='Lane_Crossing' )
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
        self.set_description(ax,'Left',(-0.1,5.1) ) 
    
        # ------------------------------------------------------
        # Warnings left
        ax = fig.add_subplot(412)
        
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Left']  ,'m', label='Sim - BX_LDW_LaneDeparture (+2)')
  
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
        self.set_description(ax,'Left',(-0.1,5.1) ) 
        
        
        # ------------------------------------------------------
        # Warnings right
        ax = fig.add_subplot(413)
        ax.plot(self.sim_input['t_rel'],  self.sim_input['ME_LDW_LaneDeparture_Right']    + 2.0,'b', label='Truck - ME Warn (+2)' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['WARN_isWarningRight']          + 2.0,'r', label='Sim - isWarnRight (+2)')
        ax.plot(self.sim_input['t_rel'],  self.sim_input['Right_Lane_Crossing']                ,'k', label='Lane_Crossing' )
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
        self.set_description(ax,'Right',(-0.1,5.1) ) 

        
        
        ax = fig.add_subplot(414)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Right']  ,'m', label='Sim - BX_LDW_LaneDeparture (+2)')
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
        self.set_description(ax,'Right',(-0.1,5.1) ) 
  
  
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
    # -------------------------------------------------------------------------------------------------------------------------
    def plot_LDWS_DetermineWarningAlarm(self,FigNr = 891):
         
        # ------------------------------------------------------
        fig = self.start_fig("LDWS_DetermineWarningAlarm", FigNr)
 
        # ------------------------------------------------------
        # Warnings left
        ax = fig.add_subplot(411)
        
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Left']  + 2.0,'m', label='Sim - BX_LDW_LaneDeparture (+2)')
  
        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentLeft']       ,'b', label='Truck - Imminent')
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Left']  ,'r', label='Sim - Imminent')

        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
        self.set_description(ax,'Left',(-0.1,5.1) ) 
        
        
        # ------------------------------------------------------
        # Warnings right
        ax = fig.add_subplot(412)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_BX_LDW_LaneDeparture_Right']  + 2.0,'m', label='Sim - BX_LDW_LaneDeparture (+2)')

        ax.plot(self.sim_input['t_rel'],  self.sim_input['LaneDepartImminentRight']       ,'b', label='Truck - Imminent' )
        ax.plot(self.sim_output['t_rel'], self.sim_output['KB_LDW_Imminent_State_Right']  ,'r', label='Sim - Imminent' )
        
        ax.set_yticks([0.0,1.0,2.0,3.0])        
        ax.set_yticklabels(['Off','On','Off','On'])
       
        self.set_description(ax,'Right',(-0.1,5.1) ) 
  
        ax = fig.add_subplot(413)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_DetermineWarningAlarmInputWarningType'] ,'b', label='Sim - DEBUG_DetermineWarningAlarmInputWarningType ')
        self.set_description(ax,'-',(-0.1,5.1) )
        
        ax = fig.add_subplot(414)
        ax.plot(self.sim_output['t_rel'], self.sim_output['DEBUG_AlarmWarningState'] ,'b', label='Sim - DEBUG_AlarmWarningState ')
        
       
       
        self.set_description(ax,'-',(-0.1,5.1) ) 
  
        ax.set_xlabel('time [s]')
        # ------------------------------------------------------
        self.show_and_save_figure()
    
    

     
    
    
    
    
    

     

    
    
    
     
    
    
    
    
    
