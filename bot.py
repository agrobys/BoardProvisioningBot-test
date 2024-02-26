from __future__ import print_function  # Needed if you want to have console output using Flask
from pyngrok import ngrok
from webexteamssdk import WebexTeamsAPI
from webexteamssdk.models.cards import AdaptiveCard, TextBlock, Text
from webexteamssdk.models.cards.actions import Submit
from admin import Admin


# Creates the adaptive card that will be sent to users to fill in information.
# Activation code will be generated based on the user input in this card
def make_card() -> AdaptiveCard:
    greeting = TextBlock("Get an activation code:")
    workspace = Text('workspace', placeholder="Enter Workspace Name")
    # model = Text('model', placeholder="Enter Device Model (Optional)")
    submit = Submit(title="Provision")

    card = AdaptiveCard(
        body=[greeting, workspace], actions=[submit]
    )
    return card


# Adds readability to the activation code
def split_code(code) -> str:
    return code[:4] + '-' + code[4:8] + '-' + code[8:12] + '-' + code[12:]


# The entity communicating with the user
class Bot:

    def __init__(self, bot_name: str, bot_token: str, bot_email: str, allowed_users: list, admin_token: str, org_id: str):
        self.name = bot_name
        self.bot_token = bot_token
        self.api = WebexTeamsAPI(access_token=self.bot_token)
        self.id = self.api.people.me().id
        self.email = bot_email
        self.card = make_card()

        self.https_tunnel = None
        self.webhooks = []

        self.admin = Admin(admin_token, org_id)
        self.allowed_users = []
        self.id_to_email = {}
        for user in allowed_users:
            user_id = self.admin.get_id_from_email(user)
            if user_id != "":
                self.allowed_users.append(user_id)
                self.id_to_email[user_id] = user

    # Creates 2 webhooks: Bot mentioned and adaptive card submitted
    def create_webhooks(self) -> None:
        print("Creating webhooks")
        self.webhooks.append(
            self.api.webhooks.create(
                name="MentionWebhook",
                targetUrl=self.https_tunnel.public_url + "/mention",
                resource="messages",
                event="created",
                # filter="roomType=direct"
            )
        )
        self.webhooks.append(
            self.api.webhooks.create(
                name="CardWebhook",
                targetUrl=self.https_tunnel.public_url + "/card",
                resource="attachmentActions",
                event="created",
                # filter="roomType=direct"
            )
        )

    def delete_webhooks(self) -> None:
        for webhook in self.webhooks:
            self.api.webhooks.delete(webhook.id)

    def start_tunnel(self) -> None:
        self.https_tunnel = ngrok.connect(bind_tls=True, addr="http://localhost:5042")

    def stop_tunnel(self) -> None:
        ngrok.disconnect(self.https_tunnel.api_url)

    def startup(self) -> None:
        self.delete_webhooks()
        self.start_tunnel()
        self.create_webhooks()

    def teardown(self) -> None:
        self.delete_webhooks()
        self.stop_tunnel()

    def add_allowed_user(self, email):
        user_id = self.admin.get_id_from_email(email)
        if user_id != "":
            self.allowed_users.append(user_id)
        return user_id

    # Is called when card was submitted. Asks Admin to create activation code and sends it in the chat
    def get_activation_code(self, attachment_id, room_id, actor_id):
        if actor_id in self.allowed_users:
            print(f"User {self.id_to_email[actor_id]} allowed.")
            card_input = self.api.attachment_actions.get(id=attachment_id)
            workspace_name = card_input.inputs["workspace"]
            # model = card_input.inputs["model"]
            # if model != "":
            #     activation_code = get_activation_code(workspace_name, model=model)
            activation_code = self.admin.get_activation_code(workspace_name)
            activation_code = split_code(activation_code)
            print(f"Sending activation code.")
            self.api.messages.create(room_id, text=f"Here's your activation code: {activation_code}")
        else:
            print(f"User {self.id_to_email[actor_id]} unauthorized.")
            self.api.messages.create(room_id, text="You're unauthorized. Please contact agrobys@cisco.com if you require access.")

    # Is called when bot is mentioned. Checks for commands (if no special command is detected, it will send the
    # adaptive card)
    def handle_command(self, message, room_id, actor_id) -> None:
        # Strips bot mention from command
        if message.split[0] == self.name:
            command = message.split()[1:]
        else:
            command = message
        print(f"Command: {' '.join(command)}")

        # Adds an allowed user on "add" command
        if len(command) > 1 and command[0] == "add" and actor_id in self.allowed_users:
            print(f"User {self.id_to_email[actor_id]} allowed.")
            user_id = self.add_allowed_user(command[1])
            # Empty user_id means provided email was not found
            if user_id == "":
                self.api.messages.create(room_id, text="Please provide a valid email as a second argument. Thank you")
            else:
                self.api.messages.create(room_id, text=f"User {command[1]} added successfully.")

        # Sends card if no special command is detected
        else:
            print(f"Sending card (No special command detected or user unauthorized).")
            self.api.messages.create(room_id, text="Here's your card", attachments=[self.card])
