import cv2
import numpy as np
from flask import Flask, render_template, Response
from ultralytics import YOLO
import os
import threading
import time
from utils.safety_simulation import SafetySimulation

# Initialize Flask app
app = Flask(__name__)

# Initialize YOLO model
model_path = os.path.join('model', 'best.pt')
model = YOLO(model_path)

# Initialize Safety Simulation system
safety_sim = SafetySimulation()

# Global variables
weapon_detected = False
last_alert_time = 0
ALERT_COOLDOWN = 60  # seconds between alerts

def process_frame(frame):
    """
    Process a single frame using YOLOv8 model.
    
    Args:
        frame: Input frame from webcam
    
    Returns:
        tuple: (processed_frame, weapon_detected)
    """
    global weapon_detected
    
    # Run YOLO detection with your trained model
    results = model(frame, conf=0.6)  # Increased confidence threshold for more accurate detection
    
    # Process detections
    weapon_detected = False
    for result in results:
        boxes = result.boxes
        for box in boxes:
            # Get detection info
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            
            # Only process weapons (knives and guns)
            if class_name.lower() in ['knife', 'gun'] and confidence > 0.6:
                weapon_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Draw red bounding box with thicker lines
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                
                # Add detection label with class name and confidence
                label = f'{class_name}: {confidence:.2f}'
                
                # Enhanced label background
                (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                cv2.rectangle(frame, (x1, y1-label_h-10), (x1+label_w, y1), (0, 0, 255), -1)
                cv2.putText(frame, label, (x1, y1-5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                # Print detection for debugging
                print(f"Detected {class_name} with {confidence:.2f} confidence")
    
    return frame, weapon_detected

def send_alerts():
    """
    Send alerts when weapon is detected.
    Includes cooldown to prevent spam.
    """
    global last_alert_time
    current_time = time.time()
    
    if current_time - last_alert_time < ALERT_COOLDOWN:
        return
    
    last_alert_time = current_time
    
    # Simulate sending alerts
    safety_sim.simulate_alert()

def generate_frames():
    """
    Generate video frames from webcam with real-time weapon detection.
    """
    cap = cv2.VideoCapture(0)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Process frame
            processed_frame, detected = process_frame(frame)
            
            # Trigger alerts if weapon detected
            if detected:
                threading.Thread(target=send_alerts).start()
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream video feed with weapon detection."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Return current weapon detection status."""
    return {'weapon_detected': weapon_detected}

if __name__ == '__main__':
    app.run(debug=True) 