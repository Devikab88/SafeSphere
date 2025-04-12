import geocoder
from typing import List
from datetime import datetime

class SafetySimulation:
    def __init__(self, user_name: str = "SafeSphere User"):
        """
        Initialize the safety simulation system.
        
        Args:
            user_name (str): Name of the user to include in alerts
        """
        self.user_name = user_name
        self.emergency_contacts = [
            "+919884743670",  # Emergency Contact 1
            "+917904731290"   # Emergency Contact 2
        ]
        self.last_location = None

    def get_location_info(self) -> str:
        """
        Get current location information using IP-based geolocation.
        
        Returns:
            str: Google Maps link if location found, fallback message otherwise
        """
        try:
            # Try to use cached location if available
            if self.last_location:
                return self.last_location

            # Get location using IP
            g = geocoder.ip('me')
            if g.latlng:
                lat, lng = g.latlng
                self.last_location = f"https://www.google.com/maps?q={lat},{lng}"
                return self.last_location
            return "Location unavailable"
        except Exception as e:
            print(f"⚠️ Error getting location: {e}")
            return "Location unavailable"

    def generate_alert_message(self, location_info: str = None) -> str:
        """
        Generate the emergency alert message.
        
        Args:
            location_info (str, optional): Custom location information. 
                                         If not provided, will use IP-based geolocation.
        
        Returns:
            str: Formatted alert message
        """
        if not location_info:
            location_info = self.get_location_info()
        
        return f"🚨 SafeSphere Alert: {self.user_name} may be in danger. Weapon detected! Location: {location_info}"

    def simulate_alert(self):
        """
        Simulate sending emergency alerts to all contacts.
        Prints the alert message to console for each contact number.
        """
        alert_message = self.generate_alert_message()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print(f"🕒 ALERT TRIGGERED at {timestamp}")
        print("="*80)
        
        for contact in self.emergency_contacts:
            print(f"\n📱 SENDING EMERGENCY ALERT to: {contact}")
            print(f"📝 Message Content:")
            print("-"*40)
            print(alert_message)
            print("-"*40)
        
        print("\n✅ Alert simulation complete!")
        print(f"📍 Location: {self.get_location_info()}")
        print("="*80 + "\n")

def run_simulation():
    """
    Run a sample simulation of the safety alert system.
    """
    # Create a simulation instance
    safety_sim = SafetySimulation(user_name="Test User")
    
    # Simulate a threat detection and alert
    print("\n🔍 Simulating threat detection...")
    safety_sim.simulate_alert()

if __name__ == "__main__":
    run_simulation() 