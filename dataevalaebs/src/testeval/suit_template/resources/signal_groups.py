#!/usr/bin/env python
# coding: utf-8

# In[ ]:


commonTimeGroupList= [
    {
            "commonTime": ("EEC1_00_s00", "EngineSpeed")
    },
    {       "commonTime": ("EEC1_00_s00","EEC1_EngSpd_00"),
    }
]
engSpeedGroupList = [
    {
            "engspeed": ("EEC1_00_s00", "EngineSpeed")
    },
    {
            "engspeed": ("EEC1_00_s00", "EEC1_EngSpd_00")
    },
    
]
vxKmhGroupList = [
    
    {
      "vx_kmh"  : ("EBC2_0B_s0B", "AverageFrontAxleWhlSpeed"),

    },
    {

      "vx_kmh"  : ("EBC2_0B_s0B", "EBC2_FrontAxleSpeed_0B"),
    }
]

customGroupList =[
    {
        "vx_kmh"  : ("EBC2_0B_s0B", "AverageFrontAxleWhlSpeed"),
    } 
]


