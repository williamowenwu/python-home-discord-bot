from datetime import datetime
import discord
from discord import app_commands
from discord.ui import Button, View
from discord.ext import commands
import sheets
from constants import TOKEN, SHEETS_URL, WILLIAM_USER_ID, JIN_USER_ID

intents = discord.Intents.default()
intents.message_content = True

prefix = '/'
bot = commands.Bot(command_prefix=prefix, intents=intents)

manager = sheets.SheetsManager()

@bot.event
async def on_ready():
    print("Booting up.....\nBot is Ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.tree.command(name="hello", description="The first slash command that I made")
async def hello(interaction: discord.Interaction):
    manager.reset_sheets_info()
    await interaction.response.send_message(f"Hey {interaction.user.mention}, this is a slash command!" )
    

@bot.tree.command()
async def blahblahblah(interaction: discord.Interaction):
    pfp = interaction.user.display_avatar
    # Create the embed
    embed = discord.Embed(
        title="New Work Day Added",
        description="",
        color=0x2057e3 # Slightly darker blue
    )
    
    embed.set_thumbnail(url=pfp)
    embed.add_field(name="Amount Earned: ", value="Nothing")
    embed.add_field(name="Total Hours Worked: ", value="Nothing", inline=True)


    await interaction.response.send_message(embed=embed)

# slash command for just adding a new work day
@bot.tree.command(
    name="add_new_work_day",
    description="Add hours worked and amount earned",
    came_in_late="If you came in late")
@app_commands.describe(amount = "Enter In Amount of Money Made", total_hours = "Enter In Hours Worked")
async def add_new_work_day(
    interaction: discord.Interaction,
    amount: float = 0.0,
    total_hours: float = 0.0,
    extra_hours: float = 0.0
):
    # Opens one sheet
    if interaction.user.id == WILLIAM_USER_ID:
        manager = sheets.SheetsManager("William")
    # opens another sheet
    elif interaction.user.id == JIN_USER_ID:
        manager = sheets.SheetsManager("Jin")
    else:
        await interaction.response.send_message(f"You are not allowed to use this bot")
    
    manager.get_sheet_info()
    manager.add_income_with_index(total_amount=amount, hours_worked=total_hours)

    worksheet_button = Button(
        label="Go To WorkSheet",
        url=SHEETS_URL,
        style=discord.ButtonStyle.primary
    )
    
    mistake_button = Button(
        label="I Made A Mistake",
        style=discord.ButtonStyle.primary,
        custom_id="mis"
    )
    
    async def mistake_callback(interaction):
        manager.del_income_with_index()
        mistake_button.disabled = True
        
        await interaction.response.edit_message(view=view)
        await interaction.followup.send(f"{interaction.user.mention}! Sucessfully removed your last input")
        
    mistake_button.callback = mistake_callback
    
    # Create the embed
    embed = discord.Embed(
        title="New Work Day Added",
        color=0x2057e3 # Slightly darker blue
    )
    now = datetime.now().strftime("%m/%d/%Y %I:%M%p")
    
    embed.set_thumbnail(url=interaction.user.display_avatar)
    embed.add_field(name="Amount Earned: ", value=amount)
    embed.add_field(name="Total Hours Worked: ", value=total_hours, inline=True)
    embed.set_footer(text=f"Created at: {now}\nCreated by: {interaction.user.name}")
    
    view = View()
    view.add_item(worksheet_button)
    view.add_item(mistake_button)
    
    await interaction.response.send_message(embed=embed, view=view)
# slash command for deleting a specific row with a day? a row?

@bot.tree.command(rando="JSDGLKJISOG")
@app_commands.describe(rando="gkdasjgoia")
async def jin_func(interaction: discord.Interaction, rando : int):
    await interaction.response.send_message(f"{interaction.user.mention} and {rando}")


# slash command for reseting? -> new month
@bot.tree.command(name="add_new_work_month", description="Create a new work month")
async def add_new_work_month(interaction: discord.Interaction):    
    await interaction.response.send_message(f" Hey {interaction.user.mention}, I sucessfully created a new month\nUwU")
    

bot.run(TOKEN)