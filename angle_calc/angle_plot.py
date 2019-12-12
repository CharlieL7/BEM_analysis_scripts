#!usr/bin/env python3
"""
Calculates the orientation angle for a folder of vesicles .dat files
"""
import sys
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

# for comparisons
MIN_FLT = -float("inf")
MAX_FLT = float("inf")


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: in_dir (where folders with dat files)")
    in_dir = sys.argv[1]
    for c_folder in sorted(glob.glob(in_dir + "*/")):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        times = []
        major_angles = []
        minor_angles = []
        for dat_file in sorted(glob.glob(c_folder+ "/*.dat")):
            positions = []
            all_data, _f2v, params = td.read_dat(dat_file)
            time = params["time"]
            for vert_data in all_data:
                f_data = [float(x) for x in vert_data[0:3]]
                positions.append(f_data)
            positions = np.array(positions)
            angles = calc_angle(positions)
            times.append(time)
            major_angles.append(angles[0])
            minor_angles.append(angles[1])
            ax.plot(times, major_angles)
            textstr = '\n'.join((
                r"$Ca={}$".format(params["deformRate"]),
                r"$\alpha={}$".format(params["alpha"]),
                r"$\lambda={}$".format(params["visc_rat"]),
                r"$\nu={}$".format(params["vol_rat"])))
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.set_xlabel(r"time $(\frac{t}{\dot{\gamma}})$")
            ax.set_ylabel("Orientation Angle$ (\degree)$")
            ax.text(0.42, 0.25, textstr, transform=ax.transAxes, fontsize=14, verticalalignment='top', bbox=props)
            plt.tight_layout(rect=[0., 0., 1., 1.])
            plt.savefig("angle_vol{0}_Ca{1}_alpha{2}_visc{3}.pdf".format(params["vol_rat"], params["deformRate"], params["alpha"], params["visc_rat"]), format="pdf")


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
