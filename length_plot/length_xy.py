import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
import tec_dat as td

'''
Plot the x-axis and y-axis length of the vesicle vs time
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    len_plot(in_dir, out_filename)


def len_plot(in_dir, out_filename):
    file_num = 0
    length_x_list = []
    length_y_list = []
    time_list = []
    for dat_file in sorted(glob.glob(in_dir + "/*.dat")):
        all_data, _f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        positions = np.array(positions)
        # note that this is simply largest x-distance
        x_length = np.amax(positions[:, 0]) - np.amin(positions[:, 0])
        y_length = np.amax(positions[:, 1]) - np.amin(positions[:, 1])
        length_x_list.append(x_length)
        length_y_list.append(y_length)
        time_list.append(params["time"])
        file_num += 1

    fig_x = plt.figure(figsize=(4.5, 4.5))
    ax_x = fig_x.add_subplot(111)
    plot_len_time(ax_x, time_list, length_x_list, r"x-axis length $(\frac{L}{a})$")
    fig_x.tight_layout(rect=[0, 0, 0.95, 1])
    plt.savefig("{}_x_len.pdf".format(out_filename), format="pdf")
    plt.close()

    fig_y = plt.figure(figsize=(4.5, 4.5))
    ax_y = fig_y.add_subplot(111)
    plot_len_time(ax_y, time_list, length_y_list, r"y-axis length $(\frac{L}{a})$")
    fig_y.tight_layout(rect=[0, 0, 0.95, 1])
    plt.savefig("{}_y_len.pdf".format(out_filename), format="pdf")
    plt.close()


def plot_len_time(ax, time_list, length_list, y_label):
    ax.plot(time_list, length_list, "-")
    ax.set_xlabel(r"time $\frac{t}{\dot{\epsilon}}$", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True)


if __name__ == "__main__":
    main()
