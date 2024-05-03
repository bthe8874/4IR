import cv2
from flask import Flask, render_template, request

app = Flask(__name__)

# Global variable for alert message
alert_message = ""

@app.route('/')
def index():
    return render_template('index.html', topic='Sysco Dock Monitor')

@app.route('/alerts')
def view_alerts():
    alerts = [alert_message] if alert_message else []  # Include alert message in list if not empty
    return render_template('alerts.html', alerts=alerts)

# Other routes and app configurations...

def process_video():
    global alert_message  # Access the global variable



    subprocess.run(['python', 'ObjectDetector.py'])
    else:
        alert_message = ''  # Reset alert message if no alert

# Run the video processing function
process_video()

if __name__ == '__main__':
    app.run(debug=True)
