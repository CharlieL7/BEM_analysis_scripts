"""
Extract surface area and volume data from vesicle output files
Plots the data to check the convergence of the simulation
"""

import pandas as pd
import argparse as argp
import numpy as np
import matplotlib.pyplot as plt

def main():
    parser = argp.ArgumentParser(description="Extracts and plots data of the surface area and volume error")
    parser.add_argument("in_file", help="data file of the surface area and volume error")
    parser.add_argument("out_file", help="output plot name")
    parser.add_argument("ca", help="capillary number")
    args = parser.parse_args()

    data = pd.read_csv(args.in_file, comment="#")
    time = data["time"]
    sa_error = data[" sa_error"]
    vol_error = data[" vol_error"]

    rel_sa_error = sa_error / (4 * np.pi)
    rel_vol_error = vol_error / ((4/3) * np.pi)

    fig = plt.figure(figsize=(6, 3))
    ax_left = fig.add_subplot(121)
    ax_right = fig.add_subplot(122)

    ax_left.plot(time, sa_error)
    ax_left.set_xlabel("Time")
    ax_left.set_ylabel("Absolute surface area error")

    ax_right.plot(time, vol_error)
    ax_right.set_xlabel("Time")
    ax_right.set_ylabel("Absolute volume error")

    textstr = (
        r"De = {:.3f}".format(1.00) +
        "\n" +
        r"Ca = {:.3f}".format(float(args.ca)) +
        "\n" +
        r"$\nu$ = {:.3f}".format(1.00) +
        "\n" +
        r"$\lambda$ = {:.3f}".format(1.00)
    )

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.85, 0.50, textstr, fontsize=10, verticalalignment='center', bbox=props)

    fig.tight_layout(rect=[0, 0, 0.85, 1])
    fig.savefig("{}.pdf".format(args.out_file), format="pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
