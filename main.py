import os
import discord
import gspread
from datetime import datetime
from pytz import timezone
from webapp import keep_alive

# Google API Crendential Setup
drive_key = os.environ['GDRIVE_KEY']
template_key = os.environ['GTEMPLATE_KEY']
dashboard_key = os.environ['GDASHBOARD_KEY']
solved_folder_key = os.environ['GSOLVED_KEY']

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
        'Welcome to Puzzle Bot!\n' +
        '$create <TITLE> | Creates a new spreadsheet.\n' +
        '$solved <ANSWER> | Use in puzzle channel to update Master Dashboard.\n'
    )

  # Create Spreadsheet Command
  if message.content.startswith('$create'):
    name = message.content.replace('$create ', '')
    await message.channel.send(
        'Creating New Channel, Spreadsheet Link to Follow...')
    # Create New Discord Channel
    cat = client.get_channel(int(os.environ['DISCORD_CATEGORY_ID']))
    channel = await message.guild.create_text_channel(name.upper(),
                                                      category=cat)
    # Duplicate Gsheet Template
    gc.copy(template_key, title=name, copy_permissions=True)
    ss = gc.open(name)
    link = 'https://docs.google.com/spreadsheets/d/' + ss.id
    await channel.send('New Spreadsheet Created Here: ' + link)
    # Update Worksheet
    ws = ss.get_worksheet(0)
    ws.update(range_name='A1', values=name)
    ws.client.session.close()

    # Update Dashboard
    ss = gc.open_by_key(dashboard_key)
    ws = ss.worksheet('Puzzle Dashboard')
    next_empty_line = 12
    while ws.acell('A' + str(next_empty_line)).value is not None or ws.acell(
        'A' + str(next_empty_line + 1)).value is not None:
      next_empty_line += 1
    ws.update_acell('A' + str(next_empty_line), cat.name)
    ws.format('A' + str(next_empty_line),
              {'textFormat': {
                  'bold': False,
                  'fontSize': 10
              }})
    ws.update_acell('B' + str(next_empty_line), name.upper())
    ws.update_acell('C' + str(next_empty_line),
                    '=hyperlink("' + link + '","Link")')
    ws.update_acell('D' + str(next_empty_line), 'Not Started')
    ws.client.session.close()
    await channel.send('Puzzle Dashboard Updated!')

  # Solved Command
  if message.content.startswith('$solved'):
    channel = message.channel
    answer = message.content.replace('$solved ', '')

    # Update Puzzle Dashboard
    ss = gc.open_by_key(dashboard_key)
    ws = ss.worksheet('Puzzle Dashboard')
    channel_line = 12
    while (ws.acell('B' + str(channel_line)).value is not None
           or ws.acell('B' + str(channel_line + 1)).value
           is not None) and ws.acell(
               'B' + str(channel_line)).value != channel.name.upper().replace(
                   "-", " "):
      channel_line += 1
    if ws.acell('B' + str(channel_line)).value is None:
      ws.client.session.close()
      await channel.send(
          'Puzzle Dashboard Not Updated. Puzzle Name Could not be Found.')
    elif ws.acell('B' +
                  str(channel_line)).value == channel.name.upper().replace(
                      "-", " "):
      ws.update_acell('D' + str(channel_line), 'Solved')
      ws.update_acell('I' + str(channel_line), answer.upper())
      ws.update_acell(
          'J' + str(channel_line),
          str(datetime.now(timezone('EST')).strftime('%a %I:%M%p')).upper())
      ws.client.session.close()
      await channel.send('Puzzle Dashboard Updated!')
    else:
      await channel.send(
          'Puzzle Dashboard Not Updated. Puzzle Name Could not be Found.')
    solved_cat = client.get_channel(
        int(os.environ['DISCORD_SOLVED_CATEGORY_ID']))
    await channel.edit(category=solved_cat)


keep_alive()
client.run(os.environ['DISCORD_KEY'])
