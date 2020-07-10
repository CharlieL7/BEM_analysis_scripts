"""
Plots the deformation parameter wrt. to strain (Ca_x).
Overlays the experimental and numerical data on one plot
"""
import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import argparse as argp

W_TYPE_LINES = [" W "]
De_TYPE_LINES = [" De "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Plots deformation parameter vs. time for experimental and numerical data")
    parser.add_argument("sim_file", help="simulation data file (csv)")
    parser.add_argument("exp_file", help="experimental datafile (tsv)")
    parser.add_argument("out_name", help="output file name (pdf)")
    parser.add_argument("-p", "--phase_lag", help="phase lag for experimental data")
    parser.add_argument("-s", "--skip_cycles", help="skip number of cycles for simulation data")
    args = parser.parse_args()
    if args.skip_cycles:
        sim_data = read_sim_data(args.sim_file, skipcycles=int(args.skip_cycles))
    else:
        sim_data = read_sim_data(args.sim_file, skipcycles=0)
    if args.phase_lag:
        exp_data = read_exp_data(args.exp_file, phase_lag=args.phase_lag)
    else:
        exp_data = read_exp_data(args.exp_file)

    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    plot_deform_ratios(ax, sim_data, line_color="darkmagenta")
    plot_deform_ratios(ax, exp_data, line_color="black")
    axins = inset_axes(ax, width=1.0, height=0.5)
    plot_sin_inset(axins)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    fig.savefig("{}.pdf".format(args.out_name), format="pdf")
    plt.close(fig)


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
                time_list.append(t)
                Ca_x = -Ca * np.sin(2 * np.pi * De * t)
                Ca_x_list.append(Ca_x)
                D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    Ca_x_arr = np.array(Ca_x_list)
    D_arr = np.array(D_list)
    time_arr = np.array(time_list)
    return {"time":time_arr, "Ca":Ca, "Ca_x":Ca_x_arr, "D":D_arr, "De":De,}


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
    phase_lag = 0.
    D_list = []
    Ca_x_list = []
    time_list = []
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
            else:
                is_header = False
                # need to move back a line for DictReader to get keys
                csv_file.seek(last_pos)
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            t = (row["time"] - phase_lag) / Ca
            time_list.append(t)
            Ca_x = -Ca * np.sin(2 * np.pi * De * t)
            Ca_x_list.append(Ca_x)
            D_list.append(row["D"])
    Ca_x_arr = np.array(Ca_x_list)
    D_arr = np.array(D_list)
    time_arr = np.array(time_list)
    return {"time":time_arr, "Ca":Ca, "Ca_x":Ca_x_arr, "D":D_arr, "De":De,}


def plot_deform_ratios(ax, data_map, **kwargs):
    """
    Plots the deformation parameter vs. Ca_x with color coded sections

    Parameters:
        ax: axes object to plot on
        data_map: a map with atleast the keys (time, D, De, Ca)
        [line_color]: color for the plot lines
    Returns:
        None
    """
    line_color = "black"
    if kwargs.get("line_color", False):
        line_color = kwargs["line_color"]
    time_arr = data_map["time"]
    D_arr = data_map["D"]
    Ca = data_map["Ca"]
    De = data_map["De"]
    p = 1. / De
    q_p = 1 / (4. * De)

    # breakup data into cycles and four sets
    Ca_x_lists = [[], [], [], []]
    D_lists = [[], [], [], []]
    cycle_num = time_arr[0] // p
    prev_cycle_num = cycle_num
    def plot_clear_data(Ca_x, D):
        ax.plot(Ca_x[0], D[0], "-", color=line_color)
        ax.plot(Ca_x[1], D[1], ".", color=line_color)
        ax.plot(Ca_x[2], D[2], ":", color=line_color)
        ax.plot(Ca_x[3], D[3], "x", color=line_color)
        for l in Ca_x:
            l.clear() # must be done this way to alter mutable
        for m in D:
            m.clear()
        nonlocal prev_cycle_num
        prev_cycle_num = cycle_num
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

    colr = "cornflowerblue"
    ax.plot(x_vals[0], y_vals[0], "-", color=colr)
    ax.plot(x_vals[1], y_vals[1], ".", color=colr)
    ax.plot(x_vals[2], y_vals[2], ":", color=colr)
    ax.plot(x_vals[3], y_vals[3], "x", color=colr)
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
