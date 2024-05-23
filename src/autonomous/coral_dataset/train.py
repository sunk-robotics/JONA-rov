from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="the_square.yaml", imgsz=640, epochs=20, batch=8, name="The_Square"
)
