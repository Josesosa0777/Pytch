# -*- dataeval: init -*-
# -*- coding: utf-8 -*-
import re

import matplotlib.pyplot as plt
import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList
from measproc.vidcalibs import VidCalibs
import MetaDataIO
sgs  = [
{
  "C0_right_wheel": ("Bendix_Info", "C0_right_wheel"),
  "C0_left_wheel": ("Bendix_Info", "C0_left_wheel"),
  "BX_LDW_Suppr": ("Bendix_Info", "BX_LDW_Suppr"),
  "FLI2_StateOfLDWS": ("FLI2_E8", "FLI2_StateOfLDWS"),
  "FLI2_LaneTrackingStatusRight": ("FLI2_E8", "FLI2_LaneTrackingStatusRight"),
  "FLI2_LaneTrackingStatusLeft": ("FLI2_E8", "FLI2_LaneTrackingStatusLeft"),
},
]

def word_in_text(word, text):
    word = word.lower()
    text = text.lower()
    match = re.search(word, text)
    if match:
        return True
    return False

class Search(iSearch):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def search(self, group):

    common_time, LDW_Suppr  = group.get_signal("BX_LDW_Suppr")  
    lanestatus_left = group.get_value("FLI2_LaneTrackingStatusLeft", ScaleTime=common_time)
    lanestatus_right = group.get_value("FLI2_LaneTrackingStatusRight", ScaleTime=common_time)
    State_LDWS  = group.get_value("FLI2_StateOfLDWS", ScaleTime=common_time)
    c0_left  = group.get_value("C0_left_wheel", ScaleTime=common_time) #[m]
    c0_right  = group.get_value("C0_right_wheel", ScaleTime=common_time) #[m]

    cond_0 = (lanestatus_left == 1) & (lanestatus_right == 1)
    
    cond_1 = State_LDWS == 3 #READY
    cond_1_5 = ((((c0_left > -1.28) & (c0_left < 1.27)) & (c0_right > -1.28)) & (c0_left < 1.27))
#     plt.subplot(511)
#     plt.plot(c0_left > -1.28)
#     plt.subplot(512)
#     plt.plot(c0_left < 1.27)
#     plt.subplot(513)
#     plt.plot(c0_right > -1.28)
#     plt.subplot(514)
#     plt.plot(c0_right < 1.27)  
#     plt.subplot(515)
#     plt.plot(cond_1_5)  
#     plt.show()
    timestep= np.mean(np.diff(common_time))

    cond_2 = LDW_Suppr == 0  #NO ACTIVE SUPPRESSION
    
    tokens = VidCalibs.parse_measurement(self.source.BaseName)
    vehicle = tokens[0] if tokens is not None else None
    parameters = MetaDataIO.cFLC20CalibData(vehicle)
    CalibData = parameters.GetData()
    leftWheel               = CalibData["leftWheel"]/100.0 #[cm]-->[m]
    rightWheel              = CalibData["rightWheel"]/100.0 #[cm]-->[m] 
    truck_width = leftWheel + rightWheel
    lane_width = -1*c0_left + c0_right + truck_width
    
    cond_3 = (lane_width > 2.5) & (lane_width < 2.7)

    if vehicle == 'HMC_Bus': limit = 0.05
    elif word_in_text('Ford', vehicle) : limit = 0.25
    else: limit= 0.15
    cond_4 = (c0_left > limit) | (c0_right < -1*limit)

    mask = (((((cond_0 &cond_1) & cond_2) & cond_3) & cond_4) & cond_1_5)

    new_mask=mask.astype( np.int8)
    #plt.plot(mask)
    raising_edge = np.array(np.where(np.diff(new_mask) == 1))
    falling_edge = np.array(np.where(np.diff(new_mask) == -1))
    #print "raising edge: ", raising_edge[0]
    #print "len raising edge: ",len(raising_edge[0])

    for x in range (len(raising_edge[0])):
        #print 'vanhossz'
        if is_warning(common_time, State_LDWS, raising_edge[0][x], 15, 0):
            #print "before: ", np.mean(new_mask[raising_edge[0][x]:falling_edge[0][x]])
            mask[raising_edge[0][x]+1:falling_edge[0][x]+1] = 0
            #print "after:",np.mean(new_mask[raising_edge[0][x]:falling_edge[0][x]])
            #print raising_edge[0][x], falling_edge[0][x]
             ###remove 1-ones from mask !!

    #plt.plot(mask+1.2)
    #prints still needed :D
    
    
    #plt.show()
    intervals = cIntervalList.fromMask(common_time, mask)

    report = Report(intervals, "(no title)")
    self.batch.add_entry(report, result=self.PASSED)
    return

def is_warning(time, signal, idx, t_tol_pre=15.0, t_tol_post=0.0):
  idx_pre = time.searchsorted(time[idx]-t_tol_pre)
  idx_post = time.searchsorted(time[idx]+t_tol_post)

  return (5 in signal[idx_pre : idx_post+1])
