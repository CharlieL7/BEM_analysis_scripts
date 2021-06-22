"""
extract the length data from a dictory full of .dat file
(tecplot data files in ascii format)
write the extracted data into a csv file
"""

import glob
import math
import csv
import os
import argparse as argp
import numpy as np
import tec_dat as td

def main():
    parser = argp.ArgumentParser(description="extracts length data from simulation data")
    parser.add_argument("in_dir", help="folder of mesh data files")
    parser.add_argument("out_dir", help="folder to output into")
    parser.add_argument("mod", help="modulus for skipping files")
    args = parser.parse_args()
    data, params = read_length_data(args.in_dir, int(args.mod))
    write_length_data(args.in_dir, args.out_dir, data, params)


def read_length_data(in_dir, mod):
    """
    reads in .dat files from

    Parameters:
        in_dir: directory of dat files
        mod: modulus for skipping files
    Returns:
        length_data: list of maps that can be written out using
        csv.DictWriter
    """
    length_data = [] # list of maps to write
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        fn = os.path.basename(dat_file)
        num = ''.join(i for i in fn if i.isdigit())
        num = int(num)
        if num % mod == 0:
            all_data, _f2v, params = td.read_dat(dat_file)
            positions = []
            for vert_data in all_data:
                pos_data = [float(x) for x in vert_data[0:3]]
                positions.append(pos_data)
            if np.isnan(positions).any():
                print("Detected nan value for file: {}".format(dat_file))
            else:
                time = params["time"]
                Ca = params["strain_rate"] / params["EB"]
                Ca_x = Ca * math.sin(2 * math.pi * params["W"] * params["time"])
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


def write_length_data(in_dir, out_dir, data, params):
    """
    writes a list of maps out

    Parameters:
        data: list of maps with the required keys
        params: simulation parameters
    Returns:
        None
    """
    #out_name = "{0}/length_data_vol_{1:.3f}_W{2:.3f}_Ca{3:.3f}_visc{4:.3f}.csv".format(
    #    out_dir,
    #    params["vol_rat"],
    #    params["W"],
    #    params["Ca"],
    #    params["visc_rat"]
    #)
    out_name = "{0}/{1}.csv".format(
        out_dir,
        os.path.basename(os.path.dirname(in_dir)),
    )

    with open(out_name, "w", newline='') as csvfile:
        # write the simulation parameters
        csvfile.write("# volRat = {}\n".format(params["vol_rat"]))
        csvfile.write("# viscRat = {}\n".format(params["visc_rat"]))
        csvfile.write("# Ca = {}\n".format(params["Ca"]))
        csvfile.write("# W = {}\n".format(params["W"]))
        fieldnames = ["time", "Ca_x", "x_len", "y_len", "major_len", "minor_len"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def ext_run(in_dir, out_dir, mod):
    """
    For running through an external python program

    Parameters:
        in_dir: the input directory
        mod: modulus for file skipping
    Returns:
        None
    """
    data, params = read_length_data(in_dir, mod)
    write_length_data(in_dir, out_dir, data, params)


if __name__ == "__main__":
    main()
