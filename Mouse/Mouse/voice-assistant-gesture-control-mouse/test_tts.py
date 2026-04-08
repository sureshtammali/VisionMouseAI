import pyttsx3

def test_tts():
    print("Testing Text-to-Speech...")
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        print("Speaking: Hello, this is a test")
        engine.say("Hello, this is a test")
        engine.runAndWait()
        
        print("TTS test completed successfully")
        return True
        
    except Exception as e:
        print(f"TTS test failed: {e}")
        return False

if __name__ == "__main__":
    test_tts()