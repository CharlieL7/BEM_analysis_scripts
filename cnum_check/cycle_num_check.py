"""
Checks all of the simulation csv files in folder have reached a specified
number of oscillatory flow cycles
"""
import csv
import glob
import argparse as argp
import numpy as np

W_TYPE_LINES = [" W "]
CA_TYPE_LINES = [" Ca ", " ca ", " capillary_number "]
VISC_RAT_TYPE_LINES = [" viscRat ", " visc_rat "]
VOL_RAT_TYPE_LINES = [" volRat ", " vol_rat "]

def main():
    parser = argp.ArgumentParser(description="Checks simulation csv files to find if they reached specifed number of cycles")
    parser.add_argument("in_dir", nargs=1, help="directory to read simulation csv files from")
    args = parser.parse_args()
    data_list = []
    for csv_file in sorted(glob.glob(args.in_dir[0] + "*.csv")):
        res = determine_num_cycles(csv_file)
        data_list.append(res)

    fieldnames = ["num_cycles", "De", "Ca",]
    with open("num_cycles.csv", "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_list)


def determine_num_cycles(file_name):
    """
    Determines the number of cycles the simulations have completed

    Parameters:
        file_name: string of csv file name
    Returns:
        {num_cycles, De, Ca}
    """
    time_list = []
    with open(file_name, newline='') as csv_file:
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
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            time_list.append(row["time"])
    time_arr = np.array(time_list)
    period = 1./W
    max_time = time_arr.max()
    num_cycles = max_time // period
    return {"num_cycles":num_cycles, "De":W*Ca, "Ca":Ca}


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
