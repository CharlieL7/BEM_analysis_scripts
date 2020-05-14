"""
short program to make a phase diagram from three csv files
for vesicle in LAOE simulations
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

out_name = sys.argv[1]
w_high, Ca_high, De_high = np.loadtxt("quasisphereical results - vol080_High.tsv", skiprows=4, unpack=True)
w_medium, Ca_medium, De_medium = np.loadtxt("quasisphereical results - vol080_Medium.tsv", skiprows=4, unpack=True)
w_low, Ca_low, De_low = np.loadtxt("quasisphereical results - vol080_Low.tsv", skiprows=4, unpack=True)
fig = plt.figure(figsize=(4.5, 4.5))
ax = fig.add_subplot(111)
ax.plot(De_high, Ca_high, "o", label="high strain")
ax.plot(De_medium, Ca_medium, "*", label="medium strain")
ax.plot(De_low, Ca_low, "^", label="low strain")
ax.set_xlabel(r"De $(\mu a^3 \omega / \kappa)$", fontsize=16)
#ax.set_xlabel(r"$\bar{\omega} (\omega / \dot{\epsilon}_0)$", fontsize=16)
ax.set_ylabel(r"Ca $(\mu a^3 \dot{\epsilon}_0 / \kappa)$", fontsize=16)
ax.set_xscale("log")
ax.set_yscale("log")
ax.grid(True)
ax.grid(True, which="minor")
ax.legend(title=r"$\nu = 0.80, \lambda = 1.00$", loc="lower right", bbox_to_anchor=(0.90, 0.10))
fig.tight_layout(rect=[0, 0, 0.95, 1])
fig.savefig("{}".format(out_name), format="pdf")
