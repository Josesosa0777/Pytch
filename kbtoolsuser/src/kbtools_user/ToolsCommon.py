

import os
#import time
#import numpy as np
#import pylab as pl

import kbtools

import sys, traceback


#=================================================================================
class CActionDetails(object):
     
    def __init__(self, ActionTask):
        self._ActionTask = ActionTask
    
        self.t_start  = None
        self.dura     = None
        self.t_stop   = None
        
        self.FileName = None
        self.DirName  = None
        self.FullPathFileName = None
        
        self.xlim     = None
        self.Vehicle  = None
        
        self.plot_start = None
        self.plot_stop  = None 
        self.plot_xlim  = None
        
        self.gate_start = None
        self.gate_stop  = None
        self.gate       = None
        
        self.VariationName = ''
        self.Description = ''
        self.SimOutput_as_ExpectedResult = False
        self.Vehicle = ''
        self.FLC20_Dataset = ''
        self.FLR20_Dataset = ''
        

    def get(self,name):
        try:
            print "self.ActionTask['%s']"%name, self._ActionTask[name]
            if self._ActionTask[name]:
                return self._ActionTask[name]
            else:
                return None
        except:
            return None
                    
        
    def complete(self):
        # FullPathFileName
        self.FullPathFileName = os.path.join(self.DirName,self.FileName)
        
        # self.dura, self.t_stop 
        if self.t_start is not None:
            if self.dura is None and self.t_stop is not None:
                self.dura = self.t_stop - self.t_start
            elif self.dura is not None and self.t_stop is  None:
                self.t_stop = self.t_start + self.dura 
                
        
        # xlim: t_start and t_stop
        if self.t_stop is not None and self.t_start is not None:
            self.xlim = (self.t_start, self.t_stop)
        else:
            if self.t_start is not None:
                self.xlim = (self.t_start-10.0, self.t_start+20.0)
            else:
                self.xlim = None
                
        #print "t_start, dura",self.t_start,  self.dura   
                
        # plot_xlim: plot_start and plot_stop        
        if self.plot_stop is not None and self.plot_start is not None:
            self.plot_xlim = (self.plot_start, self.plot_stop)
        else:
            self.plot_xlim = None
        #print "plot_start, plot_stop, plot_xlim",self.plot_start, self.plot_stop, self.plot_xlim
        if self.xlim is None and self.plot_xlim is not None:
            print "plot_xlim overrides xlim: " 
            self.xlim = self.plot_xlim
           
        
        
        # gate: gate_start and gate_stop
        if self.gate_stop is not None and self.gate_start is not None:
            self.gate = (self.gate_start, self.gate_stop)
        else:
            self.gate = None
        #print "gate_start, gate_stop, gate",self.gate_start, self.gate_stop, self.gate

        
        # VariationName
        if not self.VariationName:
            print "VariationName is empty -> create it"
            if self.FileName:
                FileName_without_Ext = os.path.splitext(self.FileName)[0]
                if self.t_start is not None:
                    # <FileName_without_Ext>@<t_start>
                    t_start_str = "%7.1fs"%self.t_start
                    t_start_str = t_start_str.replace(" ","_")
                    self.VariationName = "%s@%s"%(FileName_without_Ext,t_start_str)
                else:
                    self.VariationName = FileName_without_Ext
                  
        
#=================================================================================
def GeneratorActionList(InputFileName, verbose = False):
    '''
    
       yields instances of CActionDetails
    '''

    print "GeneratorActionList():", InputFileName
    
    # run Action List
    ActionList = kbtools.CreateActionListFromExcel(InputFileName,EnableRowNamesList=["Enable1","Enable2"])
    for idx,ActionTask in enumerate(ActionList):

        ActionDetails = CActionDetails(ActionTask)
        
        
           
        # FileName
        if 'FileName' in ActionTask:
            ActionDetails.FileName = ActionTask['FileName'].strip() 
        elif 'MeasFile' in ActionTask:
            ActionDetails.FileName = ActionTask['MeasFile'].strip() 
        
        # DirName
        if 'DirName' in ActionTask:
            ActionDetails.DirName = ActionTask['DirName'].strip() 
        elif 'MeasFolder' in ActionTask:
            ActionDetails.DirName = ActionTask['MeasFolder'].strip() 

        # t_start 
        if 't_start' in ActionTask:
            if isinstance(ActionTask['t_start'], (int, long, float, complex)):
                ActionDetails.t_start = ActionTask['t_start']
        if 't start' in ActionTask:   # without underscore !!!
            if isinstance(ActionTask['t start' ], (int, long, float, complex)):
                ActionDetails.t_start = ActionTask['t start' ]
        elif 't_event' in ActionTask:
            if isinstance(ActionTask['t_event'], (int, long, float, complex)):
                ActionDetails.t_start = ActionTask['t_event']
       
        # duration
        if 'dura' in ActionTask:
            if isinstance(ActionTask['dura'], (int, long, float, complex)):
                ActionDetails.dura = ActionTask['dura']
        # Vehicle Types     
        if 'Vehicle' in ActionTask:
            ActionDetails.Vehicle = ActionTask['Vehicle'].strip() 

        # FLC20_Dataset     
        if 'FLC20_Dataset' in ActionTask:
            ActionDetails.FLC20_Dataset = ActionTask['FLC20_Dataset'].strip() 
            
        # FLR20_Dataset     
        if 'FLR20_Dataset' in ActionTask:
            ActionDetails.FLR20_Dataset = ActionTask['FLR20_Dataset'].strip() 
            
            
        # plot_xlim: plot_start and plot_stop
        if 'plot_start' in ActionTask:
            if isinstance(ActionTask['plot_start'], (int, long, float, complex)):
                ActionDetails.plot_start = ActionTask['plot_start']
        if 'plot_stop' in ActionTask:
            if isinstance(ActionTask['plot_stop'], (int, long, float, complex)):
                ActionDetails.plot_stop = ActionTask['plot_stop']
                                
        # gate: gate_start and gate_stop
        if 'gate_start' in ActionTask:
            if isinstance(ActionTask['gate_start'], (int, long, float, complex)):
                ActionDetails.gate_start = ActionTask['gate_start']
        if 'gate_stop' in ActionTask:
            if isinstance(ActionTask['gate_stop'], (int, long, float, complex)):
                ActionDetails.gate_stop = ActionTask['gate_stop']

        # VariationName
        if 'VariationName' in ActionTask:
            if isinstance(ActionTask['VariationName'], (int, long, float, complex)):
                ActionDetails.VariationName = "%02d"%(int(ActionTask['VariationName']))
            else:
                ActionDetails.VariationName = str(ActionTask['VariationName'])


        # Description
        if 'Description' in ActionTask:
            ActionDetails.Description = ActionTask['Description']
     
        # SimOutput_as_ExpectedResult
        if 'SimOutput_as_ExpectedResult' in ActionTask:
            if "x" == ActionTask['SimOutput_as_ExpectedResult'].lower():
                ActionDetails.SimOutput_as_ExpectedResult = True
                
        # Vehicle
        if 'Vehicle' in ActionTask:
            ActionDetails.Vehicle = ActionTask['Vehicle']
    
            
        # ---------------------------------------
        ActionDetails.complete()
       
        if verbose:
            print "Action: idx:", idx
            print "  FileName:                   ", ActionDetails.FileName
            print "  DirName:                    ", ActionDetails.DirName
            print "  xlim:                       ", ActionDetails.xlim
            print "  gate:                       ", ActionDetails.gate
            print "  VariationName:              ", ActionDetails.VariationName
            print "  Description:                ", ActionDetails.Description
            print "  SimOutput_as_ExpectedResult:", ActionDetails.SimOutput_as_ExpectedResult
            print "  Vehicle:                    ", ActionDetails.Vehicle
            print "  t_start:                    ", ActionDetails.t_start
            print "  dura:                       ", ActionDetails.dura
            print "  FLC20_Dataset:              ", ActionDetails.FLC20_Dataset
            print "  FLR20_Dataset:              ", ActionDetails.FLR20_Dataset
            print "  --------"
            
        yield ActionDetails

       
#   [-1.5, -1.0, -0.5, 0.0, +0.5, +1.0, +1.5, +2.0, +2.5]
#=================================================================================
def CreateVideoSnapshots(FullPathFileName,FLR20_sig, t_event, OffsetList = [0.0], PngFolder = r".\png", Tag = '',verbose=False):

    if verbose:
        print "CreateVideoSnapshots", t_event
        
    if Tag:
        Tag = "_"+Tag
   
    if t_event is not None:
        for k,offset in enumerate(OffsetList):
            if verbose:
                print "offset:", offset
            (prefix, sep, suffix) = FullPathFileName.rpartition('.') # strip off file extension
            
            # needs to be aligned with kb_io.py/take_a_picture()
            t_event_str = "%7.1fs"%t_event
            t_event_str = t_event_str.replace(" ","_")
            PngFileName = '%s@%s%s_%02d_%+3.1fs_video.png'%(os.path.join(PngFolder,os.path.basename(prefix)),t_event_str,Tag,k,offset)
    
            #PngFileName = '%s@%3.1fs_%02d_%+3.1fs_video.png'%(os.path.join(PngFolder,os.path.basename(prefix)), t_event,k,offset)
            
            Number_of_MultimediaSignals = 0
            Multimedia_1_available = False
            try:
                if (FLR20_sig['Multimedia']["Time_Multimedia_1"] is not None):
                    Multimedia_1_available = True
                    Number_of_MultimediaSignals = Number_of_MultimediaSignals+1
            except Exception, e:
                pass    
            
            Multimedia_2_available = False
            try:
                if (FLR20_sig['Multimedia']["Time_Multimedia_2"] is not None):
                    Multimedia_2_available = True
                    Number_of_MultimediaSignals = Number_of_MultimediaSignals+1
            except Exception, e:
                pass         
               
                 
            if Number_of_MultimediaSignals==1: 
                try:
                    if Multimedia_1_available:
                        t = FLR20_sig['Multimedia']["Time_Multimedia_1"]
                        Multimedia = FLR20_sig['Multimedia']["Multimedia_1"]
                    elif Multimedia_2_available:
                        t = FLR20_sig['Multimedia']["Time_Multimedia_2"]
                        Multimedia = FLR20_sig['Multimedia']["Multimedia_2"]  
                    t_event_Multimedia = Multimedia[t>=t_event+offset][0]
                    if verbose:
                        print "t_event_Multimedia:", t_event_Multimedia
                    kbtools.take_snapshot_from_videofile(FullPathFileName,t_event_Multimedia, PngFileName, verbose=verbose)
                except Exception, e:
                    print "error - CreateVideoSnapshots(): ",e.message
                    print "error CreateVideoSnapshots",FullPathFileName
                    traceback.print_exc(file=sys.stdout)

            elif Number_of_MultimediaSignals>=2: 
                try:
                    if Multimedia_1_available:
                        t = FLR20_sig['Multimedia']["Time_Multimedia_1"]
                        Multimedia = FLR20_sig['Multimedia']["Multimedia_1"]
                        t_event_Multimedia = Multimedia[t>=t_event+offset][0]
                        if verbose:
                            print "t_event_Multimedia_1:", t_event_Multimedia
                        index = "1"
                        PngFileName = '%s@%s%s_%s.%02d_%+3.1fs_video.png'%(os.path.join(PngFolder,os.path.basename(prefix)),t_event_str,Tag,index,k,offset)
                        kbtools.take_snapshot_from_videofile(FullPathFileName,t_event_Multimedia, PngFileName, AviSuffix='', verbose=verbose)
                        
                    if Multimedia_2_available:
                        t = FLR20_sig['Multimedia']["Time_Multimedia_2"]
                        Multimedia = FLR20_sig['Multimedia']["Multimedia_2"]  
                        t_event_Multimedia = Multimedia[t>=t_event+offset][0]
                        if verbose:
                            print "t_event_Multimedia_2:", t_event_Multimedia
                        index = "2"
                        PngFileName = '%s@%s%s_%s.%02d_%+3.1fs_video_2.png'%(os.path.join(PngFolder,os.path.basename(prefix)),t_event_str,Tag,index,k,offset)
                        kbtools.take_snapshot_from_videofile(FullPathFileName,t_event_Multimedia, PngFileName, AviSuffix='_m0', verbose=verbose)
                except Exception, e:
                    print "error - CreateVideoSnapshots(): ",e.message
                    print "error CreateVideoSnapshots",FullPathFileName
                    traceback.print_exc(file=sys.stdout)
                

#=================================================================================
