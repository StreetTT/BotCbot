from database import BotCBot
import discord
from discord.ext import commands

msgctx = (int, str, bool)       

class Game:
    def __init__(self, server_id) -> None:
        self.serverID = server_id
        self.started = False
        self.players = {}
        self.storyteller = None
        self.db = BotCBot()
        self.db.get_table('Servers')._Create({
            'ServerID': self.serverID
        })
        serverInfo = self.db.get_table('Servers')._Retrieve({
            'ServerID': self.serverID
        })
        self.currentlyPlayingRoleID = serverInfo["CurrentlyPlayingRoleID"]
        self.storytellerRoleID = serverInfo["StorytellerRoleID"]
        self.townSquareChannelID = serverInfo["TownSquareChannelID"]

    
    def updateID(self, type, id):
        if type == "Currently Playing":
            self.currentlyPlayingRoleID = id
            field = "CurrentlyPlayingRoleID"
        elif type == "Storyteller":
            self.storytellerRoleID = id
            field = "StorytellerRoleID"
    
        self.db.get_table('Servers')._Update({
            field: getattr(self, (field[0].lower() + field[1:]))
        }, {
            'ServerID': self.serverID
        })

    
    def join(self, ctx: commands.Context) -> msgctx | [msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        if ctx.author.id in list(self.players.keys()):
            return (0, "Person is already playing", False)
        self.players.update({ctx.author.id: None})
        self.db.get_table('Players')._Create({'PlayerID': ctx.author.id, 'ServerID': self.serverID})
        return (1, f"{str(ctx.author)} is now playing", False)

    def leave(self, ctx: commands.Context) -> msgctx | [msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        if ctx.author.id not in list(self.players.keys()):
            return (0, "Person is not playing", False)
        self.players.pop(ctx.author.id)
        # Remove the player from the database        
        return (1, f"{str(ctx.author)} is no longer playing", False)

    def playing(self, ctx: commands.Context) -> msgctx | [msgctx]:
        role = discord.utils.get(ctx.guild.roles, id=self.currentlyPlayingRoleID)
        members_with_role = [member for member in ctx.guild.members if role in member.roles]
        if not members_with_role:
            return (0, 'No members are waiting to play', False)
        members_names = ", ".join([member.name for member in members_with_role])
        return (1, f'Members waiting to play BotC: {members_names}', False)
    
    def storytell(self, ctx: commands.Context) -> msgctx | [msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        elif self.storyteller == ctx.author.id:
            self.storyteller = None
            return (2, 'You are no longer the storyteller', False)
        elif self.storyteller != None:
            return (0, 'There is already a storyteller', False)
        self.storyteller = ctx.author.id
        return [
            (1, f'{f"<@&{self.currentlyPlayingRoleID}>"}, {ctx.author.name} is now your storyteller', False), 
            (1, f'Get ready to pick roles', True)
            ]

    def start(self, ctx: commands.Context) -> msgctx | [msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        if self.storyteller == None:
            return (0, 'There is not storyteller', False)
        if len(list(self.players.keys())) < 5:
            return (0, 'There are not enough players', False)
        return (1, f'The game has started', False)
        
