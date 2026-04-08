from robust_voice_control import voice_controller

def test_voice_commands():
    print("Testing Voice Commands...")
    print("=" * 50)
    
    # Test basic commands
    test_commands = [
        "pixel open notepad",
        "pixel what time", 
        "pixel volume up",
        "pixel left click",
        "pixel search google test",
        "pixel type text hello world"
    ]
    
    for cmd in test_commands:
        print(f"\nTesting: {cmd}")
        try:
            result = voice_controller.process_command(cmd)
            print(f"Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Available Commands:")
    commands = voice_controller.get_available_commands()
    for i, cmd in enumerate(commands[:20], 1):  # Show first 20
        print(f"{i:2d}. {cmd}")
    print(f"... and {len(commands)-20} more commands")

if __name__ == "__main__":
    test_voice_commands()