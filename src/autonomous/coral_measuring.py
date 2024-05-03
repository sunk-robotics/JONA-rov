import cv2
import numpy as np


def main():
    img = cv2.imread("coral_images/coral_measuring1.png")

    img_blur = cv2.GaussianBlur(img, (9, 9), 0)

    lower_orange = np.array([0, 0, 0])
    upper_orange = np.array([0, 0, 0])
    gray_img = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    ok, thresh = cv2.threshold(gray_img, 1, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(img, contours, -1, (0, 255, 0))
    cv2.imshow("Contours!", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
