

import numpy as np

# AECF AllowEntry_and_Cancel_Flags
class CcheckTRW_AECFlags():

    def __init__(self, verbose=False):
        self.verbose = verbose
        pass
    #=================================================================================
    def _check1_AECFlags_phase(self, t_start,t_stop, t_TRW_AECF, global_allow_entry, specific_allow_entry, global_cancel, specific_cancel):
    
    
        if (t_start is None) or (t_stop is None):
            return "no request"

        if (t_stop is None):
            return "error - no t_stop"

        # ----------------------------------
        # allow entry in small window around t_start    
        window_pre = 0.2
        window_post = 0.1
        interval1 = np.logical_and(t_TRW_AECF>=(t_start-window_pre),t_TRW_AECF<=(t_start+window_post))
        cond1 = all(global_allow_entry[interval1]>0.5)
        cond2 = all(specific_allow_entry[interval1]>0.5)
    
        # ----------------------------------
        # cancel
        #interval2 = np.logical_and(t_TRW_AECF>=t_start,t_TRW_AECF<=t_stop)
        #cond3 = not any(global_cancel[interval2]>0.5)
        #cond4 = not any(specific_cancel[interval2]>0.5)
        res_cancel = self._check_cancel_AECFlags_phase(t_start,t_stop, t_TRW_AECF, global_cancel, specific_cancel)
        if res_cancel == "okay":
           cond3 = True
           cond4 = True
        else:
           cond3 = False
           cond4 = False
           
        # ----------------------------------
        # delayed entry
        interval3 = np.logical_and(t_TRW_AECF>=t_start,t_TRW_AECF<=t_stop)
        
        try:
            idx = (np.argwhere(np.logical_and(interval3,global_allow_entry>0.5))[0])[0]   
            t_start_global_allow_entry = t_TRW_AECF[idx]
            print "t_start_global_allow_entry: %7.5fs [%7.5f, %7.5f]s"%(t_start_global_allow_entry,t_start,t_stop)
        except:
            t_start_global_allow_entry = None
            print "t_start_global_allow_entry: error [%7.5f, %7.5f]s"%(t_start,t_stop)
          
        
        try:
            idx = (np.argwhere(np.logical_and(interval3,specific_allow_entry>0.5))[0])[0]   
            t_start_specific_allow_entry = t_TRW_AECF[idx]
            print "t_start_specific_allow_entry: %7.5fs [%7.5f, %7.5f]s"%(t_start_specific_allow_entry,t_start,t_stop)
        except:
            t_start_specific_allow_entry = None
            print "t_start_specific_allow_entry: error [%7.5f, %7.5f]s"%(t_start,t_stop)
    
        delayed = None
        if (t_start_global_allow_entry is not None) and (t_start_specific_allow_entry is not None):
            delayed = min(t_start_global_allow_entry,t_start_specific_allow_entry) - t_start
    
        # ----------------------------------
        res = "not defined"
  
        if cond1 and cond2 and cond3 and cond4:
            res = "okay"
    
        elif not (cond1 and cond2):
            res = "no entry"
            if delayed is not None:
                res = "delayed %6.5f s" % delayed
        
        elif cond1 and cond2 and not (cond3 and cond4):
            res = res_cancel
    
        return res
    
    #=================================================================================
    def _check_cancel_AECFlags_phase(self, t_start, t_stop, t_TRW_AECF, global_cancel, specific_cancel):
        if self.verbose:    
            print "_check_cancel_AECFlags_phase"    
            print "t_start", t_start     
            print "t_stop", t_stop     
                
        if (t_start is None) or (t_stop is None):
            return "no request"

        if (t_stop is None):
            return "error - no t_stop"
       
        interval = np.logical_and(t_TRW_AECF>=t_start,t_TRW_AECF<=t_stop)
        cond1 = not any(global_cancel[interval]>0.5)
        cond2 = not any(specific_cancel[interval]>0.5)
               
        cond1_cancelled_at = None
        if not cond1:
            cond1_cancelled_at = t_TRW_AECF[(np.argwhere(np.logical_and(interval,global_cancel>0.5))[0])[0]]   

        cond2_cancelled_at = None
        if not cond2:
            cond2_cancelled_at = t_TRW_AECF[(np.argwhere(np.logical_and(interval,specific_cancel>0.5))[0])[0]]   

        cancelled_at =  None
        if (cond1_cancelled_at is not None) and (cond2_cancelled_at is not None):
            cancelled_at = min(cond1_cancelled_at,cond2_cancelled_at) 
        elif (cond1_cancelled_at is None) and (cond2_cancelled_at is not None):
            cancelled_at = cond2_cancelled_at
        elif (cond1_cancelled_at is not None) and (cond2_cancelled_at is None):
            cancelled_at = cond1_cancelled_at
        
        
        
        print "cond1_cancelled_at", cond1_cancelled_at
        print "cond2_cancelled_at", cond2_cancelled_at
        print "cancelled_at", cancelled_at
  
        if self.verbose:
            print "interval", interval
            print "global_cancel[interval]", global_cancel[interval]
            print "specific_cancel[interval]", specific_cancel[interval]
            print "cond1", cond1
            print "cond2", cond2
   
        res = "not defined"
  
         
        if cond1 and cond2:
            res = "okay"
        else:
            if cancelled_at is not None:
                res = "cancelled after %3.2fs" % ((cancelled_at-t_start),)
            else:
                res = "cancelled"
    
        return res
    #=================================================================================
    def calc(self, FLR20_sig,t_start):
    
        return self._calc_protected(FLR20_sig,t_start)
        #return self._calc_unprotected(FLR20_sig,t_start)

    #=================================================================================
    def _calc_protected(self, FLR20_sig,t_start):
   
        try:
            res_collision_warning,res_partial_braking,res_emergency_braking = self._calc_unprotected(FLR20_sig,t_start)
        except:
            res_collision_warning = "error2"
            res_partial_braking   = "error2"
            res_emergency_braking = "error2"
            
        return res_collision_warning,res_partial_braking,res_emergency_braking    
        
   
        
   
    #=================================================================================
    def _calc_unprotected(self, FLR20_sig,t_start):

        t_v_ego        = FLR20_sig['General']['Time']        
        v_ego          = FLR20_sig['General']['actual_vehicle_speed']
        
        t_cw_track     = FLR20_sig['PosMatrix']['CW']['Time'] 
        cw_track_valid = FLR20_sig['PosMatrix']['CW']['Valid']
        dx             = FLR20_sig['PosMatrix']['CW']['dx']
        
        # ---------------------------------------------------------------------
        # TRW's allow entry and cancel flags 
        t_TRW_AECF                        = FLR20_sig['ACC_Sxy2']['TRW_AECF']['Time'] 
       
        cm_allow_entry_global_conditions  = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cm_allow_entry_global_conditions']
        cw_allow_entry                    = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cw_allow_entry']
        cmb_allow_entry                   = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cmb_allow_entry']

        cm_cancel_global_conditions       = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cm_cancel_global_conditions']
        cw_cancel                         = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cw_cancel']
        cmb_cancel                        = FLR20_sig['ACC_Sxy2']['TRW_AECF']['cmb_cancel']
        
        
        # ---------------------------------------------------------------------
        Online_AEBSState_t                 = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']
        Online_ABESState_collision_warning = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 5
        Online_ABESState_partial_braking   = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 6
        Online_ABESState_emergency_braking = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 7
  
  
        # check
  
  
        t_start_collision_warning = None
        t_start_partial_braking = None
        t_start_emergency_braking = None
        t_stop_emergency_braking = None
        t_stop2_emergency_braking = None
        t_stop3_emergency_braking = None

        # -----------------------------------------------------
        # start of 
        
        # a) warning
        try: 
            idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start,Online_ABESState_collision_warning>0.5))[0])[0]   
            print "idx",idx
            t_start_collision_warning = Online_AEBSState_t[idx]
        except:
            t_start_collision_warning = None
            
        # b) partial braking
        try:
            idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_collision_warning,Online_ABESState_partial_braking>0.5))[0])[0]   
            print "idx",idx
            t_start_partial_braking = Online_AEBSState_t[idx]
        except:
            t_start_partial_braking = None

        # c) emergency braking    
        try:
            idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_partial_braking,Online_ABESState_emergency_braking>0.5))[0])[0]   
            print "idx",idx
            t_start_emergency_braking = Online_AEBSState_t[idx]
        except:
            t_start_emergency_braking = None
            
           
        # -----------------------------------------------------
        # stop of emergency braking
        if t_start_emergency_braking is not None:   
            try:
                idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_emergency_braking,Online_ABESState_emergency_braking<0.5))[0])[0]   
                print "idx",idx
                t_stop_emergency_braking = Online_AEBSState_t[idx]
            except:
                t_stop_emergency_braking = Online_AEBSState_t[-1]   # end of measurement
    
    
            # t_stop2_emergency_braking: vehicle speed below threshold
            try: 
                v_ego_threshold = 1.0
                cond = v_ego < v_ego_threshold
                idx = (np.argwhere(np.logical_and(t_v_ego>=t_start_emergency_braking,cond))[0])[0]   
                print "idx",idx
                t_stop2_emergency_braking = t_v_ego[idx]
            except:
                t_stop2_emergency_braking = None             
    
            dx_ICB_threshold = 3.5
            try: 
                cond = np.logical_and(cw_track_valid>0.5 , dx <dx_ICB_threshold)
                idx = (np.argwhere(np.logical_and(t_cw_track>=t_start_emergency_braking,cond))[0])[0]   
                print "idx",idx
                t_stop3_emergency_braking = t_cw_track[idx]
            except:
                t_stop3_emergency_braking = None             
        
        '''
        t_start_collision_warning = None
        t_start_partial_braking = None
        t_stop_emergency_braking = None
        t_stop2_emergency_braking = None
        t_stop3_emergency_braking = None
        '''
        
        print "t_start_collision_warning",t_start_collision_warning 
        print "Online_AEBSState_t[0]", Online_AEBSState_t[0]
        print "t_start_partial_braking",t_start_partial_braking 
        print "t_start_emergency_braking",t_start_emergency_braking 
        print "t_stop_emergency_braking",t_stop_emergency_braking
        print "t_stop2_emergency_braking",t_stop2_emergency_braking
        print "t_stop3_emergency_braking",t_stop3_emergency_braking
    
        t_stop = None
        if t_stop_emergency_braking is not None:
            t_stop = t_stop_emergency_braking
        if t_stop2_emergency_braking is not None:
            if t_stop is None:
                t_stop = t_stop2_emergency_braking
            else:
                t_stop = min(t_stop,t_stop2_emergency_braking)
        if t_stop3_emergency_braking is not None:
            if t_stop is None:
                t_stop = t_stop3_emergency_braking
            else:
                t_stop = min(t_stop,t_stop3_emergency_braking)
       
        print "t_stop", t_stop
  
        print"results:"
        # --------------------------------------------------------------------
        # 1. check collision_warning phase
        res_collision_warning = 'error'
        
        if (t_start_collision_warning is None) and (t_start_partial_braking is None):
            # no warning phase found
            res_collision_warning = "no request (???)"
        elif (t_start_collision_warning is not None) and (t_start_partial_braking is not None):
            #  full warning phase
            res_collision_warning =  self._check1_AECFlags_phase(t_start_collision_warning,t_start_partial_braking, t_TRW_AECF, cm_allow_entry_global_conditions, cw_allow_entry, cm_cancel_global_conditions, cw_cancel)
        
        elif (t_start_collision_warning is not None) and (t_start_partial_braking is None):
            # warning phase - request terminates permaturely

            # current stop of warning
            try: 
                idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_collision_warning,Online_ABESState_collision_warning<0.5))[0])[0]   
                #print "idx",idx
                t_stop_collision_warning = Online_AEBSState_t[idx]
                print "t_stop_collision_warning", t_stop_collision_warning
                res_collision_warning =  self._check1_AECFlags_phase(t_start_collision_warning,t_stop_collision_warning, t_TRW_AECF, cm_allow_entry_global_conditions, cw_allow_entry, cm_cancel_global_conditions, cw_cancel)
                res_collision_warning += " (request terminates after %4.3f s)"%((t_stop_collision_warning-t_start_collision_warning),)
            except:
                t_stop_collision_warning = None
                
        # start of measurement
        if t_start_collision_warning is not None:
            t_start_of_measurement = Online_AEBSState_t[0]
            if (t_start_collision_warning-t_start_of_measurement) < 1.0:
                res_collision_warning = "warning: late start of measurement; " + res_collision_warning
                

        print "  res_collision_warning", res_collision_warning
            
        # --------------------------------------------------------------------
  
        # --------------------------------------------------------------------
        # 2. partial_braking
        res_partial_braking = 'error'
        if (t_start_partial_braking is None) and (t_start_emergency_braking is None):
            # no partial braking phase found 
            res_partial_braking = "no request"
            
        elif (t_start_partial_braking is not None) and (t_start_emergency_braking is not None):
            #  full partial braking phase
            res_partial_braking =  self._check1_AECFlags_phase(t_start_partial_braking,t_start_emergency_braking, t_TRW_AECF, cm_allow_entry_global_conditions, cmb_allow_entry, cm_cancel_global_conditions, cmb_cancel)
            
        elif (t_start_partial_braking is not None) and (t_start_emergency_braking is None):
            # partial braking phase - request terminates permaturely
            # current stop of partial braking
            try: 
                idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_partial_braking,Online_ABESState_partial_braking<0.5))[0])[0]   
                #print "idx",idx
                t_stop_partial_braking = Online_AEBSState_t[idx]
                print "t_stop_partial_braking", t_stop_partial_braking
                res_partial_braking =  self._check1_AECFlags_phase(t_start_partial_braking,t_stop_partial_braking, t_TRW_AECF, cm_allow_entry_global_conditions, cmb_allow_entry, cm_cancel_global_conditions, cmb_cancel)
                res_partial_braking += " (request terminates after %4.3f s)"%((t_stop_partial_braking-t_start_partial_braking),)
            except:
                t_stop_partial_braking = None
        
        print "  res_partial_braking", res_partial_braking
  
        # --------------------------------------------------------------------
        # 3. emergency_braking
        res_emergency_braking = self._check_cancel_AECFlags_phase(t_start_emergency_braking,t_stop, t_TRW_AECF, cm_cancel_global_conditions, cmb_cancel)
        print "  res_emergency_braking", res_emergency_braking
        
        
        
        # --------------------------------------------------------------------
        # return 
        return res_collision_warning,res_partial_braking,res_emergency_braking
        
        
