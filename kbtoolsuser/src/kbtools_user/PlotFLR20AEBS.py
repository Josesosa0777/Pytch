#
#  FLR20 AC100 
#  AEBS use case - Approaching stationary object (Bendix/TRW version)
#
#  Ulrich Guecker
#
#  2014-11-26  AEBS_Homologation
#  2013-07-17
#  2013-06-07
# ---------------------------------------------------------------------------------------------

import os
#import time
import numpy as np
import pylab as pl
import sys, traceback

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import kbtools
import kbtools_user

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

def check_AEBS_Attr_AEBS_Track(AEBS_Attr):
    if (AEBS_Attr.AEBS_Track is not None) and (AEBS_Attr.AEBS_Track['Time'] is not None):
        return True
    else:
        return False
    
# ==========================================================
# ==========================================================
class cPlotFLR20AEBS(kbtools_user.cPlotBase):
   
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
            
        super(cPlotFLR20AEBS,self).__init__(PngFolder=self.PngFolder,show_figures=show_figures)
        
        self.input_mode = 'FLR20'   # "SilLDWS_C"
        
    # ==========================================================
    def _Calc_AEBS_Attr(self,mode = 'VBOX', t_event=None):
        '''
            Calculate AEBS characteristic attributes, 
            e.g. distance, relative velocity at start of warning, partial and emergency braking 
        '''
            
        if t_event is None:
            t_event = self.t_event
            
        AEBS_Attr = kbtools_user.cCalcAEBSAttributes(self.FLR20_sig, self.input_mode, mode, t_event)   
        
        return AEBS_Attr
     
    # ==========================================================
    def _subplot_AEBS_Attr_AEBSState(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for AEBS_Attr.AEBS State
        
        '''
    
    
        ax.plot(AEBS_Attr.Time_ABESState-t_origin, AEBS_Attr.ABESState,'b', label= 'AEBS State' )
 
        ax.set_yticks(range(8))   
        label1 = ['Not ready (0)','Temp. not avail. (1)','Deact. by driver (2)','Ready (3)']
        label2 = ['Driver override (4)','collision warning (5)','partial braking (6)','emergency braking (7)','(8)','(9)','(10)','(11)','(12)','(13)']
        label3 = ['Error (14)','NotAvailable (15)']
        ax.set_yticklabels(label1+label2+label3)

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
        

        self.set_description(ax, ylabel=None, ylim=(-0.1,8.1), grid='special')
        
       
    # ==========================================================
    def _subplot_AEBS_Attr_velocity(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.v_ego, AEBS_Attr.v_target
        
        '''
        v_kph_min = -10.0
        v_kph_max = 100.0

        v_unit = "km/h" 
 
        
        ax.plot(AEBS_Attr.Time_v_ego-t_origin, AEBS_Attr.v_ego,'b', label='v host(%s)'%AEBS_Attr.mode)
         
        if AEBS_Attr.Time_v_target is not None:
            ax.plot(AEBS_Attr.Time_v_target-t_origin,AEBS_Attr.v_target,'r', label = 'v target(%s)'%AEBS_Attr.mode)
        
        
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
 
 
        self.set_description(ax, ylabel='v [%s]'%v_unit, ylim=(v_kph_min,v_kph_max), grid='special') 
 
    # ==========================================================
    def _subplot_AEBS_Attr_velocity_vs_distance(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.v_ego, AEBS_Attr.v_target
        
        '''
        v_kph_min = -10.0
        v_kph_max = 100.0

        dx_min = -10.0
        dx_max = 80.0
        
        v_unit = "km/h" 
        dx_unit = "m"
 
        v_ego_resampled = kbtools.resample(AEBS_Attr.Time_v_ego,AEBS_Attr.v_ego, AEBS_Attr.Time_dx)
        
        ax.plot(AEBS_Attr.dx, v_ego_resampled,'b', label='v host(%s)'%AEBS_Attr.mode)
     
        # Marker + Text - v_ego
        FmtStr = '%3.1fkm/h@%3.1fm'
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_warning,AEBS_Attr.v_ego_at_t_warning, LineStyle='gd',FmtStr=FmtStr, yOffset=2.0, label='WP1')
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_braking,AEBS_Attr.v_ego_at_t_braking, LineStyle='bd',FmtStr=FmtStr, yOffset=2.0, label='WP2')
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_emergency,AEBS_Attr.v_ego_at_t_emergency, LineStyle='rd',FmtStr=FmtStr, yOffset=2.0, label='EBP')
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_impact,AEBS_Attr.v_ego_at_t_impact, LineStyle='yd',FmtStr=FmtStr, yOffset=2.0, label='impact')
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_ego_stopped,AEBS_Attr.v_ego_at_t_ego_stopped, LineStyle='m*',FmtStr=FmtStr, yOffset=2.0, label='avoid.')
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.dx_at_t_relaxed,AEBS_Attr.v_ego_at_t_relaxed, LineStyle='m*',FmtStr=FmtStr, yOffset=2.0, label='avoid.')
                
           
        # Marker + Text - v_target
        if 0:
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
 
 
        self.set_description(ax, ylabel='v [%s]'%v_unit, ylim=(v_kph_min,v_kph_max), xlabel='dx [%s]'%dx_unit, xlim=(dx_max, dx_min))

    # ==========================================================
    def _subplot_AEBS_Attr_position(self, ax, AEBS_Attr, t_origin,mark_is_video_associated=False):
        '''
           Create subplot for  AEBS_Attr.dx
        
        '''
        #dx_unit = "m"
 
        dx_min = -10.0
        dx_max = 150.0        
        
        if AEBS_Attr.Time_dx is not None:
            ax.plot(AEBS_Attr.Time_dx-t_origin, AEBS_Attr.dx,'b', label='dx (%s)'%AEBS_Attr.mode)
        
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
       
        self.set_description(ax, ylabel='dx [m]', ylim=(dx_min,dx_max), grid='special') 
        
    # ==========================================================
    def _subplot_AEBS_Attr_position_TrackById(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  
               FLR20 radar track
               FLR20 video associated track
               FLC20 video object
               FLR20 CW track
               FLR20 CW track video confirmed
               FLR20 targets (detections)
        
        '''
        #dx_unit = "m"
 
        dx_min = -10.0
        dx_max = 200.0
        
          
        
             
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            t_common = AEBS_Attr.AEBS_Track['Time']
                
            # FLR20 targets (detections) 
            ax.plot(t_common-t_origin, AEBS_Attr.AEBS_Track['Target']['range'],'bx',label='targets')
            
            # FLR20 radar track
            ax.plot(t_common-t_origin, AEBS_Attr.AEBS_Track['Track']['dx'],'b', label='track (%3.1f m) (id: %d)'%(AEBS_Attr.AEBS_tr_start_dx,AEBS_Attr.AEBS_tr_id_at_t_warning))

            # FLC20 video object
            if 'Longitudinal_Distance' in AEBS_Attr.AEBS_Track['VideoObj']: 
                ax.plot(t_common-t_origin, AEBS_Attr.AEBS_Track['VideoObj']['Longitudinal_Distance'],'m', label='video obj. (%3.1fm)'%AEBS_Attr.AEBS_video_start_dx)
            
            # FLR20 track video associated
            track_dx_vidconf = AEBS_Attr.AEBS_Track['Track']['dx']*(AEBS_Attr.AEBS_Track['Track']['is_video_associated']>0)
            ax.plot(t_common-t_origin, track_dx_vidconf,'r', label='track vid. ass. (%3.1f m)'%AEBS_Attr.AEBS_tr_is_video_associated_start_dx)

            # FLR20 track video confirmed
            if AEBS_Attr.AEBS_tr_is_video_confirmed is not None:
                tr_is_video_confirmed_dx = AEBS_Attr.AEBS_Track['Track']['dx']*(AEBS_Attr.AEBS_tr_is_video_confirmed>0)
                ax.plot(t_common-t_origin, tr_is_video_confirmed_dx,'c', label='track vid. conf. (%3.1f m)'%AEBS_Attr.AEBS_tr_is_video_confirmed_start_dx)

                        
            # CW track
            cw_track_dx = AEBS_Attr.AEBS_Track['Track']['dx']*(AEBS_Attr.AEBS_Track['Track']['CW_track']>0)
            ax.plot(t_common-t_origin, cw_track_dx,'k', label='CW (%3.1f m)'%AEBS_Attr.cw_start_dx)
               
            # CW track video confirmed
            #if AEBS_Attr.Time_cw_vidconf is not None:
            #    dx_cw_vidconf =  AEBS_Attr.AEBS_Track['Track']['dx']*(kbtools.resample(AEBS_Attr.Time_cw_vidconf, AEBS_Attr.cw_vidconf, t_common)>0) 
            #    ax.plot(t_common-t_origin, dx_cw_vidconf,'y', label='CW vid. conf. (%3.1f m)'%AEBS_Attr.cw_vidconf_start_dx)
          
        
        # --------------------------------------------------- 
        # Set markers at start of each track
        
        # FLR20 radar track
        if AEBS_Attr.AEBS_tr_start_time is not None:
            self.mark_point(ax,AEBS_Attr.AEBS_tr_start_time-t_origin,AEBS_Attr.AEBS_tr_start_dx, LineStyle='bd',FmtStr='%3.1f', yOffset=10.0)
        
        # FLC20 video object   
        if AEBS_Attr.AEBS_video_start_time is not None:
            self.mark_point(ax,AEBS_Attr.AEBS_video_start_time-t_origin,AEBS_Attr.AEBS_video_start_dx, LineStyle='md',FmtStr='%3.1f', yOffset=10.0)
       
        # FLR20 track video associated     
        if AEBS_Attr.AEBS_tr_is_video_associated_start_time is not None:
            self.mark_point(ax,AEBS_Attr.AEBS_tr_is_video_associated_start_time-t_origin,AEBS_Attr.AEBS_tr_is_video_associated_start_dx, LineStyle='rd',FmtStr='%3.1f', yOffset=10.0)
        
        # FLR20 track video associated     
        if AEBS_Attr.AEBS_tr_is_video_confirmed_start_time is not None:
            self.mark_point(ax,AEBS_Attr.AEBS_tr_is_video_confirmed_start_time-t_origin,AEBS_Attr.AEBS_tr_is_video_confirmed_start_dx, LineStyle='cd',FmtStr='%3.1f', yOffset=10.0)
        
        # CW track
        if AEBS_Attr.cw_start_time is not None:
            self.mark_point(ax,AEBS_Attr.cw_start_time-t_origin,AEBS_Attr.cw_start_dx, LineStyle='kd',FmtStr='%3.1f', yOffset=10.0)
         
        # CW track video confirmed
        #if AEBS_Attr.cw_vidconf_start_time is not None:
        #    self.mark_point(ax,AEBS_Attr.cw_vidconf_start_time-t_origin,AEBS_Attr.cw_vidconf_start_dx, LineStyle='yd',FmtStr='%3.1f', yOffset=10.0)
        
               
        self.set_description(ax, ylabel='dx [m]', ylim=(dx_min,dx_max),grid='special') 
        #ax.set_xlim(-40,10)  
        #ax.set_ylim(-10,500)  
        
    # ==========================================================
    def _subplot_AEBS_Attr_FLC20_Number_Of_Objects(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.dx
        
        '''
        
        '''
        if AEBS_Attr.Time_dx is not None:
            ax.plot(AEBS_Attr.Time_dx-t_origin, AEBS_Attr.dx,'b', label='dx (%s)'%AEBS_Attr.mode)
        
        Time_tr0_dx = AEBS_Attr.FLR20_sig['Tracks'][0]['Time']
        tr0_dx = AEBS_Attr.FLR20_sig['Tracks'][0]['dx']
        if Time_tr0_dx is not None:
            ax.plot(Time_tr0_dx-t_origin, tr0_dx,'r', label='tr0_dx')
        '''
        
        Time_Number_Of_Objects = AEBS_Attr.FLR20_sig['FLC20_CAN']['Time_Number_Of_Objects']
        Number_Of_Objects = AEBS_Attr.FLR20_sig['FLC20_CAN']['Number_Of_Objects']
        if Time_Number_Of_Objects is not None:
            ax.plot(Time_Number_Of_Objects-t_origin, Number_Of_Objects,'b', label='Number_Of_Objects')
            
        self.set_description(ax, ylabel='', ylim=(0,10), grid='special')
     
    # ==========================================================
    def _subplot_AEBS_Attr_FLC20_Detection_Score(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.dx
        
        '''
        
        '''
        if AEBS_Attr.Time_dx is not None:
            ax.plot(AEBS_Attr.Time_dx-t_origin, AEBS_Attr.dx,'b', label='dx (%s)'%AEBS_Attr.mode)
        
        Time_tr0_dx = AEBS_Attr.FLR20_sig['Tracks'][0]['Time']
        tr0_dx = AEBS_Attr.FLR20_sig['Tracks'][0]['dx']
        if Time_tr0_dx is not None:
            ax.plot(Time_tr0_dx-t_origin, tr0_dx,'r', label='tr0_dx')
        '''
        
        Time_Detection_Score = AEBS_Attr.FLR20_sig['FLC20_CAN'][0]['Time_Detection_Score']
        Detection_Score = AEBS_Attr.FLR20_sig['FLC20_CAN'][0]['Detection_Score']
        if Time_Detection_Score is not None:
            ax.plot(Time_Detection_Score-t_origin, Detection_Score,'b', label='Detection_Score')
            
        self.set_description(ax, ylabel='', ylim=None, grid='special')
     
    # ==========================================================
    def _subplot_AEBS_Attr_asso_target_index(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for asso_target_index
        
        '''
        
        #Time_t_asso_target_index   = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['Time']        
        #asso_target_index          = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['asso_target_index']
        
        try:
            Time_t_asso_target_index   = AEBS_Attr.FLR20_sig['Tracks'][0]['Time']        
            asso_target_index          = AEBS_Attr.FLR20_sig['Tracks'][0]['asso_target_index']
        except Exception, e:
            print "error - _subplot_AEBS_Attr_asso_target_index() ",e.message
            traceback.print_exc(file=sys.stdout)
            Time_t_asso_target_index = None  
            asso_target_index = None    
        
        
        
        
        
        
        if Time_t_asso_target_index is not None:
            ax.plot(Time_t_asso_target_index-t_origin, asso_target_index,'b', label='asso_target_index')
            
        if (AEBS_Attr.AEBS_Track is not None) and (AEBS_Attr.AEBS_Track['Time'] is not None):
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['asso_target_index'],'r')
        
            
        self.set_description(ax, ylabel='', ylim=(-0.5,64), grid='special')
        
    # ==========================================================
    def _subplot_AEBS_Attr_asso_video_ID(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for asso_video_ID
        
        '''
        
        #Time_asso_video_ID       = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['Time']        
        #asso_video_ID            = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['asso_video_ID']
       
       
        #Time_asso_video_ID       = AEBS_Attr.FLR20_sig['Tracks'][0]['Time']        
        #asso_video_ID            = AEBS_Attr.FLR20_sig['Tracks'][0]['asso_video_ID']
       
        Time_asso_video_ID       = AEBS_Attr.FLR20_sig['FLR20_CAN']['Tracks'][0]['Time_asso_video_ID']
        asso_video_ID            = AEBS_Attr.FLR20_sig['FLR20_CAN']['Tracks'][0]['asso_video_ID']
       
        print "Time_asso_video_ID",Time_asso_video_ID
        print "asso_video_ID",asso_video_ID
        
        
        if Time_asso_video_ID is not None:
            ax.plot(Time_asso_video_ID-t_origin, asso_video_ID,'b', label='asso_video_ID')
        
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['asso_video_ID'],'r')
                
            
        self.set_description(ax, ylabel='', ylim=(-0.5,64), grid='special')
  
    # ==========================================================
    def _subplot_AEBS_Attr_track0_ID(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for track0_ID
        
        '''
        
        #Time_asso_video_ID       = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['Time']        
        #asso_video_ID            = AEBS_Attr.FLR20_sig['PosMatrix']['CW']['asso_video_ID']
       
       
        
       
        try:
            Time_track0_ID       = AEBS_Attr.FLR20_sig['Tracks'][0]['Time']        
            track0_ID            = AEBS_Attr.FLR20_sig['Tracks'][0]['id']
        except Exception, e:
            print "error - _subplot_AEBS_Attr_asso_target_index() ",e.message
            traceback.print_exc(file=sys.stdout)
            Time_track0_ID = None  
            track0_ID = None  
       
        
        if Time_track0_ID is not None:
            ax.plot(Time_track0_ID-t_origin, track0_ID,'b', label='id')
            
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['id'],'r')

            
        self.set_description(ax, ylabel='', ylim=(-0.5,64), grid='special') 
    
    
    # ==========================================================
    def _subplot_AEBS_Attr_FLC20_CAN_Delay(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for track0_ID
        
        '''
         
        Time_CAN_Delay = AEBS_Attr.FLR20_sig['FLC20_CAN']["Time_CAN_Delay"]
        CAN_Delay      = AEBS_Attr.FLR20_sig['FLC20_CAN']["CAN_Delay"]               
  
        local_xlim = self._xlim_to_use
  
        if Time_CAN_Delay is not None:
            
            CAN_Delay_at_t_ref = kbtools.GetPreviousSample(Time_CAN_Delay, CAN_Delay,t_origin,shift=0)   
            
            t_start = local_xlim[0]+t_origin
            t_stop  = local_xlim[1]+t_origin
            idx = np.argwhere(np.logical_and(t_start<=Time_CAN_Delay,Time_CAN_Delay<t_stop))
            tmp_Time_CAN_Delay = Time_CAN_Delay[idx]
            tmp_CAN_Delay = CAN_Delay[idx]
            
            t_max_CAN_Delay = tmp_Time_CAN_Delay[np.argmax(tmp_CAN_Delay)]
            max_CAN_Delay = np.max(tmp_CAN_Delay)
            
            t_min_CAN_Delay = tmp_Time_CAN_Delay[np.argmin(tmp_CAN_Delay)]
            min_CAN_Delay = np.min(tmp_CAN_Delay)
            
            mean_CAN_Delay = np.mean(tmp_CAN_Delay)
         
        
            ax.plot(Time_CAN_Delay-t_origin, CAN_Delay,'bx-',label='CAN_Delay  (%5.3f s) mean=%5.3f s, min/max= %5.3f s/%5.3f s'%(CAN_Delay_at_t_ref,mean_CAN_Delay,min_CAN_Delay,max_CAN_Delay))
            
            
            ax.plot(0.0,CAN_Delay_at_t_ref,'dm')
            ax.text(0.0,CAN_Delay_at_t_ref,"  %5.3f s "%(CAN_Delay_at_t_ref))
      
            ax.plot(t_max_CAN_Delay-t_origin,max_CAN_Delay,'dm')
            ax.text(t_max_CAN_Delay-t_origin,max_CAN_Delay,"  %5.3f s "%(max_CAN_Delay))
      
            ax.plot(t_min_CAN_Delay-t_origin,min_CAN_Delay,'dm')
            ax.text(t_min_CAN_Delay-t_origin,min_CAN_Delay,"  %5.3f s "%(min_CAN_Delay))
        
            ax.hlines(mean_CAN_Delay,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="mean_CAN_Delay(%5.3f s)"%mean_CAN_Delay)
        
            
        self.set_description(ax, ylabel='[s]', ylim=(0.0, 0.4), grid='special',xlim=local_xlim) 

    # ==========================================================
    def _subplot_AEBS_Attr_FLC20_SamplingInterval(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for track0_ID
        
        '''
        
        # ---------------------------------------------------------------------
        # VideoPackts:
        # First packet: Video_Data_General_A    - FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        # Last packet:  Video_Lane_Next_Left_B  - FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        t_head   = AEBS_Attr.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
        cnt_head = AEBS_Attr.FLR20_sig["FLC20_CAN"]["Message_Counter_Video_Data_General_A"]

        t_tail   = AEBS_Attr.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
        cnt_tail = AEBS_Attr.FLR20_sig["FLC20_CAN"]["Message_Counter_Next_Left_B"]

       
        if (t_head is not None) and (t_tail is not None):
           
            local_xlim = self._xlim_to_use
            
            videopacket = kbtools_user.CFLC20FusionMsgArray(t_head, cnt_head, t_tail, cnt_tail)
            #t_videopacket = videopacket.t_head
            
            t_SamplingIntervals, SamplingIntervals = videopacket.getSamplingIntervals()
            
            
            SamplingInterval_at_t_ref = kbtools.GetPreviousSample(t_SamplingIntervals, SamplingIntervals,t_origin,shift=0)   
            
            t_start = local_xlim[0]+t_origin
            t_stop  = local_xlim[1]+t_origin
            idx = np.argwhere(np.logical_and(t_start<=t_SamplingIntervals,t_SamplingIntervals<t_stop))
            tmp_t_SamplingIntervals = t_SamplingIntervals[idx]
            tmp_SamplingIntervals = SamplingIntervals[idx]
            
            t_max_SamplingInterval = tmp_t_SamplingIntervals[np.argmax(tmp_SamplingIntervals)]
            max_SamplingInterval = np.max(tmp_SamplingIntervals)
            
            t_min_SamplingInterval = tmp_t_SamplingIntervals[np.argmin(tmp_SamplingIntervals)]
            min_SamplingInterval = np.min(tmp_SamplingIntervals)
            
            mean_SamplingInterval = np.mean(tmp_SamplingIntervals)
         
             
            if t_SamplingIntervals is not None:
                        
                ax.plot(t_SamplingIntervals-t_origin, SamplingIntervals,'bx-',label='SamplingInterval  (%5.3f s) mean=%5.3f s, min/max= %5.3f s/%5.3f s'%(SamplingInterval_at_t_ref,mean_SamplingInterval,min_SamplingInterval,max_SamplingInterval))
               
                ax.plot(0.0,SamplingInterval_at_t_ref,'dm')
                ax.text(0.0,SamplingInterval_at_t_ref,"  %5.3f s "%(SamplingInterval_at_t_ref))
              
                ax.plot(t_max_SamplingInterval-t_origin,max_SamplingInterval,'dm')
                ax.text(t_max_SamplingInterval-t_origin,max_SamplingInterval,"  %5.3f s "%(max_SamplingInterval))
              
                ax.plot(t_min_SamplingInterval-t_origin,min_SamplingInterval,'dm')
                ax.text(t_min_SamplingInterval-t_origin,min_SamplingInterval,"  %5.3f s "%(min_SamplingInterval))
              
                ax.hlines(mean_SamplingInterval,local_xlim[0],local_xlim[1],colors='k',linestyles='dashed',label="mean_SamplingInterval(%5.3f s)"%mean_SamplingInterval)
              
                
                    
                self.set_description(ax, ylabel='[s]', ylim=(0.0, 0.15), grid='special',xlim=local_xlim) 
       
    
    # ==========================================================
    def _subplot_AEBS_Attr_lateral_position(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.dy
        
        '''
        #dx_unit = "m"
 
        dy_min = -2.0
        dy_max =  2.0
        
        yOffset = (dy_max-dy_min)*0.1
        
        if AEBS_Attr.Time_dy is not None:
            ax.plot(AEBS_Attr.Time_dy-t_origin, AEBS_Attr.dy,'b', label='dy (%s)'%AEBS_Attr.mode)
         
        # Marker + Text
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.dy_at_t_warning, LineStyle='gd',FmtStr='%3.1f', yOffset=yOffset)
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.dy_at_t_braking, LineStyle='bd',FmtStr='%3.1f', yOffset=yOffset)
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.dy_at_t_emergency, LineStyle='rd',FmtStr='%3.1f', yOffset=yOffset)
        if AEBS_Attr.t_impact is not None:
            self.mark_point(ax,AEBS_Attr.t_impact-t_origin,AEBS_Attr.dy_at_t_impact, LineStyle='yd',FmtStr='%3.1f', yOffset=yOffset)
        elif AEBS_Attr.t_ego_stopped is not None:
            self.mark_point(ax,AEBS_Attr.t_ego_stopped-t_origin,AEBS_Attr.dy_at_t_ego_stopped, LineStyle='m*',FmtStr='%3.1f', yOffset=yOffset)
        elif AEBS_Attr.t_relaxed is not None:
            self.mark_point(ax,AEBS_Attr.t_relaxed-t_origin,AEBS_Attr.dy_at_t_relaxed, LineStyle='m*',FmtStr='%3.1f', yOffset=yOffset)
       
        self.set_description(ax, ylabel='dy [m]', ylim=(dy_min,dy_max), grid='special') 
        
    # ==========================================================
    def _subplot_AEBS_Attr_lateral_position_TrackById(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  
        
        '''
        #dx_unit = "m"
 
        dy_min = -3.0
        dy_max =  3.0
       
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            
            # Target detections   
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, -AEBS_Attr.AEBS_Track['Target']['range']*AEBS_Attr.AEBS_Track['Target']['angle']*np.pi/180.0,'bx',label='targets')
           
            # Video object
            if 'Right_Angle' in AEBS_Attr.AEBS_Track['VideoObj']:
                ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, -AEBS_Attr.AEBS_Track['Track']['dx']*AEBS_Attr.AEBS_Track['VideoObj']['Right_Angle'],'m',label='video right')
           
            if 'Left_Angle' in AEBS_Attr.AEBS_Track['VideoObj']:
                ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, -AEBS_Attr.AEBS_Track['Track']['dx']*AEBS_Attr.AEBS_Track['VideoObj']['Left_Angle'],'c',label='video left')
               
            # Track   
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['dy'],'b',label='track')
            
           
        
        self.set_description(ax, ylabel='dy [m]', ylim=(dy_min,dy_max), grid='special') 
        
    # ==========================================================
    def _subplot_AEBS_Attr_vRel_TrackById(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  
        
        '''
         
        dy_min = -30.0
        dy_max =  10.0
        
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            # Target detections     
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Target']['relative_velocitiy'],'bx',label='targets')
    
            # Video object         
            if 'Relative_Velocity' in AEBS_Attr.AEBS_Track['VideoObj']:
                ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['VideoObj']['Relative_Velocity'],'m',label='video')
            
            # Track
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['vr'],'b',label='track')
                 
       
        self.set_description(ax, ylabel='vRel [m/s]', ylim=(dy_min,dy_max), grid='special') 

    # ==========================================================
    def _subplot_AEBS_Attr_power_TrackById(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  
               power of track
               power of targets
        
        '''
 
        dB_min =   0.0
        dB_max = 100.0
        
        ylim = (dB_min,dB_max)
        
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            
            # Target detections
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Target']['power'],'bx',label='targets')
            
            # Track
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['power'],'b',label='track')
            
              
        self.set_description(ax, ylabel='power [dB]', ylim=ylim, grid='special') 

    # ==========================================================
    def _subplot_AEBS_Attr_confidence_TrackById(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  
               power of track
               power of targets
        
        '''
 
        y_min = -0.1
        y_max =  1.1
        
        ylim = (y_min,y_max)
        
        print "AEBS_Attr.AEBS_Track", AEBS_Attr.AEBS_Track
        #print "AEBS_Attr.AEBS_Track['Time']", AEBS_Attr.AEBS_Track['Time']
        #print "AEBS_Attr.AEBS_Track['Track']['radar_confidence']", AEBS_Attr.AEBS_Track['Track']['radar_confidence']
        
        if check_AEBS_Attr_AEBS_Track(AEBS_Attr):
            # radar_confidence
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['radar_confidence'],'r',label='radar')
        
            # video_confidence
            ax.plot(AEBS_Attr.AEBS_Track['Time']-t_origin, AEBS_Attr.AEBS_Track['Track']['video_confidence'],'b',label='video')
          
              
        self.set_description(ax, ylabel='0..1', ylim=ylim, grid='special') 

    # ==========================================================
    def _subplot_AEBS_Attr_aRel(self, ax, AEBS_Attr, t_origin):
        '''
           Create subplot for  AEBS_Attr.dx
        
        '''
        aRel_unit = 'm/s$^2$'
 
        aRel_min = -10.0
        aRel_max = 3.0
            
        if AEBS_Attr.Time_aRel is not None:
            ax.plot(AEBS_Attr.Time_aRel-t_origin, AEBS_Attr.aRel,'b', label='aRel(%s)'%AEBS_Attr.mode)
        
         
        # Marker + Text
        if AEBS_Attr.t_warning is not None:
            self.mark_point(ax,AEBS_Attr.t_warning-t_origin,AEBS_Attr.aRel_at_t_warning, LineStyle='gd',FmtStr='%3.1f', yOffset=1.0)
        if AEBS_Attr.t_braking is not None:
            self.mark_point(ax,AEBS_Attr.t_braking-t_origin,AEBS_Attr.aRel_at_t_braking, LineStyle='bd',FmtStr='%3.1f', yOffset=1.0)
        if AEBS_Attr.t_emergency is not None:
            self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,AEBS_Attr.aRel_at_t_emergency, LineStyle='rd',FmtStr='%3.1f', yOffset=1.0)
       
        self.set_description(ax, ylabel='aRel [%s]'%aRel_unit, ylim=(aRel_min,aRel_max), grid='special') 

    # ==========================================================
    def _subplot_AEBS_Attr_table(self, ax, AEBS_Attr, t_origin):
        '''
           Create table with results
        '''
       
        ax.axis('off')

        #ax.text(0.95, 0.01, 'colored text in axes coords',verticalalignment='bottom', horizontalalignment='right',transform=ax.transAxes,color='green', fontsize=15)
        k=1.0
        if AEBS_Attr.v_ego_at_t_warning is not None:
            ax.text(0,k, 'Initial host speed : %6.2f km/h'%(AEBS_Attr.v_ego_at_t_warning,)); k=k+1
        else:
            ax.text(0,k, 'Initial host speed : ??? km/h'); k=k+1
            
        
        
        if AEBS_Attr.v_target_at_t_warning is not None:
            ax.text(0,k, 'Initial target speed : %6.2f km/h'%(AEBS_Attr.v_target_at_t_warning,)); k=k+1
        else:
            ax.text(0,k, 'Initial target speed : ??? km/h'); k=k+1
        
        if AEBS_Attr.t_impact is not None:
            ax.text(0,k, 'Impact host speed :   %6.2f km/h'%(AEBS_Attr.v_ego_at_t_impact,)); k=k+1
        elif AEBS_Attr.t_ego_stopped is not None:
            ax.text(0,k, 'Final host speed :    %6.2f km/h'%(AEBS_Attr.v_ego_at_t_ego_stopped,)); k=k+1
        elif AEBS_Attr.t_relaxed is not None:
            ax.text(0,k, 'Final host speed :    %6.2f km/h'%(AEBS_Attr.v_ego_at_t_relaxed,)); k=k+1
        
        
        if (AEBS_Attr.t_warning is not None) and (AEBS_Attr.t_braking is not None) and (AEBS_Attr.t_emergency is not None) and (AEBS_Attr.TTC_at_t_emergency is not None):
            ax.text(0,k, 'TTC(EBP):            %6.2f s'%(AEBS_Attr.TTC_at_t_emergency)); k=k+1
            ax.text(0,k, 't(EBP)- t(WP1):      %6.2f s'%(AEBS_Attr.t_emergency-AEBS_Attr.t_warning)); k=k+1
            ax.text(0,k, 't(EBP)- t(WP2):      %6.2f s'%(AEBS_Attr.t_emergency-AEBS_Attr.t_braking)); k=k+1
        
        if (AEBS_Attr.v_ego_at_t_warning is not None):    
            if (AEBS_Attr.v_ego_at_t_emergency is not None): 
                ax.text(0,k, 'v(WP1)- v(EBP):      %6.2f km/h'%((AEBS_Attr.v_ego_at_t_warning-AEBS_Attr.v_ego_at_t_emergency),)); k=k+1
        
            if AEBS_Attr.v_ego_at_t_impact is not None:
                ax.text(0,k, 'v(WP1)- v(impact):   %6.2f km/h'%((AEBS_Attr.v_ego_at_t_warning-AEBS_Attr.v_ego_at_t_impact),)); k=k+1
            elif AEBS_Attr.v_ego_at_t_ego_stopped is not None:
                ax.text(0,k, 'v(WP1)- v(avoid):   %6.2f km/h'%((AEBS_Attr.v_ego_at_t_warning-AEBS_Attr.v_ego_at_t_ego_stopped),)); k=k+1
            elif AEBS_Attr.v_ego_at_t_relaxed is not None:
                ax.text(0,k, 'v(WP1)- v(avoid):   %6.2f km/h'%((AEBS_Attr.v_ego_at_t_warning-AEBS_Attr.v_ego_at_t_relaxed),)); k=k+1
              
        ax.axis([0, 5, k, 0])
    

    # ==========================================================
    def _subplot_XBR(self, ax, AEBS_Attr, t_origin, show_only_one_ax_signal = True,yOffset=2.0):
        '''
            Create subplot for  XBR + measured longitudinal acceleration
        '''

        aXBR_min = -11.0
        aXBR_max = 2.0
        
        #FLR20_sig = self.FLR20_sig
        
        # ---------------------------------------------------  
        if AEBS_Attr.Time_XBR_ExtAccelDem is not None:
            ax.plot(AEBS_Attr.Time_XBR_ExtAccelDem-t_origin, AEBS_Attr.XBR_ExtAccelDem ,'r', label='XBR' )           
           
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

        # ---------------------------------------------------  
        self.set_description(ax, ylabel='m/s$^2$', ylim=(aXBR_min,aXBR_max), grid='special') 
        
             
    # ==========================================================
    def _subplot_DrvOverride1(self, ax, t_origin):
        '''
           Create subplot for  Driver Override 1 (flags)
        
        '''
        
        FLR20_sig = self.FLR20_sig
        
        #ax.plot(FLR20_sig["J1939"]["Time_ReverseGearDetected"]-t_origin, FLR20_sig["J1939"]["ReverseGearDetected"]+4.0,'m', label= 'ReverseGearDetected' )
       
        if FLR20_sig["J1939"]["Time_DriverActDemand"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DriverActDemand"]-t_origin,     FLR20_sig["J1939"]["DriverActDemand"]+6.0,    'm', label= 'DriverActDemand' )
        if FLR20_sig["J1939"]["Time_EBSBrakeSwitch"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_EBSBrakeSwitch"]-t_origin,      FLR20_sig["J1939"]["EBSBrakeSwitch"]+4.0,     'c', label= 'EBSBrakeSwitch' )
        if FLR20_sig["J1939"]["Time_DirIndL_b"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DirIndL_b"]-t_origin,           FLR20_sig["J1939"]["DirIndL_b"]+2.0,          'r', label= 'DirIndL_b' )
        if FLR20_sig["J1939"]["Time_DirIndR_b"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_DirIndR_b"]-t_origin,           FLR20_sig["J1939"]["DirIndR_b"],              'b', label= 'DirIndR_b' )
 
        ax.set_yticks(range(8)) 
        label  = ['Off','DirIndR_b On']
        label += ['Off','DirIndL_b On']
        label += ['Off','EBSBrakeSwitch On']
        label += ['Off','DriverActDemand On']
        #label += ['Off','ReverseGearDetected On']
        ax.set_yticklabels(label)

        self.set_description(ax, ylabel=None, ylim=(-0.1,8.1), grid='special')
        
        
    # ==========================================================
    def _subplot_DrvOverride2(self, ax, t_origin):
        '''
           Create subplot for Driver Override 2 (steering angle)
        
        '''
        
        FLR20_sig = self.FLR20_sig
        if FLR20_sig["J1939"]["Time_SteerWhlAngle"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_SteerWhlAngle"]-t_origin,      FLR20_sig["J1939"]["SteerWhlAngle"]*180.0/np.pi, 'b',     label= 'SteerWhlAngle' )
 
        self.set_description(ax, ylabel="[degree]", ylim=(-100.1,100.1), grid='special')
        
        
    # ==========================================================
    def _subplot_DrvOverride3(self, ax, t_origin):
        '''
           Create subplot for Driver Override 3 (accelerator and brake pedal)
        
        '''
        
        FLR20_sig = self.FLR20_sig
        if FLR20_sig["J1939"]["Time_AccelPedalPos1"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_AccelPedalPos1"]-t_origin, FLR20_sig["J1939"]["AccelPedalPos1"],'b', label= 'AccelPedalPos1' )
        if FLR20_sig["J1939"]["Time_BrakePedalPos"] is not None:
            ax.plot(FLR20_sig["J1939"]["Time_BrakePedalPos"]-t_origin,  FLR20_sig["J1939"]["BrakePedalPos"], 'r', label= 'BrakePedalPos' )
     

        self.set_description(ax, ylabel='[%]', ylim=(-5.0,105.0), grid='special')
        
     
    # ==========================================================
    def _subplot_TRW_AECF(self, ax,AEBS_Attr, t_origin, mode):
        '''
            Create subplot for TRW Allow Entry and Cancel Flags
         
            kind: 'cm', 'cw', 'cmb', 
        
                   
            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['Time']                             

            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cm_allow_entry_global_conditions'] 
            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cm_cancel_global_conditions']      
            
            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cw_allow_entry']                   
            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cw_cancel']                        

            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cmb_allow_entry']                  
            FLR20_sig['ACC_Sxy2']["TRW_AECF"]['cmb_cancel']                       

        
        '''
        
        FLR20_sig = self.FLR20_sig
        Time = FLR20_sig['ACC_Sxy2']['TRW_AECF']['Time']
        ylabel_txt = ""
        if Time is not None:
            if mode in ['cm']:
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cm_allow_entry_global_conditions']+2.0, 'b',     label= 'allow_entry' )
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cm_cancel_global_conditions'],          'r',     label= 'cancel' )
                ylabel_txt = "global \n conditions \n cm"
 
            
            elif mode in ['cw']:
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cw_allow_entry']+2.0, 'b',     label= 'allow_entry' )
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cw_cancel'],          'r',     label= 'cancel' )
                ylabel_txt = "warning \n conditions \n cw"
 

            elif mode in ['cmb']:
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cmb_allow_entry']+2.0, 'b',     label= 'allow_entry' )
                ax.plot(Time-t_origin,  FLR20_sig['ACC_Sxy2']['TRW_AECF']['cmb_cancel'],          'r',     label= 'cancel' )
                ylabel_txt = "braking \n conditions \n cmb"
            
        # Marker + Text
        if AEBS_Attr.t_warning is not None:
            if mode in ['cm', 'cw']:
                self.mark_point(ax,AEBS_Attr.t_warning-t_origin,0.0, LineStyle='gd',FmtStr=None)
                self.mark_point(ax,AEBS_Attr.t_warning-t_origin,3.0, LineStyle='gd',FmtStr=None)
        if AEBS_Attr.t_braking is not None:
            if mode in ['cm', 'cmb']:
                self.mark_point(ax,AEBS_Attr.t_braking-t_origin,0.0, LineStyle='bd',FmtStr=None)
                self.mark_point(ax,AEBS_Attr.t_braking-t_origin,3.0, LineStyle='bd',FmtStr=None)
        if AEBS_Attr.t_emergency is not None:
            if mode in ['cm', 'cmb']:
                self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,0.0, LineStyle='rd',FmtStr=None)
                self.mark_point(ax,AEBS_Attr.t_emergency-t_origin,3.0, LineStyle='rd',FmtStr=None)
                    

        self.set_description(ax, ylabel=ylabel_txt, ylim=(-0.6,3.6), grid='stacked_flags')
    
        
    # ==========================================================
    def plot_all_Homologation(self,enable_png_extract=True):
    
        self.plot_AEBS_Homologation_use_case()
        self.plot_AEBS_Homologation_Ovrride()
        
        AEBS_Attr = self._Calc_AEBS_Attr(mode = 'VBOX')      
        t_origin = AEBS_Attr.t_origin
        res = AEBS_Attr.getResults()
        
        # extract frames from video
               
        if enable_png_extract:
            print "---------------------------------------"
            print "extract frames from video:"
            OffsetList = []
            for signal in ["t_warning", "t_braking", "t_emergency", "t_impact", "t_ego_stopped", "t_relaxed"]:
                if res[signal] is not None:
                    OffsetList.append(res[signal]-t_origin)
                    
            FullPathFileName = self.FLR20_sig['FileName_org']        
            Tag='AEBS_Homologation'
            kbtools_user.CreateVideoSnapshots(FullPathFileName,self.FLR20_sig, t_origin, OffsetList = OffsetList, PngFolder = self.PngFolder,Tag=Tag,verbose=self.verbose)
           

    # ==========================================================
    def plot_AEBS_Homologation_use_case(self, FigNr = 30,xlim=None, PlotName='AEBS_Homologation_H1_use_case'):
        '''
            AEBS_Homologation
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        AEBS_Attr = self._Calc_AEBS_Attr(mode = 'VBOX')     
        t_origin = AEBS_Attr.t_origin
     
          
        
       
        # -------------------------------------------------
        if self.Description is not None:
            suptitle = "%s t$_0$=%6.3fs %s (FileName: %s)"%(PlotName, t_origin, self.Description, self.FileName)
        else:
            suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(511), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(512), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(513), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        ax = fig.add_subplot(514)
        self._subplot_XBR(ax, AEBS_Attr, t_origin)
        ax.set_xlabel('time [s]')
        
        # -------------------------------------------------------------------------
        # AEBS_Attr table
        self._subplot_AEBS_Attr_table(fig.add_subplot(515),AEBS_Attr, t_origin)

        
        self.show_and_save_figure(t_event=t_origin)
        
        
    # ==========================================================
    def plot_AEBS_Homologation_Ovrride(self, FigNr=30, xlim=None, PlotName='AEBS_Homologation_H2_Ovrride'):
        '''
             AEBS_Homologation Overrides
        '''        
        
        if self.verbose:
            print PlotName

        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        AEBS_Attr = self._Calc_AEBS_Attr(mode = 'VBOX')     
        t_origin = AEBS_Attr.t_origin

        # -------------------------------------------------
        if self.Description is not None:
            suptitle = "%s t$_0$=%6.3fs %s (FileName: %s)"%(PlotName, t_origin, self.Description, self.FileName)
        else:
            suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(611), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(612), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(613), AEBS_Attr, t_origin)

        # -------------------------------------------------------------------------
        # drv override
        self._subplot_DrvOverride1(fig.add_subplot(614), t_origin)
        
        self._subplot_DrvOverride2(fig.add_subplot(615), t_origin)

        ax = fig.add_subplot(616)
        self._subplot_DrvOverride3(ax, t_origin)
        ax.set_xlabel('time [s]')
        
              
        self.show_and_save_figure(t_event=t_origin)
           
       
        
    # ==========================================================
    def plot_all(self,enable_png_extract=True):
        self.PlotAll(enable_png_extract=enable_png_extract)
    
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
            
        self.AEBS_Attr_FLR20 = self._Calc_AEBS_Attr(mode = 'FLR20') 
        
        self.plot_AEBS_use_case()
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
         
        # extract frames from video
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
  
    # ==========================================================
    def plot_AEBS_use_case(self, FigNr = 30,xlim=None, PlotName='AEBS_1_use_case'):
        '''
            AEBS_Homologation
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')
        AEBS_Attr = self.AEBS_Attr_FLR20     
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(511), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(512), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(513), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_XBR(fig.add_subplot(514), AEBS_Attr, t_origin)
 
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        # -------------------------------------------------------------------------
        # AEBS_Attr table
        self._subplot_AEBS_Attr_table(fig.add_subplot(515),AEBS_Attr, t_origin)

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
          
    # ==========================================================
    def plot_AEBS_use_case_dy(self, FigNr = 30,xlim=None, PlotName='AEBS_1_use_case_dy'):
        '''
            AEBS_Homologation dy
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')   
        AEBS_Attr = self.AEBS_Attr_FLR20  
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(511), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(512), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(513), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # dy
        self._subplot_AEBS_Attr_lateral_position(fig.add_subplot(514),AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_XBR(fig.add_subplot(515), AEBS_Attr, t_origin)
 
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
    
    # ==========================================================
    def plot_AEBS_use_case_v_vs_d(self, FigNr = 30,xlim=None, PlotName='AEBS_1_use_case_v_vs_d'):
        '''
            AEBS_Homologation
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # v_ego, velocity_vs_distance
        self._subplot_AEBS_Attr_velocity_vs_distance(fig.add_subplot(111), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        self.show_and_save_figure()
        
        
    # ==========================================================
    def plot_AEBS_Ovrride(self, FigNr=30, xlim=None, PlotName='AEBS_2_Ovrride'):
        '''
             AEBS Overrides
        '''        
        
        if self.verbose:
            print PlotName

        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin
        t_origin = self.t_event  
            
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(611), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(612), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(613), AEBS_Attr, t_origin)

        # -------------------------------------------------------------------------
        # drv override
        self._subplot_DrvOverride1(fig.add_subplot(614), t_origin)
        
        self._subplot_DrvOverride2(fig.add_subplot(615), t_origin)

        self._subplot_DrvOverride3(fig.add_subplot(616), t_origin)
        
        # -------------------------------------------------------------------------
        # time axis at bottom
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
           
    # ==========================================================
    def plot_AEBS_aRel(self, FigNr = 30,xlim=None, PlotName='AEBS_3_aRel'):
        '''
            AEBS_aRel
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(611), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(612), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(613), AEBS_Attr, t_origin)

        # -------------------------------------------------------------------------
        # aRel
        self._subplot_AEBS_Attr_aRel(fig.add_subplot(614), AEBS_Attr, t_origin)
        
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_XBR(fig.add_subplot(615), AEBS_Attr, t_origin)
        
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
        
        # -------------------------------------------------------------------------
        # AEBS_Attr table
        self._subplot_AEBS_Attr_table(fig.add_subplot(616),AEBS_Attr, t_origin)

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
           
    # ==========================================================
    def plot_AEBS_TRW_AECF(self, FigNr = 40,xlim=None, PlotName='AEBS_4_TRW_AECF'):
        '''
            AEBS_TRW_AECF
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(611), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(612), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position(fig.add_subplot(613), AEBS_Attr, t_origin,mark_is_video_associated=True)

        # -------------------------------------------------------------------------
        # TRW Allow entry and cancel flags
        self._subplot_TRW_AECF(fig.add_subplot(614), AEBS_Attr, t_origin, mode='cm')
        self._subplot_TRW_AECF(fig.add_subplot(615), AEBS_Attr, t_origin, mode='cw')
        self._subplot_TRW_AECF(fig.add_subplot(616), AEBS_Attr, t_origin, mode='cmb')
        
        # -------------------------------------------------------------------------
        # time axis at bottom
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
        
        # -------------------------------------------------------------------------
        self.show_and_save_figure()
    
    # ==========================================================
    def plot_AEBS_XBR(self, FigNr = 30,xlim=None, PlotName='AEBS_5_XBR'):
        '''
            AEBS_XBR and longitundinal acclerations
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        self._subplot_XBR(fig.add_subplot(111), AEBS_Attr, t_origin,show_only_one_ax_signal = False,yOffset=0.5)
 
        # -------------------------------------------------------------------------
        self.show_and_save_figure()
    
    # ==========================================================
    def plot_AEBS_use_case_Fusion(self, FigNr = 30,xlim=None, PlotName='AEBS_6_Fusion'):
        '''
            plot_AEBS_use_case_Fusion
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(511), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(512), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position_TrackById(fig.add_subplot(513), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # dy
        #self._subplot_AEBS_Attr_lateral_position(fig.add_subplot(514),AEBS_Attr, t_origin)
        self._subplot_AEBS_Attr_FLC20_Number_Of_Objects(fig.add_subplot(514),AEBS_Attr, t_origin)
       
       
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        #self._subplot_XBR(fig.add_subplot(515), AEBS_Attr, t_origin)
        #self._subplot_AEBS_Attr_FLC20_Detection_Score(fig.add_subplot(515),AEBS_Attr, t_origin)
        self._subplot_AEBS_Attr_confidence_TrackById(fig.add_subplot(515),AEBS_Attr, t_origin)
      
       
       
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()

    # ==========================================================
    def plot_AEBS_use_case_Fusion2(self, FigNr = 30,xlim=None, PlotName='AEBS_6_Fusion2'):
        '''
            plot_AEBS_use_case_Fusion
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        #self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(311), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_velocity(fig.add_subplot(211), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position_TrackById(fig.add_subplot(212), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # dy
        #self._subplot_AEBS_Attr_lateral_position(fig.add_subplot(514),AEBS_Attr, t_origin)
        #self._subplot_AEBS_Attr_FLC20_Number_Of_Objects(fig.add_subplot(514),AEBS_Attr, t_origin)
       
       
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        #self._subplot_XBR(fig.add_subplot(515), AEBS_Attr, t_origin)
        #self._subplot_AEBS_Attr_FLC20_Detection_Score(fig.add_subplot(515),AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
        
    # ==========================================================
    def plot_AEBS_use_case_Fusion3(self, FigNr = 30,xlim=None, PlotName='AEBS_6_Fusion3'):
        '''
            plot_AEBS_use_case_Fusion
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
   
        # -------------------------------------------------------------------------
        # AEBS system state
        #self._subplot_AEBS_Attr_AEBSState(fig.add_subplot(311), AEBS_Attr, t_origin)       

        # -------------------------------------------------------------------------
        # v_ego, v target
        self._subplot_AEBS_Attr_asso_target_index(fig.add_subplot(411), AEBS_Attr, t_origin)
    
        self._subplot_AEBS_Attr_asso_video_ID(fig.add_subplot(412), AEBS_Attr, t_origin)
    
        self._subplot_AEBS_Attr_track0_ID(fig.add_subplot(413), AEBS_Attr, t_origin)
    
    
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position_TrackById(fig.add_subplot(414), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # dy
        #self._subplot_AEBS_Attr_lateral_position(fig.add_subplot(514),AEBS_Attr, t_origin)
        #self._subplot_AEBS_Attr_FLC20_Number_Of_Objects(fig.add_subplot(514),AEBS_Attr, t_origin)
       
       
       
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        #self._subplot_XBR(fig.add_subplot(515), AEBS_Attr, t_origin)
        #self._subplot_AEBS_Attr_FLC20_Detection_Score(fig.add_subplot(515),AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
        
    # ==========================================================
    def plot_AEBS_use_case_Fusion4(self, FigNr = 30,xlim=None, PlotName='AEBS_6_Fusion4'):
        '''
            plot_AEBS_use_case_Fusion
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20')     
        AEBS_Attr = self.AEBS_Attr_FLR20
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
     
        # -------------------------------------------------------------------------
        # dx
        self._subplot_AEBS_Attr_position_TrackById(fig.add_subplot(411), AEBS_Attr, t_origin)
       
        # -------------------------------------------------------------------------
        # dy
        self._subplot_AEBS_Attr_lateral_position_TrackById(fig.add_subplot(412), AEBS_Attr, t_origin)
    
        # -------------------------------------------------------------------------
        # vRel
        self._subplot_AEBS_Attr_vRel_TrackById(fig.add_subplot(413), AEBS_Attr, t_origin)
       
        
        # -------------------------------------------------------------------------
        # power
        self._subplot_AEBS_Attr_power_TrackById(fig.add_subplot(414), AEBS_Attr, t_origin)
       
       
       
       
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
        
    # ==========================================================
    def plot_AEBS_use_case_FLC20_CAN_Delay(self, FigNr = 30,xlim=None, PlotName='AEBS_7_FLC20_CAN_Delay'):
        '''
            plot_AEBS_use_case_FLC20_CAN_Delay
        '''
      
        if self.verbose:
            print PlotName
    
        if xlim is None:
            xlim = self.xlim
        self.xlim_to_use(xlim)
           
        #AEBS_Attr = self._Calc_AEBS_Attr(mode = 'FLR20') 
        AEBS_Attr = self.AEBS_Attr_FLR20    
        #t_origin = AEBS_Attr.t_origin

        t_origin = self.t_event        
             
        # -------------------------------------------------
        suptitle = "%s t$_0$=%6.3fs (FileName: %s)"%(PlotName, t_origin, self.FileName)
        fig = self.start_fig(PlotName=PlotName,suptitle=suptitle)
     
        # -------------------------------------------------------------------------
        # FLC20_CAN_Delay
        self._subplot_AEBS_Attr_FLC20_CAN_Delay(fig.add_subplot(211), AEBS_Attr, t_origin)
       
        # FLC20_SamplingInterval
        self._subplot_AEBS_Attr_FLC20_SamplingInterval(fig.add_subplot(212), AEBS_Attr, t_origin)
       
       
        # -------------------------------------------------------------------------
        # time axis 
        pl.gca().set_xlabel("time [s] (relative to event t$_0$=%6.3fs)"%t_origin)
       
        

        # -------------------------------------------------------------------------
        self.show_and_save_figure()
    
        
    # ###########################################################################################
    #
    #  old stuff
    #  
    # ###########################################################################################
       
    # ==========================================================
    def calc_start_events_Bendix(self, t_event):
        # input:
        #   t_event      - start of AEBS warning
        #
        # output:
        #   t_vid_asso   - start of video associated
        #   t_cw_track   - start of collision warning track
        #   t_warning    - start of warning
        #   t_braking    - start of braking
        #   t_emergency  - start of emergency braking
        #   t_impact     - start of impact
        
        if self.verbose:
            print "calc_start_events_Bendix()"
    
        FLR20_sig = self.FLR20_sig
    
        # Bendix/TRW AEB cascade    
        t                    = FLR20_sig['PosMatrix']['CW']['Time']
        is_video_associated  = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['is_video_associated'], t)
        cw_track             = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['CW_track'], t)
        t_cm_system_status   = FLR20_sig['General']['Time']
        cm_system_status     = FLR20_sig['General']["cm_system_status"]
        dx                   = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['dx'], t)
        
        tolerance = 0.5
        
        
        
        # -----------------------------------------
        # t_warning
        t_warning = None
        try: 
            t_warning = t_cm_system_status[np.logical_and(cm_system_status>1.5,np.logical_and(t_cm_system_status>t_event-tolerance, t_cm_system_status<t_event+tolerance))][0] 
        except:
            t_warning = None
        
        if self.verbose:
            print "** t_warning", t_warning
        
         
        # ------------------------------------------
        # t_vid_asso
        t_vid_asso = None 
        try: 
            start_idx, _ = kbtools.getIntervalAroundEvent(t,t_warning,is_video_associated>0.5)
            if start_idx is not None:
                t_vid_asso = t[start_idx]
        except:
            t_vid_asso = None     

    
        # ------------------------------------------
        # t_cw_track   #t_cw_track = FLR20_sig['PosMatrix']['CW']['Time'][FLR20_sig['PosMatrix']['CW']['Valid']>0.5][0] - t_start
        t_cw_track = None
        try: 
            start_idx, _ = kbtools.getIntervalAroundEvent(t,t_warning,cw_track>0.5)
            if start_idx is not None:
                t_cw_track = t[start_idx]
        except:
            t_cw_track = None
        
        
        # ------------------------------------------
        # t_braking
        try: 
            t_braking = t_cm_system_status[np.logical_and(cm_system_status>2.5, t_cm_system_status>t_warning)][0]      
        except:
            t_braking = None
            
            
        # ------------------------------------------
        # t_emergency
        t_emergency = None
        
            
        # ------------------------------------------
        # t_impact
        try: 
            t_impact = t[np.logical_and(dx<0.5, t>t_braking)][0] 
        except:
            t_impact = None    

        if self.verbose:
            print "  t_vid_asso", t_vid_asso
            print "  t_cw_track", t_cw_track
            print "  t_warning", t_warning
            print "  t_braking", t_braking
            print "  t_emergency", t_emergency
            print "  t_impact", t_impact
        
        # return results
        res = {}
        res["t_vid_asso"]  = t_vid_asso 
        res["t_cw_track"]  = t_cw_track 
        res["t_warning"]   = t_warning 
        res["t_braking"]   = t_braking 
        res["t_emergency"] = t_emergency
        res["t_impact"]    = t_impact
        
        return res
        
    # ==========================================================
    def select_data_for_calc_start_events_SFN(self, AEBS_source='ECU'):
        # input:
        #   AEBS_source: 'ECU', 'AUTOBOX' or 'SIM'
        #        'ECU'     : inp['AEBS_Warning'] and inp['AEBS_XBR'] are taken from measurement
        #        'AUTOBOX' : inp['AEBS_Warning'] and inp['AEBS_XBR'] are taken from measurement (Autobox, endurance run, AEBS command not feed thru)
        #        'SIM'     : inp['AEBS_Warning'] and inp['AEBS_XBR'] are taken from simulation
        #
        # return:
        #   inp['t']                     - time
        #   inp['dx']                    - longitudinal distance to CIPV
        #   inp['cw_track']              - collision warning track 
        #   inp['is_video_associated']   - object is video associated
        #   inp['AEBS_Warning']          - AEBS warning  
        #   inp['AEBS_XBR']              - AEBS external brake request acceleration

    
        if self.verbose:
            print "select_data_for_calc_start_events_SFN()-start"
    
        FLR20_sig = self.FLR20_sig
    
        # SFN AEBS cascade    
        inp ={}
        
        # commin signals
        t = FLR20_sig['PosMatrix']['CW']['Time']
        inp['t']                    = t
        inp['dx']                   = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['dx'], t)
        inp['cw_track']             = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['CW_track'], t)
        # alternative: FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['Valid']>0.5
                
        inp['is_video_associated']  = kbtools.resample(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['is_video_associated'], t)
        
        # -----------------------------------------------
        inp['AEBS_Warning'] = None
        inp['AEBS_XBR'] = None
        inp['ABESState'] = None
        
        inp['AEBS_Partial_Braking'] = None
        inp['AEBS_Emergency_Braking'] = None

        # AEBS algorithm output of FLR20 'ECU' or Simulation
        if 'ECU' == AEBS_source:
            # on J1939 CAN 
            inp['AEBS_Warning']         = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_Warning'],     FLR20_sig['AEBS_SFN_OUT']['Warning'], t)
            inp['AEBS_XBR']             = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'], FLR20_sig['AEBS_SFN_OUT']['AccelDemand'], t)
            inp['ABESState']            = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_ABESState'],   FLR20_sig['AEBS_SFN_OUT']['ABESState'], t)   
            if inp['AEBS_Warning'] is not None:
                print "  J1939 AEBS Warning available"  
            else:
                print "  J1939 AEBS Warning not available"  
                if inp['ABESState'] is not None:
                    print "    but substituted byABESState"  
                    inp['AEBS_Warning'] =  inp['ABESState'] == 5
                    print inp['AEBS_Warning']
            if inp['AEBS_XBR'] is not None:
                print "  J1939 AEBS AccelDemand available"  
            else:
                print "  J1939 AEBS AccelDemand not available"  
            if inp['ABESState'] is not None:
                print "  J1939 ABESState available"  
            else:
                print "  J1939 ABESState not available"  

            if inp['AEBS_XBR'] is not None:            
                inp['AEBS_Partial_Braking'] = np.logical_and(inp['AEBS_XBR']<0.0, inp['AEBS_XBR']>-4.0)           
                inp['AEBS_Emergency_Braking'] = inp['AEBS_XBR']<=-4.0
                
        elif 'AUTOBOX' == AEBS_source:                     
            # Autobox (in endurance run
            inp['AEBS_Warning']         = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_Warning_Autobox'],     FLR20_sig['AEBS_SFN_OUT']['Warning_Autobox'], t)
            inp['AEBS_XBR']             = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox'], FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox'], t)
            inp['ABESState']            = kbtools.resample(FLR20_sig['AEBS_SFN_OUT']['Time_ABESState_Autobox'],   FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'], t)           
            if inp['AEBS_Warning'] is not None:
                print "  Autobox AEBS Warning, AEBS AccelDemand and ABESState available"  
            else:
                print "  Autobox AEBS Warning, AEBS AccelDemand and ABESState not available"  
    
            if inp['AEBS_XBR'] is not None:            
                inp['AEBS_Partial_Braking'] = np.logical_and(inp['AEBS_XBR']<0.0, inp['AEBS_XBR']>-4.0)           
                inp['AEBS_Emergency_Braking'] = inp['AEBS_XBR']<=-4.0
        

        elif 'SIM' == AEBS_source:
            # FLR20_sig['simulation_output']:
            # 't', 'acoopti_SetRequest', 'acopebe_SetRequest', 'acoacoi_SetRequest', 'acopebp_SetRequest', 'acopebp_RequestValue',  'acopebe_RequestValue', 
            if 'simulation_output' in FLR20_sig:
                inp['AEBS_Warning']           = self.FLR20_sig['simulation_output']['acoacoi_SetRequest']
                inp['AEBS_Partial_Braking']   = self.FLR20_sig['simulation_output']['acopebp_SetRequest'] 
                inp['AEBS_Emergency_Braking'] = self.FLR20_sig['simulation_output']['acopebe_SetRequest']               
                inp['AEBS_XBR']               = self.FLR20_sig['simulation_output']['acopebp_RequestValue'] + self.FLR20_sig['simulation_output']['acopebe_RequestValue']
                print 'simulation_output okay'
            else:
                print 'simulation_output missing'
        
        
        if self.verbose:
            print "select_data_for_calc_start_events_SFN()-end"
        
        return inp
    
    # ==========================================================
    def plot_calc_start_events_SFN(self,inp,res,t_event,FigNr = 42,xlim=None):
        
        t_vid_asso  = res["t_vid_asso"]
        t_cw_track  = res["t_cw_track"] 
        t_warning   = res["t_warning"] 
        t_braking   = res["t_braking"] 
        t_emergency = res["t_emergency"]
        #t_impact    = res["t_impact"] 

        #FLR20_sig = self.FLR20_sig
        
        t_origin = t_event
        
        # -------------------------------------------------
        FigNr = 42
        fig = pl.figure(FigNr)  
        fig.clf()
     
        # -------------------------------------------------------------------------
        # CVR3-S1 available; AEBS acoustic warning
        ax = fig.add_subplot(211)
    
        # Lines
        #                    inp['t']   
        #                    inp['dx']   
        #                    inp['cw_track']            
        #                    inp['is_video_associated']  
        #                    inp['AEBS_Warning']  
        #                    inp['AEBS_XBR']  
        
        if inp['is_video_associated'] is not None:
            ax.plot(inp['t']-t_origin, 8.0 + inp['is_video_associated'],'k')
      
        if inp['cw_track'] is not None:
            ax.plot(inp['t']-t_origin, 6.0 + inp['cw_track'],'m')
        
        if inp['AEBS_Warning'] is not None:
            ax.plot(inp['t']-t_origin, 4.0 + inp['AEBS_Warning'] ,'b' )
        
        if inp['AEBS_Partial_Braking'] is not None:
            ax.plot(inp['t']-t_origin, 2.0 + inp['AEBS_Partial_Braking'] ,'b' )
        
        if inp['AEBS_Emergency_Braking'] is not None:
            ax.plot(inp['t']-t_origin, 0.0 + inp['AEBS_Emergency_Braking'] ,'b' )
            
           
        # Marker + Text + vertical lines 
        if t_vid_asso is not None:
            ax.plot(t_vid_asso-t_origin, 1.0+8.0,'kd')
            ax.text(t_vid_asso-t_origin, 1.2+8.0,'%3.1f s'% (t_vid_asso-t_origin))

        if t_cw_track is not None:
            ax.plot(t_cw_track-t_origin, 1.0+6.0,'bd')
            ax.text(t_cw_track-t_origin, 1.2+6.0,'%3.1f s'% (t_cw_track-t_origin))
    
        if t_warning is not None:
            ax.plot(t_warning-t_origin, 1.0+4.0,'md')
            ax.text(t_warning-t_origin, 1.2+4.0,'%3.1f s'% (t_warning-t_origin))

        if t_braking is not None:
            ax.plot(t_braking-t_origin, 1.0+2.0,'rd')
            ax.text(t_braking-t_origin, 1.2+2.0,'%3.1f s'% (t_braking-t_origin))
            
        if t_emergency is not None:
            ax.plot(t_emergency-t_origin, 1.0+0.0,'rd')
            ax.text(t_emergency-t_origin, 1.2+0.0,'%3.1f s'% (t_emergency-t_origin))
            
         
    
        # legend, labels and grid
        ax.legend(('video asso (+8)','CW track (+6)','Warning (+4)', 'Part. Braking (+2)', 'Emerg. Braking'))
        ax.set_ylabel('AEBS')
        #create_special_grid(ax)
        ax.grid()
        ax.set_ylim(-0.5,10.0)
        if xlim:
            ax.set_xlim(xlim)
        
        # XBR        
        ax = fig.add_subplot(212)
        ax.plot(inp['t']-t_origin, inp['AEBS_XBR'] ,'b' )
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
           
        
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        # -------------------------------------------------------------------------
        # create png picture
        #FileName = self.FileName
        #fig.set_size_inches(16.,12.)
        #fig.savefig("%s_@%3.1fs_plot_calc_start_events_SFN.png"%(FileName,t_event))
    

    # ==========================================================
    def calc_start_events_SFN(self, inp, t_event):
    
        # input:
        #   inp          - input signals
        #                    inp['t']   
        #                    inp['dx']   
        #                    inp['cw_track']            
        #                    inp['is_video_associated']  
        #                    inp['AEBS_Warning']  
        #                    inp['AEBS_Partial_Braking']
        #                    inp['AEBS_Emergency_Braking']
        #                    inp['AEBS_XBR']  
        #   t_event      - start of AEBS warning
        #
        # output:
        #   t_vid_asso   - start of video associated
        #   t_cw_track   - start of collision warning track
        #   t_warning    - start of warning
        #   t_braking    - start of braking
        #   t_emergency  - start of emergency braking
        #   t_impact     - start of impact
        
        if self.verbose:
            print "calc_start_events_SFN()"
         
        # initialize outputs
        t_vid_asso   = None 
        t_cw_track   = None 
        t_warning    = None 
        t_braking    = None 
        t_emergency  = None 
        t_impact     = None 
       
        
        
        # map input signals
       
        t                      = inp['t']   
        dx                     = inp['dx']                 
        cw_track               = inp['cw_track']            
        is_video_associated    = inp['is_video_associated']  
        AEBS_SFN_Warning       = inp['AEBS_Warning']  
        AEBS_Partial_Braking   = inp['AEBS_Partial_Braking']
        AEBS_Emergency_Braking = inp['AEBS_Emergency_Braking']
        #AEBS_AccelDemand       = inp['AEBS_XBR']  
          

        
        if  (t is not None) and (dx is not None) and (AEBS_SFN_Warning is not None)  and (AEBS_Partial_Braking is not None) and (AEBS_Emergency_Braking is not None):
                
        
            tolerance = 1.5
            #tolerance = 10.0
            
        
            # -----------------------------------------
            # t_warning
            try: 
                t_warning = t[np.logical_and(AEBS_SFN_Warning>0.5,np.logical_and(t>t_event-tolerance, t<t_event+tolerance))][0] 
            except:
                t_warning = None
       
        
            # ------------------------------------------
            # t_vid_asso
            try: 
                start_idx, _ = kbtools.getIntervalAroundEvent(t,t_warning,is_video_associated>0.5)
                if start_idx is not None:
                    t_vid_asso = t[start_idx]
                else:
                    t_vid_asso = None 
            except:
                t_vid_asso = None     
    
            # ------------------------------------------
            # t_cw_track   
            try: 
                start_idx, _ = kbtools.getIntervalAroundEvent(t,t_warning,cw_track>0.5)
                if start_idx is not None:
                    t_cw_track = t[start_idx]
                else:
                    t_cw_track = None
            except:
                t_cw_track = None
        
        
            # ------------------------------------------
            # t_braking
            try: 
                #t_braking = t[np.logical_and(AEBS_AccelDemand<0.0, t>t_warning)][0]      
                t_braking = t[np.logical_and(AEBS_Partial_Braking, t>t_warning)][0]      
                
            except:
                t_braking = None
            
            # ------------------------------------------
            # t_emergency
            try: 
                #t_emergency = t[np.logical_and(AEBS_AccelDemand<-3.0, t>t_braking)][0] 
                t_emergency = t[np.logical_and(AEBS_Emergency_Braking, t>t_braking)][0] 
            except:
                t_emergency = None
        
            # ------------------------------------------
            # t_impact
            try: 
                t_impact = t[np.logical_and(dx<0.5, t>t_braking)][0] 
            except:
                t_impact = None
        else:
            print "AEBS_SFN_Warning", AEBS_SFN_Warning 
            #print "AEBS_AccelDemand", AEBS_AccelDemand
            
        
        if self.verbose:
            print "  t_vid_asso",  t_vid_asso
            print "  t_cw_track",  t_cw_track
            print "  t_warning",   t_warning
            print "  t_braking",   t_braking
            print "  t_emergency", t_emergency
            print "  t_impact",    t_impact
        
        # return results
        res = {}
        res["t_vid_asso"]  = t_vid_asso 
        res["t_cw_track"]  = t_cw_track 
        res["t_warning"]   = t_warning 
        res["t_braking"]   = t_braking 
        res["t_emergency"] = t_emergency
        res["t_impact"]    = t_impact
        
        
        return res
        

        
    # ==========================================================
    def plot_AEBS_overview(self, FigNr = 30,xlim=None, t_event=None, cfg=None):
        #
        #
        # todo:  do_bendix ['Bendix_CMS']["AudibleFeedback"]
        
        if self.verbose:
            print "plot_AEBS_overview()"
    
        FLR20_sig = self.FLR20_sig
        
        # --------------------------------------------------------------------
        # cfg
        # default setting
        do_bendix = False
        do_sfn = True
        show_SIM = False
        if cfg is not None:
            if 'show_SIM' in cfg:
                show_SIM = cfg['show_SIM']
            if 'do_sfn' in cfg:
                do_sfn = cfg['do_sfn']
            if 'do_bendix' in cfg:
                do_bendix = cfg['do_bendix']
            
    
        # --------------------------------------------------------------------
        if do_bendix:
            res = self.calc_start_events_Bendix(t_event)
            
        if do_sfn:
            if show_SIM:
                AEBS_source = 'SIM'
            elif 'AEBS_source' in cfg:
                AEBS_source = cfg['AEBS_source']
            else:
                AEBS_source='ECU'
               
           
            inp = self.select_data_for_calc_start_events_SFN(AEBS_source)
            res = self.calc_start_events_SFN(inp,t_event)
            
            # visual inspection
            if AEBS_source=='ECU':
                self.plot_calc_start_events_SFN(inp,res,t_event,xlim=xlim)
        
          
        t_vid_asso  = res["t_vid_asso"]
        t_cw_track  = res["t_cw_track"] 
        t_warning   = res["t_warning"] 
        t_braking   = res["t_braking"] 
        t_emergency = res["t_emergency"]
        t_impact    = res["t_impact"] 
       
        
        print "  t_vid_asso",  t_vid_asso
        print "  t_cw_track",  t_cw_track
        print "  t_warning",   t_warning
        print "  t_braking",   t_braking
        print "  t_emergency", t_emergency
        print "  t_impact",    t_impact
             
             
        # -------------------------------------------------
        # t_origin 
        if t_warning is not None:
            # origin of the time axis 
            t_origin = t_warning
        else:
            t_origin = t_event
            print "no warning not found"
             
        
       
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()
    
        # time axis
        #t  = FLR20_sig['Tracks'][0]['Time']
    
        # ----------------------------------------------------------------
        # Suptitle
        FileName = self.FileName
        if do_bendix:
            text = "Bendix AEBS on FLR20 t$_0$=%6.3fs (%s)"%(t_origin,FileName)
        if do_sfn:
            if 'ECU' == AEBS_source:
                text = "SFN AEBS on FLR20 t$_0$=%6.3fs (%s)"%(t_origin,FileName)
            elif 'AUTOBOX' == AEBS_source: 
                text = "SFN Autobox AEBS on FLR20 t$_0$=%6.3fs (%s)"%(t_origin,FileName)
            elif 'SIM' == AEBS_source:        
                text = "SFN Simulated AEBS on FLR20 t$_0$=%6.3fs (%s)"%(t_origin,FileName) 

             
            
        
        fig.suptitle(text)
    
   
        # ----------------------------------------------------------------
        # Scaling
        dx_min = -10.0
        dx_max = 110.0
    
        v_kph_min = -10.0
        v_kph_max = 90.0
    
       
        # -------------------------------------------------------------------------
        # v_ego
        ax = fig.add_subplot(811)
    
        
        t_v_ego = FLR20_sig['General']['Time']        
        v_ego = FLR20_sig['General']['actual_vehicle_speed']*3.6
        v_ego_unit = "km/h" 
    
        # Lines
        ax.plot(t_v_ego-t_origin, v_ego,'b' )
        
        
        vRef_ego    =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["actual_vehicle_speed"], FLR20_sig['PosMatrix']['CW']['Time']) 
        vRef_target = (vRef_ego + FLR20_sig['PosMatrix']['CW']['vr'])*(FLR20_sig['PosMatrix']['CW']['Valid']>0)
        ax.plot(FLR20_sig['PosMatrix']['CW']['Time']-t_origin,vRef_target*3.6,'r')
    
    
        # Marker + Text + vertical lines 
        if t_vid_asso is not None:
            v_ego_at_vid_asso   = v_ego[t_v_ego>=t_vid_asso][0]
            ax.plot(t_vid_asso-t_origin, v_ego_at_vid_asso ,'bd')
            ax.text(t_vid_asso-t_origin, 10.0+v_ego_at_vid_asso,'%3.1f %s'% (v_ego_at_vid_asso,v_ego_unit))
    
        if t_cw_track is not None:
            v_ego_at_cw_track   = v_ego[t_v_ego>=t_cw_track][0]
            ax.plot(t_cw_track-t_origin, v_ego_at_cw_track ,'bd')
            ax.text(t_cw_track-t_origin, 10.0+v_ego_at_cw_track,'%3.1f %s'% (v_ego_at_cw_track,v_ego_unit))
    
        if t_warning is not None:
            v_ego_at_t_warning  = v_ego[t_v_ego>=t_warning][0]
            ax.plot(t_warning-t_origin, v_ego_at_t_warning,'md')
            ax.text(t_warning-t_origin, 10.0+v_ego_at_t_warning,'%3.1f %s'% (v_ego_at_t_warning,v_ego_unit))

        if t_braking is not None:
            v_ego_at_t_braking  = v_ego[t_v_ego>=t_braking][0]
            ax.plot(t_braking-t_origin, v_ego_at_t_braking,'rd')
            ax.text(t_braking-t_origin, 10.0 + v_ego_at_t_braking,'%3.1f %s'% (v_ego_at_t_braking,v_ego_unit))
            
        if t_emergency is not None:
            v_ego_at_t_emergency  = v_ego[t_v_ego>=t_emergency][0]
            ax.plot(t_emergency-t_origin, v_ego_at_t_emergency,'rd')
            ax.text(t_emergency-t_origin, 10.0 + v_ego_at_t_emergency,'%3.1f %s'% (v_ego_at_t_emergency,v_ego_unit))
    
        if t_impact is not None:
            v_ego_at_t_impact  = v_ego[t_v_ego>=t_impact][0]
            ax.plot(t_impact-t_origin, v_ego_at_t_impact,'rd')
            if t_warning is not None:
                ax.text(t_impact-t_origin, 10.0 + v_ego_at_t_impact,'%3.1f %s ($\Delta v$=%3.1f %s)'% (v_ego_at_t_impact,v_ego_unit,v_ego_at_t_warning-v_ego_at_t_impact,v_ego_unit))
            else:
                ax.text(t_impact-t_origin, 10.0 + v_ego_at_t_impact,'%3.1f %s '% (v_ego_at_t_impact,v_ego_unit))
    
        
        # legend, labels and grid
        ax.legend(('v ego','v target'))
        ax.set_ylabel('v [%s]'%v_ego_unit)
        create_special_grid(ax)
        ax.set_ylim(v_kph_min,v_kph_max)
        if xlim:
            ax.set_xlim(xlim)
    
    
        # -------------------------------------------------------------------------
        # dx
        ax = fig.add_subplot(812)
    
     
        t_dx = FLR20_sig['Tracks'][0]['Time']
        dx = FLR20_sig['Tracks'][0]['dx'].copy()
        #dx[Fusobj_invalid_mask] = 0
        dx_unit = "m"
 
        # Lines
        ax.plot(t_dx-t_origin, dx,'b' )
    
        # Marker + Text + vertical lines 
        if t_vid_asso is not None:
            dx_at_vid_asso  = dx[t_dx>=t_vid_asso][0]
            ax.plot(t_vid_asso-t_origin,dx_at_vid_asso ,'bd')
            ax.text(t_vid_asso-t_origin, 10.0+dx_at_vid_asso,'%3.1f %s'% (dx_at_vid_asso,dx_unit))

        if t_cw_track is not None:
            dx_at_cw_track  = dx[t_dx>=t_cw_track][0]
            ax.plot(t_cw_track-t_origin,dx_at_cw_track ,'bd')
            ax.text(t_cw_track-t_origin, 10.0+dx_at_cw_track,'%3.1f %s'% (dx_at_cw_track,dx_unit))
    
        if t_warning is not None:
            dx_at_t_warning  = dx[t_dx>=t_warning][0]
            ax.plot(t_warning-t_origin, dx_at_t_warning,'md')
            ax.text(t_warning-t_origin, 10.0+dx_at_t_warning,'%3.1f %s'% (dx_at_t_warning,dx_unit))

        if t_braking is not None:
            dx_at_t_braking  = dx[t_dx>=t_braking][0]
            ax.plot(t_braking-t_origin, dx_at_t_braking,'rd')
            ax.text(t_braking-t_origin, 10.0 + dx_at_t_braking,'%3.1f %s'% (dx_at_t_braking,dx_unit))

        if t_emergency is not None:
            dx_at_t_emergency  = dx[t_dx>=t_emergency][0]
            ax.plot(t_emergency-t_origin, dx_at_t_emergency,'rd')
            ax.text(t_emergency-t_origin, 10.0 + dx_at_t_emergency,'%3.1f %s'% (dx_at_t_emergency,dx_unit))
    
        if t_impact is not None:
            dx_at_t_impact  = dx[t_dx>=t_impact][0]
            ax.plot(t_impact-t_origin, dx_at_t_impact,'rd')
            ax.text(t_impact-t_origin, 10.0 + dx_at_t_impact,'%3.1f %s'% (dx_at_t_impact,dx_unit))

    
    
    
        # legend, labels and grid    
        ax.legend(('dx',))
        ax.set_ylabel('dx [m]')
        create_special_grid(ax)
        ax.set_ylim(dx_min,dx_max)
        if xlim:
            ax.set_xlim(xlim)

        # ------------------------------------------------------
        # dy
        ax = fig.add_subplot(813)
    
        t_dy = FLR20_sig['Tracks'][0]['Time']
        dy = FLR20_sig['Tracks'][0]['dy']
        
        # Lines
        ax.plot(t_dy-t_origin, dy,'b' )
        ax.legend(('dy',))
        ax.set_ylabel('m')
        #ax.set_xlabel('time [s]')
        create_special_grid(ax)
        ax.set_ylim(-5.1,5.1)
        if xlim:
            ax.set_xlim(xlim)      
            
        # -------------------------------------------------------------------------
        # CVR3-S1 available; AEBS acoustic warning
        ax = fig.add_subplot(814)
    
        # Lines
        
        ax.plot(FLR20_sig['Tracks'][0]['Time']-t_origin, FLR20_sig['Tracks'][0]['is_video_associated']+8.0,'k')
    
        ax.plot(FLR20_sig['Tracks'][0]['Time']-t_origin, FLR20_sig['Tracks'][0]['CW_track']+6.0,'m')
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time']-t_origin,FLR20_sig['PosMatrix']['CW']['Valid']+6.0,'b')
    
        if do_bendix:
            ax.plot(FLR20_sig['General']["Time"]-t_origin, 4.0+(FLR20_sig['General']["cm_system_status"]==2.0) ,'b' )
            ax.plot(FLR20_sig['General']["Time"]-t_origin, 2.0+(FLR20_sig['General']["cm_system_status"]==3.0) ,'r' )

        if do_sfn:
        
            if inp['AEBS_Warning'] is not None:
                ax.plot(inp['t']-t_origin, 4.0 + inp['AEBS_Warning'] ,'b' )
        
            if inp['AEBS_Partial_Braking'] is not None:
                ax.plot(inp['t']-t_origin, 2.0 + inp['AEBS_Partial_Braking'] ,'b' )
        
            if inp['AEBS_Emergency_Braking'] is not None:
                ax.plot(inp['t']-t_origin, 0.0 + inp['AEBS_Emergency_Braking'] ,'b' )
 
            '''
            if 'ECU' == AEBS_source:
                if FLR20_sig['AEBS_SFN_OUT']['Time_Warning'] is not None:
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_Warning']-t_origin,     4.0+(FLR20_sig['AEBS_SFN_OUT']['Warning']==1.0) ,'b' )
                elif inp['AEBS_Warning'] is not None:
                    ax.plot(inp['t']-t_origin,     4.0+(inp['AEBS_Warning']==1.0) ,'b' )
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'] is not None:
                    tmp_acopebp_SetRequest = np.logical_and(FLR20_sig['AEBS_SFN_OUT']['AccelDemand']<0.0, FLR20_sig['AEBS_SFN_OUT']['AccelDemand']>-3.0)
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']-t_origin, 2.0+tmp_acopebp_SetRequest ,'g' )
                else:
                    print "FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'] not available"
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'] is not None:
                    tmp_acopebe_SetRequest = FLR20_sig['AEBS_SFN_OUT']['AccelDemand']<-3.0
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']-t_origin,     tmp_acopebe_SetRequest ,'r' )
            elif 'AUTOBOX' == AEBS_source: 
                if FLR20_sig['AEBS_SFN_OUT']['Time_Warning_Autobox'] is not None:
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_Warning_Autobox']-t_origin,     4.0+(FLR20_sig['AEBS_SFN_OUT']['Warning_Autobox']==1.0) ,'b' )
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox'] is not None:
                    tmp_acopebp_SetRequest = np.logical_and(FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox']<0.0, FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox']>-3.0)
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox']-t_origin, 2.0+tmp_acopebp_SetRequest ,'g' )
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox'] is not None:
                    tmp_acopebe_SetRequest = FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox']<-3.0
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox']-t_origin,     tmp_acopebe_SetRequest ,'r' )
            elif 'SIM' == AEBS_source:        
                ax.plot(FLR20_sig['simulation_output']['t']-t_origin,     4.0+(FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0) ,'b' )
                ax.plot(FLR20_sig['simulation_output']['t']-t_origin,     2.0+(FLR20_sig['simulation_output']['acopebp_SetRequest']==1.0) ,'g' )
                ax.plot(FLR20_sig['simulation_output']['t']-t_origin,          FLR20_sig['simulation_output']['acopebe_SetRequest']==1.0 ,'r' )
       
            '''
           
        # Marker + Text + vertical lines 
        if t_vid_asso is not None:
            ax.plot(t_vid_asso-t_origin, 1.0+8.0,'kd')
            ax.text(t_vid_asso-t_origin, 1.2+8.0,'%3.1f s'% (t_vid_asso-t_origin))

        if t_cw_track is not None:
            ax.plot(t_cw_track-t_origin, 1.0+6.0,'bd')
            ax.text(t_cw_track-t_origin, 1.2+6.0,'%3.1f s'% (t_cw_track-t_origin))
    
        if t_warning is not None:
            ax.plot(t_warning-t_origin, 1.0+4.0,'md')
            ax.text(t_warning-t_origin, 1.2+4.0,'%3.1f s'% (t_warning-t_origin))

        if t_braking is not None:
            ax.plot(t_braking-t_origin, 1.0+2.0,'rd')
            ax.text(t_braking-t_origin, 1.2+2.0,'%3.1f s'% (t_braking-t_origin))
            
        if t_emergency is not None:
            ax.plot(t_emergency-t_origin, 1.0+0.0,'rd')
            ax.text(t_emergency-t_origin, 1.2+0.0,'%3.1f s'% (t_emergency-t_origin))
            
         
    
        # legend, labels and grid
        ax.legend(('video asso (+8)','CW track (+6)','Warning (+4)', 'Part. Braking (+2)', 'Emerg. Braking'))
        ax.set_ylabel('AEBS')
        create_special_grid(ax)
        ax.set_ylim(-0.5,10.0)
        if xlim:
            ax.set_xlim(xlim)
  
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        ax = fig.add_subplot(815)
    
        # Lines
        # ax.plot(FLR20_sig["Time_XBRAccDemand"]-t_start, FLR20_sig["XBRAccDemand"] ,'r' )
        
        if do_sfn:
            if 'ECU' == AEBS_source:
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'] is not None:
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']-t_origin, FLR20_sig['AEBS_SFN_OUT']['AccelDemand'] ,'r' )
                if inp['AEBS_XBR'] is not None:
                    ax.plot(inp['t']-t_origin, inp['AEBS_XBR'] ,'b' )
                    
            elif 'AUTOBOX' == AEBS_source: 
                if FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox'] is not None:
                    ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox']-t_origin, FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox'] ,'r' )
            elif 'SIM' == AEBS_source:        
                xbr = FLR20_sig['simulation_output']['acopebp_RequestValue'] + self.FLR20_sig['simulation_output']['acopebe_RequestValue']
                ax.plot(FLR20_sig['simulation_output']['t']-t_origin, xbr ,'r' )
             
           
        if do_bendix:  
                ax.plot(FLR20_sig['Bendix_CMS']["Time"]-t_origin, FLR20_sig['Bendix_CMS']["XBRAccDemand"] ,'r' )
           
    
        
        if FLR20_sig['VBOX_IMU']["IMU_X_Acc"] is not None:
            ax.plot(FLR20_sig['VBOX_IMU']["Time_IMU_X_Acc"]-t_origin, FLR20_sig['VBOX_IMU']["IMU_X_Acc"]*9.81 ,'b' )
            # legend, labels and grid
            ax.legend(('XBR','ax meas'))
        else:
            # legend, labels and grid
            ax.legend(('XBR',))
        
        ax.set_ylabel('m/s$^2$')
        #ax.set_xlabel('time [s]')
        create_special_grid(ax)
        ax.set_ylim(-11.0,2.0)
        if xlim:
            ax.set_xlim(xlim)
      
      
      
        # ------------------------------------------------------
        ax = fig.add_subplot(816)
    
        # Lines
        if 'video_confidence' in FLR20_sig['Tracks'][0]:
            ax.plot(FLR20_sig['Tracks'][0]['Time']-t_origin, FLR20_sig['Tracks'][0]['video_confidence'],'b')
            ax.plot(FLR20_sig['Tracks'][0]['Time']-t_origin, FLR20_sig['Tracks'][0]['radar_confidence'],'r')
            ax.legend(('video_confidence','radar_confidence'))
            ax.set_ylabel('-')
            #ax.set_xlabel('time [s]')
            create_special_grid(ax)
            ax.set_ylim(-0.0,1.1)
            if xlim:
                ax.set_xlim(xlim)
        elif 'confidence_cw_track' in FLR20_sig['General']:
            # confidence_cw_track
            ax.plot(FLR20_sig['General']['Time']-t_origin,FLR20_sig['General']['confidence_cw_track'])
            ax.legend(('confidence_cw_track',))
            ax.set_ylabel('%')
            create_special_grid(ax)
            if xlim:
                ax.set_xlim(xlim)
        
        # -------------------------------------------------------------------------
        # reflected power
        ax = fig.add_subplot(817)
    
        # Lines
        ax.plot(FLR20_sig['Tracks'][0]['Time']-t_origin, FLR20_sig['Tracks'][0]['power'],'r' )
    
        # Text
        #ax.plot(CVR3_res['t_max_dx_S1'], 1.0 + CVR3_offset,'bd')
        #ax.plot(AC100_res['t_max_dx_CW'], 1.0,'rd')

    
        ax.legend(('power',))
        ax.set_ylabel('[db]')
        #ax.set_xlabel('time [s]')
    
        create_special_grid(ax)
        ax.set_ylim(-0.0,100.0)
        if xlim:
            ax.set_xlim(xlim)
      
     
        # ------------------------------------------------------
        ax = fig.add_subplot(818)
    
        # Lines
        ax.plot(FLR20_sig['General']["Time"]-t_origin, FLR20_sig['General']['cvd_yawrate']  ,'b')
        ax.legend(('yaw rate',))
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        create_special_grid(ax)
        #ax.set_ylim(-0.0,40.0)
        if xlim:
            ax.set_xlim(xlim)


  
      
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        # -------------------------------------------------------------------------
        # create png picture
        fig.set_size_inches(16.,12.)
        if show_SIM:
            fig.savefig("%s_@%3.1fs_overview_simulated.png"%(FileName,t_event))
        else:
            if do_bendix:
                fig.savefig("%s_@%3.1fs_overview_Bendix.png"%(FileName,t_event))
            if do_sfn:
                if 'ECU' == AEBS_source:
                    fig.savefig("%s_@%3.1fs_overview_SFN.png"%(FileName,t_event))
                elif 'AUTOBOX' == AEBS_source: 
                    fig.savefig("%s_@%3.1fs_overview_SFN_Autobox.png"%(FileName,t_event))     
                elif 'SIM' == AEBS_source:        
                    pass


    
    
        return fig
        
    # ==========================================================
    def plot_FLR20_processor_time_used(self, FigNr=60, xlim=None):
    
    
        FLR20_sig = self.FLR20_sig
    
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.FileName
        text = "processor time used on FLR20 (%s)"%(FileName,)
        fig.suptitle(text)
       
        
        # ------------------------------------------------------
        # processor_time_used
        ax = fig.add_subplot(711)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['processor_time_used'])
        ax.legend(('processor_time_used',))
        ax.set_ylabel('%')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # number_of_tracks, number_of_targets
        ax = fig.add_subplot(712)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['number_of_tracks'])
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['number_of_targets'])
        ax.legend(('number_of_tracks','number_of_targets'))
        ax.set_ylabel('no.')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # confidence_cw_track
        ax = fig.add_subplot(713)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['confidence_cw_track'])
        ax.legend(('confidence_cw_track',))
        ax.set_ylabel('%')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
        
        # ------------------------------------------------------
        # tacho_correction_factor
        ax = fig.add_subplot(714)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['tacho_correction_factor'])
        ax.legend(('tacho_correction_factor',))
        ax.set_ylabel('?')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

        # ------------------------------------------------------
        # yawrate_offset
        ax = fig.add_subplot(715)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['yawrate_offset'])
        ax.legend(('yawrate_offset',))
        ax.set_ylabel('rad/s')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
        
        # ------------------------------------------------------
        # SP_inst_prob_dynamic_obstruction, SP_inst_prob_antenna_distorted,SP_inst_prob_antenna_blocked
        ax = fig.add_subplot(716)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['SP_inst_prob_dynamic_obstruction'])
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['SP_inst_prob_antenna_distorted'])
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['SP_inst_prob_antenna_blocked'])
        ax.legend(('SP_inst_prob_dynamic_obstruction','SP_inst_prob_antenna_distorted','SP_inst_prob_antenna_blocked'))
        ax.set_ylabel('0..1')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
        
        # ------------------------------------------------------
        # severe_misalignment_angle
        ax = fig.add_subplot(717)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['severe_misalignment_angle'])
        ax.legend(('severe_misalignment_angle',))
        ax.set_ylabel('%')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        # -------------------------------------------------------------------------
        # create png picture
        fig.set_size_inches(16.,12.)
        fig.savefig("%s_processor_time_used.png"%(FileName,))
       
        return fig
    # ==========================================================
    def plot_experimental(self, FigNr = 30,xlim=None, t_start=0):

    
        FLR20_sig = self.FLR20_sig
    
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.FileName
        text = "AEBS on FLR20 - experimental (%s)"%(FileName,)
        fig.suptitle(text)

        # Bendix/TRW AEB cascade    
    
        #t  = FLR20_sig['AC100_tracks'][0]['Time']
        t  = FLR20_sig['PosMatrix']['CW']['Time']
        dx = FLR20_sig['Tracks'][0]['dx']
    
        t_cw_track = FLR20_sig['PosMatrix']['CW']['Time'][FLR20_sig['PosMatrix']['CW']['Valid']>0.5][0]
        t2_cw_track = t[t>t_cw_track][0] 
        dx_cw_track = dx[t>t_cw_track][0]
    
        try:
            t_warning = FLR20_sig['General']["Time"][FLR20_sig['General']["cm_system_status"]>1.5][0]
            t2_warning = t[t>t_warning][0] 
            dx_warning = dx[t>t_warning][0]
        except:
            t_warning = None
            t2_warning = None 
            dx_warning = None
        
    
        try:
            t_braking = FLR20_sig['General']["Time"][FLR20_sig['General']["cm_system_status"]>2.5][0]
            t2_braking = t[t>t_braking][0] 
            dx_braking = dx[t>t_braking][0]
        except:
            t_braking = None
            t2_braking = None
            dx_braking = None
       
    
      
        print "t_cw_track", t_cw_track, t2_cw_track, dx_cw_track
        print "t_warning", t_warning, t2_warning, dx_warning
        print "t_braking", t_braking, t2_braking, dx_braking
    
    
    
    
    
        # cm_system_status 4 "WAITING" 3 "BRAKING" 2 "WARNING" 1 "ALLOWED" 0 "NOT_ALLOWED" ;
    
        # ------------------------------------------------------
        ax = fig.add_subplot(711)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['actual_vehicle_speed']*3.6)
        ax.legend(('vehicle speed',))
        ax.set_ylabel('km/h')
        #ax.set_xlabel('time [s]')
        ax.grid()
    
        # ------------------------------------------------------
        ax = fig.add_subplot(712)
        print len(FLR20_sig['Tracks'][0]['Time']), len(FLR20_sig['Tracks'][0]['dx'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['dx'])
        ax.plot(t2_cw_track,dx_cw_track,'xr')
        ax.plot(t2_warning,dx_warning,'xr')
        ax.plot(t2_braking, dx_braking,'xr')
        ax.legend(('dx',))
        ax.set_ylabel('m')
        #ax.set_xlabel('time [s]')
        ax.grid()
    

        # ------------------------------------------------------
        ax = fig.add_subplot(713)
    
        # Lines 
        ax.plot(FLR20_sig['General']["Time"], FLR20_sig['General']["cm_system_status"] ,'b' )
        ax.plot(FLR20_sig['PosMatrix']['CW']['Time'],FLR20_sig['PosMatrix']['CW']['Valid']*0.5,'r')
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['CW_track']*0.5,'g')
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['is_video_associated'],'m')
     
        # Markers
        ax.plot(t_cw_track,0.5,'xr')
        ax.plot(t_warning,2,'xr')
        ax.plot(t_braking,3,'xr')

        ax.legend(('cm system status','CW track (1)','CW track (2)','is_video_associated'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.0,5.1)
        #ax.set_xlabel('time [s]')
        ax.grid()
    
        # ------------------------------------------------------
        ax = fig.add_subplot(714)
    
        # Lines
        ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'], FLR20_sig['AEBS_SFN_OUT']['AccelDemand'] ,'r' )
           
        
        
        ax.legend(('XBR',))
        ax.set_ylabel('m/s$^2$')
        #ax.set_xlabel('time [s]')
        ax.grid()
    
   
        # ------------------------------------------------------
        ax = fig.add_subplot(715)
    
        # Lines
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['power'])
        ax.legend(('power',))
        ax.set_ylabel('dB')
        #ax.set_xlabel('time [s]')
        ax.grid()

        # ------------------------------------------------------
        ax = fig.add_subplot(716)
    
        # Lines
        '''
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['video_confidence'])
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['radar_confidence'])
        ax.legend(('video_confidence','radar_confidence'))
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
        '''
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['asso_target_index'],'r')
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['asso_target_index'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['asso_video_ID'],'b')
    
        # cw_track
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['CW_track'],'b')
        ax.legend(('CW_track',))
        
        ax.set_ylim(-0.0,1.1)
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
    
        # ------------------------------------------------------
        ax = fig.add_subplot(717)
    
        # Lines
        '''
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['video_confidence'])
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['radar_confidence'])
        ax.legend(('video_confidence','radar_confidence'))
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
        '''
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['angle'],'r')
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['angle'],'b')
  
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['range'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_range'],'r')

        ##ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['angle_MSB']+FLR20_sig['AC100_targets'][0]['angle_LSB'],'b')
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['angle'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_angle'],'r')
    
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['power'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_power'],'r')

        # AEBS_SFN_Warning
        #ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_Warning'], FLR20_sig['AEBS_SFN_OUT']['Warning'],'r')
 
 
        if 'simulation_output' in FLR20_sig:
            ax.plot(FLR20_sig['simulation_output']['t'],     4.0+(FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0) ,'b' )
            ax.plot(FLR20_sig['simulation_output']['t'],     2.0+(FLR20_sig['simulation_output']['acopebp_SetRequest']==1.0) ,'g' )
            ax.plot(FLR20_sig['simulation_output']['t'],          FLR20_sig['simulation_output']['acopebe_SetRequest']==1.0 ,'r' )
        
        ax.set_ylim(-0.0,6.1) 
        ax.legend(('KB AEBS Warning','part. brake','emerg. brake'))
        
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
    
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
     
        # -------------------------------------------------------------------------
        # create png picture
        fig.set_size_inches(16.,12.)
        fig.savefig("%s_experimental.png"%(FileName,))
    
            
        return fig
  
