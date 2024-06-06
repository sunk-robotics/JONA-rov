import cv2
import numpy as np
import time
from ultralytics import YOLO
import glob

# Load a YOLOv8n PyTorch model
#  model = YOLO("best.pt")
#  model = YOLO("model_small.pt")
model = YOLO("model_small_ncnn_model")

img_num = 0
for filepath in glob.iglob("coral_dataset/train/new_images/*.jpg"):
    img = cv2.imread(filepath)
    img_width = img.shape[1]
    img_height = img.shape[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("ooga.jpg", gray)
    gray = cv2.imread("ooga.jpg")

    results = model.predict(source=gray, save=False, imgsz=256)
    if len(results) > 0 and len(results[0]) > 0:
        x1, y1, x2, y2 = [round(tensor.item()) for tensor in results[0].boxes.xyxy[0]]
        print(x1, y2, x2, y2)
        center_x = round((x2 + x1) / 2)
        center_y = round((y2 + y1) / 2)
        print(center_x, center_y)
        annotated_frame = results[0].plot()
        cv2.circle(img, (center_x, center_y), 5, (255, 255, 255), -1)
        cv2.putText(
            img,
            "Centroid",
            (center_x - 25, center_y - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )
        #  cv2.imshow("Object Detection", annotated_frame)
        cv2.imwrite(f"{img_num}.jpg", annotated_frame)
    else:
        #  cv2.imshow("Object Detection", img)
        cv2.imwrite(f"{img_num}.jpg", img)
    #  cv2.waitKey(0)
    img_num += 1

cv2.destroyAllWindows()
