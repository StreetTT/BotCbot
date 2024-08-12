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
        self.demonBluffs = []
        self.activeTokens = []

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

    
    def play(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.locked:
            return (0, "Ask your storyteller to unlock the game", False)
        
        elif ctx.author.id in list(self.players.keys()):
            self.players.pop(ctx.author.id)       
            return (2, f"{str(ctx.author)} is no longer playing", False)
        
        self.players.update({ctx.author.id: None})
        self.db.get_table('Players')._Create({'PlayerID': ctx.author.id, 'ServerID': self.serverID})
        return (1, f"{str(ctx.author)} is now playing", False)

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
        self.locked = True
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
                self.characterCount[0] -= 1

            self.activeTokens = [token for token in self.activeTokens if not token.startswith(role.name().lower())]
            for player in self.players.values():
                if player != None:
                    for token in player.tokens.keys():
                        if token.startswith(role.name().lower()):
                            player.tokens.update({token: False})
            return (1, f"{user.name} is no longer a {str(role)}", False)
        
        elif roleName == "Drunk":
            if self.players[user.id] == None:
                return (0, f"To assign someone the drunk, assign them their fake role first", False)
             
            elif not self.script.drunkAmongUs:
                return (0, f"{roleName} is not available in {str(self.script)}", False)
            
            elif self.players[user.id].drunk:
                self.players[user.id].drunk = False
                self.activeTokens = [token for token in self.activeTokens if "drunk"]
                return (1, f"{user.name} is a Sober {str(self.players[user.id])}", False)
            
            elif [str(role) for role in list(self.players.values()) if role != None and role.drunk]:
                return (0, f"{roleName} is already assigned", False)

            self.players[user.id].drunk = True
            self.activeTokens.append("drunk")
            return (1, f"{user.name} is a {str(self.players[user.id])}", False)
        
        elif self.players[user.id] != None:
            return (0, f"{user} has a role already", False)
        
        elif roleName not in [str(role()) for role in self.script.possibleRoles]:
            return (0, f"{roleName} is not available in {str(self.script)}", False)
        
        elif [str(role) for role in list(self.players.values()) if role != None and str(role) == roleName]:
            return (0, f"{roleName} is already assigned", False)
        
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
                for token in instanciatedRole.roleTokens:
                    self.activeTokens.append(token)
                return (1, f"{user.name} is a {str(instanciatedRole)}", False) 
    
    def grimoire(self, ctx: commands.Context, ) -> msgctx | list[msgctx]: 
        if ctx.channel.id != self.storytellerChannelID:
            return (-1, f"`{ctx.message.content}`\nUse this command in the designated Storyteller Channel: <#{self.storytellerChannelID}>", True)
        
        elif len(self.players) == 0:
            return (0, f"No one is playing", False)

        grimoire = ""
        for player in self.players:
            if self.players[player]:
                grimoire += f'{f"<@{player}> is {("a " + str(self.players[player]))}\n"}'
                currentTokens = [token for token, active in self.players[player].tokens.items() if active]
                if currentTokens:
                    grimoire += f"Tokens: {currentTokens}\n"
                else: 
                    grimoire += f"\n"
            else:
                grimoire += f'{f"<@{player}> is not assigned\n\n"}'
            grimoire += f"\n"
        grimoire += f"---\nDemon Bluff: {self.demonBluffs}"
        inactive_tokens = set(self.activeTokens)
        for token in self.activeTokens:
            for role in self.players.values():
                if role is not None and role.tokens.get(token, False):
                    inactive_tokens.remove(token)
                    break
            
        grimoire += f"\nInactive Tokens: {list(inactive_tokens)}"
        return (1, grimoire, False) 

    def lock(self, ctx: commands.Context) -> msgctx | list[msgctx]: 
        self.locked = not self.locked
        return (1, f"Game is now {'un' if not self.locked else ''}locked", False) 
    
    def roles(self, ctx: commands.Context, priv: bool) -> msgctx | list[msgctx]: 
        rolecall = ""
        for role in self.script.possibleRoles:
            instanciatedRole: Player = role()
            rolecall += f'{f"`{str(instanciatedRole)}` : {instanciatedRole.help()}\n\n"}'
        return ((2 if priv else 1), rolecall, priv) 

    def set_role_tokens(self, ctx: commands.Context, roleName: str, token: str, user: discord.User):
        topsFloorInfo = {
            "Washerwoman": (1, "townfolk"),
            "Librarian": (2, "outsider"),
            "Investigator": (-1, "minion"),
        }
        taken = False

        if ctx.channel.id != self.storytellerChannelID:
            ctx.message.delete()
            return (-1, f"`{ctx.message}`\nUse this command in the designated Storyteller Channel: <#{self.storytellerChannelID}>", True)
        
        elif [role for role in list(self.players.values()) if role == None]:
            return (0, 'Not all players have been assigned a role', False)
        
        elif roleName not in [str(role()) for role in self.script.possibleRoles]:
            return (0, f"{roleName} is not available in {str(self.script)}", False)
        
        elif self.players[user.id].name() == roleName:
                return (0, f"You cannot give the {roleName} a {roleName} token", False)
        
        elif roleName in list(topsFloorInfo.keys()): 
            if token not in ("Right", "Wrong"):
                return (0, f"{roleName} doesn't have this token", False)
            
            elif token == "Right":
                if self.players[user.id].tokens.get((roleName.lower() + "Right"), False):
                    taken = True
                
                elif self.players[user.id].team != topsFloorInfo[roleName][0]:
                    return (0, f"{user.name} must be a {topsFloorInfo[roleName][1]}", False)
                
                elif self.players[user.id].tokens.get((roleName.lower() + "Wrong"), False):
                    return (0, f"{user.name} has a conflicting token", False)

                elif [role for role in list(self.players.values()) if role != None and role.tokens.get((roleName.lower() + "Right"), False)]:
                    return (0, f"Another player already has this token", False)
            
            elif token == "Wrong":
                if self.players[user.id].tokens.get((roleName.lower() + "Wrong"), False):
                    taken = True
                
                elif self.players[user.id].tokens.get((roleName.lower() + "Right"), False):
                    return (0, f"{user.name} has a conflicting token", False)
                
                elif [role for role in list(self.players.values()) if role != None and  role.tokens.get((roleName.lower() + "Wrong"), False)]:
                    return (0, f"Another player already has this token", False)
            
            self.players[user.id].tokens.update({(roleName.lower() + token): not taken})
            return (1,f"{user.name} {'no longer has' if taken else 'has been given'} the {roleName}'s {token} token",False)
                

