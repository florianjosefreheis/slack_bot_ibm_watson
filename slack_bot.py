import os
import json

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
from flask import request
from watson_developer_cloud import ConversationV1

CLIENTS = {}

# Slack's Event Adapter for receiving actions via the Events API
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
slack_events_adapter = SlackEventAdapter(SLACK_VERIFICATION_TOKEN, "/slack/events")

# Slack App credentials for OAuth
SLACK_CLIENT_ID = os.environ["SLACK_CLIENT_ID"]
SLACK_CLIENT_SECRET = os.environ["SLACK_CLIENT_SECRET"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

# Create a SlackClient for bot to use for Web API requests
CLIENT = SlackClient(SLACK_BOT_TOKEN)

# IBM Watson credentials
CONVERSATION_USERNAME = os.environ["CONVERSATION_USERNAME"]
CONVERSATION_PASSWORD = os.environ["CONVERSATION_PASSWORD"]
CONVERSATION_WORKSPACE = os.environ["CONVERSATION_WORKSPACE"]

conversation = ConversationV1(
    username=CONVERSATION_USERNAME,
    password=CONVERSATION_PASSWORD,
    version='2016-09-20')

# Bot responder
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if message.get("subtype") is None:
        channel = message["channel"]

        response = conversation.message(workspace_id=CONVERSATION_WORKSPACE, message_input={
            'text': message.get('text') })

        for answer in response["output"]["text"]:
            CLIENT.api_call("chat.postMessage", channel=channel, text=answer)

# Example reaction emoji echo
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
    event = event_data["event"]
    emoji = event["reaction"]
    channel = event["item"]["channel"]
    text = ":%s:" % emoji
    CLIENT.api_call("chat.postMessage", channel=channel, text=text)

# Flask server with the default `/events` endpoint on port 3000
slack_events_adapter.start(port=3000)
