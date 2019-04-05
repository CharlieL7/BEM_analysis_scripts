#!usr/bin/env python3
"""
Converts a folder of .ply files into the Tecdat .dat file format
"""
import sys
import glob
import csv
import numpy as np

def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: in_dir (where dat files), out_dir")
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    file_num = 0
    for ply_file in sorted(glob.glob(in_dir + "*.ply")):
        positions, f2v, params = read_ply(ply_file)
        f2v = f2v + 1

        write_ply_to_dat(positions, f2v, params, "{0}{1:02d}_remesh.dat".format(out_dir, file_num))
        file_num += 1


def read_ply(filename):
    """
     Reads in vesicle shape ply files into python lists.
     input : the name of the file as a string
     output:
        (positions, f2v, {"nvert", "nfaces"})
        positions: coordinate data for each vertex
        f2v: connectivity data
        nvert: number of verticies nfaces: number of faces
    """
    with open(filename, 'r') as ply_file:
    # reading in the header block
        is_header = True
        while is_header:
            tmp_line = ply_file.readline()
            if tmp_line.find("end_header") != 0:
                ind_vert = tmp_line.find("element vertex")
                ind_face = tmp_line.find("element face")
                if ind_vert != -1:
                    nvert = int(tmp_line[ind_vert+14:])
                elif ind_face != -1:
                    nface = int(tmp_line[ind_face+12:])
            else:
                is_header = False

        try:
            reader = csv.reader(ply_file, delimiter=' ')
            positions = [] # position
            f2v = [] # connectivity

            count = 0
            while count < nvert:
                lst = next(reader)[0:3]
                positions.append([float(i) for i in lst])
                count += 1
            positions = np.array(positions, dtype=float)

            count = 0
            while count < nface:
                lst = next(reader)[1:4] # ignoring first column
                f2v.append([int(i) for i in lst])
                count += 1
            f2v = np.array(f2v, dtype=int)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    try:
        params = {"nvert": nvert, "nface": nface}
        return (positions, f2v, params)
    except NameError as e:
        print("One of the required variables was not instantiated: {}".format(e))


def write_ply_to_dat(positions, f2v, params, out_name):
    txt_str = '\n'.join((
        "VARIABLES = X, Y, Z",
        "ZONE N={0:d} E={1:d} F=FEPOINT ET=TRIANGLE\n".format(params["nvert"], params["nface"])
    ))
    with open(out_name, 'w') as out:
        out.write(txt_str)
        writer = csv.writer(out, delimiter=' ', lineterminator="\n")
        writer.writerows(positions)
        writer.writerows(f2v)
    return None


if __name__ == "__main__":
    main()
