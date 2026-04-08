# Voice Assistant with Gesture Control Virtual Mouse

## Abstract
The Voice Assistant with Gesture Control Virtual Mouse revolutionizes human-computer interaction by enabling seamless control through voice commands and hand gestures, minimizing the need for physical contact. Combining advanced Machine Learning (ML) and Computer Vision (CV) algorithms, this system efficiently recognizes static and dynamic gestures, enhancing versatility and usability.

A key feature is its hardware-free design, eliminating the need for external devices. The system utilizes Convolutional Neural Networks (CNN) through MediaPipe and pybind11 to process gestures. MediaPipe's Hand detection capabilities enable direct hand interaction, while an additional module supports gloves of any consistent color, expanding gesture recognition possibilities.

This innovative system transforms input and output processes by allowing users to interact with their computers using natural language and gestures. It promotes inclusivity and accessibility, making it a versatile solution for various user demographics. The hardware independence of the system further enhances adaptability, positioning it as a promising tool in the evolving field of human-computer interaction.

## Features
- **Voice Commands**: Execute tasks via speech recognition.
- **Gesture Control**: Control the virtual mouse using hand gestures.
- **Hardware-free Design**: No additional hardware required for gesture recognition.
- **Convolutional Neural Networks (CNN)**: Efficient gesture processing using MediaPipe.
- **Glove Compatibility**: Recognizes gestures even when wearing gloves of a consistent color.

## Prerequisites

Before running the system, make sure you have installed the following dependencies:

```bash
pip install pyttsx3 SpeechRecognition pyautogui opencv-python mediapipe screen_brightness_control wikipedia pynput pycaw
