import cv2 as cv
import numpy as np

def main():
    # img = cv.imread("image.jpg")

    vc = cv.VideoCapture(0)

    if vc.isOpened():
        ok, frame = vc.read()
    else:
        ok = False


    while ok:
        ok, img = vc.read()
        key = cv.waitKey(20)
        if key == 27:  # exit on ESC
            break

        img_blur = cv.GaussianBlur(img, (9, 9), 0)
        img_blur = cv.bilateralFilter(img_blur, 9, 75, 75)
        img_blur = img
        img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        red_mask1 = cv.inRange(img_hsv, lower_red1, upper_red1)
        red_mask2 = cv.inRange(img_hsv, lower_red2, upper_red2)

        red_mask = red_mask1 + red_mask2

        output_img = cv.cvtColor(cv.bitwise_and(img_hsv, img_hsv, mask=red_mask), cv.COLOR_HSV2BGR)

        cv.imshow("Red", output_img)

    cv.waitKey(0)
    cv.destroyAllWindows()
    vc.release()

#  # convert the grayscale image to binary (black and white) image
#  ok, thresh = cv.threshold(gray_image, 127, 255, 0)
#  im2, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

#  for contour in contours:
#      M = cv.moments(contour)

#      # calculate x, y coordinate of center
#      x_coord = int(M["m10"] / M["m00"])
#      y_coord = int(M["m01"] / M["m00"])
#      cv.circle(img, (x_coord, y_coord), 5, (255, 255, 255), -1)
#      cv.putText(
#          img,
#          "centroid",
#          (x_coord - 25, y_coord - 25),
#          cv.FONT_HERSHEY_SIMPLEX,
#          0.5,
#          (255, 255, 255),
#          2,
#      )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()
