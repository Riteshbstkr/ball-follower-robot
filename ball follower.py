"""
Ball-following robot: YOLO detection + L298N motor control.
Run: python3 ball_follower.py
Press Ctrl+C to stop.
"""

import cv2
import time
from picamera2 import Picamera2
from ultralytics import YOLO
from gpiozero import Motor

# ---- Config ----
MODEL_PATH = "best_ncnn_model"
CONF_THRESHOLD = 0.5
FRAME_W, FRAME_H = 640, 480

CENTER_MARGIN = 60        # pixels from center considered "centered"
TARGET_BOX_WIDTH = 220    # ball box width (px) considered "close enough" - stop
BASE_SPEED = 0.5
TURN_SPEED = 0.45

# ---- Motors (left = Motor A, right = Motor B on L298N) ----
left = Motor(forward=5, backward=6, enable=12, pwm=True)
right = Motor(forward=19, backward=26, enable=13, pwm=True)

def stop():
    left.stop()
    right.stop()

def forward(speed=BASE_SPEED):
    left.forward(speed)
    right.forward(speed)

def turn_left(speed=TURN_SPEED):
    left.backward(speed)
    right.forward(speed)

def turn_right(speed=TURN_SPEED):
    left.forward(speed)
    right.backward(speed)

def main():
    model = YOLO(MODEL_PATH, task="detect")

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": 'RGB888', "size": (FRAME_W, FRAME_H)}
    )
    picam2.configure(config)
    picam2.start()

    frame_center_x = FRAME_W // 2

    print("Ball follower running. Press Ctrl+C to stop.")

    try:
        while True:
            frame = picam2.capture_array()
            results = model.predict(frame, imgsz=320, conf=CONF_THRESHOLD, verbose=False)
            r = results[0]

            if len(r.boxes) > 0:
                box = r.boxes[r.boxes.conf.argmax()]
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = int((x1 + x2) / 2)
                box_width = int(x2 - x1)

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.circle(frame, (cx, int((y1 + y2) / 2)), 4, (0, 0, 255), -1)

                offset = cx - frame_center_x

                if abs(offset) > CENTER_MARGIN:
                    if offset < 0:
                        turn_left()
                    else:
                        turn_right()
                elif box_width < TARGET_BOX_WIDTH:
                    forward()
                else:
                    stop()  # centered and close enough
            else:
                stop()  # no ball seen

            cv2.imshow("Ball Follower", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        stop()
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
