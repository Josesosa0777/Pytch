"""
:Organization: Knorr-Bremse SfN GmbH Budapest, Schwieberdingen T/CES3.2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\scan4handles.py
'''

import os
import unittest
import time


import kbtools


#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #---------------------------------------------------------------------------------------------------
  def create_todo_for_TC001(self, todo_folder):
     ''' 10 todo script generated; script no. 3, 6 and no. 8 will fail 
           - script no. 1 will delete script no. 3 -> use case: user will delete a script after batch server has started
           - script no. 6 and no. 8 will cause a error while running 
     '''
     
     N = 10
     for k in xrange(0,10):
        print "Create %d"%k
        FileName = os.path.join(todo_folder,'todo%d.py'%k)
        print FileName
        f = open(FileName,'wt')
     
        # script no. 6 and 8 will fail
        if (k==6) or (k==8):
            f.write('something is wrong%d\n'%k)
  
        f.write('import os\n')
        f.write('print os.getcwd()\n')
  
        if (k==1):
            f.write('FileName = r"%s"\n'%r'.\Python_batch_process\todo\todo3.py')
            f.write('print FileName, os.path.exists(FileName)\n')
            f.write('os.remove(FileName)\n')
            f.write('print FileName, os.path.exists(FileName)\n')

        f.write('print %d\n'%k)
        f.close()
        time.sleep(0.1)    # this is to have different file creation times

  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' good situation '''
    
    # Batch Server is local relative to this file for this testcase !!!
    
    # define pathes
    PathName_root  = os.path.join(os.path.curdir,'Python_batch_process')
    todo_folder    = os.path.join(PathName_root,'todo')
    done_folder    = os.path.join(PathName_root,'done')
    fail_folder    = os.path.join(PathName_root,'fail')
    Summary_folder = os.path.join(PathName_root,'Summary')
    
    # --------------------------------------------------
    # clean up
    if os.path.exists(PathName_root):
      
      # if the path and if the respective folder exists, then delete the respective folder.
      # --------------------------------------------------
      # todo folder
      if os.path.exists(todo_folder):
        kbtools.delete_files(todo_folder,'.py')
        os.rmdir(todo_folder)
      # --------------------------------------------------
      # done folder
      if os.path.exists(done_folder):
        kbtools.delete_files(done_folder,'.py') 
        os.rmdir(done_folder)
      # -------------------------------------------------- 
      # fail folder
      if os.path.exists(fail_folder): 
        kbtools.delete_files(fail_folder,'.py')
        os.rmdir(fail_folder)
      # --------------------------------------------------
      # sumamry folder
      if os.path.exists(Summary_folder):  
        print "Summary_folder", Summary_folder
        kbtools.delete_files(Summary_folder,['.log','.txt'])
        os.rmdir(Summary_folder)
      # --------------------------------------------------
      os.rmdir(PathName_root)
      
      # --------------------------------------------------
      # check if files and folder are really removed
      Test_passed = True
      if os.path.exists(PathName_root):    Test_passed = False
      self.assertTrue(Test_passed)
    
    # ---------------------------------------------------------------    
    # prepare BatchServer
    myBatchServer = kbtools.cBatchServer(PathName_root)
    
    # create todo's 
    self.create_todo_for_TC001(todo_folder)
    
    # process todo's
    myBatchServer.single_run()
    
    # --------------------------------------------------------------------------------------
    # check results
    Test_passed = True
    for k in xrange(0,10):
      # check if scripts has been removed from folder todo
      if os.path.exists(os.path.join(todo_folder,'todo%d.py'%k)): Test_passed = False

      if (k==6) or (k==8):
        # check if not successful run scripts are moved to folder fail
        if not os.path.exists(os.path.join(fail_folder,'todo%d.py'%k)): Test_passed = False
      elif (k==3):
        # check was deleted and not exists any more
        if os.path.exists(os.path.join(fail_folder,'todo%d.py'%k)): Test_passed = False
      else:
        # check if successful run scripts are moved to folder done
        if not os.path.exists(os.path.join(done_folder,'todo%d.py'%k)): Test_passed = False
    
       
    # report results
    self.assertTrue(Test_passed) 


  #------------------------------------------------------------------------  

    
#========================================================================================
if __name__ == "__main__":
  print 'unittest for BatchServer'
  unittest.main()
  

