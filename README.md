# Discord Bot
---
This is a Discord bot designed to track the hourly amount and hours of a hourly job all within my discord server.

# Features
## Income Tracking
The bot helps users track their income and hours worked. It provides commands to add income with the corresponding hours worked and calculates weekly averages and totals. This will only work for two individuals (myself and jin)

## Automatic Date Tracking
It will automatically keep track of the dates without you needing to type in the today's date

## Creation of different sheets
Depending on who is the user, it will create different spreadsheets and worksheets based on the month.

## Requirements
Python 3.7 or higher
Discord.py library
Google Sheets API

### Installation
Clone the repository:
```
git clone https://github.com/williamowenwu/python-home-discord-bot.git
```

### Install the required dependencies:
```
pip install -r requirements.txt
```

Set up the Google Sheets API:

## Your own discord attendance bot
Go to the Google Developers Console and create a new project.
Enable the Google Sheets API for your project.
Create service account credentials and download the JSON file.
Rename the JSON file to credentials.json and place it in the project directory.
Configure the Discord bot token:

Create a new Discord bot and obtain the bot token.

Create a file named .env in the project directory.

Add the following line to the .env file:

```
DISCORD_TOKEN=your-bot-token
```

## Start the bot
```
python main.py
```

Once the bot is running and connected to your Discord server, you can use the following commands:

- /add_new_work_day <total_amount> (optional) <hours_worked> (optional): Add income with the corresponding hours worked.

- /hello: Give you a inital string and clear the *worksheet*.

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.