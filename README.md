# What is LittleAlchemy2Text?

This is a text-based version of the game Little Alchemy 2 that can be played by humans via command line interface or through MCP (Model Context Protocol).
We have implemented it by extending [Wordcraft](https://github.com/minqi/wordcraft), a python-based implementation of Little
Alchemy 2 that enabled playing the game with reinforcement learning agents.

How did we extend Wordcraft?

- added open-ended tasks. These start with the same items that Little Alchemy 2 starts with and have no target item
- added support for multiple agents. The agents are not in the same environment but receive information about the actions of others
- added ability to encode words into random strings
- added MCP (Model Context Protocol) support for integration with LLM clients
- some bug fixes (eg ensuring that tasks are set deterministically by the seed, dealing with items missing from the data base)

## How to use

### Installing dependencies

We have tested our code on Linux and Mac with Python version 3.11

To install all necessary package dependencies you can run:

    conda env create -f environment.yml

### Playing the game

This game supports two main interfaces:

#### Command Line Interface

To play via command line with human players, run:

    python play.py

You will be asked how many human players there will be. Human players perform actions through the command line interface.

#### MCP (Model Context Protocol) Interface

The game can also be played through MCP, which allows LLM clients to interact with the game using structured tools.

To start the MCP server:

    python mcp_server.py

Then configure your MCP client to connect and use the available tools:

- `start_game` - Begin a new game session
- `get_game_state` - View current inventory and game status
- `make_move` - Combine two items to create new ones
- `list_active_sessions` - Show all active games
- `end_game` - Finish with a summary

See `README_MCP.md` for detailed MCP setup instructions.
