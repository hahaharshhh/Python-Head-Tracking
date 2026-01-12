
```Python

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
