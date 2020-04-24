"""
Checks the minimum and maximum deformation parameter value
to figure out which dynamical regime the simulation is in
"""
import csv
import math
import glob
import sys
from enum import Enum
import numpy as np

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    in_dir = sys.argv[1]
    cycle_skip = sys.argv[2]
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        print("=================================")
        print(csv_file)
        print(determine_regime(csv_file, skipcycles=cycle_skip))
        print()


class Regime(Enum):
    HIGH_STRAIN = 1
    MEDIUM_STRAIN = 2
    LOW_STRAIN = 3


def determine_regime(file_name, **kwargs):
    """
    Determines which LAOE dynamical regime the simulation is in.
    Handles the header variables and skips a number of initial cycles, default 5

    Parameters:
        file_name: string of csv file name
        [skiprows]: optional kwarg to skip a number of rows
        [skipcycles]: optional kwargs to skip a number of cycles
    Returns:
        Regime enum
    """
    D_list = []
    skipcycles = 0
    if kwargs.get("skipcycles", False):
        skipcycles = int(kwargs["skipcycles"])
    with open(file_name, newline='') as csv_file:
        is_header = True
        while is_header:
            last_pos = csv_file.tell()
            tmp_line = csv_file.readline()
            if tmp_line.find('#') == 0: # if first character is #
                eq_pos = tmp_line.find('=')
                if eq_pos != -1:
                    if check_in_list(tmp_line, W_TYPE_LINES):
                        W = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, CA_TYPE_LINES):
                        Ca = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, VISC_RAT_TYPE_LINES):
                        visc_rat = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, VOL_RAT_TYPE_LINES):
                        vol_rat = float(tmp_line[eq_pos+1:])
            else:
                is_header = False
                # need to move back a line for DictReader to get keys
                csv_file.seek(last_pos)
        reader = csv.DictReader(csv_file)
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            if row["time"] > (skipcycles/W): # only add value if after certain number of cycles
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    print("De: {}".format(Ca * W))
    print("Ca: {}".format(Ca))
    print("viscosity ratio: {}".format(visc_rat))
    print("reduced volume: {}".format(vol_rat))
    D_arr = np.array(D_list)
    max_val = D_arr.max()
    min_val = D_arr.min()
    diff = math.fabs(max_val) - math.fabs(min_val)
    print("Maximum value: {}".format(max_val))
    print("Mimumum value: {}".format(min_val))
    if diff < 1E-03:
        return Regime.HIGH_STRAIN
    elif min_val < 0:
        return Regime.MEDIUM_STRAIN
    elif min_val > 0:
        return Regime.LOW_STRAIN
    else:
        print("Regime determination error")


def check_in_list(in_string, string_list):
    """
    checks if a string has one of the strings in the string_list

    Parameters:
        in_string : string to test
        string_list : strings to test for
    Returns:
        boolean
    """
    for tmp in string_list:
        if in_string.find(tmp) != -1:
            return True
    return False


if __name__ == "__main__":
    main()
