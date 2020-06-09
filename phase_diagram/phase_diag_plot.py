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
De_high, Ca_high, _max, _min = np.loadtxt("high_strain_list.csv", skiprows=1, delimiter=",", unpack=True)
De_medium, Ca_medium, _max, _min = np.loadtxt("med_strain_list.csv", skiprows=1, delimiter=",", unpack=True)
De_low, Ca_low, _max, _min = np.loadtxt("low_strain_list.csv", skiprows=1, delimiter=",", unpack=True)

fig = plt.figure(figsize=(4.5, 4.5))
ax = fig.add_subplot(111)
ax.plot(De_high, Ca_high, "o", label="high deform.")
ax.plot(De_medium, Ca_medium, "*", label="medium deform.")
ax.plot(De_low, Ca_low, "^", label="low deform.")
ax.set_xlabel(r"De $(\mu a^3 \omega / \kappa)$", fontsize=16)
#ax.set_xlabel(r"$\bar{\omega} (\omega / \dot{\epsilon}_0)$", fontsize=16)
ax.set_ylabel(r"Ca $(\mu a^3 \dot{\epsilon}_0 / \kappa)$", fontsize=16)
#ax.set_xlim((0, 5.0))
#ax.set_ylim((0, 14.0))
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.grid(True)
ax.grid(True, which="minor")
ax.legend(title=r"$\nu = 0.80, \lambda = 1.00$", loc="lower right", bbox_to_anchor=(0.55, 0.60))
fig.tight_layout(rect=[0, 0, 0.95, 1])
fig.savefig("{}".format(out_name), format="pdf")
