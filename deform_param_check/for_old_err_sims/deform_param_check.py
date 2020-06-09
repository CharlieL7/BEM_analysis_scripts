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
    high_strain_list = []
    med_strain_list = []
    low_strain_list = []
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        try:
            res = determine_regime(csv_file, skipcycles=cycle_skip)
            regime = res.pop("regime")
            if regime == Regime.HIGH_STRAIN:
                high_strain_list.append(res)
            elif regime == Regime.MEDIUM_STRAIN:
                med_strain_list.append(res)
            elif regime == Regime.LOW_STRAIN:
                low_strain_list.append(res)
        except IOError as err:
            print("IOError for csv file: {}".format(csv_file))
            print(err)

    fieldnames = ["De", "Ca", "max", "min",]
    with open("high_strain_list.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(high_strain_list)
    with open("med_strain_list.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(med_strain_list)
    with open("low_strain_list.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(low_strain_list)


class Regime(Enum):
    HIGH_STRAIN = 1
    MEDIUM_STRAIN = 2
    LOW_STRAIN = 3


def determine_regime(file_name, **kwargs):
    """
    Determines which LAOE dynamical regime the simulation is in.
    Handles the header variables and skips a number of initial cycles, default 6
    If not atleast 10 cycles returns -1

    Parameters:
        file_name: string of csv file name
        [skiprows]: optional kwarg to skip a number of rows
        [skipcycles]: optional kwargs to skip a number of cycles
    Returns:
        map of regime determination, simulation parameters, min and max D values
    """
    D_list = []
    time_list = []
    skipcycles = 6
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
            time_list.append(row["time"])
            if row["time"] > (skipcycles/W): # only add value if after certain number of cycles
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    D_arr = np.array(D_list)
    period = 1./W
    
    if time_list[-1] < 10*period:
        raise IOError("Cycles < 10: {} simulated, parameters: De={} Ca={}".format(time_list[-1] / period, Ca * W, Ca))

    try:
        max_val = D_arr.max()
        min_val = D_arr.min()
    except ValueError as e:
        print("skipcycles failed on {}".format(file_name))
        print(e)
    diff = math.fabs(max_val) - math.fabs(min_val)
    if diff < 1E-02 and np.sign(max_val) != np.sign(min_val):
        return {"regime": Regime.HIGH_STRAIN, "De":  W, "Ca": Ca, "max":max_val, "min":min_val}
    elif np.sign(max_val) != np.sign(min_val): # edge case of value being exactly 0 has np.sign() return 0
        return {"regime": Regime.MEDIUM_STRAIN, "De":  W, "Ca": Ca, "max":max_val, "min":min_val}
    elif np.sign(max_val) == np.sign(min_val):
        return {"regime": Regime.LOW_STRAIN, "De":  W, "Ca": Ca, "max":max_val, "min":min_val}
    else: # maybe unneeded
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
