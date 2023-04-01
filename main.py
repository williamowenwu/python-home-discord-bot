import discord
from discord.ext import commands
from constants import TOKEN

intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print("Booting up.....\nBot is Ready!")

@bot.command()
async def hello(context):
    await context.send("Hello!")


# client = discord.Client(intents=intents)

# @client.event
# async def on_ready():
#     print(f"something something something, logged in as : {client.user}")

bot.run(TOKEN)