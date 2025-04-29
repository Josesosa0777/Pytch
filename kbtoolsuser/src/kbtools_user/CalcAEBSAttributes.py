

import numpy as np
import sys, traceback

import kbtools
import kbtools_user

# ==========================================================
# ==========================================================
class cSignal(object):
    '''
       signal object
    '''
    
    def __init__(self,Time,Values,Unit=None,Description=None):
        '''
           Time        : time axis
           Values      : signal values 
           Unit        : unit of signal
           Description : signal description
        '''
        
        self.Time = Time
        self.Values = Values
        self.Unit = Unit 
        self.Description = Description

        


# ==========================================================
# ==========================================================
class cCalcAEBSAttributes(object):
    '''
  
        Calculate AEBS characteristic attributes, 
        e.g. distance, relative velocity at start of warning, partial and emergency braking 
    
        data abstraction layer: _set_signals()
    
    '''

    # ==========================================================
    def __init__(self, FLR20_sig, input_mode, mode, t_event):
        '''
        
            arguments:
                FLR20_sig  :  dictionary with signals from a measurement
                input_mode :  'FLR20' or 'SilAEBS_C'       
                mode       :  'VBOX' or 'FLR20'
                t_event    :  start of AEBS intervention
        '''
        
        print "cCalcAEBSAttributes.__init__() - start"
         
        self._extract_FLR20_sig(FLR20_sig, input_mode, mode, t_event)
        self._calcAEBSAttributes()
        self._set_t_origin()
        
        print "cCalcAEBSAttributes.__init__() - end"
             
    # ==========================================================
    def _set_signals(self, t_event, mode, signals):
        '''
            data abstraction layer:
            set AEBS relevant signals from 'signals' as attributes

            class cSignal to define signals as object     
          
        '''
    
        # backdoor
        self.FLR20_sig = signals['FLR20_sig'].Values
           
        self.t_event              = t_event
        
        self.mode                 = mode
        
        self.Time_ABESState       = signals['ABESState'].Time
        self.ABESState            = signals['ABESState'].Values
        self.Time_XBR_ExtAccelDem = signals['XBR_ExtAccelDem'].Time
        self.XBR_ExtAccelDem      = signals['XBR_ExtAccelDem'].Values
        
                
        self.Time_v_ego           = signals['v_ego'].Time
        self.v_ego                = signals['v_ego'].Values
        
        self.Time_ax_ego          = signals['ax_ego'].Time
        self.ax_ego               = signals['ax_ego'].Values

        self.Time_ax_ego_VBOX_GPS = signals['ax_ego_VBOX_GPS'].Time
        self.ax_ego_VBOX_GPS      = signals['ax_ego_VBOX_GPS'].Values
        
        self.Time_ax_ego_VBOX_IMU = signals['ax_ego_VBOX_IMU'].Time
        self.ax_ego_VBOX_IMU      = signals['ax_ego_VBOX_IMU'].Values
 
        
        self.Time_dx              = signals['dx'].Time
        self.dx                   = signals['dx'].Values
        self.Time_dy              = signals['dy'].Time
        self.dy                   = signals['dy'].Values
        self.Time_vr              = signals['vRel'].Time
        self.vr                   = signals['vRel'].Values
        self.Time_aRel            = signals['aRel'].Time
        self.aRel                 = signals['aRel'].Values
        
        
        self.Time_cw_vidconf      = signals['cw_vidconf'].Time
        self.cw_vidconf           = signals['cw_vidconf'].Values
                
        # Time_v_target
        self.Time_v_target = self.Time_vr
        print "self.Time_vr",self.Time_vr
        print "self.vr",self.vr
        print "self.Time_v_ego",self.Time_v_ego
        print "self.v_ego",self.v_ego
        
        if (self.Time_v_ego is not None) and (self.Time_vr is not None):
            self.v_target = kbtools.resample(self.Time_v_ego,self.v_ego, self.Time_v_target) + self.vr
        else:
            self.Time_v_target = None
            self.v_target = None
        if (signals['TO_valid'].Time is not None) and (self.Time_v_target is not None):
            self.v_target    = self.v_target*(kbtools.resample(signals['TO_valid'].Time, signals['TO_valid'].Values, self.Time_v_target)>0) 
    
    # ==========================================================   
    def _calc_TTC(self,dx,vr):
        
        if (dx is not None) and (vr is not None):
            return -dx/(vr/3.6)
        else:
            return None
            
    # ==========================================================
    def _calcAEBSAttributes(self):

        print "_calcAEBSAttributes() - start"

        delta_t = 1.0
        
        # ---------------------------------------------
        # default settings
        self.AEBS_Track = None
                
        self.AEBS_tr_id_at_t_warning = None                     # internal id of radar track 0..64 
                
        self.AEBS_tr_start_time = None                          # point in time when AEBS track starts
        self.AEBS_tr_start_dx = None                            # distance when AEBS track starts
                
        self.AEBS_video_start_time = None
        self.AEBS_video_start_dx = None

        self.AEBS_tr_is_video_associated_start_time = None
        self.AEBS_tr_is_video_associated_start_dx   = None  

        self.AEBS_tr_is_video_confirmed = None

        self.AEBS_tr_is_video_confirmed_start_time = None
        self.AEBS_tr_is_video_confirmed_start_dx = None
                       
        self.cw_start_time = None
        self.cw_start_dx = None
                
        
        # ---------------------------------------------
        # determine the time points
        self.t_warning   = kbtools.GetTRisingEdge(self.Time_ABESState,self.ABESState==5,t_start=(self.t_event-delta_t),t_stop=(self.t_event+delta_t),shift=0)
        self.t_braking   = kbtools.GetTRisingEdge(self.Time_ABESState,self.ABESState==6,t_start=self.t_warning,shift=0)
        if self.t_braking is not None:
            self.t_emergency = kbtools.GetTRisingEdge(self.Time_ABESState,self.ABESState==7,t_start=self.t_braking,shift=0)
        else:
            self.t_emergency = None
        
        # determine t_impact, t_ego_stopped and t_relaxed only if we had an emergency phase
        if self.t_emergency is not None:
            # self.t_impact    = self.Time_dx[np.nanargmin(self.dx)]
            self.t_impact      = kbtools.GetTRisingEdge(self.Time_dx,self.dx<1.0,t_start=self.t_warning,shift=0)
            self.t_ego_stopped = kbtools.GetTRisingEdge(self.Time_v_ego,self.v_ego<1.0,t_start=self.t_warning,shift=0)
            self.t_relaxed     = kbtools.GetTRisingEdge(self.Time_vr,self.vr>0.0,t_start=self.t_warning,shift=0)
        else:
            self.t_impact      = None
            self.t_ego_stopped = None
            self.t_relaxed     = None
        
        
        # ---------------------------------------------
        # get additional attributes at the time points:
        
        if self.t_warning is not None:
            self.v_ego_at_t_warning           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_warning)
            self.dx_at_t_warning              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_warning)
            self.dy_at_t_warning              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_warning)
            self.vr_at_t_warning              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_warning)
            self.aRel_at_t_warning            = kbtools.GetPreviousSample(self.Time_aRel,self.aRel,self.t_warning)
            self.ABESState_at_t_warning       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_warning)
            #self.v_target_at_t_warning        = self.v_ego_at_t_warning + self.vr_at_t_warning    
            self.v_target_at_t_warning        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_warning) 
            #self.TTC_at_t_warning             = -self.dx_at_t_warning/(self.vr_at_t_warning/3.6)
            self.TTC_at_t_warning             = self._calc_TTC(self.dx_at_t_warning,self.vr_at_t_warning)
            
            
            self.XBR_ExtAccelDem_at_t_warning = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_warning,shift=1)
            
            # ------------------------------------------------------------------------------
            if (self.t_warning is not None):
                # get CW track id
                try:
                    Time_CW_track_id = self.FLR20_sig['PosMatrix']['CW']['Time']
                    CW_track_id      = self.FLR20_sig['PosMatrix']['CW']['id']
                except Exception, e:
                    print "error - _calcAEBSAttributes() ",e.message
                    traceback.print_exc(file=sys.stdout)
                    Time_CW_track_id = None  
                    CW_track_id = None    
            
                self.AEBS_tr_id_at_t_warning   = kbtools.GetPreviousSample(Time_CW_track_id,CW_track_id,self.t_warning,shift=0)
                
                try:
                    self.AEBS_Track = kbtools_user.cDataAC100.get_TrackById(self.FLR20_sig, self.AEBS_tr_id_at_t_warning, verbose=False)
                except Exception, e:
                    print "error - _calcAEBSAttributes() ",e.message
                    traceback.print_exc(file=sys.stdout)
                    self.AEBS_Track = None

                if self.AEBS_Track is not None:
                    self.AEBS_tr_start_time = kbtools.getIntervalAroundEvent(self.AEBS_Track['Time'],self.t_warning,np.logical_and(~np.isnan(self.AEBS_Track['Track']['dx']),self.AEBS_Track['Track']['dx']>0.0), output_mode = 't')[0]
                    self.AEBS_tr_start_dx   = kbtools.GetPreviousSample(self.AEBS_Track['Time'],self.AEBS_Track['Track']['dx'],self.AEBS_tr_start_time)

                    try: 
                        self.AEBS_video_start_time = kbtools.getIntervalAroundEvent(self.AEBS_Track['Time'],self.t_warning,self.AEBS_Track['VideoObj']['Longitudinal_Distance']>0.5, output_mode = 't')[0]
                        self.AEBS_video_start_dx   = kbtools.GetPreviousSample(self.AEBS_Track['Time'],self.AEBS_Track['VideoObj']['Longitudinal_Distance'],self.AEBS_video_start_time)
                    except Exception, e:
                        print "error - _calcAEBSAttributes() AEBS_video_start_time, AEBS_video_start_dx ",e.message
                        traceback.print_exc(file=sys.stdout)
                        self.AEBS_video_start_time = None
                        self.AEBS_video_start_dx = None        

                    self.AEBS_tr_is_video_associated_start_time = kbtools.getIntervalAroundEvent(self.AEBS_Track['Time'],self.t_warning,self.AEBS_Track['Track']['is_video_associated']>0.5, output_mode = 't')[0]
                    self.AEBS_tr_is_video_associated_start_dx   = kbtools.GetPreviousSample(self.AEBS_Track['Time'],self.AEBS_Track['Track']['dx'],self.AEBS_tr_is_video_associated_start_time)
                    
                    self.AEBS_tr_is_video_confirmed = kbtools.hysteresis_lower_upper_threshold(self.AEBS_Track['Track']['video_confidence'],lower_treshold=0.1, upper_treshold=0.25)         
                            
                    self.AEBS_tr_is_video_confirmed_start_time = kbtools.getIntervalAroundEvent(self.AEBS_Track['Time'],self.t_warning,self.AEBS_tr_is_video_confirmed>0.5, output_mode = 't')[0]
                    self.AEBS_tr_is_video_confirmed_start_dx   = kbtools.GetPreviousSample(self.AEBS_Track['Time'],self.AEBS_Track['Track']['dx'],self.AEBS_tr_is_video_confirmed_start_time)
                    
                    self.cw_start_time = kbtools.getIntervalAroundEvent(self.AEBS_Track['Time'],self.t_warning,self.AEBS_Track['Track']['CW_track']>0.5, output_mode = 't')[0]
                    self.cw_start_dx   = kbtools.GetPreviousSample(self.AEBS_Track['Time'],self.AEBS_Track['Track']['dx'],self.cw_start_time)
                                    
                         
        else:
            self.AEBS_Track = None
            
            self.v_ego_at_t_warning           = None
            self.dx_at_t_warning              = None
            self.dy_at_t_warning              = None
            self.vr_at_t_warning              = None
            self.aRel_at_t_warning            = None
            self.ABESState_at_t_warning       = None
            self.v_target_at_t_warning        = None
            self.TTC_at_t_warning             = None
            self.XBR_ExtAccelDem_at_t_warning = None
            
            self.AEBS_tr_id_at_t_warning = None
            
            self.AEBS_tr_start_time = None
            self.AEBS_tr_start_dx = None
                
            self.AEBS_video_start_time = None
            self.AEBS_video_start_dx = None
                
            self.AEBS_tr_is_video_associated_start_time = None
            self.AEBS_tr_is_video_associated_start_dx   = None
            
            self.AEBS_tr_is_video_confirmed_start_time = None
            self.AEBS_tr_is_video_confirmed_start_dx = None
            
            self.cw_start_time = None
            self.cw_start_dx = None            
            
           
        if self.t_braking is not None:        
            self.v_ego_at_t_braking           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_braking)
            self.dx_at_t_braking              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_braking)
            self.dy_at_t_braking              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_braking)
            self.vr_at_t_braking              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_braking)
            self.aRel_at_t_braking            = kbtools.GetPreviousSample(self.Time_aRel,self.aRel,self.t_braking)
            self.ABESState_at_t_braking       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_braking)
            #self.v_target_at_t_braking        = self.v_ego_at_t_braking + self.vr_at_t_braking  
            self.v_target_at_t_braking        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_braking) 
            
            #self.TTC_at_t_braking             = -self.dx_at_t_braking/(self.vr_at_t_braking/3.6)
            self.TTC_at_t_braking             = self._calc_TTC(self.dx_at_t_braking,self.vr_at_t_braking)
            self.XBR_ExtAccelDem_at_t_braking = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_braking,shift=1)
        else:
            self.v_ego_at_t_braking           = None
            self.dx_at_t_braking              = None
            self.dy_at_t_braking              = None
            self.vr_at_t_braking              = None
            self.aRel_at_t_braking            = None
            self.ABESState_at_t_braking       = None
            self.v_target_at_t_braking        = None
            self.TTC_at_t_braking             = None
            self.XBR_ExtAccelDem_at_t_braking = None
        
        if self.t_emergency is not None:
            self.v_ego_at_t_emergency           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_emergency)
            self.dx_at_t_emergency              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_emergency)
            self.dy_at_t_emergency              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_emergency)
            self.vr_at_t_emergency              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_emergency)
            self.aRel_at_t_emergency            = kbtools.GetPreviousSample(self.Time_aRel,self.aRel,self.t_emergency)
            self.ABESState_at_t_emergency       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_emergency)
            #self.v_target_at_t_emergency        = self.v_ego_at_t_emergency + self.vr_at_t_emergency 
            self.v_target_at_t_emergency        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_emergency) 
            
            
            #self.TTC_at_t_emergency             = -self.dx_at_t_emergency/(self.vr_at_t_emergency/3.6)
            self.TTC_at_t_emergency               = self._calc_TTC(self.dx_at_t_emergency,self.vr_at_t_emergency)
            self.XBR_ExtAccelDem_at_t_emergency = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_emergency,shift=1)
        else:
            self.v_ego_at_t_emergency           = None
            self.dx_at_t_emergency              = None
            self.dy_at_t_emergency              = None
            self.vr_at_t_emergency              = None
            self.aRel_at_t_emergency            = None
            self.ABESState_at_t_emergency       = None
            self.v_target_at_t_emergency        = None
            self.TTC_at_t_emergency             = None
            self.XBR_ExtAccelDem_at_t_emergency = None
        
        if self.t_impact is not None:
            self.v_ego_at_t_impact           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_impact)
            self.dx_at_t_impact              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_impact)
            self.dy_at_t_impact              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_impact)
            self.vr_at_t_impact              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_impact)
            self.ABESState_at_t_impact       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_impact)
            #self.v_target_at_t_impact        = self.v_ego_at_t_impact + self.vr_at_t_impact     
            self.v_target_at_t_impact        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_impact) 

            
            self.XBR_ExtAccelDem_at_t_impact = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_impact,shift=1)
        else:
            self.v_ego_at_t_impact           = None
            self.dx_at_t_impact              = None
            self.dy_at_t_impact              = None
            self.vr_at_t_impact              = None
            self.ABESState_at_t_impact       = None
            self.v_target_at_t_impact        = None
            self.XBR_ExtAccelDem_at_t_impact = None
            
        if self.t_ego_stopped is not None:
            self.v_ego_at_t_ego_stopped           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_ego_stopped)
            self.dx_at_t_ego_stopped              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_ego_stopped)
            self.dy_at_t_ego_stopped              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_ego_stopped)
            self.vr_at_t_ego_stopped              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_ego_stopped)
            self.ABESState_at_t_ego_stopped       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_ego_stopped)
            #self.v_target_at_t_ego_stopped        = self.v_ego_at_t_ego_stopped + self.vr_at_t_ego_stopped    
            self.v_target_at_t_ego_stopped        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_ego_stopped) 

            self.XBR_ExtAccelDem_at_t_ego_stopped = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_ego_stopped,shift=1)
        else:
            self.v_ego_at_t_ego_stopped           = None
            self.dx_at_t_ego_stopped              = None
            self.dy_at_t_ego_stopped              = None
            self.vr_at_t_ego_stopped              = None
            self.ABESState_at_t_ego_stopped       = None
            self.v_target_at_t_ego_stopped        = None    
            self.XBR_ExtAccelDem_at_t_ego_stopped = None
            
        if self.t_relaxed is not None:
            self.v_ego_at_t_relaxed           = kbtools.GetPreviousSample(self.Time_v_ego,self.v_ego,self.t_relaxed)
            self.dx_at_t_relaxed              = kbtools.GetPreviousSample(self.Time_dx,self.dx,self.t_relaxed)
            self.dy_at_t_relaxed              = kbtools.GetPreviousSample(self.Time_dy,self.dy,self.t_relaxed)
            self.vr_at_t_relaxed              = kbtools.GetPreviousSample(self.Time_vr,self.vr,self.t_relaxed)
            self.ABESState_at_t_relaxed       = kbtools.GetPreviousSample(self.Time_ABESState,self.ABESState,self.t_relaxed)
            #self.v_target_at_t_relaxed        = self.v_ego_at_t_relaxed + self.vr_at_t_relaxed   
            self.v_target_at_t_relaxed        = kbtools.GetPreviousSample(self.Time_v_target,self.v_target,self.t_relaxed) 

            self.XBR_ExtAccelDem_at_t_relaxed = kbtools.GetPreviousSample(self.Time_XBR_ExtAccelDem,self.XBR_ExtAccelDem,self.t_relaxed,shift=1)
        else:
            self.v_ego_at_t_relaxed           = None
            self.dx_at_t_relaxed              = None
            self.dy_at_t_relaxed              = None
            self.vr_at_t_relaxed              = None
            self.ABESState_at_t_relaxed       = None
            self.v_target_at_t_relaxed        = None    
            self.XBR_ExtAccelDem_at_t_relaxed = None        
        
        if self.t_impact is not None and self.t_ego_stopped is not None:
            if self.t_impact < self.t_ego_stopped :
                self.t_ego_stopped  = None
                
                
        ''' calculate reduced speed '''
        speed_reduced = 0.0
        if (self.v_ego_at_t_warning is not None):    
            
            if self.v_ego_at_t_impact is not None:
                speed_reduced = self.v_ego_at_t_warning-self.v_ego_at_t_impact
            elif self.v_ego_at_t_ego_stopped is not None:
                speed_reduced =  self.v_ego_at_t_warning-self.v_ego_at_t_ego_stopped
            elif self.v_ego_at_t_relaxed is not None:
                speed_reduced = self.v_ego_at_t_warning-self.v_ego_at_t_relaxed
        
        self.speed_reduced = speed_reduced
    
        
        print "t_warning:",self.t_warning
        print "  v_ego_at_t_warning:    ", self.v_ego_at_t_warning
        print "  dx_at_t_warning:       ", self.dx_at_t_warning
        print "  vr_at_t_warning:       ", self.vr_at_t_warning
        print "  v_target_at_t_warning: ",self.v_target_at_t_warning
        print "  aRel_at_t_warning      ", self.aRel_at_t_warning

        print "  AEBS_tr_id_at_t_warning                ", self.AEBS_tr_id_at_t_warning

        print "  AEBS_tr_start_time                     ", self.AEBS_tr_start_time
        print "  AEBS_tr_start_dx                       ", self.AEBS_tr_start_dx

        print "  AEBS_video_start_time                  ", self.AEBS_video_start_time
        print "  AEBS_video_start_dx                    ", self.AEBS_video_start_dx

        print "  AEBS_tr_is_video_associated_start_time ", self.AEBS_tr_is_video_associated_start_time
        print "  AEBS_tr_is_video_associated_start_dx   ", self.AEBS_tr_is_video_associated_start_dx

        print "  AEBS_tr_is_video_confirmed_start_time  ", self.AEBS_tr_is_video_confirmed_start_time
        print "  AEBS_tr_is_video_confirmed_start_dx    ", self.AEBS_tr_is_video_confirmed_start_dx

        print "  cw_start_time                          ", self.cw_start_time
        print "  cw_start_dx                            ", self.cw_start_dx
        
      
        
        print "t_braking",self.t_braking, self.v_ego_at_t_braking,self.dx_at_t_braking,self.vr_at_t_braking,self.v_target_at_t_braking,self.aRel_at_t_braking
        print "t_emergency",self.t_emergency,self.v_ego_at_t_emergency,self.dx_at_t_emergency,self.vr_at_t_emergency,self.v_target_at_t_emergency,self.aRel_at_t_emergency
        print "t_impact",self.t_impact,self.v_ego_at_t_impact,self.dx_at_t_impact,self.vr_at_t_impact,self.v_target_at_t_impact 
        print "t_ego_stopped",self.t_ego_stopped,self.v_ego_at_t_ego_stopped,self.dx_at_t_ego_stopped,self.vr_at_t_ego_stopped,self.v_target_at_t_ego_stopped 
        print "t_relaxed",self.t_relaxed,self.v_ego_at_t_relaxed,self.dx_at_t_relaxed,self.vr_at_t_relaxed,self.v_target_at_t_relaxed 
    
        
    
        print "_calcAEBSAttributes() - end"
               
    
    #-------------------------------------------------------------------------
    def _extract_FLR20_sig(self, FLR20_sig, input_mode, mode, t_event):
        
        '''
            arguments:
                FLR20_sig  :  dictionary with signals from a measurement
                input_mode :  'FLR20' or 'SilAEBS_C'       
                mode       :  'VBOX' or 'FLR20'
                t_event    :  start of AEBS intervention
        '''
        
        print "_extract_FLR20_sig() - start"
        #--------------------------------------------
        # AEBS System State -> Time_ABESState, ABESState
        if input_mode == 'FLR20':   
            # AEBS System State from CAN J1939
            Time_ABESState, ABESState = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"ABESState","-")
            
        elif input_mode == 'SilAEBS_C':
            # from simulation
            Time_ABESState = FLR20_sig['sim_out']['t']    
            ABESState      = FLR20_sig['sim_out']['AEBS1_SystemState']   
        
        #--------------------------------------------
        # XBR_External Acceleration Demand ->  Time_XBR_ExtAccelDem, XBR_ExtAccelDem
        if input_mode == 'FLR20':   
            # AEBS XBR from CAN J1939
            Time_XBR_ExtAccelDem, XBR_ExtAccelDem = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"XBR_ExtAccelDem","m/s^2")
        elif input_mode == 'SilAEBS_C':
            # AEBS XBR from simulation
            Time_XBR_ExtAccelDem = FLR20_sig['sim_out']['t']    
            XBR_ExtAccelDem      = FLR20_sig['sim_out']['XBR_Demand']/2048.0  
         
        #--------------------------------------------
        if mode == 'VBOX':
            
            # Host vehicle speed - GPS
            Time_v_ego =  FLR20_sig["VBOX_IMU"]["Time_Velocity_kmh"]     
            v_ego      =  FLR20_sig["VBOX_IMU"]["Velocity_kmh"]
            
            # Host vehicle acceleration - GPS
            Time_ax_ego = None
            ax_ego = None
            
            # Distance to Target object
            Time_dx    =  FLR20_sig["VBOX_IMU"]["Time_Range_tg1"]
            dx         =  FLR20_sig["VBOX_IMU"]["Range_tg1"] 
            
            # Relative speed of target
            Time_vr    =  FLR20_sig["VBOX_IMU"]["Time_RelSpd_tg1"]
            vr         =  FLR20_sig["VBOX_IMU"]["RelSpd_tg1"]
            
            # Relative acceleration
            Time_aRel  =  FLR20_sig["VBOX_IMU"]["Time_Accel_tg1"]
            aRel       =  FLR20_sig["VBOX_IMU"]["Accel_tg1"]
            if Time_aRel is not None:
                aRel = aRel*9.81
                        
                        
        elif mode == 'FLR20':
        
            # host vehicle speed 
            Time_v_ego, v_ego = kbtools_user.cDataAC100.get_v_ego(FLR20_sig,unit='km/h')

            # host vehicle acceleration 
            Time_ax_ego, ax_ego = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='v_ego')
            
            # Long. Distance to Target object
            Time_dx, dx = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_dx","m")
            
            # Lateral Distance to Target object
            Time_dy, dy = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_dy","m")
            
            # Relative speed of target
            Time_vRel, vRel = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_vRel","km/h")
            
            # Relative acceleration
            Time_aRel, aRel = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_aRel","m/s^2")
              
        
        # host vehicle acceleration 
       
        Time_ax_ego_VBOX_GPS, ax_ego_VBOX_GPS = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_GPS',smooth_filter=True, f_g=1.0)
        Time_ax_ego_VBOX_IMU, ax_ego_VBOX_IMU = kbtools_user.cDataAC100.get_ax_ego(FLR20_sig,unit='m/s^2',mode='VBOX_IMU',smooth_filter=True, f_g=10.0)
                  
            
        
                     
        #--------------------------------------
        # "object is valid valid" flag
        # -> it's only available from A087, but not from RaceLogic
        try:
            Time_TO_valid = FLR20_sig['PosMatrix']['CW']['Time']
            TO_valid      = FLR20_sig['PosMatrix']['CW']['Valid']   
        except:
            Time_TO_valid = None
            TO_valid = None
        
        
        #--------------------------------------
        # "cw_vidconf" flag
        # -> it's only available from ACC S-messages, but not from RaceLogic
        '''
            relationship of 'is_video_associated', 'video_confidence' and 'cw_vidconf'
            
            flag 'is_video_associated' is the input to a pt1-filter with time constant 1 seconds.
            'video_confidence' is the output of this pt1-filter.
            'cw_vidconf' is the output of a hysteresis where 'video_confidence' is the input
             The hystersis has two threshold one for rising 0.25 and for falling 0.1.
             
            is_video_associated -> pt1(T=1sec) -> video_confidence -> hysteresis (risiong: 0.25; falling 0.1) -> cw_vidconf
                
        '''
        try:
            Time_cw_vidconf  = FLR20_sig['ACC_Sxy2']['Time_cw_vidconf']        
            cw_vidconf       = FLR20_sig['ACC_Sxy2']['cw_vidconf']
        except:
            try:
                # video_confidence" flag
                # -> it's only available from A087, but not from RaceLogic
                Time_video_confidence  = FLR20_sig['PosMatrix']['CW']['Time']        
                video_confidence       = FLR20_sig['PosMatrix']['CW']['video_confidence']
                
                Time_cw_vidconf = Time_video_confidence
                cw_vidconf = kbtools.hysteresis_lower_upper_threshold(video_confidence,lower_treshold=0.1, upper_treshold=0.25) 
                
            except:
                Time_cw_vidconf  = None       
                cw_vidconf       = None
                
                         
        # -------------------------------------------------  
        signals = {}     
        # exception !!! -> backdoor
        signals['FLR20_sig']       = kbtools_user.cSignal(None, FLR20_sig,"")
           
        signals['ABESState']       = kbtools_user.cSignal(Time_ABESState, ABESState,"-")
        signals['v_ego']           = kbtools_user.cSignal(Time_v_ego, v_ego,"m/s")
        
        signals['ax_ego']          = kbtools_user.cSignal(Time_ax_ego, ax_ego,"m/s^2")
        signals['ax_ego_VBOX_GPS'] = kbtools_user.cSignal(Time_ax_ego_VBOX_GPS, ax_ego_VBOX_GPS,"m/s^2")
        signals['ax_ego_VBOX_IMU'] = kbtools_user.cSignal(Time_ax_ego_VBOX_IMU, ax_ego_VBOX_IMU,"m/s^2")
        
        
        signals['dx']              = kbtools_user.cSignal(Time_dx, dx,"m")
        signals['dy']              = kbtools_user.cSignal(Time_dy, dy,"m")
        signals['vRel']            = kbtools_user.cSignal(Time_vRel, vRel,"m/s")
        signals['aRel']            = kbtools_user.cSignal(Time_aRel, aRel,"m/s^2")
        signals['TO_valid']        = kbtools_user.cSignal(Time_TO_valid, TO_valid,"-")
        signals['cw_vidconf']      = kbtools_user.cSignal(Time_cw_vidconf, cw_vidconf,"m/s")
        signals['XBR_ExtAccelDem'] = kbtools_user.cSignal(Time_XBR_ExtAccelDem, XBR_ExtAccelDem,"m/s^2")
                    
        self._set_signals(t_event, mode, signals)
        
        print "_extract_FLR20_sig() -  end" 

    #------------------------------------------------------------------------------------------
    def _set_t_origin(self):  
        # -------------------------------------------------
        # self.t_origin 
        if self.t_emergency is not None:
            # origin of the time axis 
            self.t_origin = self.t_emergency
        else:
            self.t_origin = self.t_event
            print "Warning: no AEBS intervention found"

    
   
    #------------------------------------------------------------------------------------------
    def getResults(self):
    
        res = {}
        res["t_warning"]     = self.t_warning 
        res["t_braking"]     = self.t_braking 
        res["t_emergency"]   = self.t_emergency
        res["t_impact"]      = self.t_impact
        res["t_ego_stopped"] = self.t_ego_stopped
        res["t_relaxed"]     = self.t_relaxed

        return res
        
