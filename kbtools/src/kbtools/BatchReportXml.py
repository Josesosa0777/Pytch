'''

   Batch-Report-Xml Structure 
   Access
   Sqlite Database
   
   Ulrich Guecker
   2012-02-28


'''


# python standard imports
import os
import time
import sqlite3
import xml.dom.minidom
import numpy as np
import pylab as pl
import pickle

# ===========================================================================================
# local utilities
# ===========================================================================================
verbose = True
verbose = False

def myprint(s):
    if verbose:
        print (s)

#--------------------------------------------------------------
def unique(seq): 
   # order preserving
   checked = []
   for e in seq:
       if e not in checked:
           checked.append(e)
   return checked

   
    
#--------------------------------------------------------------------------------------------
class cBatchReportXmlDataBase():

  # ---------------------------------------------------------------------  
  def __init__(self, DataBaseFileName, Reset=False):
    
    self.DataBaseFileName = DataBaseFileName
    self.Reset            = Reset   
    
    myprint("StartDB database %s (Reset=%s)"%(self.DataBaseFileName,self.Reset))
  
    self.DataBaseFileName   = os.path.abspath(self.DataBaseFileName)
    self.DataBaseFolderName = os.path.dirname(self.DataBaseFileName)
    
 
    if self.Reset:
      # start from scratch - remove old database
      if os.path.exists(self.DataBaseFileName):
        os.remove(self.DataBaseFileName)
   
    # create folder if necessary
    if not os.path.exists(self.DataBaseFolderName):
      os.makedirs(self.DataBaseFolderName)
    
    # Create Database
    self.createDb = sqlite3.connect(self.DataBaseFileName)
    
    # Creates the SQLite cursor that is used to query the database
    self.queryCurs = self.createDb.cursor()
    
    
    if self.Reset:
      # create tables in the database
      self.createTables()

    

  # ---------------------------------------------------------------------  
  def __del__(self):
    # Close database
    print "Close database"
    self.queryCurs.close()  
 
      
    
  # ---------------------------------------------------------------------  
  def commit(self):
    # commit database
    myprint("Commit database")
    self.createDb.commit()

    
  # ---------------------------------------------------------------------  
  def createTables(self):
    # Calls the execute method that will submit a create table SQL Query
    # id will auto increment and doesn't require values to be entered
    myprint("createTables")

    #.............................................................  
    '''
      TABLE BatchList
        id
        LogDate
        MeasLMD
        MeasPath
        ModuleHash
        ReportPath
        ReportTitle
        Result
        SearchClass
        SearchSign
        StartTime
        Type
        NpyFile
                
    '''    

    self.queryCurs.execute('''CREATE TABLE BatchList
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      LogDate DATETIME,
                      MeasLMD  TEXT,
                      MeasPath TEXT,
                      ModuleHash TEXT,
                      ReportPath TEXT,
                      ReportTitle TEXT,
                      Result TEXT,
                      SearchClass TEXT,
                      SearchSign TEXT,
                      StartTime TEXT,
                      Type TEXT,
                      NpyFile BLOB
                      )''')

    #.............................................................  
    '''
      TABLE Reports
        Comment
        MeasFile
        MeasLMD
        Version
        Votes
    ''' 
    
    self.queryCurs.execute('''CREATE TABLE Reports
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      LogDate DATETIME,
                      BatchEntry_id INTEGER,
                      Comment TEXT,
                      MeasFile TEXT,
                      MeasLMD TEXT,
                      Version TEXT,
                      Votes TEXT
                      )''')

    #.............................................................  
    '''
      TABLE Intervals
         Comment
         Lower
         Upper
         Vote
        
    '''
    self.queryCurs.execute('''CREATE TABLE Intervals
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      LogDate DATETIME,
                      ReportEntry_id INTEGER,
                      Comment TEXT,
                      Lower INTEGER,
                      Upper INTEGER,
                      Vote TEXT,
                      tStart REAL, 
                      dura REAL 
                      )''')
    
    
    
    #.............................................................  
    # Annotations
    '''
    TABLE Annotations
    id
    IntervalsEntry_id
    key
    item
    '''

    self.queryCurs.execute('''CREATE TABLE Annotations
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       LogDate DATETIME, 
                       IntervalsEntry_id INTEGER, 
                       key TEXT, 
                       item REAL )''')
    
                      
                      
    # Force the database to make changes with the commit command
    self.createDb.commit()
      
  # ---------------------------------------------------------------------  
  def addBatchEntry(self, BatchEntry):
        
    myprint("addBatchList -start")
    
    LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    MeasLMD     = BatchEntry['MeasLMD']
    MeasPath    = BatchEntry['MeasPath']
    ModuleHash  = BatchEntry['ModuleHash'] 
    ReportPath  = BatchEntry['ReportPath']
    ReportTitle = BatchEntry['ReportTitle'] 
    Result      = BatchEntry['Result'] 
    SearchClass = BatchEntry['SearchClass'] 
    SearchSign  = BatchEntry['SearchSign'] 
    StartTime   = BatchEntry['StartTime']
    Type        = BatchEntry['Type'] 
    NpyFile     = pickle.dumps(BatchEntry['NpyFile'],-1)
      
    self.queryCurs.execute('''INSERT INTO BatchList (LogDate, MeasLMD, MeasPath, ModuleHash, ReportPath, ReportTitle, Result, SearchClass, SearchSign, StartTime, Type, NpyFile)
                              values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',(LogDate, MeasLMD, MeasPath, ModuleHash, ReportPath, ReportTitle, Result, SearchClass, SearchSign, StartTime, Type, sqlite3.Binary(NpyFile)))
    newId = self.queryCurs.lastrowid

    myprint("BatchEntry New rowid = %d"%newId)
   
    return newId

  # ---------------------------------------------------------------------  
  def addReport(self, Report, BatchEntry_id):
        
    myprint("addReport -start")
    
    LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    Comment     = Report['Comment']
    MeasFile    = Report['MeasFile'] 
    MeasLMD     = Report['MeasLMD']
    Version     = Report['Version'] 
    Votes       = Report['Votes'] 
    
        
    self.queryCurs.execute('''INSERT INTO Reports (LogDate, BatchEntry_id, Comment, MeasFile, MeasLMD, Version, Votes)
                              values (?, ?, ?, ?, ?, ?, ?)''',(LogDate, BatchEntry_id, Comment, MeasFile, MeasLMD, Version , Votes))
    
    newId = self.queryCurs.lastrowid

    myprint("addReport: New rowid = %d"%newId)
   
    return newId
    
  # ---------------------------------------------------------------------  
  def addInterval(self, Interval, ReportEntry_id):
        
    myprint("addInterval -start")
          
    LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    Comment     = Interval['Comment']
    Lower       = Interval['Lower']
    Upper       = Interval['Upper'] 
    Vote        = Interval['Vote']
    tStart      = Interval['tStart'] 
    dura        = Interval['dura'] 
    
    self.queryCurs.execute('''INSERT INTO Intervals (LogDate, ReportEntry_id, Comment, Lower, Upper, Vote, tStart, dura)
                              values (?, ?, ?, ?, ?, ?, ?, ?)''',(LogDate, ReportEntry_id, Comment, Lower, Upper, Vote, tStart, dura))
    
    newId = self.queryCurs.lastrowid

    myprint("addInterval: New rowid = %d"%newId)
    
    return newId
 
    
  # ---------------------------------------------------------------------  
  def addAnnotation(self, IntervalsEntry_id, key, item):

    myprint("addAnnotation -start")

    LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    self.queryCurs.execute('''INSERT INTO Annotations (LogDate, IntervalsEntry_id, key, item)
                              values (?, ?, ?, ?)''',(LogDate, IntervalsEntry_id, key, item))
                              
    newId = self.queryCurs.lastrowid

    myprint("addAnnotation: New rowid = %d"%newId)
    
    return newId

  # =====================================================================
  # ---------------------------------------------------------------------  
  def QueryAllBatchList(self):   
    s = '''SELECT * FROM BatchList '''
    return self.QueryBatchList(s)
 
  # ---------------------------------------------------------------------  
  def QueryAllBatchListById(self,id):   
    s = '''SELECT * FROM BatchList WHERE id = '%d' '''%(id)
    return self.QueryBatchList(s)
    
  # ---------------------------------------------------------------------  
  def QueryBatchList(self,s):   
   
    myprint(s)
  
    self.queryCurs.execute(s)

    BatchList = []
      
    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      obj = {}
      obj['id']          = i[0]   # id INTEGER PRIMARY KEY,
      obj['LogDate']     = i[1]   # LogDate DATETIME
      obj['MeasLMD']     = i[2]   # MeasLMD  TEXT,
      obj['MeasPath']    = i[3]   # MeasPath TEXT,
      obj['ModuleHash']  = i[4]   # ModuleHash TEXT,
      obj['ReportPath']  = i[5]   # ReportPath TEXT,
      obj['ReportTitle'] = i[6]   # ReportTitle TEXT,
      obj['Result']      = i[7]   # Result TEXT,
      obj['SearchClass'] = i[8]   # SearchClass TEXT,
      obj['SearchSign']  = i[9]   # SearchSign TEXT,
      obj['StartTime']   = i[10]  # StartTime TEXT,
      obj['Type']        = i[11]  # Type TEXT,
      obj['NpyFile']     = pickle.loads(str(i[12]))  # NpyFile BLOB
      
      # print obj['id'], obj['LogDate'], obj['MeasLMD'], obj['MeasPath'], obj['ModuleHash'], obj['ReportPath'], obj['ReportTitle'],obj['SearchClass'],obj['SearchSign'],obj['StartTime'],obj['Type']   
      
      BatchList.append(obj)
    return BatchList

  # =====================================================================
  # ---------------------------------------------------------------------  
  def QueryAllReports(self):   
    s = '''SELECT * FROM Reports '''
    return self.QueryReports(s)

  # ---------------------------------------------------------------------  
  def QueryAllReportsById(self,id):   
    s = '''SELECT * FROM Reports WHERE id = '%d' '''%(id)
    return self.QueryReports(s)
    
  # ---------------------------------------------------------------------  
  def QueryReports(self,s):   
   
    myprint(s)
  
    self.queryCurs.execute(s)

    ReportList = []
      
    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      obj = {}
      obj['id']             = i[0]   # id INTEGER PRIMARY KEY AUTOINCREMENT,
      obj['LogDate']        = i[1]   # LogDate DATETIME
      obj['BatchEntry_id']  = i[2]   # BatchEntry_id INTEGER,
      obj['Comment']        = i[3]   # Comment TEXT,
      obj['MeasFile']       = i[4]   # MeasFile INTEGER,
      obj['MeasLMD']        = i[5]   # MeasLMD TEXT
      obj['Version']        = i[6]   # Version REAL
      obj['Votes']          = i[7]   # Votes REAL
     
      ReportList.append(obj)
    return ReportList
    
  # =====================================================================
  # ---------------------------------------------------------------------  
  def QueryAllIntervals(self):   
    s = '''SELECT * FROM Intervals '''
    return self.QueryIntervals(s)

  # ---------------------------------------------------------------------  
  def QueryAllIntervalsById(self,id):   
    s = '''SELECT * FROM Intervals WHERE id = '%d' '''%(id)
    return self.QueryIntervals(s)
    
  # ---------------------------------------------------------------------  
  def QueryIntervals(self,s):   
   
    myprint(s)
  
    self.queryCurs.execute(s)

    IntervalList = []
      
    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      obj = {}
      obj['id']             = i[0]   # id INTEGER PRIMARY KEY AUTOINCREMENT,
      obj['LogDate']        = i[1]   # LogDate DATETIME
      obj['ReportEntry_id'] = i[2]   # ReportEntry_id INTEGER,
      obj['Comment']        = i[3]   # Comment TEXT,
      obj['Lower']          = i[4]   # Lower INTEGER,
      obj['Upper']          = i[5]   # Upper INTEGER,
      obj['Vote']           = i[6]   # Vote TEXT
      obj['tStart']         = i[7]   # tStart REAL
      obj['dura']           = i[8]   # dura REAL
               
      # print obj['id'], obj['LogDate'], obj['ReportEntry_id'], obj['Comment'], obj['Lower'], obj['Upper'], obj['Vote'], obj['tStart'], obj['dura']
        
      IntervalList.append(obj)
    return IntervalList

  
  # =====================================================================
  # ---------------------------------------------------------------------  
  def QueryAllAnnotations(self):   
    s = '''SELECT * FROM Annotations '''
    return self.QueryAnnotations(s)

  # ---------------------------------------------------------------------  
  def QueryAllAnnotationsByKey(self,key, rel, item):   
    s = '''SELECT * FROM Annotations WHERE key = '%s' AND item %s '%f' '''%(key,rel,item)
    return self.QueryAnnotations(s)

  
  
  # ---------------------------------------------------------------------  
  def QueryAnnotations(self,s):   
     
    myprint(s)
  
    self.queryCurs.execute(s)

    ret = []

    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      #print i,"\n"
      obj = {}
      obj['id']                 = i[0]
      obj['LogDate']            = i[1]
      obj['IntervalsEntry_id']  = i[2]
      obj['key']                = i[3]
      obj['item']               = i[4]

      #print obj['id'], obj['EventId'] , obj['key'],obj['item']
      ret.append(obj)
      
    return ret
    
  #--------------------------------------------------------------------------------------------
  def IntervalList2BatchList(self, IntervalList):
      # return BatchList = [ [BatchReport_1,ReportList_1], [BatchReport_2,ReportList_2] ... [BatchReport_n,ReportList_n]]
    
      # --------------------------------------------------------------
      # get list of referenced ReportXml -> ReportEntry_id_List
      ReportEntry_id_List = []
      for Interval in IntervalList:
          ReportEntry_id_List.append(Interval['ReportEntry_id'])
      ReportEntry_id_List = unique(ReportEntry_id_List)
  
      # --------------------------------------------------------------
      # built BatchList
      BatchList = []
  
      for ReportEntry_id in ReportEntry_id_List:
        ReportList = []
        Report = self.QueryAllReportsById(ReportEntry_id)[0]
        BatchReport = self.QueryAllBatchListById(Report['BatchEntry_id'])[0]
        Intervals = []
        for Interval in IntervalList: 
          if ReportEntry_id == Interval['ReportEntry_id']:
            Intervals.append(Interval)
        Report['Intervals'] = Intervals
        ReportList.append(Report)
        BatchList.append([BatchReport,ReportList])
        myprint(BatchReport['MeasPath'])

      # sort BatchList by increasing 'MeasPath' of BatchReport
      BatchList.sort(key=lambda a: a[0]['MeasPath'])
      
      return  BatchList   
      
  #--------------------------------------------------------------------------------------------
  def ExtendIntervalList(self, IntervalList):

      for Interval in IntervalList:
          Report = self.QueryAllReportsById(Interval['ReportEntry_id'])[0]
          Batch  = self.QueryAllBatchListById(Report['BatchEntry_id'])[0]
    
          Interval['MeasPath'] = Batch['MeasPath']

      return IntervalList
    
  #--------------------------------------------------------------------------------------------
  def AnnotationList2BatchList(self, AnnotationList):

      IntervalList = []       
      for Annotation in AnnotationList:
          Interval = self.QueryAllIntervalsById(Annotation['IntervalsEntry_id'])[0]
          IntervalList.append(Interval)
    
      return self.IntervalList2BatchList(IntervalList)
      

# ======================================================================
class cBatchReportXmlAccess():


    def __init__(self, MyBatchReportXmlDataBase): 
   
        self.MyBatchReportXmlDataBase = MyBatchReportXmlDataBase
        # ---------------------------------------
        # Attributes of a report element in a batch xml file
        self.BatchReportAttributes = (
            "MeasLMD",
            "MeasPath",
            "ModuleHash",
            "ReportPath",
            "ReportTitle",
            "Result",
            "SearchClass",
            "SearchSign",
            "StartTime",
            "Type")
        
        
        # ---------------------------------------
        # Attributes of a report in ReportXml
        self.ReportAttributes = ( 
            "Comment",
            "MeasFile",
            "MeasLMD",
            "Version",
            "Votes")
        
        # ---------------------------------------
        # Attributes of an Interval in ReportXml    
        self.IntervalAttributes = (
            "Comment", 
            "Lower", 
            "Upper", 
            "Vote")
   
        pass
  
    #--------------------------------------------------------------
    def read_NpyFile(self, ReportXmlFileName):
        # read a numpy array file related to a given ReportXML file

        NpyFile = None
   
        NpyFileName = os.path.splitext(ReportXmlFileName)[0]+".npy"
        if os.path.exists(NpyFileName):
             NpyFile = np.load(NpyFileName)
             #print ReportDict['time']

        return NpyFile

    #--------------------------------------------------------------
    def write_NpyFile(self, ReportXmlFileName,NpyArray):
        # write numpy array
        
        NpyFileName = os.path.splitext(ReportXmlFileName)[0]+".npy"
        np.save(NpyFileName,NpyArray)
  
        return
  
  
    #--------------------------------------------------------------
    def read_ReportXmlFile(self, ReportXmlFileName):
        myprint("read_ReportFile()")
  
        # ----------------------------------------
        # parse XML File -> dom
        file = open(ReportXmlFileName, "r")
        dom = xml.dom.minidom.parse(file)
        file.close()

        ReportList = []
        for Report in dom.getElementsByTagName("Report"):
            OneReportDict = {}
            for Attr in self.ReportAttributes:
                OneReportDict[Attr] = Report.getAttribute(Attr)
                Intervals = Report.getElementsByTagName("Interval")
                IntervalList = []
                for Interval in Intervals:
                    IntervalElement = {} 
                    for IntervalAttr in self.IntervalAttributes:
                        IntervalElement[IntervalAttr] = Interval.getAttribute(IntervalAttr)
                    IntervalList.append(IntervalElement)
                OneReportDict['Intervals'] = IntervalList
            ReportList.append(OneReportDict)  
  
        return ReportList

    #============================================================
    def write_ReportXMLFile(self, ReportXMLFileName, ReportList):
  
        Document = xml.dom.minidom.Document()
  
        for Report in ReportList:
            
            # Report
            ReportElement = Document.createElement('Report')
            for Attr in Report.keys():
                if Attr in self.ReportAttributes:
                    ReportElement.setAttribute(Attr, str(Report[Attr]))
                    #print "Report<%s>= %s" %(Attr, Report[Attr])
    
            # Intervals
            IntervalList = Report['Intervals']
            for Interval in IntervalList:
                IntervalElement = Document.createElement('Interval')
                for Attr in Interval.keys():
                    if Attr in self.IntervalAttributes:
                        #print "Interval <%s>= %s" %(Attr, Interval[Attr])
                        IntervalElement.setAttribute(Attr, str(Interval[Attr]))
                ReportElement.appendChild(IntervalElement) 
          
            Document.appendChild(ReportElement)
    
        #print ReportXMLFileName 
        Dir, Spam = os.path.split(ReportXMLFileName)
        #print Dir, Spam
        if Dir and not os.path.exists(Dir):
            os.makedirs(Dir)
        open(ReportXMLFileName, 'w').write(Document.toprettyxml())
      
        return

    #============================================================
    def BatchXmlFile2DB(self, BatchXMLFileName, NewRepDir=None):
        myprint("BatchXmlFile2DB()")
  
        # open and parse xml file
        file = open(BatchXMLFileName, "r")
        dom = xml.dom.minidom.parse(file)
        file.close()


        # ---------------------------------------------------------  
        # BatchEntry 
        for Report in dom.getElementsByTagName("Report"):
        
            BatchEntry = {}
    
            # Attribute
            for Attr in self.BatchReportAttributes:
                BatchEntry[Attr] = Report.getAttribute(Attr)
                #print "%s %s" %(Attr, Report.getAttribute(Attr))
    
            ReportXMLFileName = BatchEntry['ReportPath']
    
            if NewRepDir:
                ReportXMLFileName = os.path.join(NewRepDir,os.path.basename(ReportXMLFileName))
    
            # npy file
            BatchEntry['NpyFile'] = self.read_NpyFile(ReportXMLFileName) 
            time = BatchEntry['NpyFile']    
    
            # insert into DB
            BatchEntry_id = self.MyBatchReportXmlDataBase.addBatchEntry(BatchEntry)
    
            # read ReportXmlFile
            ReportList = self.read_ReportXmlFile(ReportXMLFileName)
           
            for Report in ReportList:
                ReportEntry_id = self.MyBatchReportXmlDataBase.addReport(Report, BatchEntry_id)
                for Interval in Report['Intervals']:
                    Interval['tStart'] = time[int(Interval['Lower'])]
                    Interval['dura']   = time[int(Interval['Upper'])] - time[int(Interval['Lower'])]
        
                    IntervalEntry_id = self.MyBatchReportXmlDataBase.addInterval(Interval, ReportEntry_id)
  

        return  
  
  
    #============================================================
    def write_BatchXmlFile(self, BatchXmlFileName, BatchList, NewRepDir=None, RepDirRelative=True):
  
        myprint("write_BatchXmlFile()")
  
        MagicBatchXml_Verion = '1.37'
   
        # ---------------------------------------------------
        # create XML document
        Document = xml.dom.minidom.Document()
        root     = Document.createElement('root')
        root.setAttribute('Version',MagicBatchXml_Verion)
        Document.appendChild(root)

    
        for BatchReport,ReportList in BatchList: 

          # ReportFileName
          if NewRepDir:
            if RepDirRelative:
              ReportFileName = os.path.join(os.path.dirname(BatchXmlFileName), NewRepDir, os.path.basename(BatchReport['ReportPath']))
            else:
              # NewRepDir is an absolute path
              ReportFileName = os.path.join(NewRepDir,os.path.basename(BatchReport['ReportPath']))
          else:
            ReportFileName = BatchReport['ReportPath']
        
          # create report directory
          Dir = os.path.dirname(ReportFileName)
          if Dir and not os.path.exists(Dir):
              os.makedirs(Dir)
      
          # write report file  
          self.write_ReportXMLFile(ReportFileName, ReportList)
    
          # write npy file
          self.write_NpyFile(ReportFileName,BatchReport['NpyFile'])

    
          # create report element in batch xml file
          ReportElement = Document.createElement('Report')
          for Attr in BatchReport.keys():
              if Attr in self.BatchReportAttributes:
                  ReportElement.setAttribute(Attr,str(BatchReport[Attr]))
          root.appendChild(ReportElement)

        # write Batch Xml file  
        Dir = os.path.dirname(BatchXmlFileName)
        if Dir and not os.path.exists(Dir):
            os.makedirs(Dir)
        open(BatchXmlFileName, 'w').write(Document.toprettyxml())
   
        return

