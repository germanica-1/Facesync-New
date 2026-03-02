import cv2
import numpy as np
from datetime import datetime
import screeninfo  # pip install screeninfo
import os

# ---------------- Force Display ----------------
# Ensure OpenCV uses Waveshare HDMI screen (DISPLAY=:0)
os.environ["DISPLAY"] = ":0"

# ---------------- Helper ----------------
def get_screen_resolution():
    try:
        screen = screeninfo.get_monitors()[0]
        return screen.width, screen.height
    except Exception:
        # fallback to common Waveshare LCD resolution
        return 800, 480

# ---------------- Display functions ----------------

def show_camera_frame(frame, label=""):
    """
    Display camera frame on Waveshare LCD with optional overlay text.
    """
    if frame is None:
        return

    width, height = get_screen_resolution()

    # Resize frame to fit LCD resolution
    disp_frame = cv2.resize(frame, (width, height))

    # Overlay label (name, status, etc.)
    if label:
        cv2.putText(
            disp_frame,
            label,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            2,
            cv2.LINE_AA
        )

    # Overlay timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(
        disp_frame,
        timestamp,
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    # Show fullscreen on Waveshare LCD
    cv2.namedWindow("FaceSync", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("FaceSync", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("FaceSync", disp_frame)
    cv2.waitKey(1)


def show_message(message, duration=2000):
    """
    Display a static message on Waveshare LCD for a short duration (ms).
    """
    width, height = get_screen_resolution()
    disp_frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Split message into lines
    lines = message.split("\n")
    y0, dy = 80, 60
    for i, line in enumerate(lines):
        text_size, _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
        text_x = (width - text_size[0]) // 2
        y = y0 + i * dy
        cv2.putText(
            disp_frame,
            line,
            (text_x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            2,
            cv2.LINE_AA
        )

    # Show fullscreen
    cv2.namedWindow("FaceSync", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("FaceSync", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("FaceSync", disp_frame)
    cv2.waitKey(duration)
    cv2.destroyWindow("FaceSync")
