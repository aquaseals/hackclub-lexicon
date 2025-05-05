import slack
import os
import requests
from pathlib import Path 
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter

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

            headers = {
                'Content-Type': 'application/json',
            }

            json_data = {
                'messages': [
                    {
                        'role': 'user',
                        'content': '{textMessage}',
                    },
                ],
            }

            #response = requests.post('https://ai.hackclub.com/chat/completions', headers=headers, json=json_data)
            #print(response)
            print(channel_id, channel_type)
            client.chat_postMessage(channel=channel_id, text=textMessage)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

"""C, it's a public channel
D, it's a DM with the user
G, it's either a private channel or multi-person DM --> not working? should text in another way?
"""