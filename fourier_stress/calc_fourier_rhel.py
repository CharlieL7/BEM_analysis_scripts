"""
Caculates the FFT of the stresslet data
and then plots the results
"""
import sys
import csv
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def main():
    """
    works on a directory of csv files with stresslet data
    with the ending "/"
    example: "/home/user/tmp/"
    """
    in_dir = sys.argv[1]
    for csv_file in sorted(glob.glob(in_dir + "*.csv")):
        freq, fourier = read_stress_data(csv_file)
        base = os.path.basename(csv_file)
        name_only = os.path.splitext(base)[0]
        plot_fourier(freq, fourier, name_only + "S_1")


def read_stress_data(in_csv, **kwargs):
    """
    Reads in the stress data from a csv file
    tsv file should also work

    Parameters:
        in_csv: csv file to read
        ts: optional timestep setting
    Returns:
        stress_data: stress data as list of dictionaries
    """
    stress_data = []
    with open(in_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items())
            stress_data.append(row)
    time = []
    S_1 = []
    S_2 = []
    for row in stress_data:
        time.append(row["time"])
        S_1.append(row["S_yy"] - row["S_xx"])
        S_2.append(row["S_yy"] - row["S_zz"])

    S_1 = np.array(S_1)
    S_2 = np.array(S_2)
    return (time, [S_1, S_2])


def calc_fourier(time, data, **kwargs):
    """
    Calculates the Fourier transformation of data
    Also does linear interpolation of the data incase the
    timestep changes

    Parameters:
        time: array of the time data
        data: array of the data, same length as time array
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


def plot_fourier(freq, fourier, out_name):
    """
    Plots the Fourier decomposition of the data

    Parameters:
        freq: the frequency bins for the Fourier transform
        fourier: the array of complex Fourier values
        out_name: output name of figure
    Returns:
        None
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(freq, rescale_arr(np.abs(fourier)), ".-")
    ax.set_xlim((0, 15))
    ax.set_xlabel(r"Frequency")
    ax.set_ylabel(r"Amplitude")
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    fig.savefig("{}.pdf".format(out_name), format="pdf")


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


if __name__ == "__main__":
    main()
