"""
Motor test - L298N driving 4 motors (2 per side, wired in parallel)
Confirms wiring/direction before combining with ball tracking.

Run: python3 motor_test.py
"""

from gpiozero import Motor
from time import sleep

# Left side = Motor A on L298N, Right side = Motor B
# gpiozero.Motor(forward, backward) - PWM speed handled automatically
left = Motor(forward=5, backward=6, enable=12, pwm=True)
right = Motor(forward=19, backward=26, enable=13, pwm=True)

def stop():
    left.stop()
    right.stop()

try:
    print("Both sides forward (2s)...")
    left.forward(0.6)
    right.forward(0.6)
    sleep(2)
    stop()
    sleep(1)

    print("Both sides backward (2s)...")
    left.backward(0.6)
    right.backward(0.6)
    sleep(2)
    stop()
    sleep(1)

    print("Turn left in place (left back, right forward)...")
    left.backward(0.6)
    right.forward(0.6)
    sleep(1.5)
    stop()
    sleep(1)

    print("Turn right in place (left forward, right back)...")
    left.forward(0.6)
    right.backward(0.6)
    sleep(1.5)
    stop()

    print("Test complete.")

except KeyboardInterrupt:
    pass
finally:
    stop()
