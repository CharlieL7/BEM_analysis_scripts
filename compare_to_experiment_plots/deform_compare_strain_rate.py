"""
Plots the deformation parameter wrt. to strain (Ca_x).
Overlays the experimental and numerical data on one plot
"""
import csv
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

W_TYPE_LINES = [" W "]
De_TYPE_LINES = [" De "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    sim_file = sys.argv[1]
    exp_file = sys.argv[2]
    out_name = sys.argv[3]
    sim_data = read_sim_data(sim_file, skipcycles=5)
    exp_data = read_exp_data(exp_file, phase_lag=6.0)
    plot_deform_ratios(exp_data, sim_data, out_name)


def read_sim_data(file_name, **kwargs):
    """
    Reads the simulation data from file
    Note that the simulation data file has a different structure from
    the experimental data

    Parameters:
        file_name: name of the file
        [skipcycles]: skip number of cycles from begin
    Returns:
        numpy array of the time data
        numpy array of the deformation parameter data
    """
    skipcycles = 0
    if kwargs.get("skipcycles", False):
        skipcycles = kwargs["skipcycles"]
    Ca_x_list = []
    D_list = []
    with open(file_name, newline='') as csv_file:
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
            if t > skipcycles/De:
                Ca_x = -Ca * np.sin(2 * np.pi * De * t)
                Ca_x_list.append(Ca_x)
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    Ca_x_arr = np.array(Ca_x_list)
    D_arr = np.array(D_list)
    return (Ca_x_arr, D_arr)


def read_exp_data(file_name, **kwargs):
    """
    Reads the experimental data from file

    Parameters:
        file_name: name of the file
        [skiprows]: to skip a number of rows at top of file
        [phase_lag]: to add a phase lag to the time data
    Returns:
        numpy array of the time data
        numpy array of the deformation parameter data
    """
    skiprows = 0
    Ca_x_list = []
    D_list = []
    if kwargs.get("skiprows", False):
        skiprows = int(kwargs["skiprows"])
    if "phase_lag" in kwargs:
        phase_lag = float(kwargs["phase_lag"])
    with open(file_name, newline='') as csv_file:
        a = 0
        while a < skiprows:
            csv_file.readline()
            a += 1
        is_header = True
        while is_header:
            last_pos = csv_file.tell()
            tmp_line = csv_file.readline()
            if tmp_line.find('#') == 0: # if first character is #
                eq_pos = tmp_line.find('=')
                if eq_pos != -1:
                    if check_in_list(tmp_line, De_TYPE_LINES):
                        De = float(tmp_line[eq_pos+1:])
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
        reader = csv.DictReader(csv_file, delimiter="\t")
        print(De)
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            t = (row["time"] - phase_lag) / Ca
            Ca_x = -Ca * np.sin(2 * np.pi * De * t)
            Ca_x_list.append(Ca_x)
            D_list.append(row["D"])
    Ca_x_arr = np.array(Ca_x_list)
    D_arr = np.array(D_list)
    return (Ca_x_arr, D_arr)


def plot_deform_ratios(exp_data, sim_data, out_name):
    """
    Plots the deformation parameter comparison
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    ax.plot(exp_data[0], exp_data[1], "-")
    ax.plot(sim_data[0], sim_data[1], "--")
    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    fig.savefig("{}".format(out_name), format="pdf")
    plt.close()


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
