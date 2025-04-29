import datetime
import json
import os
import shutil
import subprocess
import sys
import logging

import numpy as np

from execute_cmd import executeCmd
from measparser.parserPostmarker import TrafficSignWiseCount

logger = logging.getLogger('end_run.eval')
mainLogger = logging.getLogger('end_run_state.eval')


class EvalBase(object):
    def __init__(self, conf):
        self.conf = conf

    def runCommand(self, name, command):
        logger.info('Running %s' % name)
        resp = executeCmd(command)
        mainLogger.debug(resp)
        for err_tag in ("[FATAL]", "[CRITICAL]"):
            if err_tag in resp:
                return False
        return True


class SearchBase(EvalBase):
    search_modules = []
    w_postfix = ''

    def search(self):
        startDate = datetime.datetime.strptime(self.conf.searchStartDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(self.conf.searchEndDate, "%Y-%m-%d")
        measDate = datetime.datetime.strptime(self.conf.measDate, "%Y-%m-%d")
        if not (startDate <= measDate <= endDate):
            mainLogger.info("Skipping search for {}".format(measDate))
            return 'Success'
        if not self.conf.searchNeeded:
            return 'Success'
        convertNeeded = self.conf.videoConvertNeeded or self.conf.canConvertNeeded
        folderIsEmpty = True
        if self.conf.convMeasRootFolderPath:
            if os.path.exists(self.conf.convMeasFolderPath):
                if os.listdir(self.conf.convMeasFolderPath):
                    folderIsEmpty = False
        if convertNeeded or (not convertNeeded and not folderIsEmpty):
            measFolderPath = self.conf.convMeasFolderPath
        else:
            measFolderPath = self.conf.measFolderPath
        if self.conf.group == 'Trailer_Evaluation':
            if os.path.exists(self.conf.batchFile):
                os.remove(self.conf.batchFile)
                if not os.path.exists(os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles')):
                    os.mkdir(os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles'))
                shutil.move(os.path.join(self.conf.convMeasFolderPath, min(os.listdir(self.conf.convMeasFolderPath))),
                            os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles'))

            search = (
                '{python} -m search --nosave --nodirectsound --log-file "{logfile}" --scan "{folder}" '
                '-w *{postfix}.{ext} -b "{batch}" --repdir "{repdir}" {modules}'
            ).format(
                python=sys.executable,
                logfile=os.path.join(self.conf.logFolderPath, "search.log"),
                folder=measFolderPath,
                postfix=self.w_postfix,
                ext=self.conf.fileExtension,
                batch=self.conf.batchFile,
                repdir=self.conf.repDir,
                modules=' '.join(self.search_modules)
            )
            if not self.runCommand('search', search):
                return 'Error - Search - Failed'
            return 'Success'
        else:
            search = (
                '{python} -m search --nosave --nodirectsound --log-file "{logfile}" --scan "{folder}" '
                '-w *{postfix}.{ext} -b "{batch}" --repdir "{repdir}" {modules}'
            ).format(
                python=sys.executable,
                logfile=os.path.join(self.conf.logFolderPath, "search.log"),
                folder=measFolderPath,
                postfix=self.w_postfix,
                ext=self.conf.fileExtension,
                batch=self.conf.batchFile,
                repdir=self.conf.repDir,
                modules=' '.join(self.search_modules)
            )
            if not self.runCommand('search', search):
                return 'Error - Search - Failed'
            return 'Success'

    def searchRun(self, newMeasList):
        startDate = datetime.datetime.strptime(self.conf.searchStartDate, "%Y-%m-%d")
        endDate = datetime.datetime.strptime(self.conf.searchEndDate, "%Y-%m-%d")
        measDate = datetime.datetime.strptime(self.conf.measDate, "%Y-%m-%d")
        if not (startDate <= measDate <= endDate):
            mainLogger.info("Skipping search for {}".format(measDate))
            return 'Success'
        if not self.conf.searchNeeded:
            return 'Success'
        convertNeeded = self.conf.videoConvertNeeded or self.conf.canConvertNeeded
        folderIsEmpty = True
        if self.conf.convMeasRootFolderPath:
            if os.path.exists(self.conf.convMeasFolderPath):
                if os.listdir(self.conf.convMeasFolderPath):
                    folderIsEmpty = False
        if convertNeeded or (not convertNeeded and not folderIsEmpty):
            measFolderPath = self.conf.convMeasFolderPath
        else:
            measFolderPath = self.conf.measFolderPath
        if self.conf.group == 'Trailer_Evaluation':
            if os.path.exists(self.conf.batchFile):
                os.remove(self.conf.batchFile)
                if not os.path.exists(os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles')):
                    os.mkdir(os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles'))
                shutil.move(os.path.join(self.conf.convMeasFolderPath, min(os.listdir(self.conf.convMeasFolderPath))),
                            os.path.join(self.conf.convMeasRootFolderPath, 'convertedFiles'))
            for meas in newMeasList:
                search = (
                    '{python} -m search --nosave --nodirectsound --log-file "{logfile}" --add "{folder}" '
                    '-b "{batch}" --repdir "{repdir}" {modules}'
                ).format(
                    python=sys.executable,
                    logfile=os.path.join(self.conf.logFolderPath, "search.log"),
                    folder=os.path.join(measFolderPath, meas),
                    batch=self.conf.batchFile,
                    repdir=self.conf.repDir,
                    modules=' '.join(self.search_modules)
                )
                if not self.runCommand('search', search):
                    return 'Error - Search - Failed'
                return 'Success'
        else:
            for meas in newMeasList:
                search = (
                    '{python} -m search --nosave --nodirectsound --log-file "{logfile}" --add "{folder}" '
                    '-b "{batch}" --repdir "{repdir}" {modules}'
                ).format(
                    python=sys.executable,
                    logfile=os.path.join(self.conf.logFolderPath, "search.log"),
                    folder=os.path.join(measFolderPath, meas),
                    batch=self.conf.batchFile,
                    repdir=self.conf.repDir,
                    modules=' '.join(self.search_modules)
                )
                if not self.runCommand('search', search):
                    return 'Error - Search - Failed'
            return 'Success'


class SearchContiFcw(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events@fcweval', '-n search_events@fcweval', '-p search_events@fcweval.flr25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@fcweval.systemstate',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_flr25_dtc_active_events@flr25eval.faults',
        '-i search_flr25_dm1_dtc_events@flr25eval.faults',
    ]


class SearchContiFcwResim(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_fcw@fcwresim', '-n search_events_fcw@fcwresim', '-p search_events_fcw@fcwresim.flr25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@fcwresim.systemstate',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_flr25_dtc_active_events@flr25eval.faults',
        '-i search_flr25_dm1_dtc_events@flr25eval.faults',
    ]


class SearchContiACC(SearchBase):
    search_modules = [
        '-n iSearch',
        # '-i search_acc_eval_dirk@acceval',
        '-i search_acc_overheat@acceval',
        '-i search_acc_braking@acceval',
        # '-i search_acc_shutdown@acceval',
        '-i search_acc_jerk@acceval',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchACCdirk(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_acc_eval_dirk@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchACCOverheat(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_acc_overheat@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchACCStrongBrake(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_acc_braking@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchACCShutdown(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_acc_shutdown@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchAccPedStopResim(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_acc_ped@accpedresim',
        '-i search_accped_speed_range@accpedresim',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime',
    ]


class SearchAebsResimCn(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_resim_events@aebseval.resim',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime',
    ]


class SearchAebsResimDeltaCn(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_detect_event@aebseval.resim', '-n search_detect_event@aebseval.resim',
        '-p search_detect_event@aebseval.resim.flr25',
        # '-i search_resim_events@aebseval.resim',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime',
    ]


class SearchYacaEventHits(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_yaca_event@yacainterface', '-n search_yaca_event@yacainterface',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime',
    ]


class SearchPaebsResimDelta(SearchBase):
    """
    Defines which modules (property: 'search_modules') shall be run by PyTCh search script and
    with which arguments it is called via CLI.
    Both module names and the CLI commands are specially tailored to the needs of the PAEBS Resim Delta Report.
    """

    search_modules = [
        '-n iSearch',
        '-i search_paebs_resim_event@paebseval.resim', '-n search_paebs_resim_event@paebseval.resim',
        '-p search_paebs_resim_event@paebseval.resim.flc25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime',
    ]

    def search(self):
        """
        Overwritten method to take global parameter for .json and .csv file paths into account.
        Method builds and calls CLI command from configuration data to activate PyTCh search script.
        :return: Verdict
        """
        if not self.conf.searchNeeded:
            return 'Success'
        convertNeeded = self.conf.videoConvertNeeded or self.conf.canConvertNeeded
        folderIsEmpty = True
        if self.conf.convMeasRootFolderPath:
            if os.path.exists(self.conf.convMeasFolderPath):
                if os.listdir(self.conf.convMeasFolderPath):
                    folderIsEmpty = False
        if convertNeeded or (not convertNeeded and not folderIsEmpty):
            measFolderPath = self.conf.convMeasFolderPath
        else:
            measFolderPath = self.conf.measFolderPath
        search = (
            r'{python} -m search --nosave --nodirectsound --log-file "{logfile}" --scan "{folder}" '
            r'-w *{postfix}.{ext} -b "{batch}" --repdir "{repdir}" '
            r'--global-param "csvResimOutPath" "{csvResimOutPath}" --global-param "csvMileagePath" "{csvMileagePath}" '
            r'--global-param "json" "{json}" {modules}'
        ).format(
            python=sys.executable,
            logfile=os.path.join(self.conf.logFolderPath, "search.log"),
            folder=measFolderPath,
            postfix=self.w_postfix,
            ext=self.conf.fileExtension,
            batch=self.conf.batchFile,
            repdir=self.conf.repDir,
            csvResimOutPath=self.conf.csvResimOutPath,
            csvMileagePath=self.conf.csvMileagePath,
            json=self.conf.jsonParamPath,
            modules=' '.join(self.search_modules)
        )
        if not self.runCommand('search', search):
            return 'Error - Search - Failed'
        return 'Success'


class SearchAebsResimResimDeltaCn(SearchBase):
    search_modules = [
        '-n iSearch',
        # '-i search_detect_event@aebseval.resim', '-n search_detect_event@aebseval.resim', '-p search_detect_event@aebseval.resim.flr25',
        '-i search_resim2resim_event@aebseval.resim', '-n search_resim2resim_event@aebseval.resim',
        '-p search_resim2resim_event@aebseval.resim.flr25',
        # '-i search_resim_events@aebseval.resim',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        # '-i search_daytime@flc20eval.daytime',
    ]


class SearchAccPedStop(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events@accpedstop',
        '-i search_accped_speed_range@accpedresim',
        # '-i search_acc_eval_eco_driving@acceval',
        # '-i search_acc_brakepedal_override@acceval',
        # '-i search_acc_eval_overreaction@acceval',
        # '-i search_acc_torque_request@acceval',
        # '-i search_acc_strong_brake_req@acceval',
        # '-i search_acc_take_over_req@acceval',
        # '-i search_acc_delta_dtfv_above_threshold@acceval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'

    ]


class SearchConti(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flr25',
        # '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        # '-i search_inlane_flr20_tr0@trackeval.inlane',
        # '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        # '-i search_systemstate@ldwseval.systemstate',
        # '-i search_smess_faults@flr20eval.faults',
        # '-i search_a087_faults@flr20eval.faults',
        # '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flr25_dtc_active_events@flr25eval.faults',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        # '-i search_daytime@flc20eval.daytime'
    ]


class SearchContiTsrKpi(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_kpi_events@tsreval', '-n search_kpi_events@tsreval',
        '-i search_weather_time_condition@tsreval',
        # '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        # '-i search_inlane_flr20_tr0@trackeval.inlane',
        # '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        # '-i search_systemstate@ldwseval.systemstate',
        # '-i search_smess_faults@flr20eval.faults',
        # '-i search_a087_faults@flr20eval.faults',
        # '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        # '-i search_flr25_dtc_active_events@flr25eval.faults',
        # '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchContiTsrKbKpi(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_kb_kpi_events@tsreval', '-n search_kb_kpi_events@tsreval',
        '-i search_weather_time_condition@tsreval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchContiTsrResimKpi(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_kpi_events_resim@tsreval', '-n search_kpi_events_resim@tsreval',
        # '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        # '-i search_inlane_flr20_tr0@trackeval.inlane',
        # '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        # '-i search_systemstate@ldwseval.systemstate',
        # '-i search_smess_faults@flr20eval.faults',
        # '-i search_a087_faults@flr20eval.faults',
        # '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        # '-i search_flr25_dtc_active_events@flr25eval.faults',
        # '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchContiLDWS(SearchBase):
    search_modules = [
        '-n iSearch',
        # '-i search_ld_marking_id@ldwseval.laneeval',   # This script is not necessary now
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_ld_keep_alive@ldwseval.laneeval',
        '-i search_ldws_availability_check@ldwseval.laneeval'
    ]


class SearchContiSLR(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_bsis_image_classification@srreval.bsis_right',
        '-i search_mois_image_classification@srreval.mois_front',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchContiBSIS(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_bsis_image_classification@srreval.bsis_right',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchContiMOIS(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_mois_image_classification@srreval.mois_front',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchCountUiCycleCounter(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_count_uicyclecounter@mfc525eval.laneeval',
    ]


class SearchJumpEventLdwLka(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_flc25_Jump_event@mfc525eval.laneeval',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flr25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        # '-i search_left_lane_quality_state@mfc525eval.laneeval',
        # '-i search_right_lane_quality_state@mfc525eval.laneeval',
        '-i search_flc25_camera_reset_events@mfc525eval.faults',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flc25_cem_states_detection@mfc525eval.laneeval',
        '-i search_flc25_sensor_states@mfc525eval.laneeval',
        '-i search_actl_event@mfc525eval.laneeval',
        '-i search_flc25_construction_site_event@mfc525eval.laneeval',
        '-i search_flc25_dtc_active_events@mfc525eval.faults',
        # '-i search_flc25_num_of_detected_objects@mfc525eval.objecteval',
        # '-i search_flc25_object_lane_change@mfc525eval.objecteval',
        # '-i search_flc25_object_track_switchovers@mfc525eval.objecteval',
        # '-i search_flc25_obj_jumps_in_distance_x@mfc525eval.objecteval',
        # '-i search_flc25_lane_quality_drop@mfc525eval.laneeval',
        # '-i search_flc25_lane_quality_check@mfc525eval.laneeval',
        # '-i search_flc25_lane_c0_jump@mfc525eval.laneeval',
        # '-i search_flc25_lane_blockage_detection@mfc525eval.laneeval',
        # '-i search_flc25_ldws_events@mfc525eval.laneeval',
        # '-i search_flc25_compare_c0@mfc525eval.laneeval',
        # '-i search_flc25_lane_quality_drop_worst_case@mfc525eval.laneeval',
        # '-i search_flc25_acc_obj_unstable_tracking@mfc525eval.objecteval'

    ]


class SearchContiMfc(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flr25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        # '-i search_left_lane_quality_state@mfc525eval.laneeval',
        # '-i search_right_lane_quality_state@mfc525eval.laneeval',
        '-i search_flc25_camera_reset_events@mfc525eval.faults',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flc25_cem_states_detection@mfc525eval.laneeval',
        '-i search_flc25_sensor_states@mfc525eval.laneeval',
        '-i search_actl_event@mfc525eval.laneeval',
        '-i search_flc25_construction_site_event@mfc525eval.laneeval',
        '-i search_flc25_dtc_active_events@mfc525eval.faults',
        # '-i search_flc25_num_of_detected_objects@mfc525eval.objecteval',
        # '-i search_flc25_object_lane_change@mfc525eval.objecteval',
        # '-i search_flc25_object_track_switchovers@mfc525eval.objecteval',
        # '-i search_flc25_obj_jumps_in_distance_x@mfc525eval.objecteval',
        # '-i search_flc25_lane_quality_drop@mfc525eval.laneeval',
        # '-i search_flc25_lane_quality_check@mfc525eval.laneeval',
        # '-i search_flc25_lane_c0_jump@mfc525eval.laneeval',
        # '-i search_flc25_lane_blockage_detection@mfc525eval.laneeval',
        # '-i search_flc25_ldws_events@mfc525eval.laneeval',
        # '-i search_flc25_compare_c0@mfc525eval.laneeval',
        # '-i search_flc25_lane_quality_drop_worst_case@mfc525eval.laneeval',
        # '-i search_flc25_acc_obj_unstable_tracking@mfc525eval.objecteval'

    ]


class SearchContiConstructionSite(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_flc25_camera_reset_events@mfc525eval.faults',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flc25_construction_site_event@mfc525eval.laneeval',
    ]


class SearchContiLDKPI(SearchBase):
    search_modules = [
        '-i search_flc25_lane_cutting_analysis@mfc525eval.laneeval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchContiMfcFer(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flc25',
        '-i search_events_paeb@paebseval', '-n search_events_paeb@paebseval', '-p search_events_paeb@paebseval.flc25',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_systemstate@paebseval.systemstate',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_sensorstatus@mfc525eval.sensorstatus',
        '-i search_flc25_camera_reset_events@mfc525eval.faults',
        '-i search_flc25_lane_blockage_detection@mfc525eval.laneeval',
        '-i search_flc25_cem_states_detection@mfc525eval.laneeval',
        '-i search_flc25_eSigStatus@mfc525eval.laneeval',
        # '-i search_acal_yaw_statistics@mfc525eval.laneeval',
        '-i search_flc25_dtc_active_events@mfc525eval.faults',
        '-i search_sys_bitfield_event@mfc525eval.sys_bitfield',
        '-i search_flr25_dtc_active_events@flr25eval.faults',
        '-i search_flc25_sensor_states@mfc525eval.laneeval',
        '-i search_actl_event@mfc525eval.laneeval',
        '-i search_flc25_LDWS_state@mfc525eval.laneeval',
        '-i search_flc20_LDWS_state@mfc525eval.laneeval',
        '-i search_flr25_radar_reset_events@flr25eval.faults',
        '-i search_left_lane_quality_state@mfc525eval.laneeval',
        '-i search_right_lane_quality_state@mfc525eval.laneeval',
        '-i search_onoff@egoeval.enginestate',
        '-i search_corrupt_meas@aebseval'
    ]


class SearchSysBitfieldEvent(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_sys_bitfield_event@mfc525eval.sys_bitfield',
        '-i search_flc25_dtc_active_events@mfc525eval.faults',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchContiF3DataMining(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_fdf_f3p0_fda_low_speed@mfc525eval.datamining',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchTrailerEvent(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_trailer_rsp_eval@trailereval.rsp_eval'
        # '-i search_trailer_rsp_active_events@trailereval',
        # '-i search_trailer_wl_active@trailereval',
        # '-i search_trailer_abs_and_rsp_active@trailereval',
        # '-i search_trailer_p21_or_p22_diff@trailereval',
        # '-i search_trailer_no_braking@trailereval',
        # '-i search_trailer_wheelspeed_suspicious@trailereval',
        # '-i search_trailer_ilvl_out_of_driving_level@trailereval',
    ]


class SearchContiLD(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_flc25_LD_avail_during_lane_change@mfc525eval.laneeval',
        '-i search_flc25_LD_dropout_on_highway@mfc525eval.laneeval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchContiF3Acc(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flr25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_left_lane_quality_state@mfc525eval.laneeval',
        '-i search_right_lane_quality_state@mfc525eval.laneeval',
        '-i search_onoff@egoeval.enginestate',
        '-i search_flc25_acc_obj_fusion_degradation@mfc525eval.objecteval',
        '-i search_acc_object_lane_change@mfc525eval.objecteval',
        '-i search_acc_object_track_switchovers@mfc525eval.objecteval',
        '-i search_acc_obj_jumps_in_distance_x@mfc525eval.objecteval',
        '-i search_flc25_lane_quality_drop@mfc525eval.laneeval',
        '-i search_flc25_acc_obj_unstable_tracking@mfc525eval.objecteval',
        '-i search_flc20_LDWS_state@mfc525eval.laneeval',
        '-i search_flc25_LDWS_state@mfc525eval.laneeval'
    ]


class SearchContiPaeb(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_paeb@paebseval', '-n search_events_paeb@paebseval', '-p search_events_paeb@paebseval.flc25',
        # '-i search_events_paeb@paebseval', '-n search_events_paeb@paebseval', '-p search_events_paeb@paebseval.paebs',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@paebseval.systemstate',
        '-i search_onoff@egoeval.enginestate',
    ]

class SearchContiAebs(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events_aeb@aebseval', '-n search_events_aeb@aebseval', '-p search_events_aeb@aebseval.flc25',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_onoff@egoeval.enginestate',
    ]


class SearchKB(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events@aebseval', '-n search_events@aebseval', '-p search_events@aebseval.flr20',
        '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_inlane_flr20_tr0@trackeval.inlane',
        '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_systemstate@ldwseval.systemstate',
        '-i search_smess_faults@flr20eval.faults',
        '-i search_a087_faults@flr20eval.faults',
        '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchKBnoAEBS(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_systemstate@ldwseval.systemstate',
        '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchWabco(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_events@aebseval', '-n search_events@aebseval', '-p search_events@aebseval.flr20',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_inlane_flr20_tr0@trackeval.inlane',
        '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchKBResim(SearchBase):
    w_postfix = '_kbaebs'
    search_modules = [
        '-n iSearch',
        '-i search_aebs_warning@dataevalaebs', '-n search_aebs_warning@dataevalaebs',
        '-p search_aebs_warning@dataevalaebs.DEV_DAF_89KPH_7_15_BRAKING_MBT_tuned_after_Boxberg',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_inlane_flr20_tr0@trackeval.inlane',
        '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_smess_faults@flr20eval.faults',
        '-i search_a087_faults@flr20eval.faults',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchResimNoCam(SearchBase):
    w_postfix = '_kbaebs'
    search_modules = [
        '-n iSearch',
        '-i search_aebs_warning@dataevalaebs', '-n search_aebs_warning@dataevalaebs',
        '-p search_aebs_warning@dataevalaebs.DPV_NAME',  # TODO fill with new dpv when ready
        '-i search_roadtypes@egoeval.roadtypes',
        # '-i search_inlane_flr20_tr0@trackeval.inlane',
        # '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        # '-i search_smess_faults@flr20eval.faults',
        # '-i search_a087_faults@flr20eval.faults',
        # '-i search_onoff@egoeval.enginestate',
        # '-i search_daytime@flc20eval.daytime'
    ]


class SearchBX(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_bendix_warning@dataevalaebs', '-n search_bendix_warning@dataevalaebs',
        '-p search_bendix_warning@dataevalaebs.cmt',
        '-p search_bendix_warning@dataevalaebs.stat',
        '-p search_bendix_warning@dataevalaebs.umo',
        '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_inlane_flr20_tr0@trackeval.inlane',
        '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_systemstate@ldwseval.systemstate',
        '-i search_smess_faults@flr20eval.faults',
        '-i search_a087_faults@flr20eval.faults',
        '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class SearchAebsUsecase(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_aebs_usecase_eval@mfc525eval.objecteval'
    ]


class SearchBXEly(SearchBase):
    search_modules = [
        '-n iSearch',
        '-i search_bendix_warning@dataevalaebs', '-n search_bendix_warning@dataevalaebs',
        '-p search_bendix_warning@dataevalaebs.cmt',
        '-p search_bendix_warning@dataevalaebs.stat',
        '-p search_bendix_warning@dataevalaebs.umo',
        '-p search_bendix_warning@dataevalaebs.acc',
        '-p search_bendix_warning@dataevalaebs.ldw',
        '-p search_bendix_warning@dataevalaebs.tsr',
        '-i search_events@ldwseval',
        '-i search_roadtypes@egoeval.roadtypes',
        '-i search_inlane_flr20_tr0@trackeval.inlane',
        '-i search_inlane_flr20_tr0_fused@trackeval.inlane',
        '-i search_systemstate@aebseval.systemstate',
        '-i search_systemstate@ldwseval.systemstate',
        '-i search_smess_faults@flr20eval.faults',
        '-i search_a087_faults@flr20eval.faults',
        '-i search_sensorstatus@flc20eval.sensorstatus',
        '-i search_onoff@egoeval.enginestate',
        '-i search_daytime@flc20eval.daytime'
    ]


class Search(object):
    search_class_lut = {
        n: c for n, c in globals().iteritems() if type(c) is type
                                                  and issubclass(c, SearchBase)
                                                  and c is not SearchBase
    }

    def __new__(cls, conf):
        searchClass = SearchKB
        try:
            searchClass = cls.search_class_lut[conf.searchClass]
            logger.debug("Searching with '{cls}'".format(cls=searchClass.__name__))
        except KeyError:
            logger.warning("SearchClass '{cls}' not found, using 'SearchKB' as default".format(
                cls=searchClass.__name__))
        return searchClass(conf)


class IssueBase(EvalBase):
    issuegen_modules = []

    def issueGen(self):
        if not self.conf.issuegenNeeded:
            return 'Success'
        issueGen = (
            '{python} -m analyze --nonav --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" '
            '--start-date {date} --end-date {date} --repdir "{repdir}" --doc-name "{outfile}" {modules}'
        ).format(
            python=sys.executable,
            logfile=os.path.join(self.conf.logFolderPath, "issue.log"),
            outfile=os.path.join(self.conf.issueFolderPath, "issue"),
            date=self.conf.measDate,
            batch=self.conf.batchFile,
            repdir=self.conf.repDir,
            modules=' '.join(self.issuegen_modules)
        )
        if not self.runCommand('issue generation', issueGen):
            return 'Error - Issue Generation - Failed'
        return 'Success'


class IssueKB(IssueBase):
    issuegen_modules = [
        '-n iAnalyze',
        '-i issuegen_kbendrun_daily@reportgen.kbendrun_00_daily'
    ]


class IssueKBnoAEBS(IssueBase):
    issuegen_modules = [
        '-n iAnalyze',
        '-i issuegen_kbnoaebs_daily@reportgen.kbnoaebs_00_daily'
    ]


class IssueKBResim(IssueBase):
    issuegen_modules = [
        '-n iAnalyze',
        '-i issuegen_kbresim_daily@reportgen.kbresim_00_daily'
    ]


class IssueWabco(IssueBase):
    issuegen_modules = [
        '-n iAnalyze',
        '-i issuegen_wabcoendrun_daily@reportgen.wabcoendrun_00_daily'
    ]


class IssueBX(IssueBase):
    issuegen_modules = [
        '-n iAnalyze',
        '-i issuegen_bxendrun_daily@reportgen.bxendrun_00_daily'
    ]


class Issue(object):
    issue_class_lut = {
        n: c for n, c in globals().iteritems() if type(c) is type
                                                  and issubclass(c, IssueBase)
                                                  and c is not IssueBase
    }

    def __new__(cls, conf):
        issueClass = IssueKB
        try:
            issueClass = cls.issue_class_lut[conf.issueClass]
            logger.debug("Generating issue with '{cls}'".format(cls=issueClass.__name__))
        except KeyError:
            logger.warning("IssueClass '{cls}' not found, using 'IssueKB' as default".format(
                cls=issueClass.__name__))
        return issueClass(conf)


class DocBase(EvalBase):
    docgen_modules = []

    def docGen(self):
        if self.conf.group == 'Trailer_Evaluation':
            if not self.conf.docgenNeeded:
                return 'Success'
            report = (
                '{python} -m analyze --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" --nonav '
                '--start-date {date} --end-date {date} --repdir "{repdir}" --doc-name "{outfile}" {modules}'
            ).format(
                python=sys.executable,
                logfile=os.path.join(self.conf.logFolderPath,
                                     "{}.log".format(os.listdir(self.conf.convMeasFolderPath)[0].replace('.mat', ''))),
                batch=self.conf.batchFile,
                date=self.conf.measDate,
                repdir=self.conf.repDir,
                outfile=os.path.join(self.conf.issueFolderPath,
                                     "{}.pdf".format(os.listdir(self.conf.convMeasFolderPath)[0].replace('.mat', ''))),
                modules=' '.join(self.docgen_modules)
            )
            if not self.runCommand('report generation', report):
                return 'Error - PDF Generation - Failed'
            # Converting pdf to docx
            pdf_file_path = os.path.join(self.conf.issueFolderPath, "{}.pdf".format(
                os.listdir(self.conf.convMeasFolderPath)[0].replace('.mat', '')))
            docx_file_path = os.path.join(self.conf.issueFolderPath, "{}.docx".format(
                os.listdir(self.conf.convMeasFolderPath)[0].replace('.mat', '')))
            converter_exe = os.path.join(os.path.dirname(__file__), 'pdf2doc_converter.exe')
            if "docx" in self.conf.docTypes or "doc" in self.conf.docTypes:
                if not os.path.isfile(converter_exe):
                    logger.warning('Error - MS Word Docx Generation - Failed: Due to missing conversion dependancy')
                    return "Success"
                if "html" in self.conf.docTypes:
                    command = converter_exe + ' "{pdf_path}" "{docx_path}" -html'.format(pdf_path=pdf_file_path,
                                                                                         docx_path=docx_file_path)
                else:
                    command = converter_exe + ' "{pdf_path}" "{docx_path}"'.format(pdf_path=pdf_file_path,
                                                                                   docx_path=docx_file_path)
                if not self.runCommand('report generation', command):
                    logger.warning('Error - MS Word Docx Generation - Failed')

            if len(self.conf.docTypes) > 0 and "pdf" not in self.conf.docTypes:
                os.remove(pdf_file_path)
            if self.conf.docClass == 'DocContiTsrKpi' and self.conf.searchNeeded:
                self.tsr_Sign_count(self.conf.measDate)

            return 'Success'

        else:
            if not self.conf.docgenNeeded:
                return 'Success'
            report = (
                '{python} -m analyze --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" --nonav '
                '--start-date {date} --end-date {date} --repdir "{repdir}" --doc-name "{outfile}" {modules}'
            ).format(
                python=sys.executable,
                logfile=os.path.join(self.conf.logFolderPath, "report.log"),
                batch=self.conf.batchFile,
                date=self.conf.measDate,
                repdir=self.conf.repDir,
                outfile=os.path.join(self.conf.issueFolderPath, "report.pdf"),
                modules=' '.join(self.docgen_modules)
            )
            if not self.runCommand('report generation', report):
                return 'Error - PDF Generation - Failed'
            # Converting pdf to docx
            pdf_file_path = os.path.join(self.conf.issueFolderPath, "report.pdf")
            docx_file_path = os.path.join(self.conf.issueFolderPath, "report.docx")
            converter_exe = os.path.join(os.path.dirname(__file__), 'pdf2doc_converter.exe')
            if "docx" in self.conf.docTypes or "doc" in self.conf.docTypes:
                if not os.path.isfile(converter_exe):
                    logger.warning('Error - MS Word Docx Generation - Failed: Due to missing conversion dependancy')
                    return "Success"
                if "html" in self.conf.docTypes:
                    command = converter_exe + ' "{pdf_path}" "{docx_path}" -html'.format(pdf_path=pdf_file_path,
                                                                                         docx_path=docx_file_path)
                else:
                    command = converter_exe + ' "{pdf_path}" "{docx_path}"'.format(pdf_path=pdf_file_path,
                                                                                   docx_path=docx_file_path)
                if not self.runCommand('report generation', command):
                    logger.warning('Error - MS Word Docx Generation - Failed')

            if len(self.conf.docTypes) > 0 and "pdf" not in self.conf.docTypes:
                os.remove(pdf_file_path)
            if self.conf.docClass == 'DocContiTsrKpi' and self.conf.searchNeeded:
                self.tsr_Sign_count(self.conf.measDate)

            return 'Success'

    def summaryReportGen(self):
        if self.conf.docClass == 'DocContiTsrKpi' and self.conf.searchNeeded:
            self.tsr_sign_summaryGen()
        if not self.conf.summaryReportGenNeeded:
            return 'Success'
        report = (
            '{python} -m analyze --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" --nonav '
            '--start-date {start_date} --end-date {end_date} --repdir "{repdir}" --doc-name "{outfile}" {modules}'
        ).format(
            python=sys.executable,
            logfile=os.path.join(self.conf.summaryLogFolderPath, "summary_report.log"),
            batch=self.conf.batchFile,
            start_date=self.conf.startDate,
            end_date=self.conf.endDate,
            repdir=self.conf.repDir,
            outfile=os.path.join(self.conf.summaryReportPath, "summary_report.pdf"),
            modules=' '.join(self.docgen_modules)
        )
        if not self.runCommand('summary report generation', report):
            return 'Error - PDF Generation - Failed'
        # Converting pdf to docx
        pdf_file_path = os.path.join(self.conf.summaryReportPath, "summary_report.pdf")
        docx_file_path = os.path.join(self.conf.summaryReportPath, "summary_report.docx")
        converter_exe = os.path.join(os.path.dirname(__file__), 'pdf2doc_converter.exe')
        if "docx" in self.conf.summaryDocTypes or "doc" in self.conf.summaryDocTypes:
            if not os.path.isfile(converter_exe):
                logger.warning('Error - MS Word Docx Generation - Failed: Due to missing conversion dependancy')
                return "Success"
            if "html" in self.conf.summaryDocTypes:
                command = converter_exe + ' "{pdf_path}" "{docx_path}" -html'.format(pdf_path=pdf_file_path,
                                                                                     docx_path=docx_file_path)
            else:
                command = converter_exe + ' "{pdf_path}" "{docx_path}"'.format(pdf_path=pdf_file_path,
                                                                               docx_path=docx_file_path)
            if not self.runCommand('summary report generation', command):
                logger.warning('Error - MS Word Docx Generation - Failed')

        if len(self.conf.summaryDocTypes) > 0 and "pdf" not in self.conf.summaryDocTypes:
            try:
                os.remove(pdf_file_path)
            except:
                pass
        return 'Success'

    # ---------------------Calculate traffic sign wise count and store it in csv---------------------
    def tsr_Sign_count(self, folder):
        tfc = TrafficSignWiseCount()
        tfc.parseJsonAndCreateCsv(os.path.join(self.conf.measRootFolderPath, folder), self.conf.dbFolderPath)
        print("csv generated for traffic sign data : ", folder)
        if not self.conf.summaryReportGenNeeded and self.conf.searchNeeded:
            self.tsr_sign_summaryGen()

    # ----------GT traffic Sign summary calculation------------------------------------------
    def tsr_sign_summaryGen(self):

        if not self.conf.docgenNeeded:  # only summary report  needed summaryReportGenNeeded == true and docgenNeeded==false
            tfc = TrafficSignWiseCount()
            tfc.onlySummaryReportGen(self.conf.measRootFolderPath, self.conf.dbFolderPath)

        summary_path = self.conf.measRootFolderPath + "\\TrafficSignSummary.json"
        if os.path.exists(summary_path):
            f = open(summary_path, 'r')
            summaryData = json.load(f)
            f.close()
            if (summaryData.has_key('gt')):
                gt = summaryData['gt']
            else:
                logger.exception('GT data not found in TrafficSummary json')
            signlist = set(int(sign) for key in summaryData.keys() for sign, qty in summaryData[key].items())
            a = np.zeros((len(list(signlist)), 4))
            arr = np.column_stack((list(signlist), a))

            for key in summaryData.keys():
                if key != 'gt':
                    for sign, qty in summaryData[key].items():
                        sgn = sign
                        sign = int(sign)
                        idx = np.where(arr == sign)
                        rwo = int(idx[0])
                        qty = int(qty)
                        if gt.has_key(sgn):
                            arr[rwo][1] = gt[sgn]
                        if key == "TruePositive":
                            arr[rwo][2] = arr[rwo][2] + qty
                        elif key == "FalsePositive":
                            arr[rwo][3] = arr[rwo][3] + qty
                        else:
                            arr[rwo][4] = arr[rwo][4] + qty

            np.savetxt(self.conf.dbFolderPath + "\\TrafficSignSummary.csv", arr, delimiter=',', fmt='%f',
                       header='Traffic_sign_Id,GT,TruePositive,FalsePositive,FalseNegative')
        else:
            logger.exception('TrafficSignSummary.json not found')


class DocKB(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_daily@reportgen.kbendrun_00_daily'
    ]


class DocConti(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocContiTsrKpi(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_tsr_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocContiTsrKbKpi(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_can_tsr_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocContiTsrResimKpi(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_tsr_resim_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocContiPaeb(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_paeb_daily@reportgen.kbendrun_conti_paeb_00_daily'
    ]


class DocContiPaebCn(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_kbcn_paeb_daily@reportgen.kbendrun_conti_paeb_00_daily'
    ]


class DocContiLDWS(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_mfc_ldws_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiMfc(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_mfc_newformat_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiJumpEvent(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_flc25_Jump_event@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiLeftLaneCut(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_left_lane_cutting_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiRightLaneCut(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_right_lane_cutting_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiF3DataMining(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_fusion3_data_mining@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiMfcAebs(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_mfc_aebs_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiSysBitfield(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_sys_bitfield_event_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocTrailerEvent(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        # '-i reportgen_kbendrun_rsp_trailer_daily@reportgen.kbendrun_trailer_00_daily',
        '-i reportgen_kbendrun_rsp_eval_daily@reportgen.kbendrun_trailer_00_daily',
        # '-i reportgen_kbendrun_trailer_daily@reportgen.kbendrun_trailer_00_daily'
    ]


class DocContiLD(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_ldws_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiF3Acc(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_acc_daily@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class DocContiFcw(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_fcw_daily@reportgen.kbendrun_conti_fcw_00_daily'
    ]


class DocContiFcwResim(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_fcwresim_daily@reportgen.kbendrun_conti_fcw_00_daily'
    ]


class DocContiACC(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_conti_acc_eval_daily@reportgen.kbendrun_conti_acc_00_daily'
        # '-i reportgen_acc@acceval'
    ]


class DocAccPedStopResim(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_accped_daily@reportgen.kbendrun_conti_acc_00_daily'
    ]


class DocAebsResimCn(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_aebs_resim_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocAebsResimDeltaCn(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_aebs_resim_delta_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocYacaEventHits(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_yaca_daily@yacainterface'
    ]


class DocPaebsResimDelta(DocBase):
    """
    Defines which modules (property: 'docgen_modules') shall be run by PyTCh analyze script and
    with which arguments it is called via CLI.
    Both module names and the CLI commands are specially tailored to the needs of the PAEBS Resim Delta Report.
    """
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_paebs_resim_delta_daily@reportgen.kbendrun_conti_paeb_00_daily'
    ]

    def docGen(self):
        # type: (DocPaebsResimDelta) -> str
        """
        Overwritten method to take global parameter for .json and .csv file paths into account.
        Method builds and calls CLI command from configuration data to activate PyTCh analyze script.

        :return: Verdict
        """
        if not self.conf.docgenNeeded:
            return 'Success'
        report = (
            '{python} -m analyze --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" --nonav '
            '--start-date {date} --end-date {date} --repdir "{repdir}" --doc-name "{outfile}" '
            '--global-param "csvResimOutPath" "{csvResimOutPath}" --global-param "csvMileagePath" "{csvMileagePath}" '
            '--global-param "json" "{json}" {modules}'
        ).format(
            python=sys.executable,
            logfile=os.path.join(self.conf.logFolderPath, "report.log"),
            batch=self.conf.batchFile,
            date=self.conf.measDate,
            repdir=self.conf.repDir,
            outfile=os.path.join(self.conf.issueFolderPath, "report.pdf"),
            csvResimOutPath=self.conf.csvResimOutPath,
            csvMileagePath=self.conf.csvMileagePath,
            json=self.conf.jsonParamPath,
            modules=' '.join(self.docgen_modules)
        )
        if not self.runCommand('report generation', report):
            return 'Error - PDF Generation - Failed'
        # Converting pdf to docx
        pdf_file_path = os.path.join(self.conf.issueFolderPath, "report.pdf")
        docx_file_path = os.path.join(self.conf.issueFolderPath, "report.docx")
        converter_exe = os.path.join(os.path.dirname(__file__), 'pdf2doc_converter.exe')
        if "docx" in self.conf.docTypes or "doc" in self.conf.docTypes:
            if not os.path.isfile(converter_exe):
                logger.warning('Error - MS Word Docx Generation - Failed: Due to missing conversion dependancy')
                return "Success"
            if "html" in self.conf.docTypes:
                command = converter_exe + ' "{pdf_path}" "{docx_path}" -html'.format(pdf_path=pdf_file_path,
                                                                                     docx_path=docx_file_path)
            else:
                command = converter_exe + ' "{pdf_path}" "{docx_path}"'.format(pdf_path=pdf_file_path,
                                                                               docx_path=docx_file_path)
            if not self.runCommand('report generation', command):
                logger.warning('Error - MS Word Docx Generation - Failed')

        if len(self.conf.docTypes) > 0 and "pdf" not in self.conf.docTypes:
            os.remove(pdf_file_path)
        if self.conf.docClass == 'DocContiTsrKpi' and self.conf.searchNeeded:
            self.tsr_Sign_count(self.conf.measDate)

        return 'Success'

    def summaryReportGen(self):
        # type: (DocPaebsResimDelta) -> str
        """
        Overwritten method to take global parameter for .json and .csv file paths into account.
        Method builds and calls CLI command from configuration data to activate PyTCh analyze script.

        :return: Verdict.
        """
        if self.conf.docClass == 'DocContiTsrKpi' and self.conf.searchNeeded:
            self.tsr_sign_summaryGen()
        if not self.conf.summaryReportGenNeeded:
            return 'Success'
        report = (
            '{python} -m analyze --nosave --nodirectsound --log-file "{logfile}" -b "{batch}" --nonav '
            '--start-date {start_date} --end-date {end_date} --repdir "{repdir}" --doc-name "{outfile}" '
            '--global-param "csvResimOutPath" "{csvResimOutPath}" --global-param "csvMileagePath" "{csvMileagePath}" '
            '--global-param "json" "{json}" {modules}'
        ).format(
            python=sys.executable,
            logfile=os.path.join(self.conf.summaryLogFolderPath, "summary_report.log"),
            batch=self.conf.batchFile,
            start_date=self.conf.startDate,
            end_date=self.conf.endDate,
            repdir=self.conf.repDir,
            outfile=os.path.join(self.conf.summaryReportPath, "summary_report.pdf"),
            csvResimOutPath=self.conf.csvResimOutPath,
            csvMileagePath=self.conf.csvMileagePath,
            json=self.conf.jsonParamPath,
            modules=' '.join(self.docgen_modules)
        )
        if not self.runCommand('summary report generation', report):
            return 'Error - PDF Generation - Failed'
        # Converting pdf to docx
        pdf_file_path = os.path.join(self.conf.summaryReportPath, "summary_report.pdf")
        docx_file_path = os.path.join(self.conf.summaryReportPath, "summary_report.docx")
        converter_exe = os.path.join(os.path.dirname(__file__), 'pdf2doc_converter.exe')
        if "docx" in self.conf.summaryDocTypes or "doc" in self.conf.summaryDocTypes:
            if not os.path.isfile(converter_exe):
                logger.warning('Error - MS Word Docx Generation - Failed: Due to missing conversion dependancy')
                return "Success"
            if "html" in self.conf.summaryDocTypes:
                command = converter_exe + ' "{pdf_path}" "{docx_path}" -html'.format(pdf_path=pdf_file_path,
                                                                                     docx_path=docx_file_path)
            else:
                command = converter_exe + ' "{pdf_path}" "{docx_path}"'.format(pdf_path=pdf_file_path,
                                                                               docx_path=docx_file_path)
            if not self.runCommand('summary report generation', command):
                logger.warning('Error - MS Word Docx Generation - Failed')

        if len(self.conf.summaryDocTypes) > 0 and "pdf" not in self.conf.summaryDocTypes:
            try:
                os.remove(pdf_file_path)
            except:
                pass
        return 'Success'


class DocAebsResimResimDeltaCn(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_aebs_resim2resim_daily@reportgen.kbendrun_conti_00_daily'
    ]


class DocAccPedStop(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_accped_stop_daily@reportgen.kbendrun_conti_acc_00_daily'
    ]


class DocWabco(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_wabcoendrun_daily@reportgen.wabcoendrun_00_daily'
    ]


class DocKBResim(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbresim_daily@reportgen.kbresim_00_daily'
    ]


class DocContiBSIS(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i report_bsis_right_image_classification@srreval.bsis_right'
    ]


class DocContiMOIS(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i report_mois_front_image_classification@srreval.mois_front'
    ]


class DocBX(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i docgen_bendix_warning@dataevalaebs'
    ]


class DocAEBSUsecaseEval(DocBase):
    docgen_modules = [
        '-n iAnalyze',
        '-i reportgen_kbendrun_aebs_usecase_eval@reportgen.kbendrun_conti_mfc_00_daily'
    ]


class Doc(object):
    doc_class_lut = {
        n: c for n, c in globals().iteritems() if type(c) is type
                                                  and issubclass(c, DocBase)
                                                  and c is not DocBase
    }

    def __new__(cls, conf):
        docClass = DocKB
        try:
            docClass = cls.doc_class_lut[conf.docClass]
            logger.debug("Generating doc with '{cls}'".format(cls=docClass.__name__))
        except KeyError:
            logger.warning("DocClass '{cls}' not found, using 'DocKB' as default".format(
                cls=docClass.__name__))
        return docClass(conf)
