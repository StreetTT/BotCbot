# BotCbot

Overview

This Python bot is designed to assist with playing Blood on the Clocktower—a social deduction game that combines elements of deception, strategy, and storytelling.

# Commands

## Key
[] means required

- `join`
Join the role to play the next game of BotC.

- `leave`
Leave the role to play the next game of BotC.

- `playing`
List all players ready to play BotC

- `storytell`
Gives you the role of storyteller. Only 1 person can have this role. If you are the storyteller and use this command, you will no longer be the storyteller.

- `set_role [@User] [Role]`
Give a player a role. When giving players the drunk role, apply their fake role first.
Can only be done in the Storyteller channel, by the storyteller.

- `rolecall`
Send a list of all players and what roles they will be playing.
Can only be done in the Storyteller channel, by the storyteller.

- `lock`
Toggle the game between a locked and unlocked state. When locked players can neither leave nor join.
Can only be done by the storyteller.