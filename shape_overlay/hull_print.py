#!/usr/bin/env python3

import sys
import numpy as np
import csv
import ConcaveHull as CH
import tec_dat as td

def main():
    """
    Will then go through a folder data doing this to plot the coefficients of the legendre
    least squares fitting over time to check the stability of the vesicle shape.
    input: command line input
    argv[1] : input dat file
    """
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    print_top_hull(in_file, out_file)

def print_top_hull(in_file, out_file):
    positive_hull = []

    all_data, _f2v, _params = td.read_dat(in_file)
    positions = []
    for vert_data in all_data:
        f_data = [float(x) for x in vert_data[0:3]]
        positions.append(f_data)
    positions = td.rotate_mesh(np.array(positions))

    # get x and y column only
    verts_2D = positions[:, 0:2]
    hull = CH.concaveHull(verts_2D, 40) # list of hull points
    for pt in hull:
        positive_hull.append(pt)

    with open(out_file, "w") as out:
        out.write("x, y\n")
        writer = csv.writer(out, delimiter=',', lineterminator="\n")
        writer.writerows(positive_hull)

if __name__ == "__main__":
    main()
