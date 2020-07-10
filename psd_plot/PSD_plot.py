import os
import glob
import csv
import argparse as argp
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

'''
Plots the power spectral density plots for the LAOE flows
'''

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Makes power spectial density plots for vesicles in LAOE")
    parser.add_argument("in_dir", help="directory of length csv files")
    parser.add_argument("-s", "--skip_cycles", help="number of initial cycles to skip")
    args = parser.parse_args()
    in_dir = args.in_dir
    skip_cycles = 0
    if args.skip_cycles:
        skip_cycles = args.skip_cycles
    x = PSD()
    x.plot_corr_PSD(in_dir, skip_cycles)


class PSD:
    """
    class that holds the lengths and times for the power spectral density calculation
    """

    def __init__(self):
        self.length_arr = np.array([])
        self.time_arr = np.array([])
        self.timestep = 0.01
        self.De = 0.
        self.Ca = 0.
        self.inter_times = None
        self.len_inter_arr = None


    def plot_corr_PSD(self, in_dir, num_skip):
        """
        plots the calculated cross correlation and power spectral density

        Parameters:
            in_dir: directory of length csv files
        """
        for csv_file in sorted(glob.glob(in_dir + "*.csv")):
            base = os.path.basename(csv_file)
            name_only = os.path.splitext(base)[0]
            try:
                self.read_length_data(csv_file, skip_cycles=num_skip)
                (corr_arr, freq, fourier) = self.calc_PSD()

                fig_PSD = plt.figure()
                ax_PSD = fig_PSD.add_subplot(111)
                ax_PSD.plot(freq / self.De, np.real(fourier), ".")
                ax_PSD.set_yscale("log")
                ax_PSD.set_title("PSD [De={0}, Ca={1}]".format(self.De, self.Ca))
                ax_PSD.set_xlabel(r"Frequency $\times$ T ($\frac{f}{De}$)")
                ax_PSD.set_ylabel("Amplitude")
                ax_PSD.set_xlim([0, 10])
                ax_PSD.grid(True)
                plt.xticks(np.arange(0, 11, 1.0))
                fig_PSD.savefig("{}_PSD.pdf".format(name_only), format="pdf")
                plt.close(fig_PSD)

                fig_corr = plt.figure()
                ax_corr = fig_corr.add_subplot(111)
                split_corr_arr = corr_arr[(corr_arr.size//2):]
                ax_corr.plot(self.inter_times * self.De, split_corr_arr, ".-")
                ax_corr.set_title("autocorrelation [De={0}, Ca={1}]".format(self.De, self.Ca))
                ax_corr.set_xlabel(r"phase lag $\cdot$ De")
                ax_corr.set_ylabel("ACF")
                ax_corr.set_xlim([0, 10])
                ax_corr.grid(True)
                plt.xticks(np.arange(0, 11, 1.0))
                fig_corr.savefig("{}_corr.pdf".format(name_only), format="pdf")
                plt.close(fig_corr)
            except IOError as err:
                print("IOError for csv file: {}".format(csv_file))
                print(err)


    def read_length_data(self, in_csv, **kwargs):
        """
        Reads the simulation data from file
        sets length_arr, time_arr, De, Ca

        Parameters:
            in_csv: csv file to read
            [skip_cycles]: for skipping an initial number of flow cycles
                assumes times start at 0
        Returns:
            None
        """
        length_list = []
        all_times = []
        time_list = []
        skip_cycles = 0
        if kwargs.get("skip_cycles", False):
            skip_cycles = kwargs["skip_cycles"]
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
            De = Ca * W
            for row in reader:
                row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
                t = row["time"] / Ca
                all_times.append(t)
                if row["time"] > (skip_cycles/De): # only add value if after certain number of cycles
                    time_list.append(t)
                    length_list.append(row["major_len"])
        period = 1./De

        if all_times[-1] < 10*period:
            raise IOError("Cycles < 10: {} simulated, parameters: De={} Ca={}".format(all_times[-1] / period, De, Ca))

        self.time_arr = np.array(time_list)
        self.length_arr = np.array(length_list)
        self.length_arr = self.length_arr - np.mean(self.length_arr) # subtracting the mean
        self.Ca = Ca
        self.De = De


    def calc_PSD(self):
        """
        calculates the power spectral density data
        returns : tuple of (ndarray cross correlation values, ndarray fourier frequencies,
        ndarray fourier amplitudes)
        """
        # first interpolate the data
        len_fun = interp1d(self.time_arr, self.length_arr, kind="linear")
        self.inter_times = calc_inter_range(self.time_arr[0], self.time_arr[-1], self.timestep)
        self.len_inter_arr = [len_fun(x)for x in self.inter_times]

        # cross correlate the interpolated data
        corr_arr = np.correlate(self.len_inter_arr, self.len_inter_arr, mode="full")
        fourier = np.fft.fft(corr_arr)
        n = corr_arr.size
        freq = np.fft.fftfreq(n, d=self.timestep)
        return (corr_arr, freq, fourier)


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
