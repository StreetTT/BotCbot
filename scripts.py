from roles import *

class Script:
    def __init__(self,playerInfo, possibleRoles, drunk) -> None:
        self.playerInfo = playerInfo
        self.possibleRoles: list[Player] = possibleRoles
        self.drunkAmongUs = drunk
    
    def __str__(self):
        return self.__class__.__name__

class TroubleBrewing(Script):
    def __init__(self) -> None:
        super().__init__({
            5: (3, 0, 1, 1),
            6: (3, 0, 2, 1),
            7: (5, 0, 2, 1),
            8: (5, 1, 2, 1),
            9: (5, 1, 3, 1),
            10: (7, 0, 3, 1),
            11: (7, 1, 3, 1),
            12: (7, 2, 3, 1),
            13: (9, 1, 3, 1),
            14: (9, 2, 3, 1),
            15: (9, 3, 3, 1)
        }, [
            Washerwoman,
            Librarian,
            Investigator,
            Chef,
            Empath,
            FortuneTeller,
            Undertaker,
            Monk,
            Ravenkeeper,
            Virgin,
            Slayer,
            Soldier,
            Mayor,
            Butler,
            Drunk,
            Recluse,
            Saint,
            Poisoner,
            Spy,
            ScarletWoman,
            Baron,
            Imp
        ], True
    )