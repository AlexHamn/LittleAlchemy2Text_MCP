# Little Alchemy 2 Text MCP

A text-based version of the  game Little Alchemy 2 that can be played by humans via command line interface or by AI agents through **Model Context Protocol (MCP)**.

## Overview

This project builds upon [LittleAlchemy2Text](https://github.com/eleninisioti/LittleAlchemy2Text) by adding comprehensive **Model Context Protocol (MCP)** support for AI/LLM integration.

LittleAlchemy2Text itself extended [Wordcraft](https://github.com/minqi/wordcraft), a Python-based implementation of Little Alchemy 2.

**This MCP version adds:**

- **🤖 Model Context Protocol (MCP) support** - Full integration for AI/LLM clients using structured tools
- **🔧 Professional API design** - Clean, standardized interface following MCP specifications
- **📱 Multi-session management** - Handle multiple concurrent games with unique session IDs
- **📊 Enhanced feedback** - Rich game state reporting and real-time combination results

## Game Modes

### Open-Ended Mode

Start with the four basic elements (`air`, `earth`, `fire`, `water`) and discover as many items as possible by combining elements. Perfect for exploration and creativity.

### Targeted Mode

Find specific target items within a limited number of rounds. Includes distractors and depth settings for varying difficulty levels.

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

- **`start_game`** - Create new game sessions with custom settings
- **`get_game_state`** - View inventory, combinations, and progress
- **`make_move`** - Combine two items to discover new ones
- **`list_active_sessions`** - Manage multiple concurrent games
- **`end_game`** - Complete sessions with detailed summaries

#### Example MCP Gameplay

```
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

```
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

### 🎮 Enhanced Gameplay

- **Rich combination feedback** - Success/failure with explanations
- **Progress tracking** - Rounds used, items discovered, combinations tried
- **Multi-player coordination** - Share discoveries across players
- **Flexible game settings** - Customizable rounds, difficulty, encoding

### 🛠️ Developer Features

- **Comprehensive testing** with `test_mcp_demo.py`
- **Demo scripts** for quick testing and validation
- **Clean API design** following MCP specifications
- **Extensive documentation** and examples

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
