from ultralytics import YOLO
import cv2
import os

def test_model():
    # Load the model
    model_path = os.path.join('model', 'best.pt')
    model = YOLO(model_path)
    
    # Print model information
    print("\nModel Information:")
    print("="*50)
    print(f"Model Path: {model_path}")
    print("\nAvailable Classes:")
    print("="*50)
    for idx, class_name in model.names.items():
        print(f"Class {idx}: {class_name}")
    
    # Test with webcam
    print("\nStarting Webcam Test:")
    print("="*50)
    print("Press 'q' to quit")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection with low confidence
        results = model(frame, conf=0.1)  # Very low confidence for testing
        
        # Process and display detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get detection info
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0])
                
                # Draw bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                
                # Add label
                label = f'{class_name}: {confidence:.2f}'
                cv2.putText(frame, label, (x1, y1-10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                # Print detection to console
                print(f"Detected {class_name} with confidence: {confidence:.2f}")
        
        # Show frame
        cv2.imshow('Model Test', frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_model() 