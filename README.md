# Little Alchemy 2 Text MCP

A text-based version of the game Little Alchemy 2 that can be played by humans via command line interface or by AI agents through **Model Context Protocol (MCP)**.

## Overview

This project builds upon [LittleAlchemy2Text](https://github.com/eleninisioti/LittleAlchemy2Text) by adding comprehensive **Model Context Protocol (MCP)** support for AI/LLM integration.

LittleAlchemy2Text itself extended [Wordcraft](https://github.com/minqi/wordcraft), a Python-based implementation of Little Alchemy 2.

**This MCP version adds:**

- **🤖 Model Context Protocol (MCP) support** - Full integration for AI/LLM clients using structured tools
- **🔧 Professional API design** - Clean, standardized interface following MCP specifications
- **📱 Multi-session management** - Handle multiple concurrent games with unique session IDs
- **📊 Enhanced feedback** - Rich game state reporting and real-time combination results
- **🎯 Multi-result combinations** - Fixed game engine to support combinations that produce multiple items simultaneously
- **🔒 Final items detection** - Automatic identification and notification of final items that cannot be combined further
- **📈 Comprehensive session analytics** - Track 12 key parameters per game session for research and analysis
- **🧠 Reasoning type tracking** - Categorize and analyze different reasoning approaches (logical, creative, systematic, etc.)

## Game Modes

### Open-Ended Mode

Start with the four basic elements (`air`, `earth`, `fire`, `water`) and discover as many items as possible by combining elements. Perfect for exploration and creativity.

### Targeted Mode

Find specific target items within a limited number of rounds. Includes distractors and depth settings for varying difficulty levels.

## Enhanced Game Engine

### Multi-Result Combinations

This version includes a **major improvement** to the original game engine that fixes a fundamental limitation. Some combinations in Little Alchemy 2 should produce multiple items simultaneously, but the original engine could only create one item per combination.

**Fixed Examples:**

- `pressure + lava` → **both** `granite` and `eruption` ✅
- Previously would only create one of these items ❌

**Technical Details:**

- Modified recipe book to support multiple entities per recipe
- Updated environment step function to handle multiple new items
- Enhanced MCP server to detect and report all created items

### Final Items Support

The game now recognizes **final items** - items that cannot be combined with other elements to create new items. When you discover a final item, you'll receive a notification:

🔒 _'granite' is a final item and cannot be combined with other items._

This helps players understand which items they can continue experimenting with and which represent endpoints in the combination tree. There are **170 final items** out of 700 total items in the game.

## Installation

### Prerequisites

- **Python 3.8+** (tested with Python 3.11)
- **Operating System**: Linux or macOS

### Option 1: Conda Environment (Recommended)

```bash
conda env create -f environment.yml
conda activate little_alchemy_2_text
```

### Option 2: Pip Installation

```bash
pip install -r requirements.txt
```

For MCP functionality, also install:

```bash
pip install mcp
```

## How to Play

### 🖥️ Command Line Interface

Play with human players through an interactive terminal interface:

```bash
python play.py
```

You'll be prompted to specify:

- Number of human players
- Game mode (targeted or open-ended)
- Number of rounds
- Other game settings

### 🤖 MCP (Model Context Protocol) Interface

**Full AI/LLM integration** - Any MCP-compatible client can play the game using natural language!

#### Start the MCP Server

```bash
python mcp_server.py
```

#### Available MCP Tools

- **`start_game`** - Create new game sessions with custom settings and reasoning type tracking
- **`get_game_state`** - View inventory, combinations, and progress
- **`make_move`** - Combine two items to discover new ones (with reasoning explanation logging)
- **`get_attempt_logs`** - Retrieve detailed logs of all combination attempts with comprehensive analysis parameters
- **`get_session_logs`** - Access session-level analytics including discovery rates, streaks, and performance metrics
- **`list_active_sessions`** - Manage multiple concurrent games
- **`end_game`** - Complete sessions with detailed summaries and finalized analytics

#### Example MCP Gameplay

```text
🎮 "Start a new Little Alchemy game"
→ Creates session with air, earth, fire, water

🔬 "Combine air and fire"
→ ✅ SUCCESS! air + fire = energy

🎯 "What's in my inventory?"
→ Current items: air, earth, fire, water, energy
```

#### MCP Client Configuration

For Claude Desktop, add to your configuration:

```json
{
  "mcpServers": {
    "little-alchemy-2-text": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/LittleAlchemy2Text_MCP"
    }
  }
}
```

## Project Structure

```text
LittleAlchemy2Text_MCP/
├── env/                    # Game environments
│   ├── little_alchemy_2_text/  # Core game logic
│   └── wordcraft/          # Original Wordcraft base
├── players/                # Player implementations
│   └── human.py           # Human player interface
├── mcp_server.py          # MCP server implementation
├── play.py                # Command line game interface
├── mcp_demo_simple.py     # MCP integration demo
├── requirements.txt       # Python dependencies
├── environment.yml        # Conda environment
├── pyproject.toml         # Package configuration
├── README_MCP.md          # Detailed MCP setup guide
└── MCP_INTEGRATION_SUMMARY.md  # Integration overview
```

## Key Features

### ✅ Complete MCP Integration

- **Multiple concurrent sessions** with unique IDs
- **Real-time game state** tracking and updates
- **Comprehensive error handling** with clear feedback
- **Built-in help resources** (rules, common combinations)
- **Session management** (start, pause, resume, end)
- **Advanced session analytics** with 12 tracked parameters per game session
- **Reasoning type categorization** for analyzing different cognitive approaches
- **Multi-format data export** (JSON, CSV, summary) for research and analysis

### 🎮 Enhanced Gameplay

- **Multi-result combinations** - Combinations now correctly produce all intended items (e.g., pressure + lava → granite + eruption)
- **Final items detection** - Automatic identification of items that cannot be combined further
- **Rich combination feedback** - Success/failure with explanations and multi-item notifications
- **Progress tracking** - Rounds used, items discovered, combinations tried
- **Multi-player coordination** - Share discoveries across players
- **Flexible game settings** - Customizable rounds, difficulty, encoding

### 🛠️ Developer Features

- **Comprehensive testing** with `test_mcp_demo.py`
- **Demo scripts** for quick testing and validation
- **Clean API design** following MCP specifications
- **Extensive documentation** and examples
- **Advanced analytics** - Export session data in JSON, CSV, or summary formats for research
- **Research-ready logging** - Track reasoning types, discovery patterns, streak analysis, and plateau detection

## Session Analytics & Research Features

### Comprehensive Session Logging

Every game session now tracks **12 key parameters** for detailed analysis and research:

| Parameter                  | Description                                                   | Use Cases                       |
| -------------------------- | ------------------------------------------------------------- | ------------------------------- |
| **Session_ID**             | Unique identifier for each game session                       | Multi-session comparison        |
| **Reasoning_Type**         | Cognitive approach used (logical, creative, systematic, etc.) | Strategy effectiveness analysis |
| **Start_Time / End_Time**  | Session duration tracking                                     | Time-based performance studies  |
| **Total_Attempts**         | All combination attempts made                                 | Activity level measurement      |
| **Successful_Attempts**    | Successful combinations only                                  | Success rate calculation        |
| **Elements_Discovered**    | Total unique items found                                      | Discovery effectiveness         |
| **Final_Inventory_Size**   | Items in inventory at session end                             | End-state analysis              |
| **Discovery_Rate**         | Success percentage (successful/total)                         | Performance metrics             |
| **Longest_Success_Streak** | Maximum consecutive successes                                 | Peak performance analysis       |
| **Longest_Failure_Streak** | Maximum consecutive failures                                  | Difficulty assessment           |
| **Plateau_Count**          | Periods without discovery                                     | Learning curve analysis         |

### Reasoning Type Analysis

Track and compare different cognitive approaches:

- **Logical** - Systematic, science-based reasoning
- **Creative** - Imaginative, associative thinking
- **Systematic** - Methodical, organized exploration
- **Random** - Experimental, trial-and-error approach
- **Heuristic** - Pattern-based, experience-driven decisions

### Data Export Options

Export session data in multiple formats for research and analysis:

```bash
# Human-readable summary
get_session_logs(format="summary")

# Machine-readable JSON for programming analysis
get_session_logs(format="json")

# Spreadsheet-compatible CSV for statistical analysis
get_session_logs(format="csv")
```

### Research Applications

- **Educational Psychology** - Study learning patterns and strategy effectiveness
- **AI Behavior Analysis** - Compare reasoning approaches in artificial agents
- **Cognitive Science** - Analyze problem-solving strategies and discovery patterns
- **Game Design** - Optimize difficulty curves and player engagement
- **Human-Computer Interaction** - Evaluate interface effectiveness and user experience

## Quick Start

1. **Install dependencies:**

   ```bash
   conda env create -f environment.yml && conda activate little_alchemy_2_text
   ```

2. **Try the command line version:**

   ```bash
   python play.py
   ```

3. **Experience MCP integration:**

   ```bash
   python mcp_demo_simple.py
   ```

4. **Set up with an MCP client:**
   See `README_MCP.md` for detailed setup instructions

## Documentation

- **`README_MCP.md`** - Complete MCP setup and usage guide
- **`MCP_INTEGRATION_SUMMARY.md`** - Overview of MCP features and implementation
- Built-in help via MCP resources: `game://rules` and `game://combinations`

## Troubleshooting

1. **Dependencies**: Ensure all packages are installed correctly
2. **MCP Server**: Check that the server starts without errors
3. **Client Configuration**: Verify your MCP client settings
4. **Game Paths**: Confirm environment paths are correctly set

## Acknowledgments

This project builds upon:

- **[LittleAlchemy2Text](https://github.com/eleninisioti/LittleAlchemy2Text)** - The original text-based Little Alchemy 2 implementation with LLM support

```bibtex
@article{nisioti_2024,
title={Collective Innovation in Groups of Large Language Models},
author={Eleni Nisioti and Sebastian Risi and Ida Momennejad and Pierre-Yves Oudeyer and Clément Moulin-Frier},
year={2024},
booktitle = {The 2023 {Conference} on {Artificial} {Life}},
publisher = {MIT Press},
}
```

- **[Wordcraft](https://github.com/minqi/wordcraft)** - The foundational Python implementation of Little Alchemy 2

---
