class Player:
    def __init__(self, team) -> None:
        self.team = team # Team Info
        # -2 = Demon, -1 = Minion
        # 1 = Townsfolk, 2 = Outsider
        # 0 = StoryTeller
        self.reset()

    def __str__(self):
        return f"{'Drunk ' if self.drunk else ''}{self.__class__.__name__}"

    def ability(self):
        pass
    
    def reset(self):
        self.alive = True
        self.ghostVote = True
        self.drunk = False
        self.game = None

class Washerwoman(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Townsfolk."

class Librarian(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Outsider. (Or that zero are in play.)"

class Investigator(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You start knowing that 1 of 2 players is a particular Minion."

class Chef(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You start knowing how many pairs of evil players there are."

class Empath(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night, you learn how many of your 2 alive neighbours are evil."

class FortuneTeller(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night, choose 2 players: you learn if either is a Demon. There is a good player that registers as a Demon to you."

class Undertaker(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night*, you learn which character died by execution today."

class Monk(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Each night*, choose a player (not yourself): they are safe from the Demon tonight."

class Ravenkeeper(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "If you die at night, you are woken to choose a player: you learn their character."

class Virgin(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "The 1st time you are nominated, if the nominator is a Townsfolk, they are executed immediately."

class Slayer(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "Once per game, during the day, publicly choose a player: if they are the Demon, they die."

class Soldier(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "You are safe from the Demon."

class Mayor(Player):
    def __init__(self) -> None:
        super().__init__(1)
    
    def help(self):
        return "If only 3 players live & no execution occurs, your team wins. If you die at night, another player might die instead."

class Butler(Player):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "Each night, choose a player (not yourself): tomorrow, you may only vote if they are voting too."

class Drunk(Player):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "You do not know you are the Drunk. You think you are a Townsfolk character, but you are not."

class Recluse(Player):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "You might register as evil & as a Minion or Demon, even if dead."

class Saint(Player):
    def __init__(self) -> None:
        super().__init__(2)
    
    def help(self):
        return "If you die by execution, your team loses."

class Poisoner(Player):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "Each night, choose a player: they are poisoned tonight and tomorrow day."

class Spy(Player):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "Each night, you see the Grimoire. You might register as good & as a Townsfolk or Outsider, even if dead."

class ScarletWoman(Player):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "If there are 5 or more players alive (Travellers don’t count) & the Demon dies, you become the Demon."

class Baron(Player):
    def __init__(self) -> None:
        super().__init__(-1)
    
    def help(self):
        return "There are extra Outsiders in play. [+2 Outsiders]"

class Imp(Player):
    def __init__(self) -> None:
        super().__init__(-2)
    
    def help(self):
        return "Each night*, choose a player: they die. If you kill yourself this way, a Minion becomes the Imp."
