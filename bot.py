import discord
from discord.ext import commands
import sqlite3

db = sqlite3.connect('relicdb')

prefix = "!"
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print("The bot is ready!")
    await bot.change_presence(activity=discord.Game("Making a bot"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "Hello":
        await message.channel.send("World")
    if message.content == "Tamer":
        await message.channel.send("La tchoin")
    if message.content == "Clem ?":
        await message.channel.send("GRAKATA")
    await bot.process_commands(message)


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print("le ping marche !")
    await ctx.send(latency)


@bot.command()
async def test(ctx, arg1, arg2):
    await ctx.send('Tu as mangé des {} et du {}'.format(arg1, arg2))

bot.run("NTg0NzYzODUyMzc0NDA5MjE5.XPUA6g.WC1uUgEvEIx8oEZP_g2Ry-7L6PE")

