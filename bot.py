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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)