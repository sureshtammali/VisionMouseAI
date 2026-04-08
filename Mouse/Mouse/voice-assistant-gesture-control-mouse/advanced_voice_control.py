import speech_recognition as sr
import pyttsx3
import pyautogui
import webbrowser
import os
import subprocess
import json
import re
from datetime import datetime
import threading
import time
from difflib import SequenceMatcher
import random
try:
    import psutil
except ImportError:
    psutil = None
try:
    import requests
except ImportError:
    requests = None
from collections import defaultdict
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
except ImportError:
    nltk = None
from google_search_complete import google_complete

class AdvancedVoiceController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
        self.is_listening = False
        self.commands = self.load_commands()
        self.command_history = []
        self.context = {'last_app': None, 'last_search': None, 'user_preferences': {}}
        self.synonyms = self.load_synonyms()
        self.learning_data = defaultdict(int)
        self.confidence_threshold = 0.5
        self.adaptive_responses = self.load_adaptive_responses()
        
        # Initialize NLP components
        try:
            if nltk:
                self.stop_words = set(stopwords.words('english'))
            else:
                self.stop_words = set()
        except:
            self.stop_words = set()
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def load_commands(self):
        return {
            # System Commands
            'open': self.open_application,
            'close': self.close_application,
            'minimize': lambda: pyautogui.hotkey('win', 'down'),
            'maximize': lambda: pyautogui.hotkey('win', 'up'),
            'screenshot': lambda: pyautogui.screenshot().save(f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'),
            
            # Navigation
            'go back': lambda: pyautogui.hotkey('alt', 'left'),
            'go forward': lambda: pyautogui.hotkey('alt', 'right'),
            'refresh': lambda: pyautogui.press('f5'),
            'new tab': lambda: pyautogui.hotkey('ctrl', 't'),
            'close tab': lambda: pyautogui.hotkey('ctrl', 'w'),
            
            # Text Operations
            'copy': lambda: pyautogui.hotkey('ctrl', 'c'),
            'paste': lambda: pyautogui.hotkey('ctrl', 'v'),
            'cut': lambda: pyautogui.hotkey('ctrl', 'x'),
            'undo': lambda: pyautogui.hotkey('ctrl', 'z'),
            'redo': lambda: pyautogui.hotkey('ctrl', 'y'),
            'select all': lambda: pyautogui.hotkey('ctrl', 'a'),
            'save': lambda: pyautogui.hotkey('ctrl', 's'),
            
            # Media Controls
            'play': lambda: pyautogui.press('playpause'),
            'pause': lambda: pyautogui.press('playpause'),
            'next': lambda: pyautogui.press('nexttrack'),
            'previous': lambda: pyautogui.press('prevtrack'),
            'volume up': lambda: [pyautogui.press('volumeup') for _ in range(3)],
            'volume down': lambda: [pyautogui.press('volumedown') for _ in range(3)],
            'mute': lambda: pyautogui.press('volumemute'),
            
            # Window Management
            'switch window': lambda: pyautogui.hotkey('alt', 'tab'),
            'task manager': lambda: pyautogui.hotkey('ctrl', 'shift', 'esc'),
            'desktop': lambda: pyautogui.hotkey('win', 'd'),
            
            # Search and Web
            'search': self.web_search,
            'smart search': self.smart_search,
            'youtube': self.youtube_search,
            'maps': self.maps_search,
            'weather': self.weather_search,
            
            # System Info
            'time': self.get_time,
            'date': self.get_date,
            
            # Custom Commands
            'type': self.type_text,
            'click': self.click_position,
            'scroll up': lambda: pyautogui.scroll(3),
            'scroll down': lambda: pyautogui.scroll(-3),
            'calculate': self.calculate_math,
            'repeat': self.repeat_last_command,
            'learn': self.learn_custom_command,
            'status': self.system_status,
            'news': self.get_news,
            'translate': self.translate_text,
            'note': self.take_note,
        }
    
    def load_synonyms(self):
        return {
            'open': ['launch', 'start', 'run', 'execute'],
            'close': ['exit', 'quit', 'shut', 'end'],
            'search': ['find', 'look for', 'google', 'smart search'],
            'type': ['write', 'enter', 'input'],
            'click': ['press', 'tap', 'select'],
            'volume up': ['increase volume', 'louder', 'turn up'],
            'volume down': ['decrease volume', 'quieter', 'turn down'],
            'play': ['start playing', 'resume'],
            'pause': ['stop playing', 'halt'],
            'next': ['skip', 'forward', 'next track'],
            'previous': ['back', 'last track', 'rewind']
        }
    
    def fuzzy_match(self, input_text, commands, threshold=0.6):
        best_match = None
        best_score = 0
        
        for cmd in commands:
            score = SequenceMatcher(None, input_text.lower(), cmd.lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = cmd
        
        return best_match, best_score
    
    def load_adaptive_responses(self):
        return {
            'greeting': ['Hello!', 'Hi there!', 'Hey!', 'Good to see you!'],
            'success': ['Done!', 'Completed!', 'Got it!', 'All set!'],
            'error': ['Sorry, that failed', 'Oops, something went wrong', 'Unable to complete'],
            'unknown': ['I didn\'t understand that', 'Could you repeat?', 'Not sure what you mean']
        }
    
    def smart_response(self, category):
        responses = self.adaptive_responses.get(category, ['OK'])
        return random.choice(responses)
    
    def learn_from_usage(self, command, success):
        if success:
            self.learning_data[command] += 1
        else:
            self.learning_data[command] -= 1
    
    def preprocess_command(self, text):
        try:
            if nltk:
                tokens = word_tokenize(text.lower())
                filtered = [w for w in tokens if w not in self.stop_words and w.isalpha()]
                return ' '.join(filtered)
            else:
                return text.lower()
        except:
            return text.lower()
    
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
            return self.recognizer.recognize_google(audio).lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "error"
    
    def process_command(self, command):
        command = command.lower().strip()
        original_command = command
        
        # Preprocess with NLP
        processed_command = self.preprocess_command(command)
        
        # Remove wake word
        if command.startswith('pixel'):
            command = command[5:].strip()
        
        # Add to history and learn
        self.command_history.append(original_command)
        if len(self.command_history) > 10:
            self.command_history.pop(0)
        
        # Multi-layer processing
        success = (self.execute_exact_command(command) or 
                  self.execute_synonym_command(command) or 
                  self.execute_fuzzy_command(command) or 
                  self.advanced_command_processing(command))
        
        # Learn from result
        self.learn_from_usage(command, success)
        
        # Adaptive response
        if success:
            response = self.smart_response('success')
        else:
            response = self.smart_response('unknown')
            
        return success
    
    def execute_exact_command(self, command):
        for cmd_key, cmd_func in self.commands.items():
            if command == cmd_key or command.startswith(cmd_key + ' '):
                try:
                    if cmd_key in ['search', 'smart search', 'youtube', 'maps', 'weather', 'type', 'open', 'close', 'calculate']:
                        param = command.replace(cmd_key, '').strip()
                        if param:
                            cmd_func(param)
                            return True
                    else:
                        result = cmd_func()
                        if isinstance(result, list):
                            for action in result:
                                action()
                        return True
                except Exception:
                    self.speak("Command failed")
                    return False
        return False
    
    def execute_synonym_command(self, command):
        for base_cmd, synonyms in self.synonyms.items():
            for synonym in synonyms:
                if command == synonym or command.startswith(synonym + ' '):
                    if base_cmd in self.commands:
                        try:
                            param = command.replace(synonym, '').strip()
                            if base_cmd in ['search', 'smart search', 'youtube', 'maps', 'weather', 'type', 'open', 'close']:
                                if param:
                                    self.commands[base_cmd](param)
                                    return True
                            else:
                                result = self.commands[base_cmd]()
                                if isinstance(result, list):
                                    for action in result:
                                        action()
                                return True
                        except Exception:
                            return False
        return False
    
    def execute_fuzzy_command(self, command):
        all_commands = list(self.commands.keys())
        for synonyms in self.synonyms.values():
            all_commands.extend(synonyms)
        
        match, score = self.fuzzy_match(command, all_commands, 0.7)
        if match:
            # Find the base command
            base_cmd = match
            for cmd, syns in self.synonyms.items():
                if match in syns:
                    base_cmd = cmd
                    break
            
            if base_cmd in self.commands:
                try:
                    self.commands[base_cmd]()
                    return True
                except Exception:
                    return False
        return False
    
    def advanced_command_processing(self, command):
        # Number-based commands
        if 'press' in command:
            key = command.replace('press', '').strip()
            pyautogui.press(key)
            return True
        
        # Application launching with fuzzy matching
        if 'launch' in command or 'start' in command:
            app = command.replace('launch', '').replace('start', '').strip()
            self.open_application(app)
            return True
        
        # Dynamic typing
        if 'write' in command or 'enter' in command:
            text = command.replace('write', '').replace('enter', '').strip()
            pyautogui.typewrite(text)
            return True
        
        # Math calculations
        if any(op in command for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            result = self.calculate(command)
            if result:
                self.speak(f"The result is {result}")
                return True
        
        return False
    
    def open_application(self, app_name):
        app_map = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'explorer': 'explorer.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
        }
        
        app_name = app_name.lower()
        for key, exe in app_map.items():
            if key in app_name:
                try:
                    subprocess.Popen(exe, shell=True)
                    self.speak(f"Opening {key}")
                    return
                except:
                    pass
        
        # Try direct execution
        try:
            subprocess.Popen(app_name, shell=True)
            self.speak(f"Opening {app_name}")
        except:
            self.speak(f"Could not open {app_name}")
    
    def close_application(self, app_name):
        pyautogui.hotkey('alt', 'f4')
        self.speak("Closing application")
    
    def web_search(self, query):
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        self.speak(f"Searching for {query}")
    
    def smart_search(self, query):
        try:
            search_query, suggestions = google_complete.search_with_completion(query)
            if suggestions:
                self.speak(f"Smart searching for {search_query}")
            else:
                self.speak(f"Searching for {query}")
        except:
            self.web_search(query)
    
    def youtube_search(self, query):
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        self.speak(f"Searching YouTube for {query}")
    
    def maps_search(self, location):
        url = f"https://www.google.com/maps/search/{location.replace(' ', '+')}"
        webbrowser.open(url)
        self.speak(f"Finding {location} on maps")
    
    def weather_search(self, location):
        url = f"https://www.google.com/search?q=weather+{location.replace(' ', '+')}"
        webbrowser.open(url)
        self.speak(f"Getting weather for {location}")
    
    def get_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        self.speak(f"The time is {current_time}")
    
    def get_date(self):
        current_date = datetime.now().strftime("%B %d, %Y")
        self.speak(f"Today is {current_date}")
    
    def type_text(self, text):
        pyautogui.typewrite(text)
        self.speak(f"Typed {text}")
    
    def click_position(self, position="center"):
        if position == "center":
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2)
        self.speak("Clicked")
    
    def calculate_math(self, expression):
        result = self.calculate(expression)
        if result:
            self.speak(f"The result is {result}")
        else:
            self.speak("Could not calculate that")
    
    def repeat_last_command(self):
        if self.command_history:
            last_cmd = self.command_history[-1]
            self.speak(f"Repeating: {last_cmd}")
            self.process_command(last_cmd)
        else:
            self.speak("No previous command to repeat")
    
    def learn_custom_command(self, command_def):
        parts = command_def.split(' as ')
        if len(parts) == 2:
            name, action = parts
            self.commands[name.strip()] = lambda: pyautogui.typewrite(action.strip())
            self.speak(f"Learned new command: {name}")
        else:
            self.speak("Use format: learn [name] as [action]")
    
    def system_status(self):
        if psutil:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            self.speak(f"CPU usage: {cpu}%, Memory usage: {memory}%")
        else:
            self.speak("System monitoring not available")
    
    def get_news(self, topic="general"):
        self.speak(f"Opening news about {topic}")
        webbrowser.open(f"https://news.google.com/search?q={topic}")
    
    def translate_text(self, text):
        self.speak(f"Translating: {text}")
        webbrowser.open(f"https://translate.google.com/?text={text}")
    
    def take_note(self, note):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("voice_notes.txt", "a") as f:
            f.write(f"[{timestamp}] {note}\n")
        self.speak("Note saved")
    
    def calculate(self, expression):
        # Simple math parser
        expression = expression.replace('plus', '+').replace('minus', '-')
        expression = expression.replace('times', '*').replace('divided by', '/')
        
        # Extract numbers and operators
        numbers = re.findall(r'\d+', expression)
        if len(numbers) >= 2:
            try:
                if '+' in expression:
                    return int(numbers[0]) + int(numbers[1])
                elif '-' in expression:
                    return int(numbers[0]) - int(numbers[1])
                elif '*' in expression:
                    return int(numbers[0]) * int(numbers[1])
                elif '/' in expression:
                    return int(numbers[0]) / int(numbers[1])
            except:
                pass
        return None
    
    def start_listening(self):
        self.is_listening = True
        self.speak("Voice control activated")
        
        while self.is_listening:
            command = self.listen()
            if command and command != "error":
                if "stop listening" in command or "deactivate" in command:
                    self.stop_listening()
                    break
                elif command.startswith('pixel') or len(command.split()) > 1:
                    success = self.process_command(command)
                    if not success:
                        self.speak("Command not recognized")
            time.sleep(0.1)
    
    def stop_listening(self):
        self.is_listening = False
        self.speak("Voice control deactivated")
    
    def add_custom_command(self, command_name, action):
        self.commands[command_name] = action
    
    def get_available_commands(self):
        return list(self.commands.keys())

# Global instance
voice_controller = AdvancedVoiceController()

def start_voice_control():
    threading.Thread(target=voice_controller.start_listening, daemon=True).start()

def stop_voice_control():
    try:
        voice_controller.stop_listening()
    except:
        pass

def process_voice_command(command):
    return voice_controller.process_command(command)