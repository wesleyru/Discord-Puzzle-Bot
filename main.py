import discord
from discord import Guild
import os
import gspread
from webapp import keep_alive

# Google API Crendential Setup
drive_key = os.environ['GDRIVE_KEY']
template_key = os.environ['GTEMPLATE_KEY']
credentials = {
    'type': os.environ['type'],
    'project_id': os.environ['project_id'],
    'private_key_id': os.environ['private_key_id'],
    'private_key': os.environ['private_key'].replace('\\n', '\n'),
    'client_email': os.environ['client_email'],
    'client_id': os.environ['client_id'],
    'auth_uri': os.environ['auth_uri'],
    'token_uri': os.environ['token_uri'],
    'auth_provider_x509_cert_url': os.environ['auth_provider_x509_cert_url'],
    'client_x509_cert_url': os.environ['client_x509_cert_url']
}

# Start Discord and Google Instances
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
gc = gspread.service_account_from_dict(credentials)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  # print(message)
  # print(f"message.content={message.content}")
  if message.author == client.user:
    return
    
  # Status Command
  if message.content.startswith('$status'):
    await message.channel.send(
        'Check status here: https://Discord-Puzzle-Bot.wesleyru.repl.co/')

  # Help Command
  if message.content.startswith('$help'):
    await message.channel.send(
        'Welcome to Puzzle Bot!\n $create <TITLE> | Creates a new spreadsheet.\n'
    )

  # Create Spreadsheet Command
  if message.content.startswith('$create'):
    name = message.content.replace('$create ', '')
    await message.channel.send(
        'Creating New Channel, Spreadsheet Link to Follow...')
    # Create New Discord Channel
    cat = client.get_channel(int(os.environ['DISCORD_CATEGORY_ID']))
    channel = await message.guild.create_text_channel(name, category=cat)
    # Duplicate Gsheet Template
    gc.copy(template_key, title=name, copy_permissions=True)
    ss = gc.open(name)
    link = 'https://docs.google.com/spreadsheets/d/' + ss.id
    await channel.send('New Spreadsheet Created Here: ' + link)
    # Update Worksheet
    ws = ss.get_worksheet(0)
    ws.update('A1', name)

keep_alive()
client.run(os.environ['DISCORD_KEY'])