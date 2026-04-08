from smooth_gesture_control import SmoothGestureController

print("Starting gesture control test...")
print("Camera window should open.")
print("Try pointing with your index finger - cursor should move")
print("Press 'q' in camera window to quit")

try:
    controller = SmoothGestureController()
    controller.start()
except Exception as e:
    print(f"Error: {e}")