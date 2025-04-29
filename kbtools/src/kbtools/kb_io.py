'''

   kb_io
   
'''

import os
import sys
import numpy as np
import datetime
import subprocess
import gc

# Utilities_DAS specific imports
import measparser
import kbtools
#import kbtools_user


import scipy.io as sio

class CReadDcnvt3():

    def __init__(self, FileName, FileName_org = None):
        
        print "CReadDcnvt3.__init__(), ",FileName
        # acutual file name 
        self.FileName = FileName
        
        # original FileName (mf4)
        if FileName_org is None:
            self.FileName_org = FileName
        else:   
            self.FileName_org = FileName_org
        
        # --------------------------------------------------   
        # read Matlab Binary
        
        self.MatlabSignals = None
        self.MatlabVarNameList = None
        self.VarNamel2TimeAxis = None
        
        # first check file size
        if os.path.exists(FileName):
            FileSize = os.path.getsize(FileName)
            print "File size ",FileSize
            FileSizeThreshold = 100*1024*1024
            if FileSize > FileSizeThreshold:
                print "File size is bigger than threshold ",FileSizeThreshold
                print "File too big too load"
                return 
        
        # load Matlab Binary into memory
        try:
            self.MatlabSignals = sio.loadmat(FileName)
        except:
            print "CReadDcnvt3.__init__() - error loading <%s>"%FileName
            self.MatlabSignals = None
            return 
        
        # ------------------------------------------------------------------    
        # Create MatlabVarNameList
        #   list of variable name included in the Matlab Binary file 
        if 'zzzzz_Vars_IdxString' in self.MatlabSignals:   
            self.MatlabVarNameList =  str(self.MatlabSignals['zzzzz_Vars_IdxString'][0]).split(';')
        
        # ------------------------------------------------------------------    
        # Create VarNamel2TimeAxis
        #   dictionary relating variables to corresponding time axis
        if 'zzzzz_IdxVariable_IdxTimeaxis' in self.MatlabSignals:
            self.VarNamel2TimeAxis = self._Build_VarNamel2TimeAxis(self.MatlabSignals['zzzzz_IdxVariable_IdxTimeaxis'])

            
        # ------------------------------------------------------------------    
        # 'zzzzz_StartofMeasurement' - obsolete - only for dcnvt3 V3.121; removed in V3.122
        if 'zzzzz_StartofMeasurement' in self.MatlabSignals:
            print '  zzzzz_StartofMeasurement', float(self.MatlabSignals['zzzzz_StartofMeasurement'][0])
        
        # ------------------------------------------------------------------    
        # 'zzzzz_AbsStartTimeOfMeasurement'  - dcnvt3 V3.122 option "-f rel" 
        # absolute time stamp of measurement start
        self.tp_AbsStartTimeOfMeasurement = None
        self.fmt = "%Y-%m-%d %H:%M:%S,%f"
        if 'zzzzz_AbsStartTimeOfMeasurement' in self.MatlabSignals:
            #print '  zzzzz_AbsStartTimeOfMeasurement', self.MatlabSignals['zzzzz_AbsStartTimeOfMeasurement'][0]
            
            self.tp_AbsStartTimeOfMeasurement = datetime.datetime.strptime(self.MatlabSignals['zzzzz_AbsStartTimeOfMeasurement'][0],self.fmt)
            
        # ------------------------------------------------------------------    
        # 'zzzzz_TimesMeasurement' - dcnvt3 V3.122 option "-f StartTimes" 
        # time stamp of first and last sample
        self.tp_AbsStartTimeFirstSample = None
        self.tp_AbsStartTimeLastSample = None
        
        if 'zzzzz_TimesMeasurement' in self.MatlabSignals:
            zzzzz_TimesMeasurement = [float(s) for s in self.MatlabSignals['zzzzz_TimesMeasurement'][0].split(';')]
            #print '  zzzzz_TimesMeasurement', zzzzz_TimesMeasurement, zzzzz_TimesMeasurement[0], zzzzz_TimesMeasurement[1]
            if self.tp_AbsStartTimeOfMeasurement is not None:
                self.tp_AbsStartTimeFirstSample = self.tp_AbsStartTimeOfMeasurement + datetime.timedelta(0,zzzzz_TimesMeasurement[0])
                self.tp_AbsStartTimeLastSample  = self.tp_AbsStartTimeOfMeasurement + datetime.timedelta(0,zzzzz_TimesMeasurement[1])
        
        if self.tp_AbsStartTimeOfMeasurement is not None:      
            print "  tp_AbsStartTimeOfMeasurement:", self.tp_AbsStartTimeOfMeasurement.strftime(self.fmt)
        else: 
            print "  tp_AbsStartTimeOfMeasurement:", self.tp_AbsStartTimeOfMeasurement
        
        if self.tp_AbsStartTimeFirstSample is not None:
            print "  tp_AbsStartTimeFirstSample  :", self.tp_AbsStartTimeFirstSample.strftime(self.fmt)
        else: 
            print "  tp_AbsStartTimeFirstSample  :", self.tp_AbsStartTimeFirstSample
            
        if self.tp_AbsStartTimeLastSample is not None:    
            print "  tp_AbsStartTimeLastSample   :", self.tp_AbsStartTimeLastSample.strftime(self.fmt)
        else:
            print "  tp_AbsStartTimeLastSample   :", self.tp_AbsStartTimeLastSample
        
    #=====================================================================                     
    def isValid(self):
        if self.MatlabSignals is None:
            return False
        
        return True
            
    #=====================================================================                     
    def GetAbsStartTimeOfMeasurement(self, mode='fmt', fmt=None, offset_sec=None ):
        '''
           offset_sec - offset in seconds
        
        '''
        if fmt is None:        
            fmt = self.fmt
        
        if mode=='raw':
                return self.tp_AbsStartTimeOfMeasurement
        elif mode=='fmt':    
                if self.tp_AbsStartTimeOfMeasurement is not None:  
                    if offset_sec is not None and isinstance(offset_sec, (int, long, float)):
                        tp = self.tp_AbsStartTimeOfMeasurement + datetime.timedelta(0,offset_sec)
                        return tp.strftime(self.fmt)
                    else:
                        return self.tp_AbsStartTimeOfMeasurement.strftime(self.fmt)
                else:
                    return "error"                
                  
    #=====================================================================                     
    def GetAbsStartTimeFirstSample(self, mode='fmt', fmt=None, offset_sec=None ):
        '''
           offset_sec - offset in seconds
        
        '''
        if fmt is None:        
            fmt = self.fmt
        
        if mode=='raw':
                return self.tp_AbsStartTimeFirstSample
        elif mode=='fmt':    
                if self.tp_AbsStartTimeFirstSample is not None:  
                    if offset_sec is not None and isinstance(offset_sec, (int, long, float)):
                        tp = self.tp_AbsStartTimeFirstSample + datetime.timedelta(0,offset_sec)
                        return tp.strftime(self.fmt)
                    else:
                        return self.tp_AbsStartTimeFirstSample.strftime(self.fmt)
                else:
                    return "error"            
    #=====================================================================                     
    def GetAbsStartTimeLastSample(self, mode='fmt', fmt=None, offset_sec=None ):
        '''
           offset_sec - offset in seconds
        
        '''
        if fmt is None:        
            fmt = self.fmt
        
        if mode=='raw':
                return self.tp_AbsStartTimeLastSample
        elif mode=='fmt':    
                if self.tp_AbsStartTimeLastSample is not None:  
                    if offset_sec is not None and isinstance(offset_sec, (int, long, float)):
                        tp = self.tp_AbsStartTimeLastSample + datetime.timedelta(0,offset_sec)
                        return tp.strftime(self.fmt)
                    else:
                        return self.tp_AbsStartTimeLastSample.strftime(self.fmt)
                else:
                    return "error"            
                
                      
    #=====================================================================                     
    def GetSignal(self, Device, SignalName):
        
        Time = None
        Value = None
        
        if self.VarNamel2TimeAxis is None:
            return  Time, Value 
        
        if SignalName in self.VarNamel2TimeAxis:
            #print SignalName, self.VarNamel2TimeAxis[SignalName]
            Time  = self.MatlabSignals[self.VarNamel2TimeAxis[SignalName]].squeeze() # remove single-dimensional entries (if any)
            Value = self.MatlabSignals[SignalName].squeeze() # remove single-dimensional entries (if any)
            return  Time, Value 
            
        # SignalName is not unique -> append Device Name    
        ExtendedName = "%s_%s"%(SignalName,Device)
        if ExtendedName in self.VarNamel2TimeAxis:
            #print ExtendedName, self.VarNamel2TimeAxis[ExtendedName]
            Time  = self.MatlabSignals[self.VarNamel2TimeAxis[ExtendedName]].squeeze() # remove single-dimensional entries (if any)
            Value = self.MatlabSignals[ExtendedName].squeeze() # remove single-dimensional entries (if any)
            return  Time, Value 

        
        print "missing: %s,%s "%(Device, SignalName)
         
        return  Time, Value
        
    

    #=====================================================================                     
    def _Build_VarNamel2TimeAxis(self,zzzzz_IdxVariable_IdxTimeaxis):
        VarNamel2TimeAxis = {}    
        for (SignalIndex,TimeIndex,_) in zzzzz_IdxVariable_IdxTimeaxis:
            if  SignalIndex != TimeIndex:   # we have a signal
                MatlabName = self.MatlabVarNameList[SignalIndex]
                if MatlabName not in VarNamel2TimeAxis:
                    VarNamel2TimeAxis[MatlabName] = self.MatlabVarNameList[TimeIndex]
        return VarNamel2TimeAxis
        
       
    
    #=====================================================================                     
    def Print_MatlabRawSignals(self):  
        # this are all the signals in the Matlab Binary File    
        for signal in self.MatlabSignals:
            print signal
            
    #=====================================================================                     
    def Print_MatlabVarNames(self):  
        # this are all the signals in the Matlab Binary File    
        for k,signal in enumerate(self.MatlabVarNameList):
            print k+1, signal

        print "%d signal"%(k+1)  
        
    #=====================================================================                     
    def Print_SignalNames(self):  
        # this are all the signals in the Matlab Binary File
        k = 0        
        for SignalName in self.VarNamel2TimeAxis.iterkeys():
            print k+1, SignalName
            k+=1

        print "%d signal"%(k+1)  
            
            
    #=====================================================================                     
    def save(self):
        # just to be compatible -> without any effect
        pass

#*********************************************************************************************
def GetSignal(Source,DeviceName,SignalName,verbose=False):

    if isinstance(Source, CReadDcnvt3):
        Time, Value = Source.GetSignal(DeviceName, SignalName)
        return  Time, Value
    
    elif isinstance(Source, measparser.cSignalSource):
        try: 
            SignalGroups = [{"myname": (DeviceName, SignalName),},]
            Group = Source.selectFilteredSignalGroup(SignalGroups)
            Time, Value = Source.getSignalFromSignalGroup(Group, "myname")
       
            # (N,1) -> (N,)   
            if len(Time.shape)>1:
                #print "reshape required"         
                Time  = np.reshape(Time,Time.size)
                Value =  np.reshape(Value,Value.size)
               
            return Time, Value
    
        except (ValueError,KeyError, measparser.signalgroup.SignalGroupError), error:
            '''
              measparser.signalgroup.SignalGroupError
                Group = signalgroup.select_longest(Groups, Errors)
                File "c:\util_das\dataio\src\measparser\signalgroup.py", line 109, in select_longest
                raise SignalGroupError(message)
            '''
            if verbose:
                print "Device/Signal not available : %s/%s "%(DeviceName, SignalName)  # os.path.basename(__file__)
                print error.message
            return None, None
    else:
        Time = None
        Value = None
        return Time, Value

#*********************************************************************************************
def None2Nan(x):
    '''
       Because 'None' cannot be inlcuded in a Matlab Binary; 'None' is converted to a single NaN value
    '''
    if x is None:
        x = np.nan
    return x

def load_Matlab_file(FileName, ConvertSignalNan2None = False):
    ''' load matlab binary file and convert matrix to vectors '''

    # load simulation output (*.mat)    
    matdata = sio.loadmat(FileName, matlab_compatible  = True)
        
    # matrix to vector
    matdata = matrix2vector(matdata, ConvertSignalNan2None = ConvertSignalNan2None)
    
    return matdata

def matrix2vector(matdata, ConvertSignalNan2None = False):
    # a) matrix to vector
    # b) array of chars -> string
    for signal in matdata.keys():
        if isinstance(matdata[signal],np.ndarray):
            #print matdata[signal].dtype
            if matdata[signal].dtype == np.dtype('<U1'):
                # array of chars -> string
                #print signal, matdata[signal]
                try:
                    matdata[signal] = ''.join(matdata[signal][0])    
                except:
                    matdata[signal] = ''
            else:
                # float 64
                #matdata[signal] = matdata[signal][0]
                matdata[signal] = matdata[signal].squeeze() 
                if ConvertSignalNan2None:
                    if (matdata[signal].size == 1) and (np.isnan(matdata[signal])):
                        matdata[signal] = None
                
    return matdata

#*********************************************************************************************
def convert_dcnvt(MeasFile,dbc_list, MatHomeDir = r'C:\KBData\matlab_tmp', verbose=False):
    
    if verbose:
        print "convert_dcnvt()"
    
    InputFolderName  = os.path.dirname(MeasFile)
    SubFolderName    = os.path.split(os.path.dirname(MeasFile))[1]
    BaseFileName     = os.path.splitext(os.path.basename(MeasFile))[0]
    
    if MatHomeDir is None:
        OutputFolderName = InputFolderName
    else:
        OutputFolderName = os.path.join(MatHomeDir,SubFolderName)
    
    New_MeasFile     = os.path.join(OutputFolderName,BaseFileName+'.mat')
    
    if verbose:
        print "  InputFolderName: ", InputFolderName  
        print "  SubFolderName:   ", SubFolderName    
        print "  BaseFileName:    ", BaseFileName  
        print "  OutputFolderName:", OutputFolderName    
        print "  New_MeasFile:    ", New_MeasFile    
    
    #clean_up=False
    clean_up=True
        
    dcnvt3 = kbtools.Cdcnvt3(clean_up=clean_up, verbose=verbose)
    dcnvt3.set_dbc_list(dbc_list)
    dcnvt3.set_input_files(BaseFileName, suffix_list=[], InputFolderName=InputFolderName)
    dcnvt3.set_output_file('M', BaseFileName,'.mat', OutputFolderName, overwrite=True)
    #dcnvt3.convert(DcnvtName="dcnvt3")
    dcnvt3.convert()
  
    print "conversion ready"

# ==========================================================
def wrapper_measparser_cSignalSource(FullPathFileName, NpyHomeDir):
    '''
        wrapper for measparser.cSignalSource
        
        return Source created by measparser.cSignalSource otherwise None
        
    '''

    Source = None
    
    # open measurement file to access signals -> Source
    if os.path.isfile(FullPathFileName):

        # create NpyHomeDir is necessary
        if not os.path.exists(NpyHomeDir):
            os.makedirs(NpyHomeDir)
     
        Source = measparser.cSignalSource(FullPathFileName, NpyHomeDir)
        # Source.save() # create backup directory
        
    return Source
 

# ==========================================================
def load_Source(FullPathFileName, mode= 'smart', dbc_list=None, NpyHomeDir = r'local', MatHomeDir = r'C:\KBData\matlab_tmp', verbose=False):

    #------------------------------------------------------
    # NpyHomeDir: Specify the locations where measparser.cSignalSource stores the backup files



    if verbose:
        print "load_Source()" 
        print "  FileName  :", os.path.basename(FullPathFileName)
        print "  PathName  :", os.path.dirname(FullPathFileName)
        print "  mode      :", mode
        print "  dbc_list  :", dbc_list
        print "  NpyHomeDir:", NpyHomeDir
        print "  MatHomeDir:", MatHomeDir
        
    Source = None
 
    if verbose:
        print ""
        print "  processing ..."
 
    if FullPathFileName.upper().endswith('.MAT'):
        if verbose:
            print "  -> FileName ends with *.mat -> a Matlab Binary file shall be loaded"
            
        # open measurement file to access signals -> Source
        if os.path.isfile(FullPathFileName):
            Source =  CReadDcnvt3(FullPathFileName)
            if verbose:
                print "   FLR20_sig loaded"  
            return Source            
        else:
            # try to convert a *.MF4 file
            (prefix, sep, suffix) = FullPathFileName.rpartition('.')
            MF4FileName = prefix + '.MF4'
            convert_dcnvt(MF4FileName,dbc_list,verbose=verbose)
            if os.path.isfile(FullPathFileName):
                Source =  CReadDcnvt3(FullPathFileName) 
                if verbose:
                    print "   Source loaded"  
                return Source
            else:
                print "error dcnvt3"

        return Source
        
    elif FullPathFileName.upper().endswith(('.MF4','.MDF')):
        if verbose:
            print "    -> FileName ends with *.MF4/*.MDF -> a MF4/MDF file shall be loaded"
            
        if mode == 'smart':
            # smart mode: load Matlab Binary file
            if verbose:
                print "     we are in smart mode -> load Matlab Binary"
        
            if MatHomeDir is not None:
                (prefix, sep, suffix) = FullPathFileName.rpartition('.') 
                SubFolder = os.path.split(os.path.dirname(prefix))[1]
                Basename = os.path.basename(prefix)
                MatFileName = os.path.join(MatHomeDir,SubFolder,Basename+ '.mat')
                #print "SubFolder", SubFolder
                #print "Basename", Basename
                if verbose:
                    print "     we are looking in MatHomeDir for MatFileName", MatFileName
            
                if os.path.isfile(MatFileName):
                    if verbose:
                        print "    -> Matlab Binary file available in MatHomeDir -> this is used"
                    Source =  CReadDcnvt3(MatFileName,FileName_org=FullPathFileName) 
                    if verbose:
                        print "   Success: Source loaded"  
                    return Source
                else: 
                    if verbose:
                        print "    -> Matlab Binary file not available in MatHomeDir !!!"
                                    
                
            # -------------------------------
            # load Matlab Binary next to mf4
            (prefix, sep, suffix) = FullPathFileName.rpartition('.') 
            MatFileName = prefix + '.mat'
            if verbose:
                print "  we are looking now for MatFileName", MatFileName
            if os.path.isfile(MatFileName):
                print "    -> Matlab Binary file available in specified folder -> this is used"
                Source =  CReadDcnvt3(MatFileName,FileName_org=FullPathFileName) 
                if verbose:
                    print "   Success: Source loaded"  
                return Source
            else: 
                if verbose:
                    print "    -> Matlab Binary file not available !!!"
                
            # -------------------------------
            # create Matlab Binary
            MF4FileName = FullPathFileName
            (prefix, sep, suffix) = FullPathFileName.rpartition('.') 
            SubFolder = os.path.split(os.path.dirname(prefix))[1]
            Basename = os.path.basename(prefix)
            MatFileName = os.path.join(MatHomeDir,SubFolder,Basename+ '.mat')

            if verbose:
                print "  create Matlab Binary from MF4/MDF and blf", MatFileName

            convert_dcnvt(MF4FileName,dbc_list,MatHomeDir=MatHomeDir,verbose=verbose)

            if os.path.isfile(MatFileName):
                Source =  CReadDcnvt3(MatFileName,FileName_org=FullPathFileName) 
                if verbose:
                    print "   Source loaded"  
                return Source 
            else:
                print "error dcnvt3"
                
            # -------------------------------
            # load MF4/MDF file
            if verbose:
                print "  -> FileName ends with *.MF4/MDF-> a MF4/MDF file shall be loaded"

            Source = wrapper_measparser_cSignalSource(FullPathFileName, NpyHomeDir)
                    
            if Source is not None:    
                if verbose:
                    print "   Source loaded"            
                return Source                     
            
            # if this is reached we will return None
            return Source 
        # ----------------------------------------------------------------     
        else:
            # 
            if verbose:
                print "  -> directly load a MF4/MDF file"

            Source = wrapper_measparser_cSignalSource(FullPathFileName, NpyHomeDir)
                    
            if Source is not None:    
                if verbose:
                    print "   Source loaded"            
                return Source                     
            
            # if this is reached we will return None
            return Source 
    
    else:
        print "%s doesn't exist"%FullPathFileName

    
    return Source

    
#*********************************************************************************************
def take_a_picture(fig, FileName="dummy", PlotName="default", t_event= None):
    ''' create png picture 
        leading underscores
    
    '''
            
    if t_event is None:
        PngFileName  = "%s_%s.png"%(FileName,PlotName)
    else:
        #PngFileName  = "%s@%3.1fs_%s.png"%(FileName,t_event,PlotName)
        t_event_str = "%7.1fs"%t_event
        t_event_str = t_event_str.replace(" ","_")
        PngFileName  = "%s@%s_%s.png"%(FileName,t_event_str,PlotName)
    
    # create destination folder if necessary    
    PngFolder = os.path.dirname(PngFileName)
    #print "take_a_picture PngFolder <%s>" % PngFolder
    if PngFolder and not os.path.exists(PngFolder):
        os.makedirs(PngFolder)
        
    fig.set_size_inches(16.,12.)
    fig.savefig(PngFileName)    
#*********************************************************************************************
def secs2time(s):
    ''' converts seconds to time structure'''

    # http://bytes.com/topic/python/answers/485206-time-conversions-hh-mm-ss-ms-sec-ms
    ms = int((s - int(s)) * 1000000)
    s = int(s)
    # Get rid of this line if s will never exceed 86400
    while s >= 24*60*60: s -= 24*60*60
    h = s / (60*60)
    s -= h*60*60
    m = s / 60
    s -= m*60
    return datetime.time(h, m, s, ms)
 
def time2secs(d):
    ''' converts time structure to seconds '''

    # http://bytes.com/topic/python/answers/485206-time-conversions-hh-mm-ss-ms-sec-ms
    return d.hour*60*60 + d.minute*60 + d.second + (float(d.microsecond) / 1000000)
    
#*********************************************************************************************
class CSnapshotFromVideofile(object):
    def __init__(self,BatchFileName=None,verbose=False):
        
        self.verbose=verbose
        self.run_ffmpeg = True
        
        self.setBatchFileName(BatchFileName)
        self.delete_BatchFile()
        
        if self.verbose:
            print "BatchFileName", self.BatchFileName
            print "run_ffmpeg", self.run_ffmpeg
 
 
    def setBatchFileName(self,BatchFileName):
        if self.verbose:
            print "setBatchFileName()", BatchFileName
        self.BatchFileName = BatchFileName
        if self.BatchFileName is not None:
            self.run_ffmpeg = False
        else:
            self.run_ffmpeg = True
        if self.verbose:
            print "BatchFileName", self.BatchFileName
            print "run_ffmpeg", self.run_ffmpeg

    def getBatchFileName(self):
        return self.BatchFileName   
 
    def setVerbose(self,verbose):
        self.verbose=verbose
    
    def delete_BatchFile(self):
        if self.BatchFileName is not None:
            if os.path.exists(self.BatchFileName):
                os.remove(self.BatchFileName)
        '''
        BatchFileFolder = os.path.dirname(self.BatchFileName)
        if not os.path.exists(BatchFileFolder):
            os.makedirs(BatchFileFolder)
        ''' 
  
    def take_snapshot_ffmpeg(self, FullPathFileName, t_event_Multimedia, PngFileName = 'LDW.png', AviSuffix=''):
        ''' take a snapshot from a videofile and store as png file using ffmpeg '''    
    
    
        if self.verbose:
            print "take_snapshot_ffmpeg"
    
        # assumption videofile is avi
    
        #------------------------------------------- 
        # 1. AviFileName - get video file name
        (prefix, sep, suffix) = FullPathFileName.rpartition('.')
        AviFileName = prefix + AviSuffix + '.avi'
   
        if self.verbose:
            print "  FullPathFileName:  ", FullPathFileName
            print "  AviFileName:       ", AviFileName
            print "  PngFileName:       ", PngFileName
    
        #------------------------------------------- 
        # 2. remove old png file
        if os.path.exists(PngFileName):
            os.remove(PngFileName)

        
        PngFolder = os.path.dirname(PngFileName)
        print "PngFolder",PngFolder
        if PngFolder:
            if not os.path.exists(PngFolder):
                os.makedirs(PngFolder)
    

        #------------------------------------------- 
        # call ffmpeg 
        if self.verbose:
            print "  t_event_Multimedia:", t_event_Multimedia
    
        args = []
        
        # ffmpeg
        args.append('ffmpeg')
    
        # start
        args.append('-ss')
        args.append(secs2time(t_event_Multimedia).strftime("%H:%M:%S.%f"))
   
        # Video file
        args.append('-i')
        args.append(AviFileName)
    
        args.append('-vframes')
        args.append('1')
    
        args.append(PngFileName)
    
        print "take_snapshot_ffmpeg()"
        print args
        print "before"
        sys.stdout.flush()   
    
        if self.run_ffmpeg:
            subprocess.check_call(args)

        print "after"
        sys.stdout.flush()  
    
        if self.BatchFileName is not None:
            with open(self.BatchFileName,"a") as f:
                f.write(" ".join(args))
                f.write("\n")

        collected = gc.collect()        
        print "CSnapshotFromVideofile.take_snapshot_ffmpeg() Garbage collector: collected %d objects." % (collected)
                
#*********************************************************************************************
Local_BatchFileName = "postproc_pngs_from_avi.bat"
Local_BatchFileName = None

iSnapshotFromVideofile = CSnapshotFromVideofile(Local_BatchFileName,verbose=False)
    
#*********************************************************************************************
def take_snapshot_from_videofile(FullPathFileName, t_event_Multimedia, PngFileName = 'LDW.png', AviSuffix='', verbose=False):
    ''' take a snapshot from a videofile and store a png  '''  
    iSnapshotFromVideofile.setVerbose(verbose)
    iSnapshotFromVideofile.take_snapshot_ffmpeg(FullPathFileName, t_event_Multimedia, PngFileName = PngFileName, AviSuffix=AviSuffix)

def SetBatchFileName_for_take_snapshot_from_videofile(BatchFileName):
    iSnapshotFromVideofile.setBatchFileName(BatchFileName)

def GetBatchFileName_for_take_snapshot_from_videofile():
    return iSnapshotFromVideofile.getBatchFileName()
   
    
#*********************************************************************************************
'''

# for future use - if openCV is available

import cv2
#=================================================================================
def auslager():
    
       
    for k in xrange(1000):
        ret, frame = cap.read()
        cnt = int(cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))
        pos_msec = int(cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC))
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        #cv2.putText(frame,'%3d %f'%(cnt,cnt*fps/1000),(10,400), font, 4,(255,255,255),2,cv2.CV_AA)
        cv2.putText(frame,'%3d %f'%(cnt,pos_msec/1000.0),(10,400), font, 4,(255,255,255),2,cv2.CV_AA)
        cv2.putText(frame,'%f'%(pos_msec/1000.0),(10,200), font, 4,(255,255,255),2,cv2.CV_AA)

        print ret
        if ret:
            cv2.imwrite('LDW_%04d.png'%k,frame)

#=================================================================================
def take_snapshot_CV(FullPathFileName, t_event, PngFileName = 'LDW.png'):
        
    #AviFileName 
    (prefix, sep, suffix) = FullPathFileName.rpartition('.')
    AviFileName = prefix + '.avi'
   
    print FullPathFileName
    print AviFileName
     
    
    cap = cv2.VideoCapture(AviFileName)
         

    width = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
    interval = int(1000.0 / fps)  # interval between frame in ms.
    height = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
    fourcc = int(cap.get(cv2.cv.CV_CAP_PROP_FOURCC))
    frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
    POS_FRAMES = cap.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)

    #fourcc = 1145656920

    print "FRAME_WIDTH", width 
    print "FRAME_HEIGHT", height 
    print "FPS", fps, interval
    print "FRAME_COUNT", frame_count
    print "POS_FRAMES", POS_FRAMES
    print "PROP_FOURCC", fourcc

    
 
    #cap.set(cv2.cv.CV_CAP_PROP_POS_MSEC, t_event*1000.0)
    cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, int(fps*t_event))
    
    print "PROP_PROP_POS_MSEC", cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
    ret, frame = cap.read()
    
    print ret
    if ret:
        cv2.imwrite(PngFileName,frame)

    cap.release()
    
'''
 
