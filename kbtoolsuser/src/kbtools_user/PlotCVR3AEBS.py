#
#  CVR3
#  AEBS use case - Approaching stationary object 
#
#
#  Ulrich Guecker
#
#  2013-07-23  check into MKS
#  2013-03-27
# ---------------------------------------------------------------------------------------------

import os
import time
import numpy as np
import pylab as pl

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import kbtools_user

# ==========================================================
def create_special_grid(ax):

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
    
# ==========================================================
class cPlotCVR3AEBS():

   
    # ==========================================================
    def __init__(self, CVR3_sig):
    
        # CVR3 signals 
        self.CVR3_sig = CVR3_sig
    
        # result of CVR3 Position Matrix S1 Object calculation
        self.CVR3_res = None
        
        # name of measurement file used
        self.FileName = os.path.basename(CVR3_sig['FileName'])
        
        
        self.verbose = False
        #self.verbose = True
        
        pass
 
    # ==========================================================
    def plot_AEBS_overview(self, FigNr = 30,xlim=None, t_start=0, showFileName_b=False):
    
        # ------------------------------------------------
        # CVR3 signals 
        CVR3_sig = self.CVR3_sig
    
        # ------------------------------------------------
        # result of CVR3 Position Matrix S1 Object calculation
        if self.CVR3_res is None:
            self.CVR3_res = kbtools_user.cDataCVR3.calc_S1_performance(CVR3_sig)
        CVR3_res = self.CVR3_res

    
        # ------------------------------------------------
        # AEBS cascade - determine starting point of warning, partial and emergency braking   
        t_warning = CVR3_sig['ASF']['Time'][CVR3_sig['ASF']['FirstWarning']>0.5][0] - t_start
        print "t_warning", t_warning
    
        t_partial_braking = CVR3_sig["J1939"]["Time_XBRAccDemand"][np.logical_and(CVR3_sig["J1939"]["XBRAccDemand"]<=0.0,CVR3_sig["J1939"]["XBRAccDemand"]>=-3.0)][0] - t_start
        print "t_partial_braking", t_partial_braking

        t_emergency_braking = CVR3_sig["J1939"]["Time_XBRAccDemand"][CVR3_sig["J1939"]["XBRAccDemand"]<=-4.0][0] - t_start
        print "t_emergency_braking", t_emergency_braking

    
        # -------------------------------------------------
        # crete figure with subplots
        fig = pl.figure(FigNr)  
        fig.clf()
    
    
        FusObjIdx = CVR3_res['PosS1_FusObjIdx'] 
    
        t = CVR3_sig['FusObj'][FusObjIdx]['Time']
        Fusobj_invalid_mask = np.logical_or(t<CVR3_res['t_start_FUS'], CVR3_res['t_stop_FUS']<t)
    
        # Suptitle
        FileName = self.FileName 
        #text = '%s FusObj[%s]'%(FileName,FusObjIdx)
        if showFileName_b:
            text = "Knorr-Bremse - AEBS (%s)"%(FileName,)
        else:
            text = "Knorr-Bremse - AEBS"
        fig.suptitle(text)
    

    
        # Scaling
        dx_min = -10.0
        dx_max = 60.0
    
        v_kph_min = -10.0
        v_kph_max = 80.0
    
       
        # -------------------------------------------------------------------------
        # v_ego
        ax = fig.add_subplot(411)
    
        t_v_ego = CVR3_sig["EgoVeh"]["Time"]-t_start
        v_ego = CVR3_sig["EgoVeh"]["vxvRef"]*3.6
        v_ego_unit = "km/h" 
    
        # Lines
        ax.plot(t_v_ego, v_ego,'b' )
    
        v_ego_at_t_warning  = v_ego[t_v_ego>=t_warning][0]
        v_ego_at_t_partial_braking  = v_ego[t_v_ego>=t_partial_braking][0]
        v_ego_at_t_emergency_braking  = v_ego[t_v_ego>=t_emergency_braking][0]
    
        # Marker + Text + vertical lines 
        ax.plot(t_warning,v_ego_at_t_warning ,'bd')
        ax.text(t_warning, 10.0+v_ego_at_t_warning,'%3.1f %s'% (v_ego_at_t_warning,v_ego_unit))
      
        ax.plot(t_partial_braking, v_ego_at_t_partial_braking,'md')
        ax.text(t_partial_braking, 10.0+v_ego_at_t_partial_braking,'%3.1f %s'% (v_ego_at_t_partial_braking,v_ego_unit))

        ax.plot(t_emergency_braking, v_ego_at_t_emergency_braking,'rd')
        ax.text(t_emergency_braking, 10.0 + v_ego_at_t_emergency_braking,'%3.1f %s'% (v_ego_at_t_emergency_braking,v_ego_unit))
    
    
        # legend, labels and grid
        ax.legend(('v ego',))
        ax.set_ylabel('v [%s]'%v_ego_unit)
        create_special_grid(ax)
        ax.set_ylim(v_kph_min,v_kph_max)
        if xlim:
            ax.set_xlim(xlim)
    
    
        # -------------------------------------------------------------------------
        # dx
        ax = fig.add_subplot(412)
    
        t_dx = CVR3_sig['FusObj'][FusObjIdx]['Time']-t_start
        dx = CVR3_sig['FusObj'][FusObjIdx]['dx'].copy()
        dx[Fusobj_invalid_mask] = 0
        dx_unit = "m"
 
        # Lines
        ax.plot(t_dx, dx,'b' )
    
    
        dx_at_t_warning  = dx[t_dx>=t_warning][0]
        dx_at_t_partial_braking  = dx[t_dx>=t_partial_braking][0]
        dx_at_t_emergency_braking  = dx[t_dx>=t_emergency_braking][0]
    
        # Marker + Text + vertical lines 
        ax.plot(t_warning,dx_at_t_warning ,'bd')
        ax.text(t_warning, 10.0+dx_at_t_warning,'%3.1f %s'% (dx_at_t_warning,dx_unit))
      
        ax.plot(t_partial_braking, dx_at_t_partial_braking,'md')
        ax.text(t_partial_braking, 10.0+dx_at_t_partial_braking,'%3.1f %s'% (dx_at_t_partial_braking,dx_unit))

        ax.plot(t_emergency_braking, dx_at_t_emergency_braking,'rd')
        ax.text(t_emergency_braking, 10.0 + dx_at_t_emergency_braking,'%3.1f %s'% (dx_at_t_emergency_braking,dx_unit))
    
        # legend, labels and grid    
        ax.legend(('dx',))
        ax.set_ylabel('dx [m]')
        create_special_grid(ax)
        ax.set_ylim(dx_min,dx_max)
        if xlim:
            ax.set_xlim(xlim)

      
        # -------------------------------------------------------------------------
        # CVR3-S1 available; AEBS acoustic warning
        ax = fig.add_subplot(413)
    
        # Lines
        ax.plot(CVR3_sig['ASF']['Time']-t_start, CVR3_sig['ASF']['FirstWarning']+4.0,'b')
        ax.plot(CVR3_sig["J1939"]["Time_XBRAccDemand"]-t_start, 2.0+np.logical_and(CVR3_sig["J1939"]["XBRAccDemand"]<=0.0,CVR3_sig["J1939"]["XBRAccDemand"]>=-3.0) ,'m' )
        ax.plot(CVR3_sig["J1939"]["Time_XBRAccDemand"]-t_start, (CVR3_sig["J1939"]["XBRAccDemand"]<=-4.0) ,'r' )
    
           
        # Marker + Text + vertical lines 
        ax.plot(t_warning, 1.0+4.0,'bd')
        ax.text(t_warning, 1.2+4.0,'%3.1f s'% t_warning)
       
        ax.plot(t_partial_braking, 1.0+2.0,'md')
        ax.text(t_partial_braking, 1.2+2.0,'%3.1f s'% t_partial_braking)

        ax.plot(t_emergency_braking, 1.0+0.0,'rd')
        ax.text(t_emergency_braking, 1.2+0.0,'%3.1f s'% t_emergency_braking)
    
        # legend, labels and grid
        ax.legend(('Acoustic warning (+4)','Partial Braking (+2)', 'Emergency Braking'))
        ax.set_ylabel('AEBS')
        create_special_grid(ax)
        ax.set_ylim(-0.5,6.0)
        if xlim:
            ax.set_xlim(xlim)
  
        # -------------------------------------------------------------------------
        # XBR + measured longitudinal acceleration
        ax = fig.add_subplot(414)
    
        # Lines
        ax.plot(CVR3_sig['J1939']["Time_XBRAccDemand"]-t_start, CVR3_sig['J1939']["XBRAccDemand"] ,'r' )
        ax.plot(CVR3_sig['VBOX_IMU']["Time_IMU_X_Acc"]-t_start, CVR3_sig['VBOX_IMU']["IMU_X_Acc"]*9.81 ,'b' )
    
        # legend, labels and grid
        ax.legend(('XBR','ax meas'))
        ax.set_ylabel('m/s$^2$')
        ax.set_xlabel('time [s]')
        create_special_grid(ax)
        ax.set_ylim(-11.0,2.0)
        if xlim:
            ax.set_xlim(xlim)
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        # -------------------------------------------------------------------------
        # create png picture
        fig.set_size_inches(16.,12.)
        fig.savefig("%s_overview.png"%FileName)
    
        return fig
    


   
 