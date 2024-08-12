# BotCbot

## Overview

**BotCbot** is a Python-based bot designed to assist in playing *Blood on the Clocktower*, a popular social deduction game. The game involves elements of deception, strategy, and storytelling, where players are assigned different roles and must work together (or against each other) to achieve their goals.

The bot automates many aspects of the game, making it easier for storytellers to manage the complex interactions and rules that make *Blood on the Clocktower* such a unique and engaging experience.

## Features

- **Player Management**: Keeps track of players and assigning discord roles appropriately.
- **Role Assignment**: Enforces role restrictions based on the script. 
- **Token Management**: Assign tokens relevant to different roles, checking they are correctly assigned or removed.
- **Grimoire Visualization**: Provides a detailed summary of the game state through the "Grimoire"

## Installation

To set up the bot, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/StreetTT/BotCbot
   cd BotCbot
   ```

2. **Set Up the `.env` File**:
   - Create a `.env` file in the root directory of the project. This file will store your bot's Discord token securely.
   - Add the following line to the `.env` file, replacing `YOUR_DISCORD_BOT_TOKEN` with your actual bot token:
     ```
     DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
     ```

3. **Install the Required Dependencies**:
   - Ensure you have Python 3.x installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Bot**:
   - Start the bot by executing:
   ```bash
   python bot.py
   ```

## Usage

### Basic Commands

The bot supports a variety of commands to facilitate gameplay. For a full list of commands, please refer to the [Commands List](https://valiant-silica-d27.notion.site/Commands-9f18385b3a7b47e3a2bf707e4343fead?pvs=4).

### Database Management

The bot uses an SQLite database (`botcbot.db`) to store game data. To see a visualisation of the schema, follow [this](https://dbdiagram.io/d/botcbot-66b39c348b4bb5230e7fb81e) link, which uses `schema.dmbl` file.

### Extending the Bot

The bot's functionality is organized into several Python files:
- `bot.py`: Core bot logic and command handling.
- `database.py`: Handles interactions with the SQLite database.
- `main.py`: Handles game logic and interactions between the files.
- `roles.py`: Defines the various roles and their interactions.
- `scripts.py`: Defines game scripts.

You can add new commands, roles, or modify existing behavior by editing these files.

## Contributing

If you'd like to contribute to the project, please fork the repository and submit a pull request with your changes. Ensure that your code follows the existing style and is well-documented.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository or reach out via the project's communication channels.