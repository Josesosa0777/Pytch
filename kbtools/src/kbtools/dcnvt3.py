'''
    dbc_list = ['dbc\J1939_DAS_Ford.dbc', 'dbc\Video_Fusion_Protocol_2013-11-04.dbc', 'dbc\A087MB_V3.3draft_MH1.dbc']
    suffix_list = ['_V_Box.BLF', '_private_CAN2_500k.BLF', '_private_J1939_250k.BLF', '_Puplic_J1939_250k.BLF']
    BaseFileName = '2014-02-04-19-25-29'
    InputFolderName = 'blf'
    OutputFolderName = 'output'
        
     
    dcnvt3 = kbtools.Cdcnvt3()
    dcnvt3.set_dbc_list(dbc_list)
    dcnvt3.set_input_files(BaseFileName, suffix_list, InputFolderName)
    dcnvt3.set_output_file('M', BaseFileName,'.mat', OutputFolderName, overwrite=True)
    dcnvt3.convert()
'''


import os
import sys
import subprocess
import numpy as np
import scipy.io as sio
import re
import datetime
import gc

# http://stackoverflow.com/questions/4983258/python-how-to-check-list-monotonicity
def strictly_increasing(L):
    try:
        return all(x<y for x, y in zip(L, L[1:]))
    except:
        return False    

# http://stackoverflow.com/questions/1714027/version-number-comparison
def Dcnvt3VersionNumberComparison(version1, version2):
    '''
    The return value is negative if x < y, zero if x == y and strictly positive if x > y.
    '''
    def normalize(v):
        v = Dcnvt3VersionNumberUpgrade(v)
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

def Dcnvt3VersionNumberUpgrade(inp):
    '''
      '3.122' -> '3.0.0.122'
      '3.2.1.134' -> '3.2.1.134'
    '''
    ret = inp
    x = inp.split(".")
    #print "upgrade:", len(x)
    if len(x) == 2:
        # old format
        ret = ".".join([x[0],"0","0",x[1]])

    return ret

class Cdcnvt3():

    #==========================================================================================    
    def __init__(self, DcnvtName="dcnvt3_64", clean_up=False, verbose=False):
        '''
            parameters
                DcnvtName : name of dcnvt3.exe "dcnvt3"|"dcnvt3_64"
                clean_up  : remove temporarily generated files
                verbose   : print additional debug information
        '''
        
        #verbose = True
    
        self.DcnvtName = DcnvtName
        self.InputFolderName = None
        self.BaseFileName = None
        self.InputFileName = None
        self.dbc_list = None
        self.dbc_folder = None
        self.OutputFileName = None
        self.FileFormat = None
        self.use_relative_time = False
        self.clean_up = clean_up     # remove temporarily generated files
        self.verbose = verbose
        
        if self.verbose:
            print "====================================="
            print "Cdcnvt3.__init__() - start"
        
        # check if dcnvt3 is on Windows Path and get dcnvt3 version 
        self.dcnvt3_version = self.get_dcnvt3_version(verbose=verbose)
        
        if self.dcnvt3_version is None:
            raise "dcnvt3 error"
        else:
            if self.verbose:
                #print "  %s V%3.3f"%(self.DcnvtName,self.dcnvt3_version)
                print "  %s V%s"%(self.DcnvtName,self.dcnvt3_version)
            
        if self.verbose:
            print "Cdcnvt3.__init__() - end"  
            sys.stdout.flush()            
    #========================================================================================== 
    def _loadmat(self, FileName):

        collected = gc.collect()        
        print "Cdcnvt3._loadmat() Garbage collector: collected %d objects." % (collected)
        
        # first check file size
        if os.path.exists(FileName):
            FileSize = os.path.getsize(FileName)
            print "File size ",FileSize
            FileSizeThreshold = 100*1024*1024
            if FileSize > FileSizeThreshold:
                print "File size is bigger than threshold ",FileSizeThreshold
                print "File too big too load"
                sys.stdout.flush()   
                Mat = None
                return Mat
         
        # load Matlab Binary into memory
        try:
            Mat = sio.loadmat(FileName) 
        except:
            print "CReadDcnvt3._loadmat() - error loading <%s>"%FileName
            sys.stdout.flush()    
            Mat = None
            
        return Mat

    #==========================================================================================    
    def get_dcnvt3_version(self,DcnvtName=None,verbose=None):
        '''
            get version number from dcnvt3.exe as float 
           
            parameters:
                DcnvtName : (optional) name of dcnvt3.exe  ("dcnvt3"|"dcnvt3_64")
                verbose   : print additional debug information
           
           return:
                dcnvt3_version :
                    None : dcnvt3.exe not available
                    string: version number obsolete float: version number
                     
           
        '''

        # return
        dcnvt3_version = None
       
        # parameters: local - global setting
        if DcnvtName is None:
            DcnvtName = self.DcnvtName
           
        if verbose is None:
            verbose = self.verbose
        
        #------------------------------------------- 
        args = []
        
        # dcnvt3 programm
        args.append(DcnvtName)
       
        # output format
        args.append('-v')
        
        if verbose:
            print args

        # 1. call dcnvt3 and request version information    
        try:
            output = subprocess.check_output(args)
        except:
            print "get_dcnvt3_version(): error calling dcnvt3 -> check if %s is on WINOWDS PATH"%DcnvtName
            dcnvt3_version = None
            return
        
        # 2. parse version information
        Knorr_Dcnvt_Tag = "Knorr-Dcnvt"
        try:
            if verbose:
                print "output", output
                print "output", output.split()
            found = False
            for k,element in enumerate(output.split()):
                if verbose:
                    print k,element
                if found:
                    if verbose:
                        print "version", element
                    #dcnvt3_version = float(element[1:6])          # quick and dirty
                    dcnvt3_version = element[1:]
                    if verbose:
                        print "dcnvt3_version:", dcnvt3_version
                    break
                if element.find(Knorr_Dcnvt_Tag)>=0:
                    found = True
        except:
            print "get_dcnvt3_version(): error parser dcnvt3 response"     

               
        return dcnvt3_version
        
        
    #==========================================================================================    
    def set_dbc_list(self, dbc_list, dbc_folder=None):
        self.dbc_list = dbc_list
        self.dbc_folder = dbc_folder
        
        if self.verbose:
            print "Cdcnvt3.set_dbc_list() -start"
            print "  self.dbc_list:",self.dbc_list
            print "  self.dbc_folder:",self.dbc_folder
            print "Cdcnvt3.set_dbc_list() -end"
            sys.stdout.flush()
        
    #==========================================================================================
    '''
    def f_ck_CANape(self, InputFolderName, BaseFileName, verbose = False):

        print "f_ck_CANape"
        
        # ------------------------------------------------------
        # offsets 1, -1
        #  examples
        #    blf file start one second ago -> offset = -1
        #    Ford_M1PT17__2014-06-07_19-11-23.MF4
        #    Ford_M1PT17__2014-06-07_19-11-22__J1939_Channel_1.BLF

        for offset in [1,-1,-2,2,-3,3,-4,4]:
            print "  offset: ", offset
            
            try:
                BaseName = self.f_ck_CANape2(BaseFileName,offset=offset, verbose=verbose)
                if isinstance(BaseName,basestring):
                    suffix_list = self._create_suffix_list(InputFolderName,BaseName)
                    suffix = suffix_list[0]
                    FileName = os.path.join(InputFolderName,BaseName+suffix)
                    print "FileName", FileName
                    if os.path.exists(FileName):
                        return BaseName        
            except:
                print " failed"
                pass

        # ------------------------------------------------------
        BaseName = self.f_ck_CANape1(BaseFileName,verbose)
        if isinstance(BaseName,basestring):
           return BaseName     
 
        return None   
    '''    
    #==========================================================================================
    def f_ck_CANape_new(self, InputFolderName, BaseFileName, verbose = False):

        if verbose:
            print "f_ck_CANape_new"
        
        file_list = []
        
        # ------------------------------------------------------
        # offsets 1, -1
        #  examples
        #    blf file start one second ago -> offset = -1
        #    Ford_M1PT17__2014-06-07_19-11-23.MF4
        #    Ford_M1PT17__2014-06-07_19-11-22__J1939_Channel_1.BLF

        for offset in [1,-1,-2,2,-3,3,-4,4,-5,5,-6,6,-7,7,-8,8,-9,9,-10,10,-11,11,-12,12,-13,13,-14,14,-15,15,-16,16,-17,+17,-18,+18]:   
            if verbose:
                print "  offset: ", offset
            
            try:
                BaseName = self.f_ck_CANape2(BaseFileName,offset=offset, verbose=verbose)
                if isinstance(BaseName,basestring):
                    tmp_file_list = self._find_associated_files(InputFolderName,BaseName)
                    file_list.extend(tmp_file_list)
            except:
                if verbose:
                    print " failed"
                pass

        # ------------------------------------------------------
        BaseName = self.f_ck_CANape1(BaseFileName,verbose)
        if isinstance(BaseName,basestring):
            tmp_file_list = self._find_associated_files(InputFolderName,BaseName)
            file_list.extend(tmp_file_list)
 
        return file_list
    
    #==========================================================================================
    def f_ck_CANape1(self, s, verbose = False):
        '''

        CANape12 feature
    
        mf4 and blf files have different basenames because they have different time stamps
    
        mf4 file and blf files are written in different processes and can have therefore different 
        timestamps.
    
        Ulrich Guecker
        2014-04-16

        ''' 
        regexp = re.compile(r'(?P<year>\d{2,4})[-](?P<month>\d{2})[-](?P<day>\d{2})(?P<trenner>[-_])(?P<hour>\d{2})[-](?P<minute>\d{2})[-](?P<second>\d{2})')
        result = regexp.search(s)
    
        if result:
            if verbose:
                print "year",    result.group('year')    
                print "month",   result.group('month')    
                print "day",     result.group('day')  
    
                print "trenner", result.group('trenner')   
    
                print "hour",   result.group('hour')    
                print "minute", result.group('minute')    
                print "second", result.group('second')    
    
    
            t = datetime.datetime(int(result.group('year')), int(result.group('month')), int(result.group('day')), int(result.group('hour')), int(result.group('minute')), int(result.group('second'))) 
            t = t + datetime.timedelta(0,1)
            return t.strftime(r"%%Y-%%m-%%d%s%%H-%%M-%%S"%result.group('trenner'))

        return None
        
    #==========================================================================================    
    def f_ck_CANape2(self, BaseFileName, offset=1, verbose = False):

        if verbose:
            print "f_ck_CANape2: BaseFileName=", BaseFileName
            
        Trenner = '__'
        liste = BaseFileName.split(Trenner)
    
        liste2 = []
    
        tp_detection_successful = False
        for s in liste:
            if verbose:
                print "s=", s
        
            try:
                fmt = "%Y-%m-%d_%H-%M-%S"
                tp = datetime.datetime.strptime(s,fmt)
                # print "tp=", tp
                if verbose:
                    print "current tp:", tp.strftime(fmt)
                tp2 = tp + datetime.timedelta(0,offset)
                if verbose:
                    print "new tp:", tp2.strftime(fmt)
                liste2.append(tp2.strftime(fmt))
                tp_detection_successful = True
            except:
                liste2.append(s)
                if verbose:
                    print "error"
        
        if tp_detection_successful:        
            return Trenner.join(liste2)   
        else:
            return None

    #==========================================================================================  
    '''    
    def set_input_files_old(self, BaseFileName, suffix_list = None, InputFolderName = None):
        self.BaseFileName = BaseFileName
        self.InputFolderName = InputFolderName
        
        if self.verbose:
            print "Cdcnvt3.set_input_files()"

        
        # ------------------------------------
        if suffix_list is None or not suffix_list:
            print "BaseFileName", BaseFileName
            print "InputFolderName", InputFolderName
            suffix_list = self._create_suffix_list(InputFolderName,BaseFileName)
            NewBaseFileName = BaseFileName
            print "suffix_list", suffix_list
            if not suffix_list:
               BaseFileName2 = self.f_ck_CANape(InputFolderName,BaseFileName)
               print "BaseFileName2", BaseFileName2
               suffix_list = self._create_suffix_list(InputFolderName,BaseFileName2)
               print "suffix_list", suffix_list
               NewBaseFileName = BaseFileName2
               
        # ------------------------------------
        # add input files from suffic_list       
        InputFileName = ''
        for suffix in suffix_list:
            if '' != InputFileName:
                InputFileName +=';'
            if InputFolderName is not None:
               InputFileName += os.path.join(InputFolderName,NewBaseFileName+suffix)
            else:
               InputFileName += NewBaseFileName+suffix
        self.InputFileName = InputFileName
    '''
    #==========================================================================================    
    def _remove_duplicate_from_list(self,sequence):    
        '''
        http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
        '''
        
        unique = []
        [unique.append(item) for item in sequence if item not in unique]
        
        return unique
        
    #==========================================================================================    
    def set_input_files(self, BaseFileName, suffix_list = None, InputFolderName = None):
        '''
            specifiy input measurement files for dcnvt3.exe  (mf4 + blf files)
            
            parameters:
                BaseFileName :  common part of the mf4 and blf files
                suffix_list  :  only use blf files with this suffix
                InputFolderName : folder where measurement files are stored
        
        '''
        self.BaseFileName = BaseFileName
        self.InputFolderName = InputFolderName
        
        if self.verbose:
            print "Cdcnvt3.set_input_files() - start"
            print "  BaseFileName   :", BaseFileName
            print "  suffix_list    :", suffix_list
            print "  InputFolderName:", InputFolderName
        
        InputFileNameList = []
                
        # ------------------------------------
        if self.verbose:
            print "  step1: find associated file with same BaseFileName", BaseFileName
        file_list = self._find_associated_files(InputFolderName,BaseFileName)
        InputFileNameList.extend(file_list)
        if self.verbose:
            print "  InputFileNameList:", InputFileNameList
            
        if self.verbose:
            print "  step2: find associated file with modified f*ck_CANape"
        file_list = self.f_ck_CANape_new(InputFolderName,BaseFileName,verbose=True)
        InputFileNameList.extend(file_list)
        if self.verbose:
            print "  InputFileNameList:", InputFileNameList
           
        # -------------------------------------------------------------        
        if self.verbose:
            print "  step3: remove duplicates in InputFileNameList"
        InputFileNameList = self._remove_duplicate_from_list(InputFileNameList)
        if self.verbose:
            print "  InputFileNameList:", InputFileNameList

        # -------------------------------------------------------------        
        if suffix_list:
            if self.verbose:
                print "  step4: only use files which have suffix included in suffix list"
            tmp_list = []
            for suffix in suffix_list:
                for InputFileName in InputFileNameList:
                    if InputFileName.find(suffix)>=0:
                        tmp_list.append(InputFileName)
                        
            InputFileNameList = tmp_list    
            if self.verbose:
                print "  InputFileNameList:", InputFileNameList
        
        # -------------------------------------------------------------        
        if self.verbose:
            print "  step5: join file names for dcnvt3.exe"
        InputFileName = ';'.join(InputFileNameList)
        if self.verbose:
            print "  InputFileName:", InputFileName
             
        # -------------------------------------------------------------        
        self.InputFileName = InputFileName

        if self.verbose:
            print "Cdcnvt3.set_input_files() - end "
            sys.stdout.flush()

    #==========================================================================================    
    def set_output_file(self, FileFormat = 'M', BaseFileName=None, Ext='.mat', OutputFolderName = None, overwrite=True):
        if self.verbose:
            print "Cdcnvt3.set_output_file() - start"
    
        self.FileFormat = FileFormat
        if OutputFolderName is not None:
            self.OutputFileName = os.path.join(OutputFolderName, BaseFileName+Ext)
            if not os.path.exists(OutputFolderName):
                if self.verbose:
                    print "makedirs: ", OutputFolderName
                os.makedirs(OutputFolderName)
        else:
            self.OutputFileName = BaseFileName
              
        if overwrite:
            if os.path.exists(self.OutputFileName):
                if self.verbose:
                    print "overwrite: ", self.OutputFileName
                os.remove(self.OutputFileName)
                
        if self.verbose:
            print "Cdcnvt3.set_output_file() - end "
            sys.stdout.flush()
        
    #==========================================================================================    
    def _create_suffix_list(self,PathName,BaseName):
        '''
           search for all blf files starting with 'BaseName' in given folder 'PathName'
           create a list with part of the file name that has to be added to the 'BaseName' (suffix)
           
           
        '''
    
        DirList = os.listdir(PathName)
        DirList.sort()
    
        suffix_list = []
    
        for File in DirList:
            if File.startswith(BaseName) and File.lower().endswith(".blf"):
                suffix_list.append(File[(len(BaseName)):])
            
        return suffix_list
        
    #==========================================================================================    
    def _find_associated_files(self,PathName,BaseName,ext=".blf"):
        '''
           search for all blf files starting with 'BaseName' in given folder 'PathName'
           create a list with part of the file name that has to be added to the 'BaseName' (suffix)
           
           
        '''
    
        DirList = os.listdir(PathName)
        DirList.sort()
    
        file_list = []
    
        for File in DirList:
            if File.startswith(BaseName) and File.lower().endswith(ext):
                file_list.append(os.path.join(PathName, File))
            
        return file_list
             
    #==========================================================================================    
    def _change_time_axis_MatlabBinary(self, FileName,FileNameModified):    
    
        if self.verbose:
            print "_change_time_axis_MatlabBinary"
        
        # read 
        Mat = self._loadmat(FileName)
       
        if Mat is None:
            return 
   
        list1 =  str(Mat['zzzzz_Vars_IdxString'][0]).split(';')
        
        sig2time = {}    
        for k,line in enumerate(Mat['zzzzz_IdxVariable_IdxTimeaxis']):
            SignalIndex = line[0] 
            TimeIndex = line[1]
            MatlabName = list1[k]
            if  SignalIndex == TimeIndex:
                pass
                # we have a time axis
            else:
                # we have a signal
                if MatlabName not in sig2time:
                    sig2time[MatlabName] = list1[TimeIndex]
               
        if self.verbose:
            print sig2time  
    
        # output
        signal_list = {}
    
        if ('Multimedia_1' in sig2time) and ('actual_vehicle_speed_MDF' in sig2time):
            N = 2
            zzzzz_Vars_IdxString = []
            zzzzz_IdxVariable_IdxTimeaxis = np.zeros((N*2, 3),dtype=np.int)

            #---------------------------------
            SigName = 'Multimedia_1'
            DevName = 'Multimedia'
            signal_list['t_'+DevName] = Mat[sig2time[SigName]]
            zzzzz_IdxVariable_IdxTimeaxis[0][0] = 0
            zzzzz_IdxVariable_IdxTimeaxis[0][1] = 0
            zzzzz_Vars_IdxString.append('t_'+DevName) 

            signal_list[SigName] = Mat[SigName]
            zzzzz_IdxVariable_IdxTimeaxis[1][0] = 1
            zzzzz_IdxVariable_IdxTimeaxis[1][1] = 0
            zzzzz_Vars_IdxString.append(SigName)

            #---------------------------------
            SigName = 'actual_vehicle_speed_MDF'
            DevName = 'MDF'
            signal_list['t_'+DevName] = Mat[sig2time[SigName]]
            zzzzz_IdxVariable_IdxTimeaxis[2][0] = 2
            zzzzz_IdxVariable_IdxTimeaxis[2][1] = 2
            zzzzz_Vars_IdxString.append('t_'+DevName) 

            signal_list[SigName] = Mat[SigName]
            zzzzz_IdxVariable_IdxTimeaxis[3][0] = 3
            zzzzz_IdxVariable_IdxTimeaxis[3][1] = 2
            zzzzz_Vars_IdxString.append(SigName)

            zzzzz_Vars_IdxString = ';'.join(zzzzz_Vars_IdxString)
    
            # 'zzzzz_Vars_IdxString'
            # 'zzzzz_IdxVariable_IdxTimeaxis'
            if self.verbose:
                print zzzzz_Vars_IdxString
                print zzzzz_IdxVariable_IdxTimeaxis
    
            signal_list['zzzzz_Vars_IdxString'] =  zzzzz_Vars_IdxString
            signal_list['zzzzz_IdxVariable_IdxTimeaxis'] = zzzzz_IdxVariable_IdxTimeaxis
            signal_list['zzzzz_Vars_Parts'] = zzzzz_Vars_IdxString
    
            if self.verbose:
                print "Time_actual_vehicle_speed_MF4 [s]:", signal_list['t_MDF'][0],"...",signal_list["t_MDF"][-1]
                print "Time_Multimedia [s]              :", signal_list["t_Multimedia"][0],"...",signal_list["t_Multimedia"][-1]

        sio.savemat(FileNameModified, signal_list, oned_as='row')             
        
    #==========================================================================================
    '''
    def _getMultimediaSignal_from_MF4_old(self, DcnvtName="dcnvt3_64",MatlabOutputFileNameModified = r'matlab_Multimedia_mod2.mat'):
    
        if self.verbose:
            print "_getMultimediaSignal_from_MF4()"

        MatlabOutputFileName = r'matlab_Multimedia.mat'
        
        SelectTxtFileName = "select.txt" 
        RenameTxtFileName = "rename.txt" 
        ReportMultimediaTxtFileName = "ReportMultimedia.txt"
        
        #------------------------------------------- 
        # SelectTxt
        f = open(SelectTxtFileName,"w")
        f.write("Multimedia_1\n")
        f.write("actual_vehicle_speed\n")
        f.close()
        
        #------------------------------------------- 
        # RenameTxt
        f = open(RenameTxtFileName,"w")
        f.write("actual_vehicle_speed actual_vehicle_speed_MDF\n")
        f.close()

         
        #------------------------------------------- 
        # remove MatlabOutputFileName and MatlabOutputFileNameModified
        if os.path.exists(MatlabOutputFileName):
            os.remove(MatlabOutputFileName)
        if os.path.exists(MatlabOutputFileNameModified):
            os.remove(MatlabOutputFileNameModified)
        
        #------------------------------------------- 
        args = []
        
        # dcnvt3 programm
        args.append(DcnvtName)
       
        # starting point
        if self.use_relative_time:
            args.append('-s')
            args.append('0.0')

        # output format
        args.append('-f')
        args.append('MSecondStrArray')
 
        # reporting level and file
        args.append('-r1') 
        args.append('-R')
        args.append('%s'%ReportMultimediaTxtFileName)
                  
        # SelectTxt
        args.append('-W')
        args.append('%s'%SelectTxtFileName)

        # RenameTxtFileName
        args.append('-t')
        args.append('%s'%RenameTxtFileName)
        
        # output file
        args.append('-o')
        args.append('%s'%MatlabOutputFileName)
        
        # input file
        # check if for extensions mf4 or mdf
        Ext = '.mf4'
        if os.path.exists(os.path.join(self.InputFolderName, self.BaseFileName+Ext)):
            args.append('%s'%os.path.join(self.InputFolderName, self.BaseFileName+Ext))
        
        Ext = '.mdf'
        if os.path.exists(os.path.join(self.InputFolderName, self.BaseFileName+Ext)):
            args.append('%s'%os.path.join(self.InputFolderName, self.BaseFileName+Ext))
        
        if self.verbose:
            print args
        try:
            p = subprocess.check_call(args)
        except:
            print "dcnvt3 error - but continue"

        if os.path.exists(MatlabOutputFileName):
            self._change_time_axis_MatlabBinary(MatlabOutputFileName,MatlabOutputFileNameModified)
        else:
            print "error %s doesn't exists - but continue" %MatlabOutputFileName
        
        
        if self.clean_up:
            if os.path.exists(SelectTxtFileName):
                os.remove(SelectTxtFileName)
            if os.path.exists(RenameTxtFileName):
                os.remove(RenameTxtFileName)
            if os.path.exists(ReportMultimediaTxtFileName):
                os.remove(ReportMultimediaTxtFileName)
            if os.path.exists(MatlabOutputFileName):
                os.remove(MatlabOutputFileName)
            
    '''       
    #==========================================================================================
    def _find_available_MF4(self):
        '''
            find an available MF4/MDF file with the given BaseFileName)
        '''
        
        MF4_FileName = None
        
        # check if for extensions mf4 or mdf
        for Ext in ['.mf4', '.mdf', '.MF4', '.MDF' ]:   # Archive Server: case sensitive path names
            tmp_FileName = os.path.join(self.InputFolderName, self.BaseFileName+Ext)
            print "_find_available_MF4(): tmp_FileName", tmp_FileName
            if os.path.exists(tmp_FileName):
                MF4_FileName = os.path.join(tmp_FileName)
        
        return MF4_FileName
        
    #==========================================================================================    
    def _getMultimediaSignal_from_MF4(self, MF4_FileName,MatlabOutputFileNameModified = r'matlab_Multimedia_mod.mat'):
        '''
            extract signals  "Multimedia_1" and "actual_vehicle_speed" 
            from given mf4/mdf-measurement file (MF4_FileName)
            to a Matlab Binary File (MatlabOutputFileNameModified)
            
        '''
    
        #success = False
    
        if self.verbose:
            print "Cdcnvt3._getMultimediaSignal_from_MF4() - start "
            print "  MF4_FileName:", MF4_FileName
            print "  MatlabOutputFileNameModified:", MatlabOutputFileNameModified
            sys.stdout.flush()


        # -------------------------------------------------------------------------  
        # step1: create Matlab Binary file given by MatlabOutputFileName from input file given by MF4_FileName
        
        MatlabOutputFileName = r'matlab_Multimedia.mat'
        
        SelectTxtFileName = "select.txt" 
        RenameTxtFileName = "rename.txt" 
        ReportMultimediaTxtFileName = "ReportMultimedia.txt"
        
        #------------------------------------------- 
        # step1.1: create Select.Txt - signals which shall be extracted
        f = open(SelectTxtFileName,"w")
        f.write("Multimedia\n")
        f.write("Multimedia_1\n")
        f.write("Multimedia_2\n")
        f.write("actual_vehicle_speed\n")

        '''
        von Burcu        
           RightFromCPosLateral -> Lateral Distance to Right Lane
           LeftFromBPosLateral  -> Lateral Distance to Left Lane
           RightLineVelLateral  -> Lateral Drift-Rate depending to the Right Lane
           LeftLineVelLateral   -> Lateral Drift-Rate depending to the Left Lane
        '''
        if 1:        
            
            # LeftLineLateral
            f.write("LeftLineNumber\n")
            f.write("LeftLinePosLateral\n")
            f.write("LeftLineVelLateral\n")
            f.write("LeftLineAccelLateral\n")

            # RightLineLateral
            f.write("RightLineNumber\n")
            f.write("RightLinePosLateral\n")
            f.write("RightLineVelLateral\n")
            f.write("RightLineAccelLateral\n")
        
            # TrajectoryOfA
            f.write("CurvatureOfA\n")
            f.write("LeftLineHeadingOfA\n")
            f.write("RightLineHeadingOfA\n")
        
            # LinesFromB
            f.write("LeftFromBPosLateral\n")
            f.write("RightOfBNumber\n")
            f.write("LeftOfBNumber\n")
            f.write("CurvatureOfB\n")

            # LinesFromC
            f.write("RightFromCPosLateral\n")
            f.write("RightOfCNumber\n")
            f.write("LeftOfCNumber\n")
            f.write("CurvatureOfC\n")
        
        f.close()
        
        #------------------------------------------- 
        # step1.2: create  Rename.Txt - extracted signals which shall be renamed  
        f = open(RenameTxtFileName,"w")
        f.write("actual_vehicle_speed actual_vehicle_speed_MDF\n")
        #f.write("Multimedia Multimedia_1\n")
        #f.write("Multimedia_2 Multimedia_1\n")     # todo workaround
        f.close()

         
        #------------------------------------------- 
        # step1.3: clean up before - remove MatlabOutputFileName and MatlabOutputFileNameModified
        if os.path.exists(MatlabOutputFileName):
            os.remove(MatlabOutputFileName)
        if os.path.exists(MatlabOutputFileNameModified):
            os.remove(MatlabOutputFileNameModified)
        
        #-------------------------------------------
        # step1.4: invoke dcnvt3.exe
        args = []
        
        # dcnvt3 programm
        args.append(self.DcnvtName)
       
        # only for downward compatibility
        #if self.dcnvt3_version == 3.121:
        if Dcnvt3VersionNumberComparison(self.dcnvt3_version,"3.121") == 0:
            # new: starting point
            args.append('-MeasStart_sec')
            args.append('0.0')

        # new: MDF4 Alternate Time Axis Names
        args.append('-i')
        args.append('mdf4_atan')
         
        # output format
        args.append('-f')
        args.append('DCommentASCII')     # only for MF4 comments
        args.append('MSecondStrArray')
        #if self.dcnvt3_version >= 3.122:   # new options
        if Dcnvt3VersionNumberComparison(self.dcnvt3_version,"3.122") >= 0:
            
            args.append('rel')
            args.append('starttimes')
        args.append('M')    
              
        # reporting level and file
        args.append('-r1') 
        args.append('-R')
        args.append('%s'%ReportMultimediaTxtFileName)
                  
        # SelectTxt
        args.append('-W')
        args.append('%s'%SelectTxtFileName)

        # RenameTxtFileName
        args.append('-t')
        args.append('%s'%RenameTxtFileName)
        
        # output file
        args.append('-o')
        args.append('%s'%MatlabOutputFileName)
        
        # input file
        args.append('%s'%MF4_FileName)
        
        # call dcnvt3
        if self.verbose:
            print "  args:", " ".join(args)
            sys.stdout.flush()
        try:
            subprocess.check_call(args)
        except:
            print "_getMultimediaSignal_from_MF4() error in calling dcnvt3 - but continue"
        
        if self.verbose:
            print "  "
            sys.stdout.flush()        
        
        # -------------------------------------------------------------------------  
        # step2: check generated Matlab Binary files   
        success = self._check_Matlab_Multimedia(MatlabOutputFileName)
        

        
        
        # -------------------------------------------------------------------------  
        # step3: correct time axis name  - obsolete 
        #    copy MatlabOutputFileName to MatlabOutputFileNameModified
        if 0:    
            if os.path.exists(MatlabOutputFileName):
                self._change_time_axis_MatlabBinary(MatlabOutputFileName,MatlabOutputFileNameModified)
            else:
                print "error %s doesn't exists - but continue" %MatlabOutputFileName
        else:
            if os.path.exists(MatlabOutputFileName):
                os.rename(MatlabOutputFileName,MatlabOutputFileNameModified)
            else:
                print "error %s doesn't exists - but continue" %MatlabOutputFileName
      
        # -------------------------------------------------------------------------  
        # Meas Comment
        MeasCommentFileName_dcnvt = r"matlab_Multimedia.mat_dcomment.txt"
        #MeasCommentFileName_new = r"MeasComment.txt"
        print "========================================="
        print "MeasCommentFileName - Start:"
        if os.path.exists(MeasCommentFileName_dcnvt):
            fobj = open(MeasCommentFileName_dcnvt)
            for line in fobj:
                print line.rstrip()
            fobj.close()
            try:
                os.rename(MeasCommentFileName_dcnvt, "MeasComment.txt")
            except OSError:
                pass
                
        else:
            print "not available"        
        print "MeasCommentFileName - End"
        print "========================================="
        sys.stdout.flush()        
        
        # -------------------------------------------------------------------------    
        # step4:  clean up afterwards
        if self.clean_up:
            if os.path.exists(SelectTxtFileName):
                os.remove(SelectTxtFileName)
            if os.path.exists(RenameTxtFileName):
                os.remove(RenameTxtFileName)
            if os.path.exists(ReportMultimediaTxtFileName):
                os.remove(ReportMultimediaTxtFileName)
            if os.path.exists(MatlabOutputFileName):
                os.remove(MatlabOutputFileName)
         
        if self.verbose:
            print "Cdcnvt3._getMultimediaSignal_from_MF4() - end"
            sys.stdout.flush()
 
        return success         
           
    #==========================================================================================    
    def _check_Matlab(self,FileName):
    
        print "================================"
        print "_check_Matlab(%s) - start"%FileName
        
        if not os.path.exists(FileName):
          
            print " <%s> doesn't exists"%  FileName
            print "_check_Matlab() - end" 
            sys.stdout.flush()  
            return False
            
        # ----------------------------------------------------
        # read 
        signal_list = self._loadmat(FileName)
        
        if signal_list is None:
            print "Matlab Binary was not loaded"
            print "_check_Matlab() - end"
            sys.stdout.flush()  
            return False

        '''
        sig2time = self._create_sig2time(signal_list)
        print "included signals"
        for k,signal in enumerate(sig2time.keys()):
            print k, signal, np.squeeze(signal_list[sig2time[signal]])[0] ,np.squeeze(signal_list[sig2time[signal]])[-1]
        '''
        sig2time = self._create_sig2time(signal_list)
        print "  included signals:"
        for k,signal in enumerate(sig2time.keys()):
            t = np.squeeze(signal_list[sig2time[signal]])
            if not strictly_increasing(t):
                print "    %d. %s length=%d"%(k,signal,t.size),
                if t.size > 1:
                    print "t=[%f..%f] monotonic:%s"%(t[0],t[-1],strictly_increasing(t)) 
                else:
                    print "t=",t            

        
        
        self._check_zzzzz(signal_list)
             
        print "_check_Matlab() - end"			 
        sys.stdout.flush()   			  
        return True
        
    #==========================================================================================    
    def _check_Matlab_Multimedia(self,FileName):
        '''
           check if given Matlab Binary includes signal "Multimedia_1"         
        '''
    
        print "================================"
        print "_check_Matlab_Multimedia(%s): "%FileName
        if not os.path.exists(FileName):
            print "error: <%s> doesn't exist"%FileName
            print "_check_Matlab_Multimedia() - end"	
            sys.stdout.flush()
            return False
        
        signal_list = self._loadmat(FileName)

        if signal_list is None:
            print "Matlab Binary was not loaded"	
            print "_check_Matlab_Multimedia() - end"			 
            sys.stdout.flush() 
            return False
        
        sig2time = self._create_sig2time(signal_list)
        print "  included signals:"
        for k,signal in enumerate(sig2time.keys()):
            t = np.squeeze(signal_list[sig2time[signal]])
            print "    %d. %s length=%d"%(k,signal,t.size),
            if t.size > 1:
                print "t=[%f..%f] monotonic:%s"%(t[0],t[-1],strictly_increasing(t)) 
            else:
                print "t=",t            
        
        self._check_zzzzz(signal_list)
  
        print "_check_Matlab_Multimedia() - end"	
        sys.stdout.flush()
        
        if "Multimedia_1" in sig2time.keys():
            return True
        return False
        
    #==========================================================================================    
    def _check_zzzzz(self,signal_list):    
        
        # ------------------------------------------------------------------    
        # 'zzzzz_StartofMeasurement' - obsolete - only for dcnvt3 V3.121; removed in V3.122
        if 'zzzzz_StartofMeasurement' in signal_list:
            print '  zzzzz_StartofMeasurement', float(signal_list['zzzzz_StartofMeasurement'][0])
        
        # ------------------------------------------------------------------    
        # 'zzzzz_AbsStartTimeOfMeasurement'  - dcnvt3 V3.122 option "-f rel" 
        # absolute time stamp of measurement start
        tp = None
        if 'zzzzz_AbsStartTimeOfMeasurement' in signal_list:
            print '  zzzzz_AbsStartTimeOfMeasurement', signal_list['zzzzz_AbsStartTimeOfMeasurement'][0],
            fmt = "%Y-%m-%d %H:%M:%S,%f"
            tp = datetime.datetime.strptime(signal_list['zzzzz_AbsStartTimeOfMeasurement'][0],fmt)
            # print "tp=", tp
            print " -> current tp:", tp.strftime(fmt)
            
        # ------------------------------------------------------------------    
        # 'zzzzz_TimesMeasurement' - dcnvt3 V3.122 option "-f StartTimes" 
        # time stamp of first and last sample
        if 'zzzzz_TimesMeasurement' in signal_list:
            start_stop = [float(s) for s in signal_list['zzzzz_TimesMeasurement'][0].split(';')]
            print '  zzzzz_TimesMeasurement', start_stop, start_stop[0], start_stop[1]
            if tp is not None:
                tp2 = tp + datetime.timedelta(0,start_stop[0])
                print "  -> absolute start of first sample:", tp2.strftime(fmt)
                tp3 = tp + datetime.timedelta(0,start_stop[1])
                print "  -> absolute start of last sample :", tp3.strftime(fmt)
      
    #==========================================================================================    
    def _create_sig2time(self,signal_list):    
        '''
            create mapping from signal to time axis 
           
            input: Matab Binary signals from dcnvt3 conversion as list
            output: dictionary
           
            special dcnvt3 information:
              signal_list['zzzzz_Vars_IdxString']
              signal_list['zzzzz_IdxVariable_IdxTimeaxis']
        '''
        
        list1 =  str(signal_list['zzzzz_Vars_IdxString'][0]).split(';')
        sig2time = {}    
        for k,line in enumerate(signal_list['zzzzz_IdxVariable_IdxTimeaxis']):
            SignalIndex = line[0] 
            TimeIndex = line[1]
            MatlabName = list1[k]
            if  SignalIndex == TimeIndex:
                pass
                # we have a time axis
            else:
                # we have a signal
                if MatlabName not in sig2time:
                    sig2time[MatlabName] = list1[TimeIndex]
                    
        return sig2time
                    
    #==========================================================================================    
    def _synchronize(self,FileName,FileNameModified):    
        '''

        '''        
        if self.verbose:
            print "-------------------------------"
            print "_synchronize()"
            print "  in:  FileName", FileName 
            print "  out: FileNameModified", FileNameModified
    
        # ----------------------------------------------------
        # read Matlab Binary
        signal_list = self._loadmat(FileName)

        if signal_list is None:
            return
    
        # mapping signal to time axis 
        sig2time = self._create_sig2time(signal_list)   
        
        # ----------------------------------------------------
       
        if ('Multimedia_1' in sig2time) and ('actual_vehicle_speed_MDF' in sig2time) and ('actual_vehicle_speed' in sig2time):
            t_MDF_Name = sig2time['Multimedia_1']  
            t_actual_vehicle_speed_MF4_Name = sig2time['actual_vehicle_speed_MDF']  
            t_actual_vehicle_speed_CAN_Name = sig2time['actual_vehicle_speed']  
  
            if self.verbose:
                print "t_MDF_Name",t_MDF_Name 
                print "t_actual_vehicle_speed_MF4_Name",t_actual_vehicle_speed_MF4_Name
                print "t_actual_vehicle_speed_CAN_Name",t_actual_vehicle_speed_CAN_Name
    
                print "Time_actual_vehicle_speed_MF4 [s]:", signal_list[t_actual_vehicle_speed_MF4_Name][0],"...",signal_list[t_actual_vehicle_speed_MF4_Name][-1]
                print "Time_actual_vehicle_speed_CAN [s]:", signal_list[t_actual_vehicle_speed_CAN_Name][0],"...",signal_list[t_actual_vehicle_speed_CAN_Name][-1]
                print "Time_Multimedia [s]              :", signal_list[t_MDF_Name][0],"...",signal_list[t_MDF_Name][-1]
    
            t_offset = signal_list[t_actual_vehicle_speed_CAN_Name][0] - signal_list[t_actual_vehicle_speed_MF4_Name][0]
            
            if self.verbose:
                print "t_offset", t_offset

            # correct offset
            signal_list[t_actual_vehicle_speed_MF4_Name] += t_offset
            signal_list[t_MDF_Name] += t_offset

            if self.verbose:
                print "Time_actual_vehicle_speed_MF4 [s]:", signal_list[t_actual_vehicle_speed_MF4_Name][0],"...",signal_list[t_actual_vehicle_speed_MF4_Name][-1]
                print "Time_actual_vehicle_speed_CAN [s]:", signal_list[t_actual_vehicle_speed_CAN_Name][0],"...",signal_list[t_actual_vehicle_speed_CAN_Name][-1]
                print "Time_Multimedia [s]              :", signal_list[t_MDF_Name][0],"...",signal_list[t_MDF_Name][-1]
        else:
            print "warning dcnvt3._synchronize()"
            if 'Multimedia_1' not in sig2time: print 'signal Multimedia_1 missing'
            if 'actual_vehicle_speed_MDF' not in sig2time: print 'signal actual_vehicle_speed_MDF missing'
            if 'actual_vehicle_speed' in sig2time: print 'signal actual_vehicle_speed missing'
                 
            
        # ----------------------------------------------------
        # save modified all signals including modified ones
        sio.savemat(FileNameModified, signal_list, oned_as='row')             


    #==========================================================================================    
    def _check_CAN_statistics(self,FileName):  
        '''
          
            under construction
           
        '''
    
        print "_check_CAN_statistics()",FileName
        
        #dcnvt3  -i c_stat -o Statistik_CAN1_2.txt GV_TGX__2014-10-13_13-52-30__J1939_public_Channel_1.BLF

        FileNameStatistics = "Statistik.txt"
        #------------------------------------------- 
        # remove FileNameStatistics 
        if os.path.exists(FileNameStatistics):
            os.remove(FileNameStatistics)
        
        
        #------------------------------------------- 
        args = []
        
        # dcnvt3 programm
        args.append(self.DcnvtName)
       
        # create statistics
        args.append('-i')
        args.append('c_stat')
       
        # output file
        args.append('-o')
        args.append('%s'%FileNameStatistics)
        
        # input file
        args.append('%s'%FileName)
        
        if self.verbose:
            print args
        try:
            subprocess.check_call(args)
        except:
            print "dcnvt3 error - but continue"

        
    #==========================================================================================    
    def convert(self):      
        '''
           convert measurement files
        
        '''
        
        if self.verbose:
            print "Cdcnvt3.convert() - start "
            sys.stdout.flush()

        # -------------------------------------------------
        # CAN statistic  - under constructions
        if 0:
            for FileName in self.InputFileName.split(';'):
                #print FileName
                self._check_CAN_statistics(FileName)
        
         
        
        # ------------------------------------------------
        # step1: get Multimedia signal from mf4 file       
        if self.verbose:
            print "  step1: get Multimedia signal from mf4 file "
            sys.stdout.flush()
       
        MatlabOutputFileNameModified = r'matlab_Multimedia_mod.mat'
        #MatlabOutputFileNameModified = None
        
        if MatlabOutputFileNameModified is not None:
        
            MF4_FileName = self._find_available_MF4()
            if MF4_FileName is not None:
                success = self._getMultimediaSignal_from_MF4(MF4_FileName, MatlabOutputFileNameModified=MatlabOutputFileNameModified)
        
                print "convert - step1: get Multimedia signal from mf4 file: success=", success
            else:
                print "  -> no MF4_FileName found"
            sys.stdout.flush()
        # ------------------------------------------------        
        # step2: 
        if self.verbose:
            print "  step2: convert blf files "
  
        ReportAllTxtFileName = "ReportAll.txt"
        DcnvtErrFileName = "dcnvt.err"
        
        # ------------------------------------------------        
        args = []
        
        # dcnvt3 programm
        args.append(self.DcnvtName)
        
        # starting point
        '''
        if self.use_relative_time:
            args.append('-s')
            args.append('0.0')
        '''
        # only for downward compatibility
        #if self.dcnvt3_version == 3.121:
        if Dcnvt3VersionNumberComparison(self.dcnvt3_version,"3.121") == 0:
            # new: starting point
            args.append('-MeasStart_sec')
            args.append('0.0')
        
        # reporting level
        args.append('-r2')    # very important otherwise output is not written -> JNold
        args.append('-R')
        args.append('%s'%ReportAllTxtFileName)
  
        # output format
        args.append('-f')
        args.append('MSecondStrArray')
        #if self.dcnvt3_version >= 3.122:   # new options
        if Dcnvt3VersionNumberComparison(self.dcnvt3_version,"3.122") >= 0:
            args.append('rel')
            args.append('starttimes')

        
        # output format
        #args.append("-f%s"% self.FileFormat)
        
        # dbc  dbc_file CAN_Channel
        for dbc in self.dbc_list:
            if self.verbose:
                print "    dbc: ", dbc
            if isinstance(dbc,dict):
                if self.dbc_folder is not None:
                    dbc_FileName = os.path.join(self.dbc_folder,dbc['dbc_file'])
                else:
                    dbc_FileName = dbc['dbc_file']
                args.append('-d')
                if 'CAN_Channel' in dbc and dbc['CAN_Channel'] is not None:
                    args.append('%d'%dbc['CAN_Channel'])
                if 'J1939_Option' in dbc and dbc['J1939_Option']:
                    args.append('j')
                args.append('%s'%dbc_FileName)
            
            else:
                if self.dbc_folder is not None:
                    dbc_FileName = os.path.join(self.dbc_folder,dbc)
                else:
                    dbc_FileName = dbc
                args.append('-d')
                args.append('%s'%dbc_FileName)
 
        
        # output file        
        args.append('-o')
        args.append('%s'% self.OutputFileName)
            
        # InputFiles
        if MatlabOutputFileNameModified is not None:
            args.append('%s;%s'%(self.InputFileName,MatlabOutputFileNameModified))
        else:
            args.append('%s'%(self.InputFileName,))
      
        if self.verbose:
            print "    dcnvt3:convert()"
            print "    args", " ".join(args)
            sys.stdout.flush()
        try:
            subprocess.check_call(args)
        except:
            print "convert() error calling dcnvt3 - but continue"

        if self.verbose:
            print " "
        
        self._check_Matlab(MatlabOutputFileNameModified)
        self._check_Matlab(self.OutputFileName)
        #return    
            
        # ----------------------
        #if os.path.exists(self.OutputFileName):
        #    self._synchronize(self.OutputFileName,self.OutputFileName)
        #else:
        #    print "error %s doesn't exists"%self.OutputFileName
        
        if self.clean_up:
            if os.path.exists(MatlabOutputFileNameModified):
                os.remove(MatlabOutputFileNameModified)
            if os.path.exists(ReportAllTxtFileName):
                os.remove(ReportAllTxtFileName)
            if os.path.exists(DcnvtErrFileName):
                os.remove(DcnvtErrFileName)
         
        collected = gc.collect()        
        if self.verbose:
            print "Cdcnvt3.convert() Garbage collector: collected %d objects." % (collected)

         
        if self.verbose:
            print "Cdcnvt3.convert() - end"
            sys.stdout.flush()
  
#=========================================================================
if __name__ == "__main__":
    
    print "dcnvt3 - local tests"
    print "Dcnvt3VersionNumberUpgrade ('3.122')", Dcnvt3VersionNumberUpgrade('3.122')
    print "Dcnvt3VersionNumberUpgrade ('3.2.1.134')", Dcnvt3VersionNumberUpgrade('3.2.1.134')
    
    print "cmp '3.122','3.121' -> ", Dcnvt3VersionNumberComparison('3.122','3.121')
    print "cmp '3.122','3.2.1.134' -> ", Dcnvt3VersionNumberComparison('3.122','3.2.1.134')
    print "cmp '3.0.0.122','3.2.1.134' -> ", Dcnvt3VersionNumberComparison('3.0.0.122','3.2.1.134')
    print "cmp '3.140','3.2.1.134' -> ", Dcnvt3VersionNumberComparison('3.122','3.2.1.134')
    print "cmp '3.2.1.134','3.2.1.135' -> ", Dcnvt3VersionNumberComparison('3.2.1.134','3.2.1.135')
    
    
    
    