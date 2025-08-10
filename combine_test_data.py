#!/usr/bin/env python3
"""
Script to combine all test data from different reasoning types into a single file.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

def load_json_files(directory: Path) -> List[Dict[Any, Any]]:
    """Load all JSON files from a directory and combine their contents."""
    all_data = []
    
    if not directory.exists():
        print(f"Warning: Directory {directory} does not exist")
        return all_data
    
    # Look for numbered JSON files (0.json, 1.json, etc.)
    json_files = sorted([f for f in directory.glob("*.json") if f.stem.isdigit()])
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # If data is a list, extend; if single object, append
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return all_data

def load_reasoning_type_data(reasoning_type: str, base_dir: Path) -> Dict[str, List]:
    """Load all sessions and attempts data for a specific reasoning type."""
    reasoning_dir = base_dir / reasoning_type
    
    sessions_dir = reasoning_dir / "sessions"
    attempts_dir = reasoning_dir / "attempts"
    
    sessions = load_json_files(sessions_dir)
    attempts = load_json_files(attempts_dir)
    
    # Add reasoning type to each record for identification
    for session in sessions:
        session['reasoning_type'] = reasoning_type
    
    for attempt in attempts:
        attempt['reasoning_type'] = reasoning_type
    
    return {
        'sessions': sessions,
        'attempts': attempts
    }

def main():
    # Define the base directory and reasoning types
    base_dir = Path("tests")
    
    # Get all available reasoning types from directory structure
    reasoning_types = []
    for item in base_dir.iterdir():
        if item.is_dir() and (item / "sessions").exists() and (item / "attempts").exists():
            reasoning_types.append(item.name)
    
    print(f"Found reasoning types: {reasoning_types}")
    
    # Initialize combined data structures
    all_sessions = []
    all_attempts = []
    
    # Load data from each reasoning type
    for reasoning_type in reasoning_types:
        print(f"Loading data for {reasoning_type}...")
        data = load_reasoning_type_data(reasoning_type, base_dir)
        
        sessions = data['sessions']
        attempts = data['attempts']
        
        print(f"  - Sessions: {len(sessions)}")
        print(f"  - Attempts: {len(attempts)}")
        
        all_sessions.extend(sessions)
        all_attempts.extend(attempts)
    
    # Create summary statistics
    print(f"\nCombined data summary:")
    print(f"Total sessions: {len(all_sessions)}")
    print(f"Total attempts: {len(all_attempts)}")
    
    # Sessions by reasoning type
    sessions_by_type = {}
    for session in all_sessions:
        reasoning_type = session.get('reasoning_type', 'unknown')
        sessions_by_type[reasoning_type] = sessions_by_type.get(reasoning_type, 0) + 1
    
    print(f"\nSessions by reasoning type:")
    for rtype, count in sessions_by_type.items():
        print(f"  {rtype}: {count}")
    
    # Attempts by reasoning type
    attempts_by_type = {}
    for attempt in all_attempts:
        reasoning_type = attempt.get('reasoning_type', 'unknown')
        attempts_by_type[reasoning_type] = attempts_by_type.get(reasoning_type, 0) + 1
    
    print(f"\nAttempts by reasoning type:")
    for rtype, count in attempts_by_type.items():
        print(f"  {rtype}: {count}")
    
    # Save combined data
    combined_data = {
        'metadata': {
            'reasoning_types': reasoning_types,
            'total_sessions': len(all_sessions),
            'total_attempts': len(all_attempts),
            'sessions_by_type': sessions_by_type,
            'attempts_by_type': attempts_by_type
        },
        'sessions': all_sessions,
        'attempts': all_attempts
    }
    
    # Save as JSON
    output_file = "combined_test_data.json"
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"\nCombined data saved to {output_file}")
    
    # Also save as separate CSV files for easier analysis
    if all_sessions:
        sessions_df = pd.DataFrame(all_sessions)
        sessions_df.to_csv("combined_sessions.csv", index=False)
        print(f"Sessions data saved to combined_sessions.csv")
    
    if all_attempts:
        attempts_df = pd.DataFrame(all_attempts)
        attempts_df.to_csv("combined_attempts.csv", index=False)
        print(f"Attempts data saved to combined_attempts.csv")
    
    # Sample data preview
    print(f"\nSample session data:")
    if all_sessions:
        sample_session = all_sessions[0]
        for key, value in sample_session.items():
            print(f"  {key}: {value}")
    
    print(f"\nSample attempt data:")
    if all_attempts:
        sample_attempt = all_attempts[0]
        for key, value in sample_attempt.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
