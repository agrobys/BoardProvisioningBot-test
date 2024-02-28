# Webex Board Provisioning Bot

>This code is NOT written for production. Please use for testing purposes only.

How to start the bot:

- Install ngrok and necessary packages.
- If you use my bot with my variables specified in the variables.yaml file, please let me know before you run it. Otherwise, you can create your own bot at https://developer.webex.com/my-apps/new/bot and paste its token, id, email, and name in the .yaml file.
- Run app.py

How to interact with the bot:

- Add it to a space or direct message it.
- Fill out the initialization card with your organization ID and personal Webex API access token (you have to be admin for that organization). You can find your personal temporary access token on developer.webex.com under Documentation -> Access The API and your organization ID on the Webex Control Hub under Account. To get the organization ID usable with the API, send a GET to https://webexapis.com/v1/organizations/{orgId}. You can do this easily at https://developer.webex.com/docs/api/v1/organizations/get-organization-details. The ID you need will be in the response payload.
- After initialization, mention the bot and it will send you a card.
Fill out the card with a workspace name, submit, and get your code!
- Bot data will be saved to bot_data.json upon teardown. If no such file is found on startup, it will initialize using the variables.yaml file.

Other commands:

- help: Print all available commands
- add [email]: Add an authorized user to your organization. Provided email must be in your organization. You can provide several at once separated by a space.
- token [token]: Update your access token. If you're using a temporary token, it is only valid for 48hrs.
- reinit: Reinitialize the bot. Do this if you wish to use it for a different organization in this room.

>If you have any questions, contact me at agrobys@cisco.com. 