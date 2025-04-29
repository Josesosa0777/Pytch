import os
import shutil
from datetime import date


def remove_can_files(source_dir, destination_dir):
    try:
        subdirs = [subdir for subdir in os.listdir(source_dir) if os.path.join(source_dir, subdir)]
        for subdir in subdirs:
            source_path = os.path.join(source_dir, subdir)
            if str(date.today()) > subdir and os.path.isdir(os.path.join(source_dir, subdir)):
                destination_path = os.path.join(destination_dir, subdir)
                if os.path.exists(destination_path):
                    files = os.listdir(source_path)
                    for file in files:
                        meas_path = os.path.join(source_path, file)
                        shutil.move(meas_path, destination_path)
                        os.rmdir(source_path)
                else:
                    shutil.move(source_path, destination_path)
            elif not os.path.isdir(os.path.join(source_dir, subdir)):
                os.remove(os.path.join(source_dir, subdir))
    except:
        pass


if __name__ == "__main__":
    source_directory = r"C:\KBData\Jenkins\SandBox\VT_Simulator\Measurement_Data\RSP"
    destination_directory = r"C:\KBData\Jenkins\Sandbox\VT_Simulator\Measurement_Data\can_log_files"

    remove_can_files(source_directory, destination_directory)
