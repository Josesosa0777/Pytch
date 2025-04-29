'''
    Base class for plotting


'''


import os
#import time
import numpy as np
import pylab as pl

import kbtools
#import kbtools_user

from matplotlib.ticker import MultipleLocator, FormatStrFormatter

''' http://stackoverflow.com/questions/14708695/specify-figure-size-in-centimeter-in-matplotlib '''
def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)
    
# ==========================================================
class cPlotBase(object):

    # --------------------------------------------------------------------------------------------------------
    def __init__(self,PngFolder = r".\png",show_figures=True):
        '''
            parameters:
                PngFolder      path to folder were generated png files are stored
                show_figures   flag for requesting to show matplotlib figures
        '''
    
    
        self.show_figures = show_figures
        self.PngFolder    = PngFolder
    
        self.xlim_default = None
        self.xlim_to_use(self.xlim_default)
        
        # -------------------------------------------------------------------
        #  attributes for current plot 
        self.PlotName = None  # specific name of the png file
        self.fig      = None  # figure to show and save as png to disk


    # --------------------------------------------------------------------------------------------------------
    def xlim_to_use(self, xlim):
        '''
            set xlim for the next figure
            parameters:
                xlim   (xmin, xmax)   
        '''
        
        self._xlim_to_use = xlim
                
            
            
    # --------------------------------------------------------------------------------------------------------
    def set_description(self, ax, ylabel=None, ylim=None, xlim=None, grid='standard',xlabel=None):
        '''
            set description of subplot
            parameters:  
                ax          current subplot axis
                ylabel      string
                ylim        (ymin, ymax)
                xlim        (xmin, xmax)
                grid        'standard'|'special'
                
        '''
        
        # -----------------------------------------
        # grid
        if grid=='standard':
            ax.grid()
        elif grid=='special':
            self.create_special_grid(ax)
        elif grid=='stacked_flags':
            self.create_stacked_flags_grid(ax) 
            
        # -----------------------------------------
        # y-axis
        
        # ylabel
        if ylabel is not None:
            ax.set_ylabel(ylabel)
            
        # ylim
        if ylim is not None:
            ax.set_ylim(ylim[0],ylim[1])          
        
        # special y-axis annotations
        if grid=='stacked_flags':
            if ylim is not None:
                N = int(np.ceil(ylim[1])/2)   # number of flags
                ax.set_yticks(np.arange(0,2*N)) 
                ax.set_yticklabels(N*['Off','On'])
        
        # -----------------------------------------
        # x-axis
           
        # xlabel
        if xlabel is not None:
            ax.set_xlabel(xlabel)
           
        # xlim
        if xlim is not None:
            ax.set_xlim(xlim[0],xlim[1])          
        elif self._xlim_to_use:
            ax.set_xlim(self._xlim_to_use)
        
        # -----------------------------------------
        # legend
        ax.legend(prop = {'size':10})
        
    # ==========================================================
    def mark_point(self, ax, x,y, LineStyle='',FmtStr='%3.1f', Value=None, yOffset=0.0, label=None, ylim=None):
        '''
            draw a point annotate with a value (text)
            parameters:
                ax          current subplot axis
                x           x-position                
                y           y-position
                LineStyle   color and shape e.g. 'md'
                FmtStr      format string for the value in the annotation text
                            =None -> only Marker will be plotted
                            if two % are included, Value and x will be use, otherwise only Value will be used
                Value       value to annote 
                yOffset     margin to not directly draw the test on the point
                label       set a label for the legend
                ylim        plot range (y_min, y_max)
        '''
       
        
        if Value is None:
            Value = y
        
        #print "PlotBase.mark_point Value", Value
            
        # Marker
        ax.plot(x,y,LineStyle,label=label,markersize=10)  


        # Label
        enable_Label = True
        if ylim is not None:
            y_min = ylim[0]
            y_max = ylim[1]
            if (y_min < y) and (y<y_max):
                enable_Label = True
            else:
                enable_Label = False
        
        if enable_Label and (FmtStr is not None) and (Value is not None) and not np.isnan(Value):
            if (FmtStr.count("%") > 1):
                if (x is not None):
                    ax.text(x,y+yOffset,FmtStr%(Value,x)) 
            else:
                ax.text(x,y+yOffset,FmtStr%(Value,))                  
    # ==========================================================
    def create_special_grid(self, ax):
        '''
            create a fine grid
                parameters:  
                ax          current subplot axis
     
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
  
    # ==========================================================
    def create_stacked_flags_grid(self, ax):
        '''
            create a fine grid
                parameters:  
                ax          current subplot axis
     
        '''

        majorLocator   = MultipleLocator(1)
        majorFormatter = FormatStrFormatter('%d')

        # minorLocator   = MultipleLocator(0.1)
    

        ax.xaxis.set_major_locator(majorLocator)
        ax.xaxis.set_major_formatter(majorFormatter)
        #ax.xaxis.set_minor_locator(minorLocator)
        #ax.xaxis.grid(True, which='both')
    
        #ax.grid(b=True, which='major',  color='k', linestyle='-')
        #ax.grid(b=True, which='minor',  color='k', linestyle=':')
        ax.grid(b=True, which='major', axis = 'x', color='k', linestyle=':',linewidth = 1.0)
        #ax.grid(b=True, which='minor', axis = 'x', color='grey', linestyle=':')
        ax.grid(b=True, which='major', axis = 'y', color='k', linestyle=':',linewidth = 1.0)
        #ax.grid(b=True, which='minor', axis = 'y', color='grey', linestyle=':')
        
        
            
        
        
    #=================================================================================
    def start_fig(self,PlotName="noname", suptitle=None, FigNr=100):
        '''
            create a current figure to put subplots in 
            set PlotName and create a subtitle
           
            parameters:
               PlotName    part of the file name
               suptitle    text show as title of the generated plot
               FigNr       figure number to be used
        '''
        self.PlotName = PlotName  # specific name of the png file
        
        figsize_in_cm = (21.0, 29.7)
        
        fig = pl.figure(FigNr, figsize =cm2inch(figsize_in_cm) )  

        fig.clf()
        
        if suptitle is not None:
            fig.suptitle(suptitle)
        else:
            try:
                if self.input_mode == "FLR20_sig":
                    fig.suptitle("LDWS %s(%s@%.2fs)"%(PlotName,os.path.join(self.PngFolder,self.FileName),self.t_event))
                elif self.input_mode == "SilLDWS_C":
                    fig.suptitle("%s (%s) %s"%(self.PlotName,self.FileName,self.Description))
            except:
                fig.suptitle("%s"%(self.PlotName))
    
    
        self.fig = fig            # figure to show and save as png to disk
        return fig
      

    #=================================================================================
    def show_and_save_figure(self,t_event=None):
        '''
            show current figire and create a png
            parameters:
                t_event   time stamp of event under investigation to become part of the png file name 
        '''        
            
        if self.PlotName is None or self.fig is None:
            print "error show_and_save_figure"
            return
        
        # t_event 
        if t_event is None:
            try:
                t_event = self.t_event
            except:
                t_event = None
        
        # show generated figure to the user
        if self.show_figures:
            self.fig.show()
        
        # generated a png file
        kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName, t_event)
        
        '''
        try:        
            if self.input_mode == "FLR20_sig":
                kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName, self.t_event)
        
            elif self.input_mode == "SilLDWS_C":
                # self.FileName already contains @<t_event>
                kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName)
        except:
            FileName = ''
            kbtools.take_a_picture(self.fig, os.path.join(self.PngFolder,self.FileName), self.PlotName)       
        '''
        
        # reset    
        self.PlotName = None  
        self.fig      = None  
        self.xlim_to_use(self.xlim_default)
