import cv2 as cv
import numpy as np

img = cv.imread("image.jpg")

img_blur = cv.blur(img, (6, 6))
img_hsv = cv.cvtColor(img_blur, cv.COLOR_BGR2HSV)

# lower threshold of blue
lower = np.array([175, 25, 25])
upper = np.array([260, 255, 255])
#  gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
cv.imshow("Blurred", img_hsv)

cv.waitKey(0)
cv.destroyAllWindows()

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
