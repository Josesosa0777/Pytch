import scipy.io as scio
import os
import h5py
import numpy
from collections import OrderedDict
import time
import pywintypes
import itertools
try:
    import measurementdataapilib
except ImportError:
    measurementdataapilib = None


class ConverterException(Exception):
    pass


class CdngMeasToHdf5Converter(object):
    def __init__(self, h5_file_path='', meas_type='cdng', mdl_meas_platform_names=['Platform'], 
                 bus_meas_platform_names=['CAN1_J1939', 'CAN2_Fusion'], multimedia_meas_platform_names=['Multimedia']):
        self.accept_meas_types = {'mat': ['.mat'], 'cdng': ['.idf', '.mf4']}
        self.h5_file_path = h5_file_path
        if meas_type in ['mat', 'cdng']:
            self.meas_type = meas_type
        else:
            raise ConverterException('Only "mat" and "cdng" values are accepted for meas_type. You have given: %s'
                                     % meas_type)
        if meas_type == 'cdng' and measurementdataapilib is None:
            raise ConverterException('The package "measurementdataapilib" has to be successfully imported '
                                     'to be able to convert from dSPACE measurement formats (IDF, CDNG-MF4)')
        self.mdl_meas_platform_names = mdl_meas_platform_names
        self.bus_meas_platform_names = bus_meas_platform_names
        self.multimedia_meas_platform_names = multimedia_meas_platform_names
        self.measurements = OrderedDict()
        self.h5_files = OrderedDict()
        self._DEV_EXT_MAX_UNIT = 2
        self._H5_GRP_MAX_UNIT = 3
        return

    def __call__(self, meas_files, vs_meas_fname=None):
        self.load_meas_files(meas_files)
        for h5_fname, meas_data in self.measurements.iteritems():
            self.create_h5_files(h5_fname, meas_data)
            self.fill_times_grp(h5_fname, meas_data)
            self.fill_devices_grp(h5_fname, meas_data)
        if len(self.measurements) == 1 and vs_meas_fname is not None:
            self.add_video_sync_data(vs_meas_fname, h5_fname)
        self.close_h5_files()
        return

    def load_meas_files(self, meas_files):
        if isinstance(meas_files, list) and len(meas_files) > 0:
            meas_files = list(set(meas_files))
            if len(self.h5_file_path) != 0:
                raise ConverterException('If more than one measurement is to be converted do not give non-zero-length '
                                         'string for h5_file_path. You have given: %s' % self.h5_file_path)
            for meas_file in meas_files:
                h5_fname = os.path.splitext(meas_file)[0] + '.h5'
                self.h5_files.setdefault(h5_fname, None)
        else:
            meas_files = [meas_files] if not isinstance(meas_files, list) else meas_files
            if len(self.h5_file_path) == 0:
                raise ConverterException('If only one measurement is to be converted a proper non-zero-length string '
                                         'has to be given for h5_file_path. You have given a zero-length string.')
            self.h5_files.setdefault(self.h5_file_path, None)
        if self.meas_type == 'mat':
            for f_idx, meas_file in enumerate(meas_files):
                file_ext = os.path.splitext(meas_file)[-1]
                if file_ext in self.accept_meas_types[self.meas_type]:
                    meas_data = self._load_mat_file(meas_file)
                    self._correct_mtl_struct(meas_data)
                    self._process_mat_data(meas_data)
                    corr_h5_file = self.h5_files.keys()[f_idx]
                    self.measurements[corr_h5_file] = meas_data
        else:
            meas_cont = measurementdataapilib.Measurements()
            meas_cont.RemoveAll()
            for f_idx, meas_file in enumerate(meas_files):
                file_ext = os.path.splitext(meas_file)[-1]
                if file_ext in self.accept_meas_types[self.meas_type]:
                    meas_data = meas_cont.Load(meas_file)
                    meas_data = self._process_cdng_data(meas_data)
                    corr_h5_file = self.h5_files.keys()[f_idx]
                    self.measurements[corr_h5_file] = meas_data
            meas_cont.RemoveAll()
        if len(self.measurements) == 0:
            raise ConverterException('None of the measurements input is of the acceptable type. You have requested %s '
                                     'for meas_type but none of the measurements you have input were of %s type.' %
                                     (self.meas_type, ' or '.join(self.accept_meas_types[self.meas_type])))
        return

    # def load_meas_mtl_struct(self, struct_name):
    #     if len(self.h5_file_path) == 0:
    #         raise ConverterException('If measurement data stored in Matlab workspace is to be converted a proper '
    #                                  'non-zero-length string has to be given for h5_file_path. You have given a '
    #                                  'zero-length string.')
    #     self.h5_files.setdefault(self.h5_file_path, None)
    #     mtl = matlablib2.Matlab()
    #     mtl.Open()
    #     meas_data = mtl.GetArray(struct_name)
    #     self._correct_mtl_struct(meas_data)
    #     self._correct_mtl_array(meas_data)
    #     self.measurements[self.h5_file_path] = meas_data
    #     mtl.Close()
    #     return

    def create_h5_files(self, h5_fname, meas_data, comment='', version='backup 0.1.3'):
        h5_f = h5py.File(h5_fname, 'a')
        h5_f.attrs['comment'] = comment
        h5_f.attrs['version'] = version

        meas_desc = meas_data['Description']
        h5_f.attrs['timens'] = meas_desc['General']['DateTime']
        h5_f.attrs['gen_user'] = meas_desc['General']['User']
        h5_f.attrs['gen_origin'] = meas_desc['General']['Origin']
        h5_f.attrs['gen_desc'] = meas_desc['General']['Description']
        h5_f.attrs['rec_start_cond'] = meas_desc['Recording']['StartCondition']
        h5_f.attrs['rec_stop_cond'] = meas_desc['Recording']['StopCondition']
        h5_f.attrs['meas_xaxis_offset'] = meas_desc['Measurement']['XAxisOffset']
        h5_f.attrs['meas_len'] = meas_desc['Measurement']['Length']
        h5_f.attrs['meas_start_tstamp'] = meas_desc['Measurement']['StartTimestamp']
        h5_f.attrs['meas_stop_tstamp'] = meas_desc['Measurement']['StopTimestamp']
        self.h5_files[h5_fname] = h5_f
        return

    def fill_times_grp(self, h5_fname, meas_data):
        for meas_time in meas_data['X']:
            t_data = numpy.array(meas_time['Data'])
            t_name = meas_time['Raster']
            time_key = t_name.replace(': ', '__')
            if t_data.size:
                if len(t_data.shape) == 0:
                    t_data = t_data.reshape((t_data.size,))
                times_grp = self.h5_files[h5_fname].require_group('/times/')
                dset = times_grp.create_dataset(time_key, data=t_data, compression='gzip')
                dset.attrs['device'] = meas_time['Device']
        return

    def fill_devices_grp(self, h5_fname, meas_data):
        for meas_value in meas_data['Y']:
            if meas_value['Device'] in self.bus_meas_platform_names:
                can_ctrl, can_msg_name = meas_value['Path'].split('/CANChannel/')
                can_id = meas_value['Raster'].split(': ')[-1]
                can_ctrl = can_ctrl.split('/')[-1]
                if ':' in can_id:
                    can_id, multiplexor_val = can_id.split(':')
                    dev_name_ext = '%x-%s-%s-%s' % (int(can_id), multiplexor_val, meas_value['Device'], can_ctrl)
                else:
                    dev_name_ext = '%x-%s-%s' % (int(can_id), meas_value['Device'], can_ctrl)
                short_dev_name = can_msg_name.split('/')[0]
                sgn_grp_name = meas_value['Name']
            elif meas_value['Device'] in self.mdl_meas_platform_names:
                if meas_value['Path']:
                    sgn_path_mod = meas_value['Path'].replace(' ', '_')
                    sgn_path_mod = sgn_path_mod.replace('\\n', '')
                    sgn_path_mod = sgn_path_mod.replace('//', '__')
                    sgn_path_mod = sgn_path_mod.split('/')
                    if sgn_path_mod.count('Model_Root') > 1:
                        ref_mdl_root_idx = sgn_path_mod.index('Model_Root', 1)
                        lower_bound = ref_mdl_root_idx - 1
                        upper_bound = ref_mdl_root_idx + 1
                        del sgn_path_mod[lower_bound:upper_bound]
                    dev_name_ext, short_dev_name, sgn_grp_name = self._def_h5_grp_path(sgn_path_mod, meas_value['Name'])
                else:
                    short_dev_name = 'no_path'
                    dev_name_ext = 'no_path'
                    sgn_grp_name = meas_value['Name']
            elif meas_value['Device'] in self.multimedia_meas_platform_names:
                sgn_path_mod = meas_value['Path'].split('/')
                dev_name_ext = sgn_path_mod[1]
                short_dev_name = meas_value['Device']
                sgn_grp_name = meas_value['Name']
            else:
                short_dev_name = 'unknown_device'
                dev_name_ext = 'unknown_device'
                sgn_grp_name = meas_value['Name']

            grp_path = '/devices/%s/%s/%s' % (short_dev_name, dev_name_ext, sgn_grp_name)
            t_for_sl = meas_value['Raster'].replace(': ', '__')
            time_link = '/times/%s' % t_for_sl
            v_data = numpy.array(meas_value['Data'])
            if v_data.size:
                if len(v_data.shape) == 0:
                    v_data = v_data.reshape((v_data.size,))
                v_grp = self.h5_files[h5_fname].require_group(grp_path)
                v_grp['time'] = h5py.SoftLink(time_link)
                dset = v_grp.create_dataset('value', data=v_data, compression='gzip')
                dset.attrs['unit'] = meas_value['Unit']
                dset.attrs['name'] = meas_value['Name']
                dset.attrs['disp_id'] = meas_value['DisplayIdentifier']
                dset.attrs['device'] = meas_value['Device']
                dset.attrs['path'] = meas_value['Path']
                dset.attrs['sc_name'] = meas_value['ScalingName']
                dset.attrs['sc_desc'] = meas_value['ScalingDescription']
                dset.attrs['sc_format'] = meas_value['ScalingFormat']
                dset.attrs['sc_type'] = meas_value['ScalingType']
                dset.attrs['sc_factor'] = meas_value['ScalingFactor']
                dset.attrs['sc_offset'] = meas_value['ScalingOffset']
                dset.attrs['sc_coeff'] = meas_value['ScalingCoefficients']
                dset.attrs['sc_formula'] = meas_value['ScalingFormula']
        return

    def add_video_sync_data(self, vs_meas_fname, h5_fname):
        h5v_f = h5py.File(vs_meas_fname, 'r')
        if 'video_sync_data' in h5v_f.attrs:
            vs_grp = h5v_f['/devices'].values()[0].values()[0].values()[0]
            vs_time = vs_grp['time']
            vs_t_link = h5v_f.get(vs_time.name, getlink=True)
            vs_t_link = vs_t_link.path
            vs_value = vs_grp['value']
            dset = self.h5_files[h5_fname].create_dataset(vs_t_link, data=vs_time.value)
            for k, v in vs_time.attrs.iteritems():
                dset.attrs[k] = v
            dset = self.h5_files[h5_fname].create_dataset(vs_value.name, data=vs_value.value)
            for k, v in vs_value.attrs.iteritems():
                dset.attrs[k] = v
            grp = self.h5_files[h5_fname].require_group(vs_time.parent.name)
            grp['time'] = h5py.SoftLink(vs_t_link)
        else:
            raise ConverterException('Unsupported file format for video sync data!')
        h5v_f.close()
        return

    def close_h5_files(self):
        for h5_file in self.h5_files.itervalues():
            h5_file.close()
        return

    def _def_h5_grp_path(self, sgn_pth, sgn_name):
        pth_len = len(sgn_pth)
        if pth_len < self._DEV_EXT_MAX_UNIT:
            start_idx = 0
            end_idx = self._DEV_EXT_MAX_UNIT / 2
            dev_name_ext = sgn_pth[start_idx:end_idx]

            start_idx = pth_len-len(dev_name_ext)
            end_idx = pth_len
            short_dev_name = sgn_pth[start_idx:end_idx]

            sgn_grp_name = [sgn_name]
        elif self._DEV_EXT_MAX_UNIT <= pth_len < (self._DEV_EXT_MAX_UNIT + 2 * self._H5_GRP_MAX_UNIT):
            start_idx = 0
            end_idx = self._DEV_EXT_MAX_UNIT
            dev_name_ext = sgn_pth[start_idx:end_idx]

            start_idx = self._DEV_EXT_MAX_UNIT
            end_idx = self._DEV_EXT_MAX_UNIT + min(self._H5_GRP_MAX_UNIT, pth_len - len(dev_name_ext))
            if start_idx == end_idx:
                start_idx -= 1
            if pth_len == (self._DEV_EXT_MAX_UNIT + self._H5_GRP_MAX_UNIT):
                end_idx -= 1
            short_dev_name = sgn_pth[start_idx:end_idx]

            start_idx = end_idx
            end_idx = pth_len
            sgn_grp_name = sgn_pth[start_idx:end_idx] + [sgn_name]
        else:
            start_idx = pth_len - (self._H5_GRP_MAX_UNIT - 1)
            end_idx = pth_len
            sgn_grp_name = sgn_pth[start_idx:end_idx] + [sgn_name]

            start_idx = pth_len - len(sgn_grp_name) - self._H5_GRP_MAX_UNIT
            end_idx = pth_len - len(sgn_grp_name)
            short_dev_name = sgn_pth[start_idx:end_idx]

            start_idx = 0
            end_idx = pth_len - len(short_dev_name) - len(sgn_grp_name)
            dev_name_ext = sgn_pth[start_idx:end_idx]
        dev_name_ext = '_'.join(dev_name_ext)
        short_dev_name = '_'.join(short_dev_name)
        sgn_grp_name = '_'.join(sgn_grp_name)
        return dev_name_ext, short_dev_name, sgn_grp_name

    def _load_mat_file(self, filename):
        data = scio.loadmat(filename, struct_as_record=False, squeeze_me=True)
        header_keys = data.keys()
        main_arr_name = next(x for x in header_keys if x[:2] != '__' and x[-2:] != '__')
        data = data[main_arr_name]
        mtl_data = {}
        if isinstance(data, scio.matlab.mio5_params.mat_struct):
            mtl_data = self._mat_obj_to_dict(data)
        for mtl_key in mtl_data:
            if isinstance(mtl_data[mtl_key], numpy.ndarray):
                mtl_data[mtl_key] = list(mtl_data[mtl_key])
                item_cnt = len(mtl_data[mtl_key])
                for item_idx in xrange(item_cnt):
                    mtl_data[mtl_key][item_idx] = self._mat_obj_to_dict(mtl_data[mtl_key][item_idx])
        return mtl_data

    def _mat_obj_to_dict(self, mat_obj):
        mat_dict = {}
        for strg in mat_obj._fieldnames:
            elem = mat_obj.__dict__[strg]
            if isinstance(elem, scio.matlab.mio5_params.mat_struct):
                mat_dict[strg] = self._mat_obj_to_dict(elem)
            else:
                mat_dict[strg] = elem
        return mat_dict

    @staticmethod
    def _correct_mtl_struct(meas_data):
        if not isinstance(meas_data['X'], list):
            meas_data['X'] = [meas_data['X']]
        if not isinstance(meas_data['Y'], list):
            meas_data['Y'] = [meas_data['Y']]
        return

    @staticmethod
    def _correct_mtl_array(meas_data):
        if any(isinstance(t_data, list) for t_data in meas_data['X']):
            meas_data['X'] = list(itertools.chain.from_iterable(meas_data['X']))
        if any(isinstance(t_data, list) for t_data in meas_data['Y']):
            meas_data['Y'] = list(itertools.chain.from_iterable(meas_data['Y']))
        return

    @staticmethod
    def _process_mat_data(meas_data):
        for meas_value in meas_data['Y']:
            meas_value['Data'] = numpy.array(meas_value['Data'])
            can_id = meas_value['Raster'].split(': ')[-1]
            if meas_value['Device'] in ['CAN1_J1939', 'CAN2_Fusion']:
                if ':' in can_id:
                    can_id, multiplex_id = can_id.split(':')
                    can_id = int(can_id) | 2147483648
                    sc_name = 'DT_DP_IPDU_%010d_%s_%s' % (can_id, multiplex_id, meas_value['Name'])
                else:
                    can_id = int(can_id) | 2147483648
                    sc_name = 'DT_%010d_%s' % (can_id, meas_value['Name'])
            else:
                sc_name = 'Identical'
            upd_dict_v = {'ScalingName': sc_name, 'ScalingDescription': '', 'ScalingFormat': '%g', 'ScalingType': 0,
                          'ScalingFactor': 1.0, 'ScalingOffset': 0.0, 'ScalingCoefficients': [], 'ScalingFormula': ''}
            meas_value.update(upd_dict_v)
            t_index = meas_value['XIndex'] - 1  # Matlab indexing starts from 1 and not 0
            if 'Device' not in meas_data['X'][t_index].keys():
                meas_data['X'][t_index]['Data'] = numpy.array(meas_data['X'][t_index]['Data'])
                upd_dict_t = {'Device': meas_value['Device']}
                meas_data['X'][t_index].update(upd_dict_t)
        return

    @staticmethod
    def _process_cdng_data(meas_data):
        # this method is to be used only if measurements of CDNG format (IDF, CDNG-MF4) are used as input
        meas_ddict = {}

        meas_desc = meas_ddict.setdefault('Description', {})
        meas_dgen = meas_desc.setdefault('General', {})
        dt = meas_data.DescriptionCategories('General').DateTime
        meas_dgen['DateTime'] = dt.Format('%Y.%m.%d %H:%M:%S')
        meas_dgen['User'] = meas_data.DescriptionCategories('General').User
        meas_dgen['Origin'] = meas_data.DescriptionCategories('General').Origin
        meas_dgen['Description'] = meas_data.DescriptionCategories('General').Description
        meas_drec = meas_desc.setdefault('Recording', {})
        meas_drec['StartCondition'] = meas_data.DescriptionCategories('Recording').StartCondition
        meas_drec['StopCondition'] = meas_data.DescriptionCategories('Recording').StopCondition
        meas_dmeas = meas_desc.setdefault('Measurement', {})
        meas_dmeas['XAxisOffset'] = meas_data.DescriptionCategories('Measurement').XAxisOffset
        meas_dmeas['Length'] = meas_data.DescriptionCategories('Measurement').Length
        meas_dmeas['StartTimestamp'] = meas_data.DescriptionCategories('Measurement').StartTimestamp
        meas_dmeas['StopTimestamp'] = meas_data.DescriptionCategories('Measurement').StopTimestamp

        meas_times = meas_ddict.setdefault('X', [])
        for idx in xrange(meas_data.XAxes.Count):
            meas_time = dict()
            meas_time['Data'] = numpy.array(meas_data.XAxes(idx).Data)
            meas_time['Raster'] = meas_data.XAxes(idx).Name
            meas_time['Device'] = meas_data.XAxes(idx).Device
            meas_times.append(meas_time)

        meas_values = meas_ddict.setdefault('Y', [])
        for idx in xrange(meas_data.Signals.Count):
            meas_value = dict()
            meas_value['Name'] = meas_data.Signals(idx).Name
            meas_value['Path'] = meas_data.Signals(idx).Path
            meas_value['Device'] = meas_data.Signals(idx).Device
            meas_value['Raster'] = meas_data.Signals(idx).XAxis.Name
            meas_value['Data'] = numpy.array(meas_data.Signals(idx).Data)
            meas_value['DisplayIdentifier'] = meas_data.Signals(idx).DisplayIdentifier
            meas_value['Unit'] = meas_data.Signals(idx).Scaling.Unit
            meas_value['ScalingName'] = meas_data.Signals(idx).Scaling.Name
            meas_value['ScalingDescription'] = meas_data.Signals(idx).Scaling.Description
            meas_value['ScalingFormat'] = meas_data.Signals(idx).Scaling.Format
            sc_type = meas_data.Signals(idx).Scaling.Type
            sc_factor = meas_data.Signals(idx).Scaling.Factor
            meas_value['ScalingType'] = sc_type
            meas_value['ScalingFactor'] = 0.0
            meas_value['ScalingOffset'] = 0.0
            meas_value['ScalingCoefficients'] = []
            meas_value['ScalingFormula'] = ''
            if (sc_type == measurementdataapilib.constants.stLinear and
                    hasattr(meas_data.Signals(idx).Scaling, 'Factor') and
                    sc_factor < 0.0):
                meas_value['ScalingCoefficients'] = numpy.array([0.0, sc_factor, 0.0, 0.0, 1.0])
                meas_value['ScalingType'] = measurementdataapilib.constants.stRationalFunction
            elif (sc_type == measurementdataapilib.constants.stLinear and
                  hasattr(meas_data.Signals(idx).Scaling, 'Factor') and
                  hasattr(meas_data.Signals(idx).Scaling, 'Offset')):
                meas_value['ScalingFactor'] = sc_factor
                meas_value['ScalingOffset'] = meas_data.Signals(idx).Scaling.Offset
            elif (sc_type == measurementdataapilib.constants.stRationalFunction and
                  hasattr(meas_data.Signals(idx).Scaling, 'Coefficients')):
                meas_value['ScalingCoefficients'] = numpy.array(meas_data.Signals(idx).Scaling.Coefficients)
            elif (sc_type == measurementdataapilib.constants.stFormula and
                  hasattr(meas_data.Signals(idx).Scaling, 'Formula')):
                meas_value['ScalingFormula'] = meas_data.Signals(idx).Scaling.Formula
            meas_values.append(meas_value)
        return meas_ddict


class Hdf5ToMf4Converter(object):
    class Hdf5Names(list):
        def add(self, path):
            pth_sp = path.split('/')
            if len(pth_sp) == 3:
                self.append(path)
            return

    def __init__(self):
        self.h5_names = Hdf5ToMf4Converter.Hdf5Names()
        self.cdng_files = OrderedDict()
        self.h5_files = OrderedDict()
        if measurementdataapilib is None:
            raise ConverterException('The package "measurementdataapilib" has to be successfully imported '
                                     'to be able to convert to dSPACE measurement formats (IDF, CDNG-MF4)')
        return

    def __call__(self, h5_files_paths):
        self.load_h5_files(h5_files_paths)
        for meas_fname in self.h5_files.keys():
            self.write_meas_desc(meas_fname)
            self.fill_meas_with_data(meas_fname)
            self.save_meas_file(meas_fname)
        return

    def load_h5_files(self, h5_files_paths):
        if isinstance(h5_files_paths, list) and len(h5_files_paths) > 0:
            h5_files_paths = list(set(h5_files_paths))
        else:
            h5_files_paths = [h5_files_paths] if not isinstance(h5_files_paths, list) else h5_files_paths
        meas_cont = measurementdataapilib.Measurements()
        meas_cont.RemoveAll()
        for h5_file_path in h5_files_paths:
            fname = os.path.splitext(h5_file_path)[0]
            meas_name = os.path.split(fname)[-1]
            fname += '.mf4'
            self.h5_files.setdefault(fname, h5py.File(h5_file_path, 'r'))
            self.cdng_files.setdefault(fname, meas_cont.Add(meas_name))
        return

    def write_meas_desc(self, meas_fname):
        h5_f = self.h5_files[meas_fname]
        meas = self.cdng_files[meas_fname]
        h5f_time = time.strptime(h5_f.attrs['timens'], '%Y.%m.%d. %H:%M:%S')
        meas.DescriptionCategories('General').DateTime = pywintypes.Time(h5f_time)
        meas.DescriptionCategories('General').User = h5_f.attrs['gen_user']
        meas.DescriptionCategories('General').Origin = h5_f.attrs['gen_origin']
        meas.DescriptionCategories('General').Description = h5_f.attrs['gen_desc']
        meas.DescriptionCategories('Measurement').XAxisOffset = h5_f.attrs['meas_xaxis_offset']
        meas.DescriptionCategories('Measurement').Length = h5_f.attrs['meas_len']
        meas.DescriptionCategories('Measurement').StartTimestamp = h5_f.attrs['meas_start_tstamp']
        meas.DescriptionCategories('Measurement').StopTimestamp = h5_f.attrs['meas_stop_tstamp']
        meas.DescriptionCategories('Recording').StartCondition = h5_f.attrs['rec_start_cond']
        meas.DescriptionCategories('Recording').StopCondition = h5_f.attrs['rec_stop_cond']
        return

    def fill_meas_with_data(self, meas_fname):
        h5_f = self.h5_files[meas_fname]
        meas = self.cdng_files[meas_fname]
        devs_grp = h5_f['devices']
        devs_grp.visit(self.h5_names.add)
        for h5_name in self.h5_names:
            time_link = h5_f.get('/devices/' + h5_name + '/time', getlink=True)
            sgn_val = h5_f['/devices/' + h5_name + '/value']
            sgn_time = h5_f['/devices/' + h5_name + '/time']
            time_key = time_link.path.split('/')[-1]

            xaxis_name = time_key.replace('__', ': ')
            try:
                tmp = sgn_val.attrs['device'] + '/' + xaxis_name
                xaxis = meas.XAxes.Item(tmp)
            except pywintypes.com_error, conv_err:
                if conv_err.excepinfo[-1] == -2146233086:
                    xaxis_data = sgn_time.value.tolist()
                    xaxis = meas.XAxes.Add(xaxis_name, sgn_val.attrs['device'], xaxis_data)
                else:
                    raise

            try:
                scaling = meas.Scalings.Add(sgn_val.attrs['sc_name'], sgn_val.attrs['sc_type'])
            except pywintypes.com_error, conv_err:
                if conv_err.excepinfo[-1] == -2147467260:
                    scaling = meas.Scalings.Item(sgn_val.attrs['sc_name'])
                else:
                    raise
            else:
                scaling.Description = sgn_val.attrs['sc_desc']
                scaling.Format = sgn_val.attrs['sc_format']
                scaling.Unit = sgn_val.attrs['unit']
                if sgn_val.attrs['sc_type'] == measurementdataapilib.constants.stLinear:
                    scaling.Factor = sgn_val.attrs['sc_factor']
                    scaling.Offset = sgn_val.attrs['sc_offset']
                elif sgn_val.attrs['sc_type'] == measurementdataapilib.constants.stRationalFunction:
                    scaling.Coefficients = sgn_val.attrs['sc_coeff']
                elif sgn_val.attrs['sc_type'] == measurementdataapilib.constants.stFormula:
                    scaling.Formula = sgn_val.attrs['sc_formula']

            sgn_data = sgn_val.value.tolist()
            meas.Signals.Add(sgn_val.attrs['name'], sgn_val.attrs['disp_id'], sgn_val.attrs['device'],
                             sgn_val.attrs['path'], sgn_data, xaxis, scaling)
            del xaxis
            del scaling
        return

    def save_meas_file(self, meas_fname):
        self.cdng_files[meas_fname].Export(meas_fname)
        return
