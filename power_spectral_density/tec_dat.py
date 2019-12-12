#!usr/bin/env python3
"""
This version of tec_dat has a different read_dat and write_dat
to handle additional data (velocities, forces, tension, etc)
"""
import csv
import sys
import glob
import numpy as np

def read_dat(filename):
    """
     Reads in vesicle shape dat files for tecplot into python lists.
     input : the name of the file as a string
     output:
        (all_data, f2v, params)
        all_data: data for each vertex, first 3 will always be position
        f2v: connectivity data
        params: dict of all other values taken from file
    """
    with open(filename, 'r') as dat_file:
    # reading in the header block
        is_header = True
        header_block = []
        while is_header:
            tmp_line = dat_file.readline()
            if tmp_line.find('#') == 0:
                header_block.append(tmp_line)
                eq_pos = tmp_line.find('=')
                if tmp_line.find("De") != -1:
                    De = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("time") != -1:
                    time = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("viscRat") != -1:
                    visc_rat = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("volRat") != -1:
                    vol_rat = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("deformRate") != -1:
                    deformRate = float(tmp_line[eq_pos+1:])
                elif tmp_line.find("tnum") != -1:
                    _tnum = float(tmp_line[eq_pos+1:])
            else:
                is_header = False
                # get the next two Tecplot lines and then go back one line
                header_block.append(tmp_line)
                last_pos = dat_file.tell()
                tmp_line = dat_file.readline()
                header_block.append(tmp_line)
                dat_file.seek(last_pos)

        try:
            reader = csv.reader(dat_file, delimiter=' ')
            type_line = next(reader)
            nvert = int(type_line[1][2:])
            nface = int(type_line[2][2:])
            all_data = [] # position + all other data
            f2v = [] # connectivity

            count = 0
            while count < nvert:
                lst = next(reader)
                all_data.append(lst)
                count += 1
            all_data = np.array(all_data, dtype=float)

            count = 0
            while count < nface:
                lst = next(reader)[0:3] # should just be 3 values
                f2v.append([int(i) for i in lst])
                count += 1
            f2v = np.array(f2v, dtype=int)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    try:
        params = {"visc_rat": visc_rat, "vol_rat": vol_rat, "De": De, "deformRate": deformRate,
                  "time": time, "nvert": nvert, "nface": nface, "header_block": header_block}
        return (all_data, f2v, params)
    except NameError as e:
        print("One of the required variables was not instantiated: {}".format(e))


def read_short_dat(filename):
    """
     Reads in vesicle shape dat files for tecplot into python lists.
     This version only reads the positions and connectivity
     input : the name of the file as a string
     output:
        (all_data, f2v, params)
        all_data: data for each vertex, first 3 will always be position
        f2v: connectivity data
        params: only header_block 
    """
    with open(filename, 'r') as dat_file:
    # reading in the header block
        is_header = True
        header_block = []
        while is_header:
            tmp_line = dat_file.readline()
            if tmp_line.find('#') == 0:
                header_block.append(tmp_line)
            else:
                is_header = False
                # get the next two Tecplot lines and then go back one line
                header_block.append(tmp_line)
                last_pos = dat_file.tell()
                tmp_line = dat_file.readline()
                header_block.append(tmp_line)
                dat_file.seek(last_pos)

        try:
            reader = csv.reader(dat_file, delimiter=' ')
            type_line = next(reader)
            nvert = int(type_line[1][2:])
            nface = int(type_line[2][2:])
            all_data = [] # position + all other data
            f2v = [] # connectivity

            count = 0
            while count < nvert:
                lst = next(reader)
                all_data.append(lst)
                count += 1
            all_data = np.array(all_data, dtype=float)

            count = 0
            while count < nface:
                lst = next(reader)[0:3] # should just be 3 values
                f2v.append([int(i) for i in lst])
                count += 1
            f2v = np.array(f2v, dtype=int)

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))

    try:
        params = {"header_block": header_block}
        return (all_data, f2v, params)
    except NameError as e:
        print("One of the required variables was not instantiated: {}".format(e))


def read_folder(folder):
    """
    Reads all of the .dat files from a folder and returns a list of the output
    """
    folder_files = folder + "/*.dat"
    dat_files = sorted(glob.glob(folder_files))
    data_list = []
    connect_list = []
    params_list = []
    for dat in dat_files:
        (all_data, f2v, params) = read_dat(dat)
        data_list.append(all_data)
        connect_list.append(f2v)
        params_list.append(params)
    return (data_list, connect_list, params_list)


def write_dat(all_data, f2v, params, out_name):
    """
     Writes vesicle shape data into a tecplot readable .dat format.
     input:
        all_data : postition + all other data
        f2v : connectivity data as 2D numpy array
        params : dict of all other simulation parameters
        out_name: string of the filename you want for the new file
     output :
        None
    """
    with open(out_name, 'w') as out:
        out.writelines(params["header_block"])
        writer = csv.writer(out, delimiter=' ', lineterminator="\n")
        writer.writerows(all_data)
        writer.writerows(f2v)
    return None


def calc_moment_inertia_tensor(x):
    """
    Calculates the moment of inertia tensor for a 2D numpy array of coordinates
    input:
        x : numpy array of vesicle vertex positions
    output:
        tuple of (moment of inertia tensor, the eigenvalues, and eigenvectors)
    """
    (nvert, __) = x.shape
    inertia_tensor = np.zeros((3, 3))
    delta_ij = np.identity(3)
    for i in range(0, nvert):
        r_vec = x[i, :] # positions
        inertia_tensor += np.dot(r_vec, r_vec) * delta_ij - np.outer(r_vec, r_vec)
    [eigvals, eigvecs] = np.linalg.eig(inertia_tensor)
    idx = eigvals.argsort()
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    # first vector positive x
    if eigvecs[0, 0] < 0:
        eigvecs[:, 0] = -eigvecs[:, 0]
    
    # making sure right-handed
    temp = np.cross(eigvecs[:, 0], eigvecs[:, 1])
    if np.dot(temp.T, eigvecs[:, 2]) < 0:
        eigvecs[:, 2] = -eigvecs[:, 2]

    return (inertia_tensor, eigvals, eigvecs)

def add_perturbation(x, eps):
    """
    Adds small sinusodal perturbation to the mesh
    input:
        x : 2D list of vertex coordinate data, unrotated
        eps : the perturbation intensity
    returns:
        numpy array of the the perturbed vertex data
    """
    # rotate mesh by eigenvectors
    x_loc = np.array(x)
    x_loc = x_loc - np.mean(x_loc, 0)
    (__, __, axes) = calc_moment_inertia_tensor(x_loc)
    x_loc = np.matmul(x_loc, axes)
    # add perturbation
    span = np.amax(x_loc[:, 0]) - np.amin(x_loc[:, 0])
    r = np.sqrt(np.square(x_loc[:, 1]) + np.square(x_loc[:, 2]))
    x_loc[:, 1] += eps * np.sin(2*np.pi*x_loc[:, 0]/span) * x_loc[:, 1]/r
    x_loc[:, 2] += eps * np.sin(2*np.pi*x_loc[:, 0]/span) * x_loc[:, 2]/r

    # rotate back
    x_loc = np.matmul(x_loc, axes.T)
    return x_loc


def rotate_mesh(x):
    """
    rotates just the mesh to be aligned with the x-axis
    """
    x = x - x.mean(0) # subtract center of mass, puts center of mass at (0, 0 ,0)
    (__, __, axes) = calc_moment_inertia_tensor(x)
    x_rot = np.matmul(x, axes) # rotate coordinates so aligned with x and y axis
    return x_rot

def rotate_vectors(x, vecs):
    """
    rotates the vectors using the same method as rotating the mesh points
    input:
        x : mesh points
        vecs : numpy array, dimension [x, 3], with the vectors to rotate
    output:
        list of numpy arrays with the rotated data
    """
    x = x - x.mean(0) # subtract center of mass, puts center of mass at (0, 0 ,0)
    (__, __, axes) = calc_moment_inertia_tensor(x)
    vecs_rot = np.matmul(vecs, axes)
    return vecs_rot


def scale_mesh(x_rot):
    """
    scales the mesh to the space from -1 : 1
    x_rot should already be rotated to be aligned with the x axis
    """
    span = np.amax(x_rot[:, 0]) - np.amin(x_rot[:, 0])
    x_rs = np.copy(x_rot)
    x_rs[:, 0] = x_rot[:, 0] / (span/2) #rescale length to -1 to 1
    return x_rs


def calc_length(x):
    x_rot = rotate_mesh(x)
    major = np.amax(x_rot[:, 0]) - np.amin(x_rot[:, 0])
    minor = np.amax(x_rot[:, 1]) - np.amin(x_rot[:, 1])
    return (major, minor)
