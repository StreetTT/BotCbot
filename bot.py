from main import Game
from os import getenv
from dotenv import load_dotenv as LoadEnvVariables
import discord
from discord.ext import commands
from random import choice, randint

LoadEnvVariables()
TOKEN = getenv("DiscordBotToken")

def boolify(a):
    if a in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif a in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix="!", intents=intents)

roleTypes = ["Currently Playing", "Storyteller"]
games: dict[int,Game] = {}

async def logCommands(ctx: commands.Context) -> None:
    username: str = f"{str(ctx.author.id)} ({str(ctx.author)})"
    user_message: str = ctx.message.content[1:]  # Skipping the command prefix
    channel: str = f"{str(ctx.channel.id)} ({str(ctx.channel)})"
    guild: str = f"{str(ctx.guild.id)} ({str(ctx.guild)})"

    print(f'[{guild}, {channel}] {username}: "{user_message}"')
client.before_invoke(logCommands)

async def ensure_role_exists(ctx: commands.Context, role_id: int, roleType: int):
    role = discord.utils.get(ctx.guild.roles, id=role_id)
    if role is None:
        role = await ctx.guild.create_role(name= roleTypes[roleType])
        games[ctx.guild.id].updateID(roleTypes[roleType], role.id)
    return True

async def execute_game_command(ctx, command_function):
    msgs = command_function(ctx)
    if type(msgs) != list:
        msgs = [msgs]
    for success, msg, priv in msgs:
        if not success:
            await (ctx if not priv else ctx.author).send(msg)
        else:
            await (ctx if not priv else ctx.author).send(msg)
    return success

@client.event
async def on_ready():
    print(f'{client.user} is now running')
    for guild in client.guilds:
        games[guild.id] = Game(guild.id)  

@client.command(name='join')
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].currentlyPlayingRoleID, 0))
async def join(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].join)
    if success:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].currentlyPlayingRoleID))

@client.command(name='leave')
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].currentlyPlayingRoleID, 0))
async def leave(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].leave)
    if success:
        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].currentlyPlayingRoleID))

@client.command(name='playing')
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].currentlyPlayingRoleID))
async def playing(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].leave)

@client.command(name='storytell')
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].storytellerRoleID, 1))
async def storytell(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].storytell)
    if success == 1:
        await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID))
    if success == 2:
        await ctx.author.remove_roles(discord.utils.get(ctx.guild.roles, id=games[ctx.guild.id].storytellerRoleID))

@client.command(name='start')
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].storytellerRoleID, 1))
@commands.check(lambda ctx: ensure_role_exists(ctx, games[ctx.guild.id].currentlyPlayingRoleID, 0))
async def start(ctx: commands.Context):
    success = await execute_game_command(ctx, games[ctx.guild.id].storytell)
    if success == 1:
        pass

def main() -> None:
    client.run(TOKEN)

if __name__ == '__main__':
    main()