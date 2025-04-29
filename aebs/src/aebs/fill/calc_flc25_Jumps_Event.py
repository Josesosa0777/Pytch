# -*- dataeval: init -*-

from interface import iCalc
import numpy as np

sgs = [
    {

        "LaneWidth_JumpEvent": ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_LkInput_sensor_input_ego_lane_width"),
        "frontAxleSpeed": ("CAN_VEHICLE_EBC2_0B","EBC2_FrontAxleSpeed_0B"),
        "RightWhlLaneDepDistance": ("CAN_VEHICLE_FLI2_E8","FLI2_RightWhlLaneDepDistance_E8"),

    },
    #{

     #   "constructionSiteEventAvailable": (
      #      "MFC5xx Device.LD.LdOutput",
       #     "MFC5xx_Device_LD_LdOutput_road_ego_laneEvents_constructionSiteEvent_available"),
        #"frontAxleSpeed": ("EBC2_0B", "EBC2_FrontAxleSpeed_0B_s0B"),
   # }
]


class cFill(iCalc):
    dep = ('calc_common_time-flc25',)

    def check(self):
        source = self.get_source()
        group = source.selectSignalGroup(sgs)
        return group

    def fill(self, group):
        common_time = self.modules.fill('calc_common_time-flc25')

        LaneWidth_JumpEvent_time, LaneWidth_JumpEvent_value, LaneWidth_JumpEvent_unit = group.get_signal_with_unit(
            'LaneWidth_JumpEvent', ScaleTime=common_time)
        frontAxleSpeed_time, frontAxleSpeed_value, frontAxleSpeed_unit = group.get_signal_with_unit(
            'frontAxleSpeed', ScaleTime=common_time)
        RightWhlLaneDepDistance_time, RightWhlLaneDepDistance_value, RightWhlLaneDepDistance_unit = group.get_signal_with_unit(
            'RightWhlLaneDepDistance', ScaleTime=common_time)

        LaneWidth_JumpEvent_masked_array = np.diff(LaneWidth_JumpEvent_value)>0
        #LaneWidth_JumpEvent_masked_array = np.where(np.diff(LaneWidth_JumpEvent_value) < 0)
        #LaneWidth_JumpEvent_time = np.diff(LaneWidth_JumpEvent_time)

        LaneWidth_JumpEvent_masked_array = np.zeros(len(LaneWidth_JumpEvent_value), dtype=bool)
        EntryFlag = False
        indexes = [0,0]
        redundant_check = 5
        for LaneWidth_index in range(len(LaneWidth_JumpEvent_value)):
            if (LaneWidth_index >0)&(LaneWidth_index<(len(LaneWidth_JumpEvent_value)-1)):
                if (EntryFlag==False):
                    if (LaneWidth_JumpEvent_value[LaneWidth_index + 1] > LaneWidth_JumpEvent_value[LaneWidth_index] ):
                        EntryFlag = True
                        indexes[0] = LaneWidth_index
                        #redundant_check = 5
                else:
                    if (LaneWidth_JumpEvent_value[LaneWidth_index-1] < LaneWidth_JumpEvent_value[LaneWidth_index]):
                        indexes[1] = LaneWidth_index
                        #redundant_check = 5
                    elif ((LaneWidth_JumpEvent_value[LaneWidth_index-1] == LaneWidth_JumpEvent_value[LaneWidth_index])):
                        #redundant_check = redundant_check - 1
                        indexes[1] = LaneWidth_index
                    else:
                         Value_diff_cm = (LaneWidth_JumpEvent_value[indexes[1]] - LaneWidth_JumpEvent_value[indexes[0]])
                         Time_diff_sec = (LaneWidth_JumpEvent_time[indexes[1]] - LaneWidth_JumpEvent_time[indexes[0]])
                         EntryFlag = False
                         if ((Value_diff_cm >= 0.10) & (Time_diff_sec < 0.85) & ((Value_diff_cm / Time_diff_sec) > 0.16)):
                            for inmdex in range(indexes[1] - indexes[0]+1):
                                LaneWidth_JumpEvent_masked_array[(indexes[0] + inmdex)] = True

        # for LaneWidth_index in range(len(LaneWidth_JumpEvent_value)):
        #     if LaneWidth_index >0:
        #         if (LaneWidth_JumpEvent_value[LaneWidth_index-1]>LaneWidth_JumpEvent_value[LaneWidth_index])&(LaneWidth_index<(len(LaneWidth_JumpEvent_value)-1)):
        #             if (EntryFlag):
        #                 indexes[1] = LaneWidth_index
        #             else:
        #                 indexes = [LaneWidth_index-1,LaneWidth_index]
        #                 EntryFlag = True
        #         else:
        #             if (EntryFlag):
        #
        #                 Value_diff_cm = (LaneWidth_JumpEvent_value[indexes[0]] - LaneWidth_JumpEvent_value[indexes[1]])
        #                 Time_diff_sec = (LaneWidth_JumpEvent_time[indexes[1]] - LaneWidth_JumpEvent_time[indexes[0]])
        #                 if ((Value_diff_cm >= 0.10) & (Time_diff_sec < 0.5) & ((Value_diff_cm / Time_diff_sec) > 0.20)):
        #                     for inmdex in range(indexes[1] - indexes[0]+1):
        #                         LaneWidth_JumpEvent_masked_array[(indexes[0] + inmdex)] = True
        #                 EntryFlag = False


#        for LaneWidth_index in range(len(LaneWidth_JumpEvent_value)):
 #           if (LaneWidth_JumpEvent_value[LaneWidth_index]>LaneWidth_JumpEvent_value[LaneWidth_index+1])&(EntryFlag==False):
  #              indexes = [LaneWidth_index,LaneWidth_index+1]
   #             EntryFlag = True
    #        elif LaneWidth_JumpEvent_value[LaneWidth_index]>LaneWidth_JumpEvent_value[LaneWidth_index+1]:
     #           indexes[1] = LaneWidth_index+1
      #          if (LaneWidth_JumpEvent_value[LaneWidth_index+1]>LaneWidth_JumpEvent_value[LaneWidth_index+2])|(LaneWidth_index==len(LaneWidth_JumpEvent_value)):
       #             Value_diff_cm = (LaneWidth_JumpEvent_value[indexes[1]]-LaneWidth_JumpEvent_value[indexes[0]])
        #            Time_diff_sec = (LaneWidth_JumpEvent_time[indexes[1]]-LaneWidth_JumpEvent_time[indexes[0]])
         #           if ((Value_diff_cm>=10)&(Time_diff_sec<0.5)&((Value_diff_cm/Time_diff_sec)>20)):
          #              for inmdex in len(indexes[1]-indexes[0]):
           #                 LaneWidth_JumpEvent_masked_array[indexes[0]+inmdex] = True
             #           EntryFlag = False
            #    EntryFlag = False
            #else:
             #   EntryFlag = False
              #  indexes = [0, 0]

        return common_time, LaneWidth_JumpEvent_masked_array, frontAxleSpeed_value


if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"\\corp.knorr-bremse.com\str\Measure\DAS\ConvertedMeas_Xcellis\FER\AEBS\F30\FMAX_5506\FO242072_FU241850\2024-08-02\mi5id5506__2024-08-02_10-49-14.h5"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    data = manager_modules.calc('calc_flc25_Jumps_Event@aebs.fill', manager)
    print data
