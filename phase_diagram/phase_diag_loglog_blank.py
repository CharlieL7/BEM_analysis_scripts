"""
short program to make a blank phase diagram
for vesicle in LAOE simulations
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

out_name = sys.argv[1]
fig = plt.figure(figsize=(4.5, 4.5))
ax = fig.add_subplot(111)
ax.set_xlabel(r"De $(\mu a^3 \omega / \kappa)$", fontsize=16)
ax.set_ylabel(r"Ca $(\mu a^3 \dot{\epsilon}_0 / \kappa)$", fontsize=16)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim((0.01, 100))
ax.set_ylim((0.01, 1000))
ax.grid(True)
fig.tight_layout(rect=[0, 0, 0.95, 1])
fig.savefig("{}".format(out_name), format="pdf")
