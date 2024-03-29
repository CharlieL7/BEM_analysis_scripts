#!/usr/bin/env python3

"""Ca Plotter.
plots critical Capillary number data for a folder of different
viscosity ratio csv files

author = Charlie Lin
"""

import csv
import sys
import glob
import re
import math
import collections
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cycler import cycler
import palettable.colorbrewer.qualitative

LINE_STYLE_LIST = ['-', '--', '-.', ':']

def main():
    plt.rc("font", family="sans-serif")
    plt.rc("xtick", labelsize="small")
    plt.rc("ytick", labelsize="small")
    plt.rc('axes', prop_cycle=(cycler('color',
        palettable.colorbrewer.qualitative.Dark2_4.mpl_colors) + cycler('linestyle', ['-', '--', ':', '-.'])))
    style_cnt = 0

    folder = sys.argv[1]

    unscaled_fig = plt.figure(figsize=(4.5, 4.5))
    unscaled_ax = unscaled_fig.add_subplot(111)
    scaled_fig = plt.figure(figsize=(4.5, 4.5))
    scaled_ax = scaled_fig.add_subplot(111)

    for filename in sorted(glob.glob("{}/*.csv".format(folder))):
        unscaled_data, scaled_data = get_data(filename)
        plot_crit_Ca(unscaled_ax, unscaled_data, style_cnt)
        plot_crit_Ca(scaled_ax, scaled_data, style_cnt)
        style_cnt += 1

    unscaled_fig.tight_layout()
    unscaled_fig.savefig(unscaled_data.file_name + ".pdf", format="pdf", dpi=1000)
    plt.close(unscaled_fig)

    scaled_fig.tight_layout()
    scaled_fig.savefig(scaled_data.file_name + ".pdf", format="pdf", dpi=1000)
    plt.close(scaled_fig)

def get_data(filename):
    """
    Reads the data from the csv file and returns a named tuple with the data values
    """
    # read header data:
    with open(filename) as csv_file:
        is_header = True
        scaled = False
        while is_header:
            last_pos = csv_file.tell()
            tmp_line = csv_file.readline()
            if tmp_line.find('#') == 0:
                eq_pos = tmp_line.find('=')
                if tmp_line.find("scaled") != -1 and eq_pos != -1:
                    tmp1 = tmp_line[eq_pos+1:]
                    scaled = str_to_bool(re.sub("\s+", '', tmp1))
                elif tmp_line.find("viscRat") != -1 and eq_pos != -1:
                    visc_rat = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("volRat") != -1 and eq_pos != -1:
                    vol_rat = float(tmp_line[eq_pos+1:])
                else:
                    print("Unrecognized header line: {}".format(tmp_line))

            else:
                is_header = False
                csv_file.seek(last_pos)

        # read critical Ca data
        reader = csv.DictReader(csv_file)
        data_list = list(reader)

    if scaled:
        print("Error: scaled data (use unscaled critcal Ca data)")
        return

    # moving all the data to lists for plotting
    alpha = []
    lower = []
    upper = []
    for row in data_list:
        alpha.append(float(row["alpha"]))
        lower.append(float(row["lower"]))
        upper.append(float(row["upper"]))

    num_data = len(alpha)

    crit_Ca = []
    error = []
    for i in range(num_data):
        crit_Ca.append(np.mean((lower[i], upper[i])))
        error.append(abs(upper[i] - lower[i]) / 2.)

    scaled_crit_Ca = [math.sqrt(alpha[i]) * crit_Ca[i] for i in range(num_data)]
    scaled_error = [math.sqrt(alpha[i]) * error[i] for i in range(num_data)]

    Data_Tuple = collections.namedtuple("Data_Tuple", ["file_name", "y_label", "vol_rat", "visc_rat", "alpha", "Ca_data", "error"])

    unscaled_data = Data_Tuple("unscaled_critical_Ca_plot", "critical Ca", vol_rat, visc_rat, alpha, crit_Ca, error)
    scaled_data = Data_Tuple("scaled_critical_Ca_plot", "scaled critical Ca", vol_rat, visc_rat, alpha, scaled_crit_Ca, scaled_error)
    return (unscaled_data, scaled_data)

def plot_crit_Ca(ax, plot_data, style_num):
    """
    Input the scaled or unscaled namedtuple and the the number for the line style
    """

    (plotline, caplines, barlinecols) = ax.errorbar(plot_data.alpha, plot_data.Ca_data, yerr=plot_data.error, fmt="", elinewidth=2, capsize=2, label=plot_data.vol_rat)
    for x in caplines[::2]:
        x.set_marker('^')
    for y in caplines[1::2]:
        y.set_marker('v')
    #for bar in barlinecols:
    #    bar.set_linestyle(LINE_STYLE_LIST[style_num % len(LINE_STYLE_LIST)])

    ax.set_xlabel("alpha", fontsize=15)
    ax.set_ylabel(plot_data.y_label, fontsize=15)
    ax.set_xlim((0, 1.05))
    # plt.ylim( (10**0,12**1) )
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))

    ax.xaxis.set_major_locator(ticker.AutoLocator())
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.grid(True)
    ax.legend(title="reduced volume", fontsize=10)


def expFunc(x, a, b):
    return a * np.exp(-b * x)

def asympFunc(x, a, b):
    return a*x**(b)

def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError("Cannot convert {} to a bool".format(s))

if __name__ == "__main__":
    main()
