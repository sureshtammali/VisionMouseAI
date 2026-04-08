#!/usr/bin/env python3
"""
Quick test for gesture control functionality
"""

def test_gesture_control():
    print("Testing gesture control...")
    
    try:
        from smooth_gesture_control import SmoothGestureController
        
        print("✓ Gesture controller imported successfully")
        
        # Create controller
        controller = SmoothGestureController()
        print("✓ Controller created successfully")
        
        print("\n=== GESTURE CONTROL TEST ===")
        print("Camera window should open now...")
        print("Try these gestures:")
        print("1. Point with index finger - cursor should move")
        print("2. Make a fist - should start drag mode")
        print("3. Peace sign (index + middle) - right click")
        print("4. Open palm - reset all modes")
        print("\nWatch console for debug output!")
        print("Press 'q' in camera window to quit")
        print("=" * 40)
        
        # Start gesture control
        controller.start()
        
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gesture_control()