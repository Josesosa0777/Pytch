"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' Class cDAS_eval - clone of DAS_eval_step1.m '''

'''
   configuration file "conf_DAS_eval_step1.txt" (default filename)
   tokens:
      Project       - name of the project (e.g. FLR20) 
      src_dir_meas  - folder where measurement files are stored
      meas_file_ext - measurement file extensions
      NpyHomeDir    - path where numpy backup files will be saved
      eval_function - module to be used for evaluation
      Report_Only   - only generate report and export excel - no analyse of measurements
      Debug         - don't use internal exception handling
'''
'''
   todo:
     list_range = 32:33
'''

# python standard imports
import os
import fnmatch
import sys, traceback

# KB python library imports
# todo from measproc.Batch          import findMeasurements
from measparser.SignalSource import cSignalSource

# home library 
import kbtools

def findMeasurements(Directory, Pattern, Recursively=False, FindDirToo=False):
    """
    :Parameters:
      Directory : str
      Pattern : str
        Wildcard search string
    :Keywords:
      FindDirToo : bool
        Default value is False
      Recursively : bool
        Default value is False
    :ReturnType: generator
    """
    Patterns = Pattern.split(' ')
    for Root, Dirs, Files in os.walk(Directory):
        for Name in Files:
            for Extension in Patterns:
                if fnmatch.fnmatch(Name, Extension):
                    Path = os.path.join(Root, Name)
                    yield Path
        if FindDirToo:
            for Name in Dirs:
                for Extension in Patterns:
                    if fnmatch.fnmatch(Name, Extension):
                        Path = os.path.join(Root, Name)
                        #print Path
                        yield Path
        if not Recursively:
            break
    pass


class LocalCSignalSource(cSignalSource):
    '''
    main purpose of this derived class is to add the attribute 'FileName_org'
    '''
    def __init__(self, MeasFile, NpyHomeDir, FileName_org=None):   
        #super(LocalCSignalSource,self).__init__(MeasFile, NpyHomeDir)   # call constructor from Base Class "cSignalSource"
        cSignalSource.__init__(self,MeasFile, NpyHomeDir)   # call constructor from Base Class "cSignalSource"
        self.FileName_org = FileName_org
        print "LocalCSignalSource.FileName_org:", self.FileName_org

# ============================================================================ 
class cDAS_eval():

  #----------------------------------------------------------------------------
  def __init__(self,verbose=True):
        self.verbose = verbose
        pass 
  
  #----------------------------------------------------------------------------
  def _proc_step(self, step, MeasFile):
        '''
           processing step
           
           send status messages to Batchserver
        
        '''
        d = {}
        d['comment'] = step
        d['MeasFile'] = MeasFile
        kbtools.tell_BatchServer_where_I_am(d)

    
  #----------------------------------------------------------------------------
  def LoadConfigFile(self, Args):
        '''
           load configuration file -> self.conf_DAS_eval
        '''
        if isinstance(Args[0],str):
            # if a str is given -> use it as configuration file name
            self.conf_DAS_eval = kbtools.read_input_file('tag_only',Args[0])
        elif isinstance(Args[0],dict):
            self.conf_DAS_eval = Args[0]

    
  #----------------------------------------------------------------------------
  def GetConfigPar(self, Token, ParType='str'):
        '''
           read paramerter from configuration file
           
           ParType: 'str', 'list', 'bool'
           
        '''
        Par = None
        if ParType=='str':
            Par = None
            if Token in self.conf_DAS_eval:
                if isinstance(self.conf_DAS_eval[Token],str):
                    Par = self.conf_DAS_eval[Token]  
        elif ParType=='list':
            Par = None
            if Token in self.conf_DAS_eval:
                Par = self.conf_DAS_eval[Token]  
                if isinstance(Par,str):
                    Par = [Par]           # create a list in case it's only one string
        elif ParType=='bool':
            Par = False
            if Token in self.conf_DAS_eval:
                if isinstance(self.conf_DAS_eval[Token],str):
                    if self.conf_DAS_eval[Token].lower() in ["yes","on","1"]:
                        Par = True 
 
        return Par
 
  #----------------------------------------------------------------------------
  def step1(self,*Args):

    # -------------------------------------- 
    # default behavior
    if len(Args)<1:
        # if no argument specified assume standard configuration file name
        Args = ['conf_DAS_eval_step1.txt']
  
    # -------------------------------------- 
    # load configuration file -> conf_DAS_eval
    self.LoadConfigFile(Args)
       
    # -------------------------------------- 
    # read the following tags from configuration file
    Project        = self.GetConfigPar('Project',      'str')  # "Project"       -> name of the project (e.g. FLR20) 
    SrcDirMeasList = self.GetConfigPar('src_dir_meas', 'list') # "src_dir_meas"  -> folder where measurement files are stored
    meas_file_ext  = self.GetConfigPar('meas_file_ext','str')  # "meas_file_ext" -> measurement file extensions
    NpyHomeDir     = self.GetConfigPar('NpyHomeDir',   'str')  # "NpyHomeDir"    -> NpyHomeDir
    MatlabTmpDir   = self.GetConfigPar('MatlabTmpDir', 'str')  # "MatlabTmpDir"  -> MatlabTmpDir
    
    UserModuleList = self.GetConfigPar('eval_function','list') # "eval_function" -> module to be used for evaluation
    DbcList        = self.GetConfigPar('dbc',          'list') # "dbc"           -> CAN Database file 

    Report_Only_b  = self.GetConfigPar('Report_Only',  'bool') # "Report_Only"   -> Report_Only_b = True|False 
    debug_b        = self.GetConfigPar('Debug',        'bool') # "Debug"         -> debug_b = True|False
    prefer_blf_b   = self.GetConfigPar('Prefer_BLF',   'bool') # "Prefer_BLF"    -> prefer_blf_b = True|False
    Keep_TeX_b     = self.GetConfigPar('Keep_TeX',     'bool') # "Keep_TeX"      -> keep tex sources

    CreatePngBatch = self.GetConfigPar('CreatePngBatch', 'str')  # "CreatePngBatch"  -> CreatePngBatch
    
    Keep_MatlabTmpFiles = self.GetConfigPar('Keep_MatlabTmpFiles',     'bool') # "Keep_MatlabTmpFiles"      -> keep generated Matlab Binary files 
    enable_Hunt4Event_save_events = self.GetConfigPar('enable_Hunt4Event_save_events',     'bool') # "enable_Hunt4Event_save_events"      -> save data collected by hunt4event
   
   
   
   
    if DbcList:
        DbcList_new = []
        for dbc_cfg in DbcList:
            dbc_new = {}
            dbc_cfg = dbc_cfg.split(';')
            if len(dbc_cfg)>1:
                tmp_str0 = dbc_cfg[0]
                if 'j' in tmp_str0:
                    tmp_str0 = tmp_str0.replace('j','') 
                    dbc_new['J1939_Option'] = True
                else:
                    dbc_new['J1939_Option'] = False
                try:
                    dbc_new['CAN_Channel'] = int(tmp_str0)
                except:
                    dbc_new['CAN_Channel'] = None
                dbc_new['dbc_file']    = dbc_cfg[1]
            else:
                dbc_new['dbc_file']    = dbc_cfg[0]
            DbcList_new.append(dbc_new)
        
        DbcList = DbcList_new
    print DbcList
    
    # -------------------------------------- 
    # show settings
    if self.verbose:
        print "Current Settings:"
        print "  Project        : ", Project  
        print "  src_dir_meas   : ", SrcDirMeasList
        print "  meas_file_ext  : ", meas_file_ext
        print "  NpyHomeDir     : ", NpyHomeDir
        print "  MatlabTmpDir  : ", MatlabTmpDir
        print "  eval_function  : ", UserModuleList    
        print "  Report_Only_b  : ", Report_Only_b    
        print "  Debug          : ", debug_b    
        print "  prefer_blf_b   : ", prefer_blf_b    
        print "  Keep_TeX_b     : ", Keep_TeX_b    
        print "  CreatePngBatch : ", CreatePngBatch 
        print "  Keep_MatlabTmpFiles: ", Keep_MatlabTmpFiles
        print "  enable_Hunt4Event_save_events:", enable_Hunt4Event_save_events
    
    # -------------------------------------- 
    # check if necessary information is available
    if not SrcDirMeasList:
        msg = "src_dir_meas not available -> stopp"
        print msg
        self._proc_step(msg,"")
        kbtools.tell_BatchServer_WarningMsg(msg)
        return

    
    # -------------------------------------- 
    # create 'MeasFileList'
    MeasFileList = []
    src_dir_meas = 'default'
    if  not Report_Only_b:
        for MeasFile in SrcDirMeasList:
            if not os.path.exists(MeasFile):
                msg = "Error: <%s> doesn't exist" % MeasFile
                print msg
                self._proc_step(msg,"")
                kbtools.tell_BatchServer_WarningMsg(msg)
                return
            elif os.path.isfile(MeasFile):
                MeasFileList.append(MeasFile)
            elif os.path.isdir(MeasFile):
                #MeasFileList = findMeasurements(MeasFile, '*.mdf', Recursively=False)
                MeasFileList.extend(findMeasurements(MeasFile,  meas_file_ext , Recursively=False))
  
            # sort MeasFileList (not possible because of 'generator' object ) 
            #MeasFileList = MeasFileList.sort()

        src_dir_meas = os.path.dirname(MeasFileList[0])

        
    if self.verbose:
        print "MeasFileList",len(MeasFileList)
        print "src_dir_meas", src_dir_meas    
        print "src_dir_meas :",os.path.basename(src_dir_meas)
        
        
    #--------------------------------------
    kbtools.cHunt4Event.enable_save_event = False
    if enable_Hunt4Event_save_events:
        kbtools.cHunt4Event.enable_save_event = True
        
    # -------------------------------------- 
    # create 'UserModuleInstanceList'
    UserModuleInstanceList = []
    for UserModuleName in UserModuleList:
      try:
        # module is in the current folder
        Module = __import__(UserModuleName)
      except:
        # module is in kbtools_user
        Module = __import__('kbtools_user')
      # class is ModuleName with prefix 'c'          
      Class  = getattr(Module, 'c'+UserModuleName)
      UserModuleInstanceList.append(Class())
    
    #print UserModuleInstanceList
    
    # -------------------------------------- 
    # workaround for backward compatibility
    if isinstance(self.conf_DAS_eval['src_dir_meas'], list):
        self.conf_DAS_eval['src_dir_meas_list'] = self.conf_DAS_eval['src_dir_meas']
        self.conf_DAS_eval['src_dir_meas'] = self.conf_DAS_eval['src_dir_meas_list'][0]
    
    
    # -------------------------------------- 
    # create tex-report
    self.setup_kb_tex(self.conf_DAS_eval,'step1')

    # make .kb_tex available in the UserModule
    for UserModule in UserModuleInstanceList:
        UserModule.kb_tex = self.kb_tex           
            
    # init() 
    if  Report_Only_b:
        for UserModule in UserModuleInstanceList:
            UserModule.init(src_dir_meas,self.conf_DAS_eval,load_event=True)
    else:        
        for UserModule in UserModuleInstanceList:
            UserModule.init(src_dir_meas,self.conf_DAS_eval)

    # create report structure
    for UserModule in UserModuleInstanceList:
        UserModule.report_init()
        
    # create Batch file for creating pngs; pngs are no longer created on the fly    
    kbtools.SetBatchFileName_for_take_snapshot_from_videofile(CreatePngBatch)    
    
    # loop over all measurement files
    if  not Report_Only_b:
    
        fobj = open("MeasFileList.txt", "w")
            
        if self.verbose:
            print "======================================================"
            print "======================================================"
            print "    start of loop over all measurement files          "
            print "======================================================"
            print "======================================================"
        
        
        for MeasFile in MeasFileList:
            
            if self.verbose:
                print "======================================================"
                print "MeasFile requested basename:", os.path.basename(MeasFile)
                print "MeasFile requested full    :", MeasFile
                print "======================================================"
            else:
                print "MeasFile:", os.path.basename(MeasFile)
               
            fobj.write(os.path.basename(MeasFile))       
            tmp_is_okay = True  
            MatlabTmpFile_created = False            
            
            # original MeasFile  (required if blf files converted in Matlab Binary)
            MeasFile_org = MeasFile
            
            self._proc_step("before measurement conversion", os.path.basename(MeasFile))
            
            # ---------------------------------------------------------------------------------
            # convert from blf files
            
            if prefer_blf_b: 
                # use blf files instead of mf4 file
                if self.verbose:
                    print "use blf files instead of mf4 file"
            
                # ------------------------------------------------------
                # dbc_list - list of dbcs to be used for conversion
                if not DbcList:
                    # default                                      
                    DbcPathName = r"C:\KBData\DAS_eval\dbc"
                    dbc_list = []
    
                    # ------------------------
                    dbc_list.append(r'J1939_DAS_Ford.dbc')            # J1939
                    dbc_list.append(r'A087MB_V3.3draft_MH1.dbc')      # FLR20 data acquisition
    
                    #dbc_list.append(r'Video_Fusion_Protocol_Released_v1.4b_Mar_27_2013_TrwDebug_mod.dbc')
                    #dbc_list.append(r'Video_Fusion_Protocol_2013-11-04.dbc')
                    dbc_list.append(r'Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc') # FLC20 data acquisition
       
                    dbc_list.append(r'DIRK.dbc')                      # Driver Response Key
                    # ------------------------
                    
                    dbc_list = [ os.path.join(DbcPathName,dbc) for dbc in dbc_list]
                else:
                    dbc_list = DbcList
                
                # ------------------------------------------------------
                # folder where Matlab binaries are stored
                if MatlabTmpDir is None:
                    MatlabTmpDir = r'C:\KBData\matlab_tmp'
                
        
                # ------------------------------------------------------
                InputFolderName  = os.path.dirname(MeasFile)
                SubFolderName    = os.path.split(os.path.dirname(MeasFile))[1]
                BaseFileName     = os.path.splitext(os.path.basename(MeasFile))[0]
                OutputFolderName = os.path.join(MatlabTmpDir,SubFolderName)
                
                New_FileName = BaseFileName
                New_Extension = '.mat'
                New_MeasFile = os.path.join(OutputFolderName,New_FileName+New_Extension)
                
                if self.verbose:
                    print "InputFolderName", InputFolderName  
                    print "SubFolderName", SubFolderName    
                    print "BaseFileName", BaseFileName  
                    print "OutputFolderName", OutputFolderName    
                    print "New_MeasFile", New_MeasFile 
                    print "dbc_list", dbc_list
                    
        
                if not os.path.exists(New_MeasFile):
                    clean_up=True # # remove temporarily generated files
                    verbose=True 
                    dcnvt3 = kbtools.Cdcnvt3(clean_up=clean_up,verbose=verbose)
                    dcnvt3.set_dbc_list(dbc_list)
                    dcnvt3.set_input_files(BaseFileName, suffix_list= [], InputFolderName=InputFolderName)
                    dcnvt3.set_output_file('M', New_FileName, New_Extension, OutputFolderName, overwrite=True)
                    dcnvt3.convert()
                    MatlabTmpFile_created = True
                    
                MeasFile = New_MeasFile
                
            # ---------------------------------------------------------------------------------
            # load measurement file
            if os.path.exists(MeasFile):
                             

                if self.verbose:
                    print "------------------------------------------------------"
                    print "DAS_eval.step1() - load measurement file:"
                    print "  MeasFile used basename:", os.path.basename(MeasFile)
                    print "  MeasFile used full    :", MeasFile
                    print "------------------------------------------------------"

                
                self._proc_step("before Source", os.path.basename(MeasFile))
                
                # create Source 
                if MeasFile.endswith('.mat'):
                    # Assumption Matlab Binary are created by dcnvt3 and need not to be backuped
                    Source =  kbtools.CReadDcnvt3(MeasFile,FileName_org=MeasFile_org)
                    if not Source.isValid():
                        tmp_is_okay = False
                    else:
                        if not Keep_MatlabTmpFiles and MatlabTmpFile_created:
                            print "Remove created Matlab binary file after data have been loaded into memory"
                            print "  File:", MeasFile
                            print "  Folder:",os.path.dirname(MeasFile)
                            os.remove(MeasFile)   # remove the Matlab Binary
                            try:
                                os.rmdir(os.path.dirname(MeasFile)) # remove the folder if it is empty
                            except Exception, e:
                                print "error - remove the folder if it is empty ",e.message
                                traceback.print_exc(file=sys.stdout)
                else:
                    # create SignalSource instance
                    Source = LocalCSignalSource(MeasFile, NpyHomeDir, FileName_org=MeasFile_org)      
      
                # do reinit before every measurement because we currently have no seamless continuously recorded measurements  
                for UserModule in UserModuleInstanceList:
                    UserModule.reinit()
        
                # process measurement    
                for UserModule in UserModuleInstanceList:
                    self._proc_step("User Module process: %s"%str(UserModule), os.path.basename(MeasFile))
                    UserModule.process(Source)
        
                if MeasFile.endswith('.mat'):
                    pass
                else:
                    # save Source to create numpy backup files
                    Source.save()
                  
            else:
                print "DAS_eval: Warning: %s does not exist"%MeasFile           

            if tmp_is_okay:
                fobj.write(" okay\n")
            else:
                fobj.write(" error\n")    
                
                
        fobj.close()

        if self.verbose:
            print "finish"
            
            
        # finish the data processing
        for UserModule in UserModuleInstanceList:
            UserModule.finish()

    # -------------------------------------------------------------------------        
    # UserModule has to fill in the report 
    for UserModule in UserModuleInstanceList:
      UserModule.report()
    
    # -------------------------------------------------------------------------        
    # pdf will be generated
    self.gen_kb_tex(do_clean_up__f = not Keep_TeX_b)
    
    # -------------------------------------------------------------------------        
    # Execl Export 
    for UserModule in UserModuleInstanceList:
        if debug_b:
            UserModule.excel_export()
        else:
            try:
                UserModule.excel_export()
            except:
                pass
        
    
  #----------------------------------------------------------------------------
  def step2(self,*Args):

    # default behavior
    if len(Args)<1:
      # if no argument specified assume standard configuration file name
      Args = ['conf_DAS_eval_step2.txt']
  
    # load cfg
    if isinstance(Args[0],str):
      # if a str is given -> use it as configuration file name
      cfg = kbtools.read_input_file('tag_only',Args[0])
    elif isinstance(Args[0],dict):
      cfg = Args[0]

    # check cfg 
    # tbd.    
  
    # -------------------------------------- 
    # unpack configuration 

    UserModuleList = cfg['eval_function']
    # create a list anyway
    if isinstance(UserModuleList,str):
       UserModuleList = [UserModuleList]
    #print UserModuleList    

    # -------------------------------------- 
    # create UserModuleInstanceList
    UserModuleInstanceList = []
    for UserModuleName in UserModuleList:
      try:
        # module is in the current folder
        Module = __import__(UserModuleName)
      except:
        # module is in kbtools_user
        Module = __import__('kbtools_user')
      # class is ModuleName with prefix 'c'          
      Class  = getattr(Module, 'c'+UserModuleName)
      UserModuleInstanceList.append(Class())
    
    #print UserModuleInstanceList
    
    
    # -------------------------------------- 
    # create tex-report
    self.setup_kb_tex(cfg,'step2')

    # start
    for UserModule in UserModuleInstanceList:
      # to make .kb_tex available in the UserModule
      UserModule.kb_tex = self.kb_tex   
      UserModule.step2()
    
    # pdf will be generated
    self.gen_kb_tex()

    
  #----------------------------------------------------------------------------
  def setup_kb_tex(self,cfg,mode):
  
    self.kb_tex = kbtools.cKB_TEX()
    #-----------------------------------------------
    # 1. : Setting for the report

    # init 
    d = {}
    d["Folder"]     = cfg.get('report_dir',       'my_report')             # directory, in which the report will be generated 
    d["ReportName"] = cfg.get('report_name',      'report')                # filename of the report
    d["Titel"]      = cfg.get('report_title',     'Big Paper')             # title of the report, upper line
    d["SubTitel"]   = cfg.get('report_subtitle',  'created using Python')  # title of the report, lower line
    d["Author"]     = cfg.get('report_author',    'T/BCD~4.1')             # author
    d["Department"] = cfg.get('report_department','T/BCD~4.1 - DAS')       # department
    
    
    self.kb_tex.init(d)

    # start of document
    # preface of the document
    preface = {}
    preface['title']             = cfg.get('first_page_title',            'Here you insert the Title of the Test Report')
    preface['project']           = cfg.get('first_page_project',          'Here you insert the Name of the Project')
    preface['objective']         = cfg.get('first_page_objective',        'Here you insert your Objective')
    preface['tested_by']         = cfg.get('first_page_tested_by',        'Here you insert your Name')
    preface['released_by']       = cfg.get('first_page_released_by',      'Here you insert the Name of your boss')
    preface['distribution_list'] = cfg.get('first_page_distribution_list','Here you insert the Name of the recipients')
    preface['EDM_link']          = cfg.get('first_page_EDM_link',         'Here you insert the EDM_link')
    preface['document_link']     = cfg.get('first_page_document_link',    'Here you insert the document_link')
    preface['DR_link']           = cfg.get('first_page_DR_link',          'Here you insert the DR_link')

    self.kb_tex.start(preface)

    #-----------------------------
    # 2.: layout of the report

    # sequence important !!!
    # introduction
    self.kb_tex.tex_main('\n\\input{intro.tex}\n')

    #-----------------------------
    # 3.: filling the report 

    # introduction  
    # first select the working file
    self.kb_tex.workingfile('intro.tex')
  
    # then all output is written to 'intro.tex'
    self.kb_tex.tex('\n\\newpage\\section{Introduction}')    
    if 'step1'==mode:
      self.kb_tex.tex('\nThis report is generated by DAS\_eval.py step1.')
    elif 'step2'==mode:
      self.kb_tex.tex('\nThis report is generated by DAS\_eval.py step2.')
          

  #----------------------------------------------------------------------------
  def gen_kb_tex(self,do_clean_up__f=True):
    # close report and generate pdf
    self.kb_tex.finish()
    self.kb_tex.gen(do_clean_up__f=do_clean_up__f)

