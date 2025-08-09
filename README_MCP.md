# Little Alchemy 2 Text - MCP Integration

This project now supports playing Little Alchemy 2 Text via the Model Context Protocol (MCP), allowing LLM clients to play the game directly.

## What's New

The game can now be played through MCP tools, making it accessible to any MCP-compatible LLM client like Claude Desktop, ChatGPT with MCP support, or custom implementations.

### Enhanced Game Engine

This version includes major improvements to the original game engine:

- **🎯 Multi-result combinations** - Fixed a fundamental limitation where combinations like `pressure + lava` now correctly produce **both** `granite` and `eruption` simultaneously
- **🔒 Final items support** - The game automatically detects and notifies you when you discover final items that cannot be combined further
- **📊 Enhanced feedback** - Improved combination result detection and reporting through the MCP interface

## Setup

### Prerequisites

1. **Install dependencies** (choose one method):

   **Option A: Using conda (recommended for full compatibility)**

   ```bash
   conda env create -f environment.yml
   conda activate little_alchemy_2_text
   ```

   **Option B: Using pip**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install MCP dependencies**:

   ```bash
   pip install mcp
   ```

### Running the MCP Server

1. **Start the MCP server**:

   ```bash
   python mcp_server.py
   ```

2. **Configure your MCP client** to connect to this server using the configuration in `mcp_config.json`.

## MCP Tools Available

### Game Management

- **`start_game`** - Start a new game session
- **`get_game_state`** - View current inventory and game status
- **`make_move`** - Combine two items to create new ones
- **`list_active_sessions`** - See all active game sessions
- **`end_game`** - End a game session and get final summary

### Resources

- **Game Rules** (`game://rules`) - How to play instructions
- **Combinations Guide** (`game://combinations`) - Common item combinations

## How to Play via MCP

1. **Start a game**:

   ```json
   {
     "tool": "start_game",
     "arguments": {
       "session_id": "my-game-1",
       "game_mode": "open-ended",
       "max_rounds": 15
     }
   }
   ```

2. **Check your status**:

   ```json
   {
     "tool": "get_game_state",
     "arguments": {
       "session_id": "my-game-1"
     }
   }
   ```

3. **Make combinations**:

   ```json
   {
     "tool": "make_move",
     "arguments": {
       "session_id": "my-game-1",
       "item1": "air",
       "item2": "fire"
     }
   }
   ```

4. **Experience multi-result combinations**:

   ```json
   {
     "tool": "make_move",
     "arguments": {
       "session_id": "my-game-1",
       "item1": "pressure",
       "item2": "lava"
     }
   }
   ```

   **Response:**

   ```text
   ✅ SUCCESS! 'pressure' + 'lava' = 'eruption', 'granite'
   🎉 2 items have been added to your inventory: 'eruption', 'granite'
   🔒 'eruption' is a final item and cannot be combined with other items.
   🔒 'granite' is a final item and cannot be combined with other items.
   ```

## Game Modes

- **Open-ended**: Discover as many items as possible with no specific target
- **Targeted**: Find a specific target item (more challenging)

## Example MCP Client Configuration

For Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "little-alchemy-2-text": {
      "command": "python",
      "args": ["path/to/your/mcp_server.py"],
      "cwd": "path/to/your/LittleAlchemy2Text_MCP",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Tips for Playing

1. Start with basic elements: air, earth, fire, water
2. Try logical combinations first (fire + water = steam)
3. Build on your discoveries (steam + air = cloud)
4. Look for **multi-result combinations** - some create multiple items at once!
5. Pay attention to final item notifications - they help you focus on combinable items
6. Pay attention to successful combinations from other sessions
7. Experiment! There are hundreds of possible combinations

## Game Features via MCP

- ✅ Full game functionality through MCP tools
- ✅ Multiple concurrent game sessions
- ✅ Real-time inventory and combination tracking
- ✅ **Multi-result combinations** - Single combinations can now produce multiple items
- ✅ **Final items detection** - Automatic notification when discovering final items
- ✅ Enhanced success/failure feedback for each move with multi-item support
- ✅ Game state persistence during session
- ✅ Comprehensive help and guidance resources

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed correctly
2. Check that the MCP server starts without errors
3. Verify your MCP client configuration
4. Check the game paths in your environment

For the original game features (web interface, command-line play), see the main README.md file.

Enjoy playing Little Alchemy 2 Text through MCP! 🎮✨
