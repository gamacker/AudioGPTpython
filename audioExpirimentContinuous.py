import speech_recognition as sr
import pyaudio
import time
import pyttsx3
import openai
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("apikey")
openai.api_key = token
prevConversation = ""

def chat_with_gpt(text):
    global prevConversation
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. We are going to have a back and forth conversation. I will start by saying something and then you will respond. We will continue this until I say 'Goodbye'"},
            {"role": "system", "content": "This is the context to the conversation that we are having. If there is nothing after the colon that means this is the start of the conversation: "+ prevConversation},
            {"role": "user", "content": text}
        ],
    )
    message = response['choices'][0]['message']['content']

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    # Read aloud the transcribed text
    engine.say(message)
    engine.runAndWait()

    # Extract the word types from the message using regex
    prevConversation = prevConversation + ". Human: " + text + ". AI: " + message
    return message

keepGoing = True
while keepGoing:
    # Create a recognizer object
    r = sr.Recognizer()
    # Create a microphone object
    with sr.Microphone() as source:
        while True:
            print("Please speak...")
            try:
                # Record the audio until silence is detected
                audio_data = r.listen(source, timeout=2)
                print("Recording ended.")

                # Attempt to transcribe the audio
                text = r.recognize_google(audio_data)
                print("You said: " + text)

                print("AI: " + chat_with_gpt(text))

                if text.lower() == "goodbye":
                    keepGoing = False
                    break

            except sr.WaitTimeoutError:
                print("Silence detected, recording stopped.")
                break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
