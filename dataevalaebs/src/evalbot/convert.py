import os
import re
import logging
import argparse
import tempfile
import glob
import sys

from execute_cmd import executeCmd
from measparser import dcnvt, ffmpeg
from aebs.dbc import dbc2filename
from osutils.remove import rm
from shutil import rmtree
from measparser.filenameparser import FileNameParser


logger = logging.getLogger('end_run.convert')
def_logger = None


VIDEO_EXTENSIONS = ('.avi', '.mkv', '.mp4', '.mov', '.wmv', '.mpeg')
SUPPORTED_VIDEO_EXTENSIONS = ('.avi', '.mkv')
CAN_EXTENSIONS = ('.blf', '.ttl', '.asc')
SUPPORTED_CAN_EXTENSIONS = ('.blf', '.ttl')


def mkstemp2(*args, **kwargs):
    fd, path = tempfile.mkstemp(*args, **kwargs)
    os.close(fd)
    return path


def searchTimeDelayedFile(filePath):
    deltaSec = 60
    
    dirname, basename = os.path.split(filePath)
    files = os.listdir(dirname)
    deltaSecs = [0]
    fn = FileNameParser(basename)
    if fn is not None:
        deltaSecs += [val for i in xrange(1, deltaSec+1) for val in (-i, +i)]  # results [-1, +1, -2, +2, ...]
    for d in deltaSecs:
        new_basename = fn.timedelta(d)
        if new_basename in files:
            return os.path.join(dirname, new_basename)
    return ''


this_dir = os.path.abspath(os.path.dirname(__file__))
dcnvtSelect = os.path.join(this_dir, 'convert_select.txt')
dcnvtRename = os.path.join(this_dir, 'convert_rename.txt')
def convertCanToMat(filePath, measFormat='.blf',
                    dbcList='default', channelList='default', convMeasFolderPath=".",
                    dcnvt=dcnvt.executable,
                    dcnvtSelect=None, dcnvtRename=None,
                    mainLogger=None, convLogger=None):
    if measFormat not in SUPPORTED_CAN_EXTENSIONS:
        mainLogger.error('Measurement format {} not supported'.format(measFormat))
        return 'Error - format not supported'
    if mainLogger is None:
        mainLogger = logging.getLogger()
    if convLogger is None:
        convLogger = logging.getLogger()
    if dbcList is None:
        return 'Error - Convert - dbc file missing'
    if dbcList == 'default':
        dbcList = (
            ('J1939_DAS.dbc', '1'),
            ('AC100_SMess_P0.dbc', '2'),
            ('A087MB_V3.2_MH11_truck_30obj.dbc', '2'),
            ('Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc', '2'),
            ('Bendix_Info3.dbc', '2'),
        )
        dbcList = [(dbc2filename[dbc], chn) for (dbc, chn) in dbcList]
    if channelList == 'default':
        channelList = ['J1939_Channel_1', 'CAN2_Channel_2']

    if not os.path.exists(convMeasFolderPath):
      os.makedirs(convMeasFolderPath)
    measFolderPath, fileName = os.path.split(filePath)
    import glob
    avi_filename = fileName
    # find files
    fn = FileNameParser(fileName)
    if fn is None:
        mainLogger.error('Filename does not match pattern: {}'.format(fileName))
        return 'Error - filename does not match pattern'
    basename = fn.base2
    channel = fn.device
    can_files = []
    for chn in channelList:
        other_can = filePath.replace(channel, chn)
        if not os.path.isfile(other_can):
            new_can = searchTimeDelayedFile(other_can)
            if not new_can:
                mainLogger.warning('{file} not found'.format(file=os.path.basename(other_can)))
                continue
            other_can = new_can
        if os.path.splitext(other_can)[1].lower() != measFormat:
            mainLogger.debug('{file} skipped, extension is not {ex}'.format(
                file=os.path.basename(other_can), ex=measFormat))
            continue
        can_files.append(other_can)
    if len(can_files) < 1:
        mainLogger.warning('No measurement files found for the specified CAN channels, skipping conversion')
        return 'Warning - No measurement files found for the specified CAN channels'

    out = '{basename}.mat'.format(basename=basename)
    out_fullname = os.path.join(convMeasFolderPath, out)
    tmp_files = {}

    try:
        # define (and also create) temporary files for dcnvt logs
        tmp_files['rep'] = mkstemp2(prefix='%s_dcnvt_report_' % basename, suffix='.txt')
        tmp_files['err'] = mkstemp2(prefix='%s_dcnvt_error_' % basename, suffix='.txt')

        # get Multimedia signal from MF4 - if requested
        if dcnvtSelect is not None:
            assert dcnvtRename is not None, "'dcnvtRename' is not specified"
            # define (and also create) further temporary files for dcnvt
            tmp_files['media'] = mkstemp2(prefix='%s_multimedia_' % basename, suffix='.mat')
            tmp_files['dcomment'] = '%s_dcomment.txt' % tmp_files['media']
            
            mf4 = os.path.join(measFolderPath, '%s.MF4' % basename)
            mdf = os.path.join(measFolderPath, '%s.mdf' % basename)
            if os.path.isfile(mf4):
                pass
            elif os.path.isfile(mdf):
                mf4 = mdf
            else:
                newMf4 = searchTimeDelayedFile(mf4)
                newMdf = searchTimeDelayedFile(mdf)
                if newMf4:
                    mf4 = newMf4
                elif newMdf:
                    mf4 = newMdf
                else:
                    mainLogger.warning('No MF4 or MDF file found for CAN, skipping conversion')
                    return 'Warning - No MF4 or MDF file found for CAN'

            cmd = '\"{dcnvt}\" -R {rep} -F {err} -i mdf4_atan -f DCommentASCII MSecondStrArray -W \"{sel}\" -t \"{ren}\" -o \"{media}\" \"{mf4}\"'.format(
                    dcnvt=dcnvt,
                    rep=tmp_files['rep'],
                    err=tmp_files['err'],
                    sel=dcnvtSelect,
                    ren=dcnvtRename,
                    media=tmp_files['media'],
                    mf4=mf4)
            convLogger.debug(cmd)
            output = executeCmd(cmd)
            convLogger.info(output)
        else:
            tmp_files['media'] = ''
            mainLogger.debug('Ignoring MF4 file, no multimedia signal will be available')

        # convert CAN files
        dbcs = []
        for name, channel in dbcList:
            if channel is not None:
                dbcs.append('-d {ch} \"{dbc_name}\"'.format(ch=channel, dbc_name=name))
            else:
                dbcs.append('-d \"{dbc_name}\"'.format(dbc_name=name))
        if os.path.exists(out_fullname):
            mainLogger.debug('Converted file already exists; removing %s' % out_fullname)
            rm(out_fullname)
        cmd = '\"{dcnvt}\" -R {rep} -F {err} -f MSecondStrArray -s 0.0 {dbcs} -o \"{out}\" \"{cans};{media}\"'.format(
                dcnvt=dcnvt,
                rep=tmp_files['rep'],
                err=tmp_files['err'],
                dbcs=' '.join(dbcs),
                out=out_fullname,
                cans=';'.join(can_files),
                media=tmp_files['media'])
        convLogger.debug(cmd)
        output = executeCmd(cmd)
        convLogger.info(output)
    finally:
        # remove temporary files
        for tmp_file in tmp_files.itervalues():
            rm(tmp_file)

    # return
    if os.path.exists(out_fullname):
        return 'Success'
    else:
        mainLogger.warn('Converted file not found in the specified folder: %s' % out)
        return 'Warning - converted file not found in the specified folder'

# legacy
def convertBlfToMat(filePath,
                    dbcList='default', channelList='default', convMeasFolderPath=".",
                    dcnvt=dcnvt.executable,
                    dcnvtSelect=None, dcnvtRename=None,
                    mainLogger=None, convLogger=None):
    return convertCanToMat(filePath, measFormat='.blf',
                           dbcList=dbcList, channelList=channelList, convMeasFolderPath=convMeasFolderPath,
                           dcnvt=dcnvt,
                           dcnvtSelect=dcnvtSelect, dcnvtRename=dcnvtRename,
                           mainLogger=mainLogger, convLogger=convLogger)

# legacy
def blfToMatConversion(filePath,
                    dbcList='default', channelList='default', convMeasFolderPath=".",
                    dcnvt=dcnvt.executable,
                    dcnvtSelect=None, dcnvtRename=None,
                    mainLogger=None, convLogger=None):
    return blfConversionToMat(filePath, measFormat='.blf',
                           dbcList=dbcList, channelList=channelList, convMeasFolderPath=convMeasFolderPath,
                           dcnvt=dcnvt,
                           dcnvtSelect=dcnvtSelect, dcnvtRename=dcnvtRename,
                           mainLogger=mainLogger, convLogger=convLogger)


def blfConversionToMat(filePath, measFormat='.blf',
                    dbcList='default', channelList='default', convMeasFolderPath=".",
                    dcnvt=dcnvt.executable,
                    dcnvtSelect=None, dcnvtRename=None,
                    mainLogger=None, convLogger=None):
    if measFormat not in SUPPORTED_CAN_EXTENSIONS:
        mainLogger.error('Measurement format {} not supported'.format(measFormat))
        return 'Error - format not supported'
    if mainLogger is None:
        mainLogger = logging.getLogger()
    if convLogger is None:
        convLogger = logging.getLogger()
    if dbcList is None:
        return 'Error - Convert - dbc file missing'
    if dbcList == 'default':
        dbcList = (
            ('J1939_DAS.dbc', '1'),
            ('AC100_SMess_P0.dbc', '2'),
            ('A087MB_V3.2_MH11_truck_30obj.dbc', '2'),
            ('Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc', '2'),
            ('Bendix_Info3.dbc', '2'),
        )
        dbcList = [(dbc2filename[dbc], chn) for (dbc, chn) in dbcList]
    if channelList == 'default':
        channelList = ['J1939_Channel_1', 'CAN2_Channel_2']

    if not os.path.exists(convMeasFolderPath):
        os.makedirs(convMeasFolderPath)
    measFolderPath, fileName = os.path.split(filePath)
    import glob
    avi_filename = fileName
    # find files
    fn = FileNameParser(fileName)
    if fn is None:
        mainLogger.error('Filename does not match pattern: {}'.format(fileName))
        return 'Error - filename does not match pattern'
    basename = fn.base2
    channel = fn.device
    can_files = []
    for chn in channelList:
        other_can = filePath.replace(channel, chn)
        if not os.path.isfile(other_can):
            new_can = searchTimeDelayedFile(other_can)
            if not new_can:
                mainLogger.warning('{file} not found'.format(file=os.path.basename(other_can)))
                continue
            other_can = new_can
        if os.path.splitext(other_can)[1].lower() != measFormat:
            mainLogger.debug('{file} skipped, extension is not {ex}'.format(
                file=os.path.basename(other_can), ex=measFormat))
            continue
        can_files.append(other_can)
    if len(can_files) < 1:
        mainLogger.warning('No measurement files found for the specified CAN channels, skipping conversion')
        return 'Warning - No measurement files found for the specified CAN channels'

    out = '{basename}.mat'.format(basename=basename)
    out_fullname = os.path.join(convMeasFolderPath, out)
    tmp_files = {}

    try:
        # define (and also create) temporary files for dcnvt logs
        tmp_files['rep'] = mkstemp2(prefix='%s_dcnvt_report_' % basename, suffix='.txt')
        tmp_files['err'] = mkstemp2(prefix='%s_dcnvt_error_' % basename, suffix='.txt')

        # convert CAN files
        dbcs = []
        for name, channel in dbcList:
            if channel is not None:
                dbcs.append('-d {ch} \"{dbc_name}\"'.format(ch=channel, dbc_name=name))
            else:
                dbcs.append('-d \"{dbc_name}\"'.format(dbc_name=name))
        if os.path.exists(out_fullname):
            mainLogger.debug('Converted file already exists; removing %s' % out_fullname)
            rm(out_fullname)
        cmd = '\"{dcnvt}\" -R {rep} -F {err} {dbcs} -s 0.0 -f M -o \"{out}\" \"{cans}\"'.format(
            dcnvt=dcnvt,
            rep=tmp_files['rep'],
            err=tmp_files['err'],
            dbcs=' '.join(dbcs),
            out=out_fullname,
            cans=';'.join(can_files),)
        convLogger.debug(cmd)
        output = executeCmd(cmd)
        convLogger.info(output)
    finally:
        # remove temporary files
        for tmp_file in tmp_files.itervalues():
            rm(tmp_file)

    # return
    if os.path.exists(out_fullname):
        return 'Success'
    else:
        mainLogger.warn('Converted file not found in the specified folder: %s' % out)
        return 'Warning - converted file not found in the specified folder'

def convertVideo(filePath, convMeasFolderPath=".", inputFormat='.mkv', outputFormat='.avi',
                 ffmpeg=ffmpeg.executable, mainLogger=None, convLogger=None):
    if mainLogger is None:
        mainLogger = logging.getLogger()
    if convLogger is None:
        convLogger = logging.getLogger()

    if not os.path.exists(convMeasFolderPath):
      os.makedirs(convMeasFolderPath)
    measFolderPath, fileName = os.path.split(filePath)
    fileExt = os.path.splitext(fileName)[1].lower()

    if fileExt != inputFormat:
        mainLogger.debug('Skipping conversion, of "{}", not in {} format'.format(fileExt, inputFormat))
        return 'Success'
    if fileExt not in SUPPORTED_VIDEO_EXTENSIONS:
        mainLogger.error('Skipping conversion, input video format "{}" is not supported'.format(fileExt))
        return 'Warning - format not supported'
    if outputFormat not in SUPPORTED_VIDEO_EXTENSIONS:
        mainLogger.error('Skipping conversion, requested video format "{}" is not supported'.format(outputFormat))
        return 'Warning - format not supported'


    outFile = os.path.splitext(fileName)[0] + outputFormat
    outFilePath = os.path.join(convMeasFolderPath, outFile)
    if fileExt == outputFormat:
        mainLogger.info('Skipping conversion, video already in requested format. Copying it to destination folder')
        import subprocess
        command ='echo F|xcopy /S /Q /Y /F ' + filePath + ' ' + outFilePath
        logger.debug("Executing command: {}".format(command))
        subprocess.call(command, shell=True)
        return 'Success'

    if os.path.exists(outFilePath):
        mainLogger.debug('Converted file already exists; removing {}'.format(outFilePath))
        rm(outFilePath)
    output = executeCmd('{ffmpeg} -i {input} {output}'.format(
                        ffmpeg=ffmpeg,
                        input=filePath,
                        output=outFilePath))
    convLogger.info(output)
    if os.path.exists(outFilePath):
        return 'Success'
    else:
        mainLogger.error('Converted file not found in the specified folder: {}'.format(outFile))
        return 'Warning - converted file not found in the specified folder'

    # vidresReq = executeCmd(ffmpeg + ' 2>&1 -i ' + filePath)
    # vidres = re.search('Stream .+ ([0-9]+x[0-9]+).+', vidresReq).group(1)
    # if vidres == '1280x720':
    #     output = executeCmd('%s -i %s -r 15 -s 640x360 %s'  %\
    #                         (ffmpeg, filePath, os.path.join(convMeasFolderPath, fileName)))
    #     convLogger.info(output)
    #     if os.path.exists(os.path.join(convMeasFolderPath, fileName)):
    #         return 'Success'
    #     else:
    #         mainLogger.error('Converted file not found in the specified folder: %s' % fileName)
    #         return 'Warning - converted file not found in the specified folder'
    # else:
    #     # TODO: implement for custom resolutions
    #     mainLogger.error('Video resolution != 1280x720')
    #     return 'Warning - video resolution != 1280x720'


def convertResim(indir, mainLogger=None, convLogger=None):
    if mainLogger is None:
        mainLogger = logging.getLogger()
    if convLogger is None:
        convLogger = logging.getLogger()

    files = [f for f in os.listdir(indir) if '.mat' in f.lower() and '_kbaebs' not in f.lower()]
    mainLogger.info('Preprocessing {num} files for resimulation in {dir}...'.format(
            num=len(files), dir=indir))
    cmd = '{python} {resim} -m --stdout-on -o {outdir} {indir}'.format(
            python=sys.executable,
            resim='C:/KBData/resimcvt/resimulation.py',  # TODO resim in toolchain
            outdir=os.path.dirname(indir),
            indir=indir)
    convLogger.info('Executing {command}'.format(command=cmd))
    output = executeCmd(cmd)
    convLogger.info(output)
    convertedFiles = [f for f in os.listdir(indir) if '_kbaebs.mat' in f.lower()]
    if len(convertedFiles) < 1:
        mainLogger.warn('Could not convert any files for resimulation!')
        # return 'Warning - could not convert resimulation files'
    else:
        mainLogger.info('Preprocessed {} files for resimulation'.format(len(convertedFiles)))
    # clean up after Uli
    rmtree('stdout_dumps', ignore_errors=True)
    rmtree('logs', ignore_errors=True)
    rmtree('mat_temp_files', ignore_errors=True)
    return 'Success'


class ConvertBase(object):
    def __init__(self, conf):
        self.conf = conf
        self.convLogger = logging.getLogger('convert')

    def convertCanToMat(self, fileName):
        if not self.conf.canConvertNeeded:
            return 'Success'
        return convertCanToMat(
            os.path.join(self.conf.measFolderPath, fileName),
            measFormat=self.conf.measFormat,
            dbcList=self.conf.dbcList,
            channelList=self.conf.canChannels,
            convMeasFolderPath=self.conf.convMeasFolderPath,
            dcnvt=self.conf.dcnvt,
            dcnvtSelect=self.conf.dcnvtSelect, dcnvtRename=self.conf.dcnvtRename,
            mainLogger=logger, convLogger=self.convLogger)

    # legacy
    def convertBlfToMat(self, fileName):
        if not self.conf.canConvertNeeded:
            return 'Success'
        return convertBlfToMat(
            os.path.join(self.conf.measFolderPath, fileName),
            dbcList=self.conf.dbcList,
            channelList=self.conf.canChannels,
            convMeasFolderPath=self.conf.convMeasFolderPath,
            dcnvt=self.conf.dcnvt,
            dcnvtSelect=self.conf.dcnvtSelect, dcnvtRename=self.conf.dcnvtRename,
            mainLogger=logger, convLogger=self.convLogger)

    def blfToMatConversion(self, fileName):
        if not self.conf.canConvertNeeded:
            return 'Success'
        return blfToMatConversion(
            os.path.join(self.conf.measFolderPath, fileName),
            dbcList=self.conf.dbcList,
            channelList=self.conf.canChannels,
            convMeasFolderPath=self.conf.convMeasFolderPath,
            dcnvt=self.conf.dcnvt,
            dcnvtSelect=self.conf.dcnvtSelect, dcnvtRename=self.conf.dcnvtRename,
            mainLogger=logger, convLogger=self.convLogger)

    def convertVideo(self, fileName):
        if not self.conf.videoConvertNeeded:
            return 'Success'
        return convertVideo(
            os.path.join(self.conf.measFolderPath, fileName),
            inputFormat=self.conf.inputFormat,
            outputFormat=self.conf.outputFormat,
            convMeasFolderPath=self.conf.convMeasFolderPath,
            ffmpeg=ffmpeg.executable,
            mainLogger=logger, convLogger=self.convLogger)

    def convert(self, db):
        fileConvertList = db.getWaitForConvertFileList('Wait')
        if fileConvertList:
            self.convLogger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.path.join(self.conf.logFolderPath, 'conversion.log'))
            fh.setLevel(logging.INFO)
            fhFormatter = logging.Formatter('%(message)s')
            fh.setFormatter(fhFormatter)
            self.convLogger.addHandler(fh)

            for fc in fileConvertList:
                logger.info('Converting file: %s' % fc)
                ex = os.path.splitext(fc)[1].lower()
                if ex in VIDEO_EXTENSIONS:
                    convStatus = self.convertVideo(fc)
                elif ex in CAN_EXTENSIONS:
                    convStatus = self.convertCanToMat(fc)
                    if convStatus != 'Success':
                        convStatus = self.blfToMatConversion(fc)
                else:
                    convStatus = 'Success'
                db.setConvertStatus(fc, convStatus)
                if 'Error' in convStatus:
                    self.convLogger.removeHandler(fh)
                    return 'Error - Convert - In conversion %s' % fc
            self.convLogger.removeHandler(fh)
        return 'Success'


class ConvertEndRun(ConvertBase):
    pass


class ConvertResim(ConvertBase):
    def convertResim(self):
        self.convLogger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(self.conf.logFolderPath, 'conversion.log'))
        fh.setLevel(logging.INFO)
        fhFormatter = logging.Formatter('%(message)s')
        fh.setFormatter(fhFormatter)
        self.convLogger.addHandler(fh)
        convStatus = convertResim(indir=self.conf.convMeasFolderPath,
                                  mainLogger=logger,
                                  convLogger=self.convLogger)
        self.convLogger.removeHandler(fh)
        return convStatus

    def convert(self, db):
        fileConvertList = db.getWaitForConvertFileList('Wait')
        if not fileConvertList:
            return 'Success'
        ConvertBase.convert(self, db)
        convStatus = self.convertResim()
        return convStatus


class ResimOnly(ConvertResim):
    def convert(self, db):
        fileConvertList = db.getWaitForConvertFileList('Wait')
        if not fileConvertList:
            return 'Success'
        convStatus = self.convertResim()
        return convStatus


class Convert(object):
    class_lut = {
        n: c for n, c in globals().iteritems() if type(c) is type
                                              and issubclass(c, ConvertBase)
                                              and c is not ConvertBase
    }

    def __new__(cls, conf):
        convertClass = ConvertEndRun
        try:
            convertClass = cls.class_lut[conf.convertClass]
            logger.debug("Converting with '{cls}'".format(cls=convertClass.__name__))
        except KeyError:
            logger.warning("ConvertClass '{cls}' not found, using 'ConvertEndRun' as default".format(
                    cls=convertClass.__name__))
        return convertClass(conf)


if __name__ == '__main__':
    # create logger
    def_logger = logging.getLogger()
    def_logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    chFormatter = logging.Formatter('[%(levelname)s] %(message)s')
    ch.setFormatter(chFormatter)
    def_logger.addHandler(ch)

    # parse arguments
    parser = argparse.ArgumentParser(description=
      "convert - CAN+MF4 and AVI conversion")
    parser.add_argument('files',
      nargs='+',
      help='Files to be processed. Wildcards accepted.')
    parser.add_argument('--outdir',
      default='.',
      help='Output directory of the converted files. Will be created if not exists.')
    parser.add_argument('--format',
      default='.blf',
      help='CAN measurement format, supported extensions: .blf, .ttl')
    parser.add_argument('--vidformat',
      default='.avi',
      help='video output measurement format, supported extensions: .avi, .mkv')
    args = parser.parse_args()

    # convert
    for arg in args.files:
        f_list = glob.glob(arg)
        if not f_list:
            logger.warning('No file(s) found for %s' % arg)
            continue
        for f in f_list:
            f_lower = f.lower()
            ext = os.path.splitext(f_lower)[1]
            if ext in VIDEO_EXTENSIONS:
                logger.info('Converting video file: %s' % f)
                convertVideo(f, convMeasFolderPath=args.outdir, outputFormat=args.vidformat)
            elif ext.lower() in CAN_EXTENSIONS and ('j1939_channel_1' in f_lower or 'j1939_public_channel_1' in f_lower):
                logger.info('Converting measurement file: %s and friends' % f)
                convertCanToMat(f, convMeasFolderPath=args.outdir, measFormat=arg.format)
            else:
                logger.info('Skip %s (no rule defined for such file)' % f)
