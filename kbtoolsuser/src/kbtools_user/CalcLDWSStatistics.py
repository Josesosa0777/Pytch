
import os
import sys
import time

import numpy as np
import pylab as pl

import pandas as pd

# Utilities_DAS specific imports
import kbtools

'''
bitte von den pre-Homologation-Tests als auch von den Homologation-Tests noch eine kurze Statistik erstellen mit folgenden Werten:

Warn.dist.outside        Warn.dist.inside          lat.speed          veh.speed         yaw rate
'''    
class CCalcLDWSStatistics(object):

    def __init__(self):
        self.list_left = []
        self.list_right = []
        
    def add(self, data):
       
        # data is an instance from class COneSide(object) in PlotFLC20LDWS.py
        if data.LDW_okay: 
            if data.side == 'left':
                self.list_left.append(data)
            elif data.side == 'right':
                self.list_right.append(data)
            
    def _write_one_sheet_to_Excel(self, one_list):
    
        out_table_array = []   # Excel table
    
        # --------------------------------------------------------
        # Headings
        ExcelHeadings  = ['FileName']
        ExcelHeadings += ['t start']
        ExcelHeadings += ['Warn.dist.outside']
        ExcelHeadings += ['Warn.dist.inside']
        ExcelHeadings += ['lat.speed']
        ExcelHeadings += ['veh.speed']
        ExcelHeadings += ['yaw rate']
        ExcelHeadings += ['FLC20.dist.inside']
        ExcelHeadings += ['FLC20.lat.speed']
        ExcelHeadings += ['C0 filter delta']
        ExcelHeadings += ['demanded trigger distance']
        ExcelHeadings += ['deviation demanded/real']
       
        
        out_table_array.append(ExcelHeadings)

        TLC = 0.25
        Margin = 0.15
        
        # --------------------------------------------------------
        # Data Lines
        for row in one_list:
            ExcelDataLine=[]
            for name in ExcelHeadings:
                if row.side == 'left':            
                    sign = +1.0
                elif row.side == 'right':            
                    sign = -1.0
                    
                value = 'error'

                if name == 'FileName':
                    value = row.FileName

                elif name == 't start':
                    value = row.t_LDW_start
                
                elif name == 'Warn.dist.outside':
                    try:
                        value = row.VBOX_Range_t_at_t_LDW-row.Wheel-sign*row.width_lane_marking
                    except:
                        value = 'error'
                
                elif name == 'Warn.dist.inside':
                    try:
                        value = row.VBOX_Range_t_at_t_LDW-row.Wheel
                    except:
                        value = 'error'

                elif name == 'lat.speed':
                    value = row.VBOX_Lat_Spd_t_smoothed_at_t_LDW

                elif name == 'veh.speed':
                    value = row.VBOX_Velocity_kmh_at_t_LDW 
                    
                elif name == 'yaw rate':
                    value = row.YawRate_at_t_LDW
                               
                elif name == 'FLC20.dist.inside':
                    try:
                        value = row.C0_at_t_LDW-row.Wheel
                        value = 100*value
                    except:
                        value = 'error'
                        
                elif name == 'FLC20.lat.speed':
                    value = row.lateral_speed_at_t_LDW
               
                elif name == 'C0 filter delta':
                    try:
                        value = row.C0_wheel_filtered_at_t_LDW - row.C0_wheel_at_t_LDW
                        value = 100*value
                    except:
                        value = 'error'
                        
                elif name == 'demanded trigger distance':
                    Margin = 0.15
                    try:
                        value = sign*Margin - row.lateral_speed_at_t_LDW*TLC 
                        value = 100*value
                    except:
                        value = 'error'
                        
                elif name == 'deviation demanded/real':
                   
                    try:
                        Demanded = sign*Margin - row.lateral_speed_at_t_LDW*TLC 
                        Real     = row.C0_wheel_at_t_LDW
                        value =  Demanded - Real
                        value = 100*value
                    except:
                        value = 'error'
                        
                    
                    
                ExcelDataLine.append(value)
            out_table_array.append(ExcelDataLine)
    
        return out_table_array

    
    def write(self,  ExcelFilename = 'logHomologationData.xls'):
    
        WriteExcel = kbtools.cWriteExcel()
        
        WriteExcel.add_sheet_out_table_array("left",self._write_one_sheet_to_Excel(self.list_left))
        WriteExcel.add_sheet_out_table_array("right",self._write_one_sheet_to_Excel(self.list_right))
    
        # create directory if necessary
        ExcelDirName = os.path.dirname(ExcelFilename)
        if ExcelDirName and not os.path.exists(ExcelDirName):
            os.makedirs(ExcelDirName)
    
        WriteExcel.save(ExcelFilename)        

    def read(self,  ExcelFilename = 'logHomologationData.xls'):
    
        xls = pd.ExcelFile(ExcelFilename) 
        sheetname_left = 'left'
        self.df_left = xls.parse(sheetname_left, index_col=None, na_values=['NA'] )
  
        sheetname_right = 'right'
        self.df_right = xls.parse(sheetname_right, index_col=None, na_values=['NA'] )

        print "df_left", self.df_left.head()
        print "df_right", self.df_right.head()
        
    def plot(self,PlotName='LDWS_Statistic_C0_vs_Lateral_Velocity',PngFolder=r'.\results_LDWSStatistics'):
    
        # ---------------------------------------    
        drift_rate_range = (0.0,1.0)
        #y_range = (-0.3,0.3)
        y_range = (-0.5,0.5)
    
        markersize = 10
        mode = ''
        
        
        # --------------------------------------------------
        # C0 vs  Lateral_Velocity
        FigNr = 200
        fig = pl.figure(FigNr)  
        fig.clf()
        fig.suptitle("Distance vs lateral velocity")
        
        ax = fig.add_subplot(211)
        ax.plot(self.df_left['FLC20.lat.speed'],self.df_left['FLC20.dist.inside']/100.0,color='cyan',linestyle='None', marker='o',markersize=markersize, label='FLC20.dist.inside')
        ax.plot(self.df_left['lat.speed'],self.df_left['Warn.dist.inside'],color='blue',linestyle='None', marker='d',markersize=markersize , label='Warn.dist.inside')
        ax.plot(self.df_left['lat.speed'],self.df_left['Warn.dist.outside'],color='red',linestyle='None', marker='s',markersize=markersize , label='Warn.dist.outside')
                
                
        #tmp_t = np.array([drift_rate_range[0],drift_rate_range[1]])
        #tmp_y = -tmp_t*TLC_LEFT+WARN_MARGIN_LEFT
        #ax.plot(tmp_t,tmp_y,'k:',label='TLC_LEFT %3.2f s'%TLC_LEFT)
        #ax.hlines(WARN_MARGIN_LEFT,drift_rate_range[0],drift_rate_range[1],colors='k',linestyles='dashed',label='WARN_MARGIN_LEFT %3.2f m'%WARN_MARGIN_LEFT)
        #ax.hlines(0.0,drift_rate_range[0],drift_rate_range[1],colors='b',linestyles='dashed',label='inner egde of left lane marking')
    
        ax.set_xlim(drift_rate_range)
        ax.set_ylim(y_range)
        ax.grid()
        ax.legend(loc='lower left')
        ax.set_ylabel('inside <- left line [m] -> outside')
    
        ax = fig.add_subplot(212)
                
        ax.plot(-self.df_right['FLC20.lat.speed'],self.df_right['FLC20.dist.inside']/100.0,color='cyan',linestyle='None', marker='o',markersize=markersize, label='FLC20.dist.inside')
        ax.plot(-self.df_right['lat.speed'],self.df_right['Warn.dist.inside'],color='blue',linestyle='None', marker='d',markersize=markersize , label='Warn.dist.inside')
        ax.plot(-self.df_right['lat.speed'],self.df_right['Warn.dist.outside'],color='red',linestyle='None', marker='s',markersize=markersize , label='Warn.dist.outside')

        #tmp_t = np.array([drift_rate_range[0],drift_rate_range[1]])
        #tmp_y = tmp_t*TLC_RIGHT+WARN_MARGIN_RIGHT
        #ax.plot(tmp_t,tmp_y,'k:',label='TLC_RIGHT %3.2f s'%TLC_RIGHT)
        #ax.hlines(WARN_MARGIN_RIGHT,drift_rate_range[0],drift_rate_range[1],colors='k',linestyles='dashed',label='WARN_MARGIN_RIGHT %3.2f m'%WARN_MARGIN_RIGHT)
        #ax.hlines(0.0,drift_rate_range[0],drift_rate_range[1],colors='b',linestyles='dashed',label='inner egde of right lane marking')

        ax.set_xlim(drift_rate_range)
        ax.set_ylim(y_range)
        ax.grid()
        ax.legend(loc='upper left')
        ax.set_ylabel('ouside <- right line [m] -> inside')
        ax.set_xlabel('|LateralDrift Rate| [m/s]')

            
        # ------------------------------------------------------------------    
        #fig.show()
        kbtools.take_a_picture(fig, os.path.join(PngFolder,'LDWS'), PlotName=PlotName)


    
        pass    
 