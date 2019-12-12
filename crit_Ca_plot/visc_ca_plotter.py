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
from scipy.optimize import curve_fit


LINE_STYLE_DICT = {0.010:"-", 0.500:"--", 1.000:"-.", 5.000:":"}
COLOR_STYLE_DICT = {0.010:"slateblue", 0.500:"seagreen", 1.000:"firebrick", 5.000:"coral"}
MARKER_STYLE_DICT= {0.010:"s", 0.500:"*", 1.000:".", 5.000:"X"}


def main():
    plt.rc("font", family="sans-serif")
    plt.rc("xtick", labelsize="small")
    plt.rc("ytick", labelsize="small")
    style_cnt = 0

    folder = sys.argv[1]

    unscaled_fig = plt.figure(figsize=(3.0, 3.0))
    unscaled_ax = unscaled_fig.add_subplot(111)
    scaled_fig = plt.figure(figsize=(3.0, 3.0))
    scaled_ax = scaled_fig.add_subplot(111)

    for filename in sorted(glob.glob("{}/*.csv".format(folder))):
        unscaled_data, scaled_data = get_data(filename)
        plot_crit_Ca(unscaled_ax, unscaled_data)
        plot_crit_Ca(scaled_ax, scaled_data)
        if abs(unscaled_data.visc_rat - 1.0) < 1e-5:
            plot_trend(unscaled_ax, unscaled_data)
        style_cnt += 1

    textstr = r"$\nu=0.70$"
    plot_final_setup(unscaled_fig, unscaled_ax, (5, 25), r"$Ca_{crit}$", textstr)
    plot_final_setup(scaled_fig, scaled_ax, (1, 5), r"$Ca_{crit} \cdot \sqrt{\alpha}$", textstr)

    unscaled_fig.savefig(unscaled_data.file_name + ".pdf", format="pdf", dpi=1000)
    plt.close(unscaled_fig)

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


def plot_crit_Ca(ax, plot_data):
    """
    Input the scaled or unscaled namedtuple and the the number for the line style
    """
    visc_rat = plot_data.visc_rat
    (plotline, caplines, barlinecols) = ax.errorbar(plot_data.alpha, plot_data.Ca_data, yerr=plot_data.error, fmt=" ",
            elinewidth=2, capsize=2, alpha=0.80,
            color=COLOR_STYLE_DICT[visc_rat], label=visc_rat)
    for x in caplines:
        x.set_marker(MARKER_STYLE_DICT[visc_rat])
    for bar in barlinecols:
        bar.set_linestyle(LINE_STYLE_DICT[plot_data.visc_rat])


def plot_trend(ax, plot_data):
    """
    Plots the power-law trendline
    """
    print(plot_data.alpha)
    print(plot_data.Ca_data)
    popt, pcov = curve_fit(func_powerlaw, plot_data.alpha, plot_data.Ca_data, p0 = np.asarray([-0.5, 2]))

    x_trend = np.linspace(0.1, 1.)
    ax.plot(x_trend, func_powerlaw(x_trend, *popt), "--")
    textstr = r"$y = %.2f x^{%.2f}$" % (popt[1], popt[0])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.42, 0.80, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)


def plot_final_setup(fig, ax, y_lim, y_label, textstr):
    # textbox
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.42, 0.60, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)

    ax.set_xlabel(r"$\alpha$ (flow type)", fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_xlim((0, 1.05))
    ax.set_ylim(y_lim)
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))

    ax.xaxis.set_major_locator(ticker.AutoLocator())
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
    ax.grid(True)
    #ax.legend(title=r"$\lambda$", fontsize=10, bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0, prop={"size": 10})
    fig.tight_layout(rect=[0, 0, 0.95, 1])


def str_to_bool(s):
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError("Cannot convert {} to a bool".format(s))


def func_powerlaw(x, m, c):
    return x**m * c


if __name__ == "__main__":
    main()
