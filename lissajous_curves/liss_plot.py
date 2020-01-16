import csv
import sys
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
import tec_dat as td

'''
Plot the Lissajous curves L vs Ca_x(t)
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    plot_liss(in_dir, out_filename)


def plot_liss(in_dir, out_filename):
    """
    in_dir: directory of data files
    out_filename: name for the output plot
    """

    Ca_x_list = []
    length_list = []
    for dat_file in sorted(glob.glob(in_dir + "/*.dat")):
        all_data, _f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        Ca_x = -params["deformRate"] * math.sin(2 * math.pi * params["De"] * params["time"])
        length = td.calc_length(np.array(positions))[0]
        Ca_x_list.append(Ca_x)
        length_list.append(length)

    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    ax.plot(Ca_x_list, length_list, "-")
    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=12)
    ax.set_ylabel(r"L/a (a = equivalent radius)", fontsize=12)
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    plt.savefig("{}.pdf".format(out_filename), format="pdf")
    plt.close()


if __name__ == "__main__":
    main()
