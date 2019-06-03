import discord

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

client.run("NTg0NzYzODUyMzc0NDA5MjE5.XPPqJw.pU1ACVATwLloE_lxTkz7zO-pzG8")

