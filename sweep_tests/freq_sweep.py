"""
Calculates and plots G' and G'' from directory of csv files
with vesicle stresslet data over time for a set of different
flow frequencies with the same strain rate.
"""
import csv
import glob
import os
import argparse as argp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from scipy.interpolate import interp1d

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Calculates G' and G'' from directory of stress csv files")
    parser.add_argument("stress_dir", help="directory of stress csv files")
    args = parser.parse_args()
    stress_dir = os.path.join(args.stress_dir, "")
    De_list = []
    S1_mods = []
    for csv_file in sorted(glob.glob(stress_dir + "*.csv")):
        data_map = read_stress_data(csv_file)
        De_list.append(data_map["De"])
        S1_mods.append(calc_mod(data_map["time"], data_map["S_1"], ts=0.001))

    # sorting
    S1_mods = np.array(S1_mods)
    De_arr = np.array(De_list)
    idx = np.argsort(De_arr)
    De_arr = De_arr[idx]
    S1_mods = S1_mods[idx]

    # plotting
    loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    print(np.imag(S1_mods))
    ax.plot(De_arr, np.real(S1_mods), label=r"G''")
    ax.plot(De_arr, np.imag(S1_mods), label=r"G'")
    ax.xaxis.set_major_locator(loc)
    ax.legend()
    plt.show()


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


def calc_mod(time, data, **kwargs):
    """
    Calulates the complex modulus using the Fourier Transform.
    Linearly interpolates the input data incase the sampling rate changes.
    Expecting a single peak for the transformed signal, then looking for the coefficient
    of the peak at the first mode.

    Parameters:
        time: array of the time data
        data: array of the data, same length as time array
        [ts]: optional timestep setting
    Returns:
        complex modulus
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
    
    closest_ind = 0
    for i, val in enumerate(freq):
        if (np.abs(val - 1.) < freq[closest_ind]):
            closest_ind = i

    return fourier[closest_ind]


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


if __name__ == "__main__":
    main()
