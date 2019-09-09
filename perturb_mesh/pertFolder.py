#!usr/bin/env python3
import sys
import glob
import numpy as np
sys.path.insert(0, "../tec_dat/")
import tec_dat as td

def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    pert = 0.01
    if len(sys.argv) == 4:
        pert = float(sys.argv[3])

    file_num = 0
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        all_data, f2v, params = td.read_dat(dat_file)
        positions = []
        for vert_data in all_data:
            pos_data = [float(x) for x in vert_data[0:3]]
            positions.append(pos_data)
        positions = td.add_perturbation(np.array(positions), pert)
        for i, vert in enumerate(positions):
            # replacing old data with rotated
            all_data[i][0:3] = vert
        params["time"] = 0.0;
        td.write_dat(all_data, f2v, params, "{0}{1:02d}_pert.dat".format(out_dir, file_num))
        file_num += 1

if __name__ == "__main__":
    main()
