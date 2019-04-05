#!usr/bin/env python3
"""
Converts a folder of tecdat .dat file into a .ply file format
New file will only contain the position and edge data
"""
import sys
import glob
import csv
import numpy as np
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: in_dir (where dat files), out_dir")
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    file_num = 0
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            f_data = [float(x) for x in vert_data[0:3]]
            positions.append(f_data)
        positions = td.rotate_mesh(np.array(positions))
        f2v = f2v - 1
        num_rows = f2v.shape[0]
        tri_col = np.full((num_rows, 1), 3)
        f2v = np.hstack((tri_col, f2v))

        write_ply(positions, f2v, params, "{0}{1:02d}.ply".format(out_dir, file_num))
        file_num += 1

def write_ply(positions, f2v, params, out_name):
    """
     Writes vesicle shape data into a tecplot readable .dat format.
     input:
        positions: postition data as 2D numpy array
        f2v : connectivity data as 2D numpy array
        params : dict of all other simulation parameters
        out_name: string of the filename you want for the new file
     output :
        None
    """
    txt_str = '\n'.join((
        "ply",
        "format ascii 1.0",
        "comment converted from Tecdat dat file",
        "element vertex {}".format(params["nvert"]),
        "property float x",
        "property float y",
        "property float z",
        "element face {}".format(params["nface"]),
        "property list uchar int vertex_index",
        "end_header\n"
        ))
    with open(out_name, 'w') as out:
        out.write(txt_str)
        writer = csv.writer(out, delimiter=' ', lineterminator="\n")
        writer.writerows(positions)
        writer.writerows(f2v)
    return None

if __name__ == "__main__":
    main()
