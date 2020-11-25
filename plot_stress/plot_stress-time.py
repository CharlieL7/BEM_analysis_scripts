"""
short script to make stress vs. time diagrams
for vesicle in LAOE simulations
"""
import sys
import glob
import os
import csv
import numpy as np
import matplotlib.pyplot as plt

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    in_dir = sys.argv[1]
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        base = os.path.basename(csv_file)
        name_only = os.path.splitext(base)[0]
        data_map = read_stress_data(csv_file)
        time = data_map["time"]
        De = data_map["De"]
        N1 = data_map["S_1"]
        N2 = data_map["S_2"]
        fig1 = plt.figure(figsize=(4.5, 4.5))

        ax1 = fig1.add_subplot()
        ax1.plot(time, N1, "k-", label=r"$N_1$")
        ax1.plot(time, N2, "b-", label=r"$N_2$")
        ax1.plot(time, -np.sin(2. * np.pi * time * De), "m--", label=r"$\dot{\epsilon}$")
        ax1.set_xlabel(r"time ($t \kappa / \mu a^3$)", fontsize=16)
        ax1.set_ylabel(r"normal stress difference ($\frac{\sigma_{ij}^P a^3}{V_p \kappa}$)", fontsize=16)
        ax1.grid(True)
        add_textbox(ax1,
            r"De = {:.3f}".format(data_map["De"]) +
            "\n"
            r"Ca = {:.3f}".format(data_map["Ca"]) +
            "\n"
            r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
            "\n"
            r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
        )
        ax1.legend(loc="upper left")
        #ax1.set_ylim([-10, 10])

        fig1.tight_layout(rect=[0, 0, 0.95, 1])
        fig1.savefig("{}_time_plot.pdf".format(name_only), format="pdf")
        plt.close(fig1)


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
        if 6/De < t <= 8/De:
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
    ax.text(0.70, 0.20, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)


if __name__ == "__main__":
    main()
