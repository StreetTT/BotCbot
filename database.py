import sqlite3 as sql
from datetime import datetime

# # All double comments like this one are for when I make the eventual switch to MySQL 
# # (My laptop doesn't have enough space that I can confidently run it without fear of crashing every 2 minutes)


class _Database():
    def __init__(self, name, host):  # Connect and create database
        self.__config = {}
        # # self.__config.update("host": host,
        # #                  "user": getenv(f"DB_{name.upper()}_USER"),
        # #                  "password": getenv(f"DB_{name.upper()}_PASS")})
        self.__config.update({"database": name.lower()})
        # # conn = sql.connect(**self.__config)
        conn = sql.connect(f"{self.__config['database']}.db")
        conn.row_factory = sql.Row
        c = conn.cursor()
        # # c = conn.cursor(dictionary=True)
        # # c.execute(f"CREATE DATABASE IF NOT EXISTS {name.lower()};")
        conn.close()

    def _GetName(self):
        return self.__config["database"]

    # General Subroutines

    def _SQLCommand(self, command):  # Connect and perform an SQL Command
        print(f"SQL REQUEST | {command}\nRESPONSE |", end=" ")
        # # conn = sql.connect(**self.__config)
        conn = sql.connect(f"{self.__config['database']}.db")
        # # c = conn.cursor(dictionary=True)
        conn.row_factory = sql.Row
        c = conn.cursor()
        # # c.execute(f"""START TRANSACTION;""")
        c.execute(f"""BEGIN TRANSACTION;""")
        c.execute(f"""{command};""")
        rows = (c.fetchall())
        data = [dict(row) for row in rows]
        print(str(data))
        c.execute(f"""COMMIT;""")
        conn.close()
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
        # # query = f"INSERT IGNORE INTO `{self._TableName}`"
        query = f"INSERT OR IGNORE INTO `{self._TableName}`"
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
        return results[0]

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
        self._Tables: dict[str,Entity] = {
                    "Servers": Servers(self),
                    "Players": Players(self)
                }
        
    def get_table(self, name=None)-> Entity | dict[str,Entity]:
        if name is None:
            return self._Tables
        return self._Tables.get(name, self._Tables)


class Servers(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `ServerID` INT NOT NULL UNIQUE,
        `TownSquareChannelID` INT,
        `CurrentlyPlayingRoleID` INT,
        `StorytellerRoleID` INT,
        `StorytellerChannelID` INT,
        PRIMARY KEY (`ServerID`)""")

class Players(Entity):
    def __init__(self, database):
        super().__init__(database, """
        `PlayerID` INT NOT NULL,
        `ServerID` INT NOT NULL,
        `NightChannelID` INT,
        FOREIGN KEY (`ServerID`) REFERENCES Servers(`ServerID`),
        PRIMARY KEY (`PlayerID`, `ServerID`)""")


if __name__ == "__main__":
    BotCBot()