import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
from collections import deque
import threading

class SmoothGestureController:
    def __init__(self):
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Camera setup with error handling
        self.cap = None
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Could not open camera with index 0, trying index 1...")
                self.cap = cv2.VideoCapture(1)
            
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                print("Camera initialized successfully")
            else:
                raise Exception("Could not initialize camera")
        except Exception as e:
            print(f"Camera initialization error: {e}")
            raise
        
        # Control variables
        self.is_running = False
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Smoothing and tracking
        self.cursor_history = deque(maxlen=5)
        self.gesture_history = deque(maxlen=10)
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_threshold = 0.3  # seconds
        
        # Gesture states
        self.click_performed = False
        self.drag_mode = False
        self.scroll_mode = False
        self.volume_mode = False
        
        # Calibration
        self.frame_reduction = 100  # pixels from edge
        
        pyautogui.FAILSAFE = False
    
    def get_distance(self, point1, point2):
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def get_angle(self, point1, point2, point3):
        # Calculate angle between three points
        a = math.sqrt((point2.x - point3.x)**2 + (point2.y - point3.y)**2)
        b = math.sqrt((point1.x - point3.x)**2 + (point1.y - point3.y)**2)
        c = math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
        
        try:
            angle = math.acos((a**2 + c**2 - b**2) / (2*a*c))
            return math.degrees(angle)
        except:
            return 0
    
    def detect_gesture(self, landmarks):
        # Get key landmarks
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        
        # Simple finger detection - check if fingertip is above knuckle
        fingers = []
        
        # Thumb (horizontal check)
        fingers.append(thumb_tip.x > thumb_ip.x if thumb_tip.x > landmarks[0].x else thumb_tip.x < thumb_ip.x)
        
        # Other fingers (vertical check - tip above pip joint)
        fingers.append(index_tip.y < index_pip.y)
        fingers.append(middle_tip.y < middle_pip.y) 
        fingers.append(ring_tip.y < ring_pip.y)
        fingers.append(pinky_tip.y < pinky_pip.y)
        
        # Count extended fingers
        up_count = sum(fingers)
        
        # Distance calculations for special gestures
        thumb_index_dist = self.get_distance(thumb_tip, index_tip)
        
        # Debug print
        print(f"Fingers up: {up_count}, Pattern: {fingers}")
        
        # Gesture classification with more gestures
        if up_count == 0:
            return "fist"
        elif up_count == 1 and fingers[1]:  # Only index
            return "point"
        elif up_count == 1 and fingers[0]:  # Only thumb
            return "left_click"
        elif up_count == 2 and fingers[1] and fingers[2]:  # Index + middle
            return "click_drag"  # Changed from peace to click_drag
        elif up_count == 2 and fingers[0] and fingers[1]:  # Thumb + index
            return "peace"  # New peace gesture
        elif up_count == 3 and fingers[1] and fingers[2] and fingers[3]:  # Index + middle + ring
            return "three_fingers"
        elif up_count == 4 and not fingers[0]:  # Four fingers without thumb
            return "four_fingers"
        elif up_count >= 4:
            return "open_palm"
        elif up_count == 1 and fingers[4]:  # Only pinky
            return "pinky"
        elif up_count == 2 and fingers[0] and fingers[4]:  # Thumb + pinky
            return "call_me"
        else:
            return "point"  # Default
    
    def smooth_cursor_movement(self, x, y):
        # Add current position to history
        self.cursor_history.append((x, y))
        
        # Calculate smoothed position
        if len(self.cursor_history) >= 3:
            # Use weighted average for smoothing
            weights = [0.1, 0.3, 0.6]  # More weight to recent positions
            smooth_x = sum(pos[0] * weight for pos, weight in zip(self.cursor_history, weights[-len(self.cursor_history):]))
            smooth_y = sum(pos[1] * weight for pos, weight in zip(self.cursor_history, weights[-len(self.cursor_history):]))
            return int(smooth_x), int(smooth_y)
        
        return x, y
    
    def map_to_screen(self, hand_x, hand_y, frame_width, frame_height):
        # Map hand coordinates to screen coordinates with frame reduction
        screen_x = np.interp(hand_x, [self.frame_reduction, frame_width - self.frame_reduction], 
                           [0, self.screen_width])
        screen_y = np.interp(hand_y, [self.frame_reduction, frame_height - self.frame_reduction], 
                           [0, self.screen_height])
        
        # Clamp to screen bounds
        screen_x = max(0, min(self.screen_width - 1, screen_x))
        screen_y = max(0, min(self.screen_height - 1, screen_y))
        
        return int(screen_x), int(screen_y)
    
    def execute_gesture_action(self, gesture, landmarks):
        try:
            current_time = time.time()
            
            # Get index finger position for cursor control
            index_tip = landmarks[8]
            frame_height, frame_width = 480, 640
            cursor_x, cursor_y = self.map_to_screen(
                index_tip.x * frame_width, 
                index_tip.y * frame_height, 
                frame_width, 
                frame_height
            )
            
            # Smooth cursor movement
            smooth_x, smooth_y = self.smooth_cursor_movement(cursor_x, cursor_y)
            
            # Always move cursor for point gesture or when no specific gesture
            if gesture in ["point", "unknown"]:
                try:
                    pyautogui.moveTo(smooth_x, smooth_y, duration=0.05)
                except:
                    pass
                # Reset other modes
                if self.drag_mode:
                    try:
                        pyautogui.mouseUp(button='left')
                    except:
                        pass
                    self.drag_mode = False
                self.scroll_mode = False
                self.volume_mode = False
                self.click_performed = False
                return
            
            # Prevent rapid repeated actions
            if self.last_gesture == gesture and (current_time - self.gesture_start_time) < self.gesture_threshold:
                return
            
            # Update gesture timing
            if self.last_gesture != gesture:
                self.gesture_start_time = current_time
                self.last_gesture = gesture
            
            # Execute actions based on gesture
            if gesture == "click_drag":
                # Right click (Index + Middle fingers)
                if not self.click_performed:
                    try:
                        pyautogui.rightClick()
                        self.click_performed = True
                        print("Right click")
                    except Exception as e:
                        print(f"Right click error: {e}")
            
            elif gesture == "left_click":
                # Left click (once per gesture) - only if not in drag mode
                if not self.click_performed and not self.drag_mode:
                    try:
                        pyautogui.click()
                        self.click_performed = True
                        print("Left click")
                    except Exception as e:
                        print(f"Left click error: {e}")
            
            elif gesture == "peace":
                # Right click (Thumb + Index)
                if not self.click_performed:
                    try:
                        pyautogui.rightClick()
                        self.click_performed = True
                        print("Right click")
                    except Exception as e:
                        print(f"Right click error: {e}")
            
            elif gesture == "thumbs_up":
                # Double click
                if not self.click_performed:
                    try:
                        pyautogui.doubleClick()
                        self.click_performed = True
                        print("Double click")
                    except Exception as e:
                        print(f"Double click error: {e}")
            
            elif gesture == "three_fingers":
                # Volume control (horizontal movement)
                if not self.volume_mode:
                    self.volume_mode = True
                    self.volume_start_x = cursor_x
                    print("Volume control mode ON")
                else:
                    volume_diff = cursor_x - self.volume_start_x
                    if abs(volume_diff) > 30:
                        try:
                            if volume_diff > 0:
                                pyautogui.press('volumeup')
                                print("Volume up")
                            else:
                                pyautogui.press('volumedown')
                                print("Volume down")
                            self.volume_start_x = cursor_x
                        except Exception as e:
                            print(f"Volume control error: {e}")
            
            elif gesture == "four_fingers":
                # Scroll control (vertical movement)
                if not self.scroll_mode:
                    self.scroll_mode = True
                    self.scroll_start_y = cursor_y
                    print("Scroll mode ON")
                else:
                    scroll_diff = self.scroll_start_y - cursor_y
                    if abs(scroll_diff) > 20:
                        try:
                            scroll_amount = int(scroll_diff / 20)
                            pyautogui.scroll(scroll_amount)
                            print(f"Scroll: {scroll_amount}")
                            self.scroll_start_y = cursor_y
                        except Exception as e:
                            print(f"Scroll error: {e}")
            
            elif gesture == "pinch":
                # Reserved for future use
                pass
            
            elif gesture == "pinky":
                # Click and drag (Pinky finger)
                if not self.drag_mode:
                    try:
                        pyautogui.mouseDown(button='left')
                        self.drag_mode = True
                        self.click_performed = True
                        print("Drag mode ON (Pinky)")
                    except Exception as e:
                        print(f"Drag start error: {e}")
                try:
                    pyautogui.moveTo(smooth_x, smooth_y, duration=0.05)
                except:
                    pass
            
            elif gesture == "call_me":
                # Take screenshot
                if not self.click_performed:
                    try:
                        pyautogui.hotkey('win', 'shift', 's')
                        self.click_performed = True
                        print("Screenshot")
                    except Exception as e:
                        print(f"Screenshot error: {e}")
            
            elif gesture == "open_palm":
                # Release all modes and actions
                if self.drag_mode:
                    try:
                        pyautogui.mouseUp(button='left')
                        self.drag_mode = False
                        print("Drag mode OFF")
                    except Exception as e:
                        print(f"Drag stop error: {e}")
                self.scroll_mode = False
                self.volume_mode = False
                self.click_performed = False
                print("Reset all modes")
                
        except Exception as e:
            print(f"Gesture action error: {e}")
    
    def draw_landmarks_and_info(self, image, results, gesture):
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        
        # Draw gesture info with larger text
        cv2.putText(image, f"Gesture: {gesture}", (10, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        # Draw mode indicators
        y_offset = 80
        if self.drag_mode:
            cv2.putText(image, "DRAG MODE ACTIVE", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            y_offset += 40
        
        # Draw instructions
        instructions = [
            "Point: Move cursor",
            "Thumb: Left click",
            "Index+Middle: Right click", 
            "Pinky: Click & drag",
            "3 fingers: Volume control",
            "4 fingers: Scroll",
            "Call me: Screenshot",
            "Open palm: Reset"
        ]
        
        for i, instruction in enumerate(instructions):
            y_pos = image.shape[0] - 250 + i*20
            if y_pos > 0:  # Only draw if within image bounds
                cv2.putText(image, instruction, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return image
    
    def start(self):
        if not self.cap or not self.cap.isOpened():
            print("Error: Camera not available")
            return False
            
        self.is_running = True
        print("Gesture Control Started")
        print("Gestures:")
        print("- Point (Index finger): Move cursor")
        print("- Thumb up: Left click")
        print("- Index + Middle: Right click")
        print("- Three fingers: Volume control (move left/right)")
        print("- Four fingers: Scroll (move up/down)")
        print("- Pinky: Click and drag")
        print("- Call me (Thumb + Pinky): Screenshot")
        print("- Open palm: Reset all modes")
        print("Press 'q' to quit")
        
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                if not ret or not self.is_running:
                    print("Camera read failed or stop requested")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                results = self.hands.process(rgb_frame)
                
                gesture = "none"
                if results.multi_hand_landmarks:
                    # Use first detected hand
                    hand_landmarks = results.multi_hand_landmarks[0]
                    gesture = self.detect_gesture(hand_landmarks.landmark)
                    
                    # Execute gesture action
                    self.execute_gesture_action(gesture, hand_landmarks.landmark)
                else:
                    # Reset modes when no hand detected
                    if self.drag_mode:
                        try:
                            pyautogui.mouseUp(button='left')
                            print("Drag mode OFF - no hand detected")
                        except:
                            pass
                        self.drag_mode = False
                    self.scroll_mode = False
                    self.volume_mode = False
                    self.click_performed = False
                
                # Draw visualization
                frame = self.draw_landmarks_and_info(frame, results, gesture)
                
                # Display frame
                cv2.imshow('Smooth Gesture Control', frame)
                
                # Check for quit or stop signal
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or not self.is_running:
                    print("Stop signal received")
                    break
        except Exception as e:
            print(f"Error in gesture control loop: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        print("Stop method called - setting is_running to False")
        self.is_running = False
        
        # Small delay to let the loop exit
        time.sleep(0.1)
        
        # Release mouse if in drag mode
        if self.drag_mode:
            try:
                pyautogui.mouseUp(button='left')
                print("Released mouse drag")
            except Exception as e:
                print(f"Mouse release error: {e}")
        
        # Release camera
        if self.cap and self.cap.isOpened():
            try:
                self.cap.release()
                print("Camera released")
            except Exception as e:
                print(f"Camera release error: {e}")
        
        # Close OpenCV windows
        try:
            cv2.destroyAllWindows()
            print("OpenCV windows closed")
        except Exception as e:
            print(f"Window close error: {e}")
        
        print("Gesture Control Stopped")

# Global instance
gesture_controller = SmoothGestureController()

def start_gesture_control():
    threading.Thread(target=gesture_controller.start, daemon=True).start()

def stop_gesture_control():
    try:
        gesture_controller.stop()
    except:
        pass

if __name__ == "__main__":
    gesture_controller.start()