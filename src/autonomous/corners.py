import cv2
import numpy as np
import imutils


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
        img_blur = cv2.GaussianBlur(img_blur, (9, 9), 0)
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
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

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
            cv2.imshow("Corners", img)
            continue
        # draw white filled largest contour on black just as a check to see it got the correct region
        page = np.zeros_like(img)
        cv2.drawContours(page, [big_contour], 0, (255, 255, 255), -1)

        # get perimeter and approximate a polygon
        peri = cv2.arcLength(big_contour, True)
        corners = cv2.approxPolyDP(big_contour, 0.04 * peri, True)

        # draw polygon on input image from detected corners
        polygon = img.copy()
        cv2.polylines(polygon, [corners], True, (0, 0, 255), 1, cv2.LINE_AA)
        # Alternate: cv2.drawContours(page,[corners],0,(0,0,255),1)

        # print the number of found corners and the corner coordinates
        # They seem to be listed counter-clockwise from the top most corner
        print(len(corners))
        print(corners)

        if len(corners) < 4:
            cv2.imshow("Corners", img)
            continue

        # for simplicity get average of top/bottom side widths and average of left/right side heights
        # note: probably better to get average of horizontal lengths and of vertical lengths
        width = 0.5 * (
            (corners[0][0][0] - corners[1][0][0])
            + (corners[3][0][0] - corners[2][0][0])
        )
        height = 0.5 * (
            (corners[2][0][1] - corners[1][0][1])
            + (corners[3][0][1] - corners[0][0][1])
        )
        width = np.int0(width)
        height = np.int0(height)

        # reformat input corners to x,y list
        icorners = []
        for corner in corners:
            pt = [corner[0][0], corner[0][1]]
            icorners.append(pt)
        icorners = np.float32(icorners)

        # get corresponding output corners from width and height
        ocorners = [[width, 0], [0, 0], [0, height], [width, height]]
        ocorners = np.float32(ocorners)

        if corners is not None:
            for corner in corners:
                x, y = (int(corner[0][0]), int(corner[0][1]))
                cv2.circle(img, (x, y), 5, (255, 255, 255), -1)

        cv2.imshow("Corners", img)

        # get perspective tranformation matrix
        #  M = cv2.getPerspectiveTransform(icorners, ocorners)

        # do perspective
        #  warped = cv2.warpPerspective(img, M, (width, height))

        # write results
        #  cv2.imwrite("efile_thresh.jpg", thresh)
        #  cv2.imwrite("efile_morph.jpg", morph)
        #  cv2.imwrite("efile_polygon.jpg", polygon)
        #  cv2.imwrite("efile_warped.jpg", warped)

        # display it
        #  cv2.imshow("efile_thresh", thresh)
        #  cv2.imshow("efile_morph", morph)
        #  cv2.imshow("efile_page", page)
        #  cv2.imshow("efile_polygon", polygon)
        #  cv2.imshow("efile_warped", warped)

        #  canny = cv2.Canny(gray, 120, 255, 1)

        #  lines = cv2.HoughLinesP(
        #      canny, 1, np.pi / 180, 40, minLineLength=50, maxLineGap=50
        #  )

        #  if lines is not None:
        #      print(len(lines))
        #      for line in lines:
        #          x1, y1, x2, y2 = line[0]
        #          cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        #  cv2.imshow("Corners", img)
        #  canny = cv2.Canny(gray, 120, 255, 1)

        #  corners = cv2.goodFeaturesToTrack(canny, 4, 0.8, 400)

        #  if corners is not None:
        #      for corner in corners:
        #          x, y = (int(corner[0][0]), int(corner[0][1]))
        #          cv2.circle(img, (x, y), 5, (255, 255, 255), -1)

        #  cv2.imshow("Corners", img)
        #  dst = cv2.cornerHarris(gray, 2, 3, 0.04)

        #  mask = np.zeros_like(gray)
        #  mask[dst > 0.01 * dst.max()] = 255

        #  coords = np.argwhere(mask)

        #  coor_list = [l.tolist() for l in list(coords)]
        #  coor_tuples = [tuple(l) for l in coor_list]

        #  coor_tuples_copy = coor_tuples
        #  i = 1
        #  for point1 in coor_tuples

    cv2.destroyAllWindows()
    vc.release()

    #  size = img.shape

    #  edged = cv2.Canny(gray, 35, 125)
    #  # find the contours in the edged image and keep the largest one;
    #  # we'll assume that this is our piece of paper in the image
    #  cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    #  cnts = imutils.grab_contours(cnts)
    #  if cnts == ():
    #      return None
    #  c = max(cnts, key=cv2.contourArea)
    #  # compute the bounding box of the of the paper region and return it
    #  return cv2.minAreaRect(c)


if __name__ == "__main__":
    main()
