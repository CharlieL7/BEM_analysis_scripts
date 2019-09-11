import csv
import sys
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

'''
Plot the x-axis and y-axis length of the vesicle vs time
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    
    file_num = 0
    length_x_list = []
    length_y_list = []
    time_list= []
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        x_length = np.amax(positions[:, 0]) - np.amin(positions[:, 0])
        y_length = np.amax(positions[:, 1]) - np.amin(positions[:, 1])
        length_x_list.append(x_length)
        length_y_list.append(y_length)
        time_list.append(params["time"])
        file_num += 1

    fig_x = plt.figure(figsize=(4.5, 4.5))
    fig_y = plt.figure(figsize=(4.5, 4.5))
    ax_x = fig_x.add_subplot(111)
    ax_y = fig_y.add_subplot(111)

    plot_len_time(ax_x, time_list, length_x_list, r"x-axis length (\frac{L}{a})")
    plot_len_time(ax_y, time_list, length_y_list, r"y-axis length (\frac{L}{a})")


def plot_len_time(ax, time_list, length_list, y_label):
    """
    Input the axes and the data for Lissajous curve
    """
    ax.plot(time_list, length_list, "-")
    ax.set_xlabel(r"time $\frac{t/}{\dot{\epsilon}}", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    plt.show()


if __name__ == "__main__":
    main()
