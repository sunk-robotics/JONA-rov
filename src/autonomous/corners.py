import cv2
import numpy as np
import imutils
from scipy.interpolate import splprep, splev


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

    return corners


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
        #  points_3D = np.array(
        #      [(0, 0, 0), (8.5, 0, 0), (0, 11, 0), (8.5, 11, 0)], dtype="single"
        #  )

        img_blur = cv2.GaussianBlur(img, (9, 9), 0)
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
        thresh = cv2.threshold(
            filtered_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )[1]

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

        if big_contour is not None:
            # simplify the shape of the contour to a quadrilateral
            quad_contour = simplify_contour(big_contour)
        else:
            cv2.imshow("Corners", img)
            continue

        # draw white filled largest contour on black just as a check to see it got the correct region
        #  contour_img = np.zeros_like(img)
        #  cv2.drawContours(contour_img, [big_contour], 0, (255, 255, 255), -1)
        #  cv2.imshow("Contour", contour_img)

        #  quad_contour_img = np.zeros_like(img)
        #  cv2.drawContours(quad_contour_img, [quad_contour], 0, (255, 255, 255), -1)
        #  cv2.imshow("Quadrilateral Contour", quad_contour_img)

        # get perimeter and approximate a polygon
        peri = cv2.arcLength(quad_contour, True)
        corners = cv2.approxPolyDP(quad_contour, 0.02 * peri, True)

        # print the number of found corners and the corner coordinates
        # They seem to be listed counter-clockwise from the top most corner
        print(len(corners))
        print(corners)

        if len(corners) >= 4:
            for corner in corners:
                x, y = (int(corner[0][0]), int(corner[0][1]))
                cv2.circle(img, (x, y), 5, (255, 255, 255), -1)

        cv2.imshow("Corners", img)

    cv2.destroyAllWindows()
    vc.release()


if __name__ == "__main__":
    main()
