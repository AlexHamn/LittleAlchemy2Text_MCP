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
- **`make_move`** - Combine two items to create new ones (now with comprehensive logging)
- **`list_active_sessions`** - See all active game sessions
- **`end_game`** - End a game session and get final summary

### Data Analysis & Logging

- **`get_attempt_logs`** - Retrieve detailed logs of all attempts with comprehensive parameters for analysis
- **`debug_logging_status`** - Debug tool to check logging system status across all sessions

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

3. **Make combinations** (now with reasoning logging):

   ```json
   {
     "tool": "make_move",
     "arguments": {
       "session_id": "my-game-1",
       "item1": "air",
       "item2": "fire",
       "reasoning_explanation": "Air and fire should create energy through combustion"
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

## Comprehensive Attempt Logging

### Overview

Every attempt (successful or failed) is automatically logged with comprehensive parameters for detailed analysis. This is ideal for research, learning pattern analysis, and understanding player behavior.

### Logged Parameters

Each attempt captures the following 12 parameters:

| Parameter                 | Description                            | Example                                |
| ------------------------- | -------------------------------------- | -------------------------------------- |
| `Session_ID`              | Unique game session identifier         | `"my-game-1"`                          |
| `Attempt_Number`          | Sequential attempt number (1, 2, 3...) | `5`                                    |
| `Element_1`               | First element in combination           | `"fire"`                               |
| `Element_2`               | Second element in combination          | `"water"`                              |
| `Success`                 | Whether the combination succeeded      | `true`                                 |
| `Result_Element`          | Created element(s) if successful       | `"steam"` or `"granite, eruption"`     |
| `Inventory_Size_Before`   | Number of items before this attempt    | `8`                                    |
| `Reasoning_Explanation`   | Player's reasoning for the attempt     | `"Fire and water should create steam"` |
| `Is_Novel_Combination`    | First time trying this combination     | `true`                                 |
| `Current_Streak_Type`     | Current streak type                    | `"success"` or `"failure"`             |
| `Current_Streak_Length`   | Length of current streak               | `3`                                    |
| `Time_Since_Last_Success` | Seconds since last successful attempt  | `45.2` or `null`                       |

### Accessing Logs

#### 1. View Recent Attempts (Summary)

```json
{
  "tool": "get_attempt_logs",
  "arguments": {
    "session_id": "my-game-1",
    "format": "summary"
  }
}
```

**Response:**

```text
📊 ATTEMPT LOGS SUMMARY - Session: my-game-1
Total Attempts: 8
✅ Successful Attempts: 5
❌ Failed Attempts: 3
📈 Success Rate: 62.5%

🕐 RECENT ATTEMPTS:
✅ #6: air + fire -> energy | Reasoning: Basic combustion reaction
❌ #7: energy + earth | Reasoning: Trying to create earthquake
✅ #8: fire + water -> steam | Reasoning: Evaporation process
```

#### 2. Export Complete Data (JSON)

```json
{
  "tool": "get_attempt_logs",
  "arguments": {
    "session_id": "my-game-1",
    "format": "json"
  }
}
```

#### 3. Export for Analysis (CSV)

```json
{
  "tool": "get_attempt_logs",
  "arguments": {
    "session_id": "my-game-1",
    "format": "csv"
  }
}
```

### Debug & Monitoring

Check the logging system status across all sessions:

```json
{
  "tool": "debug_logging_status",
  "arguments": {}
}
```

**Response:**

```text
🔍 LOGGING SYSTEM DEBUG STATUS

Total sessions with logs: 2

📊 LOG SUMMARY BY SESSION:
  • Session 'my-game-1': 8 attempts
    Last attempt: fire + water = ✅
    Last logged: 2024-01-15T14:30:25.123456
  • Session 'test-session': 3 attempts
    Last attempt: air + earth = ❌
    Last logged: 2024-01-15T14:25:10.987654

💡 TO ACCESS LOGS:
Use 'get_attempt_logs' with your session_id to view detailed logs.
```

### Automatic Feedback

Every `make_move` response now includes logging confirmation:

```text
✅ SUCCESS! 'fire' + 'water' = 'steam'
🎉 'steam' has been added to your inventory!

Rounds used: 5/15
Items discovered: 9
📝 Logged attempt #5 (Use 'get_attempt_logs' to view all logs)
```

### Use Cases

1. **Research Analysis**: Export CSV data for statistical analysis of learning patterns
2. **Player Behavior Study**: Analyze reasoning explanations and decision patterns
3. **Success Pattern Recognition**: Identify which reasoning approaches lead to success
4. **Streak Analysis**: Study how success/failure streaks affect player behavior
5. **Timing Analysis**: Understand how time pressure affects decision making
6. **Novel vs. Repeated Attempts**: Compare performance on new vs. familiar combinations

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
6. **Add reasoning explanations** to your attempts for better logging and analysis
7. Use `get_attempt_logs` to review your strategy and success patterns
8. Pay attention to successful combinations from other sessions
9. Experiment! There are hundreds of possible combinations

## Game Features via MCP

- ✅ Full game functionality through MCP tools
- ✅ Multiple concurrent game sessions
- ✅ Real-time inventory and combination tracking
- ✅ **Multi-result combinations** - Single combinations can now produce multiple items
- ✅ **Final items detection** - Automatic notification when discovering final items
- ✅ **Comprehensive attempt logging** - Every attempt logged with 12 parameters for analysis
- ✅ **Reasoning explanation capture** - Optional reasoning input for each attempt
- ✅ **Advanced analytics** - Success rates, streaks, timing, and pattern analysis
- ✅ **Multiple export formats** - JSON, CSV, and summary formats for data analysis
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
