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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cycler import cycler
import palettable.colorbrewer.qualitative


def main():
    line_style_list = ['-', '--', '-.', ':']
    style_cnt = 0
    plt.rc("font", family="sans-serif")
    plt.rc("xtick", labelsize="small")
    plt.rc("ytick", labelsize="small")
    plt.rc('axes', prop_cycle=(cycler('color',
        palettable.colorbrewer.qualitative.Dark2_4.mpl_colors) + cycler('linestyle', ['-', '--', ':', '-.'])))

    plt.figure(figsize=(4.5, 4.5))

    folder = sys.argv[1]
    plot_name = input("Name for the plot: ")
    for filename in sorted(glob.glob("{}/*.csv".format(folder))):
        # read header data with open(filename, 'rb') as csv_file:
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
            dataList = list(reader)

        if scaled:
            print("Error: scaled data (use unscaled critcal Ca data)")
            continue

        # moving all the data to lists for plotting
        alpha = []
        lower = []
        upper = []
        for row in dataList:
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

        plotline, caplines, barlinecols = plt.errorbar(alpha, crit_Ca, yerr=error, fmt="None", elinewidth=2, label=vol_rat)
        for x in caplines[::2]:
            x.set_marker('^')
        for y in caplines[1::2]:
            y.set_marker('v')
        for bar in barlinecols:
            bar.set_linestyle(line_style_list[style_cnt % len(line_style_list)])
        style_cnt += 1

    # plt.title('' % vol_rat)
    plt.xlabel("alpha", fontsize=15)
    plt.ylabel("critical Ca", fontsize=15)
    plt.xlim((0, 1.05))
    # plt.ylim( (10**0,12**1) )
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))

    ax.xaxis.set_major_locator(ticker.AutoLocator())
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    plt.grid(True)
    plt.legend(title="reduced volume", fontsize=10)

    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.tight_layout()

    plt.savefig(plot_name + ".pdf", format="pdf", dpi=1000)

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
