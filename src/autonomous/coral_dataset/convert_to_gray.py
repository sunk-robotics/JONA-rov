import cv2
import glob


def main():
    for i, filename in enumerate(glob.iglob("*.jpg")):
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        new_filepath = f"new_image{i + 1}.jpg"
        cv2.imwrite(new_filepath, gray)


if __name__ == "__main__":
    main()
