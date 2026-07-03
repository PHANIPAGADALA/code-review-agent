import json
import os
from datetime import datetime

# Path to the memory storage file
DB_FILE = "fixes_memory.json"

# Saves a bug fix to the memory storage file fixes_memory.json
def save_fix(bug_description: str, fix_code: str):
    print(f"[DEBUG] Attempting to save fix for bug description: '{bug_description}'")
    try:
        data = {}
        if os.path.exists(DB_FILE):
            print(f"[DEBUG] Loading existing memory from {DB_FILE}...")
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                
        data[bug_description] = {
            "fix": fix_code,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[DEBUG] Saving updated memory to {DB_FILE}...")
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
        print("[DEBUG] Fix successfully saved.")
    except Exception as e:
        print(f"[DEBUG] Error saving fix: {e}")

# Recalls a similar bug fix from memory based on word overlap in the bug description
def recall_similar_fix(bug_description: str) -> str or None:
    print(f"[DEBUG] Recalling similar fix for: '{bug_description}'")
    try:
        if not os.path.exists(DB_FILE):
            print(f"[DEBUG] Memory file {DB_FILE} does not exist. Returning None.")
            return None
            
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        input_words = set(bug_description.lower().split())
        
        best_match_count = 0
        best_fix = None
        
        for key, value in data.items():
            key_words = set(key.lower().split())
            match_count = len(input_words.intersection(key_words))
            
            if match_count > best_match_count:
                best_match_count = match_count
                best_fix = value.get("fix")
                
        print(f"[DEBUG] Best overlap found: {best_match_count} words.")
        if best_match_count >= 3:
            print("[DEBUG] Similar fix found in memory.")
            return best_fix
            
        print("[DEBUG] No match reached the threshold of 3 words. Returning None.")
        return None
    except Exception as e:
        print(f"[DEBUG] Error recalling fix: {e}")
        return None
