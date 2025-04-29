"""
Convert all measurement (matching the given extension) starting from input root directory, walking recursively
"""

import os

from preproc_xcp_meas_for_resim import preproc


def batch_convert(in_root, out_root, file_ext='.mf4', overwrite=False, verbose=False):
    for root, subdirs, files in os.walk(in_root):
        # check if mirrored directory structure exists
        out_folder  = root.replace(in_root, out_root) # noop if in_root == out_root
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        # loop on each file that matches the extension
        for file in files:
            basename, ext = os.path.splitext(file)
            if ext.lower() == file_ext.lower():
                input_file  = os.path.join(root, file)
                new_file_name = basename + '_resim.mat'
                output_file = os.path.join(out_folder, new_file_name)
                if verbose:
                  print input_file
                if os.path.exists(output_file) and not overwrite:
                    if verbose:
                        print "File skipped as already exists: %s" %output_file
                    continue
                # call converter script
                preproc(input_file, output_file)
 

if __name__ == '__main__':
    # TODO
    # import argparse

    in_root   = r"\\file\messdat\DAS"           r"\TurningAssist\06xB365\2016-10-20_TurningAssist_CP1-5_candidate" # strings concatenated
    out_root  = r"\\file\messdat\DAS\ConvertedMeas\TurningAssist\06xB365\2016-10-20_TurningAssist_CP1-5_candidate"

    batch_convert(in_root, out_root, file_ext='.mf4', overwrite=True, verbose=True)
