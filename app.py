import cv2
import mediapipe as mp
import math
import numpy as np
import time
from collections import deque

from flask import Flask, render_template, Response, jsonify, request

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

app = Flask(__name__)


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_min, vol_max = volume.GetVolumeRange()[:2]


volume_history = deque(maxlen=5)
volume_time_data = deque(maxlen=120)
start_time = time.time()

current_volume_percent = 0
freeze_volume = False   # 🔹 FREEZE FLAG


def generate_frames():
    global current_volume_percent

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        h, w, _ = img.shape
        status_text = "Volume Frozen" if freeze_volume else "Gesture Active"

        if results.multi_hand_landmarks and not freeze_volume:
            for hand_landmarks in results.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                x2, y2 = int(lm[8].x * w), int(lm[8].y * h)

                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

                distance = math.hypot(x2 - x1, y2 - y1)

                raw_vol = np.interp(distance, [20, 180], [vol_min, vol_max])
                volume_history.append(raw_vol)
                smooth_vol = sum(volume_history) / len(volume_history)

                volume.SetMasterVolumeLevel(smooth_vol, None)

                current_volume_percent = int(
                    np.interp(smooth_vol, [vol_min, vol_max], [0, 100])
                )

                volume_time_data.append({
                    "time": round(time.time() - start_time, 2),
                    "volume": current_volume_percent
                })

        # UI Overlay
        cv2.putText(img, f"Volume: {current_volume_percent}%", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(img, status_text, (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 0, 255) if freeze_volume else (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/volume_data')
def volume_data():
    if freeze_volume:
        return jsonify([])   
    return jsonify(list(volume_time_data))

@app.route('/toggle_freeze', methods=['POST'])
def toggle_freeze():
    global freeze_volume
    freeze_volume = not freeze_volume
    return jsonify({"freeze": freeze_volume})


if __name__ == "__main__":
    app.run(debug=True)
