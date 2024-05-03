import cv2
from ultralytics import YOLO
import os

alerts_goods = []
alerts_vehicles=[]
alerts_processing = False
tracked_video = None
pallet_jack_count = 0
fork_lift_count = 0
good_count = 0

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}



def tracker():
    global pallet_jack_count , fork_lift_count , good_count
    alerts_processing = True
    print(alerts_processing)
    model = YOLO('safe-watch.pt')


    cap = cv2.VideoCapture("VideoClips/clip_1.mp4")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = 0
    frame_to_save = 100

    tracked_video = 'static/output_video_2.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(tracked_video, fourcc, frame_rate, (frame_width, frame_height))

    while cap.isOpened():
        success, frame = cap.read()
        if success:
            results = model.track(frame, persist=True, show_labels=False, tracker='botsort.yaml')

            if results[0].boxes:
                track_ids = results[0].boxes.id.int().cpu().tolist()
                boxes = results[0].boxes.xywh.cpu()
                class_labels = results[0].boxes.cls.int().cpu().tolist()
                class_names = results[0].names

            for i, (track_id, class_label) in enumerate(zip(track_ids, class_labels)):
                print(track_id , class_label)
                if track_id == 3:
                    class_names[class_label] = 'Left Out Pallets'
                    print("1",class_names[class_label])

                elif track_id == 2:
                    class_names[class_label] = 'Left Out Pallets'
                    print("2",class_names[class_label])

                elif track_id == 4:
                    class_names[class_label] = 'Left Out Pallets'
                    print("2",class_names[class_label])

                elif track_id == 1:
                    class_names[class_label] = 'Opened Packages'
                    print("opened packages detected.")

                alert_messages = ['Alert: Opened Packages of Food Items!', 'Alert: Left out pallets in the dock!']


                text_y = 50


                for alert_message in alert_messages:

                    text_size = cv2.getTextSize(alert_message, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
                    text_x = (frame.shape[1] - text_size[0]) // 2


                    cv2.rectangle(frame, (0, text_y - 10), (frame.shape[1], text_y + text_size[1] + 10),
                                  (255, 255, 255), -1)


                    cv2.putText(frame, alert_message, (text_x, text_y + text_size[1]), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                (0, 0, 255), 3)


                    text_y += text_size[1] * 2

            results[0].names = class_names
            annotated_frames = results[0].plot()
            out.write(annotated_frames)

            output_folder = 'output_frames_1'
            os.makedirs(output_folder, exist_ok=True)
            frame_filename = os.path.join(output_folder, f'frame_{frame_count}.jpg')
            cv2.imwrite(frame_filename, frame)


            frame_count += 1

            cv2.imshow('YOLOv8 tracking', annotated_frames)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
    for class_label in class_labels:
        if class_label == 3:
            good_count += 1
        elif class_label == 1:
            fork_lift_count += 1
    if fork_lift_count > 0:
        alerts_vehicles.append(f"Vehicles detected {fork_lift_count} times.")
    if pallet_jack_count > 0:
        alerts.append(f"Pallet Jack detected {pallet_jack_count} times.")
    if good_count > 0:
        alert_message = 'Alert: Goods are poorly packed!'
        alerts_goods.append(alert_message)


    cap.release()
    cv2.destroyAllWindows()
    alerts_processing = False
    return tracked_video


tracker()