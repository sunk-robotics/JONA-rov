#!/usr/bin/env python
import cv2
import glob
import numpy as np
import os

# Inputs
num_squares_x = 8  # Number of chessboard squares along the x-axis
num_squares_y = 10  # Number of chessboard squares along the y-axis
num_interior_corners_x = num_squares_x - 1  # Number of interior corners along x-axis
num_interior_corners_y = num_squares_y - 1  # Number of interior corners along y-axis
checker_width = 0.020  # Checker width (in meters)
path = "calibration_images/"  # Path where all images are stored


def calibrate():
    # Set termination criteria: stop when certain number of iterations are completed or when certain accuracy is achieved.
    termination_criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001,
    )

    # Define real world coordinates for points in the 3D coordinate frame
    object_points_3D = np.zeros(
        (num_interior_corners_x * num_interior_corners_y, 3), np.float32
    )
    object_points_3D[:, :2] = np.mgrid[
        0:num_interior_corners_y, 0:num_interior_corners_x
    ].T.reshape(-1, 2)
    object_points_3D = object_points_3D * checker_width

    object_points = (
        []
    )  # to store 3D points for all chessboard images (world coordinate frame)
    image_points = (
        []
    )  # to store 2D points for all chessboard images (camera coordinate frame)

    # Get the file paths for all images
    images = glob.glob(os.path.join(path, "*.jpg"))
    for image_file in images:
        image = cv2.imread(image_file)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Find the corners on the chessboard
        success, corners = cv2.findChessboardCorners(
            gray, (num_interior_corners_y, num_interior_corners_x), None
        )
        # If corners are found succesfully, find exact corners and draw the corners on the image
        if success == True:
            object_points.append(object_points_3D)
            # Find exact corner pixels
            corners_2 = cv2.cornerSubPix(
                gray, corners, (11, 11), (-1, -1), termination_criteria
            )
            image_points.append(corners_2)
            cv2.drawChessboardCorners(
                image,
                (num_interior_corners_y, num_interior_corners_x),
                corners_2,
                success,
            )
            cv2.imshow("Image", image)
            cv2.waitKey(1000)
    # Perform camera calibration to return the camera matrix, distortion coefficients, rotation and translation vectors etc
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        object_points, image_points, gray.shape[::-1], None, None
    )

    # Save parameters to a file
    cv_file = cv2.FileStorage("calibration_chessboard_web.yaml", cv2.FILE_STORAGE_WRITE)
    cv_file.write("K", mtx)
    cv_file.write("D", dist)
    cv_file.release()

    # Load the parameters from the saved file
    cv_file = cv2.FileStorage("calibration_chessboard_web.yaml", cv2.FILE_STORAGE_READ)
    mtx = cv_file.getNode("K").mat()
    dist = cv_file.getNode("D").mat()
    cv_file.release()

    print("Camera matrix:")
    print(mtx)
    print("\n Distortion coefficient:")
    print(dist)

    cv2.destroyAllWindows()


def main():
    calibrate()


if __name__ == "__main__":
    main()
