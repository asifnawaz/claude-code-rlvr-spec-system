#!/usr/bin/env python3
"""
Tier Updater - Updates agent tiers based on performance
Run this as a cron job or manually to update agent tiers
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List

CLAUDE_DIR = Path(__file__).parent.parent
AGENTS_DIR = CLAUDE_DIR / "agents"
SCOREBOARD_DIR = CLAUDE_DIR / "scoreboard"
CONFIG_DIR = CLAUDE_DIR / "config"

def load_config() -> Dict:
    """Load tier configuration"""
    config_file = CONFIG_DIR / "settings.json"
    
    default_config = {
        "tiers": {
            "promotion_threshold": 4.0,
            "demotion_threshold": 2.0,
            "suspension_threshold": 0.0,
            "evaluation_window": 10,
            "grace_period_tasks": 3
        }
    }
    
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            return config.get("tiers", default_config["tiers"])
    
    return default_config["tiers"]

def get_agent_rewards(agent_name: str, limit: int = 10) -> List[float]:
    """Get recent rewards for an agent"""
    rewards = []
    
    # Read from JSONL scoreboard
    scoreboard_file = SCOREBOARD_DIR / "rlvr.jsonl"
    if not scoreboard_file.exists():
        return rewards
    
    with open(scoreboard_file) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("agent_name") == agent_name:
                    rewards.append(entry.get("reward", 0.0))
            except:
                continue
    
    # Return most recent rewards
    return rewards[-limit:] if len(rewards) > limit else rewards

def calculate_new_tier(current_tier: str, avg_reward: float, total_tasks: int, config: Dict) -> str:
    """Calculate new tier based on performance"""
    
    # Check if agent has enough tasks for evaluation
    if total_tasks < config["grace_period_tasks"]:
        return current_tier  # Keep current tier during grace period
    
    # Determine new tier based on thresholds
    if avg_reward >= config["promotion_threshold"]:
        new_tier = "principal"
    elif avg_reward >= config["demotion_threshold"]:
        new_tier = "senior"
    elif avg_reward > config["suspension_threshold"]:
        new_tier = "junior"
    else:
        new_tier = "suspended"
    
    return new_tier

def update_agent_tier(agent_file: Path, new_tier: str, reason: str = "automatic") -> bool:
    """Update agent tier in YAML file"""
    try:
        with open(agent_file) as f:
            agent_data = yaml.safe_load(f)
        
        old_tier = agent_data.get("tier", "junior")
        
        if old_tier == new_tier:
            return False  # No change needed
        
        # Update tier
        agent_data["tier"] = new_tier
        
        # Add to tier history
        if "tier_history" not in agent_data:
            agent_data["tier_history"] = []
        
        agent_data["tier_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "from_tier": old_tier,
            "to_tier": new_tier,
            "reason": reason,
            "rolling_avg": agent_data.get("performance", {}).get("rolling_avg_reward", 0.0)
        })
        
        # Keep only last 10 tier changes
        agent_data["tier_history"] = agent_data["tier_history"][-10:]
        
        # Write updated data
        with open(agent_file, 'w') as f:
            yaml.dump(agent_data, f, default_flow_style=False, sort_keys=False)
        
        # Log tier change
        log_tier_change(agent_data["name"], old_tier, new_tier, reason)
        
        return True
        
    except Exception as e:
        print(f"Error updating agent tier: {e}")
        return False

def log_tier_change(agent_name: str, old_tier: str, new_tier: str, reason: str):
    """Log tier change to scoreboard"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": "tier_change",
        "agent_name": agent_name,
        "from_tier": old_tier,
        "to_tier": new_tier,
        "reason": reason
    }
    
    log_file = SCOREBOARD_DIR / "tier_changes.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    # Also log to events
    events_file = SCOREBOARD_DIR / "events.jsonl"
    with open(events_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def update_leaderboard():
    """Update the leaderboard with current standings"""
    agents = []
    
    # Collect all agent data
    for agent_file in AGENTS_DIR.glob("agent-*.yml"):
        try:
            with open(agent_file) as f:
                agent_data = yaml.safe_load(f)
            
            if agent_data.get("tier") != "suspended":
                agents.append({
                    "name": agent_data["name"],
                    "tier": agent_data["tier"],
                    "rolling_avg_reward": agent_data.get("performance", {}).get("rolling_avg_reward", 0.0),
                    "total_tasks": agent_data.get("performance", {}).get("total_tasks", 0),
                    "specializations": agent_data.get("specializations", [])
                })
        except:
            continue
    
    # Sort by reward
    agents.sort(key=lambda a: a["rolling_avg_reward"], reverse=True)
    
    # Add rankings
    for i, agent in enumerate(agents):
        agent["rank"] = i + 1
    
    # Save leaderboard
    leaderboard = {
        "updated_at": datetime.utcnow().isoformat(),
        "agents": agents
    }
    
    leaderboard_file = SCOREBOARD_DIR / "leaderboard.json"
    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f, indent=2)

def main():
    """Main tier update process"""
    print(f"Starting tier update process at {datetime.utcnow().isoformat()}")
    
    # Load configuration
    config = load_config()
    
    # Track changes
    changes_made = 0
    
    # Process each agent
    for agent_file in AGENTS_DIR.glob("agent-*.yml"):
        try:
            # Load agent data
            with open(agent_file) as f:
                agent_data = yaml.safe_load(f)
            
            agent_name = agent_data["name"]
            current_tier = agent_data.get("tier", "junior")
            performance = agent_data.get("performance", {})
            
            # Get recent rewards
            recent_rewards = get_agent_rewards(agent_name, config["evaluation_window"])
            
            if not recent_rewards:
                print(f"No rewards found for {agent_name}, skipping")
                continue
            
            # Calculate new average
            avg_reward = sum(recent_rewards) / len(recent_rewards)
            total_tasks = performance.get("total_tasks", 0)
            
            # Update performance data
            performance["rolling_avg_reward"] = round(avg_reward, 2)
            performance["last_10_rewards"] = recent_rewards
            agent_data["performance"] = performance
            
            # Save updated performance
            with open(agent_file, 'w') as f:
                yaml.dump(agent_data, f, default_flow_style=False, sort_keys=False)
            
            # Calculate new tier
            new_tier = calculate_new_tier(current_tier, avg_reward, total_tasks, config)
            
            # Update if changed
            if new_tier != current_tier:
                if update_agent_tier(agent_file, new_tier):
                    print(f"Updated {agent_name}: {current_tier} → {new_tier} (avg: {avg_reward:.2f})")
                    changes_made += 1
            else:
                print(f"No change for {agent_name}: {current_tier} (avg: {avg_reward:.2f})")
                
        except Exception as e:
            print(f"Error processing {agent_file}: {e}")
            continue
    
    # Update leaderboard
    update_leaderboard()
    
    print(f"Tier update complete. {changes_made} changes made.")
    
    # Save update timestamp
    timestamp_file = SCOREBOARD_DIR / "last_tier_update.txt"
    with open(timestamp_file, 'w') as f:
        f.write(datetime.utcnow().isoformat())

if __name__ == "__main__":
    main()