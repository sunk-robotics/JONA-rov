import numpy as np
from math import atan2, acos, cos, hypot, sin


# converts vector in cartesian coordinates (x, y, z) to spherical coordinates (r, θ, ϕ)
def cartesian_to_spherical(vector: tuple) -> tuple:
    x, y, z = vector
    r = hypot(x, y, z)
    theta = atan2(y, x)  # also known as the azimuth
    phi = acos(z / r) if r != 0 else acos(0)  # also known as the inclination
    return r, theta, phi


# converts vector in spherical coordinates (r, θ, ϕ) to cartesian coordinates (x, y, z)
def spherical_to_cartesian(vector: tuple) -> tuple:
    r, theta, phi = vector

    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)

    return x, y, z


# rotates a vector supplied in cartesian (x, y, z) coordinates by specified Euler angles
def rotate_vector(vector: tuple, yaw: float, pitch: float, roll: float) -> tuple:
    a = -yaw
    b = -pitch
    c = -roll

    vector = np.array([[vector[0]], [vector[1]], [vector[2]]])

    rotation_matrix = np.matrix(
        [
            [
                cos(a) * cos(b),
                cos(a) * sin(b) * sin(c) - sin(a) * cos(c),
                cos(a) * sin(b) * cos(c) + sin(a) * sin(c),
            ],
            [
                sin(a) * cos(b),
                sin(a) * sin(b) * sin(c) + cos(a) * cos(c),
                sin(a) * sin(b) * cos(c) - cos(a) * sin(c),
            ],
            [-sin(b), cos(b) * sin(c), cos(b) * cos(c)],
        ]
    )

    rotated_vector = np.matmul(rotation_matrix, vector).A1
    return (
        round(rotated_vector[0], 4),
        round(rotated_vector[1], 4),
        round(rotated_vector[2], 4),
    )


# rotates a vector supplied in spherical (r, θ, ϕ) coordinates by specified Euler angles
def rotate_vector_spherical(
    vector: tuple, yaw: float, pitch: float, roll: float
) -> tuple:
    a = -yaw
    b = -pitch
    c = -roll

    cartesian = spherical_to_cartesian(vector)
    vector = np.array([[cartesian[0]], [cartesian[1]], [cartesian[2]]])

    rotation_matrix = np.matrix(
        [
            [
                cos(a) * cos(b),
                cos(a) * sin(b) * sin(c) - sin(a) * cos(c),
                cos(a) * sin(b) * cos(c) + sin(a) * sin(c),
            ],
            [
                sin(a) * cos(b),
                sin(a) * sin(b) * sin(c) + cos(a) * cos(c),
                sin(a) * sin(b) * cos(c) - cos(a) * sin(c),
            ],
            [-sin(b), cos(b) * sin(c), cos(b) * cos(c)],
        ]
    )

    rotated_vector = np.matmul(rotation_matrix, vector).A1
    return cartesian_to_spherical(
        (rotated_vector[0], rotated_vector[1], rotated_vector[2])
    )
