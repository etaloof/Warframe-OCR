import discord
from discord.ext import commands
import sqlite3

# Command Checker #############################################################################

Era_file = 'ref_era.txt'
Lith_file = 'ref_lith.txt'
Meso_file = 'ref_meso.txt'
Neo_file = 'ref_neo.txt'
Axi_file = 'ref_axi.txt'
Quality_file = 'ref_quality.txt'


def parse_ref_files(file):
    ref_list = []
    with open(file, "r") as fileHandler:
        for line in fileHandler:
            ref_list.append(line.strip())
    return ref_list


ref_list_era = parse_ref_files(Era_file)
ref_list_lith = parse_ref_files(Lith_file)
ref_list_meso = parse_ref_files(Meso_file)
ref_list_neo = parse_ref_files(Neo_file)
ref_list_axi = parse_ref_files(Axi_file)
ref_list_quality = parse_ref_files(Quality_file)


def syntax_check_pass(arg1, arg2, arg3):
    # Check for Era
    if arg1 not in ref_list_era:
        return 'Cette ère de relique n\'existe pas ! (' + arg1 + ')'
    else:
        # Check for Name
        if arg1 == 'Lith':
            if arg2 not in ref_list_lith:
                return 'Cette relique n\'existe pas en Lith ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Meso':
            if arg2 not in ref_list_meso:
                return 'Cette relique n\'existe pas en Meso ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Neo':
            if arg2 not in ref_list_neo:
                return 'Cette relique n\'existe pas en Neo ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True
        if arg1 == 'Axi':
            if arg2 not in ref_list_axi:
                return 'Cette relique n\'existe pas en Axi ! (' + arg2 + ')'
            else:
                if arg3 not in ref_list_quality:
                    return 'Cette qualité de relique n\'existe pas ! (' + arg3 + ')'
                else:
                    return True

###############################################################################################


db = sqlite3.connect('relicdb')


def add_relic_to_db(a1, a2, a3, a4):
    cursor = db.cursor()
    cursor.execute('''INSERT INTO Relic(Era, Name, Quality, Quantity)
                      VALUES(?,?,?,?)''', (a1, a2, a3, a4))
    db.commit()


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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("FINIS LA COMMANDE BATAR")


@bot.command()
async def ping(ctx):
    latency = bot.latency
    print("le ping marche !")
    await ctx.send(latency)


@bot.command()
async def test(ctx, arg1, arg2):
    await ctx.send('Tu as mangé des {} et du {}'.format(arg1, arg2))


@bot.command()
async def index(ctx):
    await ctx.send('https://docs.google.com/document/d/1zRJiGvXl1rY21ri0DuirK7BovAsBw1ikc0qCLChx7gw/edit?usp=sharing')


@bot.command()
async def relicadd(ctx, a1: str, a2: str, a3: str, a4: int):
    if syntax_check_pass(a1, a2, a3) is True:
        await ctx.send('Votre relique est une {} {} {}, que vous possèdez en {} exemplaire(s)'.format(a1, a2, a3, a4))
        add_relic_to_db(a1, a2, a3, a4)

    else:
        await ctx.send(syntax_check_pass(a1, a2, a3))

bot.run("NTg0NzYzODUyMzc0NDA5MjE5.XPUA6g.WC1uUgEvEIx8oEZP_g2Ry-7L6PE")

