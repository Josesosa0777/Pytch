"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: ACC evalulation '''

''' to be called by DAS_eval.py '''


'''
Signals:
  ACC1 message

'''

import os

#import numpy as np
#import pylab as pl
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import kbtools
import kbtools_user
import sys, traceback

# ==========================================================
def create_special_grid(ax):
    '''
        provide a finer grid
    '''

    majorLocator   = MultipleLocator(1)
    majorFormatter = FormatStrFormatter('%d')

    minorLocator   = MultipleLocator(0.1)
    

    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.xaxis.set_minor_locator(minorLocator)
    #ax.xaxis.grid(True, which='both')
    
    #ax.grid(b=True, which='major',  color='k', linestyle='-')
    #ax.grid(b=True, which='minor',  color='k', linestyle=':')
    ax.grid(b=True, which='major', axis = 'x', color='k', linestyle=':',linewidth = 1.0)
    ax.grid(b=True, which='minor', axis = 'x', color='grey', linestyle=':')
    ax.grid(b=True, which='major', axis = 'y', color='k', linestyle=':',linewidth = 1.0)
    ax.grid(b=True, which='minor', axis = 'y', color='grey', linestyle=':')


''' ============================================================================================== '''
class cPlotJ1939ACC(kbtools_user.cPlotBase):
   
    # ==========================================================
    def __init__(self, FLR20_sig, t_event, xlim, PngFolder = r".\png", VehicleName=None, Description=None, show_figures=False, cfg={} ,verbose=False):
       
        self.FLR20_sig    = FLR20_sig
        self.t_event      = t_event
        self.xlim         = xlim  
        self.PngFolder    = PngFolder             
        self.VehicleName  = VehicleName
        self.Description  = Description
        self.show_figures = show_figures
        self.verbose      = verbose
      
        if self.xlim is None:
            self.xlim = ( -7.0, +8.0)          # pre and post trigger
        
        # ------------------------------------------------------------------
        # FileName of measurement 
        if 'FileName' in self.FLR20_sig:
            self.FileName = os.path.splitext(os.path.basename(self.FLR20_sig['FileName']))[0]
            #self.FileName = os.path.basename(self.FLR20_sig['FileName'])
        else:
            self.FileName = ''
            
        super(cPlotJ1939ACC,self).__init__(PngFolder=self.PngFolder,show_figures=show_figures)
        
        self.input_mode = 'FLR20'   # "SilLDWS_C"
        
        
        
    def PlotAll(self,enable_png_extract = True,OffsetList=None, input_mode='FLR20', test_mode_f = False):
    
        # -------------------------------------------------
        self.input_mode = input_mode
    
        # -------------------------------------------------
        # check if A087 is available - quick & dirty
        print "self.FLR20_sig['General']", self.FLR20_sig['General']
        try:
            tmp = self.FLR20_sig['General']['Time']
            print "self.FLR20_sig['General']['Time']", tmp
        except:
            print "PlotFLR20AEBS.PlotAll(): A087 signals missing"
            #return
            
        # self.AEBS_Attr_FLR20 = self._Calc_AEBS_Attr(mode = 'FLR20') 
        
        self.plot_ACC_standard()
        
        self.plot_ACC_standard2()
        
        '''
        self.plot_AEBS_use_case_v_vs_d()
        self.plot_AEBS_use_case_dy()
        self.plot_AEBS_Ovrride()
        self.plot_AEBS_aRel()
        self.plot_AEBS_TRW_AECF()
        self.plot_AEBS_XBR()
        self.plot_AEBS_use_case_Fusion()
        self.plot_AEBS_use_case_Fusion2()
        self.plot_AEBS_use_case_Fusion3()
        self.plot_AEBS_use_case_Fusion4()
        self.plot_AEBS_use_case_FLC20_CAN_Delay()
        '''
         
        # extract frames from video
        '''
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')   
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin
        res = AEBS_Attr.getResults()
               
        if enable_png_extract:
            print "---------------------------------------"
            print "extract frames from video:"
            OffsetList = []
            for signal in ["t_warning", "t_braking", "t_emergency", "t_impact", "t_ego_stopped", "t_relaxed"]:
                if res[signal] is not None:
                    OffsetList.append(res[signal]-self.t_event)
                    if signal == "t_warning":
                        for delta_t in [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
                            OffsetList.append(res[signal]-self.t_event+delta_t)
                    
            FullPathFileName = self.FLR20_sig['FileName_org']              
            kbtools_user.CreateVideoSnapshots(FullPathFileName,self.FLR20_sig, self.t_event, OffsetList = OffsetList, PngFolder = self.PngFolder,verbose=self.verbose)
        '''

    # ==========================================================
    def plot_ACC_standard(self, FigNr = 30,xlim=None, PlotName='ACC_1_standard'):
        '''
            AEBS_Homologation
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')
        #AEBS_Attr = self.AEBS_Attr_FLR20     
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AdaptiveCruiseCtrlMode(fig.add_subplot(911), t_origin)       

        
        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_ACC_velocity(fig.add_subplot(912), t_origin)
    
        
        # -------------------------------------------------------------------------
        # dx
        self._subplot_ACC_position(fig.add_subplot(913), t_origin)
       
        
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_TSC1_XBR_CtrlMode(fig.add_subplot(914), t_origin)
 
 
        self._subplot_EngTorque(fig.add_subplot(915), t_origin)
        
        self._subplot_ACC_acceleration(fig.add_subplot(916), t_origin)
 
        self._subplot_ACC_Flags(fig.add_subplot(917), t_origin)
        
        self._subplot_DriverDemand(fig.add_subplot(918), t_origin)
        
        self._subplot_RetarderTorque(fig.add_subplot(919), t_origin)
        
        
 
        
 
        '''
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        # -------------------------------------------------------------------------
        # AEBS_Attr table
        self._subplot_AEBS_Attr_table(fig.add_subplot(515),AEBS_Attr, t_origin)
        '''

        # -------------------------------------------------------------------------
        self.show_and_save_figure()

    # ==========================================================
    def plot_ACC_standard2(self, FigNr = 30,xlim=None, PlotName='ACC_1_standard2'):
        '''
            ACC
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')
        #AEBS_Attr = self.AEBS_Attr_FLR20     
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # ACC Control Mode, AEBS system state
        self._subplot_AdaptiveCruiseCtrlMode(fig.add_subplot(511), t_origin)       

        
        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_ACC_velocity(fig.add_subplot(512), t_origin)
    
        
        # -------------------------------------------------------------------------
        # dx
        self._subplot_ACC_position(fig.add_subplot(513), t_origin)
         
        # -------------------------------------------------------------------------
        # dx
        self._subplot_ACC_acceleration(fig.add_subplot(514), t_origin)
    
        
        
        
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_TSC1_XBR_CtrlMode(fig.add_subplot(515), t_origin)
 
 
        #self._subplot_EngTorque(fig.add_subplot(915), t_origin)
        
        #self._subplot_XBR(fig.add_subplot(916), t_origin)
 
        #self._subplot_ACC_Flags(fig.add_subplot(917), t_origin)
        
        #self._subplot_DriverDemand(fig.add_subplot(918), t_origin)
        
        #self._subplot_RetarderTorque(fig.add_subplot(919), t_origin)
        
        
 
        
 
        '''
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        # -------------------------------------------------------------------------
        # AEBS_Attr table
        self._subplot_AEBS_Attr_table(fig.add_subplot(515),AEBS_Attr, t_origin)
        '''

        # -------------------------------------------------------------------------
        self.show_and_save_figure()

    # ==========================================================
    def _subplot_AdaptiveCruiseCtrlMode(self, ax, t_origin):
        '''
           Create subplot for AEBS_Attr.AEBS State
        
        '''
        
        FLR20_sig = self.FLR20_sig
        
        Time_AdaptiveCruiseCtrlMode_s2A   = FLR20_sig['J1939']["Time_AdaptiveCruiseCtrlMode_s2A"]
        AdaptiveCruiseCtrlMode_s2A        = FLR20_sig['J1939']["AdaptiveCruiseCtrlMode_s2A"]
    
        Time_AEBSState   = FLR20_sig['J1939']["Time_AEBSState"]
        AEBSState        = FLR20_sig['J1939']["AEBSState"]
        
        Time_CruiseCtrlActive_s00         = FLR20_sig['J1939']["Time_CruiseCtrlActive_s00"]
        CruiseCtrlActive_s00              = FLR20_sig['J1939']["CruiseCtrlActive_s00"]
    

        
        if Time_AEBSState is not None:
            ax.plot(Time_AEBSState-t_origin, AEBSState,'b', label= 'AEBS State' )
 
        if Time_AdaptiveCruiseCtrlMode_s2A is not None:
            ax.plot(Time_AdaptiveCruiseCtrlMode_s2A-t_origin, AdaptiveCruiseCtrlMode_s2A,'r', label= 'ACC Mode' )
         
        if Time_CruiseCtrlActive_s00 is not None:
            ax.plot(Time_CruiseCtrlActive_s00-t_origin, CruiseCtrlActive_s00,'k', label= 'CruiseCtrlActive' )

 
        ax.set_yticks(range(8))   
        label1 = ['Off (0)','Speed (1)','Distance (2)','Overtake (3)']
        label2 = ['Hold (4)','Finish (5)','Error (6)','n.a. (7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3,fontsize='small')

        '''
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.ABESState_at_t_warning, LineStyle='gd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_warning-t_origin), yOffset=0.1, label='WP1')
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.ABESState_at_t_braking, LineStyle='bd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_braking-t_origin), yOffset=0.1, label='WP2')
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.ABESState_at_t_emergency, LineStyle='rd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_emergency-t_origin), yOffset=0.1, label='EBP')
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.ABESState_at_t_impact, LineStyle='yd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_impact-t_origin), yOffset=0.1, label='impact')
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.ABESState_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.2f s',Value=(AEBS_Attr.t_ego_stopped-t_origin), yOffset=0.1, label='avoid.')
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.ABESState_at_t_relaxed, LineStyle='m*',FmtStr='%3.2f s',Value=(AEBS_Attr.t_relaxed-t_origin), yOffset=0.1, label='avoid.')
        '''

        #self.set_description(ax, ylabel=None, ylim=(-0.1,8.1), grid='special')
        self.set_description(ax, ylabel=None, ylim=(-0.1,8.1))
        
    # ==========================================================
    def _subplot_TSC1_XBR_CtrlMode(self, ax, t_origin):
        '''
           Create subplot for AEBS_Attr.AEBS State
        
        '''
        
        FLR20_sig = self.FLR20_sig
        
        
        
        #Time_OverrideCtrlModePriority_d00_s2A   = FLR20_sig['J1939']["Time_OverrideCtrlModePriority_d00_s2A"]
        #OverrideCtrlModePriority_d00_s2A        = FLR20_sig['J1939']["OverrideCtrlModePriority_d00_s2A"]
    
        Time_EngOverrideCtrlMode_d00_s2A   = FLR20_sig['J1939']["Time_EngOverrideCtrlMode_d00_s2A"]
        EngOverrideCtrlMode_d00_s2A        = FLR20_sig['J1939']["EngOverrideCtrlMode_d00_s2A"]
    
        Time_EngOverrideCtrlMode_d10_s2A   = FLR20_sig['J1939']["Time_EngOverrideCtrlMode_d10_s2A"]
        EngOverrideCtrlMode_d10_s2A        = FLR20_sig['J1939']["EngOverrideCtrlMode_d10_s2A"]

        Time_EngOverrideCtrlMode_d29_s2A   = FLR20_sig['J1939']["Time_EngOverrideCtrlMode_d29_s2A"]
        EngOverrideCtrlMode_d29_s2A        = FLR20_sig['J1939']["EngOverrideCtrlMode_d29_s2A"]
        
        Time_XBR_d0B_s2A                   = FLR20_sig['J1939']["Time_XBR_d0B_s2A"]
        XBRCtrlMode_d0B_s2A                = FLR20_sig['J1939']["XBRCtrlMode_d0B_s2A"]
    
    
       
    
        #ax.plot(Time_OverrideCtrlModePriority_d00_s2A-t_origin, OverrideCtrlModePriority_d00_s2A,'b', label= 'OverrideCtrlModePriority' )
        if Time_EngOverrideCtrlMode_d00_s2A is not None:
            ax.plot(Time_EngOverrideCtrlMode_d00_s2A-t_origin, EngOverrideCtrlMode_d00_s2A,'b', label= 'Engine s00' )

        if Time_EngOverrideCtrlMode_d10_s2A is not None:
            ax.plot(Time_EngOverrideCtrlMode_d10_s2A-t_origin, EngOverrideCtrlMode_d10_s2A,'c', label= 'Ret s10' )

        if Time_EngOverrideCtrlMode_d29_s2A is not None:
            ax.plot(Time_EngOverrideCtrlMode_d29_s2A-t_origin, EngOverrideCtrlMode_d29_s2A,'k', label= 'Ret s29' )

 
        if Time_XBR_d0B_s2A is not None:
            ax.plot(Time_XBR_d0B_s2A-t_origin, XBRCtrlMode_d0B_s2A,'r', label= 'XBR s2A' )
 

 
        ax.set_yticks(range(4))   
        #3 "Spd_TrqLmtCtrlLmtSpdAnd_OrTrqBs" 2 "TrqCtrlCntrlTrqTInclddDsrdTrqVl" 1 "SpdCtrlGvrnSpdTInclddDsrdSpdVle" 0 "OvrrdDsbldDsblAnyExstngCtrlCmdd"
        label1 = ['disabled (0)','Add / Torque (1)','Max /Speed (2)','Limit (3)']
        ax.set_yticklabels(label1,fontsize='small')

        '''
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.ABESState_at_t_warning, LineStyle='gd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_warning-t_origin), yOffset=0.1, label='WP1')
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.ABESState_at_t_braking, LineStyle='bd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_braking-t_origin), yOffset=0.1, label='WP2')
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.ABESState_at_t_emergency, LineStyle='rd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_emergency-t_origin), yOffset=0.1, label='EBP')
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.ABESState_at_t_impact, LineStyle='yd',FmtStr='%3.2f s',Value=(AEBS_Attr.t_impact-t_origin), yOffset=0.1, label='impact')
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.ABESState_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.2f s',Value=(AEBS_Attr.t_ego_stopped-t_origin), yOffset=0.1, label='avoid.')
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.ABESState_at_t_relaxed, LineStyle='m*',FmtStr='%3.2f s',Value=(AEBS_Attr.t_relaxed-t_origin), yOffset=0.1, label='avoid.')
        '''

        #self.set_description(ax, ylabel=None, ylim=(-0.1,8.1), grid='special')
        self.set_description(ax, ylabel='Ctrl Mode', ylim=(-0.1,4.1))
        
    # ==========================================================
    def _subplot_ACC_position(self, ax, t_origin,mark_is_video_associated=False):
        '''
           Create subplot for  AEBS_Attr.dx
        
        '''
        #dx_unit = "m"
 
        FLR20_sig = self.FLR20_sig
        
        dx_min = -10.0
        dx_max = 150.0        
        
       
        Time_DistanceToForwardVehicle_s2A   = FLR20_sig['J1939']["Time_DistanceToForwardVehicle_s2A"]
        DistanceToForwardVehicle_s2A        = FLR20_sig['J1939']["DistanceToForwardVehicle_s2A"]
        
        Time_WheelbasedVehSpd   = FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
        WheelbasedVehSpd        = FLR20_sig['J1939']["WheelbasedVehSpd"]
    
        # Racelogic VBOX
        Time_LngRsv_tg1, LngRsv_tg1 = kbtools.GetSignal(FLR20_sig["Source"],"ADAS_VCI_T1_2","LngRsv_tg1")
    
        
    
        TimeGap = 2.0
        Time_HeadwayDistance = Time_WheelbasedVehSpd
        HeadwayDistance = WheelbasedVehSpd/3.6*TimeGap
        
        if not Time_DistanceToForwardVehicle_s2A is None:
            ax.plot(Time_DistanceToForwardVehicle_s2A-t_origin, DistanceToForwardVehicle_s2A,'b', label='dx')
        #ax.plot(Time_HeadwayDistance-t_origin, HeadwayDistance,'r', label='headway')

        if not Time_LngRsv_tg1 is None:
            ax.plot(Time_LngRsv_tg1-t_origin, LngRsv_tg1,'m', label='LngRsv_tg1')

        
        
        '''
        if mark_is_video_associated and (AEBS_Attr.Time_cw_vidconf is not None):
            dx_cw_vidconf = AEBS_Attr.dx*(kbtools.resample(AEBS_Attr.Time_cw_vidconf, AEBS_Attr.cw_vidconf, AEBS_Attr.Time_dx)>0)      
            ax.plot(AEBS_Attr.Time_dx-t_origin, dx_cw_vidconf,'r', label='dx vid. ass. (%s)'%AEBS_Attr.mode)
        
         
         
        # Marker + Text
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.dx_at_t_warning, LineStyle='gd',FmtStr='%3.1f', yOffset=10.0)
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.dx_at_t_braking, LineStyle='bd',FmtStr='%3.1f', yOffset=10.0)
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.dx_at_t_emergency, LineStyle='rd',FmtStr='%3.1f', yOffset=10.0)
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.dx_at_t_impact, LineStyle='yd',FmtStr='%3.1f', yOffset=10.0)
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.dx_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.1f', yOffset=10.0)
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.dx_at_t_relaxed, LineStyle='m*',FmtStr='%3.1f', yOffset=10.0)
       
        '''
            
        #self.set_description(ax, ylabel='dx [m]', ylim=(dx_min,dx_max), grid='special') 
        self.set_description(ax, ylabel='dx [m]', ylim=(dx_min,dx_max)) 


       
    # ==========================================================
    def _subplot_ACC_velocity(self, ax, t_origin):
        '''
           Create subplot for  AEBS_Attr.v_ego, AEBS_Attr.v_target
        
        '''
        
        FLR20_sig = self.FLR20_sig
        
        v_kph_min = -10.0
        v_kph_max = 100.0

        v_unit = "km/h" 
        
        
        Time_WheelbasedVehSpd   = FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
        WheelbasedVehSpd        = FLR20_sig['J1939']["WheelbasedVehSpd"]
    
        Time_AdaptiveCruiseCtrlSetSpeed_s2A   = FLR20_sig['J1939']["Time_AdaptiveCruiseCtrlSetSpeed_s2A"]
        AdaptiveCruiseCtrlSetSpeed_s2A        = FLR20_sig['J1939']["AdaptiveCruiseCtrlSetSpeed_s2A"]
        
        Time_SpeedOfForwardVehicle_s2A   = FLR20_sig['J1939']["Time_SpeedOfForwardVehicle_s2A"]
        SpeedOfForwardVehicle_s2A        = FLR20_sig['J1939']["SpeedOfForwardVehicle_s2A"]
        
       
        Time_Spd_tg1, Spd_tg1 = kbtools.GetSignal(FLR20_sig["Source"],"ADAS_VCI_T1_7","Spd_tg1")
        
        ax.plot(Time_WheelbasedVehSpd-t_origin,WheelbasedVehSpd,'r', label='v host')
        ax.plot(Time_AdaptiveCruiseCtrlSetSpeed_s2A-t_origin,AdaptiveCruiseCtrlSetSpeed_s2A,'b', label='ACC set speed')
        ax.plot(Time_SpeedOfForwardVehicle_s2A-t_origin,SpeedOfForwardVehicle_s2A,'k', label='speed forward vehicle')
        if not Time_Spd_tg1 is None:
            ax.plot(Time_Spd_tg1-t_origin,Spd_tg1,'m', label='speed forward vehicle (Racelogic)')
         
        '''
        if AEBS_Attr.Time_v_target is not None:
            ax.plot(AEBS_Attr.Time_v_target-t_origin,AEBS_Attr.v_target,'r', label = 'v target(%s)'%AEBS_Attr.mode)
        '''
        
        '''
        # Marker + Text - v_ego
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.v_ego_at_t_warning, LineStyle='gd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.v_ego_at_t_braking, LineStyle='bd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.v_ego_at_t_emergency, LineStyle='rd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.v_ego_at_t_impact, LineStyle='yd',FmtStr='%3.1f', yOffset=2.0)
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.v_ego_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.1f', yOffset=2.0)
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.v_ego_at_t_relaxed, LineStyle='m*',FmtStr='%3.1f', yOffset=2.0)
            
            
        # Marker + Text - v_target
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.v_target_at_t_warning, LineStyle='gd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.v_target_at_t_braking, LineStyle='bd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.v_target_at_t_emergency, LineStyle='rd',FmtStr='%3.1f', yOffset=2.0)
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.v_target_at_t_impact, LineStyle='yd',FmtStr='%3.1f', yOffset=2.0)
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.v_target_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.1f', yOffset=2.0)
        #if AEBS_Attr.t_relaxed is not None:
        #    self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.v_target_at_t_relaxed, LineStyle='m*',FmtStr='%3.1f', yOffset=2.0)
        '''
 
        #self.set_description(ax, ylabel='v [%s]'%v_unit, ylim=(v_kph_min,v_kph_max), grid='special') 
        self.set_description(ax, ylabel='v [%s]'%v_unit, ylim=(v_kph_min,v_kph_max)) 

    # ==========================================================
    def _subplot_ACC_acceleration(self, ax, t_origin, show_only_one_ax_signal = True,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''
        FLR20_sig = self.FLR20_sig

        ax_min = -4.0
        ax_max = 2.0
        
        
        Time_WheelbasedVehSpd   = FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
        WheelbasedVehSpd                    = FLR20_sig['J1939']["WheelbasedVehSpd"]
           
        Time_SpeedOfForwardVehicle_s2A      = FLR20_sig['J1939']["Time_SpeedOfForwardVehicle_s2A"]
        SpeedOfForwardVehicle_s2A           = FLR20_sig['J1939']["SpeedOfForwardVehicle_s2A"]
        
        Time_XBR_d0B_s2A                    = FLR20_sig['J1939']["Time_XBR_d0B_s2A"]
        ExtlAccelerationDemand_d0B_s2A      = FLR20_sig['J1939']["ExtlAccelerationDemand_d0B_s2A"]

        
        # host vehicle acceleration 
        Time_ax_ego, ax_ego = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='v_ego')

        Time_ax_ego_VBOX_GPS, ax_ego_VBOX_GPS = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_GPS',smooth_filter=True, f_g=1.0)
        Time_ax_ego_VBOX_IMU, ax_ego_VBOX_IMU = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_IMU',smooth_filter=True, f_g=10.0)

        '''
        # Distance to Target object
        Time_dx    =  FLR20_sig["VBOX_IMU"]["Time_Range_tg1"]
        dx         =  FLR20_sig["VBOX_IMU"]["Range_tg1"] 
        
        # Relative speed of target
        Time_vr    =  FLR20_sig["VBOX_IMU"]["Time_RelSpd_tg1"]
        vr         =  FLR20_sig["VBOX_IMU"]["RelSpd_tg1"]
        
        # Relative acceleration
        Time_aRel  =  FLR20_sig["VBOX_IMU"]["Time_Accel_tg1"]
        aRel       =  FLR20_sig["VBOX_IMU"]["Accel_tg1"]
        '''

        Time_Spd_tg1, Spd_tg1 = kbtools.GetSignal(FLR20_sig["Source"],"ADAS_VCI_T1_7","Spd_tg1")



        f_g = 1.5 # Hz
        if Time_WheelbasedVehSpd is not None:
            Time_ax_WheelbasedVehSpd = Time_WheelbasedVehSpd
            #ax_WheelbasedVehSpd = kbtools.ugdiff(Time_WheelbasedVehSpd, WheelbasedVehSpd/3.6, verfahren=1)
            
            ax_WheelbasedVehSpd, _  = kbtools.svf_1o(Time_WheelbasedVehSpd,WheelbasedVehSpd/3.6, T=0.1)
            ax_WheelbasedVehSpd = kbtools.smooth_filter(Time_ax_WheelbasedVehSpd, ax_WheelbasedVehSpd ,f_g = f_g, filtertype = 'acausal')


        if Time_SpeedOfForwardVehicle_s2A is not None:
            Time_ax_ForwandVehicle = Time_SpeedOfForwardVehicle_s2A
            #ax_ForwandVehicle = kbtools.ugdiff(Time_SpeedOfForwardVehicle_s2A, SpeedOfForwardVehicle_s2A/3.6, verfahren=1)
            ax_ForwandVehicle, _  = kbtools.svf_1o(Time_SpeedOfForwardVehicle_s2A,SpeedOfForwardVehicle_s2A/3.6, T=0.1, valid = SpeedOfForwardVehicle_s2A< 100.0)
            ax_ForwandVehicle = kbtools.smooth_filter(Time_ax_ForwandVehicle, ax_ForwandVehicle ,f_g = f_g, filtertype = 'acausal', valid = SpeedOfForwardVehicle_s2A< 100.0)
      
        if Time_Spd_tg1 is not None:
            Time_ax_Spd_tg1 = Time_Spd_tg1
            #ax_Spd_tg1 = kbtools.ugdiff(Time_Spd_tg1, Spd_tg1/3.6, verfahren=1)
            ax_Spd_tg1, _  = kbtools.svf_1o(Time_Spd_tg1,Spd_tg1/3.6, T=0.1, valid = Spd_tg1< 100.0)
            ax_Spd_tg1 = kbtools.smooth_filter(Time_ax_Spd_tg1, ax_Spd_tg1 ,f_g = f_g, filtertype = 'acausal', valid = Spd_tg1< 100.0)



        
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego_VBOX_IMU-t_origin, ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego_VBOX_GPS-t_origin, ax_ego_VBOX_GPS ,'b', label='ax (VBOX)' )           
        
        if (Time_ax_WheelbasedVehSpd is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_WheelbasedVehSpd-t_origin, ax_WheelbasedVehSpd ,'c', label='ax CCVS1' ) 
            
        if (Time_ax_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego-t_origin, ax_ego ,'c' , label='ax (calc.)' )
            
        #if not Time_ax_ForwandVehicle is None:
        #    ax.plot(Time_ax_ForwandVehicle-t_origin, ax_ForwandVehicle ,'m', label='ax ACC1' )   
            
        if not Time_ax_Spd_tg1 is None:  
            ax.plot(Time_ax_Spd_tg1-t_origin, ax_Spd_tg1 ,'m', label='ax forward vehicle (Racelogic)' )           
        
        
        # ---------------------------------------------------  
        ax.plot(Time_XBR_d0B_s2A-t_origin, ExtlAccelerationDemand_d0B_s2A ,'r', label='XBR' )           
          
          
    
        # ---------------------------------------------------  
        #self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        self.set_description(ax, ylabel='m/s$^2$', ylim=(ax_min,ax_max)) 


    # ==========================================================
    def _subplot_EngTorque(self, ax, t_origin, show_only_one_ax_signal = True,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''
        FLR20_sig = self.FLR20_sig

        a_min = -10.0
        a_max = 110.0
        
        #FLR20_sig = self.FLR20_sig
        
        Time_EngRqedTorque_TorqueLimit_d00_s2A    = FLR20_sig['J1939']["Time_EngRqedTorque_TorqueLimit_d00_s2A"]
        EngRqedTorque_TorqueLimit_d00_s2A         = FLR20_sig['J1939']["EngRqedTorque_TorqueLimit_d00_s2A"]

        Time_ActualEngPercentTorque_s00           = FLR20_sig['J1939']["Time_ActualEngPercentTorque_s00"]
        ActualEngPercentTorque_s00                = FLR20_sig['J1939']["ActualEngPercentTorque_s00"]

        Time_DriversDemandEngPercentTorque_s00    = FLR20_sig['J1939']["Time_DriversDemandEngPercentTorque_s00"]
        DriversDemandEngPercentTorque_s00         = FLR20_sig['J1939']["DriversDemandEngPercentTorque_s00"]

        Time_EngRqedTorque_TorqueLimit_d00_s0B    = FLR20_sig['J1939']["Time_EngRqedTorque_TorqueLimit_d00_s0B"]
        EngRqedTorque_TorqueLimit_d00_s0B         = FLR20_sig['J1939']["EngRqedTorque_TorqueLimit_d00_s0B"]

        
                
        # ---------------------------------------------------  
        if Time_EngRqedTorque_TorqueLimit_d00_s2A is not None:
            ax.plot(Time_EngRqedTorque_TorqueLimit_d00_s2A-t_origin, EngRqedTorque_TorqueLimit_d00_s2A ,'r', label='ACCRqst' )           
        ax.plot(Time_ActualEngPercentTorque_s00-t_origin, ActualEngPercentTorque_s00 ,'b', label='ActEng' )           
        ax.plot(Time_DriversDemandEngPercentTorque_s00-t_origin, DriversDemandEngPercentTorque_s00 ,'k', label='DrvDmd' )
        
        #if Time_EngRqedTorque_TorqueLimit_d00_s0B is not None:           
        #    ax.plot(Time_EngRqedTorque_TorqueLimit_d00_s0B-t_origin, EngRqedTorque_TorqueLimit_d00_s0B ,'k', label='BrakeRqst' )           
           
        '''
        # Marker + Text - XBR_ExtAccelDem
        FmtStr='%3.1f'
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_warning, LineStyle='gd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_braking, LineStyle='bd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_emergency, LineStyle='rd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_impact, LineStyle='yd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_ego_stopped, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_relaxed, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
   
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (AEBS_Attr.Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_IMU-t_origin, AEBS_Attr.ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (AEBS_Attr.Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_GPS-t_origin, AEBS_Attr.ax_ego_VBOX_GPS ,'c', label='ax (VBOX)' )           
    
        
        
        
        if (AEBS_Attr.Time_v_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego-t_origin, AEBS_Attr.ax_ego ,'m' , label='ax (calc.)' )
        '''

        # ---------------------------------------------------  
        #self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        self.set_description(ax, ylabel='%', ylim=(a_min,a_max)) 
        
    # ==========================================================
    def _subplot_RetarderTorque(self, ax, t_origin, show_only_one_ax_signal = True,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''
        FLR20_sig = self.FLR20_sig

        a_min = -110.0
        a_max =   10.0
        
        #FLR20_sig = self.FLR20_sig
        
        Time_EngRqedTorque_TorqueLimit_d10_s2A    = FLR20_sig['J1939']["Time_EngRqedTorque_TorqueLimit_d10_s2A"]
        EngRqedTorque_TorqueLimit_d10_s2A         = FLR20_sig['J1939']["EngRqedTorque_TorqueLimit_d10_s2A"]

        Time_EngRqedTorque_TorqueLimit_d29_s2A           = FLR20_sig['J1939']["Time_EngRqedTorque_TorqueLimit_d29_s2A"]
        EngRqedTorque_TorqueLimit_d29_s2A                = FLR20_sig['J1939']["EngRqedTorque_TorqueLimit_d29_s2A"]

        Time_EngRqedTorque_TorqueLimit_d29_s10    = FLR20_sig['J1939']["Time_EngRqedTorque_TorqueLimit_d29_s10"]
        EngRqedTorque_TorqueLimit_d29_s10         = FLR20_sig['J1939']["EngRqedTorque_TorqueLimit_d29_s10"]

                
        # --------------------------------------------------- 
        if Time_EngRqedTorque_TorqueLimit_d10_s2A is not None:
            ax.plot(Time_EngRqedTorque_TorqueLimit_d10_s2A-t_origin, EngRqedTorque_TorqueLimit_d10_s2A ,'r', label='Rqst d10_s2A' )           
        
        if Time_EngRqedTorque_TorqueLimit_d29_s2A is not None:
            ax.plot(Time_EngRqedTorque_TorqueLimit_d29_s2A-t_origin, EngRqedTorque_TorqueLimit_d29_s2A ,'b', label='Rqst d29_s2A' )   
            
        if Time_EngRqedTorque_TorqueLimit_d29_s10 is not None: 
            ax.plot(Time_EngRqedTorque_TorqueLimit_d29_s10-t_origin, EngRqedTorque_TorqueLimit_d29_s10 ,'k', label='Rqst d29_s10' )           
           
        '''
        # Marker + Text - XBR_ExtAccelDem
        FmtStr='%3.1f'
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_warning, LineStyle='gd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_braking, LineStyle='bd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_emergency, LineStyle='rd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_impact, LineStyle='yd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_ego_stopped, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_relaxed, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
   
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (AEBS_Attr.Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_IMU-t_origin, AEBS_Attr.ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (AEBS_Attr.Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_GPS-t_origin, AEBS_Attr.ax_ego_VBOX_GPS ,'c', label='ax (VBOX)' )           
    
        
        
        
        if (AEBS_Attr.Time_v_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego-t_origin, AEBS_Attr.ax_ego ,'m' , label='ax (calc.)' )
        '''

        # ---------------------------------------------------  
        #self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        self.set_description(ax, ylabel='%', ylim=(a_min,a_max)) 
    # ==========================================================
    def _subplot_DriverDemand(self, ax, t_origin,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''
        FLR20_sig = self.FLR20_sig

        a_min = -10.0
        a_max = 110.0
        
        #FLR20_sig = self.FLR20_sig
        
        Time_AccelPedalPos1_s00    = FLR20_sig['J1939']["Time_AccelPedalPos1_s00"]
        AccelPedalPos1_s00         = FLR20_sig['J1939']["AccelPedalPos1_s00"]
        
        Time_BrakePedalPos_s0B    = FLR20_sig['J1939']["Time_BrakePedalPos_s0B"]
        BrakePedalPos_s0B         = FLR20_sig['J1939']["BrakePedalPos_s0B"]
       
       
        '''
        _, J1939["XBREBIMode_d0B_s2A"]                          = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBREBIMode_d0B_s2A")
        _, J1939["XBRPriority_d0B_s2A"]                         = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRPriority_d0B_s2A")
        _, J1939["XBRCtrlMode_d0B_s2A"]                         = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRCtrlMode_d0B_s2A")
        _, J1939["XBRUrgency_d0B_s2A"]                          = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRUrgency_d0B_s2A")
        _, J1939["XBRMessageCounter_d0B_s2A"]                   = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRMessageCounter_d0B_s2A")
        _, J1939["XBRMessageChecksum_d0B_s2A"]                  = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRMessageChecksum_d0B_s2A")
        '''
        
        # ---------------------------------------------------  
        ax.plot(Time_AccelPedalPos1_s00-t_origin, AccelPedalPos1_s00 ,'r', label='AccelPedalPos1' )   
        ax.plot(Time_BrakePedalPos_s0B-t_origin, BrakePedalPos_s0B ,'b', label='BrakePedalPos' )           
           
        '''
        # Marker + Text - XBR_ExtAccelDem
        FmtStr='%3.1f'
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_warning, LineStyle='gd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_braking, LineStyle='bd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_emergency, LineStyle='rd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_impact, LineStyle='yd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_ego_stopped, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_relaxed, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
   
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (AEBS_Attr.Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_IMU-t_origin, AEBS_Attr.ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (AEBS_Attr.Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_GPS-t_origin, AEBS_Attr.ax_ego_VBOX_GPS ,'c', label='ax (VBOX)' )           
    
        
        
        
        if (AEBS_Attr.Time_v_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego-t_origin, AEBS_Attr.ax_ego ,'m' , label='ax (calc.)' )
        '''

        # ---------------------------------------------------  
        #self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        self.set_description(ax, ylabel='%', ylim=(a_min,a_max)) 

    # ==========================================================
    def _subplot_XBR(self, ax, t_origin, show_only_one_ax_signal = True,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''
        FLR20_sig = self.FLR20_sig

        aXBR_min = -4.0
        aXBR_max = 2.0
        
        #FLR20_sig = self.FLR20_sig
        
        Time_XBR_d0B_s2A                        = FLR20_sig['J1939']["Time_XBR_d0B_s2A"]
        ExtlAccelerationDemand_d0B_s2A    = FLR20_sig['J1939']["ExtlAccelerationDemand_d0B_s2A"]

        # host vehicle acceleration 
        Time_ax_ego, ax_ego = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='v_ego')

        Time_ax_ego_VBOX_GPS, ax_ego_VBOX_GPS = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_GPS',smooth_filter=True, f_g=1.0)
        Time_ax_ego_VBOX_IMU, ax_ego_VBOX_IMU = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_IMU',smooth_filter=True, f_g=10.0)
        
        

        '''
        _, J1939["XBREBIMode_d0B_s2A"]                          = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBREBIMode_d0B_s2A")
        _, J1939["XBRPriority_d0B_s2A"]                         = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRPriority_d0B_s2A")
        _, J1939["XBRCtrlMode_d0B_s2A"]                         = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRCtrlMode_d0B_s2A")
        _, J1939["XBRUrgency_d0B_s2A"]                          = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRUrgency_d0B_s2A")
        _, J1939["XBRMessageCounter_d0B_s2A"]                   = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRMessageCounter_d0B_s2A")
        _, J1939["XBRMessageChecksum_d0B_s2A"]                  = kbtools.GetSignal(Source, "t_XBR_d0B_s2A", "XBRMessageChecksum_d0B_s2A")
        '''
        
        # ---------------------------------------------------  
        ax.plot(Time_XBR_d0B_s2A-t_origin, ExtlAccelerationDemand_d0B_s2A ,'r', label='XBR' )           
          
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego_VBOX_IMU-t_origin, ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego_VBOX_GPS-t_origin, ax_ego_VBOX_GPS ,'c', label='ax (VBOX)' )           
        
        if (Time_ax_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(Time_ax_ego-t_origin, ax_ego ,'m' , label='ax (calc.)' )


           
        '''
        # Marker + Text - XBR_ExtAccelDem
        FmtStr='%3.1f'
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_warning, LineStyle='gd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_braking, LineStyle='bd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_emergency, LineStyle='rd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_impact, LineStyle='yd',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_ego_stopped, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.XBR_ExtAccelDem_at_t_relaxed, LineStyle='m*',FmtStr=FmtStr, yOffset=yOffset, ylim=(aXBR_min,aXBR_max))
   
        # ---------------------------------------------------  
        ax_signal_found = False
        
        if (AEBS_Attr.Time_ax_ego_VBOX_IMU is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_IMU-t_origin, AEBS_Attr.ax_ego_VBOX_IMU ,'b' , label='ax (IMU)')

        if (AEBS_Attr.Time_ax_ego_VBOX_GPS is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego_VBOX_GPS-t_origin, AEBS_Attr.ax_ego_VBOX_GPS ,'c', label='ax (VBOX)' )           
    
        
        
        
        if (AEBS_Attr.Time_v_ego is not None) and (not ax_signal_found):
            if show_only_one_ax_signal:
                ax_signal_found = True
            ax.plot(AEBS_Attr.Time_ax_ego-t_origin, AEBS_Attr.ax_ego ,'m' , label='ax (calc.)' )
        '''

        # ---------------------------------------------------  
        #self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max)) 
        
    # ==========================================================
    def _subplot_ACC_Flags(self, ax, t_origin):
        '''
           Create subplot for  Driver Override 1 (flags)
        
        '''
        
        FLR20_sig = self.FLR20_sig
        
        
        Time_ACCDistanceAlertSignal_s2A   = FLR20_sig['J1939']["Time_ACCDistanceAlertSignal_s2A"]
        ACCDistanceAlertSignal_s2A        = FLR20_sig['J1939']["ACCDistanceAlertSignal_s2A"]

        Time_ACCSystemShutoffWarning_s2A  = FLR20_sig['J1939']["Time_ACCSystemShutoffWarning_s2A"]
        ACCSystemShutoffWarning_s2A       = FLR20_sig['J1939']["ACCSystemShutoffWarning_s2A"]

        Time_ACCTargetDetected_s2A        = FLR20_sig['J1939']["Time_ACCTargetDetected_s2A"]
        ACCTargetDetected_s2A             = FLR20_sig['J1939']["ACCTargetDetected_s2A"]
   
        
        
        ax.plot(Time_ACCSystemShutoffWarning_s2A-t_origin,  ACCSystemShutoffWarning_s2A,    'b', label= 'ShutoffWarning' )
        ax.plot(Time_ACCDistanceAlertSignal_s2A-t_origin,   ACCDistanceAlertSignal_s2A+2.0, 'r', label= 'DistanceAlertSignal' )
        ax.plot(Time_ACCTargetDetected_s2A-t_origin,        ACCTargetDetected_s2A+4.0,      'c', label= 'TargetDetected' )
        
        
        #ax.plot(FLR20_sig["J1939"]["Time_ReverseGearDetected"]-t_origin, FLR20_sig["J1939"]["ReverseGearDetected"]+4.0,'m', label= 'ReverseGearDetected' )
       
        '''
        if FLR20_sig["J1939"]["Time_DriverActDemand"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DriverActDemand"]-t_origin,     FLR20_sig["J1939"]["DriverActDemand"]+6.0,    'm', label= 'DriverActDemand' )
        if FLR20_sig["J1939"]["Time_EBSBrakeSwitch"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_EBSBrakeSwitch"]-t_origin,      FLR20_sig["J1939"]["EBSBrakeSwitch"]+4.0,     'c', label= 'EBSBrakeSwitch' )
        if FLR20_sig["J1939"]["Time_DirIndL_b"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DirIndL_b"]-t_origin,           FLR20_sig["J1939"]["DirIndL_b"]+2.0,          'r', label= 'DirIndL_b' )
        if FLR20_sig["J1939"]["Time_DirIndR_b"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DirIndR_b"]-t_origin,           FLR20_sig["J1939"]["DirIndR_b"],              'b', label= 'DirIndR_b' )
        '''
 
        ax.set_yticks(range(8)) 
        label  = ['Off','ShutoffWarning On']
        label += ['Off','DistanceAlertSignal On']
        label += ['Off','TargetDetected On']
        #label += ['Off','DriverActDemand On']
        #label += ['Off','ReverseGearDetected On']
        ax.set_yticklabels(label,fontsize='small')

        
        #self.set_description(ax, ylabel=None, ylim=(-0.1,8.1), grid='special')
        self.set_description(ax, ylabel=None, ylim=(-0.1,8.1))
       




''' ============================================================================================== '''
class cEvalJ1939ACC():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
        self.myname = 'EvalJ1939ACC'         # name of this user specific evaluation
        self.H4E = {}                    # H4E hunt4event directory


        self.enable_ACC_plots = True

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
        pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
      
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
      
        print "EvalJ1939ACC::Init()"
          
        # ---------------------------------------------------------------
        # TODO 
        # config -> J1939_AEBS_SA
        self.config = {}
        self.config["J1939_AEBS_SourceAddress"] = int("0x2A",16)  
        if 'J1939_AEBS_SourceAddress' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['J1939_AEBS_SourceAddress'],str):
                try:
                    J1939_AEBS_SourceAddress =  int(conf_DAS_eval['J1939_AEBS_SourceAddress'],16)  
                    self.config["J1939_AEBS_SourceAddress"] = J1939_AEBS_SourceAddress
                except:
                    pass
       
        print "  J1939_AEBS_SourceAddress = 0x%X"%self.config["J1939_AEBS_SourceAddress"]

      
      
        # ----------------------------------------------------------------------
        # LDWS outputs
        default_value = []
        self.H4E['AdaptiveCruiseCtrlMode'] = kbtools.cHunt4Event('multi_state','AEBS1 AdaptiveCruiseCtrlMode',default_value)
      
      
        # ---------------------------------------------------------------
        # load events - required for "Report_Only"
        if load_event:
            for key in self.H4E.keys():
                self.H4E[key].load_event(key)
      
      
      
    
    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
        for key in self.H4E.keys():
            self.H4E[key].reinit()



    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        print "============================================"
        print "EvalJ1939ACC::process()"
        
        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        try:
            
            FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source,config=self.config)
            # store FLR20 signals to be used in callback function "callback_rising_edge"
            self.FLR20_sig = FLR20_sig
            
        except Exception, e:
            print "error with extract FLR20 signals from measurement: ",e.message
            traceback.print_exc(file=sys.stdout) 
            return
 
        print "process(): FileName: ", self.FLR20_sig['FileName']
 
        Time_AdaptiveCruiseCtrlMode_s2A   = FLR20_sig['J1939']["Time_AdaptiveCruiseCtrlMode_s2A"]
        AdaptiveCruiseCtrlMode_s2A        = FLR20_sig['J1939']["AdaptiveCruiseCtrlMode_s2A"]
        
      
        self.H4E['AdaptiveCruiseCtrlMode'].process(Time_AdaptiveCruiseCtrlMode_s2A, AdaptiveCruiseCtrlMode_s2A, Source)
       
           
        # ----------------------------------------
        # plotting
        if self.enable_ACC_plots:
            enable_png_extract = True     # snapshots from video
            show_figures = False          # open matlablib figures

            PngFolder = r'.\ACC_png'
            Description = "Automatic Evaluation"
            
            if Time_AdaptiveCruiseCtrlMode_s2A is not None:
                t_start = Time_AdaptiveCruiseCtrlMode_s2A[0]
                t_end = Time_AdaptiveCruiseCtrlMode_s2A[-1]
            
                PlotAEBS = cPlotJ1939ACC(FLR20_sig, t_event=t_start, xlim=(0,(t_end-t_start)*1.3), PngFolder = PngFolder, Description=Description, show_figures=show_figures)
                PlotAEBS.PlotAll(enable_png_extract=enable_png_extract)

           
        print "end process - EvalJ1939ACC"
      
    # ------------------------------------------------------------------------------------------
    def finish(self):          # end of recording
        for key in self.H4E.keys():
            self.H4E[key].finish()
      
        # save events   
        for key in self.H4E.keys():
            self.H4E[key].save_event(key)
        

    # ------------------------------------------------------------------------------------------
    def report_init(self):     # prepare for report - input tex file to main
        self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
        pass  

    # ------------------------------------------------------------------------------------------
    def report(self):          # report events
        fill_table_array_into_report = True
        
        self.kb_tex.workingfile('%s.tex'%self.myname)
      
        self.kb_tex.tex('\n\\newpage\\section{EvalJ1939ACC}')
         
   
        # online ECU   
        self.kb_tex.tex('\n\\subsection{EvalJ1939ACC}')
        self.kb_tex.tex('\nAdaptiveCruiseCtrlMode: %d entries; '% self.H4E['AdaptiveCruiseCtrlMode'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        #self.kb_tex.tex('\nDFM green button: %d entries'% self.H4E['DFM_green_button'].n_entries_EventList())
        if fill_table_array_into_report:
            self.kb_tex.table(self.H4E['AdaptiveCruiseCtrlMode'].table_array())
            #self.kb_tex.table(self.H4E['DFM_green_button'].table_array())
      
        self.kb_tex.tex('\n \n\\bigskip \EvalJ1939ACC-finished')
      
     
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)
        
        # switches
        # add partial_brake and emergency_brake spreadsheets
        #braking_spreadsheets = False

        # new format 
        AddColsFormat = {}
             
        WriteExcel = kbtools.cWriteExcel()

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        
        # ---------------------------------------------------
        # online
        AddCols_online = []
        WriteExcel.add_sheet_out_table_array('AdaptiveCruiseCtrlMode',self.H4E['AdaptiveCruiseCtrlMode'].table_array2(AddCols_online,AddColsFormat))
        
        
 
        # -------------------------------------------------
        # write Excel file
        ExcelFilename = "EvalJ1939ACC_results.xls"
        if self.src_dir_meas is not None:
            ExcelFilename = "EvalJ1939ACC_results_%s.xls"%os.path.basename(self.src_dir_meas) 
        WriteExcel.save(ExcelFilename)
       
      
        
        
        print "excel_export() finish"
      
#-------------------------------------------------------------------------      









