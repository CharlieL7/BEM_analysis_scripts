"""
Caculates the FFT of the stresslet data
and then plots the results with real and imaginary components separate
"""
import sys
import csv
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from scipy.interpolate import interp1d

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    """
    works on a directory of csv files with stresslet data
    with the ending "/"
    example: "/home/user/tmp/"
    """
    in_dir = sys.argv[1]
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        data_map = read_stress_data(csv_file)
        out_name = "fourier_data_abs_vol_{0:.3f}_De_{1:.3f}_Ca_{2:.3f}".format(
            data_map["vol_rat"], data_map["De"], data_map["Ca"])
        freq_S1, amp_S1 = calc_fourier(data_map["time"], data_map["S_1"])
        freq_S2, amp_S2 = calc_fourier(data_map["time"], data_map["S_2"])
        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals

        # real version
        fig = plt.figure(figsize=(4.5, 4.5))
        ax_top = fig.add_subplot(211)
        ax_bot = fig.add_subplot(212)
        ax_top.plot(freq_S1 / data_map["De"], np.abs(np.real(amp_S1)), ".-", label=r"$N_1$", color="black")
        ax_bot.plot(freq_S2 / data_map["De"], np.abs(np.real(amp_S2)), ".-", label=r"$N_2$", color="purple")
        ax_top.legend(loc="upper right")
        ax_bot.legend(loc="upper right")
        ax_top.set_xlim((0, 8))
        ax_bot.set_xlim((0, 8))
        ax_top.xaxis.set_major_locator(loc)
        ax_bot.xaxis.set_major_locator(loc)
        ax_bot.set_xlabel(r"Frequency / De")
        ax_top.set_ylabel(r"Amplitude")
        ax_bot.set_ylabel(r"Amplitude")
        add_textbox(ax_bot,
                    r"De = {:.3f}".format(data_map["De"]) +
                    "\n"
                    r"Ca = {:.3f}".format(data_map["Ca"]) +
                    "\n"
                    r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                    "\n"
                    r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                   )
        fig.tight_layout(rect=[0, 0, 0.95, 1])
        fig.savefig("{}_real.pdf".format(out_name), format="pdf")
        plt.close(fig)
        
        # imaginary version
        fig = plt.figure(figsize=(4.5, 4.5))
        ax_top = fig.add_subplot(211)
        ax_bot = fig.add_subplot(212)
        ax_top.plot(freq_S1 / data_map["De"], np.abs(np.imag(amp_S1)), ".-", label=r"$N_1$", color="black")
        ax_bot.plot(freq_S2 / data_map["De"], np.abs(np.imag(amp_S2)), ".-", label=r"$N_2$", color="purple")
        ax_top.legend(loc="upper right")
        ax_bot.legend(loc="upper right")
        ax_top.set_xlim((0, 8))
        ax_bot.set_xlim((0, 8))
        ax_top.xaxis.set_major_locator(loc)
        ax_bot.xaxis.set_major_locator(loc)
        ax_bot.set_xlabel(r"Frequency / De")
        ax_top.set_ylabel(r"Amplitude")
        ax_bot.set_ylabel(r"Amplitude")
        add_textbox(ax_bot,
                    r"De = {:.3f}".format(data_map["De"]) +
                    "\n"
                    r"Ca = {:.3f}".format(data_map["Ca"]) +
                    "\n"
                    r"$\nu$ = {:.3f}".format(data_map["vol_rat"]) +
                    "\n"
                    r"$\lambda$ = {:.3f}".format(data_map["visc_rat"])
                   )
        fig.tight_layout(rect=[0, 0, 0.95, 1])
        fig.savefig("{}_imag.pdf".format(out_name), format="pdf")
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
    for row in stress_data:
        time.append(row["time"] / Ca) # convert to time non-dim by bending timescale
        S_1.append(row["S_xx"] - row["S_yy"])
        S_2.append(row["S_yy"] - row["S_zz"])

    S_1 = np.array(S_1)
    S_2 = np.array(S_2)
    data = {
        "time": np.array(time),
        "S_1": np.array(S_1),
        "S_2": np.array(S_2),
        "W": W,
        "De": W * Ca,
        "Ca": Ca,
        "visc_rat": visc_rat,
        "vol_rat": vol_rat,
    }
    return data


def calc_fourier(time, data, **kwargs):
    """
    Calculates the Fourier transformation of data
    Also does linear interpolation of the data incase the
    timestep changes

    Parameters:
        time: array of the time data
        data: array of the data, same length as time array
        [ts]: optional timestep setting
    Output:
        (freq, fourier), frequency bins and amplitudes as numpy arrays
    """
    ts = 0.001
    if kwargs.get("ts", False):
        ts = kwargs["ts"]
    data_fun = interp1d(time, data, kind="linear")
    inter_times = calc_inter_range(time[0], time[-1], ts)
    data_inter = [data_fun(x) for x in inter_times]

    fourier = np.fft.fft(data_inter)
    n = len(data_inter)
    freq = np.fft.fftfreq(n, d=ts)
    return(freq, fourier)


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
    ax.text(0.70, 0.70, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)


def rescale_arr(arr):
    """
    recale a numpy array such that highest signal is 1

    Parameters:
        arr: the numpy array to rescale
    Returns:
        rescaled numpy array
    """
    max_amp = np.max(arr)
    return arr / max_amp


def calc_inter_range(start, end, timestep):
    """
    outputs an evenly spaced numpy array from start to greatest n fulfilling:
    start + n * timestep < end
    start: starting time
    end: ending time
    timestep: interval for range
    returns: ndarray of times
    """
    lst = []
    t = start
    while t < end:
        lst.append(t)
        t += timestep
    return np.array(lst)


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
