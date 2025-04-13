import pywhatkit
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import os
import threading
import time
from utils.safety_simulation import SafetySimulation
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize YOLO model
try:
    model_path = os.path.join('model', 'best.pt')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = YOLO(model_path)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {str(e)}")
    raise

# Initialize Safety Simulation system
safety_sim = SafetySimulation()

# Global variables
weapon_detected = False
last_alert_time = 0
ALERT_COOLDOWN = 30  # reduced cooldown to 30 seconds
detection_threshold = 0.4  # reduced threshold for better detection

def process_frame(frame):
    """
    Process a single frame using YOLOv8 model.
    
    Args:
        frame: Input frame from webcam
    
    Returns:
        tuple: (processed_frame, weapon_detected)
    """
    global weapon_detected
    
    try:
        # Ensure frame is in correct format
        if frame is None:
            return frame, False
            
        # Convert frame to RGB if needed
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        elif frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            
        # Run YOLO detection
        results = model(frame, conf=detection_threshold)
        
        # Reset weapon detection status
        weapon_detected = False
        
        # Process detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get detection info
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                
                # Debug print
                print(f"Detected object: {class_name} with confidence: {confidence:.2f}")
                
                # Only process weapons (knives and guns)
                if class_name.lower() in ['knife', 'gun'] and confidence > detection_threshold:
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
                    
                    print(f"🚨 Weapon Detected: {class_name} with {confidence:.2f} confidence")
        
        return frame, weapon_detected
        
    except Exception as e:
        print(f"❌ Error processing frame: {str(e)}")
        return frame, False


import pywhatkit

def send_whatsapp_alert(phone_number, message):
    """
    Sends a WhatsApp message instantly to the specified phone number.
    
    Parameters:
    - phone_number (str): The recipient's phone number in international format (e.g., '+919876543210').
    - message (str): The message content to send.
    """
    try:
        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=True)
        print(f"Message sent to {phone_number}")
    except Exception as e:
        print(f"An error occurred: {e}")
# After detecting a weapon
send_whatsapp_alert("+919884743670", "🚨 Weapon detected! Immediate action required.")

def generate_frames():
    """
    Generate video frames from webcam with real-time weapon detection.
    """
    cap = cv2.VideoCapture(0)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while True:
        success, frame = cap.read()
        if not success:
            print("❌ Failed to read frame from camera")
            break
            
        try:
            # Process frame
            processed_frame, detected = process_frame(frame)
            
            # Convert frame to JPEG
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                   
        except Exception as e:
            print(f"❌ Error in generate_frames: {str(e)}")
            continue

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
    return jsonify({
        'weapon_detected': weapon_detected,
        'last_alert_time': last_alert_time
    })

def cleanup():
    global cap
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Run the Flask app
    print("\nStarting SafeSphere Safety System...")
    print("Access the web interface at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    finally:
        cleanup() 