

import os
import datetime
import shutil
import codecs

import numpy as np

#==========================================================================================
class CDiademDatWriter(object):

    def __init__(self):
        
        self.SiglNameList = []
        self.SignalDict = {}
        
        self.SigCnt = 0
        
        # 201,Erfassungskanal
        self.datEntries = { '200'  : 'chName',
                        '202'  : 'unit',
                        '210'  : 'channelType',
                        '211'  : 'sourceFile',
                        '213'  : 'dataStruct',
                        '214'  : 'dataType',
                        '220'  : 'size',
                        '221'  : 'channelPos',
                        '222'  : 'binBlock',
                        'null' : 'startPos',
                        '240'  : 'startVal',
                        '241'  : 'stepVal',
                        '250'  : 'minVal',
                        '251'  : 'maxVal'}
    
    # ------------------------------------------------------------
    def addTimeChannelIMPLICIT(self, SigName='Zeit'):
        '''
           register an implicit time channel
           
           A implicit time channel is specified by its parameters
        
        '''
    
        SigAttr ={}
        SigAttr['chName'] = SigName   # 200
        
        SigAttr['unit'] = 's'     # 202
        SigAttr['channelType'] = 'IMPLICIT' # 210
        
        SigAttr['size'] = 0   # 220
        
               
        SigAttr['startVal'] = 0.00000000  # 240                
        SigAttr['stepVal']  = 1.00000000  # 241

        # minimum and maximum value
        SigAttr['minVal'] = 0  # 250                
        SigAttr['maxVal'] = 0  # 251         
         
        SigAttr['TimeOrNumeric'] =  'Numeric'  # 260
             
        SigAttr['252'] =  'NO'  # 260
    
        # ------------------------------------
        # register
        self.SiglNameList.append(SigName)
        self.SignalDict[SigName] = SigAttr
        
    # ------------------------------------------------------------
    def putTimeChannelIMPLICIT(self, SigName, N):
        '''
           extend the implicit Time Channel by N samples
         
        '''
        SigAttr = self.SignalDict[SigName]
        SigAttr['size'] = SigAttr['size']+N
        SigAttr['maxVal'] = SigAttr['size']
        
    # ------------------------------------------------------------
    def addChannel(self, SigName,SigType,SigUnit=""):
        '''
            register an channel
            SigName : str name of the channel
            SigType : 'Time' or 'Numeric'
          
        '''
    
        SigAttr ={}
        SigAttr['chName'] = SigName   # 200
        
        SigAttr['unit'] = SigUnit     # 202
        SigAttr['channelType'] = 'EXPLICIT' # 210
        SigAttr['sourceFile'] = 'data%d.W16'%self.SigCnt # 211
        SigAttr['dataStruct'] = 'CHANNEL'   # 213
        SigAttr['dataType'] = 'REAL64'   # 214
        SigAttr['size'] = 0   # 220
        SigAttr['channelPos'] = 1   # 221
               
        SigAttr['startVal'] = 0.00000000  # 240                
        SigAttr['stepVal'] = 1.00000000  # 241  
        
        # minimum and maximum value
        SigAttr['minVal'] = np.inf  # 250                
        SigAttr['maxVal'] = -np.inf  # 251                
              
        if SigType == 'Time':        
            SigAttr['chDescprition'] = 'dcnvt-timeaxis'   # 201        
            SigAttr['TimeOrNumeric'] =  'Time'  # 260    
        elif SigType == 'Numeric':
            SigAttr['chDescprition'] = 'Erfassungskanal'   # 201
            SigAttr['TimeOrNumeric'] =  'Numeric'  # 260
    
        # ---------------------------------------------
        # register
        self.SigCnt = self.SigCnt+1
        self.SiglNameList.append(SigName)
        self.SignalDict[SigName] = SigAttr
        
        
        # ---------------------------------
        # delete binary file 
        if os.path.exists(SigAttr['sourceFile']):
            os.remove(SigAttr['sourceFile'])
        
        
        
    # ------------------------------------------------------------
    def putChannel(self, SigName,SigValue):
        '''
        
            put SigValue into the Channel 'SigName'
        
        '''
    
        SigAttr = self.SignalDict[SigName]
        
        # convert to double REAL64
        a = np.array(SigValue,'float64')
        
        # write to file
        output_file = open(SigAttr['sourceFile'],"ab")
        a.tofile(output_file)
        output_file.close()
        
        # update signal attributes
        SigAttr['size'] = SigAttr['size']+len(a)
        SigAttr['minVal'] = min(SigAttr['minVal'],np.min(a) )              
        SigAttr['maxVal'] = max(SigAttr['maxVal'],np.max(a) )                
        
        return len(a)
   
    # ------------------------------------------------------------
    def save(self,PathFileName):
    
        # create Folder if necessary 
        FolderName = os.path.dirname(PathFileName)
        print "FolderName",FolderName
        if FolderName:
            if not os.path.exists(FolderName):
                os.makedirs(FolderName)
    
        # -----------------------------------
        # write Header File
        self._WriteHeaderFile(PathFileName)
        
        # ------------------------------------
        # copy binrary files
        for k in range(self.SigCnt):
            FileName = 'data%d.W16'%k
            shutil.move(FileName, os.path.join(FolderName,FileName))
            
        
    # ------------------------------------------------------------
    def _WriteHeaderFile(self, HeaderFileName):
    
        #fout = open(HeaderFileName,"wt")
        fout = codecs.open(HeaderFileName,'w','utf-8')
    
        # Preanble
        fout.write("DIAEXTENDED  {@:ENGLISH\n")
        
        # globale header
        self._WriteGLOBALHEADER(fout)
        
        # channel headers
        for SigName in  self.SiglNameList:
            SigAttr = self.SignalDict[SigName]
            self._WriteCHANNELHEADER(fout,SigAttr)
        
        fout.close()
        
    # ------------------------------------------------------------
    def _WriteGLOBALHEADER(self, fout):
         
        fout.write("\n#BEGINGLOBALHEADER\n")
        fout.write("  1,WINDOWS 32Bit\n")
        fout.write("  2,Knorr-Bremse Python Tool Chain - Ulrich Guecker\n")
        fout.write("101,\n")
        fout.write("103,Knorr-Bremse Python Tool Chain - Ulrich Guecker\n")
        tp = datetime.datetime.now()
        fout.write("104,%s\n"%tp.strftime("%Y-%m-%d"))
        fout.write("105,%s\n"%tp.strftime("%H:%M:%S"))
        fout.write("111,9.900000e+034\n")
        fout.write("112,High -> Low\n")
        fout.write("#ENDGLOBALHEADER\n")

    # ------------------------------------------------------------
    def _WriteCHANNELHEADER(self, fout, SigAttr):
   
        fout.write("\n#BEGINCHANNELHEADER\n")
        
        if 'chName' in SigAttr:
            fout.write("200,%s\n"%SigAttr['chName'])
        if 'chDescprition' in SigAttr:
            fout.write("201,%s\n"%SigAttr['chDescprition'])
        if 'unit' in SigAttr:
            fout.write(u"202,%s\n"%SigAttr['unit'])
        if 'channelType' in SigAttr:
            fout.write("210,%s\n"%SigAttr['channelType'])
        if 'sourceFile' in SigAttr:
            fout.write("211,%s\n"%SigAttr['sourceFile'])
        if 'dataStruct' in SigAttr:
            fout.write("213,%s\n"%SigAttr['dataStruct'])
        if 'dataType' in SigAttr:
            fout.write("214,%s\n"%SigAttr['dataType'])
        if 'size' in SigAttr:
            fout.write("220,%d\n"%SigAttr['size'])
        if 'channelPos' in SigAttr:
            fout.write("221,%d\n"%SigAttr['channelPos'])
        if 'startVal' in SigAttr:
            fout.write("240,%f\n"%SigAttr['startVal'])
        if 'stepVal' in SigAttr:
            fout.write("241,%f\n"%SigAttr['stepVal'])
        if 'minVal' in SigAttr:
            fout.write("250,%f\n"%SigAttr['minVal'])
        if 'maxVal' in SigAttr:
            fout.write("251,%f\n"%SigAttr['maxVal'])
        if '252' in SigAttr:
            fout.write("252,%s\n"%SigAttr['252'])
        if 'TimeOrNumeric' in SigAttr:
            fout.write("260,%s\n"%SigAttr['TimeOrNumeric'])
            
        fout.write("#ENDCHANNELHEADER\n")

