"""
Rotates a mesh around the z-axis.
Originally used to make an alternative prolate spheroid initial condition
"""
import argparse as argp
import numpy as np
import tec_dat as td

def main():
    parser = argp.ArgumentParser(description="Rotates a mesh and writes to a new file")
    parser.add_argument("dat_file", help="Mesh data file")
    args = parser.parse_args()
    rot_90z(args.dat_file)

def rot_90z(dat_file):
    """
    Rotates a mesh 90 degrees in the z-axis.
    Then writes the resulting mesh to a file.

    Parameters:
        dat_file: the vesicle data file
    Returns:
        None
    """
    all_data, f2v, params = td.read_short_dat(dat_file)
    positions = []
    for vert_data in all_data:
        pos_data = [float(x) for x in vert_data[0:3]]
        positions.append(pos_data)
    theta = np.radians(90)
    c, s = np.cos(theta), np.sin(theta)
    rot_mat = np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])
    new_pos = np.matmul(positions, rot_mat)
    for i, vert in enumerate(new_pos):
        # replacing old data with rotated
        all_data[i][0:3] = vert
    td.write_dat(all_data, f2v, params, "rot_out.dat")

if __name__ == "__main__":
    main()
