1. Installing
```# 🎵 Gesture Media Controller

A Python-based computer vision project that controls your media playback (Spotify, YouTube, VLC) using webcam gestures. It detects when you **tilt your head** or **remove your earbuds** and automatically toggles Play/Pause.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Tracking-orange)

## 🚀 Features

* **Head Tilt Detection:** Pauses video/music when you tilt your head sideways (>15°).
* **Earbud Gesture Recognition:** Pauses when you raise your hand to your ear (imitating removing headphones).
* **Global Media Control:** Uses the system-wide `Play/Pause` media key, so it works even if your browser or Spotify is minimized.
* **Visual UI:** "Iron Man" style overlay showing system status, tracking lines, and gesture progress bars.
* **Cooldown System:** Prevents the system from spamming the pause button.

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/hahaharshhh/Python-Head-Tracking.git](https://github.com/hahaharshhh/Python-Head-Tracking.git)
cd Python-Head-Tracking
```

2. Install Dependencies

Note: This project works best with Python 3.10 or 3.11. (MediaPipe has known issues with Python 3.12+).
```Bash

pip install -r requirements.txt
```

If requirements.txt is missing, run:
```Bash

pip install opencv-python mediapipe pyautogui numpy
```

3. Run the Project
```Bash

python main.py
```


🎮 How to Use

Run the script. A window will open showing your webcam feed.

State: ACTIVE (Green Border): The system is monitoring.

To Pause/Play:

Tilt Head: Tilt your head to the left or right.

Touch Ear: Touch your ear with your index finger and hold for 0.5 seconds (Wait for the yellow bar to fill).

State: PAUSED (Red Border): The trigger has been sent.

Press 'q' on your keyboard to quit the application.

⚙️ Configuration

You can tweak the sensitivity settings at the top of main.py:
```python

CAMERA_ID = 0             # Change if you have multiple cameras
TILT_THRESHOLD = 15       # Angle needed to trigger pause
HAND_EAR_DIST = 60        # How close (pixels) hand must be to ear
GESTURE_HOLD_TIME = 0.5   # How long to hold hand at ear
```


🐛 Troubleshooting

"AttributeError: module 'mediapipe' has no attribute 'solutions'"

You are likely using an incompatible version of Python (3.12+). Please downgrade to Python 3.10 or 3.11.
Alternatively, try: pip install "protobuf<4"

Media not pausing when I'm in another window?

The script uses pyautogui.press('playpause'). Ensure your keyboard/laptop supports media keys.
On Mac, you may need to grant "Accessibility" permissions to your terminal.

🤝 Contributing

Feel free to fork this project and submit pull requests! Ideas for improvements:

Add Volume control (e.g., sliding hand up/down).
Add "Next Track" gesture (e.g., swipe right).

📄 License

This project is open-source. Feel free to use and modify it.
