import os
from ultralytics import YOLO
import cv2
import numpy as np  # Import numpy for color generation

video_path = 'VideoClips/clip_1.mp4'
video_path_1 = 'C:/Users/Basadi Thennakoon/Downloads/12_3_2023 5_59_59 PM (UTC-06_00) (1).mkv'
video_path_out = '{}_out_1.mp4'.format(video_path)

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
H, W, _ = frame.shape
out = cv2.VideoWriter(video_path_out, cv2.VideoWriter_fourcc(*'MP4V'), int(cap.get(cv2.CAP_PROP_FPS)), (W, H))

model_path = os.path.join('safe-watch.pt')

# Load a model
model = YOLO(model_path)  # load a custom model

threshold = 0.1

# Generate random colors for different classes
colors = np.random.randint(0, 255, size=(len(model.names), 3), dtype=np.uint8)

while ret:
    results = model(frame)[0]
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, class_id = result

        if score > threshold:
            # Get the color corresponding to the class ID
            color = tuple(map(int, colors[int(class_id)]))

            # Draw rectangle with the assigned color
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 4)
            cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, color, 3, cv2.LINE_AA)

    out.write(frame)
    ret, frame = cap.read()

cap.release()
out.release()
cv2.destroyAllWindows()
