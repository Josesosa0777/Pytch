# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from flr20_raw_tracks_base import ObjectFromMessage
from interface import iCalc
from primitives.bases import PrimitiveCollection
import logging
import os.path
logger = logging.getLogger('fill_bitfield_aebs_tracks')

signalTemplates = (
    (
        "MTSI_stKBFreeze_020ms_t",
        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_first_obj_bitfield"),
    (
        "MTSI_stKBFreeze_020ms_t",
        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_second_obj_bitfield"),
    (
        "MTSI_stKBFreeze_020ms_t",
        "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_third_obj_bitfield"),
    (
        "MTSI_stKBFreeze_100ms_t",
        "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_aebs_object_enable_bitfield"),
)
#
signalTemplates_1 = (
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_first_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_second_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_third_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_100ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_aebs_object_enable_bitfield"),

    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_first_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_second_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_third_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_first_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_second_bitfield_value"),
    ("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_third_bitfield_value"),

)
#TODO temperory workaround for MAT parser bug: Mat parser takes device name as last word
signalTemplates_2 = (
    ("MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_first_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_second_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_aebs_third_bitfield_value"),
    ("MTSI_stKBFreeze_100ms_t",
	 "MFC5xx_Device_KB_MTSI_stKBFreeze_100ms_t_sFlc25_AoaParams_flts_aebs_object_enable_bitfield"),

    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_first_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_second_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_left_third_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_first_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_second_bitfield_value"),
    ("MTSI_stKBFreeze_020ms_t",
     "MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_*_mlaeb_right_third_bitfield_value"),

)

def createMessageGroups(MESSAGE_NUM, signalTemplates, signalTemplates_1, signalTemplates_2):
    messageGroups = []
    for m in xrange(MESSAGE_NUM):
        messageGroup = {}
        # SignalDict = []
        for signalTemplate in signalTemplates:
            if signalTemplate[1].count('enable_bitfield') == 1:
                for n in range(12):
                    fullName = signalTemplate[1]
                    signal = fullName
                    signal_name = signal + '[:,' + str(n) + ']'
                    shortName = signal_name.split("_t_")[-1]
                    if shortName.count("object_") == 1:
                        shortName = shortName.split("object_")[-1]
                    messageGroup[shortName] = (signalTemplate[0], signal_name)
            else:
                fullName = signalTemplate[1]
                shortName = signalTemplate[1].split("_t_")[-1]
                shortName = "aebs_" + shortName
                messageGroup[shortName] = (signalTemplate[0], fullName)
        # SignalDict.append(messageGroup)
        messageGroups.append(messageGroup)
        for sigTemplate in [signalTemplates_1, signalTemplates_2]:
            messageGroup2 = {}
            for signalTemplate in sigTemplate:
                if signalTemplate[1].count('enable_bitfield') == 1:
                    for n in range(12):
                        fullName = signalTemplate[1]
                        signal = fullName
                        signal_name = signal + '[:,' + str(n) + ']'
                        shortName = signal_name.split("_t_")[-1]
                        if shortName.count("object_") == 1:
                            shortName = shortName.split("object_")[-1]
                        messageGroup2[shortName] = (signalTemplate[0], signal_name)
                else:
                    fullName = signalTemplate[1]
                    shortName = signalTemplate[1].split("*_")[-1]
                    messageGroup2[shortName] = (signalTemplate[0], fullName)
            messageGroups.append(messageGroup2)
    return messageGroups


messageGroups = createMessageGroups(1, signalTemplates, signalTemplates_1, signalTemplates_2)


class Calc(iCalc):
    dep = 'calc_common_time-flr25',

    def check(self):
        modules = self.get_modules()
        source = self.get_source()
        commonTime = modules.fill(self.dep[0])
        detailed_groups = []
        try:
            detailed_groups.append(source.selectSignalGroup([messageGroups[0]]))
        except:
            validSignalTemplate = self.getValidSignalTemplate(messageGroups[1:], source)
            detailed_groups.append(source.selectSignalGroup([validSignalTemplate]))
        return detailed_groups, commonTime

    def fill(self, groups, common_time):

        bitfieldInfo = []

        enable_bitfield = []
        for _id, group in enumerate(groups):
            group.all_aliases.sort()
            signal_aliases = group.all_aliases
            first_obj_bitfield_raw = group.get_value(signal_aliases[0], ScaleTime=common_time)
            first_bitfield = self.calculate_bitfield_values(first_obj_bitfield_raw)

            second_obj_bitfield_raw = group.get_value(signal_aliases[1], ScaleTime=common_time)
            second_bitfield = self.calculate_bitfield_values(second_obj_bitfield_raw)

            third_obj_bitfield_raw = group.get_value(signal_aliases[2], ScaleTime=common_time)
            third_bitfield = self.calculate_bitfield_values(third_obj_bitfield_raw)

            # ----------------------------------------------------------------------
            try:
                mlaeb_left_first_bitfield_raw = group.get_value(signal_aliases[15], ScaleTime=common_time)
                mlaeb_left_first_bitfield = self.calculate_bitfield_values(mlaeb_left_first_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_left_first_bitfield_value: Signal not available")
            try:
                mlaeb_left_second_bitfield_raw = group.get_value(signal_aliases[16], ScaleTime=common_time)
                mlaeb_left_second_bitfield = self.calculate_bitfield_values(mlaeb_left_second_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_left_second_bitfield_value: Signal not available")
            try:
                mlaeb_left_third_bitfield_raw = group.get_value(signal_aliases[17], ScaleTime=common_time)
                mlaeb_left_third_bitfield = self.calculate_bitfield_values(mlaeb_left_third_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_left_third_bitfield_value: Signal not available")

            try:
                mlaeb_right_first_bitfield_raw = group.get_value(signal_aliases[18], ScaleTime=common_time)
                mlaeb_right_first_bitfield = self.calculate_bitfield_values(mlaeb_right_first_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_right_first_bitfield_value: Signal not available")
            try:
                mlaeb_right_second_bitfield_raw = group.get_value(signal_aliases[19], ScaleTime=common_time)
                mlaeb_right_second_bitfield = self.calculate_bitfield_values(mlaeb_right_second_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_right_second_bitfield_value: Signal not available")
            try:
                mlaeb_right_third_bitfield_raw = group.get_value(signal_aliases[20], ScaleTime=common_time)
                mlaeb_right_third_bitfield = self.calculate_bitfield_values(mlaeb_right_third_bitfield_raw)
            except:
                logger.info("MFC5xx_Device_KB_MTSI_stKBFreeze_020ms_t_flts_aebs_meas_mlaeb_right_third_bitfield_value: Signal not available")

            enable_bitfield_0 = group.get_value('enable_bitfield[:,0]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_0)
            enable_bitfield_1 = group.get_value('enable_bitfield[:,1]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_1)
            enable_bitfield_2 = group.get_value('enable_bitfield[:,2]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_2)
            enable_bitfield_3 = group.get_value('enable_bitfield[:,3]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_3)
            enable_bitfield_4 = group.get_value('enable_bitfield[:,4]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_4)
            enable_bitfield_5 = group.get_value('enable_bitfield[:,5]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_5)
            enable_bitfield_6 = group.get_value('enable_bitfield[:,6]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_6)
            enable_bitfield_7 = group.get_value('enable_bitfield[:,7]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_7)
            enable_bitfield_8 = group.get_value('enable_bitfield[:,8]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_8)
            enable_bitfield_9 = group.get_value('enable_bitfield[:,9]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_9)
            enable_bitfield_10 = group.get_value('enable_bitfield[:,10]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_10)
            enable_bitfield_11 = group.get_value('enable_bitfield[:,11]', ScaleTime=common_time)
            enable_bitfield.append(enable_bitfield_11)

            attribute = []
            class_1 = np.repeat("Class", len(common_time))
            class_confidencess = np.repeat("Class Confidence", len(common_time))
            quality = np.repeat("Quality", len(common_time))
            width = np.repeat("Width", len(common_time))
            length = np.repeat("Length", len(common_time))
            motion_state = np.repeat("Motion State", len(common_time))
            lane_confidence = np.repeat("Lane Confidence", len(common_time))
            lane = np.repeat("Lane", len(common_time))
            tPF_lifetime = np.repeat("TPF Lifetime", len(common_time))
            in_path = np.repeat("In_path Quality", len(common_time))
            source = np.repeat("Source", len(common_time))
            predicted_lateral_distance = np.repeat("Predicted Lateral Distance", len(common_time))
            attribute.append(class_1)
            attribute.append(class_confidencess)
            attribute.append(quality)
            attribute.append(width)
            attribute.append(length)
            attribute.append(motion_state)
            attribute.append(lane_confidence)
            attribute.append(lane)
            attribute.append(tPF_lifetime)
            attribute.append(in_path)
            attribute.append(source)
            attribute.append(predicted_lateral_distance)

            for i in range(len(first_bitfield)):
                bitfield = {}
                chararray = np.chararray(first_bitfield[i].shape)
                chararray[:] = 'NA'
                bitfield["first_bitfield"] = first_bitfield[i]
                bitfield["second_bitfield"] = second_bitfield[i]
                bitfield["third_bitfield"] = third_bitfield[i]
                try:
                    bitfield["mlaeb_left_first_bitfield"] = mlaeb_left_first_bitfield[i]
                except:
                    bitfield["mlaeb_left_first_bitfield"] = chararray
                try:
                    bitfield["mlaeb_left_second_bitfield"] = mlaeb_left_second_bitfield[i]
                except:
                    bitfield["mlaeb_left_second_bitfield"] = chararray
                try:
                    bitfield["mlaeb_left_third_bitfield"] = mlaeb_left_third_bitfield[i]
                except:
                    bitfield["mlaeb_left_third_bitfield"] = chararray
                try:
                    bitfield["mlaeb_right_first_bitfield"] = mlaeb_right_first_bitfield[i]
                except:
                    bitfield["mlaeb_right_first_bitfield"] = chararray
                try:
                    bitfield["mlaeb_right_second_bitfield"] = mlaeb_right_second_bitfield[i]
                except:
                    bitfield["mlaeb_right_second_bitfield"] = chararray
                try:
                    bitfield["mlaeb_right_third_bitfield"] = mlaeb_right_third_bitfield[i]
                except:
                    bitfield["mlaeb_right_third_bitfield"] = chararray

                bitfield["enable_bitfield"] = enable_bitfield[i]
                bitfield["valid"] = np.ones_like(common_time, dtype=bool)
                bitfield["attribute"] = attribute[i]
                bitfieldInfo.append(bitfield)

        return common_time, bitfieldInfo

    def calculate_bitfield_values(self, bitfield):
        bitfield_info = []
        class_1 = np.zeros_like(bitfield, dtype=int)
        class_confidence = np.zeros_like(bitfield, dtype=int)
        quality = np.zeros_like(bitfield, dtype=int)
        width = np.zeros_like(bitfield, dtype=int)
        length = np.zeros_like(bitfield, dtype=int)
        motion_state = np.zeros_like(bitfield, dtype=int)
        lane_confidence = np.zeros_like(bitfield, dtype=int)
        lane = np.zeros_like(bitfield, dtype=int)
        tPF_lifetime = np.zeros_like(bitfield, dtype=int)
        in_path_quality = np.zeros_like(bitfield, dtype=int)
        source = np.zeros_like(bitfield, dtype=int)
        predicted_lateral_distance = np.zeros_like(bitfield, dtype=int)

        for i in range(len(bitfield)):
            binaryValueBitfield = list("%012d" % int(bin(bitfield[i]).replace("0b", "")))
            class_1[i] = int(binaryValueBitfield[0])
            class_confidence[i] = int(binaryValueBitfield[1])
            quality[i] = int(binaryValueBitfield[2])
            width[i] = int(binaryValueBitfield[3])
            length[i] = int(binaryValueBitfield[4])
            motion_state[i] = int(binaryValueBitfield[5])
            lane_confidence[i] = int(binaryValueBitfield[6])
            lane[i] = int(binaryValueBitfield[7])
            tPF_lifetime[i] = int(binaryValueBitfield[8])
            in_path_quality[i] = int(binaryValueBitfield[9])
            source[i] = int(binaryValueBitfield[10])
            predicted_lateral_distance[i] = int(binaryValueBitfield[11])

        bitfield_info.append(class_1)
        bitfield_info.append(class_confidence)
        bitfield_info.append(quality)
        bitfield_info.append(width)
        bitfield_info.append(length)
        bitfield_info.append(motion_state)
        bitfield_info.append(lane_confidence)
        bitfield_info.append(lane)
        bitfield_info.append(tPF_lifetime)
        bitfield_info.append(in_path_quality)
        bitfield_info.append(source)
        bitfield_info.append(predicted_lateral_distance)
        return bitfield_info

    def getValidSignalTemplate(self, signalGroups, source):
        # Distinct device names from template: list(set([a[0] for a in signalTemplates2_1]))
        # list(source.Parser.iterSignalNames("MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t"))
        # source.Parser.Devices["MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t"]
        # [signal for signal in source.Parser.Devices["MFC5xx Device.KB.MTSI_stKBFreeze_020ms_t"].keys()
        # if signal.endswith("_aebs_first_bitfield_value")]
        validSignalTemplate = {}
        originalSignalNames = {}
        distinctDevices_1 = list(set([a[0] for a in signalTemplates_1]))
        distinctDevices_2 = list(set([a[0] for a in signalTemplates_2]))
        # distinctDevices_1.extend(distinctDevices_2)
        _, extension = os.path.splitext(source.BaseName)
        for device in distinctDevices_1:
            #TODO this is for H5 specific
            try:
                if extension == ".h5":
                    list(source.Parser.iterSignalNames(device))
                originalSignalNames[device] = source.Parser.Devices[device].keys()
                signalGroup = signalGroups[0]
            except KeyError:
                logger.warning("Missing device in measurement: {}".format(device))
                break
            except Exception as e:
                logger.critical(str(e))
                break
        for device in distinctDevices_2:
            #TODO this is for H5 specific
            try:
                if extension == ".h5":
                    list(source.Parser.iterSignalNames(device))
                originalSignalNames[device] = source.Parser.Devices[device].keys()
                signalGroup = signalGroups[1]
            except KeyError:
                logger.warning("Missing device in measurement: {}".format(device))
                break
            except Exception as e:
                logger.critical(str(e))
                break
        if len(originalSignalNames) == 0:
            logger.error("Missing devices in measurement: {}".format(distinctDevices_1 + distinctDevices_2))
            return validSignalTemplate

        for alias, deviceSignalTuple in signalGroup.items():
            if "*" in deviceSignalTuple[1]:
                SIGNAL_FOUND_FLAG = False
                start, end = deviceSignalTuple[1].split("*")
                for originalSignalName in originalSignalNames[deviceSignalTuple[0]]:
                    if originalSignalName.startswith(start) and originalSignalName.endswith(end):
                        validSignalTemplate[alias] = (deviceSignalTuple[0], originalSignalName,)
                        SIGNAL_FOUND_FLAG = True
                        break
                if not SIGNAL_FOUND_FLAG:
                    logger.critical("Missing signal name in measurement: {}".format(deviceSignalTuple[1]))
            else:
                validSignalTemplate[alias] = deviceSignalTuple

        return validSignalTemplate



if __name__ == '__main__':
    from config.Config import init_dataeval

    meas_path = r"C:\KBData\__PythonToolchain\Meas\bitField\mi5id786__2022-04-20_07-53-37.mat"
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    conti = manager_modules.calc('fill_bitfield_aebs_tracks@aebs.fill', manager)
    print(conti)
