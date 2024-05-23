import cv2
import math
import numpy as np
from scipy.interpolate import splprep, splev

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
img = None
refPt = []


def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(refPt) == 0 or len(refPt) >= 2:
            refPt = [(x, y)]
        else:
            refPt.append((x, y))
            clone = img.copy()
            cv2.rectangle(clone, refPt[0], refPt[1], (0, 0, 255), 2)
            cv2.imshow("Cropped", clone)


def smooth_contour(contour: np.ndarray) -> np.ndarray:
    x, y = contour.T
    x = x.tolist()[0]
    y = y.tolist()[0]
    tck, u = splprep([x, y], u=None, s=1.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 100)
    x_new, y_new = splev(u_new, tck, der=0)
    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
    return np.asarray(res_array, dtype=np.int32)


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
            and area < 20_000 / (iter_num + 1)
            and aspect_ratio > 0.8
            and solidity > 0.5
        ):
            filtered_contours.append(contour)

    return filtered_contours


# find the x and y coordinates of the center of a red object in the image
def get_contour(img: np.ndarray) -> (int, int):
    if img is None:
        return None, None

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Gray Image", gray_img)
    # blurring helps reduce noise that might confuse the algorithm
    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    # crop out part of the top, left, and right sides of the image to remove
    # interference from reflections and other irrelevant parts of the image
    img_width = img.shape[1]
    img_height = img.shape[0]
    mask = np.zeros(img.shape[:2], dtype="uint8")

    cv2.rectangle(
        mask,
        (0, int(img_height / 6)),
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
    for i in range(0, 5):
        filter_img = img_hsv
        lower_red = np.array([0, 10, 10])
        upper_red = np.array([i * 5 + 10, 255, 150])
        red_mask = cv2.inRange(filter_img, lower_red, upper_red)

        # turn all parts of the image that aren't red into black
        red_img = cv2.bitwise_and(filter_img, filter_img, mask=red_mask)
        cv2.imshow("Red Image", cv2.cvtColor(red_img, cv2.COLOR_HSV2BGR))

        # turn the image into a binary (black and white) image, where the white parts
        # represent anything red, and the black parts represent anything not red
        gray_img = cv2.split(red_img)[2]
        #  gray_img = cv2.equalizeHist(gray_img)
        #  cv2.imshow("Equalized Image", cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR))
        ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)
        thresh = cv2.morphologyEx(
            thresh, cv2.MORPH_DILATE, np.ones((7, 7), np.uint8), iterations=4
        )

        contours, hierarchy = cv2.findContours(
            thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        #  for contour in contours:
        #      area = cv2.contourArea(contour)
        #      print(f"Contour Area: {area}")

        #      x, y, w, h = cv2.boundingRect(contour)
        #      aspect_ratio = w / h if h != 0 else math.inf
        #      print(f"Aspect Ratio: {aspect_ratio}")

        #      hull = cv2.convexHull(contour)
        #      hull_area = cv2.contourArea(hull)

        #      solidity = area / hull_area if hull_area != 0 else math.inf

        #      print(f"Solidity: {solidity}")

        # filter out any contours that don't match the shape of the square
        filtered_contours = filter_contours(contours, i)

        if len(filtered_contours) > 0:
            largest_contour = max(filtered_contours, key=cv2.contourArea)
            break

    return largest_contour


def main():
    global img, refPt
    i = 1
    while i < 513:
        print(f"Image Number: {i}")
        refPt = []
        img = cv2.imread(f"train/images/color_image{i:03}.jpg")

        img_width = img.shape[1]
        img_height = img.shape[0]

        contour = get_contour(img)
        x, y, w, h = cv2.boundingRect(contour)
        middle_x = x + w / 2
        middle_y = y + h / 2

        normalized_x = middle_x / img_width
        normalized_y = middle_y / img_height

        normalized_width = w / img_width
        normalized_height = h / img_height

        label = (
            f"0 {normalized_x} {normalized_y} {normalized_width} {normalized_height}"
        )

        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.imshow("Image", img)

        cv2.setMouseCallback("Image", click_and_crop)

        key = cv2.waitKey(0) & 0xFF

        # if the 'n' key is pressed, move on to the next image
        if key == ord("n"):
            print(len(refPt))
            if len(refPt) == 2:
                x1, y1 = refPt[0]
                x2, y2 = refPt[1]
                w = abs(x2 - x1)
                h = abs(y2 - y1)

                middle_x = (x1 + x2) / 2
                middle_y = (y1 + y2) / 2
                print(middle_y)

                normalized_x = middle_x / img_width
                normalized_y = middle_y / img_height

                normalized_width = w / img_width
                normalized_height = h / img_height

                label = f"0 {normalized_x} {normalized_y} {normalized_width} {normalized_height}"

            cv2.imwrite(f"train/images/image{i}.jpg", gray_img)
            print(f"Label: {label}")
            with open(f"train/labels/image{i}.txt", "w") as f:
                f.writelines(label)
            i += 1
            continue

        elif key == ord("b"):
            print("Going back to last image")
            i -= 1
            continue
        elif key == ord("q"):
            print("Qutting!")
            break
        elif key == ord("d"):
            print("No red square! Moving onto next image")
            i += 1
            continue

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
