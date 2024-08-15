from roles import Role

class Player:
    def __init__(self, id, role):
        self.role: Role = role
        self.ID = id
        self.left: Player = None
        self.right: Player = None
    
    def __str__(self) -> str:
        return str(self.ID)

class PlayerList:
    def __init__(self):
        self.head: Player = None
        self.size = 0
    
    def __iter__(self):
        current = self.head
        count = 0
        while count < self.size:
            yield current
            current = current.right
            count += 1
    
    def __len__(self):
        return self.size

    def append(self, id, role=None):
        new_player = Player(id, role)
        if not self.head:
            self.head = new_player
            self.head.right = self.head
            self.head.left = self.head
        else:
            last = self.head.left
            last.right = new_player
            new_player.left = last
            new_player.right = self.head
            self.head.left = new_player
        self.size += 1
        return new_player

    def prepend(self, id, role=None):
        new_player = Player(id, role)
        if not self.head:
            self.head = new_player
            self.head.right = self.head
            self.head.left = self.head
        else:
            last = self.head.left
            new_player.right = self.head
            new_player.left = last
            self.head.left = new_player
            last.right = new_player
            self.head = new_player
        self.size += 1
        return new_player

    def remove(self, id):
        if not self.head:
            return

        current = self.head
        while True:
            if current.ID == id:
                old_player = current
                if current == self.head and current.right == self.head:
                    # Only one element in the list
                    self.head = None
                else:
                    current.left.right = current.right
                    current.right.left = current.left
                    if current == self.head:
                        self.head = current.right
                self.size -= 1
                return old_player
            current = current.right
            if current == self.head:
                break

    def search(self, id=None, role=None):
        if not self.head:
            return None

        current = self.head
        while True:
            if id is not None and current.ID == id:
                return current
            elif role is not None and current.role == role:
                return current
            current = current.right
            if current == self.head:
                break
        return None

    def print_list(self):
        if not self.head:
            return

        current = self.head
        while True:
            print(f"{current.role}", end=" -> ")
            current = current.right
            if current == self.head:
                break
        print(f"{self.head.role} ({self.size})")