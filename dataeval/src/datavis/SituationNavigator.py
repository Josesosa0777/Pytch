import pyglet_workaround  # necessary as early as possible (#164)

from operator import attrgetter

import numpy

import measparser
from Synchronizer import iSynchronizable
from PlotNavigator import cPylabNavigator

class cSituationNavigator(cPylabNavigator, iSynchronizable):
     '''
     Visualizes actual driving Situations.
     '''
     def __init__(self, sms, title='', figureNr=None):
        
        cPylabNavigator.__init__(self, 'SituationNavigator', 100, '')
        #------------------------------------------
        #convert all Indices to same scaletime
        #------------------------------------------
        for sm  in sms:
          if len(sm.intervallists.values())>0:
             self.base_intervallist=sm.intervallists.values()[0]
             self.scaletime=self.base_intervallist.Time
             self.len_scaletime=len(self.scaletime)
             break
        
        for sm in sms:
          for key in sm.intervallists.iterkeys():
            sm.intervallists[key]=self.base_intervallist.convertIndices(sm.intervallists[key])
            try:
              sm.reliances[key]=measparser.cSignalSource.rescale(sm.intervallists[key].Time, sm.reliances[key], self.scaletime)[1]
            except KeyError:
              sm.reliances[key]=numpy.repeat(numpy.array([1.]),self.len_scaletime)
        #------------------------------------------
        #delete multiple types
        #------------------------------------------
        self.types=[]
        for sm in sms:
          self.types.append(sm.type)
        self.types = list(set(self.types))
        #------------------------------------------
        #make classes by type
        #------------------------------------------
        self.sms={}
        for type in self.types:
          self.sms[type]=[]
        for sm in sms:
          for type in self.types:
            if sm.type==type:
              self.sms[type].append(sm)
        #------------------------------------------
        #calculate weight*reliance
        #------------------------------------------
        for type in self.types:
          for sm in self.sms[type]:
            sm.reliance_mult_weight={}
            for key in sm.reliances.iterkeys():
              sm.reliance_mult_weight[key]=sm.reliances[key]*sm.weight
        #------------------------------------------
        #Visualize Intervals over Time for different types
        #------------------------------------------
        self.plotsignals={}
        self.signals = []
        for type in self.types:
          self.plotsignals[type]=[]
          for sm in self.sms[type]:
            for key in sm.intervallists.iterkeys():
              self.plotsignals[type].append(sm.name+"-"+key)
              self.plotsignals[type].append((sm.calcArrayOfIntervals(self.scaletime, key)))
        # for key in self.plotsignals.iterkeys():
          # self.addsignal(*self.plotsignals[key])
        #------------------------------------------
        #self.fig = pl.figure(55,figsize=(4,6))
        self.fig.show()
        
     def getplotsignals(self):
        return self.plotsignals
        
     def seek(self, time):
     
        self.Time   = time
        self.Actsms = {}

        Index = max(0, self.scaletime.searchsorted(self.Time, side='right') - 1)
        
        for type in self.types:
          self.Actsms[type]=[]
          for sm in self.sms[type]:
            for key in sm.intervallists.iterkeys():
              try:
                sm.intervallists[key].findInterval(Index)
                self.Actsms[type].append(cActsms(sm.name,sm.level,key,sm.reliance_mult_weight[key][Index]))
              except ValueError:
                pass
        self.fig.clear()
        self.text = {}
        text=''
        for type in self.types:
          self.text[type]=''
          #sort the all instances Actsm in Actsms[key] by relecance of attributes in order
          Actsms=sorted(self.Actsms[type], key=attrgetter('level','reliance_mult_weight'))
          for Actsm in Actsms:
            self.text[type]+="%s\n(%s-%s)\n"%(Actsm.key,Actsm.level,Actsm.reliance_mult_weight)
          if self.text[type]:
            text+='\n.:|%s|:.\n%s'%(type,self.text[type])
        self.fig.text(0.5,0.5,text,va='center',ha='center')
        return
        
     
     def start(self):
       self.seek(0.0)
       pass

     def show(self):
       self.fig.show()
       return
     

            
class cActsms():
    '''
    Instance representing Actual "S"ituation"M"odule"S".
    Important for sorting and displaying in cSituationNavigator
    '''
    def __init__(self, name, level, key, reliance_mult_weight):
        
        """
        :Parameters:
          self.name: string
            name of the module
          self.type: string
            type of the module. Types are basic classes of situations wich can exists side by side
          self.level: float
            level of the module. Top level module always overwrite requests of low level modules without exclusion
          self.key: string
            represents actual Situation for type
          self.reliances_mult_weight: dict
            dict(key: <string>= value: ndarray)
            key represents actual Situation for type. Value represents reliance multiplied with module.weight as float value over time.
        """
        
        self.name=name
        self.level=level
        self.key=key
        self.reliance_mult_weight=reliance_mult_weight
    def __repr__(self):
        return repr((self.name, self.level, self.key, self.reliance_mult_weight))
        
        
        
class cSituationModule():
    '''
    interface for Situation modules.
    '''
    def __init__(self, name, type, level=0., weight=1., intervallists={}, reliances={}):
        
        """
        :Parameters:
          self.name: string
            name of the module
          self.type: string
            type of the module. Types are basic classes of situations wich can exists side by side
          self.level: float
            level of the module. Top level module always overwrite requests of low level modules without exclusion
          self.weight: float
            weight of whole module. Float value represention an reliance factor for whole module. Multiplied with reliance of Interval later on.
          self.intervallists: dict
            dict(key: <string>= value: <cIntervalList>)
            key represents actual Situation for type. Value is intervallist for this key (Situation)
          self.reliances: dict
            dict(key: <string>= value: ndarray)
            key represents actual Situation for type. Value represents reliance float value over time.
            
        :Sorting in cSituationNavigator:
            :types: All different types represent different Situations existing side by side
               :type: In one type all Situations are sorted:
                      primary: level
                      secondary: reliance*weight
        """
        
        self.name=name
        self.type=type
        self.level=level
        self.weight=weight
        self.intervallists=intervallists
        self.reliances=reliances
    
    def __repr__(self):
        return repr((self.name, self.type, self.level, self.weight, self.intervallists, self.reliances))
    
    def calcArrayOfIntervals(self, scaletime, key):
        '''
        Creates Signals representing the Intervals.
        value: 0: Interval doesn't exist
               !=0: Interval exists. Value equal to self.level+1
        '''
        """
        :Returns:
          scaletime: ndarray
          array: ndarray
        """
        array = numpy.zeros_like(scaletime)
        for lower, upper in self.intervallists[key]:
          array[lower:upper]=self.level+1
        
        return scaletime, array
        
if __name__ == '__main__':
  import sys
  import optparse
  
  import numpy
  from PySide import QtGui, QtCore
  
  import measproc
  
  parser = optparse.OptionParser()
  parser.add_option('-p', '--hold-navigator', 
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
                    
  opts, args = parser.parse_args()
  
  app = QtGui.QApplication([])
  sms = []
  
  t = numpy.arange(0, 20, 0.01)
  y = numpy.sin(t)
  z = numpy.cos(t)
  
  i1 = measproc.cEventFinder.compExtSigScal(t, y, measproc.less, 0.5)
  i2 = measproc.cEventFinder.compExtSigScal(t, z, measproc.greater, 0.5)
  
  intervals1 = {'i1' : i1, }
  intervals2 = {'i2' : i2, }
  
  sms.append(cSituationModule('Name1', 'Type1', intervallists=intervals1))
  sms.append(cSituationModule('Name2', 'Type2', intervallists=intervals2))
  SN = cSituationNavigator(sms)
  SN.start()
  SN.seek(12.5)
  if opts.hold_navigator:
    sys.exit(app.exec_())