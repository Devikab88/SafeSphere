import os
import time
import json
import pygame
import numpy as np
import cv2
import threading
from typing import List, Dict, Optional
from ultralytics import YOLO
from twilio.rest import Client
import pywhatkit
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class SafetySimulation:
    def __init__(self, user_name: str = None, emergency_contacts: List[str] = None):
        """
        Initialize the safety simulation system.
        
        Args:
            user_name (str, optional): Name of the user to include in alerts.
                                     If not provided, will be loaded from environment.
            emergency_contacts (List[str], optional): List of emergency contact numbers.
                                                    If not provided, will be loaded from environment.
        """
        # Load configuration from environment with proper defaults
        self.user_name = self._load_user_name(user_name)
        self.alert_cooldown = self._load_alert_cooldown()
        
        # Initialize state variables
        self.weapon_detected = False
        self.last_alert_time = None
        self.last_alert_status = None
        self.sound_playing = False
        self.sound_enabled = False
        
        # Load emergency contacts with validation
        self.emergency_contacts = self._load_emergency_contacts(emergency_contacts)
        
        # Initialize Twilio client with exact credentials
        self.account_sid = 'ACa590f19220639ccfd59e5698d2007daf'
        self.auth_token = '4bedaf0919857419d00b8967b5246f90'
        self.twilio_client = Client(self.account_sid, self.auth_token)
        self.from_number = '+12254200926'  # Your Twilio number
        
        # Initialize YOLO model with improved detection settings
        try:
            # Load model without weights_only parameter
            self.model = YOLO(r'C:\Users\SUBHASHREE NS\safespheretest\model\best.pt')
            self.confidence_threshold = 0.35  # Lower threshold for initial detection
            self.min_knife_size = 0.02  # Minimum size relative to frame
            self.max_knife_size = 0.3   # Maximum size relative to frame
            self.detection_history = []  # Store recent detections
            self.history_length = 5     # Number of frames to consider
            print("✅ Model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            raise
        
        # Initialize sound system
        try:
            pygame.mixer.init()
            # Use the absolute path for the sound file
            sound_file = r'C:\Users\SUBHASHREE NS\safespheretest\static\sounds\siren-alarm.mp3'
            if os.path.exists(sound_file):
                self.alert_sound = pygame.mixer.Sound(sound_file)
                self.sound_enabled = True
                print(f"Sound file loaded successfully from: {sound_file}")
            else:
                print(f"Warning: Alert sound file not found at {sound_file}. Sound alerts will be disabled.")
                self.sound_enabled = False
        except Exception as e:
            print(f"Warning: Could not initialize sound system: {str(e)}")
            self.sound_enabled = False

    def _load_user_name(self, user_name: str = None) -> str:
        if user_name:
            return user_name.strip()
        
        env_name = os.getenv("USER_NAME")
        if env_name:
            return env_name.strip()
            
        return "SafeSphere User"

    def _load_alert_cooldown(self) -> int:
        try:
            cooldown = os.getenv("ALERT_COOLDOWN", "300")
            return max(60, int(cooldown))  # Minimum 60 seconds
        except ValueError:
            return 300

    def _load_emergency_contacts(self, contacts: List[str] = None) -> List[str]:
        try:
            if contacts:
                validated_contacts = self._validate_phone_numbers(contacts)
                if validated_contacts:
                    return validated_contacts
            
            env_contacts = os.getenv("EMERGENCY_CONTACTS")
            if env_contacts:
                try:
                    # Try to parse as JSON
                    contact_data = json.loads(env_contacts)
                    if "emergency_contact" in contact_data:
                        phone = contact_data["emergency_contact"]["phone"]
                        validated_contacts = self._validate_phone_numbers([phone])
                        if validated_contacts:
                            return validated_contacts
                except json.JSONDecodeError:
                    # Fallback to comma-separated list
                    contacts_list = [num.strip() for num in env_contacts.split(",")]
                    validated_contacts = self._validate_phone_numbers(contacts_list)
                    if validated_contacts:
                        return validated_contacts
            
            return []
        except Exception:
            return []

    def _validate_phone_number(self, number: str) -> str:
        try:
            clean = ''.join(filter(str.isdigit, number))
            
            if len(clean) < 10:
                return ""
                
            if len(clean) > 10:
                clean = clean[-10:]
            
            return clean
        except Exception:
            return ""

    def _validate_phone_numbers(self, numbers: List[str]) -> List[str]:
        validated = []
        for number in numbers:
            clean = self._validate_phone_number(number)
            if clean:
                validated.append(clean)
        
        return validated

    def update_emergency_contacts(self, new_contacts: List[str]) -> bool:
        validated = self._validate_phone_numbers(new_contacts)
        if validated:
            self.emergency_contacts = validated
            return True
        
        return False

    def play_alert_sound(self):
        if self.sound_enabled and not self.sound_playing:
            try:
                self.sound_playing = True
                self.alert_sound.play()
                # Reset sound playing flag after sound finishes
                threading.Timer(self.alert_sound.get_length(), self.reset_sound_flag).start()
            except Exception as e:
                print(f"Warning: Could not play alert sound: {str(e)}")
                self.sound_playing = False

    def reset_sound_flag(self):
        self.sound_playing = False

    def process_frame(self, frame):
        try:
            results = self.model(frame, conf=self.confidence_threshold)
            weapon_detected = False
            frame_height, frame_width = frame.shape[:2]
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    if cls in [0, 1] and conf >= self.confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Calculate object size relative to frame
                        width = x2 - x1
                        height = y2 - y1
                        size_ratio = (width * height) / (frame_width * frame_height)
                        
                        # For knife detection (class 0)
                        if cls == 0:
                            # Apply size-based filtering for knives
                            if self.min_knife_size <= size_ratio <= self.max_knife_size:
                                # Add to detection history
                                self.detection_history.append((cls, conf, size_ratio))
                                if len(self.detection_history) > self.history_length:
                                    self.detection_history.pop(0)
                                
                                # Check if we have consistent detections
                                if len(self.detection_history) >= self.history_length:
                                    knife_detections = [d for d in self.detection_history if d[0] == 0]
                                    if len(knife_detections) >= 3:  # Require at least 3 knife detections
                                        weapon_detected = True
                                        
                                        # Draw red bounding box with thicker lines
                                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                                        
                                        # Add label with confidence
                                        label = f"Knife {conf:.2f}"
                                        # Draw filled background for label
                                        (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                                        cv2.rectangle(frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), (0, 0, 255), -1)
                                        cv2.putText(frame, label, (x1, y1 - 10),
                                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                                        
                                        # Trigger alert
                                        if self.can_send_alert():
                                            self.trigger_weapon_alert(conf, "Knife")
                        
                        # For gun detection (class 1)
                        elif cls == 1 and conf >= 0.45:  # Higher threshold for guns
                            weapon_detected = True
                            
                            # Draw red bounding box with thicker lines
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                            
                            # Add label with confidence
                            label = f"Gun {conf:.2f}"
                            # Draw filled background for label
                            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                            cv2.rectangle(frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), (0, 0, 255), -1)
                            cv2.putText(frame, label, (x1, y1 - 10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                            
                            # Trigger alert
                            if self.can_send_alert():
                                self.trigger_weapon_alert(conf, "Gun")
            
            return frame, weapon_detected
            
        except Exception:
            return frame, False

    def trigger_weapon_alert(self, confidence: float, weapon_type: str):
        try:
            self.last_alert_time = time.time()
            
            # Send WhatsApp alert
            try:
                phone_number = "+919884743670"  # Your WhatsApp number
                message = f"🚨 {weapon_type.upper()} detected with {confidence:.2f}% confidence! Immediate action required."
                pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=True)
                print(f"Message sent to {phone_number}")
            except Exception as e:
                print(f"An error occurred while sending WhatsApp alert: {e}")
            
            # Play alert sound
            self.play_alert_sound()
            self.last_alert_status = True
            
        except Exception as e:
            print(f"Error in trigger_weapon_alert: {str(e)}")
            self.last_alert_status = False

    def can_send_alert(self) -> bool:
        if self.last_alert_time is None:
            return True
            
        current_time = time.time()
        time_since_last_alert = current_time - self.last_alert_time
        
        if time_since_last_alert < self.alert_cooldown:
            return False
            
        return True

    def get_location_info(self) -> str:
        try:
            # Return a default location string since geocoder is not required
            return "Location tracking disabled"
        except Exception:
            return "Location unavailable"

    def simulate_alert(self):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("\n" + "="*80)
            print(f"🕒 ALERT TRIGGERED at {timestamp}")
            print("="*80)
            
            # Debug: Print current state
            print("\nCurrent Configuration:")
            print(f"User Name: {self.user_name}")
            print(f"Emergency Contacts: {self.emergency_contacts}")
            print(f"Location: {self.get_location_info()}")
            
            # Send WhatsApp alert
            try:
                phone_number = "+919884743670"  # Your WhatsApp number
                message = f"🚨 ALERT: Weapon detected at {timestamp}! Immediate action required."
                pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10, tab_close=True)
                print(f"\n✅ WhatsApp alert sent to {phone_number}")
            except Exception as e:
                print(f"\n⚠️ Error sending WhatsApp alert: {str(e)}")
            
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error in simulate_alert: {str(e)}")
            print(f"Full error details: {repr(e)}")
            print("="*80 + "\n")

def run_simulation():
    safety_sim = SafetySimulation(user_name="Test User")
    safety_sim.simulate_alert()

if __name__ == "__main__":
    run_simulation() 