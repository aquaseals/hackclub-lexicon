#import slack
import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pathlib import Path 
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter

def askAI(message):
    url = "https://ai.hackclub.com/chat/completions"
    data = {
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, json=data)
    responseMSG = response.json()["choices"][0]["message"]["content"]
    return responseMSG

def searchWorkspace(keyword, question):
    print(keyword)
    messages = []
    client = WebClient(token=os.environ['USER_TOKEN'])
    try:
        response = client.search_messages(query=f'"{keyword}"', sort='score', highlight=True, count=100)
        for match in response.get('messages', {}).get('matches', []):
            text = match.get("text", '')
            time = match.get("ts", '')
            userID = match.get("user", '')
            channelID = match['channel']['id']
            if keyword in text:
                messages.append({
                    "text": text,
                    "time" : time,
                    "userID" : userID,
                    "channelID" : channelID,
                })

        print(askAI("based on this dictionary \n" + str(messages) + " reformat it to only contain the most relevant inofmration to answering this question " + question))
        return messages

    except SlackApiError as e:
        return e.response['error']

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'],
    '/slack/events',
    app
)

client = WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']

@slack_event_adapter.on('message')
def message (payload):

    #get info about message event
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    textMessage = event.get('text')
    channel_type = event.get('channel_type')

    if user_id != BOT_ID:
        if BOT_ID in textMessage or channel_type == 'group' or channel_type == "im":
            keywords = askAI("based on the following message generate only relevant search tags/keywords. max 1 keyword and dont use keywords not within the given message. provide answer: " + textMessage)
            matches = searchWorkspace(keywords, textMessage)

            answer = askAI("using the most relevant parts of the following information answer the question {textMessage} in the context of hack club. limit answers to 100 words" + str(matches))

            #response = askAI("based on the following unformatted information, answer {textMessage} within 100 words :" + str(test))

            # Print the response
            #print(response.json())
            #response = requests.post('https://ai.hackclub.com/chat/completions', headers=headers, json=json_data)
            #print(response)
            #print(channel_id, channel_type)
            client.chat_postMessage(channel=channel_id, text=str(answer))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

"""C, it's a public channel
D, it's a DM with the user
G, it's either a private channel or multi-person DM --> not working? should text in another way?
"""