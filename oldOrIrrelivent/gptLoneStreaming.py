import openai
import os
import time
import json

prevConversation = ""

openai.api_key = "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"

def chat_with_gpt(text):
    global prevConversation
    delay_time = 0.01
    start_time = time.time()

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a concise and helpful assistant. I will start by saying something and then you will respond. We will continue this until I say 'Goodbye'"},
            {"role": "system", "content": "This is the context to the conversation that we are having. The text after \"Human:\" is what I have said, until \"AI:\", and the stuff after that is what you said. If there is nothing after the colon that means this is the start of the conversation. Here is the context: "+ prevConversation},
            {"role": "user", "content": text}
        ],
        temperature=0,
        stream=True,
    )

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

repeat = True
while repeat:
    question = input("\nWhat do you want to ask ChatGpt? ")
    if question.lower() == "goodbye":
        repeat = False
    elif question.lower().startswith("save context "):
        filename = question[13:] + '.json'
        with open(filename, 'w') as file:
            json.dump(prevConversation, file)
        print("Context saved as " + filename)
    elif question.lower().startswith("open context "):
        filename = question[13:] + '.json'
        try:
            with open(filename, 'r') as file:
                prevConversation = json.load(file)
            print("Context loaded from " + filename)
        except FileNotFoundError:
            print("No such file: " + filename)
    elif question.lower().startswith("list context"):
        files = [f for f in os.listdir() if f.endswith('.json')]
        for i in range(len(files)):
            files[i] = files[i][:-5]
        fileNames = ', '.join(files)
        print("JSON files: " + fileNames)
    elif question.lower().startswith("clear context"):
        prevConversation = ""
        print("Context cleared.")
    else:
        chat_with_gpt(question)
