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
voiceID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"

totalTokens = 100

def checkFinished(response):
    global totalTokens
    response = response.split()
    for i in range(len(response)):
        tokens = tokens + len(response[i])
    print(tokens)
    if tokens < totalTokens * 4:
        return False
    

def chat_with_gpt(text):
    global prevConversation
    global voiceID
    global totalTokens
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a concise and helpful assistant. I will start by saying something and then you will respond. We will continue this until I say 'Goodbye'"},
            {"role": "system", "content": "This is the context to the conversation that we are having. If there is nothing after the colon that means this is the start of the conversation: "+ prevConversation},
            {"role": "user", "content": text}
        ],
        max_tokens=totalTokens,
    )
    message = response['choices'][0]['message']['content']

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    #choose voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voiceID)


    #check response length
    print(checkFinished(message))

    # Read aloud the transcribed text
    if check_length_with_gpt(message):

        engine.say(message)
    

    # Extract the word types from the message using regex
    prevConversation = prevConversation + ". Human: " + text + ". AI: " + message
    return message


def check_length_with_gpt(text):
    global prevConversation
    global voiceID
    global totalTokens
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a concise and helpful assistant."},
            {"role": "system", "content": "This is the context to the conversation that we are having. If there is nothing after the colon that means this is the start of the conversation: "+ prevConversation},
            {"role": "user", "content": "This is your last message. If it looks complete, like it was finished by the AI, simply respond with \"yes\", but if it looks incomplete, like it was cut off, respond with \"no\"."}
        ],
    )
    message = response['choices'][0]['message']['content']

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()

    #choose voice
    if message == "yes":
        return False
    elif message == "no":
        return True


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
                time.sleep(0.025)
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
                    engine.setProperty('voice', voiceID)
                    engine.say("Context saved as " + filename)
                    engine.runAndWait()
                    continue
                elif text.lower().startswith("open context ") or text.lower().startswith("open contacts "):
                    filename = text[13:] + '.json'
                    try:
                        with open(filename, 'r') as file:
                            prevConversation = json.load(file)
                        print("Context loaded from " + filename)
                        engine.say("Context loaded from " + filename)
                        engine.runAndWait()
                    except FileNotFoundError:
                        print("No such file: " + filename)
                        engine.setProperty('voice', voiceID)
                        engine.say("No such file: " + filename)
                        engine.runAndWait()
                    continue
                elif text.lower().startswith("list context") or text.lower().startswith("list contacts"):
                    files = [f for f in os.listdir() if f.endswith('.json')]
                    for i in range(len(files)):
                        files[i] = files[i][:-5]
                    fileNames = ', '.join(files)
                    print("JSON files: " + fileNames)
                    engine.setProperty('voice', voiceID)
                    engine.say(fileNames)
                    engine.runAndWait()

                    continue

                print("AI: " + chat_with_gpt(text))


            except sr.WaitTimeoutError:
                print("Silence detected, recording stopped.")
                break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
