import sqlite3 as sql
from datetime import datetime


class _Database():
    def __init__(self, name, host):  # Connect and create database
        self.__config = {}
        # self.__config.update("host": host,
        #                  "user": getenv(f"DB_{name.upper()}_USER"),
        #                  "password": getenv(f"DB_{name.upper()}_PASS")})
        self.__config.update({"database": name.lower()})
        # conn = sql.connect(**self.__config)
        conn = sql.connect(f"{self.__config['database']}.db")
        conn.row_factory = sql.Row
        c = conn.cursor()
        # c = conn.cursor(dictionary=True)
        # c.execute(f"CREATE DATABASE IF NOT EXISTS {name.lower()};")
        conn.close()

    def _GetName(self):
        return self.__config["database"]

    # General Subroutines

    def _SQLCommand(self, command):  # Connect and perform an SQL Command
        # conn = sql.connect(**self.__config)
        conn = sql.connect(f"{self.__config['database']}.db")
        # c = conn.cursor(dictionary=True)
        c = conn.cursor()
        # c.execute(f"""START TRANSACTION;""")
        c.execute(f"""BEGIN TRANSACTION;""")
        c.execute(f"""{command};""")
        data = c.fetchall()
        c.execute(f"""COMMIT;""")
        conn.close()
        print(f"SQL REQUEST | {command}\nRESPONSE | {str(data)}")
        return data

    def _ProtectFromInjection(self, rawValue):
        value = ""
        for i in rawValue:
            if i in ("'", '"', "\\"):
                value = value + "\\"
            value = value + i
        return value


class Entity():
    def __init__(self, database, createCommand):
        self._Database = database
        self._TableName = self.__class__.__name__
        self._Database._SQLCommand(
            f"""CREATE TABLE IF NOT EXISTS `{self._TableName}` ({createCommand})""")

    # Getters and Setters

    def _GetTableName(self):
        return self._TableName

    # CRUD

    def _Create(self, data={}):
        # query = f"INSERT IGNORE INTO `{self._TableName}`"
        query = f"INSERT OR REPLACE`{self._TableName}`"
        attributes = []
        values = []
        for attribute, value in data.items():
            if value != None:
                attributes.append(f"`{attribute}`")
                if type(value) in (int, float):
                    values.append(str(value))
                elif type(value) == datetime:
                    values.append(f"'{str(value)}'")                
                else:
                    value = self._Database._ProtectFromInjection(value)
                    values.append(f"'{str(value)}'")
        query += "(" + ", ".join(attributes) + ") VALUES (" + ", ".join(values) + ")"
        self._Database._SQLCommand(query)

    def _Retrieve(self, conditions={}):
        query = f"SELECT * FROM `{self._TableName}`"
        filters = self.__SplitParameters(conditions)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        results = self._Database._SQLCommand(query)
        return results

    def _Update(self, atributes={}, conditions={}):
        query = f"UPDATE `{self._TableName}`"
        data = self.__SplitParameters(atributes, False)
        if data:
            query += " SET " + ", ".join(data)
        filters = self.__SplitParameters(conditions)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        self._Database._SQLCommand(query)

    def _Delete(self, conditions={}):
        query = f"DELETE FROM `{self._TableName}`"
        filters = self.__SplitParameters(conditions)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        self._Database._SQLCommand(query)

    # General Subroutines

    # Turns a a list of parameters into an SQL statement
    def __SplitParameters(self, data, searchingStatement=True):
        parameters = []
        for attribute, value in data.items():
            if value != None:
                if type(value) in (int, float):
                    parameters.append(f"`{attribute}` = {str(value)}")
                elif type(value) == datetime:
                    parameters.append(f"`{attribute}` = '{str(value)}'")
                else:
                    value = self._Database._ProtectFromInjection(value)
                    parameters.append(f"`{attribute}` = '{str(value)}'")
            # If the query is being used to find an item (and is None)
            elif searchingStatement:
                parameters.append(f"`{attribute}` IS NULL")
            elif not searchingStatement:
                parameters.append(f"`{attribute}` = NULL")
        return parameters


class BotCBot(_Database):
    def __init__(self):
        super().__init__("botcbot", "localhost")
        self._Tables = {
                    "Servers": Servers(self),
                    "Roles": Roles(self),
                    "Game": Game(self),
                    "PlayersInServer": PlayersInServer(self)
                }
        
    def get_table(self, name=None):
        if name is None:
            return self._Tables
        return self._Tables.get(name, self._Tables)


class Servers(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `ServerID` TEXT NOT NULL UNIQUE,
        `TownSquareChannelID` TEXT,
        `NightChannelID` TEXT,
        PRIMARY KEY (`ServerID`)""")


class Roles(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `RoleName` TEXT NOT NULL UNIQUE,
        `Team` INT NOT NULL, 
        PRIMARY KEY (`RoleName`)""")
        # Team Info
        # -2 = Demon, -1 = Minion
        # 1 = Townsfolk, 2 = Outsider
        # 0 = StoryTeller


class Game(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `PlayerID` TEXT NOT NULL,
        `RoleName` TEXT,
        `ServerID` TEXT NOT NULL,
        FOREIGN KEY (`RoleName`) REFERENCES Roles(`RoleName`),
        FOREIGN KEY (`ServerID`) REFERENCES Servers(`ServerID`),
        PRIMARY KEY (`PlayerID`, `ServerID`)""")

class PlayersInServer(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `PlayerID` TEXT NOT NULL,
        `ServerID` TEXT NOT NULL,
        `NightChannelID` TEXT,
        FOREIGN KEY (`ServerID`) REFERENCES Servers(`ServerID`),
        PRIMARY KEY (`PlayerID`, `ServerID`)""")


if __name__ == "__main__":
    BotCBot()