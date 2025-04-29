'''
    FLC20 Fusion Msg Array ( CAN message data burst)
    
'''

import numpy as np
import pylab as pl


# Utilities_DAS specific imports
import kbtools


#=================================================================================
class CFLC20FusionMsgArray(object):

    # ---------------------------------------------------------------
    def __init__(self,t_head, cnt_head, t_tail, cnt_tail, verbose=True):
    
        self.verbose = verbose

        # attributes to be calculated
        self.success = True
        self.packet_length = None
        self.t_head_BxInfo = None
        self.delay = None
        
        if self.verbose:
            print "CFLC20FusionMsgArray.init() - start"  
            
        # packet start 
        #    t_head:    time point
        #    cnt_head:  message counter values
        # packet end
        #    t_tail:    time point
        #    cnt_tail:  message counter values
  
        self.t_head, self.cnt_head = self._check_Message_Counter(t_head,cnt_head,'Head')
        self.t_tail, self.cnt_tail = self._check_Message_Counter(t_tail,cnt_tail,'Tail')
        
        
        
        
        # processing
        self._treat_start_and_end()
        self._check_packet_length()
        
        if self.verbose:
            print  "head (t_start,t_end,length)", self.t_head[0], self.t_head[-1], self.t_head.size
            print  "tail (t_start,t_end,length)", self.t_tail[0], self.t_tail[-1], self.t_tail.size

        if self.verbose:
            print "CFLC20FusionMsgArray.init() - end"        

    # ---------------------------------------------------------------
    def getSamplingIntervals(self):
        t_SamplingIntervals = self.t_head[0:-1]
        SamplingIntervals = np.diff(self.t_head)
        return t_SamplingIntervals, SamplingIntervals
    
    # ---------------------------------------------------------------
    def _check_Message_Counter(self,t,x,comment):
    
        if self.verbose:
            print "CFLC20FusionMsgArray._check_Message_Counter() - start"
            #print comment, t[0],t[-1],t.size, np.min(np.diff(t))*1000.0, np.max(np.diff(t))*1000.0
            print "  position          :", comment
            print "  t_start, t_end [s]:", t[0],t[-1]
            print "  no of samples     :", t.size
            print "  dt min/max [ms]   :", np.min(np.diff(t))*1000.0, np.max(np.diff(t))*1000.0
            

        # check at which positions counter value is not correctly increased
        idx = np.argwhere(np.diff(x)==0).squeeze()
    
        print "  -> counter violations: ", len(np.atleast_1d(idx))   # len(idx)   -> crashes with idx only one element
       
        t_red = np.delete(t,idx+1)
        x_red = np.delete(x,idx+1)

        if self.verbose:
            if len(np.atleast_1d(idx))>0:
                #print comment, t_red[0],t_red[-1],x_red.size, np.min(np.diff(t_red))*1000.0, np.max(np.diff(t_red))*1000.0
                print "  after reduction:"
                print "    t_start, t_end [s]:", t_red[0],t_red[-1]
                print "    no of samples     :", t_red.size
                print "    dt min/max [ms]   :", np.min(np.diff(t_red))*1000.0, np.max(np.diff(t_red))*1000.0
        
        if self.verbose:
            print "CFLC20FusionMsgArray._check_Message_Counter() - end"
            
        return t_red, x_red    

    # ---------------------------------------------------------------
    def _treat_start_and_end(self):
    
        if self.verbose:
            print "CFLC20FusionMsgArray._treat_start_and_end() - start"
    
        self.packet_length = None
    
        # measurement start        
        if self.t_head[0] < self.t_tail[0]:
            # measurement starts before a packet
            pass
        elif self.t_head[0] < self.t_tail[1]:
            # measurment starts within a packet -> take next packet 
            self.t_head = self.t_head
            self.t_tail = self.t_tail[1:]
        else:  
            self.success = False
            print "CCANMsgDataBurst - error start of measurement"
            print "self.success:", self.success
            print "CFLC20FusionMsgArray._treat_start_and_end() - end"
            return

        # measurement end
        delta_size = self.t_head.size - self.t_tail.size
        print "delta_size", delta_size
        
        if delta_size == 0:
            # measurement ends after a packet
            pass
        elif delta_size == -1:
            # measurement ends within a packet
            self.t_head = self.t_head
            self.t_tail = self.t_tail[:-1]
        elif delta_size == 1:
            # measurement ends within a packet
            self.t_head = self.t_head[:-1]
            self.t_tail = self.t_tail
        else:
            self.success = False        
            print "CCANMsgDataBurst - error at end of measurement 1"
            print "self.success:", self.success
            print "CFLC20FusionMsgArray._treat_start_and_end() - end"
            return
       
        # check          
        if self.t_head[-1] < self.t_tail[-1]:
            pass
        else: 
            self.success = False        
            print "CCANMsgDataBurst - error at end of measurement 2"
            print "self.success:", self.success
            print "CFLC20FusionMsgArray._treat_start_and_end() - end"
            return
        
        self.packet_length = self.t_tail -  self.t_head
        
        if self.verbose:
            print "self.success:", self.success
            print "CFLC20FusionMsgArray._treat_start_and_end() - end"
            
    # ---------------------------------------------------------------
    def _check_packet_length(self):
        if self.packet_length is not None:
            print "packet_length min, max, mean [ms]", np.min(self.packet_length)*1000.0, np.max(self.packet_length)*1000.0,np.mean(self.packet_length)*1000.0
        
    # ---------------------------------------------------------------
    def sync(self,t_sig,sig, tol = 0.01):
        if self.success:
            sync_sig = kbtools.resample(t_sig, sig, self.t_tail+tol) 
            return sync_sig
        else:
            return None
            
    # ---------------------------------------------------------------
    def resample(self,t_sig,sig, t,tol = 0.01):
        if self.success:
            sync_sig = self.sync(t_sig,sig, tol = tol)
        
            resampled_sig = kbtools.resample(self.t_head, sync_sig,t) 
            return resampled_sig
        else:
            return None
    
    # ---------------------------------------------------------------
    def calc_delay(self,Time_Frame_ID,Frame_ID, Time_LNVU_Frame_Id_LSB,LNVU_Frame_Id_LSB,n = 4):

        if self.verbose:
            print "CFLC20FusionMsgArray.calc_delay() - start"
        
        '''
        print "Time_Frame_ID", Time_Frame_ID
        print "Frame_ID", Frame_ID
        print "Time_LNVU_Frame_Id_LSB", Time_LNVU_Frame_Id_LSB
        print "LNVU_Frame_Id_LSB", LNVU_Frame_Id_LSB
        '''
        
        if (Time_Frame_ID is None) or (Time_LNVU_Frame_Id_LSB is None):
            if self.verbose:
                print "CFLC20FusionMsgArray.calc_delay() - end - error"
            return None, None
           
        # ------------------------------------------------------  
        x1 = self.sync(Time_Frame_ID,Frame_ID)
        print "x1", x1
        
        if x1 is None:
            if self.verbose:
                print "CFLC20FusionMsgArray.calc_delay() - end - error"
            return None, None
        
        x1 = x1%n
        x2 = self.sync(Time_LNVU_Frame_Id_LSB,LNVU_Frame_Id_LSB)
    
        dx = x2.astype(np.int16)-x1.astype(np.int16)
        dx[np.logical_and(dx==(n-1),x1==0)] = -1
        dx[np.logical_and(dx==(n-2),x1==0)] = -2
        dx[np.logical_and(dx==(n-3),x1==0)] = -3
        
        # delay is opposite of counter difference
        delay = -dx
        
        

        # create correcte time vector        
        idx = np.arange(delay.size)
        idx = idx-delay
        idx = np.maximum(idx,0)
        idx = np.minimum(idx,idx.size-1)
        t_head_BxInfo = self.t_head[idx]
        
        
        # register        
        self.x1 = x1
        self.x2 = x2
        self.dx = dx
        self.delay = delay
        self.t_head_BxInfo = t_head_BxInfo
        
        if self.verbose:
            print "CFLC20FusionMsgArray.calc_delay() - end - success"
        
        return  self.t_head_BxInfo, self.delay


     
        