#!/usr/bin/env python
# coding: utf-8

# In[ ]:


commonTimeGroupList= [
    {
            "commonTime": ("EEC1_00_s00", "EngineSpeed")
    },
    {       "commonTime": ("EEC1_00_s00","EEC1_EngSpd_00"),
    }]
engSpeedGroupList = [
    {
            "engspeed": ("EEC1_00_s00", "EngineSpeed")
    },
    {
            "engspeed": ("EEC1_00_s00", "EEC1_EngSpd_00")
    },
    {
            "engspeed": ("EEC1_s00", "EngSpeed")
    },
    {
            "engspeed": ("EEC1", "EngSpeed_s00")
    },
    ]
vxKmhGroupList = [
     {
        "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B"),

      },
     {
        "vx_kmh": ("EBC2", "MeanFASpeed"),

      },
     {
        "vx_kmh": ("EBC2_BS", "FA_Spd_Cval"),

      },
     {
        "vx_kmh": ("EBC2_0B", "EBC2_MeanSpdFA_0B_C2"),

    },
    {
        "vx_kmh": ("EBC2_VDY_s0B", "EBC2_MeanSpdFA_0B"),

    },
    {
      "vx_kmh"  : ("EBC2_0B_s0B", "AverageFrontAxleWhlSpeed"),

    },
    {
      "vx_kmh"  : ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),

    },
    {
      "vx_kmh"  : ("EBC2_s0B", "FrontAxleSpeed"),

    },
    {
      "vx_kmh"  : ("EBC2_0B_s0B", "EBC2_MeanSpdFA_0B_s0B"),


    },
    {
      "vx_kmh"  : ("EBC2", "FrontAxleSpeed_s0B"),

    },
    {

      "vx_kmh"  : ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
    }
]
tssGroupList  = [
    {
      "TSSCurrentRegion": ("FLC_PROP1_sE8", "TSSCurrentRegion"),
      "TSSLifeTime": ("FLC_PROP1_sE8", "TSSLifeTime"),
      "TSSDetectedUoM": ("FLC_PROP1_sE8", "TSSDetectedUoM"),
      "TSSDetectedStatus": ("FLC_PROP1_sE8", "TSSDetectedStatus"),
      "TSSOverspeedAlert": ("FLC_PROP1_sE8", "TSSOverspeedAlert"),
      "TSSDetectedValue": ("FLC_PROP1_sE8", "TSSDetectedValue"),
    },
    {
    "TSSCurrentRegion": ("FLC_PROP1_E8_sE8","FLCProp1_TSSCurrentRegion_E8"),
    "TSSDetectedStatus": ("FLC_PROP1_E8_sE8","FLCProp1_TSSDetectedStatus_E8"),
    "TSSDetectedUoM": ("FLC_PROP1_E8_sE8","FLCProp1_TSSDetectedUoM_E8"),
    "TSSDetectedValue": ("FLC_PROP1_E8_sE8","FLCProp1_TSSDetectedValue_E8"),
    "TSSLifeTime": ("FLC_PROP1_E8_sE8","FLCProp1_TSSLifeTime_E8"),
    "TSSOverspeedAlert": ("FLC_PROP1_E8_sE8","FLCProp1_TSSOverspeedAlert_E8"),
    }
]

customGroupList =[{
   
    }]


