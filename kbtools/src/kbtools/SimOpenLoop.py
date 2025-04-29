'''
    Interface for Conducting an Open Loop Simulation

    A simulation is open loop if the calculated outputs of the simulation influence the inputs signals to the simulation; 
    there is no feedback; there is no loop.
    Measured data can be used as input to an open loop simulation.
    
    For example algorithms generating a warning or estimating something can be simulated in open loop, whereas algorithms
    like the emergency brake phase of an AEBS algorithm have to be simulated close loop.
    For a closed loop simulation the calculated output are used to calculated the new input values for a the simulation using a plant model.
    
    2014-09-29
    Ulrich Guecker
''' 

import os
import time
import imp
import numpy as np
import pylab as pl


# Utilities_DAS specific imports
import kbtools
import kbtools_user

import scipy.io as sio
import subprocess


#from kbtools import load_Matlab_file
#=================================================================================
class CSimOL_InterfaceBaseClass(object):
    '''
       This is the base class implementing the inteface for condcuting a open loop simulation.
       For a specific application it has to be extended.
    
       The following three methods have to be overridden by the derived class:
         def CreateInputsSignalList(self,  xlim=(0,0), gate=(0,0), Description="", VehicleName='tbd', t_start=None, dura=None):
         def SelectParameterSet(self, ParameterSet=1):
         def CreateExpectedResultsSignalList(self, xlim=(0,0), gate=(0,0),Description=""):

    '''

    #=================================================================================
    def __init__(self):
        pass
        
    
    #=================================================================================
    def CreateInputsSignalList(self,  xlim=(0,0), gate=(0,0), Description="", VehicleName='tbd', t_start=None, dura=None):
        '''
        This method has to create a "list" with input signals for the simulation
        The list is in fact a Python dictionry. 
        
        Parameters: (all parameters provide meta data)
        xlim          range of x axis for plots
        gate          interval where calculated results are compared against expected results
        Description   textual specification of the test case 
        VehicleName   name of the vehicle to select vehicle specific parameters
        t_start       start of the event
        dura          duration of the event
        
        Note: optional signal which are not available shall be np.nan and not None
              automatic correction can not distinguish between mandatory and optional signals
                -> if an mandatory signal is missing, simulation is not started.
                   But simulation can be started when optional signal are missing
        '''
        
        signal_list = []
        '''
            application specific
        '''
        return signal_list

    #=================================================================================
    def SaveInputsAsMatlabBinary(self, FileName, xlim=(0,0), gate=(0,0),Description="", VehicleName='tbd', t_start=None, dura=None):
        '''
        This method saves signal list created by CreateInputsSignalList() to a Matlab Binary file.
        
        Method parameters: 
        FileName    filename for Matlab Binary file
        Meta data is the same as for CreateInputsSignalList().
        
        Before writing the Matlab Binary file, it is checked that signals of signal list are free from None.
        Matlab Binary file doesn't like signals contains Python's None
        
        '''
    
        signal_list = self.CreateInputsSignalList(xlim=xlim,gate=gate,Description=Description,VehicleName=VehicleName,t_start=t_start, dura=dura)
        
        if signal_list and self._check_for_free_of_None(signal_list, correct_it=False):
            sio.savemat(FileName, signal_list, oned_as='row')    
        else:
            print "InputsAsMatlabBinary %s is not written"%FileName
        
        return

    
    #=================================================================================
    def CreateExpectedResultsSignalList(self, xlim=(0,0), gate=(0,0),Description=""):
        '''
        This method has to create a "list" with expected result signals for the simulation
        The list is in fact a Python dictionry. 
        '''
        
        signal_list = []
        '''
            application specific
        '''
        return signal_list
    
    #=================================================================================
    def SaveExpectedResultsAsMatlabBinary(self, FileName, xlim=(0,0), gate=(0,0),Description=""):
        '''
        This method saves signal list created by CreateExpectedResultsSignalList() to a Matlab Binary file.
        
        Method parameters: 
        FileName    filename for Matlab Binary file
        Meta data is the same as for CreateExpectedResultsSignalList().
        
        Before writing the Matlab Binary file, it is checked that signals of signal list are free from None.
        Matlab Binary file doesn't like signals contains Python's None
        
        '''
 
        signal_list = self.CreateExpectedResultsSignalList(xlim=xlim,gate=gate,Description=Description)
        
        if signal_list and self._check_for_free_of_None(signal_list, correct_it=False):   
            sio.savemat(FileName, signal_list, oned_as='row')    
        else:
            print "SaveExpectedResultsAsMatlabBinary %s is not written"%FileName
           
        return

    
    
    #=================================================================================
    def CheckMatlabBinary(self, FileName):
        '''
        This method check a Matlab Binary file by loading it and display the description
        
        under construction 
        '''
        
        print "CheckMatlabBinary()"
        
        try:
            MatBinContents = kbtools.load_Matlab_file(FileName)
    
            if "Description" in MatBinContents:
                print "  Description:", MatBinContents["Description"]
            #print MatBinContents
    
            '''
            if 't' in MatBinContents:
                print "t", MatBinContents['t']
            '''
            print "   -> okay"
            return True
        except:
            print "   -> error"
            return False   
            
            
    #=================================================================================
    #
    # Parameter
    #
    #=================================================================================
    def SelectParameterSet(self, ParameterSet=1):
        '''
        This method has to create a dictionary containing the parameters used by simulation.
        The idea is to select one out of different predefined parameter sets.
        Parameter set is stored at self.parameters.
        
        Method parameter:
        ParameterSet : select one of the predefined parameter sets
        '''
       
        self.parameters = None  

        return self.parameters    
        
    #=================================================================================
    def ChangeParameters(self, ParameterChnDict = {}):
        '''
        This method can change parameter values of the selected parameter set.
        
        Method parameters:
        ParameterChnDict :  key: parameter name; value: new parameter value
        '''
         
        for key in ParameterChnDict.keys():
            old_value = self.parameters[key]
            self.parameters[key] = ParameterChnDict[key]
            print "%s changed from %s to %f"%(key, old_value, self.parameters[key])

    
    
    #=================================================================================
    def SaveParametersAsMatlabBinary(self, FileName):
        '''
        This method saves self.parameters created by SelectParameterSet() and changed by ChangeParameters() to a Matlab Binary file.
                
        Method parameters: 
        FileName    filename for Matlab Binary file

        Before writing the Matlab Binary file, it is checked that signals of signal list are free from None.
        Matlab Binary file doesn't like signals contains Python's None
        
        '''
        if self.parameters and self._check_for_free_of_None(self.parameters , correct_it=False):
            sio.savemat(FileName, self.parameters, oned_as='row')    
        else:
            print "SaveParametersAsMatlabBinary %s is not written"%FileName

        
    #=================================================================================
    def _check_for_free_of_None(self,signal_list, correct_it = False):
        '''
        This method checks that signals of signal list are not None
        '''
    
        None_found = []
        
        for name in signal_list.keys():
            if signal_list[name] is None:
                print name
                if correct_it:
                   signal_list[name] = np.nan
                None_found.append(name)
        
        if None_found:
            print "Following signals are None: ",  None_found
            if correct_it:
                print "  -> corrected"
                return True        
            return False
        else:
            return True        
      

#=================================================================================
class CSimOL_MatlabBinInterface(object):
    '''
    This class conducts the open loop simulation
    
    '''

    def __init__(self,ProgName=None,SimInterfaceFileName=None, SimInterfaceClassName=None, dbc_list =[], verbose=False):

        # 1. parameter (optional): ProgName: path and name of simulation programm *.exe
        self.ProgName = ProgName

        # 2. parameter (required): SimInterfaceFileName : path and name of interface or   interface class               
        # 3. parameter (optional): SimInterfaceClassName
        if isinstance(SimInterfaceFileName,(str,unicode)):
            # Task: Get a class from module given by its absolute file name
            
            # SimInterfaceFileName: this is the file name of a python module
            #                       e.g. 
            
            ModulName = os.path.splitext(os.path.basename(SimInterfaceFileName))[0]
            Module = imp.load_source(ModulName, SimInterfaceFileName)
            if SimInterfaceClassName is None:
               SimInterfaceClassName ='C_sim_interface'
            SimInterfaceClass  = getattr(Module, SimInterfaceClassName)
            self.SimInterfaceClass = SimInterfaceClass
           
        else:
            self.SimInterfaceClass = SimInterfaceFileName
        
    
        # 4. parameter :  list of required dbc file use for converting CAN bus data
        self.dbc_list = dbc_list
        
        # 5. parameter :  verbose [True|False]
        self.verbose = verbose
        
        # Init BaseName + FileNames_MatlabBin
        self.CreateFileNames_MatlabBin()
        
        # initialize variable that will be fill during simulation
        self.FLR20_sig                = None
        self.matdata_input            = None
        self.matdata_output           = None
        self.matdata_expected_results = None
        self.Description              = None
        self.xlim                     = None
        
        # error status
        self.error_status = ""
        
    #=================================================================================
    def Run(self, Source_or_FullPathFileName=None, VariationName=None,xlim=None,gate=None,Description="", \
                  create_expected_results = False,SimOutput_as_ExpectedResult=False, \
                  ParameterSet=1, ParameterChnDict = {},FileBaseName_MatlabBin = r'TD_ldws_01',
                  VehicleName='tbd', t_start=None, dura=None, ActionDetails = None, cfg=None, Do_CleanUp_of_MatlabBinaryFiles=True):

        if self.verbose:
            print "Run() - start"

        self.CreateMatlabBin(Source_or_FullPathFileName=Source_or_FullPathFileName,
                             VariationName=VariationName,
                             xlim=xlim,
                             gate=gate,
                             Description=Description,
                             create_expected_results = create_expected_results,
                             SimOutput_as_ExpectedResult=SimOutput_as_ExpectedResult,
                             ParameterSet=ParameterSet, 
                             ParameterChnDict = ParameterChnDict,
                             FileBaseName_MatlabBin = FileBaseName_MatlabBin,
                             VehicleName=VehicleName, 
                             t_start=t_start, 
                             dura=dura, 
                             ActionDetails = ActionDetails, 
                             cfg=cfg)
        
        self.RunSimulation()
        self._LoadMatlabBin()
        if Do_CleanUp_of_MatlabBinaryFiles:
            self.CleanUp()          # remove created Matlab Binary
            
        if self.verbose:
            print "Run() - end"

    
    #=================================================================================
    def GetBaseName(self):
        return self.BaseName
        
    #=================================================================================
    def CreateFileNames_MatlabBin(self,BaseName = r"sil_"):

        if self.verbose:
            print "CreateFileNames_MatlabBin() - start"    
        BaseName = os.path.basename(BaseName)

        self.BaseName = BaseName
        self.FileName_MatlabBin_parameters       = r'%s_parameters.mat'%BaseName
        self.FileName_MatlabBin_input            = r'%s_input.mat'%BaseName
        self.FileName_MatlabBin_expected_results = r'%s_expected_results.mat'%BaseName
        self.FileName_MatlabBin_output           = r'%s_output.mat'%BaseName

        if self.verbose:
            print "FileName_MatlabBin_parameters      : ",self.FileName_MatlabBin_parameters
            print "FileName_MatlabBin_input           : ",self.FileName_MatlabBin_input
            print "FileName_MatlabBin_expected_results: ",self.FileName_MatlabBin_expected_results
            print "FileName_MatlabBin_output          : ",self.FileName_MatlabBin_output
            print "CreateFileNames_MatlabBin() - end"    
            
        return 
        
    #=================================================================================
    def _RemoveFile(self,FileName):
        if os.path.exists(FileName):
            os.remove(FileName)
            
            
    def CleanUp_MatlabBin(self):
    
        if self.verbose:
            print "CleanUp_MatlabBin() - start"

        self._RemoveFile(self.FileName_MatlabBin_parameters)
        self._RemoveFile(self.FileName_MatlabBin_input)
        self._RemoveFile(self.FileName_MatlabBin_expected_results)
        self._RemoveFile(self.FileName_MatlabBin_output)
        
        if self.verbose:
            print "CleanUp_MatlabBin() - end"


        return 
        
    #=================================================================================
    def RunSimulation(self,BaseName=None,ProgName=None):
        '''
           run simulation
           
           parameters:
           BaseName : filename for input signals, parameter and generated output signals
           ProgName : filename of simulation executable
        '''
        
        if self.verbose:
            print "RunSimulation() - start"
            
        # ---------------------------------
        # prepare inputs
      
        # select Matlab Binaries
        if BaseName is not None:
            self.CreateFileNames_MatlabBin(BaseName)
        
        # simulation execuable        
        if ProgName is None:
            ProgName = self.ProgName

        # ---------------------------------
        # checks before running the simulation
        if ProgName is None:
            self.error_status = "error - ProgName not given"
            print self.error_status 
            return
            
        if not os.path.exists(self.FileName_MatlabBin_parameters):
            self.error_status = "error - %s doesn't exists"%self.FileName_MatlabBin_parameters
            return self.error_status
        
        if not os.path.exists(self.FileName_MatlabBin_input):
            self.error_status = "error - %s doesn't exists"%self.FileName_MatlabBin_input
            return self.error_status
            
            
        # build command line  
        args = []
        args.append(ProgName)
        args.append(r'-debug')

        args.append(r'-p')
        args.append(self.FileName_MatlabBin_parameters)

        args.append(r'-i')
        args.append(self.FileName_MatlabBin_input)
    
        args.append(r'-o')
        args.append(self.FileName_MatlabBin_output)
    
        if self.verbose:
            print args

        # call    
        p = subprocess.check_call(args)
        if self.verbose:
            print "p",p
            
        if self.verbose:
            print "RunSimulation() - end"
    
        return p
        
    #=================================================================================
    def CreateMatlabBin(self, Source_or_FullPathFileName=None, VariationName=None,xlim=None,gate=None,Description="", \
                              create_expected_results = False,SimOutput_as_ExpectedResult=False, \
                              ParameterSet=1, ParameterChnDict = {},FileBaseName_MatlabBin = r'TD_ldws_01',
                              VehicleName='tbd', t_start=None, dura=None, ActionDetails = None, cfg=None):
        '''
            not included in ActionDetails: 'create_expected_results','ParameterSet', 'ParameterChnDict', 'FileBaseName_MatlabBin'
        
        '''
        
        if self.verbose:
            print "CreateMatlabBin() - start"
    
        if isinstance(ActionDetails, kbtools_user.CActionDetails):
            Source_or_FullPathFileName  = ActionDetails.FullPathFileName
            VariationName               = ActionDetails.VariationName
            xlim                        = ActionDetails.xlim
            gate                        = ActionDetails.gate
            Description                 = ActionDetails.Description
            SimOutput_as_ExpectedResult = ActionDetails.SimOutput_as_ExpectedResult
            VehicleName                 = ActionDetails.Vehicle
            t_start                     = ActionDetails.t_start
            dura                        = ActionDetails.dura              
    
        # -----------------------------------------------------
        if VariationName is not None:
            # Name for the Variation
            if isinstance(VariationName, (int, long, float, complex)):
                VariationName = "%02d"%(int(VariationName))
            else:
                VariationName = str(VariationName)
            print "  VariationName:", VariationName

            # -----------------------------------------------------
            # FileNames
            if FileBaseName_MatlabBin:
                #BaseName = r"%s_var_%s"%(FileBaseName_MatlabBin,VariationName)
                BaseName = r"%s_%s"%(FileBaseName_MatlabBin,VariationName)
            else:
                BaseName = VariationName
        else:
            BaseName = FileBaseName_MatlabBin
            
        self.CreateFileNames_MatlabBin(BaseName)
        
       
        # -----------------------------------------------------
        # signals
        print "  signals  ...", 
  
        # use simulation output as expected results
        if SimOutput_as_ExpectedResult:
            print "     SimOutput as ExpectedResult"
            iSimInterface = self.SimInterfaceClass(self.FileName_MatlabBin_output,'matdata_output')
            #iSimInterface.SaveInputsAsMatlabBinary(FileName_MatlabBin_input)  # not yet available
            if create_expected_results:
                 iSimInterface.SaveExpectedResultsAsMatlabBinary(self.FileName_MatlabBin_expected_results,xlim=xlim,gate=gate,Description=Description)
        else:
            print "     Measurement as ExpectedResult"
            self.CleanUp_MatlabBin()
            iSimInterface = self.SimInterfaceClass(Source_or_FullPathFileName,dbc_list = self.dbc_list,verbose=self.verbose)
            iSimInterface.cfg = cfg
            iSimInterface.SaveInputsAsMatlabBinary(self.FileName_MatlabBin_input,xlim=xlim,gate=gate,Description=Description,VehicleName=VehicleName,t_start=t_start,dura=dura)
            if create_expected_results:
                iSimInterface.SaveExpectedResultsAsMatlabBinary(self.FileName_MatlabBin_expected_results,xlim=xlim,gate=gate,Description=Description)

    
        # -----------------------------------------------------
        # parameter
        print "  parameters in ", self.FileName_MatlabBin_parameters
        iSimInterface.SelectParameterSet(ParameterSet=ParameterSet) 
        iSimInterface.ChangeParameters(ParameterChnDict = ParameterChnDict)
        iSimInterface.SaveParametersAsMatlabBinary(self.FileName_MatlabBin_parameters)
    
    
        # ----------------------------------------------------------
        # check generated Matlab Binary Files
        print "  check generated Matlab Binary Files"
        iSimInterface.CheckMatlabBinary(self.FileName_MatlabBin_input)
        if create_expected_results:
            iSimInterface.CheckMatlabBinary(self.FileName_MatlabBin_expected_results)
        iSimInterface.CheckMatlabBinary(self.FileName_MatlabBin_parameters)
        
        self.FLR20_sig = iSimInterface.GetFLR20_sig()
        
        if self.verbose:
            print "CreateMatlabBin() - end"

        return iSimInterface.GetFLR20_sig()
    #=================================================================================
    def LoadMatlabBin(self,VariationName):
        BaseName = VariationName
        self._LoadMatlabBin(BaseName)
        
            
    #=================================================================================
    def _LoadMatlabBin(self, BaseName=None):
        '''
           Load the following Matlab Binary files into Python variables:
              input            -> self.matdata_input
              output           -> self.matdata_output
              expected_results -> self.matdata_expected_results
              
           Extract information:
              Description      -> self.Description      short description given to this measurement
              xlim             -> self.xlim             range for plotting the x-axis 
        
        '''
        if self.verbose:
            print "_LoadMatlabBin() - start"
            print "BaseName:", BaseName  # os.path.basename(BaseName)
        
        # select Matlab Binaries
        if BaseName is not None:
            self.CreateFileNames_MatlabBin(BaseName)

       
        # ------------------------------------------------------------
        # load data from Matlab Binary files
        try:
            matdata_input  = kbtools.load_Matlab_file(self.FileName_MatlabBin_input,ConvertSignalNan2None = True)
        except:
            matdata_input  = None
            
        try:
            matdata_parameters = kbtools.load_Matlab_file(self.FileName_MatlabBin_parameters,ConvertSignalNan2None = True)
        except:
            matdata_parameters  = None
            
        try:    
            matdata_output = kbtools.load_Matlab_file(self.FileName_MatlabBin_output,ConvertSignalNan2None = True)
        except:
            matdata_output = None
            
        try:
            matdata_expected_results = kbtools.load_Matlab_file(self.FileName_MatlabBin_expected_results,ConvertSignalNan2None = True)
        except:
            matdata_expected_results = None

        # ------------------------------------------------------------
        # get xlim and Description
        xlim = None  
        Description = ""    
        VehicleName = ""
        t_start = None
        dura = None
        
        if matdata_expected_results is not None:
            if 'xlim' in matdata_expected_results and len(matdata_expected_results['xlim'])>1:
                xlim = list(matdata_expected_results['xlim'])
            if 'Description' in matdata_expected_results and matdata_expected_results['Description'] is not None:
                Description = matdata_expected_results['Description']
        if matdata_input is not None:
            if 'xlim' in matdata_input and len(matdata_input['xlim'])>1:
                xlim = list(matdata_input['xlim'])
            if 'Description' in matdata_input and matdata_input['Description'] is not None:
                Description = matdata_input['Description']
            if 'VehicleName' in matdata_input and matdata_input['VehicleName'] is not None:
                VehicleName = matdata_input['VehicleName']
            if 't_start' in matdata_input and matdata_input['t_start'] is not None:
                t_start = matdata_input['t_start']
                # nan
            if 'dura' in matdata_input and matdata_input['dura'] is not None:
                dura = matdata_input['dura']
                # nan
                
  
        if self.verbose:
            print "xlim:        ", xlim    
            print "Description: ", Description
            print "VehicleName: ", VehicleName
            print "t_start:     ", t_start
            print "dura:        ", dura
                        
       
        # ---------------------------------------------
        # register simulation signal and parameter
        self.matdata_input            = matdata_input
        self.matdata_parameters       = matdata_parameters 
        self.matdata_output           = matdata_output
        self.matdata_expected_results = matdata_expected_results
        
        # register meta data
        self.Description              = Description
        self.xlim                     = xlim
        self.VehicleName              = VehicleName
        self.t_start                  = t_start
        self.dura                     = dura
        
        if self.verbose:
            print "_LoadMatlabBin() - end"

        
        
    #=================================================================================
    def CleanUp(self):
        '''
           clean up
              remove Matlab Binary file temporarily generated for the simulation
        '''
        if self.verbose:
            print "CleanUp() - start"

        self._remove_file(self.FileName_MatlabBin_input)
        self._remove_file(self.FileName_MatlabBin_parameters)
        self._remove_file(self.FileName_MatlabBin_output)
        self._remove_file(self.FileName_MatlabBin_expected_results)
        #self._remove_file(r'matlab_Multimedia.mat_dcomment.txt')

        if self.verbose:
            print "CleanUp() - end"
        
        
    #=================================================================================
    def _remove_file(self,FileName):
        '''
           remove file specified by FileName
        '''
        if self.verbose:
           print "_remove_file()"
           print "FileName: ", FileName
           
        AbsFileName = os.path.abspath(FileName)
        
        if self.verbose:
           print "AbsFileName: ", AbsFileName
        if os.path.exists(AbsFileName):
            if self.verbose:
                print "file exists -> will be removed"
            os.remove(AbsFileName)
        
    #=================================================================================
