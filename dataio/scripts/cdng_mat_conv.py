from argparse import ArgumentParser
from measparser.cdng_meas_data_conv import CdngMeasToHdf5Converter
import glob
import os

parser = ArgumentParser(description='Converts MAT files created by ControlDeskNG measurement')
parser.add_argument('meas_dir',
                    help='Path to the directory containing the measurement files')

args = parser.parse_args()

test_meas = glob.glob(os.path.join(args.meas_dir, '*.mat'))
converter = CdngMeasToHdf5Converter(meas_type='mat', mdl_meas_platform_names=['MABX'])
converter(test_meas)