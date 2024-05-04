import cv2
import numpy as np


# find the x and y coordinates of the center of a red object in the image
def center_of_red(img: np.ndarray) -> (int, int):
    if img is None:
        return None, None

    # blurring helps reduce noise that might confuse the algorithm
    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    # converting to HSV (Hue, Saturation, Value) makes it easier to identify a range
    # of possible red values
    img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

    #  lower_red1 = np.array([0, 80, 80])
    #  upper_red1 = np.array([10, 255, 255])

    #  lower_red2 = np.array([170, 80, 80])
    #  upper_red2 = np.array([180, 255, 255])

    #  red_mask1 = cv2.inRange(img_hsv, lower_red1, upper_red1)
    #  red_mask2 = cv2.inRange(img_hsv, lower_red2, upper_red2)

    #  red_mask = red_mask1 + red_mask2

    lower_red = np.array([0, 10, 10])
    upper_red = np.array([30, 255, 150])
    red_mask = cv2.inRange(img_hsv, lower_red, upper_red)

    # turn all parts of the image that aren't red into black
    red_img = cv2.cvtColor(
        cv2.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv2.COLOR_HSV2BGR
    )
    cv2.imshow("Red Image", red_img)

    # turn the image into a binary (black and white) image, where the white parts
    # represent anything red, and the black parts represent anything not red
    gray_img = cv2.cvtColor(red_img, cv2.COLOR_BGR2GRAY)
    ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    if len(contours) <= 0:
        return None, None

    largest_contour = max(contours, key=cv2.contourArea)
    moment = cv2.moments(largest_contour)
    if moment["m00"] == 0:
        return None, None

    x_coord = int(moment["m10"] / moment["m00"])
    y_coord = int(moment["m01"] / moment["m00"])
    return x_coord, y_coord


def main():
    #  vc = cv2.VideoCapture(0)

    # problem images: 5, 8, 9, 12
    img = cv2.imread("coral_images/red_square8.png")
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
