"""
short script to make stress vs. strain-rate diagrams
for vesicle in LAOE simulations
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt

csv_file = sys.argv[1]
out_name = sys.argv[2]
data = pd.read_csv(csv_file)
Ca_x = data["Ca_x"]
N1 = -(data["S_xx"] - data["S_yy"])
N2 = -(data["S_zz"] - data["S_yy"])
fig1 = plt.figure(figsize=(4.5, 4.5))
fig2 = plt.figure(figsize=(4.5, 4.5))

ax1 = fig1.add_subplot()
ax2 = fig2.add_subplot()
ax1.plot(Ca_x, N1, "-")
ax1.set_xlabel(r"$Ca_x$", fontsize=12)
ax1.set_ylabel(r"$-(S_{xx} - S_{yy})$", fontsize=12)
ax1.grid(True)

ax2.plot(Ca_x, N2, "-")
ax2.set_xlabel(r"$Ca_x$", fontsize=12)
ax2.set_ylabel(r"$-(S_{zz} - S_{yy})$", fontsize=12)
ax2.grid(True)

fig1.tight_layout(rect=[0, 0, 0.95, 1])
fig2.tight_layout(rect=[0, 0, 0.95, 1])
fig1.savefig("{}_N1.pdf".format(out_name), format="pdf")
fig2.savefig("{}_N2.pdf".format(out_name), format="pdf")
