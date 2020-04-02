"""
Adds header data from vesicle simulation data
that only has the simulation parameters in the
file name
"""
import glob
import sys
import os
import re

def main():
    in_dir = sys.argv[1]
    for csv_file in glob.glob(in_dir + "*.csv"):
        insert_header(csv_file)


def insert_header(csv_file):
    """
    Uses the filename to insert simulation parameters to the header of the file

    Parameters:
        csv_file: path to the csv file
    Returns:
        None
    """
    base = os.path.basename(csv_file)
    name_only = os.path.splitext(base)[0]
    vals = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", name_only)
    keys = ["vol_rat", "W", "Ca", "visc_rat"]
    params = dict(zip(keys, vals))
    with open(csv_file, 'r') as f:
        with open("newfile.txt", 'w') as f2:
            f2.write("# volRat = {}\n".format(params["vol_rat"]))
            f2.write("# viscRat = {}\n".format(params["visc_rat"]))
            f2.write("# Ca = {}\n".format(params["Ca"]))
            f2.write("# W = {}\n".format(params["W"]))
            f2.write(f.read())
    os.rename("newfile.txt", csv_file)


if __name__ == "__main__":
    main()
