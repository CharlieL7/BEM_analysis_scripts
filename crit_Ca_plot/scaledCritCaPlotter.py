#!/usr/bin/env python2

"""Scaled Ca Plotter.
plots critical Capillary number data for a folder of different
viscosity ratio csv files

author = Charlie Lin
"""

import csv
import sys
import glob
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# from scipy.optimize import curve_fit
# from scipy import stats
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

        if not scaled:
            print("Used scaled critcal Ca ploter on unscaled data")
            continue

        # moving all the data to lists for plotting
        alpha = []
        lower = []
        upper = []
        for row in dataList:
            alpha.append(float(row["alpha"]))
            lower.append(float(row["lower"]))
            upper.append(float(row["upper"]))

        crit_Ca = []
        error = []
        for i in range(len(lower)):
            crit_Ca.append(np.mean((lower[i], upper[i])))
            error.append(abs(upper[i] - lower[i]) / 2.)

        # xVals = np.linspace(0,1,50)
        # popt, pcov = curve_fit(expFunc, alpha, crit_Ca)
        # popt, pcov = curve_fit(asympFunc, alpha, crit_Ca)

        # plotting norm vs time
        # plt.xscale("log", nonposx='clip')
        # plt.yscale("log", nonposy='clip')

        # plt.errorbar(alpha, crit_Ca, yerr=error, fmt=markerList[markCnt % len(markerList)], label="Simulations")

        plotline, caplines, barlinecols = plt.errorbar(alpha, crit_Ca, yerr=error, fmt="None", elinewidth=2, label=vol_rat)
        for x in caplines[::2]:
            x.set_marker('^')
        for y in caplines[1::2]:
            y.set_marker('v')
        for bar in barlinecols:
            bar.set_linestyle(line_style_list[style_cnt % len(line_style_list)])
        style_cnt += 1

        # disabled
        # plt.plot(xVals, asympFunc(xVals, *popt), ls='-', label="Power Fit")

    # plt.title('' % vol_rat)
    plt.xlabel("alpha", fontsize=15)
    plt.ylabel("scaled critical Ca", fontsize=15)
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
    # textstr = '\n'.join((
    #    r'Non-Linear Fit: $Ax^B$',
    #    r'$A = {0:7.2f}$'.format(popt[0]),
    #    r'$B = {0:7.2f}$'.format(popt[1])))
    # ax.text(0.10, 0.10, textstr, transform=ax.transAxes, fontsize=14,
    #    verticalalignment='bottom', bbox=props)
    plt.tight_layout()

    plt.savefig("scaledCritCa.pdf", format="pdf", dpi=1000)

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
