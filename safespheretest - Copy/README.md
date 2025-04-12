# SafeSphere - Smart Surveillance Simulation for Women's Safety

SafeSphere is a Python-based smart surveillance simulation system designed to act as a virtual women's safety bag. It uses AI-driven camera-based object detection to identify potential threats like weapons in real-time.

## Features

- Real-time weapon detection using YOLOv8
- Webcam video streaming
- SMS alerts to emergency contacts
- Visual notifications
- Modern, secure-themed web interface

## Prerequisites

- Python 3.8 or higher
- Webcam
- Fast2SMS API key (for SMS alerts)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/safesphere.git
cd safesphere
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following content:
```
FAST2SMS_API_KEY=your_api_key_here
EMERGENCY_NUMBER1=+911234567890
EMERGENCY_NUMBER2=+919876543210
```

4. Download the alert sound file and place it in the `static` directory as `alert.mp3`

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. The application will:
   - Access your webcam
   - Stream the video feed
   - Detect weapons in real-time
   - Send SMS alerts when weapons are detected
   - Display notifications on the web interface

## Security Notes

- This is a simulation system and should not be used as a sole means of protection
- Keep your Fast2SMS API key secure
- The system uses YOLOv8's pre-trained model which may have limitations in weapon detection accuracy

## License

This project is licensed under the MIT License - see the LICENSE file for details. 