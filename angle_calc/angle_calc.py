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
        sys.exit("Usage: in_dir (where dat files), out_dir")
    in_dir = sys.argv[1]
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        positions = []
        all_data, _f2v, params = td.read_dat(dat_file)
        ca = params["deformRate"]
        alpha = params["alpha"]
        vol_rat = params["vol_rat"]
        visc_rat = params["visc_rat"]
        for vert_data in all_data:
            f_data = [float(x) for x in vert_data[0:3]]
            positions.append(f_data)
        positions = np.array(positions)
        angles = calc_angle(positions)
        print("vol_rat: {0}, visc_rat: {1}, Ca: {2}, alpha: {3}, Angles: {4}".format(vol_rat, visc_rat, ca, alpha, angles))


def calc_angle(positions):
    """
    expecting numpy array of mesh points
    returns angles in degrees
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
    planar_angle = math.atan2(major_axis[1], major_axis[0]) * 180/math.pi
    kayak_angle = math.atan2(major_axis[2], major_axis[0]) * 180/math.pi
    return (planar_angle, kayak_angle)

if __name__ == "__main__":
    main();
