from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model.train(
    data="the_square.yaml", imgsz=320, epochs=40, batch=8, name="The_Square"
)
