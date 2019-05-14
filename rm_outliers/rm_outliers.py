#!usr/bin/env python3
"""
Rotates a bunch of meshes in a folder so x-axis is major axis of the vesicle
Note that the vectors other than position, such as velocity or the forces, have not been rotated
"""
import sys
import glob
import numpy as np
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: in_dir (where dat files to rotate), out_dir")
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    file_num = 0
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, f2v, params = td.read_dat(dat_file)
        forces = []
        bending = []
        for vert_data in all_data:
            f_data = [float(x) for x in vert_data[9:12]]
            fb_data = [float(x) for x in vert_data[6:9]]
            forces.append(f_data)
            bending.append(fb_data)
        dists = [np.linalg.norm(f) for f in forces]
        std_dev = np.std(dists)
        mean = np.mean(dists)
        bound = 3. * std_dev + mean

        for i in range(len(forces)):
            if abs(dists[i]) > bound:
                forces[i] = [0., 0., 0.]

        for i, f in enumerate(forces):
            # replacing old data with rotated
            all_data[i][9:12] = f
        td.write_dat(all_data, f2v, params, "{0}{1:02d}_rm_o.dat".format(out_dir, file_num))
        file_num += 1

if __name__ == "__main__":
    main()
