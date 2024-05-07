# TODO - Filter out contours by size (exclude contours that are too big or too small),
# maximum perimeter to area ratio, and maybe by shape
import cv2
import math
import numpy as np
from scipy.interpolate import splprep, splev


def smooth_contour(contour: np.ndarray) -> np.ndarray:
    x, y = contour.T
    x = x.tolist()[0]
    y = y.tolist()[0]
    tck, u = splprep([x, y], u=None, s=1.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 100)
    x_new, y_new = splev(u_new, tck, der=0)
    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
    return np.asarray(res_array, dtype=np.int32)


# Remove the horkfook from the image, which often interferes with the image
# segmentation algorithm. Image must be HSV (Hue, Saturation, Value).
def filter_out_hork(img: np.ndarray) -> np.ndarray:
    lower_orange = np.array([13, 10, 10])
    upper_orange = np.array([35, 255, 255])
    orange_mask = cv2.inRange(img, lower_orange, upper_orange)
    # turn all parts of the image that aren't orange into black
    orange_img = cv2.bitwise_and(img, img, mask=orange_mask)
    gray_img = cv2.split(orange_img)[2]
    ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)
    #  cv2.imshow("Thresh", thresh)
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    #  cv2.imshow("Thresh2", thresh)

    # find the contours of the two hooks
    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    hook_contours = sorted(contours, key=cv2.contourArea, reverse=True)[0:2]
    if len(hook_contours) < 2:
        print("Unable to filter out hork!")
        return img
    smoothened_contours = [
        smooth_contour(hook_contours[0]),
        smooth_contour(hook_contours[1]),
    ]

    mask = np.zeros_like(thresh)
    cv2.drawContours(mask, smoothened_contours, -1, 255, -1)
    # dilate the mask to remove the pixels around the edges of the hooks that
    # like to cause problems
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)
    cv2.imshow("Mask", mask)
    cv2.bitwise_not(mask, mask)

    return cv2.bitwise_and(img, img, mask=mask)


def filter_contours(contours: np.ndarray, iter_num: int) -> bool:
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        _, _, width, height = cv2.boundingRect(contour)
        aspect_ratio = width / height if height != 0 else math.inf

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        solidity = area / hull_area if hull_area != 0 else math.inf

        if (
            area > 100 / (iter_num + 1)
            and area < 10_000 / (iter_num + 1)
            and aspect_ratio > 0.8
            and solidity > 0.5
        ):
            filtered_contours.append(contour)

    return filtered_contours


# find the x and y coordinates of the center of a red object in the image
def center_of_red(img: np.ndarray) -> (int, int):
    if img is None:
        return None, None

    # blurring helps reduce noise that might confuse the algorithm
    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    # crop out part of the top, left, and right sides of the image to remove
    # interference from reflections and other irrelevant parts of the image
    img_width = img.shape[1]
    img_height = img.shape[0]
    mask = np.zeros(img.shape[:2], dtype="uint8")

    cv2.rectangle(
        mask,
        (int(img_width / 5), int(img_height / 4)),
        (int(img_width * (4 / 5)), img_height),
        255,
        -1,
    )
    cropped_img = cv2.bitwise_and(img_blur, img_blur, mask=mask)

    # converting to HSV (Hue, Saturation, Value) makes it easier to identify a range
    # of possibcv2.imshow('mask', mask)le red values
    img_hsv = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)

    largest_contour = None
    # red light attenuates very quickly underwater, so the farther the ROV is
    # away from the square, the grayer/browner the square becomes, so gradually
    # increase the range of colors until the square can be found
    for i in range(0, 7):
        filter_img = filter_out_hork(img_hsv) if i > 3 else img_hsv
        lower_red = np.array([0, 10, 10])
        upper_red = np.array([i * 5 + 10, 255, 150])
        red_mask = cv2.inRange(filter_img, lower_red, upper_red)

        cv2.imshow("Horkless Image", cv2.cvtColor(filter_img, cv2.COLOR_HSV2BGR))
        # turn all parts of the image that aren't red into black
        red_img = cv2.bitwise_and(filter_img, filter_img, mask=red_mask)
        cv2.imshow("Red Image", cv2.cvtColor(red_img, cv2.COLOR_HSV2BGR))

        # turn the image into a binary (black and white) image, where the white parts
        # represent anything red, and the black parts represent anything not red
        gray_img = cv2.split(red_img)[2]
        #  gray_img = cv2.equalizeHist(gray_img)
        #  cv2.imshow("Equalized Image", cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR))
        ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)
            print(f"Contour Area: {area}")

            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h != 0 else math.inf
            print(f"Aspect Ratio: {aspect_ratio}")

            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)

            solidity = area / hull_area if hull_area != 0 else math.inf

            print(f"Solidity: {solidity}")

        # filter out any contours that don't match the shape of the square
        filtered_contours = filter_contours(contours, i)

        if len(filtered_contours) > 0:
            largest_contour = max(filtered_contours, key=cv2.contourArea)
            break

    if largest_contour is None:
        return None, None

    moment = cv2.moments(largest_contour)
    if moment["m00"] == 0:
        print("shit")
        return None, None

    x_coord = int(moment["m10"] / moment["m00"])
    y_coord = int(moment["m01"] / moment["m00"])
    return x_coord, y_coord


def main():
    #  vc = cv2.VideoCapture(0)

    # problem images: 5, 8, 9, 12
    img = cv2.imread("coral_images/red_square1.png")

    x_coord, y_coord = center_of_red(img)
    if x_coord is not None and y_coord is not None:
        cv2.circle(img, (x_coord, y_coord), 5, (255, 255, 255), -1)
        cv2.putText(
            img,
            "Centroid",
            (x_coord - 25, y_coord - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
    else:
        print("Unable to find red square!")

    cv2.imshow("Center of Red Square", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #  if vc.isOpened():
    #      ok, frame = vc.read()
    #  else:
    #      ok = False

    #  while ok:
    #      ok, img = vc.read()
    #      key = cv2.waitKey(20)
    #      if key == 27:  # exit on ESC
    #          break

    #      (x_coord, y_coord) = center_of_red(img)
    #      if x_coord is not None and y_coord is not None:
    #          cv2.circle(img, (x_coord, y_coord), 5, (255, 255, 255), -1)
    #          cv2.putText(
    #              img,
    #              "Centroid",
    #              (x_coord - 25, y_coord - 25),
    #              cv2.FONT_HERSHEY_SIMPLEX,
    #              0.5,
    #              (255, 255, 255),
    #              2,
    #          )
    #          img_height, img_width = img.shape[:2]
    #          img_center_x = img_width / 2
    #          img_center_y = img_height / 2

    #          x_error = img_center_x - x_coord
    #          y_error = img_center_y - y_coord

    #          print(f"X Error: {x_error}, Y Error: {y_error}")

    #      cv2.imshow("Center of Red Square", img)

    #  cv2.destroyAllWindows()
    #  vc.release()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
