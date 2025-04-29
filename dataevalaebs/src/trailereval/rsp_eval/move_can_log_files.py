import os
import shutil


def move_folders(source_dir, destination_dir):
    try:
        subdirs = [subdir for subdir in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, subdir))]
        for subdir in subdirs:
            source_path = os.path.join(source_dir, subdir)
            destination_path = os.path.join(destination_dir, subdir)
            if os.path.exists(destination_path):
                files = os.listdir(source_path)
                for file in files:
                    meas_path = os.path.join(source_path, file)
                    destination_path = os.path.join(destination_dir, subdir)
                    shutil.move(meas_path, destination_path)
                    os.rmdir(source_path)
            else:
                shutil.move(source_path, destination_path)
    except:
        pass


if __name__ == "__main__":
    source_directory = r"C:\KBData\Jenkins\Sandbox\VT_Simulator\Measurement_Data\RSP"
    destination_directory = r"C:\KBData\Jenkins\Sandbox\VT_Simulator\Measurement_Data\can_log_files"

    move_folders(source_directory, destination_directory)
