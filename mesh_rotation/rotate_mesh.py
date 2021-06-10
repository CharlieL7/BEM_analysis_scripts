"""
Rotates a mesh around the z-axis.
Originally used to make an alternative prolate spheroid initial condition
"""
import argparse as argp
import sys
from enum import Enum
import numpy as np
import tec_dat as td

class Axis(Enum):
    X = 1
    Y = 2
    Z = 3


def main():
    parser = argp.ArgumentParser(description="Rotates a mesh and writes to a new file")
    parser.add_argument("dat_file", help="Mesh data file")
    parser.add_argument("axis", type=int, help="axis to rotate about (x, y, z) as integer")
    parser.add_argument("degrees", type=float, help="number of degrees to rotate the mesh")
    args = parser.parse_args()
    axis_type = Axis(args.axis)
    rot_mesh(axis_type, args.degrees, args.dat_file)

def rot_mesh(ax, d, dat_file):
    """
    Rotates a mesh d degrees around the given axis
    Then writes the resulting mesh to a file.

    Parameters:
        ax: x, y, or z axis
        d: degrees to rotate
        dat_file: the vesicle data file
    Returns:
        None
    """
    all_data, f2v, params = td.read_short_dat(dat_file)
    positions = []
    for vert_data in all_data:
        pos_data = [float(x) for x in vert_data[0:3]]
        positions.append(pos_data)
    theta = np.radians(d)
    c, s = np.cos(theta), np.sin(theta)

    if ax == Axis.X:
        rot_mat = np.array([
            [1, 0, 0],
            [0, c, -s],
            [0, s, c]
        ])
    elif ax == Axis.Y:
        rot_mat = np.array([
            [c, 0, s],
            [0, 1, 0],
            [-s, 0, c]
        ])
    elif ax == Axis.Z:
        rot_mat = np.array([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1]
        ])
    else:
        sys.exit("Failed to recognize the axis to rotate around")

    new_pos = np.matmul(positions, rot_mat)
    for i, vert in enumerate(new_pos):
        # replacing old data with rotated
        all_data[i][0:3] = vert
    td.write_dat(all_data, f2v, params, "rot_out.dat")

if __name__ == "__main__":
    main()
