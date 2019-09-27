import csv
import sys
import glob
import math
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
import tec_dat as td

'''
Plots the power spectral density plots for the LAOE flows
'''

def main():
    in_dir = sys.argv[1]
    out_filename = sys.argv[2]
    x = PSD()
    x.get_length_data(in_dir, out_filename)
    x.calc_PSD()


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

    def get_length_data(self, in_dir, out_filename):
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
            file_num += 1
        self.length_arr = np.array(self.length_list)
        self.time_arr = np.array(self.time_list)
        self.max_index = self.time_arr.size - 1


    def len_auto_corr(self, offset):
        """
        offset : integer with timestep offset
        convention that times outside of the dataset are set to 0
        """
        # making offset length array
        if (offset > 0 and offset < self.max_index):
            len_off = self.length_arr[0:-offset]
            len_off = np.append(len_off, np.zeros(offset)) # zero if outside
        elif (offset < 0 and abs(offset) < self.max_index):
            len_off = self.length_arr[offset:]
            tmp_zeros = np.zeros(abs(offset))
            len_off = np.append(tmp_zeros, len_off) # zero if outside
        elif offset == 0:
            len_off = self.length_arr
        else:
            return 0. # offset outside

        max_time = self.time_arr[-1]
        tmp_arr = np.multiply(self.length_arr, len_off)
        tmp_ret = integrate.simps(tmp_arr, self.time_arr)
        return tmp_ret * (1. / max_time)


    def calc_PSD(self):
        corr_array = []
        for i in range(0, self.max_index):
            corr_array.append(self.len_auto_corr(i))
    
        fourier = np.fft.rfft(corr_array)
        n = fourier.size
        print(fourier)
        timestep = 0.001
        freq = np.fft.fftfreq(n, d=timestep)
        plt.figure(2)
        plt.scatter(freq, fourier)
        plt.show()


if __name__ == "__main__":
    main()
