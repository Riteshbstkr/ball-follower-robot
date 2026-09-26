# Ball-Following Robot (Raspberry Pi 4 + YOLO)

An autonomous robot that detects and follows a tennis ball using a custom-trained
YOLO26n object detection model, running on a Raspberry Pi 4 with a Pi Camera Module.

## Demo

*(Add a photo or short video of your robot here once mounted)*

## Hardware Used

- Raspberry Pi 4
- Pi Camera Module v2 (imx219, CSI ribbon)
- 4WD acrylic robot chassis kit
- 4x DC geared motors (wired in pairs: left side / right side)
- L298N motor driver
- 12V DC power adapter (for motors)
- Separate 5V power supply (for the Pi)

## How It Works

1. The Pi Camera captures live video frames.
2. A custom-trained **YOLO26n** model (trained on ~200 self-collected images of a
   tennis ball, labeled via Roboflow) detects the ball's bounding box in each frame.
3. The ball's horizontal position and box width determine motor commands:
   - Off-center → turn toward the ball
   - Centered but far → drive forward
   - Centered and close → stop
4. Motor commands are sent via `gpiozero` to an L298N driver controlling all 4 wheels.

## Wiring

| L298N Pin | Raspberry Pi GPIO (BCM) | Physical Pin |
|---|---|---|
| ENA | GPIO 12 | 32 |
| IN1 | GPIO 5  | 29 |
| IN2 | GPIO 6  | 31 |
| ENB | GPIO 13 | 33 |
| IN3 | GPIO 19 | 35 |
| IN4 | GPIO 26 | 37 |
| GND | — | Any Pi GND pin |

- Motor A (OUT1/OUT2) → both LEFT motors, wired in parallel
- Motor B (OUT3/OUT4) → both RIGHT motors, wired in parallel
- L298N 12V/GND terminal → 12V DC power adapter (**not** USB power)
- L298N GND ↔ Pi GND (common ground — required)
- Pi powered separately from its own 5V supply — never share the L298N's onboard regulator

> **Note:** On some compact L298N boards, ENA/ENB have no jumper and must be
> actively driven by GPIO for the motor channel to work at all — if your motors
> don't respond, check this first (see `gpiozero.Motor(..., enable=<pin>)`).

## Software Setup

```bash
# System packages
sudo apt update
sudo apt install -y rpicam-apps python3-picamera2 python3-opencv git

# Python packages (redirect temp dir if low on disk space)
mkdir -p ~/pip_tmp
TMPDIR=~/pip_tmp pip install ultralytics ncnn gpiozero --break-system-packages --no-cache-dir
```

## Training Your Own Model

1. Capture training images: `scripts/collect_images.py`
2. Label them on [Roboflow](https://roboflow.com) (bounding boxes, class name e.g. `ball`)
3. Export dataset in **YOLOv8** format
4. Train in Google Colab (free GPU):
   ```python
   from ultralytics import YOLO
   model = YOLO("yolo26n.pt")
   model.train(data="data.yaml", epochs=100, imgsz=320, batch=16, patience=20)
   ```
5. Export for Pi inference:
   ```python
   model.export(format="ncnn")
   ```
6. Copy the resulting `best_ncnn_model/` folder to `model/` in this repo

## Running

**Test camera + detection only (no motors):**
```bash
python3 scripts/detect_yolo.py
```

**Test motors only (prop wheels off the ground first):**
```bash
python3 scripts/motor_test.py
```

**Run the full ball-follower:**
```bash
python3 scripts/ball_follower.py
```
Press `q` (in the video window) or `Ctrl+C` to stop.

## Tuning

Key parameters at the top of `ball_follower.py`:

| Parameter | Effect |
|---|---|
| `CENTER_MARGIN` | How precisely the ball must be centered before driving forward |
| `TARGET_BOX_WIDTH` | Ball size (px) at which the robot stops — tune to your desired stopping distance |
| `BASE_SPEED` / `TURN_SPEED` | Motor power (0.0–1.0) |

## Model Performance

Trained on ~200 images, single class (`Tennis-Ball`):
- Precision: 99.85%
- Recall: 100%
- mAP50: 99.5%

## License

MIT — feel free to use, modify, and build on this project.
