"""
Plots the deformation parameter wrt. to strain (Ca_x).
Overlays the experimental and numerical data on one plot
"""
import csv
import sys
import math
import numpy as np
import matplotlib.pyplot as plt


def main():
    sim_file = sys.argv[1]
    exp_file = sys.argv[2]
    out_name = sys.argv[3]
    sim_data = read_sim_data(sim_file)
    exp_data = read_exp_data(exp_file, skiprows=6)
    plot_deform_ratios(exp_data, sim_data, out_name)


def read_sim_data(file_name):
    """
    Reads the simulation data from file
    Note that the simulation data file has a different structure from
    the experimental data

    Parameters:
        file_name: name of the file
    Returns:
        numpy array of the time data
        numpy array of the deformation parameter data
    """
    Ca_x_list = []
    D_list = []
    with open(file_name, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            time = row["time"]
            Ca = 55.7
            De = 2.4
            Ca_x = -Ca * math.sin(2 * math.pi * De/Ca * time)
            Ca_x_list.append(Ca_x)
            D_list.append((row["x_len"] - row["y_len"]) / (row["x_len"] + row["y_len"]))
    Ca_x_arr = np.array(Ca_x_list)
    print(Ca_x_arr)
    D_arr = np.array(D_list)
    return (Ca_x_arr, D_arr)


def read_exp_data(file_name, **kwargs):
    """
    Reads the experimental data from file

    Parameters:
        file_name: name of the file
        skiprows to skip a number of rows at top of file
    Returns:
        numpy array of the time data
        numpy array of the deformation parameter data
    """
    skiprows = 0
    Ca_x_list = []
    D_list = []
    if "skiprows" in kwargs:
        skiprows = kwargs["skiprows"]
    with open(file_name, newline='') as csv_file:
        a = 0
        while a < skiprows:
            csv_file.readline()
            a += 1
        reader = csv.DictReader(csv_file, delimiter="\t")
        for row in reader:
            row = dict([a, float(x)] for a, x in row.items()) # convert data to floats
            Ca_x_list.append(row["Ca_x"])
            D_list.append(row["D"])
    Ca_x_arr = np.array(Ca_x_list)
    D_arr = np.array(D_list)
    return (Ca_x_arr, D_arr)


def plot_deform_ratios(exp_data, sim_data, out_name):
    """
    Plots the deformation parameter comparison
    """
    fig = plt.figure(figsize=(4.5, 4.5))
    ax = fig.add_subplot(111)
    ax.plot(exp_data[0], exp_data[1], "-")
    ax.plot(sim_data[0], sim_data[1], "--")
    ax.set_xlabel(r"$Ca_{x} (\frac{\mu a^3 \dot{\epsilon}}{\kappa})$", fontsize=14)
    ax.set_ylabel(r"Deformation parameter $\left( \frac{l_x - l_y}{l_x + l_y} \right)$", fontsize=14)
    ax.set_ylim([-1, 1])
    ax.grid(True)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    fig.savefig("{}".format(out_name), format="pdf")
    plt.close()


if __name__ == "__main__":
    main()
