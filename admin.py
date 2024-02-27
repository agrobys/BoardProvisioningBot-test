from __future__ import print_function  # Needed if you want to have console output using Flask
import requests
import json
from webexteamssdk import WebexTeamsAPI, ApiError


# The entity making calls on the organization
class Admin:

    def __init__(self, my_token: str, org_id: str):
        self.my_token = my_token
        self.org_id = org_id
        self.api = WebexTeamsAPI(access_token=self.my_token)
        self.headers = self.get_headers()
        try:
            self.my_id = self.api.people.me().id
        except ApiError:
            self.my_id = ""

    def update_token(self, token):
        self.my_token = token
        self.my_id = self.api.people.me().id

    # Converts email to User ID. Needed for allowed users list. Returns empty string if email not found.
    def get_id_from_email(self, email) -> str:
        try:
            users = self.api.people.list(email=email)
            user_id = ""
            for user in users:
                user_id = user.id
            return user_id
        except ApiError:
            return ""

    def get_email_from_id(self, id) -> str:
        try:
            users = self.api.people.list(id=id)
            email = ""
            for user in users:
                email = user.emails[0]
            return email
        except ApiError:
            return ""

    def get_headers(self) -> dict:
        headers = {
            "Authorization": "Bearer " + self.my_token,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        return headers

    # Need to use requests library here since Webex SDK doesn't yet support workspaces & devices
    # Is called by get_activation_code. Checks if workspace name exists, creates workspace if not and returns ID
    def get_workspace_id(self, workspace_name) -> str:
        workspace_id = ""
        # Get ID for specified workspace name
        try:
            response = requests.get(
                url=f'https://webexapis.com/v1/workspaces?orgId={self.org_id}&displayName={workspace_name}',
                headers=self.headers)
        except ApiError:
            return ""
        # print(response.json())
        for workspace in response.json()["items"]:
            workspace_id = workspace["id"]
        # Create workspace if it doesn't exist
        if workspace_id == "":
            print(f"Creating workspace {workspace_name}.")
            payload = {
                "displayName": workspace_name,
                "orgId": self.org_id
            }
            try:
                response = requests.post(url="https://webexapis.com/v1/workspaces",
                                     data=json.dumps(payload), headers=self.headers)
            except ApiError:
                return ""
            # print(response.content)
            workspace_id = json.loads(response.content)["id"]
        return workspace_id

    # Need to use requests library here since Webex SDK doesn't yet support workspaces & devices
    # Gets activation code for a workspace
    def get_activation_code(self, workspace_name, model=None) -> str:
        # Get ID for specified workspace name
        workspace_id = self.get_workspace_id(workspace_name)
        if workspace_id == "":
            return ""
        payload = {
            "workspaceId": workspace_id
        }
        if model:
            payload["model"] = model
        # Create activation code
        try:
            response = requests.post(url="https://webexapis.com/v1/devices/activationCode?orgId=" + self.org_id,
                                 data=json.dumps(payload), headers=self.headers)
        except ApiError:
            return ""
        print(json.loads(response.content))
        activation_code = json.loads(response.content)["code"]
        return activation_code

    def save(self):
        data = {
            "my_token": self.my_token,
            "org_id": self.org_id,
        }
        return data

