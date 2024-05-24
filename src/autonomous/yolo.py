import cv2
import time
from ultralytics import YOLO
import glob

# Load a YOLOv8n PyTorch model
model = YOLO("best.pt")

for filepath in glob.iglob("coral_dataset/train/new_images/*.jpg"):
    img = cv2.imread(filepath)
    results = model.predict(source=img, save=False)
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
    #  cv2.imshow("Center of Square", img)
    cv2.imshow("Object Detection", annotated_frame)
    cv2.waitKey(0)

cv2.destroyAllWindows()
