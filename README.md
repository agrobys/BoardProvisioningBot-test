# Webex Board Provisioning Bot

>This code is NOT written for production. Please use for testing purposes only.

How to interact with the bot:

- Add it to a space or direct message it.
- Mention it and it will send you a card.
- Fill out the card with a workspace name, submit, and get your code!
- If you need to add another authorized user, mention the bot and specify "add [email]". Make sure to provide a valid email within your organization. 

How to start the bot:

- Install ngrok and necessary packages.
- Fill out your values in the variables.yaml file. You can find your personal temporary access token on developer.webex.com under Documentation -> Access The API and your organization ID on the Webex Control Hub under Account. You will have to encode the ID from the Control Hub to get the ID usable with the API.
- If you use my bot, please let me know before you run it. Otherwise, you can create your own bot and paste its token, id, email, and name in the variables.yaml file.
- Run main.py

>If you have any questions, contact me at agrobys@cisco.com. 