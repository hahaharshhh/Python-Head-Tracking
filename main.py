import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import math

# --- CONFIGURATION ---
CAMERA_ID = 0             # 0 is usually the default webcam
TILT_THRESHOLD = 15       # Angle in degrees to trigger pause
HAND_EAR_DIST = 60        # Distance (pixels) to consider hand is touching ear
COOLDOWN_SECONDS = 2.0    # Time to wait between triggers
GESTURE_HOLD_TIME = 0.5   # Seconds hand must be at ear to trigger
# ---------------------

# Initialize MediaPipe solutions
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands

# Setup Face Mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)

# Setup Hand Tracking
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize Webcam
cap = cv2.VideoCapture(CAMERA_ID)

# Timers and State
last_trigger_time = 0
hand_near_ear_start_time = 0
is_hand_near_ear = False
system_state = "PLAYING" # Keeps track of our assumed state (Playing/Paused)

def calculate_angle(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    theta = math.atan2(y2 - y1, x2 - x1)
    angle = math.degrees(theta)
    return angle

def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def draw_ui(image, state, status_text, cooldown_active, hand_progress):
    h, w, _ = image.shape
    
    # 1. Color Scheme based on State
    if state == "PLAYING":
        color = (0, 255, 0) # Green
        main_text = "ACTIVE - PLAYING"
    else:
        color = (0, 0, 255) # Red
        main_text = "PAUSED"

    if cooldown_active:
        color = (0, 165, 255) # Orange during cooldown
        main_text = "COOLDOWN..."

    # 2. Draw Borders
    cv2.rectangle(image, (0, 0), (w, h), color, 10)
    
    # 3. Top Info Bar Background
    cv2.rectangle(image, (0, 0), (w, 60), (0, 0, 0), -1)
    
    # 4. Main Status Text
    cv2.putText(image, main_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    # 5. Detail Text (Right side)
    cv2.putText(image, status_text, (w - 350, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

    # 6. Hand Gesture Progress Bar (if hand is detected near ear)
    if hand_progress > 0:
        bar_width = 300
        bar_height = 20
        start_x = (w - bar_width) // 2
        start_y = h - 50
        
        # Background bar
        cv2.rectangle(image, (start_x, start_y), (start_x + bar_width, start_y + bar_height), (50, 50, 50), -1)
        # Fill bar
        fill_width = int(bar_width * hand_progress)
        cv2.rectangle(image, (start_x, start_y), (start_x + fill_width, start_y + bar_height), (0, 255, 255), -1)
        cv2.putText(image, "EARBUD GESTURE", (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

print("System Started with UI. Press 'q' to quit.")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Flip image and convert to RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape
    
    # Process Face and Hands
    face_results = face_mesh.process(rgb_image)
    hand_results = hands.process(rgb_image)
    
    trigger_detected = False
    trigger_reason = "Scanning..."
    
    # Variables for drawing
    left_ear_coords = None
    right_ear_coords = None
    hand_progress = 0.0

    # --------------------------
    # 1. FACE LOGIC
    # --------------------------
    if face_results.multi_face_landmarks:
        for face_landmarks in face_results.multi_face_landmarks:
            # Eyes
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]
            pt1 = (int(left_eye.x * w), int(left_eye.y * h))
            pt2 = (int(right_eye.x * w), int(right_eye.y * h))
            
            # Ears
            l_ear = face_landmarks.landmark[234]
            r_ear = face_landmarks.landmark[454]
            left_ear_coords = (int(l_ear.x * w), int(l_ear.y * h))
            right_ear_coords = (int(r_ear.x * w), int(r_ear.y * h))

            # Visuals: Eye Line
            cv2.line(image, pt1, pt2, (255, 255, 255), 1)
            # Visuals: Ear Dots
            cv2.circle(image, left_ear_coords, 5, (255, 200, 0), -1) 
            cv2.circle(image, right_ear_coords, 5, (255, 200, 0), -1)

            # Check Tilt
            angle = calculate_angle(pt1, pt2)
            if abs(angle) > TILT_THRESHOLD:
                trigger_detected = True
                trigger_reason = f"Head Tilt: {int(angle)} deg"

    # --------------------------
    # 2. HAND LOGIC
    # --------------------------
    current_hand_near_ear = False
    
    if hand_results.multi_hand_landmarks and left_ear_coords:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            # Tip of Index Finger
            tip = hand_landmarks.landmark[8] 
            tip_coords = (int(tip.x * w), int(tip.y * h))
            
            dist_left = distance(tip_coords, left_ear_coords)
            dist_right = distance(tip_coords, right_ear_coords)
            
            # Draw line if close
            if dist_left < 150:
                cv2.line(image, tip_coords, left_ear_coords, (0, 255, 255), 1)
            if dist_right < 150:
                cv2.line(image, tip_coords, right_ear_coords, (0, 255, 255), 1)

            if dist_left < HAND_EAR_DIST or dist_right < HAND_EAR_DIST:
                current_hand_near_ear = True
                cv2.circle(image, tip_coords, 10, (0, 0, 255), -1)

    # --------------------------
    # 3. GESTURE TIMING
    # --------------------------
    if current_hand_near_ear:
        if not is_hand_near_ear:
            hand_near_ear_start_time = time.time()
            is_hand_near_ear = True
        
        # Calculate progress (0.0 to 1.0)
        elapsed = time.time() - hand_near_ear_start_time
        hand_progress = min(elapsed / GESTURE_HOLD_TIME, 1.0)
        
        if elapsed > GESTURE_HOLD_TIME:
            trigger_detected = True
            trigger_reason = "Earbud Gesture"
    else:
        is_hand_near_ear = False
        hand_progress = 0.0

    # --------------------------
    # 4. TRIGGER ACTION
    # --------------------------
    current_time = time.time()
    cooldown_active = (current_time - last_trigger_time < COOLDOWN_SECONDS)

    if trigger_detected and not cooldown_active:
        print(f"Trigger: {trigger_reason}")
        
        # Toggle State
        if system_state == "PLAYING":
            system_state = "PAUSED"
        else:
            system_state = "PLAYING"
            
        pyautogui.press('space')
        last_trigger_time = current_time

    # --------------------------
    # 5. DRAW UI OVERLAY
    # --------------------------
    draw_ui(image, system_state, trigger_reason, cooldown_active, hand_progress)

    cv2.imshow('Gesture Controller UI', image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 