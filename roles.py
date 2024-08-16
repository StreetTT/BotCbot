from random import randint
from tokens import Token
from players import Player
from main import Game

class Role:
    def __init__(self, team) -> None:
        self.team = team # Team Info
        # -2 = Demon, -1 = Minion
        # 1 = Townsfolk, 2 = Outsider
        # 0 = StoryTeller
        self.alive = True
        self.ghostVote = True
        self.drunk = False
        self.game: Game = None
        self.roleTokens: list[Token] = []

    def __str__(self):
        return f"{'Drunk ' if self.drunk else ''}{self.__class__.__name__}"
    
    def name(self):
        return self.__class__.__name__

    def ability(self):
        pass
    
    def help(self):
        pass
    
    def perform_ability(self):
        if self.drunk:
            return "Oh let's 'ave a likle drink *hickup*"
        return self.ability()

    def topFloor(self):
        players: list[Player] = []
        folk = None
        for token in self.roleTokens:
            player = self.game.tokens.findToken(token)[0]
            if token.name == "Right":
                folk = player.role
            players.append(player)
        x = randint(0,1)
        return f"Either <@{players[x].ID}> or <@{players[0 if x else 1].ID}> is a {str(folk)}"

class Washerwoman(Role):
    def __init__(self) -> None:
        super().__init__(1)
        for token in ("Right", "Wrong"):
            self.roleTokens.append(Token(self, token))
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Townsfolk."
    
    def ability(self):
        return self.topFloor()

class Librarian(Role):
    def __init__(self) -> None:
        super().__init__(1)
        for token in ("Right", "Wrong"):
            self.roleTokens.append(Token(self, token))
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)"
    
    def ability(self):
        if self.game.characterCount[1] == 0:
            return "There are 0 Outsiders in play"
        return self.topFloor()
        

class Investigator(Role):
    def __init__(self) -> None:
        super().__init__(1)
        for token in ("Right", "Wrong"):
            self.roleTokens.append(Token(self, token))
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Minion."
    
    def ability(self):
        return self.topFloor()

class Chef(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You start knowing how many pairs of evil players there are."

class Empath(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night, you learn how many of your 2 alive neighbours are evil."

class FortuneTeller(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you."

class Undertaker(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night (excluding the first), you learn which character died by execution today."

class Monk(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night (excluding the first), choose a player (not yourself): they are safe from the Demon tonight."

class Ravenkeeper(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "If you die at night, you are woken to choose a player: you learn their character."

class Virgin(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately."

class Slayer(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Once per game, during the day, publicly choose a player: if they are the Demon, they die."

class Soldier(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You are safe from the Demon."

class Mayor(Role):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead."

class Butler(Role):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too."

class Drunk(Role):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "You do not know you are the Drunk. You think you are a Townsfolk character, but you are not."

class Recluse(Role):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "You might register as evil & as a Minion or Demon, even if dead."

class Saint(Role):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "If you die by execution, your team loses."

class Poisoner(Role):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "Each night, choose a player: they are poisoned tonight and tomorrow day."

class Spy(Role):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead."

class ScarletWoman(Role):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "If there are 5 or more players alive (Travellers don't count) & the Demon dies, you become the Demon."

class Baron(Role):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "There are extra Outsiders in play. [+2 Outsiders]"

class Imp(Role):
    def __init__(self) -> None:
        super().__init__(-2)
    
    def help(self):
        return "Each night (excluding the first), choose a player: they die. If you kill yourself this way, a Minion becomes the Imp."
