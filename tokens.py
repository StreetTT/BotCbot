from roles import Role
from players import Player

class Token:
    def __init__(self, role, name) -> None:
        self.role = role
        self.name: str = name.title().replace(" ","")
    
    def __eq__(self, other):
        if isinstance(other, Token):
            return (self.role == other.role) and (self.name == other.name) or (self.name == other.name == "Drunk")
        return False

    def __str__(self) -> str:
        return str(self.role).lower() + self.name

class TokenManager:
    def __init__(self) -> None:
        self.manager: dict[Player, set[Token]] = {

        }
        self.tokens = set()

    def addToken(self, token: Token):
        self.tokens.add(token)

    def removeToken(self, token: Token):
        self.revokeToken(token)
        if token in self.tokens:
            self.tokens.remove(token)
    
    def applyToken(self, player: Player, token: Token):
        if token not in self.tokens:
            self.addToken(token)
        if player not in self.manager:
            self.manager[player] = set()
        self.manager[player].add(token)
    
    def revokeToken(self, token: Token):
        for tokens_set in self.manager.values():
            if token in tokens_set:
                tokens_set.remove(token)
    
    def getInactiveTokens(self) -> list[Token]:
        active_tokens = set()
        for token_set in self.manager.values():
            active_tokens.update(token_set)
        inactive_tokens = self.tokens - active_tokens
        return list(inactive_tokens)
    
    def findToken(self, token: Token):
        players_with_token: list[Player] = []
        for player, tokens in self.manager.items():
            if token in tokens:
                players_with_token.append(player)
        return players_with_token

    def findPlayer(self, player: Player):
        return list(self.manager[player])