import discord, io, os, random, sys, datetime
from discord.ext import commands

with open('token.txt', 'r') as f:
    token = f.read()

client = commands.Bot(command_prefix="-")

@client.event                                                           #on ready 
async def on_ready():
    print(f"Zalogowano jako {client.user.name}")
    bot_activity = discord.Game(name='Made by Tomasz Hańderek')
    await client.change_presence(activity=bot_activity)

@client.event                                                           #message edit
async def on_message_edit(bf, af):
    await client.process_commands(af)

@client.event                                                           #on message
async def on_message(msg):
    await client.process_commands(msg)

@client.command()                                                       #obecnosc
async def obecnosc(ctx, *, topic):
    if not ctx.author.guild_permissions.administrator:
        return
    
    embed=discord.Embed(title='Obecność na lekcji', description=topic, color=0x00ff00, timestamp=ctx.message.created_at)
    embed.add_field(name='Obecność', value='Zareaguj w reakcję pod wiadomością aby potwierdzić swoją obecność na lekcji')
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/ZwdwSQoEbNeIqWZCGaCGvWThw8M84rFMIIDlgYQ39GY/http/34.89.156.194/static/img/check.png")
    embed.set_footer(text=ctx.message.author.name)
    message = await ctx.send('@here', embed=embed)
    await message.add_reaction('👍')

@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    user = client.get_guild(payload.guild_id).get_member(payload.user_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author != client.user or user == client.user:
        return
    principal_name = message.embeds[0].footer.text
    principal = discord.utils.get(message.guild.members, name=principal_name)
    topic = message.embeds[0].description

    embed = discord.Embed(title=f'Uczeń {user.nick} zgłosił obecność na lekcji', description=f'{user.nick} zgłosił obecność na lekcji {channel.name} {topic}\n w dniu {datetime.datetime.now().strftime("%d/%m/%Y, o godzinie %H:%M:%S")}', color=0xffffff)
    await principal.send(embed=embed)

client.run(token)