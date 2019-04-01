import csv
import sys
import numpy as np

def read_data(filename):
    # expecting tecplot readable data
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=' ')
        try:
            reader.next()
            reader.next()
            typeLine = reader.next()
            nvert = int(typeLine[1][2:])
            nface = int(typeLine[2][2:])
            x = [] # the vertec positions
            f2v = []    # element numbering

            count = 0
            while count < nvert:
                lst = reader.next()[0:3]
                x.append([float(i) for i in lst])
                count += 1

            count = 0
            while count < nface:
                lst = reader.next()[0:3]
                f2v.append([float(i) for i in lst])
                count += 1

        except csv.Error as e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
    return [x, f2v, nvert, nface]

def add_perturbation(x, eps):
    x = np.array(x)
    x = x - x.mean(0)

    (__, __, axes) = calc_moment_inertia_tensor(x)
    # rotate mesh by eigenvectors
    x_prime = np.matmul(x, axes)

    span = np.amax(x_prime[:, 0]) - np.amin(x_prime[:, 0])
    r = np.sqrt(np.square(x_prime[:, 1]) + np.square(x_prime[:, 2]))
    #   add perturbation
    x_prime[:, 1] += eps * np.sin(2*np.pi*x_prime[:, 0]/span) * x_prime[:, 1]/r
    x_prime[:, 2] += eps * np.sin(2*np.pi*x_prime[:, 0]/span) * x_prime[:, 2]/r

    x = np.matmul(x_prime, axes.T)
    return x

def calc_moment_inertia_tensor(x):
    (nvert, __) = x.shape
    inertia_tensor = np.zeros((3, 3))
    delta_ij = np.identity(3)
    for i in range(0, nvert):
        r_vec = x[i, :]
        inertia_tensor += np.dot(r_vec, r_vec) * delta_ij - np.outer(r_vec, r_vec)
    [eigvals, eigvecs] = np.linalg.eig(inertia_tensor)
    idx = eigvals.argsort()
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    if (eigvecs[0, 0] < 0):
        eigvecs[:, 0] = -eigvecs[:, 0]
    temp = np.cross(eigvecs[:, 0], eigvecs[:, 1])
    if (np.dot(temp.T, eigvecs[:, 2]) < 0):
        eigvecs[:, 2] = -eigvecs[:, 2]

    return (inertia_tensor, eigvals, eigvecs)

def write_data(x, f2v, filename):
    nvert = np.size(x[:, 0])
    nface = np.size(f2v[:, 0])
    with open(filename, 'wb') as out:
        writer = csv.writer(out, delimiter=' ')
        out.write("# TIME=0.000000\r\nVARIABLES = X, Y, Z\r\nZONE N=%s E=%s F=FEPOINT ET=TRIANGLE\r\n"
            % (nvert, nface))
        writer.writerows(x)
        writer.writerows(f2v)

def main():
    # pass three arguments inFile, perturbation strength (eps), outFile
    inFile = sys.argv[1]
    eps = float(sys.argv[2])
    outFile = sys.argv[3]
    [x, f2v, _nvert, _nface] = read_data(inFile)
    x = add_perturbation(x, eps)
    f2v = np.array(f2v).astype(int)
    write_data(x, f2v, outFile)

if __name__ == "__main__":
    main()
