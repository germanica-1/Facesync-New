import cv2
import base64
import requests
import time
import threading
from monitor_display import show_camera_frame
from buzzer import buzz, buzz_success


# ---------------- Config ----------------
CAM_INDEX = 0
API_URL = "http://192.168.1.112:5000/api/match_face_api"
FRAME_WIDTH = 480      # Match LCD aspect ratio
FRAME_HEIGHT = 480
LCD_WIDTH = 800
LCD_HEIGHT = 480
FPS = 30
COOLDOWN = 5 # seconds before scanning again

# ---------------- Globals ----------------
last_label = "Align your face in the green box..."
lock = threading.Lock()
last_capture_time = 0

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ---------------- Functions ----------------
def encode_frame_to_base64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer.tobytes()).decode("utf-8")

def send_frame_to_server(frame_b64):
    payload = {"image": f"data:image/jpeg;base64,{frame_b64}"}
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[WARN] Server returned status {response.status_code}")
            return {"match": False}
    except Exception as e:
        print("[ERROR] Failed to send frame:", e)
        return {"error": "server_unreachable", "match": False}

def background_recognition(frame):
    global last_label
    frame_b64 = encode_frame_to_base64(frame)
    result = send_frame_to_server(frame_b64)

    with lock:
        if result.get("error") == "server_unreachable":
            last_label = "Server not available!"
        elif result.get("match"):
            student_name = result.get("student_name", "Unknown")
            timestamp = result.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))
            last_label = f"{student_name} ({timestamp})"
            try:
                buzz_success()  # Play success tone for recognized face
            except Exception as e:
                print(f"[WARN] Failed to buzz success: {e}")
        else:
            last_label = "Unknown face!"
            try:
                buzz(duration=0.2, repeat=2)  # Buzz pattern for unknown face
            except Exception as e:
                print(f"[WARN] Failed to buzz: {e}")


    # Reset label back to default after 3 seconds
    def reset_label():
        global last_label
        time.sleep(3)
        with lock:
            last_label = "Align your face in the green box..."
    
    threading.Thread(target=reset_label, daemon=True).start()

# ---------------- Main Loop ----------------
def main():
    global last_label, last_capture_time

    cap = cv2.VideoCapture(CAM_INDEX)

    # Force capture size to match LCD
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[ERROR] Cannot open webcam")
        return

    print("[INFO] Press Ctrl+C to quit")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARN] Failed to grab frame")
                continue

            # Resize directly to LCD size (no padding, no zoom issues)
            frame = cv2.resize(frame, (LCD_WIDTH, LCD_HEIGHT))

            h, w = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Define target green box (centered, smaller so easier to align)
            box_w, box_h = int(w * 0.6), int(h * 0.6)   #% of screen
            box_x, box_y = (w - box_w) // 2 - 10, (h - box_h) // 2 - 10
            # Move box to the right by +# pixels
            box_x += 10 
            cv2.rectangle(frame, (box_x, box_y), (box_x + box_w, box_y + box_h), (0, 255, 0), 2)

            # Check each detected face
            for (x, y, fw, fh) in faces:
                cv2.rectangle(frame, (x, y), (x + fw, y + fh), (255, 0, 0), 2)

                if (box_x < x and x + fw < box_x + box_w) and (box_y < y and y + fh < box_y + box_h):
                    if time.time() - last_capture_time > COOLDOWN:
                        last_capture_time = time.time()
                        with lock:
                            last_label = "Capturing..."
                        threading.Thread(target=background_recognition, args=(frame,), daemon=True).start()

            # Show live feed with last label
            try:
                with lock:
                    show_camera_frame(frame, last_label)
            except Exception as e:
                print(f"[WARN] Could not display frame on LCD: {e}")

            time.sleep(1 / FPS)

    except KeyboardInterrupt:
        print("[INFO] Exiting...")
    finally:
        cap.release()
        try:
            from utils.buzzer import cleanup
            cleanup()
        except Exception as e:
            print(f"[WARN] GPIO cleanup failed {e}")

if __name__ == "__main__":
    main()
