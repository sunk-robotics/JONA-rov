import cv2
import numpy as np
import math


def simplify_contour(contour, n_corners=4):
    """
    Binary searches best `epsilon` value to force contour
        approximation contain exactly `n_corners` points.

    :param contour: OpenCV2 contour.
    :param n_corners: Number of corners (points) the contour must contain.

    :returns: Simplified contour in successful case. Otherwise returns initial contour.
    """
    n_iter, max_iter = 0, 100
    lb, ub = 0.0, 1.0

    while True:
        n_iter += 1
        if n_iter > max_iter:
            return contour

        k = (lb + ub) / 2.0
        eps = k * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, eps, True)

        if len(approx) > n_corners:
            lb = (lb + ub) / 2.0
        elif len(approx) < n_corners:
            ub = (lb + ub) / 2.0
        else:
            return approx


# gets the coordinates of the four corners of the largest red square in an image
# returns None if corners can't be found
def find_corners(image):
    img_blur = cv2.GaussianBlur(image, (9, 9), 0)
    img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 80, 80])
    upper_red2 = np.array([180, 255, 255])

    red_mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)

    red_mask = red_mask1 + red_mask2

    # turn all parts of the image that aren't red into black
    red_img = cv2.cvtColor(
        cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv2.COLOR_HSV2BGR
    )

    gray = cv2.cvtColor(red_img, cv2.COLOR_BGR2GRAY)
    # filter to remove noise from the edges that can result in the contours becoming
    # jagged
    filtered_gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # turn image into a binary (black and white) image
    thresh = cv2.threshold(filtered_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[
        1
    ]

    # apply morphology
    kernel = np.ones((7, 7), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

    # get largest contour
    contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    area_thresh = 0
    big_contour = None
    for c in contours:
        area = cv2.contourArea(c)
        if area > area_thresh:
            area_thresh = area
            big_contour = c

    if big_contour is None:
        return None
    # simplify the shape of the contour to a quadrilateral
    quad_contour = simplify_contour(big_contour)
    # get perimeter and approximate a polygon
    peri = cv2.arcLength(quad_contour, True)
    corners = cv2.approxPolyDP(quad_contour, 0.02 * peri, True)

    if len(corners) != 4:
        return None

    corners = np.resize(corners, (4, 2))
    print(f"Corners: {corners}")
    keys = (corners[:, 0], corners[:, 1])

    # Indices for sorted array
    sorted_indices = np.lexsort(keys)

    # Apply array indexing to obtain sorted array
    corners = corners[sorted_indices]

    top_corners = corners[0:2]
    keys = (top_corners[:, 1], top_corners[:, 0])
    sorted_indices = np.lexsort(keys)
    top_corners = top_corners[sorted_indices]

    bottom_corners = corners[2:4]
    keys = (bottom_corners[:, 1], bottom_corners[:, 0])
    sorted_indices = np.lexsort(keys)
    bottom_corners = bottom_corners[sorted_indices]

    corners = np.append(top_corners, bottom_corners, axis=0)

    print(f"Sorted Corners: {corners}")

    return corners.astype(np.float32)


def main():
    vc = cv2.VideoCapture(2)

    if vc.isOpened():
        ok, frame = vc.read()
    else:
        ok = False

    while ok:
        ok, img = vc.read()
        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

        camera_matrix = np.array(
            [
                (2.1484589086606215e03, 0, 8.8823443046428349e02),
                (0, 2.1553101552978601e03, 6.1716956646878486e02),
                (0, 0, 1),
            ]
        )
        #  dist_coeffs = np.array(
        #      [
        #          (
        #              -0.81642321343572366,
        #              1.5568737137734159,
        #              -0.0042440573440693579,
        #              -0.0022688996764112274,
        #              -2.1523633613219233,
        #          )
        #      ]
        #  )
        dist_coeffs = np.zeros((4, 1))
        points_3d = np.array(
            [[-3, -2.125, 0], [3, -2.125, 0], [-3, 2.125, 0], [3, 2.125, 0]]
        )
        #  points_3d = np.array([(0, 0, 0), (0, 6, 0), (4.25, 6, 0), (4.25, 0, 0)])
        points_2d = find_corners(img)
        #  print(f"Points: {points_2d}")
        #  if points_2d is not None:
        #      print(f"Points Sorted: {np.sort(points_2d, axis=0)}")
        #  points_3d = np.array(
        #      [
        #          (0.0, 0.0, 0.0),  # Nose tip
        #          (0.0, -330.0, -65.0),  # Chin
        #          (-225.0, 170.0, -135.0),  # Left eye corner
        #          (225.0, 170.0, -135.0),  # Right eye corner
        #          #  (-150.0, -150.0, -125.0),  # Left mouth
        #          #  (150.0, -150.0, -125.0),  # Right mouth
        #      ]
        #  )

        if points_2d is not None:
            ok, rotation_vec, translation_vec = cv2.solvePnP(
                points_3d, points_2d, camera_matrix, dist_coeffs
            )
            print(translation_vec)
            dist_from_cam = math.hypot(
                translation_vec[0], translation_vec[1], translation_vec[2]
            )
            print(dist_from_cam)

        #  if points_2d is not None:
        #      for i in range(len(points_2d)):
        #          point = points_2d[i]
        #          x, y = (int(point[0][0]), int(point[0][1]))
        #          cv2.circle(img, (x, y), 5, (i * 64 - 1, i * 64 - 1, 0), -1)

        cv2.imshow("Corners", img)


if __name__ == "__main__":
    main()
