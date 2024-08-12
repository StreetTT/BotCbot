from main import Game
from os import getenv
from dotenv import load_dotenv as LoadEnvVariables
import discord
from discord.ext import commands
import re

LoadEnvVariables()
TOKEN = getenv("DiscordBotToken")

def boolify(a: str):
    a = a.lower()
    if a in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif a in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False

def chunkify(text, max_chunk_size=2000):
    chunks = []
    while len(text) > max_chunk_size:
        # Find the closest newline before the 2000 character limit
        split_index = text.rfind('\n', 0, max_chunk_size)
        if split_index == -1:
            # If there's no newline, split at the 2000 character limit
            split_index = max_chunk_size
        chunks.append(text[:split_index])
        text = text[split_index:].lstrip('\n')  # Remove the newline from the next chunk if it exists
    chunks.append(text)  # Add the remaining text as the last chunk
    return chunks

def anCheck(text):
    # Define a regular expression pattern to match "a" followed by a space and a word
    pattern = r'\ba\b\s+(?=[aeiouAEIOU])'
    
    # Use re.sub to replace "a " with "an " when the next word starts with a vowel
    corrected_text = re.sub(pattern, 'an ', text)
    
    return corrected_text

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)
games: dict[int,Game] = {}

async def logCommands(ctx: commands.Context) -> None:
    username: str = f"{str(ctx.author.id)} ({str(ctx.author)})"
    user_message: str = ctx.message.content[1:]  # Skipping the command prefix
    channel: str = f"{str(ctx.channel.id)} ({str(ctx.channel)})"
    guild: str = f"{str(ctx.guild.id)} ({str(ctx.guild)})"

    print(f'[{guild}, {channel}] {username}: "{user_message}"')
client.before_invoke(logCommands)

async def ensure_cp_exists(ctx: commands.Context):
    role = discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].currentlyPlayingRoleID)
    if role is None:
        role = await ctx.guild.create_role(name="Currently Playing")
        games[ctx.guild.id].setCurrentlyPlayingRoleID(role.id)
    return True

async def ensure_st_exists(ctx: commands.Context):
    role = discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID)
    if role is None:
        role = await ctx.guild.create_role(name= "Storyteller")
        games[ctx.guild.id].setStorytellerRoleID(role.id)
        ensure_st_channel_exists(ctx)
    return True

async def ensure_st_channel_exists(ctx: commands.Context):
    channel = discord.utils.get(ctx.guild.channels, id=games[ctx.guild.id].storytellerChannelID)
    if channel is None:
        channel = await ctx.guild.create_text_channel(
            name="Storyteller Channel", 
            overwrites={
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Default members cannot see the channel
                discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID): discord.PermissionOverwrite(read_messages=True)  # The specific role can see the channel
            }
        )
    games[ctx.guild.id].setStorytellerChannelID(channel.id)
    return True


async def execute_game_command(ctx, command_function):
    msgs = command_function(ctx)
    if type(msgs) != list:
        msgs = [msgs]
    for success, msg, priv in msgs:
        for msgChunk in chunkify(anCheck(msg)): 
            if not success:
                await (ctx if not priv else ctx.author).send(msgChunk)
            
            else:
                await (ctx if not priv else ctx.author).send(msgChunk)
    return success

@client.event
async def on_ready():
    print(f'{client.user} is now running')
    for guild in client.guilds:
        games[guild.id] = Game(guild.id)  
    channel = client.get_channel(1270783733796048898)
    await channel.send(f'{client.user} is now running')

@client.command(name='play', aliases=["p"])
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def play(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].play)
    if success == 1:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].currentlyPlayingRoleID))

    elif success == 2:
        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].currentlyPlayingRoleID))

@client.command(name='playing', aliases=["pl"])
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def playing(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].playing)

@client.command(name='storytell', aliases=["st"])
@commands.check(lambda ctx: ensure_st_exists(ctx))
async def storytell(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].storytell)
    if success == 1:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID))
    
    elif success == 2:
        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID))

@client.command(name='start', aliases=["s"])
@commands.check(lambda ctx: ensure_st_exists(ctx))
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def start(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].storytell)
    if success == 1:
        pass

@client.command(name='set_role', aliases=["sr", "setrole"])
@commands.check(lambda ctx: ensure_st_exists(ctx))
@commands.check(lambda ctx: ensure_st_channel_exists(ctx))
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def set_role(ctx: commands.Context, player: discord.User, roleName: str):
    success = await execute_game_command(ctx, lambda ctx=ctx: games[ctx.guild.id].set_role(ctx, player, roleName.title()))
    if success == -1:
        await ctx.message.delete()

@client.command(name='grimoire', aliases=["g"])
@commands.check(lambda ctx: ensure_st_exists(ctx))
@commands.check(lambda ctx: ensure_st_channel_exists(ctx))
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def grimoire(ctx: commands.Context):
    success = await execute_game_command(ctx, lambda ctx=ctx: games[ctx.guild.id].grimoire(ctx))
    if success == -1:
        await ctx.message.delete()

@client.command(name='lock', aliases=["l"])
@commands.check(lambda ctx: ensure_st_exists(ctx))
async def lock(ctx: commands.Context):
    success = await execute_game_command(ctx, lambda ctx=ctx: games[ctx.guild.id].lock(ctx))

@client.command(name='roles', aliases=["rs"])
async def roles(ctx: commands.Context, priv : str = "y"):
    priv = boolify(priv)
    success = await execute_game_command(ctx, lambda ctx=ctx: games[ctx.guild.id].roles(ctx, priv))
    if success == 2:
        await ctx.message.delete()

@client.command(name='set_role_tokens', aliases=["srt", 'setroletokens'])
@commands.check(lambda ctx: ensure_st_exists(ctx))
@commands.check(lambda ctx: ensure_st_channel_exists(ctx))
@commands.check(lambda ctx: ensure_cp_exists(ctx))
async def set_role_tokens(ctx: commands.Context, role : str, token : str, player: discord.User):
    success = await execute_game_command(ctx, lambda ctx=ctx: games[ctx.guild.id].set_role_tokens(ctx, role.title(), token.title(), player))
    if success == -1:
        await ctx.message.delete()

def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()