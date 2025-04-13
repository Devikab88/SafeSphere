# SafeSphere - Women's Safety Platform

A real-time weapon detection system with emergency alert capabilities.

## Setup in VS Code

1. First, open the project in VS Code:
   ```bash
   code .
   ```

2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Ensure your `.env` file exists with the following content:
   ```
   FAST2SMS_API_KEY=your_api_key_here
   EMERGENCY_CONTACTS=919884743670,917904731290,917305211171
   ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

## Troubleshooting

If SMS alerts are not being received:

1. Check your Fast2SMS account balance
2. Verify the phone numbers are correct (10 digits with country code)
3. Check the console for any error messages
4. Ensure your Fast2SMS API key is correct
5. Try sending a test SMS through the Fast2SMS dashboard

## Features

- Real-time weapon detection (guns and knives)
- Emergency SMS alerts to configured contacts
- Location tracking and sharing
- Audio alerts
- Visual notifications

## Note

Make sure your webcam is properly connected and accessible before running the application. 