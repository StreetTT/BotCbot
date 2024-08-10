from database import BotCBot
from scripts import *
import discord
from discord.ext import commands

msgctx = tuple[int, str, bool]       

class Game:
    def __init__(self, server_id) -> None:
        self.serverID = server_id
        self.started = False
        self.locked = False
        self.players:dict[int, Player] = {}
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
        self.storytellerChannelID = serverInfo["StorytellerChannelID"]
        self.script: Script = TroubleBrewing()
        self.characterCount = [0,0,0,0]

    def setCurrentlyPlayingRoleID(self, id):
        self.currentlyPlayingRoleID = id
        self.db.get_table('Servers')._Update({
            "CurrentlyPlayingRoleID": self.currentlyPlayingRoleID
        }, {
            'ServerID': self.serverID
        })
    
    def setStorytellerRoleID(self, id):
        self.storytellerRoleID = id
        self.db.get_table('Servers')._Update({
            "StorytellerRoleID": self.storytellerRoleID
        }, {
            'ServerID': self.serverID
        })

    def setTownSquareChannelID(self, id):
        self.townSquareChannelID = id
        self.db.get_table('Servers')._Update({
            "TownSquareChannelID": self.townSquareChannelID
        }, {
            'ServerID': self.serverID
        })
    
    def setStorytellerChannelID(self, id):
        self.storytellerChannelID = id
        self.db.get_table('Servers')._Update({
            "StorytellerChannelID": self.storytellerChannelID
        }, {
            'ServerID': self.serverID
        })
    
    def set_script(self):
        self.maxCharacterCount = self.script.playerInfo.get(
            len(list(self.players.keys())),
            self.script.playerInfo[15]
        )


    
    def join(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.locked:
            return (0, "Ask your storyteller to unlock the game", False)
        
        elif ctx.author.id in list(self.players.keys()):
            return (0, "Person is already playing", False)
        
        self.players.update({ctx.author.id: None})
        self.db.get_table('Players')._Create({'PlayerID': ctx.author.id, 'ServerID': self.serverID})
        return (1, f"{str(ctx.author)} is now playing", False)

    def leave(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.locked:
            return (0, "Ask your storyteller to unlock the game", False)
        
        elif ctx.author.id not in list(self.players.keys()):
            return (0, "Person is not playing", False)
        
        self.players.pop(ctx.author.id)       
        return (1, f"{str(ctx.author)} is no longer playing", False)

    def playing(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        role = discord.utils.get(ctx.guild.roles, id=self.currentlyPlayingRoleID)
        members_with_role = [member for member in ctx.guild.members if role in member.roles]
        if not members_with_role:
            return (0, 'No members are waiting to play', False)
        
        members_names = ", ".join([member.name for member in members_with_role])
        return (1, f'Members waiting to play BotC: {members_names}', False)
    
    def storytell(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.storyteller == ctx.author.id:
            self.storyteller = None
            return (2, 'You are no longer the storyteller', False)
        
        elif self.storyteller != None:
            return (0, 'There is already a storyteller', False)
        
        self.storyteller = ctx.author.id
        return (1, f'{f"<@&{self.currentlyPlayingRoleID}>"}, {ctx.author.name} is now your storyteller', False)

    def start(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.storyteller == None:
            return (0, "Game doesn't have storyteller", False)
        
        elif len(list(self.players.keys())) < 5:
            return (0, 'There are not enough players', False)
        
        elif len(list(self.players.keys())) > 20:
            return (0, 'There are too many players', False)
        
        elif [role for role in list(self.players.items()) if role == None]:
            return (0, 'Not all players have been assigned a role', False)
        
        self.started = True
        return (1, f'The game has started', False)

    def set_role(self, ctx: commands.Context, user: discord.User, roleName:str) -> msgctx | list[msgctx]:
        if ctx.channel.id != self.storytellerChannelID:
            ctx.message.delete()
            return (-1, f"`{ctx.message}`\nUse this command in the designated Storyteller Channel: <#{self.storytellerChannelID}>", True)
        self.set_script()
        if self.started:
            return (0, "Game has already started", False)
        
        elif user.id not in list(self.players.keys()):
            return (0, f"{user} is not playing", False)
        
        elif str(self.players[user.id]) == roleName:
            role = self.players[user.id]
            self.players[user.id] = None
            if role.team == -2:
                self.characterCount[3] -= 1
            
            elif role.team == -1:
                self.characterCount[2] -= 1
            
            elif role.team == 2:
                self.characterCount[1] -= 1
            
            elif role.team == 1:
                self.characterCount[0] += 1

            return (1, f"{user.name} is no longer a {str(role)}", False)
        
        elif roleName == "Drunk":
            if self.players[user.id] == None:
                return (0, f"To assign someone the drunk, assign them their fake role first", False)
             
            elif not self.script.drunkAmongUs:
                return (0, f"{roleName} is not available in {str(self.script)}", False)
            
            elif self.players[user.id].drunk:
                self.players[user.id].drunk = False
                return (1, f"{user.name} is a Sober {str(self.players[user.id])}", False)
            
            elif [str(role) for role in list(self.players.values()) if role != None and role.drunk]:
                return (0, f"{roleName} is already assigned", False)

            self.players[user.id].drunk = True
            return (1, f"{user.name} is a {str(self.players[user.id])}", False)
        
        elif roleName not in [str(role()) for role in self.script.possibleRoles]:
            return (0, f"{roleName} is not available in {str(self.script)}", False)
        
        elif [str(role) for role in list(self.players.values()) if role != None and str(role) == roleName]:
            return (0, f"{roleName} is already assigned", False)
        
        self.locked = True
        for role in self.script.possibleRoles:
            instanciatedRole: Player = role()
            if str(instanciatedRole) == roleName:
                if instanciatedRole.team == -2:
                    if self.characterCount[3] != self.maxCharacterCount[3]:
                        self.characterCount[3] += 1
                    else:
                        return (0, f"There are enough Demons in this game", False)
                
                elif instanciatedRole.team == -1:
                    if self.characterCount[2] != self.maxCharacterCount[2]:
                        self.characterCount[2] += 1
                    else:
                        return (0, f"There are enough Minions in this game", False)
                
                elif instanciatedRole.team == 2:
                    if self.characterCount[1] != self.maxCharacterCount[1]:
                        self.characterCount[1] += 1
                    else:
                        return (0, f"There are enough Outsiders in this game", False)
                
                elif instanciatedRole.team == 1:
                    if self.characterCount[0] != self.maxCharacterCount[0]:
                        self.characterCount[0] += 1
                    else:
                        return (0, f"There are enough Townfolk in this game", False)
                self.players.update({user.id: instanciatedRole})
                instanciatedRole.game = self
                return (1, f"{user.name} is a {str(instanciatedRole)}", False) 
    
    def rolecall(self, ctx: commands.Context) -> msgctx | list[msgctx]: 
        if ctx.channel.id != self.storytellerChannelID:
            return (-1, f"`{ctx.message.content}`\nUse this command in the designated Storyteller Channel: <#{self.storytellerChannelID}>", True)
        
        elif len(self.players) == 0:
            return (0, f"No one is playing", False)

        rolecall = ""
        for player in self.players:
             rolecall += f'{f"<@{player}> is {("a " + str(self.players[player])) if self.players[player] else "not assigned"}\n"}'
        return (1, rolecall, False) 

    def lock(self, ctx: commands.Context) -> msgctx | list[msgctx]: 
        self.locked = not self.locked
        return (1, f"Game is now {'un' if not self.locked else ''}locked", False) 

