#!/usr/bin/env python3
"""
Little Alchemy 2 Text MCP Server

This MCP server exposes the Little Alchemy 2 text game as tools that can be called
by LLM clients. Players can start games, view their inventory, combine items, and 
see the results of their combinations.

The game works like Little Alchemy 2:
- Start with basic elements (air, earth, fire, water)
- Combine two items to create new items
- Discover as many combinations as possible
- See valid and invalid combinations from previous attempts
"""

import asyncio
import sys
import os
import json
import signal
import argparse
from typing import Dict, Any, List, Optional

# Add paths for the game modules
sys.path.append(os.getcwd())
sys.path.append("env/wordcraft")

# Import MCP server modules
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent
import mcp.server.stdio

# Import game modules
import gymnasium as gym
import env.little_alchemy_2_text.openended.env
import env.little_alchemy_2_text.targeted.env
from box import Box
import numpy as np

# Global game state storage
game_sessions: Dict[str, Dict[str, Any]] = {}

# Load final items data
def load_final_items() -> set:
    """Load the list of final items that cannot be combined further."""
    try:
        # Use absolute path based on script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        final_items_path = os.path.join(script_dir, 'final_items.json')
        with open(final_items_path, 'r') as f:
            data = json.load(f)
            final_items_set = set(data['final_items'])
            return final_items_set
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        # Fallback to empty set if file doesn't exist or is invalid
        print(f"⚠️ Warning: Could not load final items data: {e}", file=sys.stderr)
        return set()

# Initialize final items set
final_items = load_final_items()

def is_final_item(item_name: str) -> bool:
    """Check if an item is final (cannot be combined further)."""
    global final_items
    
    # If final_items is empty, try reloading it
    if not final_items:
        final_items = load_final_items()
    
    return item_name.lower() in final_items

def get_final_item_message(item_name: str) -> str:
    """Get a message indicating if an item is final."""
    if is_final_item(item_name):
        return f"🔒 '{item_name}' is a final item and cannot be combined with other items."
    return ""

def create_game_session(session_id: str, targeted: bool = False, max_rounds: int = 10) -> Dict[str, Any]:
    """Create a new game session with the specified parameters."""
    
    # Set up game arguments
    args = {
        'targeted': targeted,
        'distractors': 3,
        'depth': 1,
        'rounds': max_rounds,
        'seed': np.random.randint(0, 10000),
        'encoded': False
    }
    args = Box(args)
    
    # Create environment
    if targeted:
        env = gym.make("LittleAlchemy2TextTargeted-v0",
                        max_mix_steps=args.rounds,
                        num_distractors=args.distractors,
                        max_depth=args.depth,
                        encoded=args.encoded)
    else:
        env = gym.make("LittleAlchemy2TextOpen-v0",
                        max_mix_steps=args.rounds,
                        encoded=args.encoded)
    
    # Reset environment
    env.reset(seed=args.seed)
    
    # Create session data
    session = {
        'env': env,
        'unwrapped_env': env.unwrapped,  # Store unwrapped for custom methods
        'args': args,
        'rounds_played': 0,
        'max_rounds': max_rounds,
        'done': False,
        'targeted': targeted
    }
    
    return session

def get_game_state(session: Dict[str, Any]) -> str:
    """Get the current state of the game as a formatted string."""
    unwrapped_env = session['unwrapped_env']
    
    # Get basic game info
    inventory = unwrapped_env.get_inventory()
    rounds_left = session['max_rounds'] - session['rounds_played']
    
    # Get valid and invalid combinations
    valid_combs, past_invalid_combs = unwrapped_env._print_valid_and_invalid_combs()
    
    # Format the state
    state = f"""=== LITTLE ALCHEMY 2 TEXT ===
Game Mode: {'Targeted' if session['targeted'] else 'Open-ended'}
Rounds Remaining: {rounds_left}
Items Discovered: {len(inventory)}

CURRENT INVENTORY:
{', '.join([f"'{item}'" for item in inventory])}

VALID COMBINATIONS DISCOVERED:
{valid_combs if valid_combs else 'None yet'}

INVALID COMBINATIONS TRIED:
{past_invalid_combs if past_invalid_combs else 'None yet'}

To make a move, combine two items from your inventory using the make_move tool.
Example: make_move('air', 'fire') might create 'energy'
"""
    
    if session['done']:
        state += f"\n🎉 GAME COMPLETED!\nFinal Score: {len(inventory)} items discovered"
    
    return state

# Create MCP server instance
app = Server("little-alchemy-2-text")

@app.list_resources()
async def list_resources() -> List[Resource]:
    """List available game resources."""
    return [
        Resource(
            uri="game://rules",
            name="Little Alchemy 2 Rules",
            mimeType="text/plain",
        ),
        Resource(
            uri="game://combinations",
            name="Common Combinations Guide",
            mimeType="text/plain",
        )
    ]

@app.read_resource()
async def read_resource(uri: str) -> TextContent:
    """Read game resources."""
    if uri == "game://rules":
        return TextContent(
            type="text",
            text="""LITTLE ALCHEMY 2 TEXT - GAME RULES

🎯 OBJECTIVE:
- Open-ended mode: Discover as many items as possible by combining elements
- Targeted mode: Find the specific target item

🎮 HOW TO PLAY:
1. Start with basic elements: air, earth, fire, water
2. Combine any two items from your inventory to try creating new items
3. Successful combinations add new items to your inventory
4. Failed combinations are remembered to avoid repetition
5. You have limited rounds to discover items

💡 TIPS:
- Try logical combinations (fire + water = steam)
- Experiment with basic elements first
- Build on your discoveries (steam + air might make cloud)
- Pay attention to previous valid combinations for patterns

🔄 GAME FLOW:
1. Use start_game to begin
2. Use get_game_state to see your inventory and progress
3. Use make_move to combine two items
4. Repeat until rounds are exhausted or target found
"""
        )
    
    elif uri == "game://combinations":
        return TextContent(
            type="text",
            text="""COMMON LITTLE ALCHEMY 2 COMBINATIONS

🔥 BASIC ELEMENT COMBINATIONS:
- air + fire = energy
- earth + water = mud
- fire + water = steam
- air + water = rain
- earth + fire = lava

⚡ ENERGY-BASED:
- energy + air = wind
- energy + earth = earthquake
- energy + water = tsunami

🌍 NATURE COMBINATIONS:
- rain + earth = plant
- plant + fire = ash
- water + earth = mud
- mud + fire = brick

🏗️ BUILDING MATERIALS:
- earth + earth = land
- water + water = sea
- fire + fire = sun
- air + air = pressure

💨 WEATHER & ATMOSPHERE:
- steam + air = cloud
- cloud + cloud = rain
- wind + water = wave

Remember: These are just examples! The game has hundreds of possible combinations.
Experiment and discover new ones!
"""
        )
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available game tools."""
    return [
        Tool(
            name="start_game",
            description="Start a new Little Alchemy 2 game session. You can choose between open-ended mode (discover as many items as possible) or targeted mode (find a specific target item).",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Unique identifier for this game session"
                    },
                    "game_mode": {
                        "type": "string",
                        "enum": ["open-ended", "targeted"],
                        "description": "Game mode: 'open-ended' to discover items freely, 'targeted' to find a specific target",
                        "default": "open-ended"
                    },
                    "max_rounds": {
                        "type": "integer",
                        "description": "Maximum number of combination attempts allowed",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 200
                    }
                },
                "required": ["session_id"]
            }
        ),
        
        Tool(
            name="get_game_state",
            description="Get the current state of your Little Alchemy 2 game, including your inventory, discovered combinations, and remaining rounds.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Game session identifier"
                    }
                },
                "required": ["session_id"]
            }
        ),
        
        Tool(
            name="make_move",
            description="Combine two items from your inventory to try creating a new item. The items must be in your current inventory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Game session identifier"
                    },
                    "item1": {
                        "type": "string",
                        "description": "First item to combine (must be in inventory)"
                    },
                    "item2": {
                        "type": "string",
                        "description": "Second item to combine (must be in inventory)"
                    }
                },
                "required": ["session_id", "item1", "item2"]
            }
        ),
        
        Tool(
            name="list_active_sessions",
            description="List all active game sessions.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        
        Tool(
            name="end_game",
            description="End a game session and get the final summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Game session identifier to end"
                    }
                },
                "required": ["session_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls for the Little Alchemy 2 game."""
    
    if name == "start_game":
        session_id = arguments["session_id"]
        game_mode = arguments.get("game_mode", "open-ended")
        max_rounds = arguments.get("max_rounds", 10)
        
        # Check if session already exists
        if session_id in game_sessions:
            return [TextContent(
                type="text",
                text=f"❌ Game session '{session_id}' already exists. Please choose a different session_id or end the existing session first."
            )]
        
        try:
            # Create new game session
            targeted = (game_mode == "targeted")
            session = create_game_session(session_id, targeted, max_rounds)
            game_sessions[session_id] = session
            
            # Get initial state
            initial_state = get_game_state(session)
            
            return [TextContent(
                type="text",
                text=f"🎮 NEW GAME STARTED!\nSession ID: {session_id}\nMode: {game_mode.title()}\nMax Rounds: {max_rounds}\n\n{initial_state}"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error starting game: {str(e)}"
            )]
    
    elif name == "get_game_state":
        session_id = arguments["session_id"]
        
        if session_id not in game_sessions:
            return [TextContent(
                type="text",
                text=f"❌ Game session '{session_id}' not found. Use start_game to create a new session."
            )]
        
        try:
            session = game_sessions[session_id]
            state = get_game_state(session)
            
            return [TextContent(
                type="text",
                text=state
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error getting game state: {str(e)}"
            )]
    
    elif name == "make_move":
        session_id = arguments["session_id"]
        item1 = arguments["item1"].strip().lower()
        item2 = arguments["item2"].strip().lower()
        
        if session_id not in game_sessions:
            return [TextContent(
                type="text",
                text=f"❌ Game session '{session_id}' not found. Use start_game to create a new session."
            )]
        
        try:
            session = game_sessions[session_id]
            env = session['env']
            unwrapped_env = session['unwrapped_env']
            
            if session['done']:
                return [TextContent(
                    type="text",
                    text="🎮 This game session has already ended. Start a new game to continue playing."
                )]
            
            # Check if items are in inventory
            inventory = [item.lower() for item in unwrapped_env.get_inventory()]
            if item1 not in inventory:
                available_items = ', '.join([f"'{item}'" for item in unwrapped_env.get_inventory()])
                return [TextContent(
                    type="text",
                    text=f"❌ '{item1}' is not in your inventory. Available items: {available_items}"
                )]
            
            if item2 not in inventory:
                available_items = ', '.join([f"'{item}'" for item in unwrapped_env.get_inventory()])
                return [TextContent(
                    type="text",
                    text=f"❌ '{item2}' is not in your inventory. Available items: {available_items}"
                )]
            
            # Check if this combination was already attempted before calling env.step()
            try:
                item1_idx = unwrapped_env.table.index(item1)
                item2_idx = unwrapped_env.table.index(item2)
                
                # Check both possible orderings of the combination
                combination_tuple = (item1_idx, item2_idx)
                reverse_combination_tuple = (item2_idx, item1_idx)
                
                # Check if this was a previously successful combination
                is_repeated_successful = False
                repeated_result = None
                if combination_tuple in unwrapped_env.past_valid_combs:
                    result_idx = unwrapped_env.past_valid_combs[combination_tuple]
                    repeated_result = unwrapped_env.index_to_word(result_idx)
                    is_repeated_successful = True
                elif reverse_combination_tuple in unwrapped_env.past_valid_combs:
                    result_idx = unwrapped_env.past_valid_combs[reverse_combination_tuple]
                    repeated_result = unwrapped_env.index_to_word(result_idx)
                    is_repeated_successful = True
                
                # Check if this was a previously failed combination
                is_repeated_failed = (combination_tuple in unwrapped_env.past_invalid_combs or 
                                    reverse_combination_tuple in unwrapped_env.past_invalid_combs)
                
                if is_repeated_successful or is_repeated_failed:
                    # Handle repeated combination without calling env.step()
                    obs = unwrapped_env._get_observation()
                    reward = 0
                    done = unwrapped_env.done
                    info = {"repeat": True, "repeated_result": repeated_result if is_repeated_successful else None}
                else:
                    # Create action string (the game expects this format)
                    action = f"Combination: '{item1}' and '{item2}'"
                    
                    # Perform the action - note that the openended env returns (obs, reward, done, info)
                    # but the underlying _step returns (result, obs, reward, done, info)
                    # We need to access the unwrapped env to get the result
                    unwrapped_env = session['unwrapped_env']
                    
                    # Perform the action
                    obs, reward, done, info = env.step(action)
                    
                    # Get the new item from subgoal_history (more reliable than inventory comparison)
                    new_item = None
                    if reward and reward > 0 and hasattr(unwrapped_env, 'subgoal_history'):
                        # Try multiple approaches to find the new item
                        combination_key1 = f"'{item1}' and '{item2}'"
                        combination_key2 = f"'{item2}' and '{item1}'"  # Try reverse order
                        
                        if combination_key1 in unwrapped_env.subgoal_history:
                            new_item = unwrapped_env.subgoal_history[combination_key1]
                        elif combination_key2 in unwrapped_env.subgoal_history:
                            new_item = unwrapped_env.subgoal_history[combination_key2]
                        else:
                            # Get the most recent addition to subgoal_history
                            if unwrapped_env.subgoal_history and isinstance(unwrapped_env.subgoal_history, dict):
                                new_item = list(unwrapped_env.subgoal_history.values())[-1]
                    
            except (ValueError, IndexError):
                # If there's an issue with finding indices, proceed with normal step
                action = f"Combination: '{item1}' and '{item2}'"
                
                obs, reward, done, info = env.step(action)
                
                # Get the new item from subgoal_history (fallback case)
                new_item = None
                if reward and reward > 0 and hasattr(unwrapped_env, 'subgoal_history'):
                    combination_key1 = f"'{item1}' and '{item2}'"
                    combination_key2 = f"'{item2}' and '{item1}'"
                    
                    if combination_key1 in unwrapped_env.subgoal_history:
                        new_item = unwrapped_env.subgoal_history[combination_key1]
                    elif combination_key2 in unwrapped_env.subgoal_history:
                        new_item = unwrapped_env.subgoal_history[combination_key2]
                    elif unwrapped_env.subgoal_history and isinstance(unwrapped_env.subgoal_history, dict):
                        new_item = list(unwrapped_env.subgoal_history.values())[-1]
            
            # Update session state
            session['rounds_played'] += 1
            if done or session['rounds_played'] >= session['max_rounds']:
                session['done'] = True
            

            
            # Create response message
            if info.get("repeat", False):
                # Check if we have a repeated result from our custom detection
                repeated_result = info.get("repeated_result")
                if repeated_result:
                    response = f"🔄 You've already used this combination! '{item1}' + '{item2}' = '{repeated_result}' (already in your inventory)"
                    
                    # Check if the repeated result is final and inform the user
                    final_message = get_final_item_message(repeated_result)
                    if final_message:
                        response += f"\n{final_message}"
                else:
                    response = f"🔄 You've already tried this combination. '{item1}' and '{item2}' don't combine into anything."
            else:
                if reward and reward > 0:
                    if new_item:
                        response = f"✅ SUCCESS! '{item1}' + '{item2}' = '{new_item}'"
                        response += f"\n🎉 '{new_item}' has been added to your inventory!"
                        
                        # Check if the new item is final and inform the user
                        final_message = get_final_item_message(new_item)
                        if final_message:
                            response += f"\n{final_message}"
                    else:
                        response = f"✅ SUCCESS! '{item1}' + '{item2}' created a new item, but couldn't identify which one."
                else:
                    response = f"❌ No result: '{item1}' and '{item2}' don't combine into anything."
            
            # Add current state
            response += f"\n\nRounds used: {session['rounds_played']}/{session['max_rounds']}"
            response += f"\nItems discovered: {len(unwrapped_env.get_inventory())}"
            
            if session['done']:
                response += f"\n\n🎮 GAME COMPLETED!"
                response += unwrapped_env.summarise()
            
            return [TextContent(
                type="text",
                text=response
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error making move: {str(e)}"
            )]
    
    elif name == "list_active_sessions":
        if not game_sessions:
            return [TextContent(
                type="text",
                text="📋 No active game sessions. Use start_game to create a new session."
            )]
        
        session_list = "📋 ACTIVE GAME SESSIONS:\n\n"
        for session_id, session in game_sessions.items():
            mode = "Targeted" if session['targeted'] else "Open-ended"
            status = "Completed" if session['done'] else "Active"
            rounds = f"{session['rounds_played']}/{session['max_rounds']}"
            items = len(session['unwrapped_env'].get_inventory())
            
            session_list += f"🎮 Session: {session_id}\n"
            session_list += f"   Mode: {mode} | Status: {status} | Rounds: {rounds} | Items: {items}\n\n"
        
        return [TextContent(
            type="text",
            text=session_list
        )]
    
    elif name == "end_game":
        session_id = arguments["session_id"]
        
        if session_id not in game_sessions:
            return [TextContent(
                type="text",
                text=f"❌ Game session '{session_id}' not found."
            )]
        
        try:
            session = game_sessions[session_id]
            unwrapped_env = session['unwrapped_env']
            
            # Generate final summary
            final_summary = f"🎮 GAME SESSION '{session_id}' ENDED\n\n"
            final_summary += f"Mode: {'Targeted' if session['targeted'] else 'Open-ended'}\n"
            final_summary += f"Rounds Used: {session['rounds_played']}/{session['max_rounds']}\n"
            final_summary += f"Final Score: {len(unwrapped_env.get_inventory())} items discovered\n\n"
            
            inventory_list = ', '.join([f"'{item}'" for item in unwrapped_env.get_inventory()])
            final_summary += f"FINAL INVENTORY:\n{inventory_list}\n\n"
            
            valid_combs, invalid_combs = unwrapped_env._print_valid_and_invalid_combs()
            if valid_combs:
                final_summary += f"SUCCESSFUL COMBINATIONS:\n{valid_combs}\n\n"
            
            final_summary += "Thanks for playing Little Alchemy 2 Text! 🎉"
            
            # Remove session
            del game_sessions[session_id]
            
            return [TextContent(
                type="text",
                text=final_summary
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error ending game: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"❌ Unknown tool: {name}"
        )]

async def main():
    """Run the MCP server."""
    
    # Set up signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        print("\n🛑 Received shutdown signal, closing server...", file=sys.stderr)
        shutdown_event.set()
    
    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        if hasattr(signal, sig.name):
            signal.signal(sig, lambda s, f: signal_handler())
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            print("🎮 Little Alchemy 2 Text MCP Server started - VERSION WITH IMPROVED FEEDBACK", file=sys.stderr)
            print("💡 Press Ctrl+C to stop the server", file=sys.stderr)
            
            # Create a task for the server
            server_task = asyncio.create_task(
                app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options()
                )
            )
            
            # Wait for either the server to complete or shutdown signal
            done, pending = await asyncio.wait(
                [server_task, asyncio.create_task(shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted by user", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Server error: {e}", file=sys.stderr)
        raise
    finally:
        print("✅ Server stopped cleanly", file=sys.stderr)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Little Alchemy 2 Text MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This MCP server exposes the Little Alchemy 2 text game as tools that can be called
by LLM clients. Players can start games, view their inventory, combine items, and 
see the results of their combinations.

The server communicates over stdio and is designed to be used with MCP-compatible
clients like Claude Desktop or other AI assistants.

Example usage in Claude Desktop mcp_servers config:
{
  "little-alchemy-2-text": {
    "command": "python",
    "args": ["/path/to/mcp_server.py"]
  }
}
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Little Alchemy 2 Text MCP Server v1.0"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show server information and available tools"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.info:
        print("🎮 Little Alchemy 2 Text MCP Server")
        print("=" * 50)
        print("This server provides the following tools:")
        print("• start_game - Start a new game session")
        print("• get_game_state - View current game state")
        print("• make_move - Combine two items")
        print("• list_active_sessions - List all game sessions")
        print("• end_game - End a game session")
        print()
        print("Game modes:")
        print("• Open-ended: Discover as many items as possible")
        print("• Targeted: Find a specific target item")
        print()
        print("Use with MCP-compatible clients like Claude Desktop.")
        sys.exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!", file=sys.stderr)
        sys.exit(0)