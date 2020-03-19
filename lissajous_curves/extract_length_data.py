"""
extract the length data from a dictory full of .dat file
(tecplot data files in ascii format)
write the extracted data into a csv file
"""

import sys
import glob
import math
import csv
import numpy as np
import tec_dat as td

def main():
    in_dir = sys.argv[1]
    data, params = read_length_data(in_dir)
    write_length_data(data, params)


def read_length_data(in_dir):
    """
    reads in .dat files from

    Parameters:
        in_dir: directory of dat files
    Returns:
        length_data: list of maps that can be written out using
        csv.DictWriter
    """
    length_data = [] # list of maps to write
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, _f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        time = params["time"]
        Ca_x = -params["strain_rate"] * math.sin(2 * math.pi * params["W"] * params["time"])
        x_len, y_len = td.calc_xy_lengths(np.array(positions))
        major_len, minor_len = td.calc_major_minor_lengths(np.array(positions))
        tmp_map = {
            "time": time,
            "Ca_x": Ca_x,
            "x_len": x_len,
            "y_len": y_len,
            "major_len": major_len,
            "minor_len": minor_len
            }
        length_data.append(tmp_map)
    return (length_data, params)


def write_length_data(data, params):
    """
    writes a list of maps out

    Parameters:
        data: list of maps with the required keys
        params: simulation parameters
    Returns:
        None
    """
    out_name = "length_data_vol_{0:.3f}_W{1:.3f}_Ca{2:.3f}_visc{3:.3f}.csv".format(
        params["vol_rat"],
        params["W"],
        params["strain_rate"],
        params["visc_rat"]
    )

    with open(out_name, "w", newline='') as csvfile:
        fieldnames = ["time", "Ca_x", "x_len", "y_len", "major_len", "minor_len"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def ext_run(in_dir):
    """
    For running through an external python program
    """
    data, params = read_length_data(in_dir)
    write_length_data(data, params)


if __name__ == "__main__":
    main()
