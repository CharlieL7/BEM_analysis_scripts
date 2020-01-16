import math
import numpy as np

def int_over_tri(func, nodes):
    """
    Integrate a function over a triangle surface using Gaussian quadrature.
    Seven point quadrature.

    Parameters:
        func : function to integrate, can return any order tensor
               expecting f(eta, xi)
    Returns:
        integrated function
    """

    # Gaussian quadrature weights
    w = 1./60. * np.array([3., 8., 3., 8., 3., 8., 27.])

    # Gaussian quadrature points
    f1 = func(0.0, 0.0)
    f2 = func(0.5, 0.0)
    f3 = func(1.0, 0.0)
    f4 = func(0.5, 0.5)
    f5 = func(0.0, 1.0)
    f6 = func(0.0, 0.5)
    f7 = func(1.0/3.0, 1.0/3.0)

    # metric function for surface area
    n = np.cross(nodes[1] - nodes[0], nodes[2] - nodes[0])
    h = np.linalg.norm(n)

    ret = f1 * w[0] + f2 * w[1] + f3 * w[2] + f4 * w[3] + f5 * w[4] + f6 * w[5] + f7 * w[6]
    ret *= 0.5 * h
    return ret
