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
        positions = []
        vels = []
        for vert_data in all_data:
            f_data = [float(x) for x in vert_data[0:3]]
            v_data = [float(x) for x in vert_data[3:6]]
            positions.append(f_data)
            vels.append(v_data)
        vels = td.rotate_vectors(np.array(positions), np.array(vels))
        positions = td.rotate_mesh(np.array(positions))
        
        for i, vert in enumerate(positions): 
            # replacing old data with rotated
            all_data[i][0:3] = vert
            all_data[i][3:6] = vels[i]
        td.write_dat(all_data, f2v, params, "{0}{1:02d}_rot.dat".format(out_dir, file_num))
        file_num += 1

if __name__ == "__main__":
    main()
