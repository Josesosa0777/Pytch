# -*- dataeval: init -*-
import numpy as np
from interface import iCalc
from numpy.core.fromnumeric import size

signals = [
    {
        "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
        "mean_spd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA")

    },
    {
        #"aebs_state": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
        "aebs_state": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sFlc25_EbOutput_hmi_output_aebs_system_state"),
        #"mean_spd": ("MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA")
        "mean_spd": ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t","MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_sAoa_CanInput_EBC2_EBC2_MeanSpdFA"),

    },
]
class cFill(iCalc):
        dep = ('fill_flc25_aoa_aebs_tracks', 'calc_common_time-flc25')
        def check(self):
            modules = self.get_modules()
            source = self.get_source()
            signal_group = source.selectSignalGroup(signals)
            aebs_obj = modules.fill("fill_flc25_aoa_aebs_tracks")[0]
            common_time = modules.fill('calc_common_time-flc25')
            return aebs_obj, signal_group, common_time

        def fill(self, aebs_obj, signal_group, common_time):
            aebs_eval = {}
            _, aebs_state, _ = signal_group.get_signal_with_unit('aebs_state', ScaleTime=common_time)
            _, mean_spd, _ = signal_group.get_signal_with_unit('mean_spd', ScaleTime=common_time)
            aebs_obj_dx = aebs_obj['dx']
            start_warning = np.where(aebs_state == 5)[0]
            start_braking = np.where(aebs_state == 6)[0]
            start_emergency_brake = np.where(aebs_state == 7)[0]
            stop_emergency_brake = np.where(aebs_state == 7)[-1]

            if start_warning.size >0:
                aebs_eval['ego_vx_at_warning'] = mean_spd[start_warning[0]]
                aebs_eval['aebs_obj_vx_at_warning'] = aebs_obj['vx'][start_warning[0]]
                aebs_eval['dx_warning'] = aebs_obj_dx[start_warning[0]]
                aebs_eval['t_warning']= common_time[start_warning[0]]
            else:
                aebs_eval['ego_vx_at_warning'] = 0
                aebs_eval['aebs_obj_vx_at_warning'] = 0
                aebs_eval['dx_warning'] = 999
                aebs_eval['t_warning']= common_time[-1]

            if start_braking.size >0:    
                aebs_eval['dx_braking'] = aebs_obj_dx[start_braking[0]]
            else: 
                aebs_eval['dx_braking'] = 999

            if start_emergency_brake.size >0: 
                aebs_eval['dx_emergency'] = aebs_obj_dx[start_emergency_brake[0]]
            else:
                aebs_eval['dx_emergency'] = 999

            if stop_emergency_brake.size >0:
                    aebs_eval['dx_stopping'] = aebs_obj_dx[stop_emergency_brake[-1]]
                    aebs_eval['ego_vx_stopping'] = mean_spd[stop_emergency_brake[-1]]
            else:
                aebs_eval['dx_stopping'] = 999
                aebs_eval['ego_vx_stopping'] = 999

            return common_time, aebs_eval

if __name__ == '__main__':
        from config.Config import init_dataeval
        meas_path = r"C:\KBApps\GIT\dataevalaebs\test_aebs_eval_script"
        config, manager, manager_modules = init_dataeval(['-m', meas_path])
        tracks = manager_modules.calc('calc_aebs_usecase_eval@aebs.fill', manager)
        print(tracks)
