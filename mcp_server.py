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
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

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

# Global attempt logging storage
attempt_logs: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> list of attempt logs

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

def get_current_streak(session_id: str) -> Tuple[str, int]:
    """Get the current streak type and length for a session."""
    if session_id not in attempt_logs or not attempt_logs[session_id]:
        return "none", 0
    
    logs = attempt_logs[session_id]
    if not logs:
        return "none", 0
    
    # Check the most recent attempts to determine current streak
    current_streak_type = "success" if logs[-1]["Success"] else "failure"
    current_streak_length = 1
    
    # Count backwards to find the length of the current streak
    for i in range(len(logs) - 2, -1, -1):
        if (logs[i]["Success"] and current_streak_type == "success") or \
           (not logs[i]["Success"] and current_streak_type == "failure"):
            current_streak_length += 1
        else:
            break
    
    return current_streak_type, current_streak_length

def get_time_since_last_success(session_id: str, current_time: float) -> Optional[float]:
    """Get the time in seconds since the last successful attempt."""
    if session_id not in attempt_logs or not attempt_logs[session_id]:
        return None
    
    logs = attempt_logs[session_id]
    
    # Find the most recent successful attempt
    for log in reversed(logs):
        if log["Success"]:
            return current_time - log["_timestamp"]
    
    return None  # No previous success

def is_novel_combination(session_id: str, element1: str, element2: str) -> bool:
    """Check if this combination has been attempted before in this session."""
    if session_id not in attempt_logs or not attempt_logs[session_id]:
        return True
    
    logs = attempt_logs[session_id]
    
    # Check both orderings of the combination
    for log in logs:
        if ((log["Element_1"].lower() == element1.lower() and log["Element_2"].lower() == element2.lower()) or
            (log["Element_1"].lower() == element2.lower() and log["Element_2"].lower() == element1.lower())):
            return False
    
    return True

def log_attempt(session_id: str, attempt_number: int, element1: str, element2: str, 
                success: bool, result_element: Optional[str], inventory_size_before: int,
                reasoning_explanation: str, is_novel: bool, streak_type: str, 
                streak_length: int, time_since_last_success: Optional[float]) -> None:
    """Log an attempt with all required parameters."""
    if session_id not in attempt_logs:
        attempt_logs[session_id] = []
    
    log_entry = {
        "Session_ID": session_id,
        "Attempt_Number": attempt_number,
        "Element_1": element1,
        "Element_2": element2,
        "Success": success,
        "Result_Element": result_element,
        "Inventory_Size_Before": inventory_size_before,
        "Reasoning_Explanation": reasoning_explanation,
        "Is_Novel_Combination": is_novel,
        "Current_Streak_Type": streak_type,
        "Current_Streak_Length": streak_length,
        "Time_Since_Last_Success": time_since_last_success,
        "_timestamp": time.time(),  # Internal timestamp for calculations
        "_datetime": datetime.now().isoformat()  # Human-readable timestamp
    }
    
    attempt_logs[session_id].append(log_entry)

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
                    },
                    "reasoning_explanation": {
                        "type": "string",
                        "description": "Optional explanation of the reasoning behind this combination attempt",
                        "default": ""
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
        ),
        
        Tool(
            name="get_attempt_logs",
            description="Retrieve detailed logs of all attempts for a game session, including all required parameters for analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Game session identifier"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "csv", "summary"],
                        "description": "Output format: 'json' for structured data, 'csv' for tabular format, 'summary' for human-readable summary",
                        "default": "summary"
                    }
                },
                "required": ["session_id"]
            }
        ),
        
        Tool(
            name="debug_logging_status",
            description="Debug tool to check the current status of the logging system across all sessions.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
        reasoning_explanation = arguments.get("reasoning_explanation", "").strip()
        
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
            
            # Capture state for logging
            current_time = time.time()
            inventory = [item.lower() for item in unwrapped_env.get_inventory()]
            pre_action_inventory = unwrapped_env.get_inventory().copy()  # Capture inventory before action
            inventory_size_before = len(pre_action_inventory)
            attempt_number = len(attempt_logs.get(session_id, [])) + 1
            
            # Get streak information (before this attempt)
            streak_type, streak_length = get_current_streak(session_id)
            
            # Get time since last success
            time_since_last_success = get_time_since_last_success(session_id, current_time)
            
            # Check if this is a novel combination
            is_novel = is_novel_combination(session_id, item1, item2)
            
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
                    
                    # Get ALL new items by comparing inventories before and after
                    post_action_inventory = unwrapped_env.get_inventory()
                    new_items = [item for item in post_action_inventory if item not in pre_action_inventory]
                    
            except (ValueError, IndexError):
                # If there's an issue with finding indices, proceed with normal step
                action = f"Combination: '{item1}' and '{item2}'"
                
                obs, reward, done, info = env.step(action)
                
                # Get ALL new items by comparing inventories (fallback case)
                post_action_inventory = unwrapped_env.get_inventory()
                new_items = [item for item in post_action_inventory if item not in pre_action_inventory]
            
            # Update session state
            session['rounds_played'] += 1
            if done or session['rounds_played'] >= session['max_rounds']:
                session['done'] = True

            # Determine success and result for logging
            success = False
            result_element = None
            
            if info.get("repeat", False):
                # For repeated combinations, check if it was a successful repeat
                repeated_result = info.get("repeated_result")
                if repeated_result:
                    success = True
                    result_element = repeated_result
                else:
                    success = False
                    result_element = None
            else:
                # For new combinations
                if reward and reward > 0 and new_items:
                    success = True
                    result_element = new_items[0] if len(new_items) == 1 else ", ".join(new_items)
                else:
                    success = False
                    result_element = None
            
            # Log the attempt with all required parameters
            log_attempt(
                session_id=session_id,
                attempt_number=attempt_number,
                element1=item1,
                element2=item2,
                success=success,
                result_element=result_element,
                inventory_size_before=inventory_size_before,
                reasoning_explanation=reasoning_explanation,
                is_novel=is_novel,
                streak_type=streak_type,
                streak_length=streak_length,
                time_since_last_success=time_since_last_success
            )
            
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
                    if new_items:
                        if len(new_items) == 1:
                            response = f"✅ SUCCESS! '{item1}' + '{item2}' = '{new_items[0]}'"
                            response += f"\n🎉 '{new_items[0]}' has been added to your inventory!"
                            
                            # Check if the new item is final and inform the user
                            final_message = get_final_item_message(new_items[0])
                            if final_message:
                                response += f"\n{final_message}"
                        else:
                            # Multiple items created
                            items_list = "', '".join(new_items)
                            response = f"✅ SUCCESS! '{item1}' + '{item2}' = '{items_list}'"
                            response += f"\n🎉 {len(new_items)} items have been added to your inventory: '{items_list}'"
                            
                            # Check if any new items are final
                            for item in new_items:
                                final_message = get_final_item_message(item)
                                if final_message:
                                    response += f"\n{final_message}"
                    else:
                        response = f"✅ SUCCESS! '{item1}' + '{item2}' created a new item, but couldn't identify which one."
                else:
                    response = f"❌ No result: '{item1}' and '{item2}' don't combine into anything."
            
            # Add current state and logging confirmation
            response += f"\n\nRounds used: {session['rounds_played']}/{session['max_rounds']}"
            response += f"\nItems discovered: {len(unwrapped_env.get_inventory())}"
            response += f"\n📝 Logged attempt #{attempt_number} (Use 'get_attempt_logs' to view all logs)"
            
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
            
            # Remove session and its logs
            del game_sessions[session_id]
            if session_id in attempt_logs:
                del attempt_logs[session_id]
            
            return [TextContent(
                type="text",
                text=final_summary
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error ending game: {str(e)}"
            )]
    
    elif name == "get_attempt_logs":
        session_id = arguments["session_id"]
        format_type = arguments.get("format", "summary")
        
        if session_id not in attempt_logs or not attempt_logs[session_id]:
            return [TextContent(
                type="text",
                text=f"📋 No attempt logs found for session '{session_id}'. Make sure you've made some moves first using 'make_move'."
            )]
        
        try:
            logs = attempt_logs[session_id]
            
            if format_type == "json":
                # Return as JSON string
                import json
                json_output = json.dumps(logs, indent=2)
                return [TextContent(
                    type="text",
                    text=f"📊 ATTEMPT LOGS (JSON) - Session: {session_id}\n\n```json\n{json_output}\n```"
                )]
            
            elif format_type == "csv":
                # Return as CSV format
                if not logs:
                    return [TextContent(type="text", text="No logs available")]
                
                # Create CSV header
                headers = ["Session_ID", "Attempt_Number", "Element_1", "Element_2", "Success", 
                          "Result_Element", "Inventory_Size_Before", "Reasoning_Explanation", 
                          "Is_Novel_Combination", "Current_Streak_Type", "Current_Streak_Length", 
                          "Time_Since_Last_Success"]
                
                csv_lines = [",".join(headers)]
                
                for log in logs:
                    row = []
                    for header in headers:
                        value = log.get(header, "")
                        # Handle None values and escape commas
                        if value is None:
                            value = ""
                        value_str = str(value).replace(",", ";").replace("\n", " ")
                        row.append(f'"{value_str}"')
                    csv_lines.append(",".join(row))
                
                csv_output = "\n".join(csv_lines)
                return [TextContent(
                    type="text",
                    text=f"📊 ATTEMPT LOGS (CSV) - Session: {session_id}\n\n```csv\n{csv_output}\n```"
                )]
            
            else:  # summary format
                summary = f"📊 ATTEMPT LOGS SUMMARY - Session: {session_id}\n"
                summary += f"Total Attempts: {len(logs)}\n\n"
                
                successful_attempts = [log for log in logs if log["Success"]]
                failed_attempts = [log for log in logs if not log["Success"]]
                
                summary += f"✅ Successful Attempts: {len(successful_attempts)}\n"
                summary += f"❌ Failed Attempts: {len(failed_attempts)}\n"
                summary += f"📈 Success Rate: {len(successful_attempts)/len(logs)*100:.1f}%\n\n"
                
                # Show recent attempts
                summary += "🕐 RECENT ATTEMPTS:\n"
                for log in logs[-5:]:  # Show last 5 attempts
                    status = "✅" if log["Success"] else "❌"
                    result = f" -> {log['Result_Element']}" if log["Result_Element"] else ""
                    reasoning = f" | Reasoning: {log['Reasoning_Explanation']}" if log['Reasoning_Explanation'] else ""
                    summary += f"{status} #{log['Attempt_Number']}: {log['Element_1']} + {log['Element_2']}{result}{reasoning}\n"
                
                if len(logs) > 5:
                    summary += f"\n... and {len(logs) - 5} more attempts. Use format='json' or format='csv' for complete data.\n"
                
                return [TextContent(
                    type="text",
                    text=summary
                )]
                
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error retrieving attempt logs: {str(e)}"
            )]
    
    elif name == "debug_logging_status":
        try:
            debug_info = "🔍 LOGGING SYSTEM DEBUG STATUS\n\n"
            
            # Check global attempt_logs state
            debug_info += f"Total sessions with logs: {len(attempt_logs)}\n"
            
            if not attempt_logs:
                debug_info += "❌ No logs found in any session.\n"
                debug_info += "This could mean:\n"
                debug_info += "- No games have been started yet\n"
                debug_info += "- No moves have been made\n"
                debug_info += "- There's an issue with the logging implementation\n\n"
            else:
                debug_info += "\n📊 LOG SUMMARY BY SESSION:\n"
                for session_id, logs in attempt_logs.items():
                    debug_info += f"  • Session '{session_id}': {len(logs)} attempts\n"
                    if logs:
                        latest_log = logs[-1]
                        debug_info += f"    Last attempt: {latest_log['Element_1']} + {latest_log['Element_2']} "
                        debug_info += f"= {'✅' if latest_log['Success'] else '❌'}\n"
                        debug_info += f"    Last logged: {latest_log['_datetime']}\n"
            
            # Check active game sessions
            debug_info += f"\nActive game sessions: {len(game_sessions)}\n"
            for session_id in game_sessions.keys():
                debug_info += f"  • Session '{session_id}'\n"
            
            debug_info += "\n💡 TO ACCESS LOGS:\n"
            debug_info += "Use 'get_attempt_logs' with your session_id to view detailed logs.\n"
            debug_info += "Example: get_attempt_logs(session_id='your_session_name', format='summary')\n"
            
            return [TextContent(
                type="text",
                text=debug_info
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"❌ Error in debug tool: {str(e)}"
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
        print("• make_move - Combine two items (now with reasoning_explanation logging)")
        print("• get_attempt_logs - Retrieve detailed logs of all attempts")
        print("• debug_logging_status - Check logging system status (debug tool)")
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