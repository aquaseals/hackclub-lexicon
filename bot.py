import slack
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

def searchWorkspace(keywords):
    messages = []
    client = WebClient(token=os.environ['USER_TOKEN'])
    try:
        for word in keywords:
                queryResults = client.search_messages(query=word)
                for match in queryResults:
                    for match in queryResults.get("messages", {}).get("matches", []):  # Correct path
                        messages.append([
                            match.get("text", ""),
                            match.get("channel", {}).get("name", "unknown"),
                            match.get("user", "unknown")
                        ])
        
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

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
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
            keywords = askAI("based on the following message generate only relevant search tags/keywords. max 2 keywords and dont go off track from given message. provide answer in a python list format: " + textMessage)
            test = searchWorkspace(keywords)

            #response = askAI("based on the following unformatted information, answer {textMessage} within 100 words :" + str(test))

            # Print the response
            #print(response.json())
            #response = requests.post('https://ai.hackclub.com/chat/completions', headers=headers, json=json_data)
            #print(response)
            #print(channel_id, channel_type)
            client.chat_postMessage(channel=channel_id, text=str(test))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

"""C, it's a public channel
D, it's a DM with the user
G, it's either a private channel or multi-person DM --> not working? should text in another way?
"""