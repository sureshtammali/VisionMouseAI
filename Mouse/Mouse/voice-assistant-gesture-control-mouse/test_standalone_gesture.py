from smooth_gesture_control import SmoothGestureController
import time

def test_gesture_control():
    print("Starting gesture control test...")
    print("Move your hand in front of the camera")
    print("Gestures:")
    print("- Point (index finger): Move cursor")
    print("- Fist: Click and drag") 
    print("- Peace sign: Right click")
    print("- Open palm: Reset modes")
    print("Press Ctrl+C to stop")
    
    try:
        controller = SmoothGestureController()
        controller.start()
    except KeyboardInterrupt:
        print("\nStopping gesture control...")
        controller.stop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gesture_control()