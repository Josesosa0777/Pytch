'''
   
   data source: CVR3

   ego vehicle: vehicle speed, yaw rate, curavture, etc.
   OHY-Objects
   Video Objects
   Fus-Objects,
   PositionsMatrix (S1,S2,L1,L2,R1,R2)
   ASF
   ATS-Objects (0,1,2,3,4)
   Intro             CVR3_sig['Intro']
   ego vehicle sync  CVR3_sig['Fus_General_TC'] 
   driver override   CVR3_sig['Sit_BasicInput_TC'], CVR3_sig['Asf_BasicInput_TC'], 
   
      
   Ulrich Guecker 
   
   2013-07-23   introduce CVR3_sig['VBOX_IMU'], CVR3_sig['J1939']
   2013-04-03   CVR3_sig['Intro'], CVR3_sig['Fus_General_TC'], CVR3_sig['Sit_BasicInput_TC'],  CVR3_sig['Crm_OstaskdataTc_TC']
   2012-11-30
   2012-08-24
   2011-12-14

'''


# standard Python imports
import pickle
import numpy as np
import pylab as pl

# KB specific imports
import measparser
import kbtools
import kbtools_user



#*********************************************************************************************
class cDataCVR3():

  # class variables 
  N_OhyObj = 40   # number of Radar Objcets
  
  N_VidObj = 10   # number of Video Objects

  N_FusObj = 32   # number of Fus Objects + 1 ExtVideoObj
  
  N_ATSObj = 5    # number of ACC Target Selection Objects  (Index 0..4)
  
  # show comment
  verbose = False
  #verbose = True

  
  #============================================================================================
  @staticmethod
  def load_CVR3_from_Source(Source, PickleFilename=None, ShortDeviceName='RadarFC'):
    # load standard set of CVR3 signals from SignalSource
    # ShortDeviceName
    #  CVR2 aka LRR3 : ECU
    #  CVR3          : MRR1plus, RadarFC
    
    
       
    # ------------------------------------------------
    # build CVR3_sig dictionary
    CVR3_sig = {}
    CVR3_sig['SensorType'] = "CVR3"
    CVR3_sig['FileName']   = Source.FileName
        
    CVR3_sig['Crm_OstaskdataTc_TC'] = cDataCVR3.create_Crm_OstaskdataTc_TC(Source, ShortDeviceName)    
    
    CVR3_sig['EgoVeh']    = cDataCVR3.create_EgoVeh(Source, ShortDeviceName)
    CVR3_sig['Time']      = CVR3_sig['EgoVeh']['Time']
    #CVR3_sig.update(CVR3_sig['EgoVeh'])  # for downward compatibility
    
    CVR3_sig['Fus_General_TC']    = cDataCVR3.create_Fus_General_TC(Source, ShortDeviceName)
    CVR3_sig['Sit_BasicInput_TC'] = cDataCVR3.create_Sit_BasicInput_TC(Source, ShortDeviceName)
    CVR3_sig['Asf_BasicInput_TC'] = cDataCVR3.create_Asf_BasicInput_TC(Source, ShortDeviceName)
      
    CVR3_sig['OhyObj']    = cDataCVR3.create_OhyObj(Source, ShortDeviceName)
    
    CVR3_sig['VidObj']    = cDataCVR3.create_VidObj(Source, ShortDeviceName)
    CVR3_sig['VidObjT20'] = cDataCVR3.create_VidObjT20(Source, ShortDeviceName)
       
    CVR3_sig['FusObj']    = cDataCVR3.create_FusObj(Source, ShortDeviceName,CVR3_sig['OhyObj'], CVR3_sig['VidObj'])
    
    CVR3_sig['PosMatrix'] = cDataCVR3.create_PosMatrix(Source, ShortDeviceName,CVR3_sig['FusObj'],CVR3_sig['OhyObj'],CVR3_sig['VidObj'])

    CVR3_sig['Intro']     = cDataCVR3.create_Intro(Source, ShortDeviceName,CVR3_sig['FusObj'],CVR3_sig['OhyObj'],CVR3_sig['VidObj'])
    
    # ASF (Active Safety Function - RB SW component for AEBS)
    CVR3_sig['ASF']       = cDataCVR3.create_ASF(Source, ShortDeviceName)

    # ATS (ACC Target Selection)    
    CVR3_sig['ATS']       = cDataCVR3.create_ATS(Source, ShortDeviceName,CVR3_sig['FusObj'])
    
    # VBOX_IMU    
    CVR3_sig['VBOX_IMU']  =  cDataCVR3.create_VBOX_IMU(Source)

    # J1939    
    CVR3_sig['J1939']     =  cDataCVR3.create_J1939(Source)


    
    # -------------------------------------------------
    # save if filename given to a pickle file
    if CVR3_sig and PickleFilename:
      output = open(PickleFilename, 'wb')
      pickle.dump(CVR3_sig, output,-1)     # -1: using the highest protocol available
      output.close()

    return CVR3_sig
    
  #============================================================================================
  @staticmethod
  def load_CVR3_from_picklefile(FileName):

    # load data from file (pickle)
    pkl_file = open(FileName, 'rb')
    CVR3_sig  = pickle.load(pkl_file)
    pkl_file.close()
    
    return CVR3_sig

  #============================================================================================
  @staticmethod
  def create_Crm_OstaskdataTc_TC(Source, DeviceName):
    Crm_OstaskdataTc_TC = {}
    
       
    Crm_OstaskdataTc_TC['tdtTC']   = kbtools.GetSignal(Source, DeviceName,  "crm.OstaskdataTc_TC.tdtTC") [1]
    Crm_OstaskdataTc_TC['CountTC'] = kbtools.GetSignal(Source, DeviceName,  "crm.OstaskdataTc_TC.CountTC") [1]
 
    return Crm_OstaskdataTc_TC
    
  #============================================================================================
  @staticmethod
  def create_EgoVeh(Source, DeviceName):
    EgoVeh = {}
    
    # time axis + vehicle signals
    EgoVeh["Time"],EgoVeh["vxvRef"] = kbtools.GetSignal(Source, DeviceName, "evi.General_TC.vxvRef")
    EgoVeh["axvRef"]                = kbtools.GetSignal(Source, DeviceName, "evi.General_TC.axvRef")[1]
    EgoVeh["psiDtOpt"]              = kbtools.GetSignal(Source, DeviceName, "evi.General_TC.psiDtOpt")[1]
    #EgoVeh["kapCurvTraj"]          = kbtools.GetSignal(Source, DeviceName, "evi.MovementData_TC.kapCurvTraj")[1]
    EgoVeh["kapCurvTraj"]           = kbtools.GetSignal(Source, DeviceName, "evi.General_TC.kapCurvTraj")[1]

    return EgoVeh
    
  #============================================================================================
  @staticmethod
  def create_Fus_General_TC(Source, DeviceName):
    Fus_General_TC = {}
    
    # fus.General_TC
    # time axis and timestamp
    Fus_General_TC["Time"],Fus_General_TC['tAbsRefTime']  = kbtools.GetSignal(Source, DeviceName,  "fus.General_TC.tAbsRefTime") 
    
    # ego vehicle speed, acceleration and yaw rate
    Fus_General_TC["vRefSync"]     = kbtools.GetSignal(Source, DeviceName, "fus.General_TC.vRefSync")[1]
    Fus_General_TC['aRefSync']     = kbtools.GetSignal(Source, DeviceName, "fus.General_TC.aRefSync")[1]
    Fus_General_TC['psiDtOptSync'] = kbtools.GetSignal(Source, DeviceName, "fus.General_TC.psiDtOptSync")[1]
       
    return Fus_General_TC

  #============================================================================================
  @staticmethod
  def create_Sit_BasicInput_TC(Source, DeviceName):
    Sit_BasicInput_TC = {}
     
    Sit_BasicInput_TC['GPPos']               = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.GPPos") [1]
    Sit_BasicInput_TC['GPdtPos']             = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.GPdtPos") [1]
    Sit_BasicInput_TC['alpDtSteeringWheel']  = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.alpDtSteeringWheel") [1]
    Sit_BasicInput_TC['pDtBrake']            = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.pDtBrake") [1]
 
    Sit_BasicInput_TC['BPAct_b']          = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.Flags.b.BPAct_b") [1]
    Sit_BasicInput_TC['DirIndL_b']        = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.Flags.b.DirIndL_b") [1]
    Sit_BasicInput_TC['DirIndR_b']        = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.Flags.b.DirIndR_b") [1]
    Sit_BasicInput_TC['DriverOverride_b'] = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.Flags.b.DriverOverride_b") [1]
    Sit_BasicInput_TC['GPKickdown_B']     = kbtools.GetSignal(Source, DeviceName, "sit.BasicInput_TC.Flags.b.GPKickdown_B") [1]
    
       
    return Sit_BasicInput_TC
    
  #============================================================================================
  @staticmethod
  def create_Asf_BasicInput_TC(Source, DeviceName):
    Asf_BasicInput_TC = {}
    
    Asf_BasicInput_TC['pBrake']              = kbtools.GetSignal(Source, DeviceName, "asf.BasicInput_TC.pBrake") [1]
    Asf_BasicInput_TC['pBrakeValid_b']       = kbtools.GetSignal(Source, DeviceName, "asf.BasicInput_TC.Flags.Flags.pBrakeValid_b") [1]

    Asf_BasicInput_TC['EngineOn_b']          = kbtools.GetSignal(Source, DeviceName, "asf.BasicInput_TC.Flags.Flags.EngineOn_b") [1]
    Asf_BasicInput_TC['dVehicleWidth']       = kbtools.GetSignal(Source, DeviceName, "asf.BasicInput_TC.dVehicleWidth") [1]
  
    return Asf_BasicInput_TC
    
    
  #============================================================================================
  @staticmethod
  def create_OhyObj(Source, DeviceName):
    OhyObj = {}
    for OhyObjIdx in xrange(cDataCVR3.N_OhyObj):
      OhyObj[OhyObjIdx] = {}
      OhyObj[OhyObjIdx]["Time"],\
      OhyObj[OhyObjIdx]["Valid_b"] = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.c.c.Valid_b"%OhyObjIdx)

      OhyObj[OhyObjIdx]["dx"]      = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.dx"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["dy"]      = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.dy"%OhyObjIdx)[1]

      OhyObj[OhyObjIdx]["vx"]      = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.vx"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["vy"]      = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.vy"%OhyObjIdx)[1]

      OhyObj[OhyObjIdx]["wClassNoObstacle"]    = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wClassNoObstacle"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wClassObstacle"]      = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wClassObstacle"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wClassObstacleNear"]  = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wClassObstacleNear"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wConstElem"]          = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wConstElem"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wExistProb"]          = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wExistProb"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wGroundReflex"]       = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wGroundReflex"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["wInterfProb"]         = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.wInterfProb"%OhyObjIdx)[1]


      
      #OhyObj[OhyObjIdx]["GRI_Features_value"] = kbtools.GetSignal(Source, DeviceName, "ohyIntern.GRI_Features.i%d.value"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["GRI_Features_value"] = kbtools.GetSignal(Source, DeviceName, "ohy_s_Intern.GRI_Features.i%d.value"%OhyObjIdx)[1]

      OhyObj[OhyObjIdx]["dbPowerFilt"] = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.internal.dbPowerFilt"%OhyObjIdx)[1]

     
      
      OhyObj[OhyObjIdx]["probClass.i0"]     = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.probClass.i0"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["probClass.i1"]     = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.probClass.i1"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["probClass.i2"]     = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.probClass.i2"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["probClass.i3"]     = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.probClass.i3"%OhyObjIdx)[1]
      OhyObj[OhyObjIdx]["probClass.i4"]     = kbtools.GetSignal(Source, DeviceName, "ohy.ObjData_TC.OhlObj.i%d.probClass.i4"%OhyObjIdx)[1]
      
      if OhyObj[OhyObjIdx]["probClass.i0"] is not None:     
        OhyObj[OhyObjIdx]["probClass.i0"] = OhyObj[OhyObjIdx]["probClass.i0"]/32768.0
        OhyObj[OhyObjIdx]["probClass.i1"] = OhyObj[OhyObjIdx]["probClass.i1"]/32768.0
        OhyObj[OhyObjIdx]["probClass.i2"] = OhyObj[OhyObjIdx]["probClass.i2"]/32768.0
        OhyObj[OhyObjIdx]["probClass.i3"] = OhyObj[OhyObjIdx]["probClass.i3"]/32768.0
        OhyObj[OhyObjIdx]["probClass.i4"] = OhyObj[OhyObjIdx]["probClass.i4"]/32768.0
           
      
    return OhyObj 
    
  #============================================================================================
  @staticmethod
  def create_VidObj(Source, DeviceName):
    # Video Objects TC
    VidObj = {}
    for VidObjIdx in xrange(cDataCVR3.N_VidObj):
      VidObj[VidObjIdx] = {}
      VidObj[VidObjIdx]["Time"],\
      VidObj[VidObjIdx]["Handle"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.Handle"%VidObjIdx)
      VidObj[VidObjIdx]["countAlive"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.countAlive"%VidObjIdx)[1]
      VidObj[VidObjIdx]["Hist_b"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.b.b.Hist_b"%VidObjIdx)[1]
      VidObj[VidObjIdx]["Measured_b"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.b.b.Measured_b"%VidObjIdx)[1]

      VidObj[VidObjIdx]["dx"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.dxv"%VidObjIdx)[1]
      VidObj[VidObjIdx]["dy"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.dyv"%VidObjIdx)[1]
      VidObj[VidObjIdx]["vx"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.vxv"%VidObjIdx)[1]
      VidObj[VidObjIdx]["vy"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.vyv"%VidObjIdx)[1]
      VidObj[VidObjIdx]["dWidth"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.dWidth"%VidObjIdx)[1]
      VidObj[VidObjIdx]["dLength"]    = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.dLength"%VidObjIdx)[1]
      
      VidObj[VidObjIdx]["wExistProb"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.wExistProb"%VidObjIdx)[1]
      VidObj[VidObjIdx]["ObjType"]    = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_TC.VidObj.i%d.ObjType"%VidObjIdx)[1]
     
    return VidObj
    
  #============================================================================================
  @staticmethod
  def create_VidObjT20(Source, DeviceName):
    # Video Objects T20
    VidObjT20 = {}
    for VidObjIdx in xrange(cDataCVR3.N_VidObj):
      VidObjT20[VidObjIdx] = {}
      VidObjT20[VidObjIdx]["Time"],\
      VidObjT20[VidObjIdx]["Handle"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.Handle"%VidObjIdx)
      VidObjT20[VidObjIdx]["countAlive"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.countAlive"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["Hist_b"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.b.b.Hist_b"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["Measured_b"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.b.b.Measured_b"%VidObjIdx)[1]
      
      VidObjT20[VidObjIdx]["dx"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.dxv"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["dy"]         = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.dyv"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["dWidth"]     = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.dWidth"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["dLength"]    = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.dLength"%VidObjIdx)[1]
      
      VidObjT20[VidObjIdx]["wExistProb"] = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.wExistProb"%VidObjIdx)[1]
      VidObjT20[VidObjIdx]["ObjType"]    = kbtools.GetSignal(Source, DeviceName, "fus.SVidBasicInput_T20.VidObj.i%d.ObjType"%VidObjIdx)[1]
      
    return VidObjT20
    
  #============================================================================================
  @staticmethod
  def create_FusObj(Source, DeviceName,OhyObj, VidObj):
  
    # FUS Objects
    FusObj = {}
    for FusObjIdx in xrange(cDataCVR3.N_FusObj):
      FusObj[FusObjIdx] = {}
      FusObj[FusObjIdx]["Time"],\
      FusObj[FusObjIdx]["Handle"]     = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.Handle"%FusObjIdx)
      FusObj[FusObjIdx]["dx"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dxv"%FusObjIdx)[1]
      FusObj[FusObjIdx]["dy"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dyv"%FusObjIdx)[1]
      FusObj[FusObjIdx]["dyvBase"]    = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dyvBase"%FusObjIdx)[1]
      
      FusObj[FusObjIdx]["vx"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.vxv"%FusObjIdx)[1]
      FusObj[FusObjIdx]["vy"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.vyv"%FusObjIdx)[1]
      FusObj[FusObjIdx]["ax"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.axv"%FusObjIdx)[1]
      FusObj[FusObjIdx]["ay"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.ayv"%FusObjIdx)[1]
      
      FusObj[FusObjIdx]["dVarYvBase"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dVarYvBase"%FusObjIdx)[1]
      
      
      FusObj[FusObjIdx]["DriveInvDir_b"]   = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.DriveInvDir_b"%FusObjIdx)[1]
      FusObj[FusObjIdx]["Drive_b"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.Drive_b"%FusObjIdx)[1]
      FusObj[FusObjIdx]["NotClassified_b"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.NotClassified_b"%FusObjIdx)[1]
      FusObj[FusObjIdx]["Stand_b"]         = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.Stand_b"%FusObjIdx)[1]
      FusObj[FusObjIdx]["StoppedInvDir_b"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.StoppedInvDir_b"%FusObjIdx)[1]
      FusObj[FusObjIdx]["Stopped_b"]       = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.Stopped_b"%FusObjIdx)[1]
      
     
      FusObj[FusObjIdx]["wExistProb"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wExistProb"%FusObjIdx)[1]
      FusObj[FusObjIdx]["wGroundReflex"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wGroundReflex"%FusObjIdx)[1]
      FusObj[FusObjIdx]["wConstElem"]    = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wConstElem"%FusObjIdx)[1]
      
      # Obstacle Classifier
      FusObj[FusObjIdx]["wObstacle"]           = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wObstacle"%FusObjIdx)[1]
      FusObj[FusObjIdx]["wClassObstacle"]      = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wClassObstacle"%FusObjIdx)[1]
      FusObj[FusObjIdx]["wClassObstacleNear"]  = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.wClassObstacleNear"%FusObjIdx)[1]
      FusObj[FusObjIdx]["qClass"]              = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.qClass"%FusObjIdx)[1]

      FusObj[FusObjIdx]["AdditionalSensorAssociated_b"]  = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.b.b.AdditionalSensorAssociated_b"%FusObjIdx)[1]

      FusObj[FusObjIdx]["dLength"]    = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dLength"%FusObjIdx)[1]
      FusObj[FusObjIdx]["dWidth"]     = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dWidth"%FusObjIdx)[1]
      FusObj[FusObjIdx]["dWidthBase"] = kbtools.GetSignal(Source, DeviceName, "fus.ObjData_TC.FusObj.i%d.dWidthBase"%FusObjIdx)[1]
     
      FusObj[FusObjIdx]["LrrObjIdx"]  = kbtools.GetSignal(Source, DeviceName, "fus_asso_mat.LrrObjIdx.i%d"%FusObjIdx)[1]
      FusObj[FusObjIdx]["VidObjIdx"]  = kbtools.GetSignal(Source, DeviceName, "fus_s_asso_mat.VidObjIdx.i%d"%FusObjIdx)[1]
      
      
      # Ohy Objects
      FusObj[FusObjIdx]['dx_OHY']          = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['dy_OHY']          = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['dbPowerFilt_OHY'] = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['GRI_Features_value_OHY'] = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      
      for OhyObjIdx in xrange(cDataCVR3.N_OhyObj):
          mask = np.logical_and(FusObj[FusObjIdx]["LrrObjIdx"] < 255, FusObj[FusObjIdx]["LrrObjIdx"] == OhyObjIdx)
          if OhyObj[OhyObjIdx]['dx'] is not None:
            FusObj[FusObjIdx]['dx_OHY'][mask] = OhyObj[OhyObjIdx]['dx'][mask]      
            FusObj[FusObjIdx]['dy_OHY'][mask] = OhyObj[OhyObjIdx]['dy'][mask]
          if OhyObj[OhyObjIdx]['dbPowerFilt'] is not None:
            FusObj[FusObjIdx]['dbPowerFilt_OHY'][mask] = OhyObj[OhyObjIdx]['dbPowerFilt'][mask]
          if OhyObj[OhyObjIdx]['GRI_Features_value'] is not None:
            FusObj[FusObjIdx]['GRI_Features_value_OHY'][mask] = OhyObj[OhyObjIdx]['GRI_Features_value'][mask]  
      
      # Video Objects
      FusObj[FusObjIdx]['dx_VID']        = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['dy_VID']        = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['vx_VID']        = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      FusObj[FusObjIdx]['vy_VID']        = 0.0*np.ones_like(FusObj[FusObjIdx]["Time"])
      for VidObjIdx in xrange(cDataCVR3.N_VidObj):
          mask = np.logical_and(FusObj[FusObjIdx]["VidObjIdx"] < 255, FusObj[FusObjIdx]["VidObjIdx"] == VidObjIdx)
          if VidObj[VidObjIdx]['dx'] is not None:
            FusObj[FusObjIdx]['dx_VID'][mask] = VidObj[VidObjIdx]['dx'][mask]      
            FusObj[FusObjIdx]['dy_VID'][mask] = VidObj[VidObjIdx]['dy'][mask] 
            FusObj[FusObjIdx]['vx_VID'][mask] = VidObj[VidObjIdx]['vx'][mask]      
            FusObj[FusObjIdx]['vy_VID'][mask] = VidObj[VidObjIdx]['vy'][mask] 

      
    return FusObj
    

  #============================================================================================
  @staticmethod
  def create_PosMatrix(Source, DeviceName,FusObj,OhyObj,VidObj):
    # Position Matrix from FilteredObjects
    PosMatrix={}
 
    #PosMatrixObjListe = (('S1',1),)
    PosMatrixObjListe = (('L1',0),('S1',1),('R1',2),('L2',3),('S2',4),('R2',5))
   
    # init  
    for ObjName, Idx in PosMatrixObjListe:
        if cDataCVR3.verbose:
            print "ObjName %s, Idx %d"%(ObjName, Idx)
   
        PosMatrix[ObjName] = {}
        PosMatrix[ObjName]['Time'], PosMatrix[ObjName]['FusHandle'] = kbtools.GetSignal(Source, DeviceName, "sit.IntroFinder_TC.FilteredObjects.i0.ObjectList.i%d"%Idx)
        
        FusHandle = PosMatrix[ObjName]['FusHandle'] 
        PosMatrix[ObjName]['FusHandle']     = np.zeros_like(FusHandle)
        PosMatrix[ObjName]['FusObjIdx']     = 255.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dx']            = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dx_Lrr']        = 0.0*np.ones_like(FusHandle)
      
        PosMatrix[ObjName]['dy']            = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dy_Lrr']        = 0.0*np.ones_like(FusHandle)

        PosMatrix[ObjName]['vx']            = 0.0*np.ones_like(FusHandle)
      
        PosMatrix[ObjName]['vy']            = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['ax']            = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['ay']            = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['Stand_b']       = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['wExistProb']    = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['wObstacle']     = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['AdditionalSensorAssociated_b']     = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dWidth']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dWidthBase']    = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dLength']       = 0.0*np.ones_like(FusHandle)
 
        # no ExtVid
        PosMatrix[ObjName]['LrrObjIdx']     = 255.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['VidObjIdx']     = 255.0*np.ones_like(FusHandle)
      
      
        # Radar Objects
        PosMatrix[ObjName]['dx_OHY']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dy_OHY']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['vx_OHY']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['vy_OHY']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dbPowerFilt_OHY']        = 0.0*np.ones_like(FusHandle)

      
        # Video Objects
        PosMatrix[ObjName]['dx_VID']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['dy_VID']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['vx_VID']        = 0.0*np.ones_like(FusHandle)
        PosMatrix[ObjName]['vy_VID']        = 0.0*np.ones_like(FusHandle)
      
 
        # fill
        for FusObjIdx in xrange(cDataCVR3.N_FusObj):
            #print FusObj[FusObjIdx]["FusHandle"]
            #print FusHandle
            #print FusObj[FusObjIdx]["FusHandle"] == FusHandle
            #mask = (np.logical_and(0 < FusHandle, FusObj[FusObjIdx]["Handle"] == FusHandle)).nonzero()
            mask = np.logical_and(0 < FusHandle, FusObj[FusObjIdx]["Handle"] == FusHandle)
        
            #if mask.size >0:
            #print len(FusObj[FusObjIdx]["dx"][mask])
            #print FusObj[FusObjIdx]["dx"][mask]
        
            if FusObj[FusObjIdx]["Handle"] is not None:
              PosMatrix[ObjName]['FusHandle'][mask]     = FusObj[FusObjIdx]["Handle"][mask]
              PosMatrix[ObjName]['FusObjIdx'][mask]     = FusObjIdx*np.ones_like(FusObj[FusObjIdx]["Handle"])[mask]
              PosMatrix[ObjName]['dx'][mask]            = FusObj[FusObjIdx]["dx"][mask]
              PosMatrix[ObjName]['dy'][mask]            = FusObj[FusObjIdx]["dy"][mask]
              PosMatrix[ObjName]['vx'][mask]            = FusObj[FusObjIdx]["vx"][mask]

              PosMatrix[ObjName]['vy'][mask]            = FusObj[FusObjIdx]["vy"][mask]
              PosMatrix[ObjName]['ax'][mask]            = FusObj[FusObjIdx]["ax"][mask]
              PosMatrix[ObjName]['ay'][mask]            = FusObj[FusObjIdx]["ay"][mask]
              PosMatrix[ObjName]['Stand_b'][mask]       = FusObj[FusObjIdx]["Stand_b"][mask]
              PosMatrix[ObjName]['wExistProb'][mask]    = FusObj[FusObjIdx]["wExistProb"][mask]
              PosMatrix[ObjName]['wObstacle'][mask]     = FusObj[FusObjIdx]["wObstacle"][mask]
              PosMatrix[ObjName]['AdditionalSensorAssociated_b'][mask] = FusObj[FusObjIdx]["AdditionalSensorAssociated_b"][mask]
              PosMatrix[ObjName]['dWidth'][mask]        = FusObj[FusObjIdx]["dWidth"][mask]
              PosMatrix[ObjName]['dWidthBase'][mask]    = FusObj[FusObjIdx]["dWidthBase"][mask]
              PosMatrix[ObjName]['dLength'][mask]       = FusObj[FusObjIdx]["dLength"][mask]
      
              PosMatrix[ObjName]['dbPowerFilt_OHY'][mask] = FusObj[FusObjIdx]['dbPowerFilt_OHY'][mask] 
  
              # no ExtVid
              PosMatrix[ObjName]['LrrObjIdx'][mask]     = FusObj[FusObjIdx]["LrrObjIdx"][mask] 
              PosMatrix[ObjName]['VidObjIdx'][mask]     = FusObj[FusObjIdx]["VidObjIdx"][mask] 

            
        
  
              # Ohy Objects
              for OhyObjIdx in xrange(cDataCVR3.N_OhyObj):
                  mask = np.logical_and(PosMatrix[ObjName]["LrrObjIdx"] < 255, PosMatrix[ObjName]["LrrObjIdx"] == OhyObjIdx)
                  PosMatrix[ObjName]['dx_OHY'][mask] = OhyObj[OhyObjIdx]['dx'][mask]      
                  PosMatrix[ObjName]['dy_OHY'][mask] = OhyObj[OhyObjIdx]['dy'][mask] 
                  PosMatrix[ObjName]['vx_OHY'][mask] = OhyObj[OhyObjIdx]['vx'][mask]      
                  PosMatrix[ObjName]['vy_OHY'][mask] = OhyObj[OhyObjIdx]['vy'][mask] 

 
              # Video objects
              for VidObjIdx in xrange(cDataCVR3.N_VidObj):
                  mask = np.logical_and(PosMatrix[ObjName]['VidObjIdx'] < 255, PosMatrix[ObjName]['VidObjIdx'] == VidObjIdx)
                  PosMatrix[ObjName]['dx_VID'][mask] = VidObj[VidObjIdx]['dx'][mask]      
                  PosMatrix[ObjName]['dy_VID'][mask] = VidObj[VidObjIdx]['dy'][mask] 
                  PosMatrix[ObjName]['vx_VID'][mask] = VidObj[VidObjIdx]['vx'][mask]      
                  PosMatrix[ObjName]['vy_VID'][mask] = VidObj[VidObjIdx]['vy'][mask] 
          
          
        # -------------------------------------------------------------
        PosMatrix[ObjName]['Valid'] = PosMatrix[ObjName]['FusHandle']>0

    return PosMatrix

  #============================================================================================
  @staticmethod
  def create_Intro(Source, DeviceName,FusObj,OhyObj,VidObj):
        # Intro from  sit.IntroFinder_TC.Intro.i0.Id

        Intro = {}
        Intro['Id']             = kbtools.GetSignal(Source, DeviceName, "sit.IntroFinder_TC.Intro.i0.Id")[1]              
        Intro['ObjectList0']    = kbtools.GetSignal(Source, DeviceName, "sit.IntroFinder_TC.Intro.i0.ObjectList.i0")[1]   
        Intro['ObjectRelation'] = kbtools.GetSignal(Source, DeviceName, "sit.IntroFinder_TC.Intro.i0.ObjectRelation.i0")[1] 
                
            
        FusHandle = Intro['ObjectList0'] 
        
        Intro['FusHandle']     = np.zeros_like(FusHandle)
        Intro['FusObjIdx']     = 255.0*np.ones_like(FusHandle)
        Intro['dx']            = 0.0*np.ones_like(FusHandle)
        Intro['dy']            = 0.0*np.ones_like(FusHandle)
        Intro['dyvBase']       = 0.0*np.ones_like(FusHandle)
               
        
        Intro['vx']            = 0.0*np.ones_like(FusHandle)
        Intro['vy']            = 0.0*np.ones_like(FusHandle)
      
        Intro['ax']            = 0.0*np.ones_like(FusHandle)
        Intro['ay']            = 0.0*np.ones_like(FusHandle)
   
        Intro['Stand_b']         = 0.0*np.ones_like(FusHandle)
        Intro['DriveInvDir_b']   = 0.0*np.ones_like(FusHandle)
        Intro['Drive_b']         = 0.0*np.ones_like(FusHandle) 
        Intro['NotClassified_b'] = 0.0*np.ones_like(FusHandle)
        Intro['Stand_b']         = 0.0*np.ones_like(FusHandle)
        Intro['StoppedInvDir_b'] = 0.0*np.ones_like(FusHandle)
        Intro['Stopped_b']       = 0.0*np.ones_like(FusHandle)
        
        Intro['AdditionalSensorAssociated_b']     = 0.0*np.ones_like(FusHandle)
    
        
        Intro['wExistProb']    = 0.0*np.ones_like(FusHandle)
        Intro['wObstacle']     = 0.0*np.ones_like(FusHandle)
        Intro['dWidth']        = 0.0*np.ones_like(FusHandle)
        Intro['dWidthBase']    = 0.0*np.ones_like(FusHandle)
        Intro['dLength']       = 0.0*np.ones_like(FusHandle)
 
        # no ExtVid
        Intro['LrrObjIdx']     = 255.0*np.ones_like(FusHandle)
        Intro['VidObjIdx']     = 255.0*np.ones_like(FusHandle)
      
      
        # Radar Objects
        Intro['dx_OHY']        = 0.0*np.ones_like(FusHandle)
        Intro['dy_OHY']        = 0.0*np.ones_like(FusHandle)
        Intro['vx_OHY']        = 0.0*np.ones_like(FusHandle)
        Intro['vy_OHY']        = 0.0*np.ones_like(FusHandle)
        Intro['dbPowerFilt_OHY']        = 0.0*np.ones_like(FusHandle)

      
        # Video Objects
        Intro['dx_VID']        = 0.0*np.ones_like(FusHandle)
        Intro['dy_VID']        = 0.0*np.ones_like(FusHandle)
        Intro['vx_VID']        = 0.0*np.ones_like(FusHandle)
        Intro['vy_VID']        = 0.0*np.ones_like(FusHandle)
      
 
        # fill
        for FusObjIdx in xrange(kbtools_user.cDataCVR3.N_FusObj):
            #print FusObj[FusObjIdx]["FusHandle"]
            #print FusHandle
            #print FusObj[FusObjIdx]["FusHandle"] == FusHandle
            #mask = (np.logical_and(0 < FusHandle, FusObj[FusObjIdx]["Handle"] == FusHandle)).nonzero()
            mask = np.logical_and(0 < FusHandle, FusObj[FusObjIdx]["Handle"] == FusHandle)
        
            #if mask.size >0:
            #print len(FusObj[FusObjIdx]["dx"][mask])
            #print FusObj[FusObjIdx]["dx"][mask]
        
            if FusObj[FusObjIdx]["Handle"] is not None:
              Intro['FusHandle'][mask]     = FusObj[FusObjIdx]["Handle"][mask]
              Intro['FusObjIdx'][mask]     = FusObjIdx*np.ones_like(FusObj[FusObjIdx]["Handle"])[mask]
              Intro['dx'][mask]            = FusObj[FusObjIdx]["dx"][mask]
              Intro['dy'][mask]            = FusObj[FusObjIdx]["dy"][mask]
              Intro['dyvBase'][mask]       = FusObj[FusObjIdx]["dyvBase"][mask]
                            
              Intro['vx'][mask]            = FusObj[FusObjIdx]["vx"][mask]

              Intro['vy'][mask]            = FusObj[FusObjIdx]["vy"][mask]
              Intro['ax'][mask]            = FusObj[FusObjIdx]["ax"][mask]
              Intro['ay'][mask]            = FusObj[FusObjIdx]["ay"][mask]
              
              
              Intro['DriveInvDir_b'][mask]   = FusObj[FusObjIdx]["DriveInvDir_b"][mask]
              Intro['Drive_b'][mask]         = FusObj[FusObjIdx]["Drive_b"][mask]
              Intro['NotClassified_b'][mask] = FusObj[FusObjIdx]["NotClassified_b"][mask]
              Intro['Stand_b'][mask]         = FusObj[FusObjIdx]["Stand_b"][mask]
              Intro['StoppedInvDir_b'][mask] = FusObj[FusObjIdx]["StoppedInvDir_b"][mask]
              Intro['Stopped_b'][mask]       = FusObj[FusObjIdx]["Stopped_b"][mask]
                      
              Intro['AdditionalSensorAssociated_b'][mask] = FusObj[FusObjIdx]["AdditionalSensorAssociated_b"][mask]
    
              
              Intro['wExistProb'][mask]    = FusObj[FusObjIdx]["wExistProb"][mask]
              Intro['wObstacle'][mask]     = FusObj[FusObjIdx]["wObstacle"][mask]
              Intro['dWidth'][mask]        = FusObj[FusObjIdx]["dWidth"][mask]
              Intro['dWidthBase'][mask]    = FusObj[FusObjIdx]["dWidthBase"][mask]
              Intro['dLength'][mask]       = FusObj[FusObjIdx]["dLength"][mask]
      
              Intro['dbPowerFilt_OHY'][mask] = FusObj[FusObjIdx]['dbPowerFilt_OHY'][mask] 
  
              # no ExtVid
              Intro['LrrObjIdx'][mask]     = FusObj[FusObjIdx]["LrrObjIdx"][mask] 
              Intro['VidObjIdx'][mask]     = FusObj[FusObjIdx]["VidObjIdx"][mask] 

            
        
  
              # Ohy Objects
              for OhyObjIdx in xrange(kbtools_user.cDataCVR3.N_OhyObj):
                  mask = np.logical_and(Intro["LrrObjIdx"] < 255, Intro["LrrObjIdx"] == OhyObjIdx)
                  Intro['dx_OHY'][mask] = OhyObj[OhyObjIdx]['dx'][mask]      
                  Intro['dy_OHY'][mask] = OhyObj[OhyObjIdx]['dy'][mask] 
                  Intro['vx_OHY'][mask] = OhyObj[OhyObjIdx]['vx'][mask]      
                  Intro['vy_OHY'][mask] = OhyObj[OhyObjIdx]['vy'][mask] 

 
              # Video objects
              for VidObjIdx in xrange(kbtools_user.cDataCVR3.N_VidObj):
                  mask = np.logical_and(Intro['VidObjIdx'] < 255, Intro['VidObjIdx'] == VidObjIdx)
                  Intro['dx_VID'][mask] = VidObj[VidObjIdx]['dx'][mask]      
                  Intro['dy_VID'][mask] = VidObj[VidObjIdx]['dy'][mask] 
                  Intro['vx_VID'][mask] = VidObj[VidObjIdx]['vx'][mask]      
                  Intro['vy_VID'][mask] = VidObj[VidObjIdx]['vy'][mask] 
          
          
        # -------------------------------------------------------------
        Intro['Valid'] = Intro['FusHandle']>0
 
        return Intro

  #============================================================================================
  @staticmethod
  def create_ASF(Source, DeviceName):
    ASF = {}
    
    # time axis + vehicle signals
    ASF["Time"]         = kbtools.GetSignal(Source, DeviceName, "repprew.__b_Rep.__b_RepBase.status")[0]
    ASF["repPrewStatus"] = kbtools.GetSignal(Source, DeviceName, "repprew.__b_Rep.__b_RepBase.status")[1]
    ASF["FirstWarning"] = ASF["repPrewStatus"] == 6
    
    ASF["repRetgStatus"] = kbtools.GetSignal(Source, DeviceName, "repretg.__b_Rep.__b_RepBase.status")[1]
    ASF["Braking"] = ASF["repRetgStatus"] == 6

    ASF["Dam_tReactionTime"] = kbtools.GetSignal(Source, DeviceName, "Dam._.tReactionTime_UW")[1]
    
    ASF["Time_repprew.aAvoid_DEBUG"] =  kbtools.GetSignal(Source, DeviceName, "repprew.aAvoid_DEBUG")[0]
    ASF["repprew.aAvoid_DEBUG"]      = kbtools.GetSignal(Source, DeviceName, "repprew.aAvoid_DEBUG")[1]

    ASF["Time_repretg.aAvoid_DEBUG"] =  kbtools.GetSignal(Source, DeviceName, "repretg.aAvoid_DEBUG")[0]
    ASF["repretg.aAvoid_DEBUG"]      = kbtools.GetSignal(Source, DeviceName, "repretg.aAvoid_DEBUG")[1]

    ASF["repretg.aPartialBraking"] = kbtools.GetSignal(Source, DeviceName, "repretg.aPartialBraking")[1]
    
    ASF["dxSecure"] = kbtools.GetSignal(Source, DeviceName, "Cpr._.dxSecure_SW")[1]

    
    
    # -----------------------------------------------------------------------------------
    # aco - T20
    ASF['t_T20']                    = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acoopti.SetRequest_b1") [0]
    ASF['acoopti_SetRequest_T20']   = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acoopti.SetRequest_b1") [1]
    ASF['acoacoi_SetRequest_T20']   = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acoacoi.SetRequest_b1") [1]
    ASF['acopebp_SetRequest_T20']   = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acopebp.SetRequest_b1") [1]
    ASF['acopebe_SetRequest_T20']   = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acopebe.SetRequest_b1") [1]
        
    ASF['acopebp_RequestValue_T20'] = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acopebp.RequestValue") [1]
    ASF['acopebe_RequestValue_T20'] = kbtools.GetSignal(Source, DeviceName,  "asf.RepStatesReq_T20.acopebe.RequestValue") [1]

    if ASF['acopebp_RequestValue_T20'] is not None:
       ASF['acopebp_RequestValue_T20'] =  ASF['acopebp_RequestValue_T20']/2048.0
    if ASF['acopebe_RequestValue_T20'] is not None:
       ASF['acopebe_RequestValue_T20'] =  ASF['acopebe_RequestValue_T20']/2048.0

    ASF['acoopti_SetRequest']   =  kbtools.resample(ASF['t_T20'], ASF['acoopti_SetRequest_T20'],    ASF["Time"], method='zoh_next')
    ASF['acoacoi_SetRequest']   =  kbtools.resample(ASF['t_T20'], ASF['acoacoi_SetRequest_T20'],    ASF["Time"], method='zoh_next')
    ASF['acopebp_SetRequest']   =  kbtools.resample(ASF['t_T20'], ASF['acopebp_SetRequest_T20'],    ASF["Time"], method='zoh_next')
    ASF['acopebe_SetRequest']   =  kbtools.resample(ASF['t_T20'], ASF['acopebe_SetRequest_T20'],    ASF["Time"], method='zoh_next')
    ASF['acopebp_RequestValue'] =  kbtools.resample(ASF['t_T20'], ASF['acopebp_RequestValue_T20'],  ASF["Time"], method='zoh_next')
    ASF['acopebe_RequestValue'] =  kbtools.resample(ASF['t_T20'], ASF['acopebe_RequestValue_T20'],  ASF["Time"], method='zoh_next')
    
    # -----------------------------------------------------------------------------------
    # ACO States
    
    ASF["acooptiState"]  = kbtools.GetSignal(Source, DeviceName, "aco.States_TC.acooptiState")[1]
    ASF["acoacoiState"]  = kbtools.GetSignal(Source, DeviceName, "aco.States_TC.acoacoiState")[1]

    ASF["acopebpState"]  = kbtools.GetSignal(Source, DeviceName, "aco.States_TC.acopebpState")[1]
    ASF["acopebeState"]  = kbtools.GetSignal(Source, DeviceName, "aco.States_TC.acopebeState")[1]

      
    # -----------------------------------------------------------------------------------
    # Envra
    ASF['Envra_tAbsASF']  = kbtools.GetSignal(Source, DeviceName,  "Envra._.tAbsASF_ul") [1]
       
    
    # -----------------------------------------------------------------------------------
    # Master
    ASF["MasterId"]  = kbtools.GetSignal(Source, DeviceName, "man.MstId")[1]
    ASF["MastSam"]   = ASF["MasterId"] == 1
    ASF["MastSxm"]   = ASF["MasterId"] == 2
    ASF["MastSas"]   = ASF["MasterId"] == 3
    
    ASF["MastSam.activePhase"]  = kbtools.GetSignal(Source, DeviceName, "mastsam.__b_Mst.activePhase")[1]
    
    ASF["MastSam.activePhase.pintsam"] = ASF["MastSam.activePhase"] == 1
    ASF["MastSam.activePhase.pressam"] = ASF["MastSam.activePhase"] == 4

    ASF["MastSas.activePhase"]  = kbtools.GetSignal(Source, DeviceName, "mastsas.__b_Mst.activePhase")[1]
    
    ASF["MastSas.activePhase.pintsas"] = ASF["MastSas.activePhase"] == 1
    ASF["MastSas.activePhase.pressas"] = ASF["MastSas.activePhase"] == 4
    
    # -----------------------------------------------------------------------------------
    # Agents
    AgtList = ['asaxsex', 'asamlam','asamram','axasxas','axamxam','asaslas','asasras']
    AgtNameDict = {"asaxsex":"asaxsex", 
                   "asamlam":"asamlam.__b_ASxxLxx",
                   "asamram":"asamram.__b_ASxxRxx",
                   "axasxas":"axasxas.__b_AXaxXax",
                   "axamxam":"axamxam.__b_AXaxXax",
                   "asaslas":"asaslas.__b_ASxxLxx",
                   "asasras":"asasras.__b_ASxxRxx"}
    
    for k,Agt in enumerate(AgtList):
      if cDataCVR3.verbose: 
        print k, Agt
      #ASF["Time_%s"%Agt]        = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.skill"%AgtNameDict[Agt])[0]
      tmp_Time                  = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.skill"%AgtNameDict[Agt])[0]
      ASF["%s_skill"%Agt]       = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.skill"%AgtNameDict[Agt])[1]
      ASF["%s_skillW"%Agt]      = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.skillW"%AgtNameDict[Agt])[1]
      ASF["%s_plaus"%Agt]       = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.plaus"%AgtNameDict[Agt])[1]
      ASF["%s_status"%Agt]      = kbtools.GetSignal(Source, DeviceName, "%s.__b_Agt.status"%AgtNameDict[Agt])[1]
    
    
      # if necessary resample signal to ASF["Time"]
      if (tmp_Time is not None) and (ASF["Time"] is not tmp_Time):
        print "!!!! resample necessary for", Agt, len(tmp_Time), len(ASF["Time"])
        if 0:
          ASF["%s_time_org"%Agt]   = tmp_Time
          ASF["%s_skill_org"%Agt]  = np.copy(ASF["%s_skill"%Agt])
          ASF["%s_skillW_org"%Agt] = np.copy(ASF["%s_skillW"%Agt])
          ASF["%s_plaus_org"%Agt]  = np.copy(ASF["%s_plaus"%Agt])
          ASF["%s_status_org"%Agt] = np.copy(ASF["%s_status"%Agt])
        
        # resample
        ASF["%s_skill"%Agt]  =  kbtools.resample(tmp_Time, ASF["%s_skill"%Agt],  ASF["Time"], method='zoh_next')
        ASF["%s_skillW"%Agt] =  kbtools.resample(tmp_Time, ASF["%s_skillW"%Agt], ASF["Time"], method='zoh_next')
        ASF["%s_plaus"%Agt]  =  kbtools.resample(tmp_Time, ASF["%s_plaus"%Agt],  ASF["Time"], method='zoh_next')
        ASF["%s_status"%Agt] =  kbtools.resample(tmp_Time, ASF["%s_status"%Agt], ASF["Time"], method='zoh_next')

      # scale skill and skillW signals 
      if ASF["%s_skill"%Agt] is not None:
        ASF["%s_skill"%Agt] =  ASF["%s_skill"%Agt] /256.0
        if "%s_time_org"%Agt in ASF:
          ASF["%s_skill_org"%Agt] =  ASF["%s_skill_org"%Agt] /256.0
 
      if ASF["%s_skillW"%Agt] is not None:
        ASF["%s_skillW"%Agt] = ASF["%s_skillW"%Agt]/256.0
        if "%s_time_org"%Agt in ASF:
          ASF["%s_skillW_org"%Agt] =  ASF["%s_skillW_org"%Agt] /256.0

      #print len(ASF["%s_skill"%Agt])
      #print len(ASF["%s_skillW"%Agt])
      #print len(ASF["%s_plaus"%Agt])
    
    if ASF["asaxsex_skill"] is not None:
      ASF["aAvoidance"]          = ASF["asaxsex_skill"]*(-16.0)
      ASF["aAvoidancePredicted"] = ASF["asaxsex_skillW"] /256.0*(-16.0)
    
    # -----------------------------------------------------------------------------------------
    ASF["Time_pressas_PSSBrakeInterventionInProgress"], ASF["pressas_PSSBrakeInterventionInProgress"]  = kbtools.GetSignal(Source, DeviceName, "pressas.__b_Pha.__b_PhaBase.PSSBrakeInterventionInProgress_")
    ASF["Time_repretg_ExecutionStatus"], ASF["repretg_ExecutionStatus"]  = kbtools.GetSignal(Source, DeviceName, "repretg.__b_Rep.__b_RepBase.ExecutionStatus")

    
    return ASF
    
  #============================================================================================
  @staticmethod
  def create_ATS(Source, DeviceName,FusObj):
    # ACC Target Selection
    # ATS-Objects (0,1,2,3,4)
    #  0 first vehicle in ego lane
    #  1 second vehicle in ego lane
    #  2 first vehicle in left adjacent lane
    #  3 first vehicle in right adjacent lane
      
  
    ATS = {}

    ATS["Time"]                     = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.NrFollowPO")[0]
    ATS["NrFollowPO"]               = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.NrFollowPO")[1]
    ATS["dxMaxFollowPO"]            = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.dxMaxFollowPO")[1]
    ATS["plausLimitAcceptFollowPO"] = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.plausLimitAcceptFollowPO")[1]
    ATS["plausLimitRejectFollowPO"] = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.plausLimitRejectFollowPO")[1]
    
    for ATSObjIdx in xrange(cDataCVR3.N_ATSObj):
        ATS[ATSObjIdx] = {}
        ATS[ATSObjIdx]["Time"]        = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.Handle"%ATSObjIdx)[0]
        ATS[ATSObjIdx]["Handle"]      = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.Handle"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["Index"]       = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.Index"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["dycAct"]      = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.dycAct"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["dycHist"]     = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.dycHist"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["CutIn_b"]     = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.flags.flags.CutIn_b"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["LeftLane_b"]  = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.flags.flags.LeftLane_b"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["OwnLane_b"]   = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.flags.flags.OwnLane_b"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["RightLane_b"] = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.flags.flags.RightLane_b"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["lpb"]         = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.lpb"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["plaus"]       = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.plaus"%ATSObjIdx)[1]
        ATS[ATSObjIdx]["wCutIn"]      = kbtools.GetSignal(Source, DeviceName, "ats.Po_TC.PO.i%d.wCutIn"%ATSObjIdx)[1]

        ATSHandle = ATS[ATSObjIdx]["Handle"] 
        ATS[ATSObjIdx]['FusHandle']     = 0.0*np.ones_like(ATSHandle)
        ATS[ATSObjIdx]['FusObjIdx']     = 255.0*np.ones_like(ATSHandle)
        ATS[ATSObjIdx]['dx']            = 0.0*np.ones_like(ATSHandle)
        ATS[ATSObjIdx]['dy']            = 0.0*np.ones_like(ATSHandle)
        ATS[ATSObjIdx]['vx']            = 0.0*np.ones_like(ATSHandle)
 
        # fill
        for FusObjIdx in xrange(cDataCVR3.N_FusObj):
            #print FusObj[FusObjIdx]["FusHandle"]
            #print ATSHandle
            mask = np.logical_and(0 < ATSHandle, FusObj[FusObjIdx]["Handle"] == ATSHandle)
        
            #if mask.size >0:
            #print len(FusObj[FusObjIdx]["dx"][mask])
            #print FusObj[FusObjIdx]["dx"][mask]
        
            if FusObj[FusObjIdx]["Handle"] is not None:
                ATS[ATSObjIdx]['FusHandle'][mask]     = FusObj[FusObjIdx]["Handle"][mask]
                ATS[ATSObjIdx]['FusObjIdx'][mask]     = FusObjIdx*np.ones_like(FusObj[FusObjIdx]["Handle"])[mask]
                ATS[ATSObjIdx]['dx'][mask]            = FusObj[FusObjIdx]["dx"][mask]
                ATS[ATSObjIdx]['dy'][mask]            = FusObj[FusObjIdx]["dy"][mask]
                ATS[ATSObjIdx]['vx'][mask]            = FusObj[FusObjIdx]["vx"][mask]
        # -------------------------------------------------------------
        ATS[ATSObjIdx]['Valid'] = ATS[ATSObjIdx]['FusHandle']>0

    return ATS
 
  #============================================================================================
  @staticmethod
  def create_VBOX_IMU(Source):
        
        VBOX_IMU = {}        
        # ----------------------------------------------------------------        
        # longitudinal acceleration
        VBOX_IMU["Time_IMU_X_Acc"],VBOX_IMU["IMU_X_Acc"]       = kbtools.GetSignal(Source, "IMU_XAccel_and_YawRate", "X_Accel")
        
        
        return VBOX_IMU

  #============================================================================================
  @staticmethod
  def create_J1939(Source):
        
        J1939 = {}        
        # ----------------------------------------------------------------        
        # longitudinal acceleration
        J1939["Time_XBRAccDemand"],J1939["XBRAccDemand"]       = kbtools.GetSignal(Source, "XBR", "ExtAccelerationDemand")

        
        return J1939
       
        
  #============================================================================================
  @staticmethod  
  def create_FUS_segment_list(CVR3_sig):
    # create list of segments of all FUS objects

    segment_list = []
    for FusObjIdx in xrange(cDataCVR3.N_FusObj):
      Handle = CVR3_sig['FusObj'][FusObjIdx]["Handle"]>0
          
      handle_list = kbtools.scan4handles(Handle)
    
      # create tracks from handle list and append to track list
      for start_idx, end_idx in handle_list:
        idx = range(start_idx,end_idx+1,1)
        current_segment = {'idx'         :idx,
                          'Time'       :CVR3_sig['FusObj'][FusObjIdx]['Time'][idx],
                          'dx'         :CVR3_sig['FusObj'][FusObjIdx]['dx'][idx],
                          'dy'         :CVR3_sig['FusObj'][FusObjIdx]['dy'][idx],
                          'vx'         :CVR3_sig['FusObj'][FusObjIdx]['vx'][idx],
                          'vy'         :CVR3_sig['FusObj'][FusObjIdx]['vy'][idx],
                          'ax'         :CVR3_sig['FusObj'][FusObjIdx]['ax'][idx],
                          'ay'         :CVR3_sig['FusObj'][FusObjIdx]['ay'][idx],
                          'Stand_b'    :CVR3_sig['FusObj'][FusObjIdx]['Stand_b'][idx],
                          'wExistProb' :CVR3_sig['FusObj'][FusObjIdx]['wExistProb'][idx],
                          'wObstacle'  :CVR3_sig['FusObj'][FusObjIdx]['wObstacle'][idx],
                          'vxvRef'     :CVR3_sig['EgoVeh']['vxvRef'][idx],
                          'axvRef'     :CVR3_sig['EgoVeh']['axvRef'][idx],
                          'kapCurvTraj':CVR3_sig['EgoVeh']['kapCurvTraj'][idx],
                        }
        segment_list.append(current_segment)

    return segment_list

 
  #============================================================================================
  @staticmethod  
  def create_PosMatrix_segment_list(CVR3_sig, ObjName='S1'):
    # create list of segments of a given object from the Position Matrix
    
    if 0:
      FigNr =100
    
      fig = pl.figure(FigNr); 
      fig.suptitle('create_PosMatrix_segment_list')
      sp = fig.add_subplot(311)
      sp.plot(CVR3_sig['Time'], CVR3_sig['vxvRef'],'b-')
      mask = CVR3_sig['PosMatrix'][ObjName]['Valid']>0.5
      sp.plot(CVR3_sig['Time'][mask], CVR3_sig['vxvRef'][mask],'rx')
      sp.grid()
   
      sp = fig.add_subplot(312)
      sp.plot(CVR3_sig['PosMatrix'][ObjName]['Time'], CVR3_sig['PosMatrix'][ObjName]['Valid'],'x-')
      sp.grid()
      sp.set_ylim(-0.1,1.1) 
  
      sp = fig.add_subplot(313)
      sp.plot(CVR3_sig['PosMatrix'][ObjName]['Time'], CVR3_sig['PosMatrix'][ObjName]['dx'],'x-')
      sp.grid()
  
  
      fig.show()

    
    Valid = CVR3_sig['PosMatrix'][ObjName]['Valid']
    
    
    handle_list = kbtools.scan4handles(Valid)
    
    segment_list = []
    # create tracks from handle list and append to track list
    for start_idx, end_idx in handle_list:
      idx = range(start_idx,end_idx+1,1)
      current_track = {'idx'      :idx,
                        'Time'    :CVR3_sig['PosMatrix'][ObjName]['Time'][idx],
                        'FusIdx'  :CVR3_sig['PosMatrix'][ObjName]['FusObjIdx'][idx],
                        'dx'      :CVR3_sig['PosMatrix'][ObjName]['dx'][idx],
                        'dy'      :CVR3_sig['PosMatrix'][ObjName]['dy'][idx],
                        'vx'      :CVR3_sig['PosMatrix'][ObjName]['vx'][idx],
                        'vy'      :CVR3_sig['PosMatrix'][ObjName]['vy'][idx],
                        'ax'      :CVR3_sig['PosMatrix'][ObjName]['ax'][idx],
                        'ay'      :CVR3_sig['PosMatrix'][ObjName]['ay'][idx],
                        'Stand_b' :CVR3_sig['PosMatrix'][ObjName]['Stand_b'][idx],
                        'wExistProb' :CVR3_sig['PosMatrix'][ObjName]['wExistProb'][idx],
                        'wObstacle'  :CVR3_sig['PosMatrix'][ObjName]['wObstacle'][idx],
                        'vxvRef'     :CVR3_sig['EgoVeh']['vxvRef'][idx],
                        'axvRef'     :CVR3_sig['EgoVeh']['axvRef'][idx],
                        'kapCurvTraj':CVR3_sig['EgoVeh']['kapCurvTraj'][idx],
                    }
      segment_list.append(current_track)

    return segment_list
  #============================================================================================
  @staticmethod
  def FusObjObstacleIsValid(CVR3_sig,FusObjIdx):
  
      # Flag: ObstacleIsValid
    
      # parameter   (parameter values of 1.2.1.8 release)
      P_dVarYLimitStationary_uw = 1.0 # K1 is 1.0 as well
      P_wExistStationary_uw     = 0.8 # K1 is 0.8 as well
      P_wGroundReflex_ub        = 0.1  
  
      # signals  
      wExistProb    = CVR3_sig['FusObj'][FusObjIdx]['wExistProb']
      dVarYvBase    = CVR3_sig['FusObj'][FusObjIdx]['dVarYvBase']
      wGroundReflex = CVR3_sig['FusObj'][FusObjIdx]['wGroundReflex']
    
      # condition
      ObstacleIsValid = (wExistProb >= P_wExistStationary_uw) &\
                        (dVarYvBase <= P_dVarYLimitStationary_uw) &\
                        (wGroundReflex <= P_wGroundReflex_ub)
    
      return ObstacleIsValid
    
  #============================================================================================
  @staticmethod
  def FusObjObstacleIsRelevant(CVR3_sig,FusObjIdx):
      # -------------------------------------------------
      # Flag: ObstacleIsRelevant
    
      # Relevant parameter values of 1.2.1.8 release
      P_dOutOfSightSO_sw = 100.0
      P_wObstacleProbFar_uw = 0.5
      P_wObstacleNear_uw = 0.7
      P_wObstacleNearQClass_uw = 0.7
      P_dLengthFar_sw = 1.0
      P_wConstructionElementFar_ub = 0.003
      P_dVarYLimitFar_uw = 0.5
    
      dx                 = CVR3_sig['FusObj'][FusObjIdx]['dx']
      wClassObstacle     = CVR3_sig['FusObj'][FusObjIdx]['wClassObstacle']
      wConstElem         = CVR3_sig['FusObj'][FusObjIdx]['wConstElem']
      dLength            = CVR3_sig['FusObj'][FusObjIdx]['dLength']
      dVarYvBase         = CVR3_sig['FusObj'][FusObjIdx]['dVarYvBase']
      wClassObstacleNear = CVR3_sig['FusObj'][FusObjIdx]['wClassObstacleNear']
      qClass             = CVR3_sig['FusObj'][FusObjIdx]['qClass']
    
      # Check if the stationary object is a relevant obstacle.
      # If one of the classifieres (near or far) and for near also the qClass value
      # is above the threshold, the obstacle is relevant.
      ObstacleIsRelevant = (dx <= P_dOutOfSightSO_sw) &\
          (
          (wClassObstacle >= P_wObstacleProbFar_uw) &\
          (wConstElem < P_wConstructionElementFar_ub) &\
          (dLength > P_dLengthFar_sw) &\
          (dVarYvBase < P_dVarYLimitFar_uw)
          ) |\
          (\
          (wClassObstacleNear >= P_wObstacleNearQClass_uw) &\
          (qClass             >= P_wObstacleNearQClass_uw)\
          )
        
      return ObstacleIsRelevant
  #============================================================================================
  @staticmethod
  def calc_AEBS_warning(CVR3_sig):
    # --------------------------------------------------------------
    # AEBS warning
    #  res['t_start_AEBS_Warning'] 
    #  res['dx_start_AEBS_Warning'] 
    #  res['vxvRef_start_AEBS_Warning'] 
    
    if cDataCVR3.verbose:
      print "calc_AEBS_warning()"
    
    
    res ={}
    res['t_start_AEBS_Warning'] = None
    res['dx_start_AEBS_Warning'] = None
    res['vxvRef_start_AEBS_Warning'] = None
    
    if 'ASF' not in CVR3_sig:
      if cDataCVR3.verbose:
        print "  -> no AEBS warning signals found"
      return res
        
    t              = CVR3_sig['ASF']['Time']  
    AEBS_warning   = CVR3_sig['ASF']['FirstWarning']
    AEBS_warning_list = kbtools.scan4handles(AEBS_warning)

    # ---------------------------------------------   
    # How much warnings do we have?
    #  -> select one AEBS_warning_interval
    if len(AEBS_warning_list)==0:
      # no warning
      if cDataCVR3.verbose:
        print "  -> no AEBS warning found"
      return res
    elif len(AEBS_warning_list)==1:
      # only one warning
      if cDataCVR3.verbose:
        print "  -> only one AEBS warning"
      AEBS_warning_interval = AEBS_warning_list[0]   
    else:
      # multiple warnings
      if cDataCVR3.verbose:
        print "  -> %d warning"%len(AEBS_warning_list)      
      # more than one segment exists
      # chose the longest segment
      AEBS_warning_interval = AEBS_warning_list[0]
      for k,interval in enumerate(AEBS_warning_list):
        if cDataCVR3.verbose:
          print "  %d. interval"%k, interval      
        if (interval[1] - interval[0]) > (AEBS_warning_interval[1] - AEBS_warning_interval[0]):
          AEBS_warning_interval = interval
      #AEBS_warning_interval = AEBS_warning_list[0]
         
    # ---------------------------------------------   
    if cDataCVR3.verbose:
      print "  AEBS_warning_interval", AEBS_warning_interval

    # idx and t of start and stop of AEBS warning  
    start_idx = AEBS_warning_interval[0]
    stop_idx  = AEBS_warning_interval[1]
    t_start_AEBS_warning = t[start_idx]
    t_stop_AEBS_warning  = t[stop_idx]
    if cDataCVR3.verbose:
      print "  start_idx, stop_idx:", start_idx, stop_idx
      print "  t[start_idx], t[stop_idx]:", t_start_AEBS_warning, t_stop_AEBS_warning

    # t and dx at start of AEBS warning            
    res['t_start_AEBS_Warning']  = t[start_idx]
    res['dx_start_AEBS_Warning'] = CVR3_sig['PosMatrix']['S1']['dx'][start_idx]
    if cDataCVR3.verbose:
      print "  t_start_AEBS_Warning  ", res['t_start_AEBS_Warning']
      print "  dx_start_AEBS_Warning ", res['dx_start_AEBS_Warning']
         
    res['t_stop_AEBS_Warning'] = t[stop_idx]
    if cDataCVR3.verbose:
      print "  t_stop_AEBS_Warning  ", res['t_stop_AEBS_Warning']
        
         
    # ego vehicle speed at start of AEBS warning          
    if CVR3_sig["EgoVeh"]["Time"] is not t:
      print "CVR3_sig['EgoVeh']['Time'] is not t"
    res['vxvRef_start_AEBS_Warning']   = CVR3_sig["EgoVeh"]["vxvRef"][start_idx]
    if cDataCVR3.verbose:
      print "  vxvRef_start_AEBS_Warning  ",res['vxvRef_start_AEBS_Warning']
    

    return res
  #============================================================================================
  @staticmethod
  def calc_S1_performance(CVR3_sig, given_t_center = None,given_FusObjIdx = None):

    if cDataCVR3.verbose:
      print "calc_S1_performance:()"

    # AEBS Warning
    res = cDataCVR3.calc_AEBS_warning(CVR3_sig)
  
    if res['t_start_AEBS_Warning'] is not None:
      # if AEBS Warning present, use it to determine FusObjIdx and FusHandle
      t = CVR3_sig['ASF']['Time']
      t_center = 0.5*(res['t_start_AEBS_Warning']+res['t_stop_AEBS_Warning']) 
      PosS1_FusObjIdx = int(CVR3_sig['PosMatrix']['S1']['FusObjIdx'][t>=t_center][0])
      #PosS1_FusHandle = int(CVR3_sig['FusObj'][PosS1_FusObjIdx]["Handle"][t>=t_center][0])
      PosS1_FusHandle = int(CVR3_sig['PosMatrix']['S1']['FusHandle'][t>=t_center][0])
      
      if cDataCVR3.verbose:
        print "  t_center", t_center
        print "  PosS1_FusObjIdx", PosS1_FusObjIdx
        print "  PosS1_FusHandle", PosS1_FusHandle
      res['t_center'] = t_center     
      res['PosS1_FusObjIdx']  = PosS1_FusObjIdx 
      res['PosS1_FusHandle']  = PosS1_FusHandle
      
      ##print CVR3_sig['PosMatrix']['S1']['FusHandle']
      ##print CVR3_sig['PosMatrix']['S1']['FusHandle'][t>=t_center]
      
      if CVR3_sig['PosMatrix']['S1']['Time'] is not t:
        print " CVR3_sig['PosMatrix']['S1']['Time'] is not t"
      Valid = CVR3_sig['PosMatrix']['S1']['FusHandle'] == PosS1_FusHandle
      
      ##print Valid      
      start_idx, stop_idx = kbtools.getIntervalAroundEvent(t,t_center,Valid)
      S1_interval = [start_idx, stop_idx]
      
      
      if cDataCVR3.verbose:
        print "-> res['t_center']:",  res['t_center']
        print "-> res['PosS1_FusObjIdx']:",  res['PosS1_FusObjIdx']
        print "-> res['PosS1_FusHandle']:",  res['PosS1_FusHandle']
        print "S1_interval", S1_interval
        
    else:
  
      # -----------------------------------------------------
      #  create S1_interval
      if cDataCVR3.verbose:
        print "  create S1_interval ..."
      # t_center : time stamp of last uninterrupted S1 appearance
      t     = CVR3_sig['PosMatrix']['S1']['Time']
      Valid = CVR3_sig['PosMatrix']['S1']['Valid']
      S1_appearance_list = kbtools.scan4handles(Valid)
    
      if cDataCVR3.verbose:
        print "  Number of S1 segments:", len(S1_appearance_list)
        print "  No. Start and Stop Idx, Start and Stop time"
        for k,x in enumerate(S1_appearance_list):
          print "  ",k, x, t[x]
    
      if len(S1_appearance_list)==0:
         # no S1 obj
         S1_interval = None
         pass 
      elif len(S1_appearance_list)==1:
         # only one segment exists
         S1_interval = S1_appearance_list[0]
      elif len(S1_appearance_list)>1:
         # more than one segment exists
         if res['t_start_AEBS_Warning'] is not None:
           # AEBS warning present
           # chose first segment with AEBS warning
           length = 0
           t_AEBS = res['t_start_AEBS_Warning']
           for k in S1_appearance_list:
             if (t[k[0]] <= t_AEBS) and (t_AEBS <= t[k[1]]):
              S1_interval = k
         else:
           # chose the first segment
           S1_interval = S1_appearance_list[0]
     
         # more than one segment exists
         # chose the longest segment
         '''
         length = 0
         for k in S1_appearance_list:
           if k[1] - k[0] > 0:
              length = k[1] - k[0] 
              S1_interval = k
         '''
      if cDataCVR3.verbose:
        print "S1_interval: ", S1_interval

      #------------------------------------------------------------
      # determine 
      #    't_center'
      #    'PosS1_FusObjIdx' - Index FusObj corresponding to PosS1
      if cDataCVR3.verbose:
        print "determine 't_center' and 'PosS1_FusObjIdx' ... "

      if S1_interval is not None:
        t_center = np.mean(t[S1_interval])
        PosS1_FusObjIdx_at_t_center = int(CVR3_sig['PosMatrix']['S1']['FusObjIdx'][t>=t_center][0])
      else:
        # use given given_t_center and given_FusObjIdx
        if given_t_center is not None and given_FusObjIdx is not None:
          t_center = given_t_center 
          PosS1_FusObjIdx_at_t_center = given_FusObjIdx
        else:
          raise
        
      # Handle at t_center
      PosS1_FusHandle_at_t_center = int(CVR3_sig['FusObj'][PosS1_FusObjIdx_at_t_center]["Handle"][t>=t_center][0])

      if cDataCVR3.verbose:
        print "S1_interval: ", S1_interval
        print "t_center", t_center
        print "PosS1_FusObjIdx_at_t_center", PosS1_FusObjIdx_at_t_center
        print "PosS1_FusHandle_at_t_center", PosS1_FusHandle_at_t_center
 
      res['t_center'] = t_center
      res['PosS1_FusObjIdx']  = PosS1_FusObjIdx_at_t_center 
      res['PosS1_FusHandle']  = PosS1_FusHandle_at_t_center
      if cDataCVR3.verbose:
        print "-> res['t_center']:",  res['t_center']
        print "-> res['PosS1_FusObjIdx']:",  res['PosS1_FusObjIdx']
        print "-> res['PosS1_FusHandle']:",  res['PosS1_FusHandle']
    
    #------------------------------------------------------------
    # determine start and stop of FusObj correspond to PosS1
    if cDataCVR3.verbose:
      print "determine start and stop of FusObj correspond to PosS1 ..."
    
    t_center = res['t_center']
    PosS1_FusObjIdx = res['PosS1_FusObjIdx']
    PosS1_FusHandle = res['PosS1_FusHandle']
    
    bool_signal = CVR3_sig['FusObj'][PosS1_FusObjIdx]["Handle"] == PosS1_FusHandle
    start_idx, stop_idx = kbtools.getIntervalAroundEvent(t,t_center,bool_signal)
    if cDataCVR3.verbose:
      print "start_idx, stop_idx:", start_idx, stop_idx
      print "t[start_idx], t[stop_idx]:", t[start_idx], t[stop_idx]
      if S1_interval is not None:
        print "S1 dx ", CVR3_sig['PosMatrix']['S1']['dx'][S1_interval]
      print "FUS dx ", CVR3_sig['FusObj'][PosS1_FusObjIdx]['dx'][start_idx], CVR3_sig['FusObj'][PosS1_FusObjIdx]['dx'][stop_idx]
      #print "FUS dx ", CVR3_sig['FusObj'][PosS1_FusObjIdx]['dx'][(start_idx, stop_idx)]
    res['t_start_FUS']         = t[start_idx]
    res['t_stop_FUS']          = t[stop_idx]
    res['max_dx_FUS_detected']   = CVR3_sig['FusObj'][PosS1_FusObjIdx]['dx'][start_idx]
    res['t_max_dx_FUS_detected'] = CVR3_sig['FusObj'][PosS1_FusObjIdx]['Time'][start_idx]

    # ego vehicle speed at start of AEBS warning          
    if CVR3_sig["EgoVeh"]["Time"] is not t:
       print "CVR3_sig['EgoVeh']['Time'] is not t"
    res['vxvRef_max_dx_FUS_detected']   = CVR3_sig["EgoVeh"]["vxvRef"][start_idx]
    if cDataCVR3.verbose:
       print "vxvRef_max_dx_FUS_detected  ",res['vxvRef_max_dx_FUS_detected']

       
   
    # ----------------------------------------------------------
    # determine start of obstacle classifier
    if cDataCVR3.verbose:
      print "determine start of obstacle classifier ..."

    ObstacleIsValid    = kbtools_user.cDataCVR3.FusObjObstacleIsValid(CVR3_sig,PosS1_FusObjIdx)
    ObstacleIsRelevant = kbtools_user.cDataCVR3.FusObjObstacleIsRelevant(CVR3_sig,PosS1_FusObjIdx)
    Obstacle = ObstacleIsValid & ObstacleIsRelevant
  
    try:
      if S1_interval is not None:
        Obstacle_start_idx, Obstacle_stop_idx = kbtools.getIntervalAroundEvent(t,t_center,Obstacle)
      else:
        # no S1 present
        Obstacle_start_idx = np.nonzero(Obstacle)[0][0]
        Obstacle_stop_idx  = np.nonzero(Obstacle)[0][-2]
      res['max_dx_FUS_obstacle']   = CVR3_sig['FusObj'][PosS1_FusObjIdx]['dx'][Obstacle_start_idx]
      res['t_max_dx_FUS_obstacle'] = CVR3_sig['FusObj'][PosS1_FusObjIdx]['Time'][Obstacle_start_idx]
    except:
      res['max_dx_FUS_obstacle']   = None
      res['t_max_dx_FUS_obstacle'] = None
    if cDataCVR3.verbose:
        print "res['t_max_dx_FUS_obstacle']",  res['t_max_dx_FUS_obstacle']
        print "res['max_dx_FUS_obstacle']",    res['max_dx_FUS_obstacle']
        
    
    
    if S1_interval is not None:
      res['max_dx_S1']           = CVR3_sig['PosMatrix']['S1']['dx'][S1_interval[0]]
      res['t_max_dx_S1']         = CVR3_sig['PosMatrix']['S1']['Time'][S1_interval[0]]
      res['min_dx_S1']           = CVR3_sig['PosMatrix']['S1']['dx'][S1_interval[1]]
      res['t_min_dx_S1']         = CVR3_sig['PosMatrix']['S1']['Time'][S1_interval[1]]
    else:    
      res['max_dx_S1']           = None
      res['t_max_dx_S1']         = None
      res['min_dx_S1']           = None
      res['t_min_dx_S1']         = None
      
    
    
    return res

  #============================================================================================
  @staticmethod
  def plot_CVR3_FusObj(sig, FigNr=100,FusObjIdx=0, xlim = None):
    # plot given fusion object (FusObj)
    # sig : dict with signals
    # FigNr : figure number for plot
    # FusObjIdx = Fusion object index 0,1, ... 31
    
    
    CVR3 = sig['FusObj']
    
    # obstacle classifier
    ObstacleIsValid    = cDataCVR3.FusObjObstacleIsValid(sig,FusObjIdx)
    ObstacleIsRelevant = cDataCVR3.FusObjObstacleIsRelevant(sig,FusObjIdx)

    # FusObj is in ego lane
    kapCurvTraj = sig["EgoVeh"]["kapCurvTraj"]
    dx          = sig['FusObj'][FusObjIdx]['dx']
    dy          = sig['FusObj'][FusObjIdx]['dy'] 
    
    dy_path = 0.5*kapCurvTraj*dx**2
    FusObjIsInEgoLane = ((dy_path-dy) < 0.9) & ((dy_path-dy) > -0.9)
    
     
    
    # -------------------------------------------------
    fig = pl.figure(FigNr)
    
    fig.suptitle('FusObj[%s]'%FusObjIdx)
    
    # S1 available
    ax = fig.add_subplot(611)
    ax.plot(sig['PosMatrix']['L1']['Time'], sig['PosMatrix']['L1']['Valid']+4)
    ax.plot(sig['PosMatrix']['S1']['Time'], sig['PosMatrix']['S1']['Valid']+2)
    ax.plot(sig['PosMatrix']['R1']['Time'], sig['PosMatrix']['R1']['Valid'] )
    ax.legend(('L1','S1','R1'))
    ax.grid()
    ax.set_ylim(-0.1,5.1)
    if xlim:
      ax.set_xlim(xlim)
    
     
    
    # dx
    ax = fig.add_subplot(612)
    ax.plot(CVR3[FusObjIdx]['Time'], CVR3[FusObjIdx]['dx'] )
    ax.plot(CVR3[FusObjIdx]['Time'], CVR3[FusObjIdx]['dx_OHY'] )
    ax.plot(CVR3[FusObjIdx]['Time'], CVR3[FusObjIdx]['dx_VID'] )
        
    ax.legend(('dx FUS','dx OHY','dx VID'))
    ax.grid()
    if xlim:
      ax.set_xlim(xlim)

    # ObstacleIsValid, ObstacleIsRelevant
    ax = fig.add_subplot(613)
    ax.plot(CVR3[FusObjIdx]['Time'], ObstacleIsValid+6,'b' )
    ax.plot(CVR3[FusObjIdx]['Time'], ObstacleIsRelevant+4,'r' )
    ax.plot(CVR3[FusObjIdx]['Time'], FusObjIsInEgoLane+2,'m' )
    ax.plot(CVR3[FusObjIdx]['Time'], ObstacleIsValid&ObstacleIsRelevant&FusObjIsInEgoLane,'k' )
    
    
    
    ax.legend(('ObstacleIsValid+4','ObstacleIsRelevant+2','IsEgoLane','All'))
    ax.grid()
    ax.set_ylim(-0.1,7.1)
    if xlim:
      ax.set_xlim(xlim)
    
    
    
    # -----------------------------------------------
    # kapCurvTraj
    
    
    
    ax = fig.add_subplot(614)
    #ax.plot(sig["Time"], sig["psiDtOpt"] ,'b' )
    #ax.legend(('psiDtOpt',))
    ax.plot(sig["Time"],dy_path  ,'b' )
    ax.plot(sig["Time"],dy ,'r' )
    ax.plot(CVR3[FusObjIdx]['Time'], CVR3[FusObjIdx]['dy_OHY'], 'g' )
    ax.plot(CVR3[FusObjIdx]['Time'], CVR3[FusObjIdx]['dy_VID'], 'm' )

    ax.legend(('kap/2*dx^2','dy FUS','dy OHY','dy VID'))
    
    ax.grid()
    ax.set_ylim(-3.1,3.1)
    if xlim:
      ax.set_xlim(xlim)
    
  
    ax = fig.add_subplot(615)
    #ax.plot(sig["Time"], sig["psiDtOpt"] ,'b' )
    #ax.legend(('psiDtOpt',))
    ax.plot(sig["Time"],dy_path-dy  ,'b' )
    cond = (dy_path-dy) > 0.9
    ax.plot(sig["Time"][cond], (dy_path-dy)[cond] ,'r.' )
    cond = (dy_path-dy) < -0.9
    ax.plot(sig["Time"][cond], (dy_path-dy)[cond] ,'r.' )
    ax.legend(('deviation',))
    
    ax.grid()
    ax.set_ylim(-3.1,3.1)
    if xlim:
      ax.set_xlim(xlim)
      
    # ---------------------------------------------------------
    ax = fig.add_subplot(616)
    #ax.plot(sig["Time"], sig["psiDtOpt"] ,'b' )
    #ax.legend(('psiDtOpt',))
    ax.plot(sig["Time"],sig['FusObj'][FusObjIdx]['AdditionalSensorAssociated_b']  ,'b' )
    ax.legend(('AdditionalSensorAssociated_b',))
    
    ax.grid()
    ax.set_ylim(-3.1,3.1)
    if xlim:
      ax.set_xlim(xlim)
      
      
    fig.show()
    
  #============================================================================================
  @staticmethod
  def plot_CVR3_PosMatrix(sig, FigNr=200,ObjName='S1',xlim = None):
    # plot given object of Position Matrix in detail
    # sig : dict with signals
    # FigNr : figure number for plot
    # ObjName = 'S1', 'L1', 'R1', 'S2', 'L2', 'R2'

    
    CVR3 = sig['PosMatrix']
    
    fig = pl.figure(FigNr)
    
    fig.suptitle('%s'%ObjName)
    
    # ---------------------------------------------------
    # S1 available
    ax = fig.add_subplot(811)
    #ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['FusHandle']>0 )
   
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['Valid'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['AdditionalSensorAssociated_b']+2.0 )
    ax.legend(('%s avail.'%ObjName,'AdditionalSensorAssociated_b+2'))
    ax.grid()
   
    ax.set_ylim(-0.1,4.1)
    if xlim:
      ax.set_xlim(xlim)

    # ---------------------------------------------------
    # S1 FUS Index
    ax = fig.add_subplot(812)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['FusObjIdx'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['LrrObjIdx'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['VidObjIdx'] )
    
    ax.legend(('FusObjIdx','LrrObjIdx','VidObjIdx'))
    ax.grid()
    #ax.set_ylim(-0.1,33.1) 
    if xlim:
      ax.set_xlim(xlim)

    # ---------------------------------------------------
    # dx
    ax = fig.add_subplot(813)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dx'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dx_OHY'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dx_VID'] )
     
    ax.legend(('dx FUS','dx OHY','dx VID'))
    ax.grid()
    if xlim:
      ax.set_xlim(xlim)

    # ---------------------------------------------------
    # dy
    ax = fig.add_subplot(814)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dy'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dy_OHY'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dy_VID'] )
    ax.legend(('dy FUS','dy OHY','dy VID'))
    ax.grid()
    if xlim:
      ax.set_xlim(xlim)

    # ---------------------------------------------------
    # vx
    ax = fig.add_subplot(815)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['vx'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['vx_OHY'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['vx_VID'] )

    ax.legend(('vx FUS','vx OHY','vx VID'))
    ax.grid()
    if xlim:
      ax.set_xlim(xlim)
    
    # ---------------------------------------------------
    # wExistProb, wObstacle
    ax = fig.add_subplot(816)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['wExistProb'] )
    #ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['wObstacle'] )
    #ax.legend(('wExistProb','wObstacle'))
    ax.legend(('wExistProb',))
    ax.grid()
    ax.set_ylim(-0.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
    
    # Stand_b
    ax = fig.add_subplot(817)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['Stand_b'] )
    
    ax.legend(('Stand_b',))
    ax.grid()
    ax.set_ylim(-0.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
            
    # Stand_b
    ax = fig.add_subplot(818)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dWidthBase'] )
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dWidth'] )
   
    ax.legend(('dWidthBase','dWidth'))
    ax.grid()
    #ax.set_ylim(-0.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
            
    
            
            
            
    fig.show()
    
  #============================================================================================
  @staticmethod
  def plot_CVR3_VidObj(sig, FigNr=300,ObjName=0 ,xlim = None):
    # plot given video object in detail
    # sig : dict with signals
    # FigNr : figure number for plot
    # ObjName = 0,1,2,..,9

    
    #CVR3 = sig['VidObj']
    CVR3 = sig['VidObjT20']
    
        
    fig = pl.figure(FigNr)
    
    fig.suptitle('Video Object No %s'%ObjName)
    
    # ----------------------------------------------------------------
    # Video object Handle
    ax = fig.add_subplot(811)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['Handle'] )
    ax.legend(('Handle',))
    ax.grid()
    #ax.set_ylim(-0.1,1.1)
    if xlim:
      ax.set_xlim(xlim)

    # ----------------------------------------------------------------
    # Measure and Hist_b Flag
    ax = fig.add_subplot(812)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['countAlive'])
    
    ax.legend(('countAlive',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # Measure and Hist_b Flag
    ax = fig.add_subplot(813)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['Measured_b']+2)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['Hist_b'] )
    
    ax.legend(('Measured_b+2','Hist_b'))
    ax.grid()
    ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # dx
    ax = fig.add_subplot(814)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dx'])
    
    ax.legend(('dx',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # dx
    ax = fig.add_subplot(815)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dy'])
    
    ax.legend(('dy',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)

    # ----------------------------------------------------------------
    # dLength, dWidth
    ax = fig.add_subplot(816)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dLength'])
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['dWidth'])
    
    ax.legend(('dLength','dWidth'))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
    
    # ----------------------------------------------------------------
    # ObjType
    ax = fig.add_subplot(817)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['ObjType'])
    
    ax.legend(('ObjType',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
          
    # ----------------------------------------------------------------
    # ObjType
    ax = fig.add_subplot(818)
    ax.plot(CVR3[ObjName]['Time'], CVR3[ObjName]['wExistProb'])
    
    ax.legend(('wExistProb',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
     

    fig.show()
    
  #============================================================================================
  @staticmethod
  def plot_CVR3_ATS(sig, FigNr=600,ObjName=0 ,xlim = None):
    # plot given object of Position Matrix in detail
    # sig : dict with signals
    # FigNr : figure number for plot
    # ObjName = 0,1,2,3,4

    
    ATS = sig['ATS']
    
        
    fig = pl.figure(FigNr)
    
    fig.suptitle('ATS Object No %s'%ObjName)
    
    # ----------------------------------------------------------------
    # ATS object Handle
    ax = fig.add_subplot(911)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['Handle'] )
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['FusHandle'] )
    
    ax.legend(('Handle',))
    ax.grid()
    #ax.set_ylim(-0.1,1.1)
    if xlim:
      ax.set_xlim(xlim)

    # ----------------------------------------------------------------
    # Index
    ax = fig.add_subplot(912)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['Index'])      # from ATS
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['FusObjIdx'])  # from DataCVR3
    
    ax.legend(('Index',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)

    # ----------------------------------------------------------------
    # Index
    ax = fig.add_subplot(913)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['Valid'])      
    
    ax.legend(('Valid',))
    ax.grid()
    ax.set_ylim(-0.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # dx
    ax = fig.add_subplot(914)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['dx'])
    
    ax.legend(('dx',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # dy
    ax = fig.add_subplot(915)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['dy'])
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['dycAct'])
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['dycHist'])
    
    ax.legend(('dy','dycAct','dycHist'))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)
   
    # ----------------------------------------------------------------
    # vx
    ax = fig.add_subplot(916)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['vx'])
    
    ax.legend(('vx',))
    ax.grid()
    #ax.set_ylim(-0.1,3.1) 
    if xlim:
      ax.set_xlim(xlim)

    # ----------------------------------------------------------------
    # Flags
    ax = fig.add_subplot(917)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['CutIn_b']+6.0)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['LeftLane_b']+4.0)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['OwnLane_b']+2.0)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['RightLane_b'])
        
    ax.legend(('CutIn_b+6','LeftLane_b+4','OwnLane_b+2','RightLane_b'))
    ax.grid()
    ax.set_ylim(-0.1,7.1) 
    if xlim:
      ax.set_xlim(xlim)
       
    # ----------------------------------------------------------------
    # probabilities -1 .. 0 .. 1
    ax = fig.add_subplot(918)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['lpb'])
    
    ax.legend(('lpb',))
    ax.grid()
    ax.set_ylim(-1.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
    
    # ----------------------------------------------------------------
    # probabilities 0..1
    ax = fig.add_subplot(919)
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['plaus'])
    ax.plot(ATS[ObjName]['Time'], ATS[ObjName]['wCutIn'])
    
    
    ax.legend(('plaus','wCutIn'))
    ax.grid()
    ax.set_ylim(-0.1,1.1) 
    if xlim:
      ax.set_xlim(xlim)
    
    fig.show()
  #============================================================================================
  # following methods are under construction !!!
  #============================================================================================

 
