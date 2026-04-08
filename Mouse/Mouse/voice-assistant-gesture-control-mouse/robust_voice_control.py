import speech_recognition as sr
import pyttsx3
import pyautogui
import webbrowser
import os
import subprocess
import time
import threading
from datetime import datetime
from difflib import SequenceMatcher
import random
import numpy as np
import audioop
from google_search_complete import google_complete

# Configure PyAutoGUI safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

class RobustVoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.is_listening = False
        self.command_history = []
        self.responses = {
            'success': ['Done!', 'Completed!', 'Got it!', 'All set!'],
            'error': ['Sorry, that failed', 'Unable to complete', 'Something went wrong'],
            'unknown': ['I didn\'t understand', 'Could you repeat?', 'Not recognized']
        }
        
        try:
            self.commands = self.load_commands()
        except Exception as e:
            print(f"Command loading error: {e}")
            self.commands = {}
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Microphone calibrated")
        except Exception as e:
            print(f"Microphone setup error: {e}")
    
    def safe_pyautogui_action(self, action, *args, **kwargs):
        try:
            return action(*args, **kwargs)
        except Exception as e:
            print(f"PyAutoGUI action failed: {e}")
            return False
    
    def load_commands(self):
        return {
            'notepad': lambda: subprocess.Popen('notepad.exe', shell=True),
            'calculator': lambda: subprocess.Popen('calc.exe', shell=True),
            'chrome': lambda: self.open_browser('chrome'),
            'firefox': lambda: self.open_browser('firefox'),
            'edge': lambda: self.open_browser('msedge'),
            'explorer': lambda: subprocess.Popen('explorer.exe', shell=True),
            'cmd': lambda: subprocess.Popen('cmd.exe', shell=True),
            'paint': lambda: subprocess.Popen('mspaint.exe', shell=True),
            'close': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'f4'),
            'close all': self.close_all_applications,
            'close chrome': lambda: self.close_specific_app('chrome'),
            'close firefox': lambda: self.close_specific_app('firefox'),
            'close edge': lambda: self.close_specific_app('edge'),
            'close notepad': lambda: self.close_specific_app('notepad'),
            'close calculator': lambda: self.close_specific_app('calculator'),
            'close youtube': lambda: self.close_specific_app('youtube'),
            'close browser': lambda: self.close_browser_tabs(),
            'minimize': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'win', 'down'),
            'maximize': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'win', 'up'),
            'switch': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'tab'),
            'desktop': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'win', 'd'),
            'task manager': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'shift', 'esc'),
            'new tab': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 't'),
            'close tab': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'w'),
            'refresh': lambda: self.safe_pyautogui_action(pyautogui.press, 'f5'),
            'back': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'left'),
            'forward': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'right'),
            'copy': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'c'),
            'paste': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'v'),
            'cut': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'x'),
            'select all': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'a'),
            'undo': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'z'),
            'save': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 's'),
            'play': lambda: self.safe_pyautogui_action(pyautogui.press, 'playpause'),
            'pause': lambda: self.safe_pyautogui_action(pyautogui.press, 'playpause'),
            'next': lambda: self.safe_pyautogui_action(pyautogui.press, 'nexttrack'),
            'previous': lambda: self.safe_pyautogui_action(pyautogui.press, 'prevtrack'),
            'volume up': lambda: self.volume_control('up'),
            'volume down': lambda: self.volume_control('down'),
            'mute': lambda: self.safe_pyautogui_action(pyautogui.press, 'volumemute'),
            'click': lambda: self.safe_pyautogui_action(pyautogui.click),
            'right click': lambda: self.safe_pyautogui_action(pyautogui.rightClick),
            'double click': lambda: self.safe_pyautogui_action(pyautogui.doubleClick),
            'scroll up': lambda: self.safe_pyautogui_action(pyautogui.scroll, 3),
            'scroll down': lambda: self.safe_pyautogui_action(pyautogui.scroll, -3),
            'google': self.search_google,
            'smart search': self.smart_search,
            'youtube': self.search_youtube,
            'maps': self.open_maps,
            'weather': self.check_weather,
            'time': self.get_time,
            'date': self.get_date,
            'screenshot': self.take_screenshot,
            'lock screen': lambda: subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True),
            'sleep mode': lambda: subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], shell=True),
            'restart': lambda: subprocess.run(['shutdown', '/r', '/t', '0'], shell=True),
            'shutdown': lambda: subprocess.run(['shutdown', '/s', '/t', '0'], shell=True),
            'task manager': lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'shift', 'esc'),
            'run command': self.run_command,
            'system info': lambda: subprocess.Popen('msinfo32.exe', shell=True),
            'device manager': lambda: subprocess.Popen('devmgmt.msc', shell=True),
            'start gesture': self.start_gesture_control,
            'stop gesture': self.stop_gesture_control,
            'tell me a joke': self.tell_joke,
            'flip a coin': self.flip_coin,
            'roll dice': self.roll_dice,
            'what can you do': self.show_capabilities,
            'open settings': lambda: subprocess.Popen('ms-settings:', shell=True),
            'battery status': self.battery_status,
            'create folder': self.create_folder,
            'what is my name': lambda: self.speak("I am Pixel, your voice assistant"),
            'who are you': lambda: self.speak("I am Pixel, your voice assistant"),
        }
    
    def speak(self, text):
        print(f"TTS: {text}")
        def _speak():
            engine = None
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")
            finally:
                if engine:
                    try:
                        engine.stop()
                        del engine
                    except:
                        pass
        threading.Thread(target=_speak, daemon=True).start()
    
    def ai_noise_reduction(self, audio_data):
        """Simple noise reduction using audio processing"""
        try:
            # Get raw audio data
            raw_data = audio_data.get_raw_data()
            
            # Apply noise reduction using audioop
            # Amplify audio to improve signal
            amplified = audioop.mul(raw_data, audio_data.sample_width, 1.5)
            
            # Apply simple high-pass filter by removing DC offset
            filtered = audioop.bias(amplified, audio_data.sample_width, 0)
            
            # Create new audio data with processed audio
            return sr.AudioData(filtered, audio_data.sample_rate, audio_data.sample_width)
        except Exception as e:
            print(f"Noise reduction error: {e}")
            return audio_data
    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                
                # Apply AI noise reduction
                audio = self.ai_noise_reduction(audio)
                print("Processing speech...")
            
            # Try multiple recognition engines
            try:
                result = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: '{result}'")
                return result
            except sr.UnknownValueError:
                try:
                    result = self.recognizer.recognize_sphinx(audio).lower()
                    print(f"Recognized (offline): '{result}'")
                    return result
                except:
                    return ""
        except sr.WaitTimeoutError:
            return ""
        except sr.RequestError as e:
            print(f"Recognition error: {e}")
            return ""
        except Exception as e:
            print(f"Listen error: {e}")
            return ""
    
    def process_command(self, command):
        try:
            command = command.lower().strip()
            print(f"Processing: '{command}'")
            
            pixel_index = command.find('pixel')
            if pixel_index == -1:
                return False
            
            command = command[pixel_index + 5:].strip()
            print(f"Clean command: '{command}'")
            
            if not command:
                return False
            
            # Advanced command processing
            processed_command = self.process_advanced_command(command)
            if processed_command:
                try:
                    processed_command()
                    self.speak(random.choice(self.responses['success']))
                    return True
                except Exception as e:
                    print(f"Advanced command error: {e}")
            
            # Check for exact matches first
            if command in self.commands:
                try:
                    self.commands[command]()
                    self.speak(random.choice(self.responses['success']))
                    return True
                except Exception as e:
                    print(f"Exact match error: {e}")
            
            # Then check for keyword matches
            for keyword, cmd_func in self.commands.items():
                if keyword in command:
                    try:
                        if keyword in ['google', 'youtube', 'maps', 'weather']:
                            param = command.replace(keyword, '').strip()
                            cmd_func(param) if param else cmd_func()
                        else:
                            cmd_func()
                        self.speak(random.choice(self.responses['success']))
                        return True
                    except Exception as e:
                        print(f"Command error for '{keyword}': {e}")
                        continue
            
            self.speak(random.choice(self.responses['unknown']))
            return False
        except Exception as e:
            print(f"Process command error: {e}")
            return False
    
    def open_browser(self, browser):
        try:
            paths = {
                'chrome': ['chrome.exe'],
                'firefox': ['firefox.exe'],
                'msedge': ['msedge.exe']
            }
            for path in paths.get(browser, []):
                try:
                    subprocess.Popen([path])
                    return True
                except:
                    continue
            webbrowser.open('http://google.com')
            return True
        except:
            return False
    
    def volume_control(self, direction):
        try:
            for _ in range(3):
                self.safe_pyautogui_action(pyautogui.press, 'volumeup' if direction == 'up' else 'volumedown')
            return True
        except:
            return False
    
    def search_google(self, query=""):
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}" if query else "https://www.google.com"
            webbrowser.open(url)
            return True
        except:
            return False
    
    def smart_search(self, query=""):
        try:
            if query:
                search_query, suggestions = google_complete.search_with_completion(query)
                self.speak(f"Smart searching for {search_query}")
            else:
                webbrowser.open("https://www.google.com")
            return True
        except:
            return self.search_google(query)
    
    def search_youtube(self, query=""):
        try:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}" if query else "https://www.youtube.com"
            webbrowser.open(url)
            return True
        except:
            return False
    
    def open_maps(self, location=""):
        try:
            url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}" if location else "https://www.google.com/maps"
            webbrowser.open(url)
            return True
        except:
            return False
    
    def process_advanced_command(self, command):
        """Process advanced and partial commands"""
        try:
            # Volume commands
            if 'volume' in command:
                if 'up' in command or 'increase' in command or 'louder' in command:
                    return lambda: self.volume_control('up')
                elif 'down' in command or 'decrease' in command or 'lower' in command or 'quiet' in command:
                    return lambda: self.volume_control('down')
                else:
                    return lambda: self.volume_control('up')  # Default to up
            
            # Weather commands
            if 'weather' in command:
                location = command.replace('weather', '').replace('what', '').replace('the', '').replace('is', '').strip()
                return lambda: self.check_weather(location)
            
            # Time commands
            if any(word in command for word in ['time', 'clock']):
                return self.get_time
            
            # Date commands
            if any(word in command for word in ['date', 'today']):
                return self.get_date
            
            # Application opening
            if 'open' in command:
                if 'notepad' in command or 'note' in command:
                    return lambda: subprocess.Popen('notepad.exe', shell=True)
                elif 'calculator' in command or 'calc' in command:
                    return lambda: subprocess.Popen('calc.exe', shell=True)
                elif 'chrome' in command:
                    return lambda: self.open_browser('chrome')
                elif 'firefox' in command:
                    return lambda: self.open_browser('firefox')
                elif 'edge' in command:
                    return lambda: self.open_browser('msedge')
            
            # Close commands
            if any(word in command for word in ['close', 'exit', 'quit']):
                if 'all' in command:
                    return self.close_all_applications
                else:
                    return lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'f4')
            
            # Search commands
            if 'search' in command or 'google' in command:
                if 'smart' in command:
                    query = command.replace('smart', '').replace('search', '').replace('google', '').strip()
                    return lambda: self.smart_search(query)
                else:
                    query = command.replace('search', '').replace('google', '').strip()
                    return lambda: self.search_google(query)
            
            # YouTube commands
            if 'youtube' in command:
                query = command.replace('youtube', '').strip()
                return lambda: self.search_youtube(query)
            
            # Screenshot commands
            if any(word in command for word in ['screenshot', 'capture', 'snap']):
                return self.take_screenshot
            
            # Media controls
            if any(word in command for word in ['play', 'pause', 'stop']):
                return lambda: self.safe_pyautogui_action(pyautogui.press, 'playpause')
            
            if any(word in command for word in ['next', 'skip']):
                return lambda: self.safe_pyautogui_action(pyautogui.press, 'nexttrack')
            
            if any(word in command for word in ['previous', 'back', 'last']):
                return lambda: self.safe_pyautogui_action(pyautogui.press, 'prevtrack')
            
            # Mute commands
            if any(word in command for word in ['mute', 'silent', 'quiet']):
                return lambda: self.safe_pyautogui_action(pyautogui.press, 'volumemute')
            
            # System commands
            if any(word in command for word in ['lock', 'secure']):
                return lambda: subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], shell=True)
            
            if any(word in command for word in ['sleep', 'hibernate']):
                return lambda: subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], shell=True)
            
            if 'restart' in command or 'reboot' in command:
                return lambda: subprocess.run(['shutdown', '/r', '/t', '0'], shell=True)
            
            if 'shutdown' in command or 'power off' in command:
                return lambda: subprocess.run(['shutdown', '/s', '/t', '0'], shell=True)
            
            if 'task manager' in command or 'processes' in command:
                return lambda: self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'shift', 'esc')
            
            if 'run command' in command or 'run dialog' in command:
                return self.run_command
            
            # Advanced system info
            if 'system info' in command or 'computer info' in command:
                return lambda: subprocess.Popen('msinfo32.exe', shell=True)
            
            if 'device manager' in command:
                return lambda: subprocess.Popen('devmgmt.msc', shell=True)
            
            # Gesture control commands
            if 'start gesture' in command or 'gesture control' in command:
                return self.start_gesture_control
            
            if 'stop gesture' in command:
                return self.stop_gesture_control
            
            # Fun commands
            if 'joke' in command or 'funny' in command:
                return self.tell_joke
            
            if 'flip coin' in command or 'coin flip' in command:
                return self.flip_coin
            
            if 'roll dice' in command or 'dice roll' in command:
                return self.roll_dice
            
            if 'what can you do' in command or 'capabilities' in command:
                return self.show_capabilities
            
            if 'battery' in command:
                return self.battery_status
            
            if 'create folder' in command or 'new folder' in command:
                return self.create_folder
            
            # Identity commands
            if "what's my name" in command or 'who am i' in command or 'my name' in command:
                return lambda: self.speak("I am Pixel, your voice assistant")
            
            if 'who are you' in command:
                return lambda: self.speak("I am Pixel, your voice assistant")
            
            return None
        except Exception as e:
            print(f"Advanced command processing error: {e}")
            return None
    
    def check_weather(self, location=""):
        try:
            url = f"https://www.google.com/search?q=weather+{location.replace(' ', '+')}" if location else "https://www.google.com/search?q=weather"
            webbrowser.open(url)
            return True
        except:
            return False
    
    def close_specific_app(self, app_name):
        try:
            app_map = {
                'chrome': ['chrome.exe', 'Google Chrome'],
                'firefox': ['firefox.exe', 'Mozilla Firefox'],
                'edge': ['msedge.exe', 'Microsoft Edge'],
                'notepad': ['notepad.exe', 'Notepad'],
                'calculator': ['Calculator.exe', 'Calculator'],
                'youtube': ['chrome.exe', 'firefox.exe', 'msedge.exe']
            }
            
            if app_name in app_map:
                # Try to close by process name
                for process in app_map[app_name]:
                    try:
                        subprocess.run(['taskkill', '/f', '/im', process], shell=True, capture_output=True)
                    except:
                        pass
                
                # Special handling for YouTube (close browser tabs with YouTube)
                if app_name == 'youtube':
                    self.close_youtube_tabs()
                
                self.speak(f"{app_name} closed")
                return True
            return False
        except Exception as e:
            print(f"Close {app_name} error: {e}")
            return False
    
    def close_browser_tabs(self):
        try:
            # Close current tab
            self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'w')
            self.speak("Browser tab closed")
            return True
        except:
            return False
    
    def close_youtube_tabs(self):
        try:
            # Try to close YouTube tabs by checking window titles
            for _ in range(5):  # Check up to 5 tabs
                try:
                    window = pyautogui.getActiveWindow()
                    if window and 'youtube' in window.title.lower():
                        self.safe_pyautogui_action(pyautogui.hotkey, 'ctrl', 'w')
                        time.sleep(0.3)
                    else:
                        break
                except:
                    break
            return True
        except:
            return False
    
    def close_all_applications(self):
        try:
            for _ in range(10):
                try:
                    current_window = pyautogui.getActiveWindow()
                    if current_window is None:
                        break
                    window_title = current_window.title.lower()
                    if any(skip in window_title for skip in ['desktop', 'taskbar', 'start menu', 'pixel']):
                        break
                    self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'f4')
                    time.sleep(0.5)
                except Exception:
                    self.safe_pyautogui_action(pyautogui.hotkey, 'alt', 'f4')
                    time.sleep(0.5)
            self.speak("All applications closed")
            return True
        except Exception as e:
            print(f"Close all error: {e}")
            return False
    
    def get_time(self):
        try:
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
            return True
        except:
            return False
    
    def get_date(self):
        try:
            current_date = datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current_date}")
            return True
        except:
            return False
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            self.speak("Screenshot saved")
            return True
        except:
            return False
    
    def start_gesture_control(self):
        try:
            import requests
            response = requests.post('http://127.0.0.1:5000/start_gesture')
            print("Gesture control started")
            return True
        except:
            print("Failed to start gesture control")
            return False
    
    def stop_gesture_control(self):
        try:
            import requests
            response = requests.post('http://127.0.0.1:5000/stop_gesture')
            print("Gesture control stopped")
            return True
        except:
            print("Failed to stop gesture control")
            return False
    
    def tell_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't programmers like nature? It has too many bugs!"
        ]
        joke = random.choice(jokes)
        self.speak(joke)
        return True
    
    def flip_coin(self):
        result = random.choice(["Heads", "Tails"])
        self.speak(f"The coin landed on {result}")
        return True
    
    def roll_dice(self):
        result = random.randint(1, 6)
        self.speak(f"You rolled a {result}")
        return True
    
    def show_capabilities(self):
        self.speak("I can open apps, control media, search the web, take screenshots, manage windows, tell jokes, flip coins, and much more!")
        return True
    
    def battery_status(self):
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not plugged in"
                self.speak(f"Battery is at {percent}% and {plugged}")
            else:
                self.speak("Battery information not available")
            return True
        except:
            self.speak("Cannot get battery status")
            return False
    
    def create_folder(self):
        try:
            folder_name = f"NewFolder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(folder_name)
            self.speak(f"Created folder {folder_name}")
            return True
        except:
            self.speak("Failed to create folder")
            return False
    
    def run_command(self):
        try:
            self.safe_pyautogui_action(pyautogui.hotkey, 'win', 'r')
            return True
        except:
            return False
    
    def start_listening(self):
        self.is_listening = True
        self.speak("Voice control activated")
        
        failed_attempts = 0
        max_failed = 3
        
        while self.is_listening:
            try:
                command = self.listen()
                if command and len(command.strip()) > 0:
                    failed_attempts = 0
                    
                    if any(word in command for word in ["stop listening", "deactivate", "stop voice"]):
                        self.stop_listening()
                        break
                    
                    # Process command without adding extra pixel
                    if "pixel" not in command:
                        command = f"pixel {command}"
                    
                    self.process_command(command)
                else:
                    failed_attempts += 1
                    if failed_attempts >= max_failed:
                        print("Multiple failed attempts, checking microphone...")
                        try:
                            with sr.Microphone() as source:
                                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        except:
                            pass
                        failed_attempts = 0
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"Voice control error: {e}")
                time.sleep(1)
    
    def stop_listening(self):
        self.is_listening = False
        self.speak("Voice control deactivated")
    
    def get_available_commands(self):
        return list(self.commands.keys())

# Global instance with error handling
try:
    voice_controller = RobustVoiceController()
except Exception as e:
    print(f"Failed to initialize voice controller: {e}")
    voice_controller = None

def start_voice_control():
    if voice_controller:
        try:
            threading.Thread(target=voice_controller.start_listening, daemon=True).start()
        except Exception as e:
            print(f"Failed to start voice control: {e}")

def stop_voice_control():
    if voice_controller:
        try:
            voice_controller.stop_listening()
        except Exception as e:
            print(f"Failed to stop voice control: {e}")

def process_voice_command(command):
    if voice_controller:
        try:
            return voice_controller.process_command(command)
        except Exception as e:
            print(f"Failed to process command: {e}")
            return False
    return False