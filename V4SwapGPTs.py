import speech_recognition as sr
import pyaudio
import time
import pyttsx3
import openai
import os
from dotenv import load_dotenv
import keyboard
import json
import subprocess
import os
import subprocess
import win32com.client

load_dotenv()
token = os.environ.get("apikey")
openai.api_key = token
prevConversation = ""
engine = pyttsx3.init()


version = "gpt-3.5-turbo"

def chat_with_gpt(text):
    global prevConversation
    global version
    delay_time = 0.01
    start_time = time.time()
    
    response = openai.ChatCompletion.create(
        model=version,
        messages=[
            {"role": "system", "content": "You are a concise and helpful assistant. I will start by saying something and then you will respond. We will continue this until I say 'Goodbye'"},
            {"role": "system", "content": "This is the context to the conversation that we are having. The text after \"Human:\" is what I have said, until \"AI:\", and the stuff after that is what you said. If there is nothing after the colon that means this is the start of the conversation. Here is the context: "+ prevConversation},
            {"role": "user", "content": text}
        ],
        temperature=0,
        stream=True,
    )
    print("AI:")
    # STREAM THE ANSWER
    full_answer = ""
    for event in response:
        event_time = time.time() - start_time
        event_text = event['choices'][0]['delta']
        chunk = event_text.get('content', '')
        full_answer += chunk
        print(chunk, end='', flush=True)
        time.sleep(delay_time)

    prevConversation += ". Human: " + text + ". AI: " + full_answer
    # Initialize the text-to-speech engine

    engine = pyttsx3.init()

    #choose voice
    voices = engine.getProperty('voices')
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')

    # Read aloud the transcribed text
    

    engine.say(full_answer)
    engine.runAndWait()
    return full_answer


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
                    print("Context saved as " + filename)
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
                        engine.say("No such file: " + filename)
                        engine.runAndWait()
                    continue
                elif text.lower().startswith("list context") or text.lower().startswith("list contacts"):
                    files = [f for f in os.listdir() if f.endswith('.json')]
                    for i in range(len(files)):
                        files[i] = files[i][:-5]
                    fileNames = ', '.join(files)
                    print("JSON files: " + fileNames)
                    engine.say(fileNames)
                    engine.runAndWait()
                    continue

                elif text.lower().startswith("clear context") or text.lower().startswith("clear contacts"):
                    
                    prevConversation = ""
                    engine.say("Clearing Context")
                    engine.runAndWait()

                    continue
                    # assuming 'text' is already defined
                elif text.lower().startswith("admin open "):
                    filename = text[11:] + '.txt'  # extract filename from the text
                    try:
                        with open(filename, 'r') as file:
                            command = file.read().strip()  # read file content into variable command
        
                        # check the extension of the command
                        _, extension = os.path.splitext(command)

                        # for .url files
                        if extension == '.url':
                            command_to_run = f'start {command}'

                        # for .lnk files
                        elif extension == '.lnk':
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortCut(command)
                            target_path = shortcut.Targetpath  # get the path that the shortcut points to

                            command_to_run = f'"{target_path}"'  # ensure the target path is surrounded by quotes in case it contains spaces

                        else:
                            command_to_run = command

                        process = subprocess.Popen(command_to_run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        output, error = process.communicate()

                        if output:
                            print("Output: \n{}\n".format(output.decode("utf-8")))

                        if error:
                            print("Error: \n{}\n".format(error.decode("utf-8")))

                    except FileNotFoundError:
                        print("No such file: " + filename)

                elif text.lower().startswith("chat basic"):
                    version = "gpt-3.5-turbo"
                    print("Basic chat mode activated")
                elif text.lower().startswith("chat detailed"):
                    version = "gpt-4"
                    print("Detailed chat mode activated")
                elif text.lower().startswith("chat oh so fancy"):
                    #dont use, no access to gpt-4-32k. yet.
                    version = "gpt-4-32k"
                    print("Oh so fancy chat mode activated")
                else:
                    chat_with_gpt(text)



            except sr.WaitTimeoutError:
                print("Silence detected, recording stopped.")
                break
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
