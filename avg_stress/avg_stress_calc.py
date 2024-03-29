import glob
import csv
import sys
import os
import argparse as argp
import numpy as np
import slm_UF
import gauss_quad as gq


def calc_stresslet_data(in_dir, **kwargs):
    """
    Reads in the mesh data and then calculates the stresslet at each time
    then returns the data as a list of maps for writing into a csv and the simulation parameters.
    Can skip times by a modifier for faster operation.

    Parameters:
        in_dir: directory of dat files
        [skip_mod]: integer for modulo operation to skip time values
    Returns:
        stress_data: list of maps that can be written out using
        csv.DictWriter
    """
    skip_mod = 1
    stress_data = []
    if "skip_mod" in kwargs:
        tmp = int(kwargs["skip_mod"])
        if tmp != 0:
            skip_mod = int(kwargs["skip_mod"])
        else:
            sys.exit("skip_mod set to 0, fails")
    for dat_file in sorted(glob.glob(in_dir + "*.dat")):
        # code for extracting timestep number from file name, faster than reading file
        fn = os.path.basename(dat_file)
        num = ''.join(i for i in fn if i.isdigit())
        num = int(num)
        if num % skip_mod == 0:
            vesicle = slm_UF.slm_UF.read_dat(dat_file)
            num_faces = vesicle.faces.shape[0]
            S = np.zeros((3, 3))
            for face_num in range(num_faces):
                x_ele = vesicle.get_nodes(vesicle.faces[face_num])
                n_ele = vesicle.calc_normal(vesicle.faces[face_num])
                v_ele = vesicle.get_vels(vesicle.faces[face_num])
                f_ele = vesicle.get_tractions(vesicle.faces[face_num])
                S += gq.int_over_tri(
                    make_coeff_stresslet(x_ele, n_ele, v_ele, f_ele, vesicle.visc_rat),
                    x_ele
                )
            S /= vesicle.volume
            tmp_map = {
                "time": vesicle.time,
                "S_xx": S[0, 0],
                "S_yy": S[1, 1],
                "S_zz": S[2, 2],
                "S_xy": S[0, 1],
                "S_xz": S[0, 2],
                "S_yz": S[1, 2],
            }
            stress_data.append(tmp_map)
    params = {
        "vol_rat": vesicle.vol_rat,
        "visc_rat": vesicle.visc_rat,
        "W": vesicle.W,
        "strain_rate": vesicle.Ca,
        "EB": vesicle.EB,
        "alpha" : vesicle.alpha,
        "nvert" : vesicle.vertices.shape[0],
        "nface" : vesicle.faces.shape[0],
    }
    return (stress_data, params)


def ext_run(in_dir, **kwargs):
    """
    for running the calculation from an external python program

    Parameters:
        in_dir: directory of dat files
        [skip_mod]: integer for modulo operation to skip time values
    Returns:
        None
    """
    if "skip_mod" in kwargs:
        tmp = int(kwargs["skip_mod"])
        stress_data, params = calc_stresslet_data(in_dir, skip_mod=tmp)
    else:
        stress_data, params = calc_stresslet_data(in_dir)
    write_stress_data(stress_data, params)


def write_stress_data(data, params):
    """
    writes the stress data to a csv file

    Parameters:
        data: list of maps with the required keys
        params: parameter map with atleast {vol_rat, W, strain_rate, EB, visc_rat}
    Returns:
        None
    """
    out_name = "stress_data_vol_{0:.3f}_W{1:.3f}_Ca{2:.3f}_visc{3:.3f}.csv".format(
        params["vol_rat"],
        params["W"],
        params["strain_rate"]/ params["EB"],
        params["visc_rat"]
    )
    with open(out_name, "w", newline='') as out:
        # write the simulation parameters
        out.write("# volRat = {}\n".format(params["vol_rat"]))
        out.write("# viscRat = {}\n".format(params["visc_rat"]))
        out.write("# Ca = {}\n".format(params["strain_rate"] / params["EB"]))
        out.write("# W = {}\n".format(params["W"]))
        fieldnames = ["time", "S_xx", "S_yy", "S_zz", "S_xy", "S_xz", "S_yz"]
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def make_coeff_stresslet(x_ele, n_ele, v_ele, f_ele, visc_rat):
    """
    Coefficient of the stresslet for average particle stress tensor calculation

    Parameters:
        x_ele : nodal positions (3, 3) ndarray, rows as positions
        n_ele : normal vector of linear element
        v_ele : nodal velocities (3, 3) ndarray, rows as vels
        f_ele : nodal tractions (3, 3) ndarray, rows as tractions
        visc_rat : viscosity ratio of vesicle
    Returns:
        quad_func : function to input into
        gaussian quadrature func(eta, xi)
    """

    def quad_func(eta, xi):
        f_x_0 = np.outer(f_ele[0], x_ele[0])
        f_x_1 = np.outer(f_ele[1], x_ele[1])
        f_x_2 = np.outer(f_ele[2], x_ele[2])
        A = ( # first term in coeff
            (1. - eta - xi) * f_x_0 +
            eta * f_x_1 +
            xi * f_x_2
        )
        vn_0 = np.outer(v_ele[0], n_ele)
        vn_1 = np.outer(v_ele[1], n_ele)
        vn_2 = np.outer(v_ele[2], n_ele)
        B = ( # second term in coeff
            (1. - eta - xi) * (vn_0 + np.transpose(vn_0)) +
            (eta) * (vn_1 + np.transpose(vn_1)) +
            (xi) * (vn_2 + np.transpose(vn_2))
        )
        return A - (1. - visc_rat) * B

    return quad_func


def main():
    parser = argp.ArgumentParser(description="Calculates the stresslet of a vesicle over a folder" +
                                 "of dat files. Then writes to a csv file.")
    parser.add_argument("in_dir", help="directory of vesicle dat files")
    parser.add_argument("-s", "-skip_mod", help="skip mod argument to parse a subset of the dat files")
    args = parser.parse_args()
    if args.skip_mod:
        ext_run(args.in_dir, skip_mod=args.skip_mod)
    else:
        ext_run(args.in_dir)


if __name__ == "__main__":
    main()
