"""
Plots a color coded negative sin curve
for usage as a legend to the deformation parameter curve
"""
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(4.5, 4.5))
ax = fig.add_subplot(111)
x_vals = []
x_vals.append(np.linspace(0, 0.5*np.pi))
x_vals.append(np.linspace(0.5*np.pi, 1.0*np.pi))
x_vals.append(np.linspace(1.0*np.pi, 1.5*np.pi))
x_vals.append(np.linspace(1.5*np.pi, 2.0*np.pi))

y_vals = []
y_vals.append(-np.sin(x_vals[0]))
y_vals.append(-np.sin(x_vals[1]))
y_vals.append(-np.sin(x_vals[2]))
y_vals.append(-np.sin(x_vals[3]))

ax.plot(x_vals[0], y_vals[0], "k-")
ax.plot(x_vals[1], y_vals[1], "b--")
ax.plot(x_vals[2], y_vals[2], "g-.")
ax.plot(x_vals[3], y_vals[3], "r:")

ax.grid(True)
fig.tight_layout(rect=[0, 0, 0.95, 1])
fig.savefig("{}.pdf".format("sin_legend"), format="pdf")
plt.close(fig)
