import cv2
from ultralytics import FastSAM
from ultralytics.models.fastsam import FastSAMPrompt

# Define an inference source
source = "coral_images/red_square1.png"

# Create a FastSAM model
model = FastSAM("FastSAM-s.pt")  # or FastSAM-x.pt

# Run inference on an image
everything_results = model(
    source, device="cpu", retina_masks=True, imgsz=640, conf=0.4, iou=0.9
)

# Prepare a Prompt Process object
prompt_process = FastSAMPrompt(source, everything_results, device="cpu")

# Everything prompt
#  ann = prompt_process.everything_prompt()

# Bbox default shape [0,0,0,0] -> [x1,y1,x2,y2]
#  ann = prompt_process.box_prompt(bbox=[200, 200, 300, 300])

# Text prompt
ann = prompt_process.text_prompt(text="small rectangle")

# Point prompt
# points default [[0,0]] [[x1,y1],[x2,y2]]
# point_label default [0] [1,0] 0:background, 1:foreground
#  ann = prompt_process.point_prompt(points=[[356, 329]], pointlabel=[1])
#  img = prompt_process.plot(annotations=ann, output="./")
prompt_process.plot(annotations=ann, output="./")
cv2.imshow("Ooga", cv2.imread("red_square1.png"))
cv2.waitKey(0)
cv2.destroyAllWindows()
