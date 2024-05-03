import cv2
from ultralytics import YOLO
from flask import Flask, render_template, request , redirect , url_for, request, jsonify , send_from_directory
import  threading
import os
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)
CORS(app)

# Global variable for alerts
alerts_goods = []
alerts_vehicles=[]
alerts_processing = False
tracked_video = None
pallet_jack_count = 0
fork_lift_count = 0
good_count = 0

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}  # Add more video extensions if needed
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_video_frame():
    global alerts_processing, alerts_goods, alerts_vehicles
    if 'videoFrame' not in request.files:
        return redirect(request.url)

    file = request.files['videoFrame']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return file_path

    return redirect(request.url)


def tracker():
    global pallet_jack_count , fork_lift_count , good_count
    alerts_processing = True
    print(alerts_processing)
    model = YOLO('safe-watch.pt')
    # uploaded_video = upload_video_frame()

    cap = cv2.VideoCapture("VideoClips/clip_9.mp4")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = 0  # Counter for frames processed
    frame_to_save = 100

    tracked_video = 'static/sample_output_video.mp4'
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
                    class_names[class_label] = 'Fork Lift'
                    print("1",class_names[class_label])

                elif track_id == 2:
                    class_names[class_label] = 'Pallet Jack'
                    print("2",class_names[class_label])

                if class_label == 1 and class_names[class_label] == 'Goods':
                    alert_message = 'Alert: Goods are poorly packed!'
                    cv2.putText(frame, alert_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)




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

@app.route('/')
def index():
    return render_template('index.html', topic='Sysco Dock Monitor')



@app.route('/alerts')
def view_alerts():
    if alerts_processing:
        return jsonify({'message': 'Processing...'})
    else:
        return jsonify({
            'alerts_goods': alerts_goods,
            'alerts_vehicles': alerts_vehicles
        })



@app.route('/play_tracked_video')
def play_tracked_video():
    # video_filename = 'sample_output_video.mp4'  # Assuming the video file name is 'video.mp4' in the static folder
    # video_path = url_for('static', filename=video_filename)
    return render_template('play_video.html')


@app.route('/start_processing', methods=['POST'])
def start_processing():
    global alerts_processing
    if not alerts_processing:
        alerts_goods.clear()
        alerts_vehicles.clear()
        threading.Thread(target=tracker).start()
        return jsonify({'message': 'Processing Started'})
        return jsonify({'message': 'Done Processing'})



if __name__ == '__main__':
    app.run(debug=True)
      # Start the video tracking

