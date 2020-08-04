"""
Plots the deformation parameter wrt. to time (t/epsilon).
Overlays the experimental and numerical data on one plot
"""
import csv
import math
import argparse as argp
import numpy as np
import matplotlib.pyplot as plt

W_TYPE_LINES = [" W "]
DE_TYPE_LINES = [" De "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Plots deformation parameter vs. time for experimental and numerical data")
    parser.add_argument("sim_file", help="simulation data file (csv)")
    parser.add_argument("exp_file", help="experimental datafile (tsv)")
    parser.add_argument("out_name", help="output file name (pdf)")
    parser.add_argument("-p", "--phase_lag", help="phase lag for experimental data")
    args = parser.parse_args()
    sim_data = read_sim_data(args.sim_file)
    if args.phase_lag:
        exp_data = read_exp_data(args.exp_file, phase_lag=args.phase_lag)
    else:
        exp_data = read_exp_data(args.exp_file)
    plot_deform_ratios(exp_data, sim_data, args.out_name)

def read_sim_data(file_name):
    """
    Reads the simulation data from file
    Note that the simulation data file has a different structure from
    the experimental data

    Parameters:
        file_name: name of the file
    Returns:
        numpy array of the time data
        numpy array of the deformation parameter data
        W as a double
    """
    D_list = []
    time_list = []
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
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            time_list.append(row["time"])
            D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    time_arr = np.array(time_list)
    time_arr -= 5 / W # translating by 5 periods
    D_arr = np.array(D_list)
    return (time_arr, D_arr, W)


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
        W as a double
    """
    skiprows = 0
    phase_lag = 0.
    D_list = []
    time_list = []
    if "skiprows" in kwargs:
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
                    if check_in_list(tmp_line, DE_TYPE_LINES):
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
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            time_list.append((row["time"] - phase_lag)) # convert to other non-dim
            D_list.append(row["D"])
    time_arr = np.array(time_list)
    D_arr = np.array(D_list)
    W = De / Ca
    return (time_arr, D_arr, W)


def plot_deform_ratios(exp_data, sim_data, out_name):
    """
    Plots the deformation parameter comparison
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    min_time = np.amin(sim_data[0])
    max_time = np.amax(sim_data[0])
    sin_times = np.linspace(min_time, max_time, num=500)
    W = sim_data[2]
    ax.plot(exp_data[0], exp_data[1], "k.-", label="exp.")
    ax.plot(sim_data[0], sim_data[1], "m-", label="sim.")
    ax.plot(sin_times,
            np.sin(2. * np.pi * sin_times * W),
            "--",
            label=r"$\dot{\epsilon} / Ca_0$"
           )
    ax.legend(loc="lower right")
    ax.set_xlabel(r"time $(t \dot{\epsilon})$", fontsize=14)
    ax.set_ylabel(r"D $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    #ax.set_ylim([-1, 1])
    ax.set_xlim([0, 50])
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
