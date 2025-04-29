"""
:Organization: Knorr-Bremse SfN GmbH Budapest, Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' Class cBatchServer - clone of server_server.m '''
import os
import shutil
import time
import logging
import logging.handlers
import os.path
import sys
import os.path
import datetime
import gc
try: 
    import psutil
except:
    pass

  # -------------------------------------------------------------------
    # 1. Batch server needs a path name to start execution and store the results and executed files.
    # 2. it runs until there is an external interrupt from keyboard etc.,
    # 3. Sorts the number of files by its own and file execution based on its date/time of creation.
  # -------------------------------------------------------------------

Info_tell_BatchServer_where_I_am = None
Info_Python_File = None

# used externally 
def tell_BatchServer_where_I_am(Info):
   global Info_tell_BatchServer_where_I_am
   print "tell_BatchServer_where_I_am", Info
   Info_tell_BatchServer_where_I_am = Info
 
Warnings_from_Application = [] 
def tell_BatchServer_WarningMsg (WarningMsg):
   global Warnings_from_Application
   print "tell_BatchServer_WarningMsg", WarningMsg
   Warnings_from_Application.append([datetime.datetime.now(), WarningMsg])
   print Warnings_from_Application
   
# -----------------------------------------------------
# used internally 
def Get_Info_say_where_I_am():
    global Info_tell_BatchServer_where_I_am
    global Info_Python_File
    s = []
    s.append("\n--------------------------")
    s.append("\nInfo:")
    if Info_Python_File is not None:
        s.append("\nPython_File :  %s"%Info_Python_File)
    else:
        s.append("\nPython_File :  not available")
        
    if Info_tell_BatchServer_where_I_am is not None:
        s.append("\ncomment     :  %s"%Info_tell_BatchServer_where_I_am['comment'])
        s.append("\nMeasFile    :  %s"%Info_tell_BatchServer_where_I_am['MeasFile'])
    else:
        s.append("\ncomment     :  not available")
        s.append("\nMeasFile    :  not available")
   
        
    s.append("\n--------------------------")
   
    return "".join(s)
   
    
class cBatchServer():
  # -------------------------------------------------------------------
  def __init__(self, PathName_root):
    self.PathName_root = PathName_root
  # -------------------------------------------------------------------
    # define folder names
    self.PathName_todo          = os.path.join(self.PathName_root,'todo')
    self.PathName_done          = os.path.join(self.PathName_root,'done')
    self.PathName_fail          = os.path.join(self.PathName_root,'fail')
    self.PathName_summary       = os.path.join(self.PathName_root,'Summary')
  # -------------------------------------------------------------------
    # create folder if necessary
    if not os.path.exists(self.PathName_todo):
      os.makedirs(self.PathName_todo)
    if not os.path.exists(self.PathName_done):
      os.makedirs(self.PathName_done)
    if not os.path.exists(self.PathName_fail):
      os.makedirs(self.PathName_fail)
    if not os.path.exists(self.PathName_summary):
      os.makedirs(self.PathName_summary)
  # -------------------------------------------------------------------
    # define file descriptor and summary files
    self.SummaryFile            = os.path.join(self.PathName_summary, "Summary.log" )
    self.Measurement            = os.path.join(self.PathName_summary, "Measfiles")
    self.SummaryHighlight       = os.path.join(self.PathName_summary, "summary_highlights.log")
    
  # -------------------------------------------------------------------
    # create instances and initialize variables 
    '''
    * self.TestResult = 0  - Test failed,
    * self.TestResult = 1  - Test passed,
    '''
    self.StartTime              = {}
    self.EndTime                = {}
    self.TestResult             = 0
    self.logger_module          = cLogger(self.PathName_summary)
    self.exception_handling     = cExceptionHandling(self.logger_module)
    self.Summary                = cSummary(self.SummaryFile, self.Measurement, self.SummaryHighlight)
  
  # -------------------------------------------------------------------
 # Files sorted by its creation date/time.
  def getSortedFileList(self, PathName):
  
  # -------------------------------------------------------------------
    ''' sort the file inside the folder by time of most recent content modification '''
    # sorting in Python :  http://wiki.python.org/moin/HowTo/Sorting/
    '''
    * st_mode  - protection bits,
    * st_ino   - inode number,
    * st_dev   - device,
    * st_nlink - number of hard links,
    * st_uid   - user id of owner,
    * st_gid   - group id of owner,
    * st_size  - size of file, in bytes,
    * st_atime - time of most recent access,
    * st_mtime - time of most recent content modification,
    * st_ctime - platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows)
    '''
    FileList = []
    
    for FileName in os.listdir(PathName):
      my_stat = os.stat(os.path.join(PathName,FileName))
      FileList.append([FileName,my_stat.st_mtime])
    # sort list by time of most recent content modification
    FileList.sort(key=lambda a: a[1],reverse=False) 
      
    # crete list with only the FileNames
    FileList2 = []
    for File in FileList:
      FileList2.append(File[0])
    return FileList2
  
  # -------------------------------------------------------------------
 # Main loop which execute files based on the sorted file list.
 # It sends information to respective methods for keeping the details of the execution. 
 
  def single_run(self):
    global Info_Python_File
    global Warnings_from_Application
  
    # -------------------------------------------------------------------
    for File in self.getSortedFileList(self.PathName_todo):
      print "BatchServer.single_run.Script:", File
      Info_Python_File = File
     # -------------------------------------------------------------------
      try:
        # -------------------------------------------------------------------
        self.StartTime = time.time()
        self.Summary.summaryFileInit(File)
        self.Summary.summaryStartEnd()
        self.Summary.viewFile()
        self.Summary.measFileWrite(File)
        # -------------------------------------------------------------------
        self.Summary.pipeStdout2File()
        execfile(os.path.join(self.PathName_todo,File))
        self.Summary.returnStdout2Console()
        #print Warnings_from_Application
        if Warnings_from_Application:
           self.Summary.AddList(Warnings_from_Application)
        Warnings_from_Application = []
        # -------------------------------------------------------------------
        self.TestResult             = 1
        self.Summary.successWrite()
        self.Summary.viewFile()
        shutil.move(os.path.join(self.PathName_todo,File), os.path.join(self.PathName_done,File))
     # -------------------------------------------------------------------
      except Exception, ex:
        self.Summary.returnStdout2Console()
        self.TestResult             = 0
        self.exception_handling.exceptionLogging()
        self.Summary.failureWrite()
        self.Summary.viewFile()
        if os.path.exists(os.path.join(self.PathName_todo,File)):
            shutil.move(os.path.join(self.PathName_todo,File), os.path.join(self.PathName_fail,File))
     # ------------------------------------------------------------------- 
      finally:
        self.Summary.viewFile()
        self.Summary.summaryStartEnd()
        self.EndTime = time.time()
        Hours, Minutes, Seconds = self.Summary.executionEnd(self.EndTime, self.StartTime, File)
        self.Summary.inShort(File, self.TestResult, Hours, Minutes, Seconds)
        self.Summary.viewFile()
        self.Summary.fileSizeCheck(File, self.PathName_summary)
 # -------------------------------------------------------------------
  def run(self):
    while 1:
      self.single_run()
      print 'Awaiting input'
      time.sleep(1.5) # wait 1.5 Seconds
      
 # -------------------------------------------------------------------
    # Definition of the loggers, handlers and the format of the logging message are described.
    # It uses rotating file handler and the number of files and its size can be defined accordingly.
 # -------------------------------------------------------------------

class cLogger():
 # -------------------------------------------------------------------
  def __init__(self, PathName_summary):
    self.Path = PathName_summary
    self.file_maxsize            = 1024*1024  # Size of the summary and exception logging files
    self.file_Noof               = 100        # Maximum number of summary and exception logging files each.
   
    self.datetime_now_str = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S")  # with fractions of seconds: "%Y-%m-%d_%H.%M.%S.%f"

   
 # -------------------------------------------------------------------
# Corresponding Handlers,format and its linkages for the respective logger.
 # -------------------------------------------------------------------
# 1.This handler writes everything to a file when debug.
  def debug(self):
    #os.chdir(self.Path)
    self.x1 = logging.getLogger("logall")
    self.x1.setLevel(logging.DEBUG)
    #path = os.path.join(self.Path,'Debug.log')
    path = os.path.join(self.Path,"%s_%s.txt"%('Debug',self.datetime_now_str))
    h1 = logging.handlers.RotatingFileHandler(path, maxBytes= self.file_maxsize,backupCount=self.file_Noof, mode="a")
    f  = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s \n" )
    h1.setFormatter(f)
    h1.setLevel(logging.DEBUG)
    self.x1.addHandler(h1)
    return self.x1
 # -------------------------------------------------------------------
# 2.This handler writes everything to a file when error.
  def error(self):
    #os.chdir(self.Path)
    self.x2 = logging.getLogger("logall")
    self.x2.setLevel(logging.ERROR)
    #path = os.path.join(self.Path,'Error.log')
    path = os.path.join(self.Path,"%s_%s.txt"%('Error',self.datetime_now_str))
    h2 = logging.handlers.RotatingFileHandler(path, maxBytes= self.file_maxsize,backupCount=self.file_Noof, mode="a")
    f  = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s \n" )
    h2.setFormatter(f)
    h2.setLevel(logging.ERROR)
    self.x2.addHandler(h2)
    return self.x2
 # -------------------------------------------------------------------
# 3.This handler writes everything to a file when critical.
  def critical(self):
    #os.chdir(self.Path)
    self.x3 = logging.getLogger("logall")
    self.x3.setLevel(logging.CRITICAL)
    #path = os.path.join(self.Path,'Critical.log')
    path = os.path.join(self.Path,"%s_%s.txt"%('Critical',self.datetime_now_str))
    h3 = logging.handlers.RotatingFileHandler(path, maxBytes= self.file_maxsize,backupCount=self.file_Noof, mode="a")
    f  = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s \n")
    h3.setFormatter(f)
    h3.setLevel(logging.CRITICAL)
    self.x3.addHandler(h3)
    return self.x3
 # -------------------------------------------------------------------
# 4.This handler writes everything to a file when warning.
  def warning(self):
    #os.chdir(self.Path)
    self.x4 = logging.getLogger("logall")
    self.x4.setLevel(logging.WARNING)
    #path = os.path.join(self.Path,'Warning.log')
    path = os.path.join(self.Path,"%s_%s.txt"%('Warning',self.datetime_now_str))
    h4 = logging.handlers.RotatingFileHandler(path, maxBytes= self.file_maxsize,backupCount=self.file_Noof, mode="a")
    f  = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s \n" )
    h4.setFormatter(f)
    h4.setLevel(logging.WARNING)
    self.x4.addHandler(h4)
    return self.x4
 # -------------------------------------------------------------------
# 5.This handler writes everything to a file when info.
  def info(self):
    #os.chdir(self.Path)
    self.x5 = logging.getLogger("logall")
    self.x5.setLevel(logging.INFO)
    #path = os.path.join(self.Path,'Information.log')
    path = os.path.join(self.Path,"%s_%s.txt"%('Information',self.datetime_now_str))
    h5 = os.path.join(self.Path, logging.handlers.RotatingFileHandler(path, maxBytes= self.file_maxsize,backupCount=self.file_Noof, mode="a"))
    f  = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s \n" )
    h5.setFormatter(f)
    h5.setLevel(logging.info)
    self.x5.addHandler(h5)
    return self.x5
 
 # -------------------------------------------------------------------
    # Exceptions based on the loggers described in class cLogger().
    # exceptionLogging method finds the verbosity of the exception occured through getEffectiveLevel method from logger module.
    # It calls the corresponding logger and logging the exception message.
 # -------------------------------------------------------------------

class cExceptionHandling():
 # -------------------------------------------------------------------
  def __init__(self, LoggerInitialize):
    self.exceptionlogger = LoggerInitialize
    #self.rangeoflevel=range(0,500,10)
    logger = logging.getLogger()
    self.geteffectivelevel = logger.getEffectiveLevel()
 # -------------------------------------------------------------------
  def exceptionLogging(self):
    if (self.geteffectivelevel==10):
      self.exceptionlogger.debug()
      print"Debugging required!! Open Debug.log for details"
      self.exceptionlogger.x1.debug("Debug! ")
      self.exceptionlogger.x1.exception("Debug! ")
    elif (self.geteffectivelevel==20):
      self.exceptionlogger.info()
      print"Information!!open Info.log for details"
      self.exceptionlogger.x5.info("Information!! ")
      self.exceptionlogger.x5.exception("Info! ")
    elif (self.geteffectivelevel==30):
      self.exceptionlogger.warning()
      print "Warning!! Open Warning.log for details"
      self.exceptionlogger.x4.warning("Warning! %s "%Get_Info_say_where_I_am())
      self.exceptionlogger.x4.exception("Warning! %s "%Get_Info_say_where_I_am())
    elif (self.geteffectivelevel==40):
      self.exceptionlogger.error()
      print"Error occurred!! Open Error.log for details"
      self.exceptionlogger.x2.error("Error! ")
      self.exceptionlogger.x2.exception("Error! ")
      #break
    elif (self.geteffectivelevel==50):
      self.exceptionlogger.critical()
      print"Critical! Open Critical.log for details"
      self.exceptionlogger.x3.critical("Critical! ")
      self.exceptionlogger.x3.exception("Critical! ")
      #break
    else:
      print "Logging system was unable to detect the error occured.Please run it again."

 # -------------------------------------------------------------------
    # Summary file for overall summary. 
    # 1. Summary.log is for extracting the overall summary from the current execution and stores it.
    # 2. Measfiles.log is for storing the .MDF files along with its path out of the current execution.
    # 3. summary_highlights.log is for a quick one line result of the current execution.
    # So, in general, this class extends the execution of a file by storing the results in a respective log file.  
# -------------------------------------------------------------------
class cSummary():
 
  # -------------------------------------------------------------------
  def __init__(self, FileSummary, FileMeasurement, FileSummaryHighlight):
    # -------------------------------------------------------------------
    self.FileSummary                    = FileSummary
    self.FileMeasurement                = FileMeasurement
    self.FileSummaryHighlight           = FileSummaryHighlight
    # -------------------------------------------------------------------
    self.summaryfile_maxsize            = 1024*1024  # Size of the summary and exception logging files
    self.summaryfile_Noof               = 100        # Maximum number of summary and exception logging files each.
    self.totalnooffiles                 = range(1, self.summaryfile_Noof, 1)
    # -------------------------------------------------------------------
    self.file_summary_highlight         = open(self.FileSummaryHighlight, "a")
    self.file_summary                   = open(self.FileSummary, "a")
    
    # Measurement File will be created for each new start
    FileName = "%s_%s.txt"%(self.FileMeasurement, datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))   # "%Y-%m-%d_%H.%M.%S.%f"
    self.file_measurement               = open(FileName, "w")
    
    self.save_output_stdout = None
    self.save_output_stderr = None
 
  # -------------------------------------------------------------------
  def _timestamp(self, t = None):
    if t is None:  
        t = datetime.datetime.now()
       
    return t.strftime("%Y-%m-%d_%H:%M:%S.%f")+";"
  # -------------------------------------------------------------------
  def fileSizeCheck(self, PyFile, PathName):
    file_path,file_name = os.path.split(PathName)
    size = os.stat(self.FileSummary)[6]
    if not size > self.summaryfile_maxsize:
      return None
    else:
      print "Creating a new summary file"
      AddFileName   = os.path.splitext(PyFile)[0]
      AddSummaryFilename = os.path.splitext(file_name)[0]
      self.NewSummaryFile =  AddSummaryFileName + AddFileName + ".log"
      shutil.copy(self.FileSummary, self.NewSummaryFile)
      self.file_summary   = open(self.FileSummary, "w")
      self.file_summary   = open(self.FileSummary, "a")
      
 # ------------------------------------------------------------------- 
  def summaryFileInit(self, FileName):
    print >> self.file_summary, "#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print >> self.file_summary, self._timestamp(), "Starting new Batch server" 
    print >> self.file_summary, "#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print >> self.file_summary, self._timestamp(), "Start;",  FileName 

  # -------------------------------------------------------------------
  def summaryStartEnd(self):
    #print >> self.file_summary, self._timestamp(), "Time: "
    pass
    
  # -------------------------------------------------------------------
  def AddList(self,List):
    for t, WarningMsg in List:
        print >> self.file_summary, self._timestamp(t), WarningMsg 
    
  # -------------------------------------------------------------------
  def bytes2human(self, n): 

    # http://code.activestate.com/recipes/578019 
    # >>> bytes2human(10000) 
    # '9.8K' 
    # >>> bytes2human(100001221) 
    # '95.4M' 
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y') 
    prefix = {} 
    for i, s in enumerate(symbols): 
        prefix[s] = 1 << (i + 1) * 10 
    for s in reversed(symbols): 
        if n >= prefix[s]: 
            value = float(n) / prefix[s] 
            return '%.1f%s' % (value, s) 
    return "%sB" % n 
   
  # -------------------------------------------------------------------
  def pprint_ntuple(self,nt): 
    print >> self.file_summary, self._timestamp(), 'MEMORY:'
    for name in nt._fields: 
        value = getattr(nt, name) 
        if name != 'percent': 
            value = self.bytes2human(value) 
        print >> self.file_summary, self._timestamp(), '  %-10s : %7s' % (name.capitalize(), value)

  
    
  # -------------------------------------------------------------------
  def _callGarbageCollector(self):
    collected = gc.collect()
    print >> self.file_summary, self._timestamp(), "Garbage collector: collected %d objects." % (collected)
    
    #  mem = psutil.virtual_memory() -> named tupel
    # mem(total=8374149120L, available=1247768576L, percent=85.1, used=8246628352L, free=127520768L, active=3208777728, inactive=1133408256, buffers=342413312L, cached=777834496)
    try:
        self.pprint_ntuple(psutil.virtual_memory()) 
    except:
        pass
 
 # -------------------------------------------------------------------
  def successWrite(self):
    print >> self.file_summary, self._timestamp(), "Run successful !!!"
    self._callGarbageCollector()
    #print >> self.file_summary,  "Please open Measfiles.log for list of measurement files." + "\n"
 # -------------------------------------------------------------------
  def failureWrite(self):
    print >> self.file_summary, self._timestamp(), "Run failed !!!" 
    self._callGarbageCollector()
    #print >> self.file_summary, self._timestamp(), "Fail Run: Run Failed.Please open the corresponding exception log file(s) for details." 
    #print >> self.file_summary, "Please open Measfiles.log for list of measurement files."
 # -------------------------------------------------------------------
  def executionEnd(self, end, start, FileName):
    T = end - start
    Hours, Remainder = divmod(T, 3600)
    Minutes, Seconds = divmod(Remainder, 60)
    print >> self.file_summary, self._timestamp(), "End; Execution time:", "%02d:%02d:%02d"  % (Hours, Minutes, Seconds), "(HH:MM:SS)"
    #print >> self.file_summary,        "*****************"
    #print >> self.file_summary, "Total Execution time(sec):" 
    #print >> self.file_summary, "File: " , FileName  + ", Execution time (HH:MM:SS): " ,  "%02d:%02d:%02d"  % (Hours, Minutes, Seconds)
    return Hours, Minutes,Seconds
 # -------------------------------------------------------------------
  def viewFile(self):
    # Flush summary file
    self.file_summary.flush()
    os.fsync(self.file_summary)
    
    # Flush Measurement file
    self.file_measurement.flush()
    os.fsync(self.file_measurement)
    
    # Flush summary highlights file
    self.file_summary_highlight.flush()
    os.fsync(self.file_summary_highlight)
 # -------------------------------------------------------------------
  def measFileWrite(self, FileName):
    print >> self.file_measurement, "#************************************************************"
    print >> self.file_measurement, self._timestamp(), FileName
    print >> self.file_measurement, "#------------------------------------------------------------"
    print >> self.file_measurement, "#Corresponding measurement files and its path are as follows: "
    print >> self.file_measurement, "#------------------------------------------------------------"
 # -------------------------------------------------------------------
  def inShort(self, FileName, Result, Hours, Minutes, Seconds):
    self.Result = Result
    #print >> self.file_summary_highlight, "#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"  
    if self.Result == 1:
        print >> self.file_summary_highlight, self._timestamp(), "Run passed;", "%02d:%02d:%02d;" % (Hours, Minutes, Seconds),  FileName
    else:
        print >> self.file_summary_highlight, self._timestamp(), "Run failed;", "%02d:%02d:%02d;" % (Hours, Minutes, Seconds),  FileName
 # -------------------------------------------------------------------
  def pipeStdout2File(self):
    self.save_output_stdout = sys.stdout
    self.save_output_stderr = sys.stderr
    
    sys.stdout = self.file_measurement
    sys.stderr = self.file_measurement
    
    
  def returnStdout2Console(self):
    sys.stdout = self.save_output_stdout
# ---------------------------------------------------------------------------------------------------------------
