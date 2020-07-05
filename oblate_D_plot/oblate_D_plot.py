"""
Plots the deformation parameter wrt. strain rate and time for just simulation data
This version uses color coding of different sections of the curve
Note ths version also uses the W non-dimensionalization
"""
import sys
import csv
import os
import glob
import math
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.pyplot as plt

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    """
    works on a directory of csv files with length data
    with the ending "/"
    example: "/home/user/tmp/"
    """
    in_dir = sys.argv[1]
    skipcycles = int(sys.argv[2])
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        base = os.path.basename(csv_file)
        name_only = os.path.splitext(base)[0]
        try:
            data_map = read_length_data(csv_file, skipcycles=skipcycles)
            fig = plt.figure(figsize=(4.5, 4.5))
            ax = fig.add_subplot(111)
            plot_deform_cax_CC(ax, data_map)
            add_textbox(ax,
                        r"De = {:.3f}".format(data_map["De"]) +
                        "\n"
                        r"Ca = {:.3f}".format(data_map["Ca"]) +
                        "\n"
                        r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                        "\n"
                        r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                        )
            axins = inset_axes(ax, width=1.0, height=0.5)
            plot_sin_inset(axins)
            fig.tight_layout(rect=[0, 0, 0.95, 1])
            fig.savefig("{}.pdf".format(name_only + "_D_cax"), format="pdf")
            plt.close(fig)

            fig = plt.figure(figsize=(4.5, 4.5))
            ax = fig.add_subplot(111)
            plot_deform_time(ax, data_map)
            add_textbox(ax,
                        r"De = {:.3f}".format(data_map["De"]) +
                        "\n"
                        r"Ca = {:.3f}".format(data_map["Ca"]) +
                        "\n"
                        r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                        "\n"
                        r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                        )
            fig.tight_layout(rect=[0, 0, 0.95, 1])
            fig.savefig("{}.pdf".format(name_only + "_D_time"), format="pdf")
            plt.close(fig)
        except IOError as err:
            print("IOError for csv file: {}".format(csv_file))
            print(err)


def read_length_data(in_csv, **kwargs):
    """
    Reads the simulation data from file

    Parameters:
        in_csv: csv file to read
        [skipcycles]: for skipping an initial number of flow cycles
            assumes times start at 0
    Returns:
        data: times, D, and parameters as map
    """
    D_list = []
    all_times = []
    time_list = []
    skipcycles = 0
    if kwargs.get("skipcycles", False):
        skipcycles = kwargs["skipcycles"]
    with open(in_csv, newline='') as csv_file:
        is_header = True
        while is_header:
            last_pos = csv_file.tell()
            tmp_line = csv_file.readline()
            if tmp_line.find('#') == 0: # if first character is #
                eq_pos = tmp_line.find('=')
                if eq_pos != -1:
                    if check_in_list(tmp_line, W_TYPE_LINES):
                        W = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, CA_TYPE_LINES):
                        Ca = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, VISC_RAT_TYPE_LINES):
                        visc_rat = float(tmp_line[eq_pos+1:])
                    elif check_in_list(tmp_line, VOL_RAT_TYPE_LINES):
                        vol_rat = float(tmp_line[eq_pos+1:])
            else:
                is_header = False
                # need to move back a line for DictReader to get keys
                csv_file.seek(last_pos)
        reader = csv.DictReader(csv_file)
        De = Ca * W
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            t = row["time"] / Ca
            all_times.append(t)
            if row["time"] > (skipcycles/De): # only add value if after certain number of cycles
                time_list.append(t)
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    period = 1./De

    if all_times[-1] < 10*period:
        raise IOError("Cycles < 10: {} simulated, parameters: De={} Ca={}".format(all_times[-1] / period, De, Ca))

    data = {
        "time": np.array(time_list),
        "D": np.array(D_list),
        "W": W,
        "De": De,
        "Ca": Ca,
        "visc_rat": visc_rat,
        "vol_rat": vol_rat,
    }
    return data


def plot_deform_cax_CC(ax, data_map):
    """
    Plots the deformation parameter vs. Ca_x with color coded sections

    Parameters:
        ax: axes object to plot on
        data_map: a map with the keys (time, D, W, Ca, visc_rat, vol_rat)
    Returns:
        None
    """
    time_arr = data_map["time"]
    D_arr = data_map["D"]
    Ca = data_map["Ca"]
    De = data_map["De"]
    p = 1. /De
    q_p = 1 / (4. * De)

    # breakup data into cycles and four sets
    Ca_x_lists = [[], [], [], []]
    D_lists = [[], [], [], []]
    cycle_num = time_arr[0] // p
    prev_cycle_num = cycle_num

    def plot_clear_data(Ca_x, D):
        ax.plot(Ca_x[0], D[0], "k-")
        ax.plot(Ca_x[1], D[1], "b--")
        ax.plot(Ca_x[2], D[2], "g:")
        ax.plot(Ca_x[3], D[3], "r-.")
        for l in Ca_x:
            l.clear() # must be done this way to alter mutable
        for m in D:
            m.clear()
        nonlocal prev_cycle_num
        prev_cycle_num = cycle_num

    Ca_x_0 = -Ca * math.sin(2 * math.pi * De * time_arr[0])
    ax.plot(Ca_x_0, D_arr[0], "ko", mfc="None") # plot start point
    for i in range(time_arr.size):
        time = time_arr[i]
        cycle_num = time // p
        mod_time = time % p
        Ca_x = -Ca * math.sin(2 * math.pi * De * time)
        D = D_arr[i]

        if cycle_num != prev_cycle_num:
            plot_clear_data(Ca_x_lists, D_lists)

        if mod_time < q_p:
            Ca_x_lists[0].append(Ca_x)
            D_lists[0].append(D)
        elif mod_time < 2*q_p:
            Ca_x_lists[1].append(Ca_x)
            D_lists[1].append(D)
        elif mod_time < 3*q_p:
            Ca_x_lists[2].append(Ca_x)
            D_lists[2].append(D)
        else:
            Ca_x_lists[3].append(Ca_x)
            D_lists[3].append(D)
    plot_clear_data(Ca_x_lists, D_lists)# once more to plot last of data

    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)


def plot_deform_time(ax, data_map):
    """
    Plots the deformation parameter vs. time and the strain rate curve

    Parameters:
        ax: axes object to plot on
        data_map: a map with atleast the keys (time, D, De)
    Returns:
        None
    """
    time_arr = data_map["time"]
    D_arr = data_map["D"]
    De = data_map["De"]
    min_time = np.amin(time_arr)
    max_time = np.amax(time_arr)
    sin_times = np.linspace(min_time, max_time, num=500)
    ax.plot(sin_times,
            np.sin(-2. * np.pi * sin_times * De),
            "k-",
            label=r"$\dot{\epsilon} / Ca$"
           )
    ax.plot(time_arr, D_arr, "--", color="orange", label="sim.")
    ax.legend(loc="upper left")
    ax.set_xlabel(r"$time (\frac{t \kappa}{\mu a^3})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    #ax.set_ylim([-1, 1])
    ax.grid(True)


def add_textbox(ax, textstr):
    """
    Adds an informative textbox to to figure

    Parameters:
        ax: the axes object
        textstr: the string in the textbox
    Returns:
        None
    """
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.70, 0.20, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)


def check_in_list(in_string, string_list):
    """
    checks if a string has one of the strings in the string_list

    Parameters:
        in_string : string to test
        string_list : strings to test for
    Returns:
        boolean
    """
    for tmp in string_list:
        if in_string.find(tmp) != -1:
            return True
    return False


def plot_sin_inset(ax):
    """
    plots the sinusoidal strain rate legend as an inset

    Parameters:
        ax: the inset axis to plot on
    Returns:
        None
    """
    x_vals = []
    x_vals.append(np.linspace(0, 0.5*np.pi))
    x_vals.append(np.linspace(0.5*np.pi, 1.0*np.pi))
    x_vals.append(np.linspace(1.0*np.pi, 1.5*np.pi))
    x_vals.append(np.linspace(1.5*np.pi, 2.0*np.pi))

    y_vals = []
    y_vals.append(-np.sin(x_vals[0]))
    y_vals.append(-np.sin(x_vals[1]))
    y_vals.append(-np.sin(x_vals[2]))
    y_vals.append(-np.sin(x_vals[3]))

    ax.plot(x_vals[0], y_vals[0], "k-")
    ax.plot(x_vals[1], y_vals[1], "b--")
    ax.plot(x_vals[2], y_vals[2], "g:")
    ax.plot(x_vals[3], y_vals[3], "r-.")
    ax.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom=False,      # ticks along the bottom edge are off
        top=False,         # ticks along the top edge are off
        left=False,
        labelbottom=False, # labels along the bottom edge are off
        labelleft=False
    )
    ax.set_ylabel(r"$\frac{\dot{\epsilon}}{Ca}$", rotation=0)


if __name__ == "__main__":
    main()
