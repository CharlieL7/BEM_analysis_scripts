#! usr/bin/env python3
import glob
import sys
import shutil

"""
copies the last vesicle data file to somewhere
renames to sequential numbers
"""
def main():
    parent_folder = sys.argv[1]
    dest_folder = sys.argv[2]
    child_folders = sorted(glob.glob(parent_folder + "*/"))
    file_num = 0
    for c_folder in child_folders:
        file_list = glob.glob(c_folder + '/*.dat')
        file_list = sorted(file_list)
        latest_file = file_list[-1]
        print("latest_file = {0}".format(latest_file))
        shutil.copy(latest_file, "{0}{1:02d}.dat".format(dest_folder, file_num))
        file_num += 1

if __name__ == "__main__":
    main()
