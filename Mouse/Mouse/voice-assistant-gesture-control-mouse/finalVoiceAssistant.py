import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import finalVirtualMouse as Gesture_Controller
import app
from threading import Thread
from google_search_complete import google_complete


# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# ----------------Variables------------------------
file_exp_status = False
files = []
path = ''
is_awake = True  # Bot status
commands = ['wake up', 'sleep', 'exit', 'hello', 'date', 'time', 'search', 'smart search', 'location', 'stop', 'play', 'mute', 'unmute', 'forward',
            'backward', 'full screen', 'caption', 'speed up', 'slow down', 'launch gesture recognition', 'stop gesture recognition']

# ------------------Functions----------------------


def reply(audio):
    app.ChatBot.addAppMsg(audio)

    print(audio)
    engine.say(audio)
    engine.runAndWait()


def wish():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")
    else:
        reply("Good Evening!")

    reply("I am pixel here to assist you.")
    reply('say "pixel help" to know the commands')


# Set Microphone parameters
with sr.Microphone() as source:
    r.energy_threshold = 500
    r.dynamic_energy_threshold = False

# Audio to String


def record_audio():
    with sr.Microphone() as source:
        r.pause_threshold = 0.6
        voice_data = ''
        audio = r.listen(source, phrase_time_limit=5)

        try:
            voice_data = r.recognize_google(audio)
        except sr.RequestError:
            reply('Sorry my Service is down. Plz check your Internet connection')
        except sr.UnknownValueError:
            print('cant recognize')
            pass
        return voice_data.lower()


# Executes Commands (input: string)
def respond(voice_data):
    global file_exp_status, files, is_awake, path
    print(voice_data)
    voice_data.replace('', '')
    app.eel.addUserMsg(voice_data)

    if is_awake == False:
        if commands[0] in voice_data:
            is_awake = True
            wish()

    # HELP
    elif 'help' in voice_data:
        app.eel.addUserMsg(f"""
                           <h3>Voice Commands</h3>
                           {commands[0]} ➜ to wake the bot<br/>
                           {commands[1]}/bye ➜ to sleep the bot<br/>
                           {commands[2]}/terminate ➜to exit chatbot<br/>
                           <b><u>Basic controls</u></b><br/>
                           {commands[3]}<br/>
                           {commands[4]}<br/>
                           {commands[5]}<br/>
                           {commands[6]}<br/>
                           {commands[7]}<br/>
                           change Command<br/>
                           <b>PPt commands</b><br/>
                           present<br/>next<br/>back<br/>stop present</br>
                           <b><u>Youtube</u></b><br/>
                           {commands[8]}<br/>{commands[9]}<br/>{commands[10]}<br/>{commands[11]}<br/>{commands[12]}<br/>{commands[13]}<br/>{commands[14]}<br/>{commands[15]}<br/>{commands[16]}<br/>{commands[17]}<br/>
                           <b><u>Dynamic Gesture control</u></b><br/>
                           {commands[18]}<br/>{commands[19]}<br/>copy<br/>paste</br>
                           <b><u>File Navigation</u></b><br/>
                           list<br/>open<br/>back
""")

    # STATIC CONTROLS
    elif commands[3] in voice_data:
        wish()

    elif 'what is your name' in voice_data:
        reply('My name is Pixie!')

    elif commands[4] in voice_data:
        reply(today.strftime("%B %d, %Y"))

    elif commands[5] in voice_data:
        reply(str(datetime.datetime.now()).split(" ")[1].split('.')[0])

    elif commands[6] in voice_data:
        reply('Searching for ' + voice_data.split(commands[6])[1])
        url = 'https://google.com/search?q=' + voice_data.split(commands[6])[1]
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')
    
    elif 'smart search' in voice_data:
        query = voice_data.split('smart search')[1].strip()
        reply(f'Smart searching for {query}')
        try:
            search_query, suggestions = google_complete.search_with_completion(query)
            if suggestions:
                reply(f'Found suggestions. Searching for: {search_query}')
            else:
                reply('No suggestions found. Searching original query')
        except:
            reply('Please check your Internet')

    # Change Commands
    elif 'change command' in voice_data:
        reply('Specify command to be changed')
        old_cmd = record_audio()
        old_cmd = old_cmd.split('pixel ')[1]
        app.eel.addUserMsg(old_cmd)
        reply('Specify new command')
        new_cmd = record_audio()
        new_cmd = new_cmd.split('pixel ')[1]
        app.eel.addUserMsg(new_cmd)
        try:
            idx = commands.index(old_cmd)
            commands[idx] = new_cmd
            reply('Command changed successful')
        except:
            reply('failed to change command')

    elif commands[7] in voice_data:
        reply('Which place are you looking for ?')
        temp_audio = record_audio()
        app.eel.addUserMsg(temp_audio)
        reply('Locating...')
        url = 'https://google.nl/maps/place/' + temp_audio + '/&amp;'
        try:
            webbrowser.get().open(url)
            reply('This is what I found Sir')
        except:
            reply('Please check your Internet')

    elif (commands[1] in voice_data) or ('by' in voice_data) or ('sleep' in voice_data):
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif (commands[2] in voice_data) or ('terminate' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        app.ChatBot.close()
        # sys.exit() always raises SystemExit, Handle it in main loop
        sys.exit()

    # YOUTUBE controls
    elif commands[8] in voice_data:
        keyboard.press('k')
        # pyautogui.press('k')
        reply('Paused')

    elif commands[9] in voice_data:
        pyautogui.press('k')
        reply('Continuing')

    elif commands[10] in voice_data:
        pyautogui.press('m')
        reply('muted')

    elif commands[11] in voice_data:
        pyautogui.press('m')
        reply('unmuted')

    elif commands[12] in voice_data:
        pyautogui.press('l')

    elif commands[13] in voice_data:
        pyautogui.press('j')

    elif commands[14] in voice_data:
        pyautogui.press('f')

    elif commands[15] in voice_data:
        pyautogui.press('c')

    elif commands[16] in voice_data:
        pyautogui.press('>')

    elif commands[17] in voice_data:
        pyautogui.press('<')

    elif 'next' in voice_data:
        pyautogui.press('down')
    elif 'back' in voice_data:
        pyautogui.press('up')
    elif 'present' in voice_data:
        pyautogui.press('f5')
    elif 'end' in voice_data or 'stop present' in voice_data:
        pyautogui.press('Esc')

    # DYNAMIC CONTROLS
    elif commands[18] in voice_data:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active')
        else:
            gc = Gesture_Controller.GestureController()
            t = Thread(target=gc.start)
            t.start()
            reply('Launched Successfully')

    elif (commands[19] in voice_data) or ('top gesture recognition' in voice_data):
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped')
        else:
            reply('Gesture recognition is already inactive')

    elif 'copy' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')

    elif 'page' in voice_data or 'pest' in voice_data or 'paste' in voice_data:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')

    # File Navigation (Default Folder set to C://)
    elif 'list' in voice_data:
        counter = 0
        path = 'C://'
        files = listdir(path)
        filestr = ""
        for f in files:
            counter += 1
            print(str(counter) + ':  ' + f)
            filestr += str(counter) + ':  ' + f + '<br>'
        file_exp_status = True
        reply('These are the files in your root directory')
        app.ChatBot.addAppMsg(filestr)

    elif file_exp_status == True:
        counter = 0
        if 'open' in voice_data:
            if isfile(join(path, files[int(voice_data.split(' ')[-1])-1])):
                os.startfile(path + files[int(voice_data.split(' ')[-1])-1])
                file_exp_status = False
            else:
                try:
                    path = path + \
                        files[int(voice_data.split(' ')[-1])-1] + '//'
                    files = listdir(path)
                    filestr = ""
                    for f in files:
                        counter += 1
                        filestr += str(counter) + ':  ' + f + '<br>'
                        print(str(counter) + ':  ' + f)
                    reply('Opened Successfully')
                    app.ChatBot.addAppMsg(filestr)

                except:
                    reply('You do not have permission to access this folder')

        if 'back' in voice_data:
            filestr = ""
            if path == 'C://':
                reply('Sorry, this is the root directory')
            else:
                a = path.split('//')[:-2]
                path = '//'.join(a)
                path += '//'
                files = listdir(path)
                for f in files:
                    counter += 1
                    filestr += str(counter) + ':  ' + f + '<br>'
                    print(str(counter) + ':  ' + f)
                reply('ok')
                app.ChatBot.addAppMsg(filestr)

    else:
        reply('I am not functioned to do this !')

# ------------------Driver Code--------------------


t1 = Thread(target=app.ChatBot.start)
t1.start()

# Lock main thread until Chatbot has started
while not app.ChatBot.started:
    time.sleep(0.5)

wish()
voice_data = None
while True:
    if app.ChatBot.isUserInput():
        # take input from GUI
        voice_data = 'pixel ' + app.ChatBot.popUserInput()
    else:
        # take input from Voice
        voice_data = record_audio()

    # process voice_data
    if 'pixel' in voice_data or 'pixie' in voice_data:
        try:
            # Handle sys.exit()
            respond(voice_data)
        except SystemExit:
            reply("Exit Successfull")
            break
        except:
            # some other exception got raised
            print("EXCEPTION raised while closing.")
            break
