import sys
import traceback

def test_gesture_dependencies():
    print("Testing gesture control dependencies...")
    
    # Test OpenCV
    try:
        import cv2
        print("[OK] OpenCV imported successfully")
        
        # Test camera
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[OK] Camera accessible")
            cap.release()
        else:
            print("[ERROR] Camera not accessible")
    except Exception as e:
        print(f"[ERROR] OpenCV error: {e}")
    
    # Test MediaPipe
    try:
        import mediapipe as mp
        print("[OK] MediaPipe imported successfully")
    except Exception as e:
        print(f"[ERROR] MediaPipe error: {e}")
    
    # Test PyAutoGUI
    try:
        import pyautogui
        print("[OK] PyAutoGUI imported successfully")
        pyautogui.FAILSAFE = False
    except Exception as e:
        print(f"[ERROR] PyAutoGUI error: {e}")
    
    # Test gesture controller
    try:
        from smooth_gesture_control import SmoothGestureController
        controller = SmoothGestureController()
        print("[OK] Gesture controller created successfully")
        return controller
    except Exception as e:
        print(f"[ERROR] Gesture controller error: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    controller = test_gesture_dependencies()
    if controller:
        print("\n[SUCCESS] All dependencies working! Gesture control should work.")
    else:
        print("\n[FAILED] Some dependencies failed. Please install missing packages.")