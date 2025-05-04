import slack
import os
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

client.chat_postMessage(channel='#lexicon-testing', text="hello world!")

@slack_event_adapter.on('message')
def message (payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

