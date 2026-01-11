import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import math

# --- CONFIGURATION ---
CAMERA_ID = 0             # 0 is usually the default webcam
TILT_THRESHOLD = 15       # Angle in degrees to trigger pause
COOLDOWN_SECONDS = 2.0    # Time to wait between triggers
# ---------------------

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# Initialize Webcam
cap = cv2.VideoCapture(CAMERA_ID)

# Cooldown tracker
last_trigger_time = 0

def calculate_angle(p1, p2):
    """Calculates the angle between two points (eyes) relative to horizontal."""
    x1, y1 = p1
    x2, y2 = p2
    theta = math.atan2(y2 - y1, x2 - x1)
    angle = math.degrees(theta)
    return angle

print("System Started. Press 'q' to quit.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip image horizontally for a mirror view and convert to RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image with MediaPipe
    results = face_mesh.process(rgb_image)
    
    # Get image dimensions
    h, w, _ = image.shape

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get coordinates for Left Eye (Index 33) and Right Eye (Index 263)
            # MediaPipe uses normalized coordinates (0.0 to 1.0), so we multiply by width/height
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            
            pt1 = (int(left_eye.x * w), int(left_eye.y * h))
            pt2 = (int(right_eye.x * w), int(right_eye.y * h))

            # Draw a line between eyes for visual debug
            cv2.line(image, pt1, pt2, (0, 255, 0), 2)

            # Calculate Angle
            angle = calculate_angle(pt1, pt2)
            
            # MediaPipe's angle is usually 0 when straight. 
            # If the head tilts, the angle deviates.
            # We check the absolute difference.
            if abs(angle) > TILT_THRESHOLD:
                current_time = time.time()
                
                # Check cooldown to avoid spamming
                if current_time - last_trigger_time > COOLDOWN_SECONDS:
                    print(f"Angle {int(angle)}° detected! Toggling Play/Pause.")
                    
                    # --- ACTION ---
                    pyautogui.press('space') 
                    # --------------
                    
                    last_trigger_time = current_time
                    
                    # Visual indicator on screen (Red Text)
                    cv2.putText(image, "PAUSED", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Show the output window
    cv2.imshow('Gesture Controller', image)

    # Quit if 'q' is pressed
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()