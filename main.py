import discord
import os
import gspread
from webapp import keep_alive

drive_key = os.environ['GDRIVE_KEY']
template_key = os.environ['GTEMPLATE_KEY']
credentials = {
  'type': os.environ['type'],
  'project_id': os.environ['project_id'],
  'private_key_id': os.environ['private_key_id'],
  'private_key': os.environ['private_key'].replace('\\n','\n'),
  'client_email': os.environ['client_email'],
  'client_id': os.environ['client_id'],
  'auth_uri': os.environ['auth_uri'],
  'token_uri': os.environ['token_uri'],
  'auth_provider_x509_cert_url': os.environ['auth_provider_x509_cert_url'],
  'client_x509_cert_url': os.environ['client_x509_cert_url']
}

client = discord.Client()
gc = gspread.service_account_from_dict(credentials)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send('Welcome to Puzzle Bot!\nType $create <TITLE> to create a new spreadsheet.')

    if message.content.startswith('$create'):
        await message.channel.send('Creating New Spreadsheet...')
        name = message.content.replace('$create ', '')
        gc.copy(template_key, title=name, copy_permissions=True)
        ss = gc.open(name)
        link = 'https://docs.google.com/spreadsheets/d/' + ss.id
        await message.channel.send('New Spreadsheet Created Here: ' + link)

keep_alive()
client.run(os.getenv('DISCORD_KEY'))



