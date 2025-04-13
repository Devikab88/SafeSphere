from utils.safety_simulation import SafetySimulation
import os
from dotenv import load_dotenv

def test_sms():
    try:
        # Load environment variables
        load_dotenv()
        
        # Print environment variables (masked)
        api_key = os.getenv("FAST2SMS_API_KEY")
        contacts = os.getenv("EMERGENCY_CONTACTS")
        print(f"\n🔑 API Key: {api_key[:5]}...{api_key[-5:]}")
        print(f"📱 Emergency Contacts: {contacts}")
        
        # Create safety simulation instance
        safety = SafetySimulation(user_name="Test User")
        
        # Test message (simpler format)
        test_message = "SafeSphere Test Alert: This is a test message"
        
        # Test with single number first
        test_number = "9884743670"  # First emergency contact
        
        print("\n🔄 Testing SMS with single number...")
        success = safety.send_sms_alert(test_message, [test_number])
        
        if success:
            print("\n✅ Test completed successfully!")
            print("\n🔄 Now testing with all numbers...")
            # If single number works, try all numbers
            success = safety.send_sms_alert(test_message, safety.emergency_contacts)
        else:
            print("\n❌ Test failed! Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        print(f"Full error details: {repr(e)}")

if __name__ == "__main__":
    test_sms() 