import discord
import sqlite3

db = sqlite3.connect('relicdb')


def sql_fetch(con):
    cursorObj = db.cursor()
    cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    print(cursorObj.fetchall())


sql_fetch(db)

client = discord.Client()

@client.event
async def on_ready():
    print("The bot is ready!")
    await client.change_presence(activity=discord.Game("Making a bot"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "Hello":
        await message.channel.send("World")
    if message.content == "Tamer":
        await message.channel.send("La tchoin")
    if message.content == "Clem ?":
        await message.channel.send("GRAKATA")

client.run("NTg0NzYzODUyMzc0NDA5MjE5.XPPqJw.pU1ACVATwLloE_lxTkz7zO-pzG8")

