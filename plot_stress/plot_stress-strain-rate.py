"""
short script to make Lissajous type stress vs. strain rate diagrams
for vesicle in LAOE simulations
"""
import glob
import os
import csv
import math
import argparse as argp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Makes a Lissajous-type curve for the normal stress differences")
    parser.add_argument("in_dir", help="input directory of stresslet data files")
    args = parser.parse_args()
    for csv_file in sorted(glob.glob(args.in_dir + "*.csv")):
        base = os.path.basename(csv_file)
        name_only = os.path.splitext(base)[0]
        data_map = read_stress_data(csv_file)
        fig = plt.figure(figsize=(3.5, 3.5))
        ax = fig.add_subplot()
        plot_stress_cax(ax, data_map)
        ax.set_xlabel(r"$Ca_x$")
        ax.set_ylabel(r"normal stress difference ($\frac{\tilde{S_{ij}}^P}{\dot{\epsilon} \mu_{\mathit{out}} V_p}$)")
        ax.grid(True)
        add_textbox(ax,
            r"De = {:.3f}".format(data_map["De"]) +
            "\n"
            r"Ca = {:.3f}".format(data_map["Ca"]) +
            "\n"
            r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
            "\n"
            r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
        )
        ax.set_ylim([-15, 15])
        ax.legend(loc="upper left")
        axins = inset_axes(ax, width=1.0, height=0.5)
        plot_sin_inset(axins)
        fig.tight_layout(rect=[0, 0, 0.95, 1])
        fig.savefig("{}_Cax_plot.pdf".format(name_only), format="pdf")
        plt.close(fig)


def read_stress_data(in_csv):
    """
    Reads in the stress data from a csv file
    also handles the simulation parameters

    Parameters:
        in_csv: csv file to read
    Returns:
        data: times, stresses, and parameters as map
    """
    stress_data = []
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
            row = dict([a, float(x)] for a, x in row.items())
            stress_data.append(row)
    time = []
    S_1 = []
    S_2 = []
    De = Ca * W
    for row in stress_data:
        t = row["time"] / Ca
        if  t > 3/De:
            time.append(t)
            S_1.append(row["S_xx"] - row["S_yy"])
            S_2.append(row["S_yy"] - row["S_zz"])

    S_1 = np.array(S_1)
    S_2 = np.array(S_2)
    data = {
        "time": np.array(time),
        "S_1": np.array(S_1),
        "S_2": np.array(S_2),
        "W": W,
        "Ca": Ca,
        "De": Ca * W,
        "visc_rat": visc_rat,
        "vol_rat": vol_rat,
    }
    return data


def plot_stress_cax(ax, data_map):
    """
    Plots the stress vs Ca_x with color coded sections

    Parameters:
        ax: axes object to plot on
        data_map: data to plot
    Returns:
        None
    """
    time_arr = data_map["time"]
    De = data_map["De"]
    Ca = data_map["Ca"]
    N1_arr = data_map["S_1"]
    N2_arr = data_map["S_2"]
    p = 1. /De
    q_p = 1 / (4. * De)

    # breakup data into cycles and four sets
    Ca_x_lists = [[], [], [], []]
    N1_lists = [[], [], [], []]
    N2_lists = [[], [], [], []]
    try:
        cycle_num = time_arr[0] // p
    except IndexError:
        print("simulation Ca = {}, De = {} does not have enough times".format(Ca, De))
        return None
    prev_cycle_num = cycle_num

    for i in range(time_arr.size):
        time = time_arr[i]
        cycle_num = time // p
        mod_time = time % p
        Ca_x = -Ca * math.sin(2 * math.pi * De * time)
        N1 = N1_arr[i]
        N2 = N2_arr[i]

        if cycle_num != prev_cycle_num:
            ax.plot(Ca_x_lists[0], N1_lists[0], "k-")
            ax.plot(Ca_x_lists[1], N1_lists[1], "k--")
            ax.plot(Ca_x_lists[2], N1_lists[2], "k:")
            ax.plot(Ca_x_lists[3], N1_lists[3], "k-.")

            ax.plot(Ca_x_lists[0], N2_lists[0], "b-")
            ax.plot(Ca_x_lists[1], N2_lists[1], "b--")
            ax.plot(Ca_x_lists[2], N2_lists[2], "b:")
            ax.plot(Ca_x_lists[3], N2_lists[3], "b-.")
            prev_cycle_num = cycle_num
            Ca_x_lists = [[], [], [], []]
            N1_lists = [[], [], [], []]
            N2_lists = [[], [], [], []]

        if mod_time < q_p:
            Ca_x_lists[0].append(Ca_x)
            N1_lists[0].append(N1)
            N2_lists[0].append(N2)
        elif mod_time < 2*q_p:
            Ca_x_lists[1].append(Ca_x)
            N1_lists[1].append(N1)
            N2_lists[1].append(N2)
        elif mod_time < 3*q_p:
            Ca_x_lists[2].append(Ca_x)
            N1_lists[2].append(N1)
            N2_lists[2].append(N2)
        else:
            Ca_x_lists[3].append(Ca_x)
            N1_lists[3].append(N1)
            N2_lists[3].append(N2)

    # once more
    ax.plot(Ca_x_lists[0], N1_lists[0], "k-", label=r"$N_1$")
    ax.plot(Ca_x_lists[1], N1_lists[1], "k--")
    ax.plot(Ca_x_lists[2], N1_lists[2], "k:")
    ax.plot(Ca_x_lists[3], N1_lists[3], "k-.")

    ax.plot(Ca_x_lists[0], N2_lists[0], "b-", label=r"$N_2$")
    ax.plot(Ca_x_lists[1], N2_lists[1], "b--")
    ax.plot(Ca_x_lists[2], N2_lists[2], "b:")
    ax.plot(Ca_x_lists[3], N2_lists[3], "b-.")


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
    ax.text(0.63, 0.23, textstr, transform=ax.transAxes, verticalalignment='top', bbox=props)


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
    ax.plot(x_vals[1], y_vals[1], "k--")
    ax.plot(x_vals[2], y_vals[2], "k:")
    ax.plot(x_vals[3], y_vals[3], "k-.")
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
