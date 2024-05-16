import cv2
from ultralytics import YOLO

# Load a YOLOv8n PyTorch model
#  model = YOLO("yolov8x-seg.pt")
model = YOLO("yolov9c-seg.pt")

#  Export the model to NCNN format
model.export(format="ncnn")  # creates 'yolov8n_ncnn_model'

# Load the exported NCNN model
ncnn_model = YOLO("yolov9c-seg_ncnn_model")

results = ncnn_model("coral_images/red_square1.png")
annotated_frame = results[0].plot()
cv2.imshow("Object Detection", annotated_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
