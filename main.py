import discord, io, os, random, sys, datetime, time
from discord.ext import commands

with open('token.txt', 'r') as f:
    token = f.read()

client = commands.Bot(command_prefix="-", fetch_offline_members=True, intents=discord.Intents().all())

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

@client.command()
async def pytanie(ctx, *, content):
    if not ctx.author.guild_permissions.administrator:
        return

    embed=discord.Embed(title='Szybkie pytanie!', color=0x00ff00, timestamp=ctx.message.created_at)
    embed.add_field(name=content, value='Tak - 👍\nNie - 👎', inline=False)
    embed.add_field(name='Rezultat', value='0% - Tak\n0% - Nie')
    embed.set_footer(text=ctx.message.author.name)
    message = await ctx.send(embed=embed)
    await message.add_reaction('👍')
    await message.add_reaction('👎')

@client.command()
async def ankieta(ctx, *, text):
    if not ctx.author.guild_permissions.administrator:
        return

    print(text)
    text = text.split(' - ')
    question = text[0]
    responses = text[1].split(', ')
    print(question, '--a', responses)
    
    emoji_list = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
    embed=discord.Embed(title='Ankieta', color=0x00ff00, timestamp=ctx.message.created_at)
    embed.add_field(name=question, value='Odpowiedzi:', inline=False)
    for i, responce in enumerate(responses):
        embed.add_field(name=responses[i], value=emoji_list[i], inline=False)
    embed.set_footer(text=ctx.message.author.name)
    message = await ctx.send(embed=embed)
    for i in range(len(responses)):
        await message.add_reaction(emoji_list[i])
        time.sleep(0.5)
    new_embed = embed.add_field(name='Aby wygodnie przejrzeć odpowiedzi:', value=f'-ankieta_check {message.id}')
    await message.edit(embed=new_embed)

@client.command()
async def ankieta_check(ctx, id: int):
    if not ctx.author.guild_permissions.administrator:
        return
    
    emoji_list = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣']
    message = await ctx.channel.fetch_message(id)
    formated_text = ''
    for reaction in message.reactions:
        if not reaction.emoji in emoji_list:
            continue
        for field in message.embeds[0].fields:
            if field.value != reaction.emoji:
                continue
            temp_ppl = ''
            async for user in reaction.users():
                if not user.bot:
                    temp_ppl += f'{ctx.guild.get_member(user.id).nick}, '
            formated_text += f'``{field.name}`` - {reaction.count - 1} reakcji\nOsoby które wybrały tą odpowiedż:\n{temp_ppl[:-2]}\n'
    
    await ctx.send(f'**Wyniki ankiety:**\n{formated_text}')

@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    user = client.get_guild(payload.guild_id).get_member(payload.user_id)
    message = await channel.fetch_message(payload.message_id)
    emoji = payload.emoji
    if message.author != client.user or user == client.user:
        return

    if message.embeds[0].title == 'Obecność na lekcji':
        principal_name = message.embeds[0].footer.text
        principal = discord.utils.get(message.guild.members, name=principal_name)
        topic = message.embeds[0].description

        embed = discord.Embed(title=f'Uczeń {user.nick} zgłosił obecność na lekcji', description=f'{user.nick} zgłosił obecność na lekcji {channel.name} {topic}\n w dniu {datetime.datetime.now().strftime("%d/%m/%Y, o godzinie %H:%M:%S")}', color=0xffffff)
        await principal.send(embed=embed)
    
    elif message.embeds[0].title == 'Szybkie pytanie!':
        if str(emoji) == '👍' or str(emoji) == '👎':
            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == '👍':
                    yes_votes = reaction.count - 1
                elif reaction.emoji == '👎':
                    no_votes = reaction.count - 1
            all_votes = no_votes + yes_votes 
            formated_text = f'{int((yes_votes/all_votes)*100)}% - Tak\n{int((no_votes/all_votes)*100)}% - Nie'
            old_embed = message.embeds[0]
            old_embed.remove_field(1)
            new_embed = old_embed.add_field(name='Rezultat', value=formated_text)
            await message.edit(embed=new_embed)

@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    user = client.get_guild(payload.guild_id).get_member(payload.user_id)
    message = await channel.fetch_message(payload.message_id)
    emoji = payload.emoji
    if message.author != client.user or user == client.user:
        return

    if message.embeds[0].title == 'Szybkie pytanie!':
        if str(emoji) == '👍' or str(emoji) == '👎':
            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == '👍':
                    yes_votes = reaction.count - 1
                elif reaction.emoji == '👎':
                    no_votes = reaction.count - 1
            all_votes = no_votes + yes_votes 
            formated_text = f'{int((yes_votes/all_votes)*100)}% - Tak\n{int((no_votes/all_votes)*100)}% - Nie'
            old_embed = message.embeds[0]
            old_embed.remove_field(1)
            new_embed = old_embed.add_field(name='Rezultat', value=formated_text)
            await message.edit(embed=new_embed)

client.run(token)
