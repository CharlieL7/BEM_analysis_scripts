import sys
import glob
import numpy as np
import matplotlib.pyplot as plt
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
        self.length_list = []
        self.time_list = []
        self.max_index = 0
        self.total_time = 0.
        self.timestep = 0.001
        self.De = 0.


    def plot_corr_PSD(self, in_dir, out_filename):
        self.get_length_data(in_dir)
        (corr_array, freq, fourier) = self.calc_PSD(out_filename)

        fig_corr = plt.figure()
        ax_corr = fig_corr.add_subplot(111)
        ax_corr.plot(corr_array)
        ax_corr.set_xlim(left=0)
        fig_corr.savefig("{}_corr.pdf".format(out_filename), format="pdf")

        fig_PSD = plt.figure()
        ax_PSD = fig_PSD.add_subplot(111)
        ax_PSD.plot(freq, np.real(fourier), ".")
        ax_PSD.set_yscale("log")
        ax_PSD.set_xlim(left=0)
        fig_PSD.savefig("{}_PSD.pdf".format(out_filename), format="pdf")


    def get_length_data(self, in_dir):
        # get lengths and times
        file_num = 0
        for dat_file in sorted(glob.glob(in_dir + "*.dat")):
            all_data, _f2v, params = td.read_dat(dat_file)
            points = []
            for vert_data in all_data:
                pos_data = [float(x) for x in vert_data[0:3]]
                points.append(pos_data)
            points = np.array(points)
            major = td.calc_length(points)[0]
            self.length_list.append(major)
            self.time_list.append(params["time"])
            if file_num == 0:
                self.De = params["De"]
            file_num += 1
        self.length_arr = np.array(self.length_list)
        self.time_arr = np.array(self.time_list)
        self.max_index = self.time_arr.size - 1
        self.total_time = self.time_arr[self.max_index] - self.time_arr[0]
        self.length_arr = self.length_arr - np.mean(self.length_arr) # subtracting the mean


    def inter_len(self, ts):
        """
        linearly interpolate the length data so that it is constant timestep
        needed to do the cross-correlation
        ts : the timestep that we want to interpolate to
        """
        #TODO


    def calc_PSD(self, out_filename):
        corr_array = np.correlate(self.length_arr, self.length_arr, mode="full")
        fourier = np.fft.fft(corr_array)
        n = corr_array.size
        freq = np.fft.fftfreq(n, d=self.timestep) * (1/self.De)
        return (corr_array, freq, fourier)

if __name__ == "__main__":
    main()
