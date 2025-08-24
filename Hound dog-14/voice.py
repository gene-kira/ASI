import pyttsx3

voice_engine = pyttsx3.init()
voice_engine.setProperty('rate', 150)
voice_engine.setProperty('volume', 1.0)

def speak(text):
    voice_engine.say(text)
    voice_engine.runAndWait()

