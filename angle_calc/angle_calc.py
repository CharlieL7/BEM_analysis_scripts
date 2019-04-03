#!usr/bin/env python3
"""
Calculates the orientation angle for a folder of vesicles .dat files
"""
import sys
import glob
import math
import numpy as np
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

# for comparisons
MIN_FLT = -float("inf")
MAX_FLT = float("inf")


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: in_dir (where dat files to rotate), out_dir")
    in_dir = sys.argv[1]
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        positions = []
        angles = []
        times = []
        all_data, _f2v, params = td.read_dat(dat_file)
        times.append(params["time"])
        for vert_data in all_data:
            f_data = [float(x) for x in vert_data[0:3]]
            positions.append(f_data)
        positions = np.array(positions)
        angles.append(calc_angle(positions))
        for i in range(len(angles)):
            print("Time: {0}, Angle: {1}".format(times[i], angles[i]))


def calc_angle(positions):
    """
    expecting numpy array of mesh points
    """
    (_I, _eig_vals, eig_vecs) = td.calc_moment_inertia_tensor(positions)

    # need to find the major axis of the vesicle (longest length)
    # project to each eigenvector and find one with the largest difference in magnitude
    max_span = 0
    major_axis_ind = None
    for i, eig_vec in enumerate(eig_vecs):
        min_val = MAX_FLT
        max_val = MIN_FLT
        for point in positions:
            proj = np.dot(eig_vec, point)
            if proj < min_val:
                min_val = proj
            elif proj > max_val:
                max_val = proj
        span = max_val - min_val
        if span > max_span:
            max_span = span
            major_axis_ind = i

    major_axis = eig_vecs[major_axis_ind]
    planar_angle = math.atan2(major_axis[1], major_axis[0])
    kayak_angle = math.atan2(major_axis[2], major_axis[0])
    return (planar_angle, kayak_angle)

if __name__ == "__main__":
    main();
