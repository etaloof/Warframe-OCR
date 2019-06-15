import discord
from discord.ext import commands
import asyncio
from utils import *
from db_operations import *

# Initialize ##################################################################################

prefix = "!"
bot = commands.Bot(command_prefix=prefix)
print('[Init] Bot configuré !')


###############################################################################################
# Background Tasks ############################################################################


async def task_vault_update(timeout):
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            update_vault_list()
            await asyncio.sleep(timeout)
        except Exception as e:
            print(str(e))
            await asyncio.sleep(timeout)


###############################################################################################
# Custom Convertors ################################################################################

@bot.event
async def on_command_error(ctx, message):
    if isinstance(message, commands.UserInputError):
        await ctx.send(message)


# Check if number is too high or not an absolute
class CheckNbr(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            if int(argument) > 100:
                raise commands.UserInputError('{} ? De qui te moques-tu, Tenno !?'.format(argument))
            else:
                return int(argument)
        else:
            raise commands.UserInputError('Vous ne pouvez entrer qu\'un nombre absolu !')

###############################################################################################
# Bot-commands ################################################################################


@bot.event
async def on_ready():
    print("[Init] Bot en ligne !")
    await bot.change_presence(activity=discord.Game("JE TRAVAILLE OK"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "Hello":
        await message.channel.send("Yo !")
    if message.content == "Jour ?":
        await message.channel.send("Nuit")
    if message.content == "Clem ?":
        await message.channel.send("GRAKATA")
    if message.content == "Demokdawa":
        await message.channel.send("LE DIEU !")
    if message.content == "A Kadoc ?":
        await message.channel.send("Il dit que c'est a lui de jouer...")
    await bot.process_commands(message)


#@bot.event
#async def on_command_error(ctx, error):
    #if isinstance(error, commands.MissingRequiredArgument):
        #await ctx.send("FINIS LA COMMANDE BATAR")


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print("le ping marche !")
    await ctx.send(latency)


@bot.command()
async def index(ctx):
    await ctx.send('https://docs.google.com/document/d/1zRJiGvXl1rY21ri0DuirK7BovAsBw1ikc0qCLChx7gw/edit?usp=sharing')


@bot.command()
async def todo(ctx):
    await ctx.send('https://docs.google.com/spreadsheets/d/17olsWjmOeoMx60y7jnxmEsTCpATqAbgcZ7nZBQ7FpKg/edit?usp=sharing')


@bot.command()
async def relicadd(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: CheckNbr):
    if syntax_check_pass(a1, a2, a3) is True:
        add_relic_to_db(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
        new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
        relic_state = is_vaulted(a1, a2)
        await ctx.send('Votre relique est une {} {} {}, que vous possedez dorénavant en {} exemplaire(s) **({})**'.format(a1, a2, a3, new_quantity, relic_state))
    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))


@bot.command()
async def relicdel(ctx, a1: spell_correct, a2: spell_correct, a3: spell_correct, a4: CheckNbr):
    if syntax_check_pass(a1, a2, a3) is True:
        del_state = del_relic_on_db(a1, a2, a3, a4, clean_disctag(str(ctx.message.author)))
        if del_state is True:
            new_quantity = check_relic_quantity(a1, a2, a3, clean_disctag(str(ctx.message.author)))
            await ctx.send('Vous avez supprimé {} reliques {} {} {}, que vous possedez dorénavant en {} exemplaire(s)'.format(a4, a1, a2, a3, new_quantity))
        else:
            await ctx.send(del_state)
    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))


@bot.command()
async def ressourcedrop(ctx):
    await ctx.send('J\'ai pas encore fait la commande, oups !')

bot.loop.create_task(task_vault_update(7200))
bot.run("NTg0NzYzODUyMzc0NDA5MjE5.XQUmRg.XXveAx0-lE1CKvI6F3y-Mh1uoP4")

