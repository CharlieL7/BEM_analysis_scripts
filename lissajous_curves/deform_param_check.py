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


def main():
    in_dir = sys.argv[1]
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        print(csv_file)
        print(determine_regime(csv_file))


class Regime(Enum):
    HIGH_STRAIN = 1
    MEDIUM_STRAIN = 2
    LOW_STRAIN = 3


def determine_regime(file_name):
    """
    Determines which LAOE dynamical regime the simulation is in

    Parameters:
        file_name: string of csv file name
    Returns:
        None
    """
    D_list = []
    with open(file_name, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    D_arr = np.array(D_list)
    max_val = D_arr.max()
    min_val = D_arr.min()
    diff = math.fabs(max_val) - math.fabs(min_val)
    if diff < 1E-03:
        return Regime.HIGH_STRAIN
    elif min_val < 0:
        return Regime.MEDIUM_STRAIN
    elif min_val > 0:
        return Regime.LOW_STRAIN
    else:
        print("Regime determination error")


if __name__ == "__main__":
    main()
