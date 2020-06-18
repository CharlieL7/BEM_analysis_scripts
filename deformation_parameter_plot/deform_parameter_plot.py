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
            fig, ax = plot_deform_cax_CC(data_map)
            add_textbox(ax,
                        r"W = {:.3f}".format(data_map["W"]) +
                        "\n"
                        r"Ca = {:.3f}".format(data_map["Ca"]) +
                        "\n"
                        r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                        "\n"
                        r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                        )
            fig.savefig("{}.pdf".format(name_only + "_D_cax"), format="pdf")
            plt.close(fig)
            fig, ax = plot_deform_time_CC(data_map)
            add_textbox(ax,
                        r"W = {:.3f}".format(data_map["W"]) +
                        "\n"
                        r"Ca = {:.3f}".format(data_map["Ca"]) +
                        "\n"
                        r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                        "\n"
                        r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                        )
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
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            all_times.append(row["time"])
            if row["time"] > (skipcycles/W): # only add value if after certain number of cycles
                time_list.append(row["time"])
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    period = 1./W

    if all_times[-1] < 10*period:
        raise IOError("Cycles < 10: {} simulated, parameters: De={} Ca={}".format(all_times[-1] / period, Ca * W, Ca))

    data = {
        "time": np.array(time_list),
        "D": np.array(D_list),
        "W": W,
        "Ca": Ca,
        "visc_rat": visc_rat,
        "vol_rat": vol_rat,
    }
    return data


def plot_deform_cax_CC(data_map):
    """
    Plots the deformation parameter vs. Ca_x with color coded sections

    Parameters:
        data_map: a map with the keys (time, D, W, Ca, visc_rat, vol_rat)
    Returns:
        fig: the figure created
        ax: the axes object created
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    time_arr = data_map["time"]
    D_arr = data_map["D"]
    Ca = data_map["Ca"]
    W = data_map["W"]
    p = 1. / W
    q_p = 1 / (4. * W)

    # breakup data into cycles and four sets
    Ca_x_lists = [[], [], [], []]
    D_lists = [[], [], [], []]
    cycle_num = time_arr[0] // p
    prev_cycle_num = cycle_num
    for i in range(time_arr.size):
        time = time_arr[i]
        cycle_num = time // p
        mod_time = time % p
        Ca_x = -Ca * math.sin(2 * math.pi * W * time)
        D = D_arr[i]

        if cycle_num != prev_cycle_num:
            # plot lines and empty data lists
            ax.plot(Ca_x_lists[0], D_lists[0], "k-")
            ax.plot(Ca_x_lists[1], D_lists[1], "b--")
            ax.plot(Ca_x_lists[2], D_lists[2], "g-.")
            ax.plot(Ca_x_lists[3], D_lists[3], "r:")
            Ca_x_lists = [[], [], [], []]
            D_lists = [[], [], [], []]
            prev_cycle_num = cycle_num

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

    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    return fig, ax


def plot_deform_time_CC(data_map):
    """
    Plots the deformation parameter vs. time with color coded sections

    Parameters:
        data_map: a map with the keys (time, D, W, Ca, visc_rat, vol_rat)
    Returns:
        fig: the figure created
        ax: the axes object created
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    time_arr = data_map["time"]
    D_arr = data_map["D"]
    Ca = data_map["Ca"]
    W = data_map["W"]
    p = 1. / W
    q_p = 1 / (4. * W)

    # breakup data into cycles and four sets
    time_lists = [[], [], [], []]
    D_lists = [[], [], [], []]
    cycle_num = time_arr[0] // p
    prev_cycle_num = cycle_num
    for i in range(time_arr.size):
        time = time_arr[i]
        cycle_num = time // p
        mod_time = time % p
        D = D_arr[i]

        if cycle_num != prev_cycle_num:
            # plot lines and empty data lists
            ax.plot(time_lists[0], D_lists[0], "k-")
            ax.plot(time_lists[1], D_lists[1], "b--")
            ax.plot(time_lists[2], D_lists[2], "g-.")
            ax.plot(time_lists[3], D_lists[3], "r:")
            time_lists = [[], [], [], []]
            D_lists = [[], [], [], []]
            prev_cycle_num = cycle_num

        if mod_time < q_p:
            time_lists[0].append(time)
            D_lists[0].append(D)
        elif mod_time < 2*q_p:
            time_lists[1].append(time)
            D_lists[1].append(D)
        elif mod_time < 3*q_p:
            time_lists[2].append(time)
            D_lists[2].append(D)
        else:
            time_lists[3].append(time)
            D_lists[3].append(D)

    ax.set_xlabel(r"$time (\frac{t \kappa}{\mu{out} a^3})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    return fig, ax


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


if __name__ == "__main__":
    main()
