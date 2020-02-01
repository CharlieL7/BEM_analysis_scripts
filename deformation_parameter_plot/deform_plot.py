"""
Makes the deformation parameter, defined as (x axis length - y axis length) / (x axis length + y axis length)
plots from raw simulation data.
DOES NOT ROTATE MESH.
This will only really make sense for extensional flows as the vesicle might
have some orientation outside of purely x or y axis
"""
import sys
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
import tec_dat as td


def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    plot_deform_ratio(in_dir, out_filename)


def plot_deform_ratio(in_dir, out_filename):
    """
    in_dir: directory of data files
    out_filename: name for the output plot
    """

    Ca_x_list = []
    deform_ratio_list = []
    for dat_file in sorted(glob.glob(in_dir + "/*.dat")):
        all_data, _f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        Ca_x = -params["deformRate"] * math.sin(2 * math.pi * params["De"] * params["time"])
        length = calc_deform_ratio(np.array(positions))
        Ca_x_list.append(Ca_x)
        deform_ratio_list.append(length)

    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    ax.plot(Ca_x_list, deform_ratio_list, "-")
    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=14)
    ax.set_ylabel(r"Deformation parameter $\left( \frac{a - b}{a + b} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    plt.savefig("{}.pdf".format(out_filename), format="pdf")
    plt.close()


def calc_deform_ratio(x):
    """
    Calculates the deformation parameter defined as
    (x_len - y_len) / (x_len + y_len)
    such that the parameter will be negative when major
    axis is on y-axis for planar extensional flows

    Parameters:
        x : all the nodal positions in a (3, N) ndarray
    """
    x_len = np.amax(x[:, 0]) - np.amin(x[:, 0])
    y_len = np.amax(x[:, 1]) - np.amin(x[:, 1])
    deform_ratio = (x_len - y_len) / (x_len + y_len)
    return deform_ratio

if __name__ == "__main__":
    main()
