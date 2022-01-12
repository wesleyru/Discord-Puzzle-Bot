from config import api_key, drive_id, template_key
import discord
import os
from discord.ext.commands import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

client = discord.Client()

gc = gspread.service_account(filename=api_key)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$create'):
        name = message.content.replace('$create ', '')
        gc.copy(template_key, title=name, copy_permissions=True)
        ss = gc.open(name)
        link = "https://docs.google.com/spreadsheets/d/" + ss.id
        await message.channel.send('New Spreadsheet Created Here: ' + link)

client.run(os.getenv('TOKEN'))



