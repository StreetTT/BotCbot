from database import BotCBot
from scripts import *
import discord
from discord.ext import commands
from players import PlayerList
from tokens import Token, TokenManager

msgctx = tuple[int, str, bool]       

class Game:
    def __init__(self, server_id) -> None:
        self.serverID = server_id
        self.started = False
        self.locked = False
        self.players = PlayerList()
        self.tokens = TokenManager()
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
            len(self.players),
            self.script.playerInfo[15]
        )

    def tally_role(self, role, subtract = False):
        x = -1 if subtract else 1
        if role.team == -2:
            if subtract or self.characterCount[3] != self.maxCharacterCount[3]:
                self.characterCount[3] += x
            else:
                return (0, f"There are enough Demons in this game", False)
        
        elif role.team == -1:
            if subtract or self.characterCount[2] != self.maxCharacterCount[2]:
                self.characterCount[2] += x
            else:
                return (0, f"There are enough Minions in this game", False)
        
        elif role.team == 2:
            if subtract or self.characterCount[1] != self.maxCharacterCount[1]:
                self.characterCount[1] += x
            else:
                return (0, f"There are enough Outsiders in this game", False)
        
        elif role.team == 1:
            if subtract or self.characterCount[0] != self.maxCharacterCount[0]:
                self.characterCount[0] += x
            else:
                return (0, f"There are enough Townfolk in this game", False)
    
    def play(self, ctx: commands.Context) -> msgctx | list[msgctx]:
        if self.started:
            return (0, "Game has already started", False)
        
        elif self.locked:
            return (0, "Ask your storyteller to unlock the game", False)
        
        elif self.players.search(id=ctx.author.id):
            self.players.remove(ctx.author.id)
            return (2, f"{str(ctx.author)} is no longer playing", False)
        
        self.players.append(ctx.author.id)
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
        
        elif len(self.players) < self.script.minPlayers():
            return (0, 'There are not enough players', False)
        
        elif len(self.players) > self.script.maxPlayers():
            return (0, 'There are too many players', False)
        
        elif any(player.role is None for player in self.players):
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
        
        elif not self.players.search(id=user.id):
            return (0, f"{user} is not playing", False)
        
        usersPlayer = self.players.search(id=user.id)
        if str(usersPlayer.role) == roleName:
            role = usersPlayer.role
            usersPlayer.role = None
            self.tally_role(role, subtract=True)
            for token in role.roleTokens:
                self.tokens.removeToken(token)
            return (1, f"{user.name} is no longer a {str(role)}", False)
        
        elif roleName == "Drunk":
            if usersPlayer.role == None:
                return (0, f"To assign someone the drunk, assign them their fake role first", False)
             
            elif not self.script.drunkAmongUs:
                return (0, f"{roleName} is not available in {str(self.script)}", False)
            
            elif usersPlayer.role.drunk:
                usersPlayer.role.drunk = False
                self.tokens.revokeToken(Token(usersPlayer.role, "Drunk"))
                return (1, f"{user.name} is a Sober {str(usersPlayer.role)}", False)
            
            elif any((player.role.drunk) for player in self.players):
                return (0, f"{roleName} is already assigned", False)

            usersPlayer.role.drunk = True
            self.tokens.applyToken(usersPlayer, Token(usersPlayer.role, "Drunk"))
            return (1, f"{user.name} is a {str(usersPlayer.role)}", False)
        
        elif usersPlayer.role != None:
            return (0, f"{user} has a role already", False)
        
        elif roleName not in [str(role()) for role in self.script.possibleRoles]:
            return (0, f"{roleName} is not available in {str(self.script)}", False)
        
        elif any((player.role is not None and str(player.role) == roleName) for player in self.players):
            return (0, f"{roleName} is already assigned", False)
        
        for role in self.script.possibleRoles:
            instanciatedRole: Role = role()
            if str(instanciatedRole) == roleName:
                msg = self.tally_role(instanciatedRole)
                if msg:
                    return msg
                usersPlayer.role = instanciatedRole
                instanciatedRole.game = self
                for token in instanciatedRole.roleTokens:
                    self.tokens.addToken(token)
                return (1, f"{user.name} is a {str(instanciatedRole)}", False) 
    
    def grimoire(self, ctx: commands.Context, ) -> msgctx | list[msgctx]: 
        if ctx.channel.id != self.storytellerChannelID:
            return (-1, f"`{ctx.message.content}`\nUse this command in the designated Storyteller Channel: <#{self.storytellerChannelID}>", True)
        
        elif len(self.players) == 0:
            return (0, f"No one is playing", False)

        grimoire = ""
        for player in self.players:
            if player.role:
                grimoire += f'{f"<@{str(player)}> is {("a " + str(player.role))}\n"}'
                currentTokens = self.tokens.findPlayer(player)
                if currentTokens:
                    grimoire += f"Tokens: {currentTokens}\n"
                else: 
                    grimoire += f"\n"
            else:
                grimoire += f'{f"<@{str(player)}> is not assigned\n\n"}'
            grimoire += f"\n"
        grimoire += f"---\nDemon Bluff: {self.demonBluffs}"
        grimoire += f"\nInactive Tokens: {self.tokens.getInactiveTokens()}"
        return (1, grimoire, False) 

    def lock(self, ctx: commands.Context) -> msgctx | list[msgctx]: 
        self.locked = not self.locked
        return (1, f"Game is now {'un' if not self.locked else ''}locked", False) 
    
    def roles(self, ctx: commands.Context, priv: bool) -> msgctx | list[msgctx]: 
        rolecall = ""
        for role in self.script.possibleRoles:
            instanciatedRole: Role = role()
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
        
        elif [player.role for player in self.players if not player.role]:
            return (0, 'Not all players have been assigned a role', False)
        
        elif roleName not in [str(role()) for role in self.script.possibleRoles]:
            return (0, f"{roleName} is not available in {str(self.script)}", False)
        
        usersPlayer = self.players.search(id=user.id)
        if usersPlayer.role.name() == roleName:
                return (0, f"You cannot give the {roleName} a {roleName} token", False)
        
        elif roleName in list(topsFloorInfo.keys()): 
            if token not in ("Right", "Wrong"):
                return (0, f"{roleName} doesn't have this token", False)
            

            right_token = Token(role=roleName, name="Right")
            wrong_token = Token(role=roleName, name="Wrong")
            playersTokens = self.tokens.findPlayer(usersPlayer)
            if token == "Right":
                if right_token in playersTokens:
                    taken = True

                elif usersPlayer.role.team != topsFloorInfo[roleName][0]:
                    return (0, f"{user.name} must be a {topsFloorInfo[roleName][1]}", False)

                elif wrong_token in playersTokens:
                    return (0, f"{user.name} has a conflicting token", False)
                
                # If people already have the right_token token (We know user doesn't already)
                elif self.tokens.findToken(right_token):
                    return (0, f"Another player already has this token", False)

            elif token == "Wrong":
                if wrong_token in playersTokens:
                    taken = True
                
                elif right_token in playersTokens:
                    return (0, f"{user.name} has a conflicting token", False)
                
                # If people already have the wrong_token token (We know user doesn't already)
                elif self.tokens.findToken(wrong_token):
                    return (0, f"Another player already has this token", False)
            
            if taken:
                self.tokens.revokeToken(usersPlayer, token)
            else: 
                self.tokens.applyToken(usersPlayer, token)
            return (1,f"{user.name} {'no longer has' if taken else 'has been given'} the {roleName}'s {token} token",False)
                

