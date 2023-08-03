import speech_recognition as sr
import pyaudio
import time
import pyttsx3
import openai
import os
from dotenv import load_dotenv
import keyboard
import json

load_dotenv()
token = os.environ.get("apikey")
openai.api_key = token
prevConversation = ""
engine = pyttsx3.init()

def chat_with_gpt(text):
    global prevConversation
    message = ''
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a concise and helpful assistant. I will start by saying something and then you will respond. We will continue this until I say 'Goodbye'"},
            {"role": "system", "content": "This is the context to the conversation that we are having. If there is nothing after the colon that means this is the start of the conversation: "+ prevConversation},
            {"role": "user", "content": text}
        ],
        stream=True
    )
    for i in range(10):
        for chunk in response:
            if 'choices' in chunk:
                if 'message' in chunk['choices'][0]:
                    message_chunk = chunk['choices'][0]['message']['content']
                    message += message_chunk

                    print("AI Chunk: ", message_chunk)

                    # Extract the word types from the message using regex
                    prevConversation = prevConversation + ". Human: " + text + ". AI: " + message_chunk
        if message == '':
            print("No message in response from OpenAI")
        print(message)
        time.sleep(1)
    return message






voices = engine.getProperty('voices')

keepGoing = True
while keepGoing:
    # Create a recognizer object
    r = sr.Recognizer()
    # Create a microphone object
    with sr.Microphone() as source:
        while True:
            # Check if 'z' is being pressed
            if not keyboard.is_pressed('z'):
                time.sleep(0.1)
                continue

            print("Please speak...")
            try:
                # Record the audio until silence is detected
                audio_data = r.listen(source, timeout=2)
                print("Recording ended.")

                # Attempt to transcribe the audio
                text = r.recognize_google(audio_data)
                print("You said: " + text)

                # ... other parts of your code ...

                if text.lower() == "goodbye":
                    keepGoing = False
                    break
                elif text.lower().startswith("save context ") or text.lower().startswith("save contacts ") or text.lower().startswith("dave context ") or text.lower().startswith("dave contacts "):
                    filename = text[13:] + '.json'
                    with open(filename, 'w') as file:
                        json.dump(prevConversation, file)
                    prevConversation = ""
                    print("Context saved as " + filename)
                    continue
                elif text.lower().startswith("open context ") or text.lower().startswith("open contacts "):
                    filename = text[13:] + '.json'
                    try:
                        with open(filename, 'r') as file:
                            prevConversation = json.load(file)
                        print("Context loaded from " + filename)
                    except FileNotFoundError:
                        print("No such file: " + filename)
                    continue
                elif text.lower().startswith("list context") or text.lower().startswith("list contacts"):
                    files = [f for f in os.listdir() if f.endswith('.json')]
                    for i in range(len(files)):
                        files[i] = files[i][:-5]
                    fileNames = ', '.join(files)
                    print("JSON files: " + fileNames)
                    continue

                chat_with_gpt(text)  # Call the function and let it handle printing

            except sr.WaitTimeoutError:
                print("Silence detected, recording stopped.")
                break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

