

import os
import sys, traceback

#==========================================================================================    
def ExpandFilename(PathName,BaseName):
    '''
       return list of files beginning with BaseName in the given folder PathName
       
       example: FileName_list = kbtools.ExpandFilename(r'\myFolder',r'EvalJ1939_results')
           \myFolder includes:
                 EvalJ1939_results_2014-07-07.xls
                 |<--BaseName--->|
            
            return FileName_list=[EvalJ1939_results_2014-07-07.xls]
    '''
    try:
        DirList = os.listdir(PathName)
        DirList.sort()
    
        FileName_list = []
    
        for File in DirList:
            if File.startswith(BaseName):
                FileName_list.append(os.path.join(PathName,File))
            
        return FileName_list
    except WindowsError:
        print "ExpandFilename - WindowsError"
        traceback.print_exc(file=sys.stdout)
        return []
#==========================================================================================    
