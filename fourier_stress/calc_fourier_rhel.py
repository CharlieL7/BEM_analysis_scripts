"""
Caculates the FFT of the stresslet data
and then plots the results
"""
import sys
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def main():
    in_csv = sys.argv[1]
    freq, fourier = read_stress_data(in_csv)
    plot_fourier(freq, fourier, os.path.basename(in_csv))


def read_stress_data(in_csv):
    """
    Reads in the stress data from a csv file
    tsv file should also work

    Parameters:
        in_csv: csv file to read
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
    
    ts = 0.001
    # first interpolate the data, might be needed
    S_1_fun = interp1d(time, S_1, kind="linear")
    inter_times = calc_inter_range(time[0], time[-1], ts)
    S_1_inter = [S_1_fun(x) for x in inter_times]

    fourier = np.fft.fft(S_1_inter)
    n = len(S_1_inter)
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
