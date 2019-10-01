import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import tec_dat as td

'''
Plots the power spectral density plots for the LAOE flows
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    x = PSD()
    x.plot_corr_PSD(in_dir, out_filename)


class PSD:
    """
    class that holds the lengths and times for the power spectral density calculation
    """

    def __init__(self):
        self.length_arr = np.array([])
        self.time_arr = np.array([])
        self.timestep = 0.001
        self.De = 0.
        self.Ca = 0.


    def plot_corr_PSD(self, in_dir, out_filename):
        """
        plots the calculated cross correlation and power spectral density
        """
        self.read_length_data(in_dir)
        (corr_arr, freq, fourier) = self.calc_PSD()
        
        lag_arr = np.arange(corr_arr.size - 1, corr_arr.size, 1)
        fig_corr = plt.figure()
        ax_corr = fig_corr.add_subplot(111)
        ax_corr.plot(lag_arr, corr_arr)
        ax_corr.set_xlim(left=0)
        fig_corr.savefig("{}_corr.pdf".format(out_filename), format="pdf")
        fig_corr.close();

        fig_PSD = plt.figure()
        ax_PSD = fig_PSD.add_subplot(111)
        ax_PSD.plot(freq, np.real(fourier), ".")
        ax_PSD.set_yscale("log")
        ax_PSD.set_xlim(left=0)
        fig_PSD.savefig("{}_PSD.pdf".format(out_filename), format="pdf")
        fig_PSD.close();


    def read_length_data(self, in_dir):
        """
        reads lengths and times from a directory of dat files
        sets length_arr, time_arr, De, Ca
        in_dir : directory string
        returns : nothing
        """
        file_num = 0
        length_list = []
        time_list = []
        for dat_file in sorted(glob.glob(in_dir + "/*.dat")):
            all_data, _f2v, params = td.read_dat(dat_file)
            points = []
            for vert_data in all_data:
                pos_data = [float(x) for x in vert_data[0:3]]
                points.append(pos_data)
            points = np.array(points)
            major = td.calc_length(points)[0]
            length_list.append(major)
            time_list.append(params["time"])
            if file_num == 0:
                self.De = params["De"]
                self.Ca = params["Ca"]
            file_num += 1
        self.length_arr = np.array(self.length_list)
        self.time_arr = np.array(self.time_list)
        self.length_arr = self.length_arr - np.mean(self.length_arr) # subtracting the mean


    def calc_PSD(self):
        """
        calculates the power spectral density data
        returns : tuple of (n1array cross correlation values, n1array fourier frequencies, n1array fourier amplitudes)
        """
        # first interpolate the data
        len_fun = interp1d(self.length_arr, self.time_arr, kind="linear")
        inter_times = calc_inter_range(self.time_arr[0], self.time_arr[-1], self.timestep)
        len_inter_arr = [ len_fun(x) for x in inter_times ]
        
        # cross correlate the interpolated data
        corr_arr = np.correlate(len_inter_arr, len_inter_arr, mode="full")
        fourier = np.fft.fft(corr_arr)
        n = corr_arr.size
        # getting frequencies multiplied by cycle peroid (non-dimensionalized by bending timescale)
        freq = np.fft.fftfreq(n, d=self.timestep) / (self.De * self.Ca)
        return (corr_arr, freq, fourier)


def calc_inter_range(start, end, timestep):
    """
    outputs an evenly spaced numpy array from start to greatest n fulfilling:
    start + n * timestep < end
    start: starting time
    end: ending time
    timestep: interval for range
    returns: n1array of times
    """
    lst = []
    t = start
    while t < end:
        lst.append(t)
        t += timestep
    return np.array(lst)


if __name__ == "__main__":
    main()
