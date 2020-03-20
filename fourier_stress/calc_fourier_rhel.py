"""
Caculates the FFT of the stresslet data
and then plots the results
"""
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt

def main():
    in_csv = sys.argv[1]
    out_file = sys.argv[2]
    freq, fourier = read_stress_data(in_csv)
    plot_fourier(freq, fourier)


def read_stress_data(in_csv):
    """
    Reads in the stress data from a csv file

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
    fourier = np.fft.fft(S_1)
    n = S_1.size
    freq = np.fft.fftfreq(n, d=0.001)
    return(freq, fourier)


def plot_fourier(freq, fourier):
    """
    Plots the Fourier decomposition of the data
    
    Parameters:
        freq: the frequency bins for the Fourier transform
        fourier: the array of complex Fourier values
    Returns:
        None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(freq, rescale_arr(np.abs(fourier)), ".-")
    ax.set_xlim((0, 15))
    ax.set_xlabel(r"Frequency")
    ax.set_ylabel(r"Amplitude")
    plt.show()


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


if __name__ == "__main__":
    main()
