from __future__ import print_function  # Needed if you want to have console output using Flask
import yaml, json
from flask import Flask, request
from bot import Bot

with open('variables2.yaml', 'r') as file:
    variables = yaml.safe_load(file)


app = Flask(__name__)


# Bot mentioned -> Send adaptive card and handle special commands
@app.route("/mention", methods=['POST'])
def mention():
    payload = request.get_json()
    person_id = payload["data"]["personId"]

    # Ignore own bot messages
    if person_id == bot.id:
        return 'success'

    message_id = payload["data"]["id"]
    room_id = payload["data"]["roomId"]

    # Load message
    message = bot.api.messages.get(message_id)

    # Handle the message
    bot.handle_command(message.text, room_id, person_id)

    return 'success'


# Adaptive Card submitted -> Get and return activation code
@app.route("/card", methods=['POST'])
def card():
    payload = request.get_json()
    person_id = payload["data"]["personId"]

    room_id = payload["data"]["roomId"]
    attachment_id = payload["data"]["id"]

    # Handle the message
    bot.handle_card(attachment_id, room_id, person_id)

    return 'success'


@app.route("/added", methods=['POST'])
def added():
    payload = request.get_json()
    person_id = payload["data"]["personId"]

    room_id = payload["data"]["roomId"]

    # Handle the message
    bot.handle_added(room_id)

    return 'success'


@app.route("/removed", methods=['POST'])
def removed():
    payload = request.get_json()
    person_id = payload["data"]["personId"]

    room_id = payload["data"]["roomId"]

    # Handle the message
    bot.handle_removed(room_id)

    return 'success'


if __name__ == "__main__":

    try:
        with open("bot_data.json") as file:
            data = json.load(file)
    except:
        data = {
            "bot_name": variables["bot_name"],
            "bot_token": variables["bot_token"],
            "bot_email": variables["bot_email"],
            "orgs": [],
            "org_admin": {},
            "org_allowed_users": {},
            "room_to_org": {},
            "org_id_to_email": {}
        }

    bot = Bot(data)
    print("Starting bot")
    bot.startup()
    try:
        app.run(port=5042)
    finally:
        bot.teardown()