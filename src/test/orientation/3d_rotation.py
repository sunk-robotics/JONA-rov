import numpy as np
from math import cos
from math import sin
from math import pi as PI


def magnitude(vector: tuple) -> float:
    return (vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2) ** 0.5


def rotate_vector(vector: tuple, yaw, pitch, roll) -> tuple:
    a = -yaw
    b = -pitch
    c = -roll

    vector = np.array([
        [vector[0]],
        [vector[1]],
        [vector[2]]
    ])

    #  rotation_matrix = np.matrix(
    #      [
    #          [cos(b)*cos(c), sin(a)*sin(b)*cos(c) - cos(a)*sin(c), cos(a)*sin(b)*cos(c) + sin(a)*sin(c)],
    #          [cos(b)*cos(c), sin(a)*sin(b)*sin(c) + cos(a)*cos(c), cos(a)*cos(b)*sin(c) - sin(a)*cos(c)],
    #          [-sin(b), sin(a)*cos(b), cos(a)*cos(b)]
    #      ]
    #  )
    rotation_matrix = np.matrix(
        [
            [cos(a)*cos(b), cos(a)*sin(b)*sin(c) - sin(a)*cos(c), cos(a)*sin(b)*cos(c) + sin(a)*sin(c)],
            [sin(a)*cos(b), sin(a)*sin(b)*sin(c) + cos(a)*cos(c), sin(a)*sin(b)*cos(c) - cos(a)*sin(c)],
            [-sin(b), cos(b)*sin(c), cos(b)*cos(c)]
        ]
    )

    rotated_vector = np.matmul(rotation_matrix, vector).A1
    return (
        round(rotated_vector[0], 4),
        round(rotated_vector[1], 4),
        round(rotated_vector[2], 4)
    )


def main():
    yaw = PI / 4
    pitch = PI / 4
    roll = PI / 4

    vector = (1, 1, 1)

    rotated_vector = rotate_vector(vector, yaw, pitch, roll)

    print(rotated_vector)
    print(magnitude(rotated_vector))


if __name__ == "__main__":
    main()
