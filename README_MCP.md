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

- **`start_game`** - Start a new game session with reasoning type tracking
- **`get_game_state`** - View current inventory and game status
- **`make_move`** - Combine two items to create new ones (with comprehensive logging)
- **`list_active_sessions`** - See all active game sessions
- **`end_game`** - End a game session and get final summary with session analytics

### Data Analysis & Logging

- **`get_attempt_logs`** - Retrieve detailed logs of all attempts with comprehensive parameters for analysis
- **`get_session_logs`** - Access session-level analytics with 12 key performance metrics
- **`debug_logging_status`** - Debug tool to check logging system status across all sessions

### Resources

- **Game Rules** (`game://rules`) - How to play instructions
- **Combinations Guide** (`game://combinations`) - Common item combinations

## How to Play via MCP

1. **Start a game** (now with reasoning type tracking):

   ```json
   {
     "tool": "start_game",
     "arguments": {
       "session_id": "123456",
       "game_mode": "open-ended",
       "max_rounds": 15,
       "reasoning_type": "logical"
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
       "session_id": "123456",
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
       "session_id": "123456",
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

⚠️ **Note**: All parameter keys are shortened to minimize character usage in logs due to size constraints.

Each attempt captures the following 12 parameters:

| Parameter | Description                            | Example                                |
| --------- | -------------------------------------- | -------------------------------------- |
| `sid`     | Unique 6-digit game session identifier | `"123456"`                             |
| `att_n`   | Sequential attempt number (1, 2, 3...) | `5`                                    |
| `e1`      | First element in combination           | `"fire"`                               |
| `e2`      | Second element in combination          | `"water"`                              |
| `ok`      | Whether the combination succeeded      | `true`                                 |
| `res`     | Created element(s) if successful       | `"steam"` or `"granite, eruption"`     |
| `inv_b4`  | Number of items before this attempt    | `8`                                    |
| `reason`  | Player's reasoning for the attempt     | `"Fire and water should create steam"` |
| `novel`   | First time trying this combination     | `true`                                 |
| `str_typ` | Current streak type                    | `"success"` or `"failure"`             |
| `str_len` | Length of current streak               | `3`                                    |
| `t_since` | Seconds since last successful attempt  | `45.2` or `null`                       |

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

## Session-Level Analytics

### Overview

Beyond individual attempt logging, the system now tracks comprehensive **session-level metrics** that provide insights into overall game performance, learning patterns, and reasoning effectiveness.

### Session Parameters Tracked

Every game session automatically logs **12 key parameters**:

| Parameter     | Description                              | Research Value                          |
| ------------- | ---------------------------------------- | --------------------------------------- |
| **sid**       | Unique identifier for each session       | Multi-session comparison and tracking   |
| **r_typ**     | Cognitive approach categorization        | Strategy effectiveness analysis         |
| **start/end** | Session duration and timing              | Time-based performance correlation      |
| **tot_att**   | All combination attempts made            | Activity and engagement measurement     |
| **succ_att**  | Number of successful combinations        | Success rate and learning effectiveness |
| **elem_disc** | Total unique items found                 | Discovery capability assessment         |
| **final_inv** | Items remaining at session end           | End-state achievement analysis          |
| **disc_rate** | Success percentage (successful/total)    | Overall performance metric              |
| **max_succ**  | Maximum consecutive successes            | Peak performance identification         |
| **max_fail**  | Maximum consecutive failures             | Challenge and difficulty assessment     |
| **plateaus**  | Periods of 5+ attempts without discovery | Learning curve and stagnation analysis  |

### Accessing Session Logs

#### 1. View Session Summary

```json
{
  "tool": "get_session_logs",
  "arguments": {
    "session_id": "my-game-1",
    "format": "summary"
  }
}
```

**Response:**

```text
📊 SESSION LOGS - Session: my-game-1
==================================================

🎮 Session: my-game-1
   Reasoning Type: logical
   Duration: 2024-01-15T14:25:30 → 2024-01-15T14:45:22
   Attempts: 12/20 (60.0% success rate)
   Elements: 15 discovered, 13 final inventory
   Streaks: 4 success, 3 failure
   Plateaus: 2

Total Sessions: 1

💡 Use format='json' or format='csv' for machine-readable data.
```

#### 2. Export All Sessions (CSV for Analysis)

```json
{
  "tool": "get_session_logs",
  "arguments": {
    "format": "csv"
  }
}
```

**Response:**

```csv
Session_ID,Reasoning_Type,Start_Time,End_Time,Total_Attempts,Successful_Attempts,Elements_Discovered,Final_Inventory_Size,Discovery_Rate,Longest_Success_Streak,Longest_Failure_Streak,Plateau_Count
"123456","logical","2024-01-15T14:25:30","2024-01-15T14:45:22","20","12","15","13","60.0%","4","3","2"
"654321","creative","2024-01-15T15:10:15","2024-01-15T15:35:45","18","8","12","10","44.4%","3","5","3"
```

#### 3. Export Structured Data (JSON)

```json
{
  "tool": "get_session_logs",
  "arguments": {
    "session_id": "my-game-1",
    "format": "json"
  }
}
```

### Reasoning Type Categories

The system supports multiple reasoning type classifications for comparative analysis:

- **`logical`** - Science-based, cause-and-effect reasoning
- **`creative`** - Imaginative, associative thinking
- **`systematic`** - Methodical, organized exploration
- **`random`** - Experimental, trial-and-error approach
- **`heuristic`** - Pattern-based, experience-driven decisions
- **`collaborative`** - Group-based or discussion-informed choices
- **`intuitive`** - Gut-feeling or instinct-based attempts

### Research Applications

#### Educational Research

- Compare learning effectiveness across different reasoning approaches
- Analyze correlation between reasoning type and success rates
- Study plateau patterns and breakthrough moments

#### AI Behavior Analysis

- Evaluate different AI reasoning strategies
- Compare human vs. AI learning patterns
- Assess reasoning consistency across sessions

#### Cognitive Science

- Analyze problem-solving strategy evolution
- Study decision-making patterns under different conditions
- Evaluate cognitive load and performance correlation

#### Game Design Optimization

- Identify optimal difficulty progression
- Analyze player engagement patterns
- Optimize feedback and hint systems

### Multi-Session Analysis

Export data from multiple sessions to compare:

```json
{
  "tool": "get_session_logs",
  "arguments": {
    "format": "csv"
  }
}
```

This exports all session data for statistical analysis in tools like:

- **Excel/Google Sheets** - Basic statistical analysis and visualization
- **R/Python** - Advanced statistical modeling and machine learning
- **SPSS/SAS** - Professional statistical analysis
- **Tableau/Power BI** - Interactive data visualization and dashboards

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
6. **Specify reasoning types** when starting games to enable cognitive approach analysis
7. **Include reasoning explanations** with every attempt (required for logging and analysis)
8. Use `get_attempt_logs` to review individual attempt patterns and strategies
9. Use `get_session_logs` to analyze overall performance and learning effectiveness
10. Pay attention to successful combinations from other sessions
11. Experiment! There are hundreds of possible combinations

## Game Features via MCP

- ✅ Full game functionality through MCP tools
- ✅ Multiple concurrent game sessions
- ✅ Real-time inventory and combination tracking
- ✅ **Multi-result combinations** - Single combinations can now produce multiple items
- ✅ **Final items detection** - Automatic notification when discovering final items
- ✅ **Comprehensive attempt logging** - Every attempt logged with 12 parameters for analysis
- ✅ **Session-level analytics** - Track 12 key performance metrics per game session
- ✅ **Reasoning type tracking** - Categorize and analyze different cognitive approaches
- ✅ **Reasoning explanation capture** - Required reasoning input for each attempt
- ✅ **Advanced analytics** - Success rates, streaks, timing, and pattern analysis
- ✅ **Multiple export formats** - JSON, CSV, and summary formats for data analysis
- ✅ **Research-ready data** - Export session data for statistical analysis and visualization
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
