import csv
import sys
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

'''
Plot the Lissajous curves L vs Ca_x(t)
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    
    file_num = 0
    Ca_x_list = []
    length_list = []
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        Ca_x = -params["deformRate"] * math.sin(2 * math.pi * params["deformRate"] * params["time"])
        length = td.calc_length(np.array(positions))[0]
        Ca_x_list.append(Ca_x)
        length_list.append(length)
        file_num += 1

    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    plot_liss(ax, Ca_x_list, length_list)

    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=12)
    ax.set_ylabel(r"L/a (a = equivalent radius)", fontsize=12)
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    plt.show()

def plot_liss(ax, Ca_x_list, length_list):
    """
    Input the axes and the data for Lissajous curve
    Arguements:
    ax : the matplotlib axes to plot on
    Ca_x_list : the x direction capillary numbers
    length_list : the lengths 
    """
    ax.plot(Ca_x_list, length_list, "-")


if __name__ == "__main__":
    main()
