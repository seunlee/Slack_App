
import os
import logging
import meraki
from dotenv import load_dotenv
from flask import Flask, request, make_response, jsonify
import json
import requests
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from slack_sdk.signature import SignatureVerifier
from blocks import start_message, camera_modal

# Load all environment variables
load_dotenv()
MERAKI_API_KEY = os.getenv("MERAKI_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
mv_serial = os.getenv("mv_serial")

# global variables
headers = dict()
headers['X-Cisco-Meraki-API-Key'] = MERAKI_API_KEY
headers['Content-Type'] = "application/json"
headers['Accept'] = "application/json"
base_url = "https://api.meraki.com/api/v1"
signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)
request_channel_id = None


# Helper function
# Generic API call function
def meraki_api(method, uri, payload=None):
    response = requests.request(method, base_url+uri, headers=headers, data=json.dumps(payload))
    return response

# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=SLACK_BOT_TOKEN)

# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
@slack_events_adapter.on("message")
def message(payload):
    global request_channel_id

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "meraki":
        request_channel_id = channel_id
        return slack_web_client.chat_postMessage(channel=channel_id, blocks=start_message)

    elif text and text.lower() == "analytics live":
        request_channel_id = channel_id
        dashboard = meraki.DashboardAPI(MERAKI_API_KEY)
        response = dashboard.camera.getDeviceCameraAnalyticsLive(mv_serial)
        return slack_web_client.chat_postMessage(channel=channel_id, text='Camera Analytics (live) :'+json.dumps(response))

    elif text and text.lower() == "analytics overview":
        request_channel_id = channel_id
        dashboard = meraki.DashboardAPI(MERAKI_API_KEY)
        response = dashboard.camera.getDeviceCameraAnalyticsOverview(mv_serial)
        return slack_web_client.chat_postMessage(channel=channel_id, text='Camera Analytics (Overview) :'+json.dumps(response))


# ============== Interactive Events ============= #
@app.route("/slack/interactive", methods=["POST"])
def interactive():
    global org_id, request_channel_id

    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)

    if "payload" in request.form:
        payload = json.loads(request.form["payload"])

        # Start button clicked
        if payload["type"] == "block_actions":
            if payload["actions"][0]["action_id"] == "start-button":
                try:
                    open_modal_form = slack_web_client.views_open(
                        trigger_id = payload["trigger_id"],
                        view = camera_modal
                    )
                    return make_response("", 200)
                except SlackAPIError as e:
                    code = e.response["error"]
                    return make_response(f"Failed to open a modal due to {code}", 200)

        # Request form submit
        if payload["type"] == "view_submission" and payload["view"]["callback_id"] == "camera_modal":
            camera_serial = payload["view"]["state"]["values"]["camera_serial"]["camera_serial"]["value"]
            dashboard = meraki.DashboardAPI(MERAKI_API_KEY)
            response = dashboard.camera.generateDeviceCameraSnapshot(camera_serial)
            slack_web_client.chat_postMessage(channel=request_channel_id, text=json.dumps(response))
            return {}

    return make_response("", 404)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
