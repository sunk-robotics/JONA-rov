from imutils import paths
import numpy as np
import imutils
import cv2


def find_marker(image):
    # converting to HSV (Hue, Saturation, Value) makes it easier to identify a range
    # of possible red values
    #  img_blur = cv2.GaussianBlur(image, (7, 7), 0)
    img_blur = image
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
    edged = cv2.Canny(gray, 35, 125)
    # find the contours in the edged image and keep the largest one;
    # we'll assume that this is our piece of paper in the image
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if cnts == ():
        return None
    c = max(cnts, key=cv2.contourArea)
    # compute the bounding box of the of the paper region and return it
    return cv2.minAreaRect(c)


def distance_to_camera(knownWidth, focalLength, perWidth):
    # compute and return the distance from the maker to the camera
    if perWidth == 0:
        return 0
    return (knownWidth * focalLength) / perWidth


def main():
    # initialize the known distance from the camera to the object, which
    # in this case is 24 inches
    KNOWN_DISTANCE = 30.0
    # initialize the known object width, which in this case, the piece of
    # paper is 12 inches wide
    KNOWN_WIDTH = 5.1
    # load the furst image that contains an object that is KNOWN TO BE 2 feet
    # from our camera, then find the paper marker in the image, and initialize
    # the focal length
    image = cv2.imread("images/calibration2.jpg")
    marker = find_marker(image)
    focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH

    print(focalLength)

    # loop over the images

    vc = cv2.VideoCapture(0)

    if vc.isOpened():
        ok, img = vc.read()
    else:
        ok = False

    while ok:
        ok, image = vc.read()

        key = cv2.waitKey(20)
        if key == 27:  # exit on ESC
            break

        #  for imagePath in sorted(paths.list_images("images")):
        # load the image, find the marker in the image, then compute the
        # distance to the marker from the camera
        #  image = cv2.imread(imagePath)
        marker = find_marker(image)
        if marker is None:
            cv2.imshow("image", image)
            continue
        inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
        print(inches)
        # draw a bounding box around the image and display it
        box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
        box = np.int0(box)
        cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
        cv2.putText(
            image,
            "%.1fin" % (inches),
            (image.shape[1] - 200, image.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            2.0,
            (0, 255, 0),
            3,
        )
        cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
