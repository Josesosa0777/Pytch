
# python standard imports
import os
import time
import sqlite3

# Utilities_DAS specific imports
import kbtools


# ===========================================================================================
def StartDB(DataBaseFileName, Reset=False, verbose=False):

  if verbose:
    print "StartDB", DataBaseFileName
    
  DataBaseFileName = os.path.abspath(DataBaseFileName)
  DataBaseFolderName = os.path.dirname(DataBaseFileName)
 
  if verbose:
    print "DataBaseFileName: ", DataBaseFileName
    print "DataBaseFolderName: ", DataBaseFolderName
 
  if Reset:
    # start from scratch - remove old database
    if os.path.exists(DataBaseFileName):
      os.remove(DataBaseFileName)
   
  if not os.path.exists(DataBaseFolderName):
    # create Tex-Generation Folder
    os.makedirs(DataBaseFolderName)
  
  # open new database
  myKbDataBase = kbtools.cKbDataBase(DataBaseFileName,verbose=verbose)
  
  if Reset:
    # create tables in the database
    myKbDataBase.createTables()

  # inject reference to database into Hunt4Event
  kbtools.cHunt4Event.SetKBDataBase(myKbDataBase,verbose=verbose)

#--------------------------------------------------------------------------------------------
class cKbDataBase():

  # ---------------------------------------------------------------------  
  def __init__(self, DataBaseFileName, verbose=False):
    
    self.DataBaseFileName = DataBaseFileName
    self.verbose = verbose
    
    if self.verbose:
      print "Connect database"
   
    # Create Database
    self.createDb = sqlite3.connect(self.DataBaseFileName)
    
    # Creates the SQLite cursor that is used to query the database
    self.queryCurs = self.createDb.cursor()

  # ---------------------------------------------------------------------  
  def __del__(self):
    # Close database
    if self.verbose:
      print "Close database"
    self.queryCurs.close()

  # ---------------------------------------------------------------------  
  def createTables(self):
    # Calls the execute method that will submit a create table SQL Query
    # id will auto increment and doesn't require values to be entered
    if self.verbose:
      print "createTables"
    self.queryCurs.execute('''CREATE TABLE events
                      (id INTEGER PRIMARY KEY, LogDate DATETIME, path TEXT, file TEXT, type TEXT, description TEXT, start REAL, dura REAL, HuntType TEXT, Par0 REAL)''')

    '''
      TABLE events
        id
        path
        file
        type
        start
        dura
    '''        
    '''
          obj['FullPath']    = Source.FileName
          obj['FileName']    = os.path.basename(Source.FileName)
          obj['description'] = self.Description
          obj['interval']    = Interval
          obj['t_start']     = t_start
          obj['t_stop']      = t_stop
          obj['dura']        = dura
    '''
    
    # Annotations
    self.queryCurs.execute('''CREATE TABLE annotations
                      (id INTEGER PRIMARY KEY, LogDate DATETIME, event_id INTEGER, key TEXT, item REAL )''')
    
    '''
    TABLE annotations
    id
    event_id
    key
    item
    '''
                      
                      
    # Force the database to make changes with the commit command
    self.createDb.commit()
  # ---------------------------------------------------------------------  
  def addEventList(self, EventType, EventList):
    
    if self.verbose: 
      print "addEventList -start EventType %s"%EventType
    
    for Event in EventList:
      LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
      path        = Event['FullPath'] 
      file        = Event['FileName'] 
      type        = EventType
      description = Event['description'] 
      start       = Event['t_start'] 
      dura        = Event['dura']
      HuntType    = Event['HuntType']
      Par0        = Event['Par0']
    
      if self.verbose:
        print "addEventList", path, file, type, description, start, dura
      self.queryCurs.execute('''INSERT INTO events (LogDate, path, file, type, description, start, dura, HuntType,Par0)
                              values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',(LogDate, path, file, type, description, start, dura, HuntType,Par0))
                              
    # Force the database to make changes with the commit command
    self.createDb.commit()

    if self.verbose:
      print "addEventList -end"


  # ---------------------------------------------------------------------  
  def addAnnotation(self, event_id, key, item):
  
    LogDate     = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    self.queryCurs.execute('''INSERT INTO annotations (LogDate, event_id, key, item)
                              values (?, ?, ?, ?)''',(LogDate, event_id, key, item))
    # Force the database to make changes with the commit command
    self.createDb.commit()

  # ---------------------------------------------------------------------  
  def QueryAllEvents(self):   
    s = '''SELECT * FROM events '''
    return self.QueryEvents(s)
 
  # ---------------------------------------------------------------------  
  def QueryAllEventsFromType(self,type):   
    s = '''SELECT * FROM events WHERE type = '%s' '''%(type)
    return self.QueryEvents(s)
    
  # ---------------------------------------------------------------------  
  def QueryEvents(self,s):   
   
    if self.verbose:
      print s
  
    self.queryCurs.execute(s)

    ret = []
    if self.verbose:
      print "Query 1:"
      
    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      #print i,"\n"
      obj = {}
      obj['EventId']     = i[0]
      obj['LogDate']     = i[1]
      obj['FullPath']    = i[2]
      obj['FileName']    = i[3]
      obj['EventType']   = i[4]
      obj['description'] = i[5]
      obj['t_start']     = i[6]
      obj['dura']        = i[7]
      obj['HuntType']    = i[8]
      obj['Par0']        = i[9]

      if self.verbose:
        print obj['EventId'], obj['FullPath'], obj['FileName'], obj['EventType'], obj['description'], obj['t_start'], obj['dura'],obj['HuntType'],obj['Par0']
      
      ret.append(obj)
    return ret
    
  # ---------------------------------------------------------------------  
  def QueryAllAnnotationsFromEvent(self,EventId):   
    s = '''SELECT * FROM annotations WHERE event_id = '%s' '''%(EventId)
    
    if self.verbose:
      print s
  
    self.queryCurs.execute(s)

    ret = []

    if self.verbose:
      print "Query 1:"
      
    # Cycles through the tuple and prints the entries to screen
    for i in self.queryCurs:
      #print i,"\n"
      obj = {}
      obj['id']       = i[0]
      obj['LogDate']  = i[1]
      obj['EventId']  = i[2]
      obj['key']      = i[3]
      obj['item']     = i[4]

      print obj['id'], obj['EventId'] , obj['key'],obj['item']
      ret.append(obj)
      
    return ret

#--------------------------------------------------------------------------------------------
def main():

  if os.path.exists(DataBaseFileName):
    os.remove(DataBaseFileName)
    
  myEventDataBase = cKbDataBase(DataBaseFileName)
    
  myEventDataBase.createTables()
  
  # Add tracks to the database
  myEventDataBase.addEvent("Pfad1", "File1", "Warn", 1.0, 0.3)
  myEventDataBase.addEvent("Pfad1", "File2", "Brake", 2.0, 0.3)
  myEventDataBase.addEvent("Pfad1", "File3", "Warn", 3.0, 0.3)
  myEventDataBase.addEvent("Pfad1", "File4", "Brake", 4.0, 0.3)
  myEventDataBase.addEvent("Pfad1", "File5", "Warn", 5.0, 0.3)
  
  EventList = myEventDataBase.QueryAllEventsFromType("Brake")  
 
  n = 10
  for Event in EventList:
    print Event
    myEventDataBase.addAnnotation(Event['EventId'],'v_ego',3.6*n)
    myEventDataBase.addAnnotation(Event['EventId'],'sit',3*n)
    n=n+10
 
 
  myEventDataBase.QueryAllAnnotationsFromEvent(2)
  myEventDataBase.QueryAllAnnotationsFromEvent(4)
 
 
 
  return
  
  typ = 'Sensor1'
  min_dura = 3.0
  limit_start_idx = 1   # index start by 0
  limit_n = 2
  s = '''SELECT id, typ, start, stop, stop-start as dura FROM tracks WHERE typ = '%s' AND dura > %f
         ORDER by dura DESC LIMIT %d , %d '''%(typ,min_dura,limit_start_idx,limit_n)

  myEventDataBase.Query(s)
 
    
    
    
  
  typ = 'Sensor2'  
  start = 2.5
  stop  = 6.5  
  
  # Track1 enthaelt Track2               Track1.start <= Track2.start AND Track2.stop <= Track1.stop
  # Track2 enthaelt Track1               Track2.start <= Track1.start AND Track1.stop <= Track2.stop
  # Track1 ueberlappt Anfang von Track2  Track1.start <= Track2.start AND Track1.stop <= Track2.stop
  # Track2 ueberlappt Anfang von Track1  Track2.start <= Track1.start AND Track2.stop <= Track1.stop
  
  s = '''SELECT * FROM tracks WHERE start >= '%f' AND stop <= %f'''%(start, stop)
  
  s = '''SELECT * FROM tracks WHERE typ = '%s' AND
         (%f    <= start  AND stop <= %f  
         OR  start <= %f     AND %f   <= stop 
         OR  %f    <= start  AND %f   <= stop AND start <= %f
         OR  start <= %f     AND stop <= %f AND  %f <= stop)    '''%(typ,start, stop,start, stop,start, stop, stop, start, stop, start)
  
  myEventDataBase.Query(s)

  '''
  print s
  queryCurs.execute(s)

  print "Query 2:"
  # Cycles through the tuple and prints the entries to screen
  for i in queryCurs:
    print "\n"
    for j in i:
      print j
  '''
  
# =================================================================================================
if __name__ == "__main__": 
  main()


