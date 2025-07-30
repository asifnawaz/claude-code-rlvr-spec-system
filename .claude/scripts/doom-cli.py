#!/usr/bin/env python3
"""
Doom CLI - Command-line interface for Doom-RLVR system
"""

import typer
import json
import yaml
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint

app = typer.Typer(help="Doom-RLVR CLI for Claude Code agent management")
console = Console()

CLAUDE_DIR = Path(__file__).parent.parent
AGENTS_DIR = CLAUDE_DIR / "agents"
SCOREBOARD_DIR = CLAUDE_DIR / "scoreboard"
TASKS_DIR = CLAUDE_DIR / "tasks"

@app.command()
def status(
    task_id: str = typer.Argument(None, help="Specific task ID to check"),
    format: str = typer.Option("table", help="Output format: table or json")
):
    """Check status of tasks or specific task"""
    
    if task_id:
        # Show specific task
        task_dir = TASKS_DIR / task_id
        if not task_dir.exists():
            console.print(f"[red]Task {task_id} not found[/red]")
            raise typer.Exit(1)
        
        metadata_file = task_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)
            
            if format == "json":
                print(json.dumps(metadata, indent=2))
            else:
                console.print(f"\n[bold]Task: {task_id}[/bold]")
                console.print(f"Status: {metadata.get('status', 'unknown')}")
                console.print(f"Agent: {metadata.get('agent_name', 'unassigned')}")
                console.print(f"Type: {metadata.get('task_type', 'unknown')}")
                console.print(f"Created: {metadata.get('created_at', 'unknown')}")
                if 'reward' in metadata:
                    console.print(f"Reward: {metadata['reward']:.2f}")
    else:
        # Show all recent tasks
        table = Table(title="Recent Tasks")
        table.add_column("Task ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Agent", style="yellow")
        table.add_column("Reward", style="magenta")
        
        tasks = []
        for task_dir in sorted(TASKS_DIR.iterdir(), reverse=True)[:10]:
            if task_dir.is_dir() and task_dir.name != "archive":
                metadata_file = task_dir / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        tasks.append(metadata)
                        table.add_row(
                            task_dir.name,
                            metadata.get('status', 'unknown'),
                            metadata.get('agent_name', 'unassigned'),
                            f"{metadata.get('reward', 0):.2f}" if 'reward' in metadata else "-"
                        )
        
        if format == "json":
            print(json.dumps(tasks, indent=2))
        else:
            console.print(table)

@app.command()
def agents(
    list: bool = typer.Option(True, "--list", help="List all agents"),
    tier: str = typer.Option(None, help="Filter by tier"),
    show: str = typer.Option(None, help="Show details for specific agent")
):
    """Manage and view agents"""
    
    if show:
        # Show specific agent
        agent_file = AGENTS_DIR / f"{show}.yml"
        if not agent_file.exists():
            agent_file = AGENTS_DIR / f"agent-{show}.yml"
        
        if not agent_file.exists():
            console.print(f"[red]Agent {show} not found[/red]")
            raise typer.Exit(1)
        
        with open(agent_file) as f:
            agent_data = yaml.safe_load(f)
        
        console.print(f"\n[bold]Agent: {agent_data['name']}[/bold]")
        console.print(f"Tier: {agent_data['tier']}")
        console.print(f"Specializations: {', '.join(agent_data['specializations'])}")
        
        perf = agent_data.get('performance', {})
        console.print(f"\n[bold]Performance:[/bold]")
        console.print(f"Rolling Average: {perf.get('rolling_avg_reward', 0):.2f}")
        console.print(f"Total Tasks: {perf.get('total_tasks', 0)}")
        console.print(f"Recent Rewards: {perf.get('last_10_rewards', [])}")
        
    else:
        # List agents
        table = Table(title="Claude Code Agents")
        table.add_column("Name", style="cyan")
        table.add_column("Tier", style="green")
        table.add_column("Specializations", style="yellow")
        table.add_column("Avg Reward", style="magenta")
        table.add_column("Tasks", style="blue")
        
        for agent_file in sorted(AGENTS_DIR.glob("agent-*.yml")):
            with open(agent_file) as f:
                agent_data = yaml.safe_load(f)
            
            if tier and agent_data.get('tier') != tier:
                continue
            
            perf = agent_data.get('performance', {})
            table.add_row(
                agent_data['name'],
                agent_data.get('tier', 'unknown'),
                ", ".join(agent_data.get('specializations', [])),
                f"{perf.get('rolling_avg_reward', 0):.2f}",
                str(perf.get('total_tasks', 0))
            )
        
        console.print(table)

@app.command()
def leaderboard(
    metric: str = typer.Option("reward", help="Metric to sort by: reward, tasks, or tier"),
    limit: int = typer.Option(10, help="Number of agents to show")
):
    """Show agent leaderboard"""
    
    leaderboard_file = SCOREBOARD_DIR / "leaderboard.json"
    
    if not leaderboard_file.exists():
        console.print("[yellow]No leaderboard data. Run tier update first.[/yellow]")
        raise typer.Exit(1)
    
    with open(leaderboard_file) as f:
        data = json.load(f)
    
    agents = data['agents'][:limit]
    
    table = Table(title=f"Agent Leaderboard (by {metric})")
    table.add_column("Rank", style="cyan")
    table.add_column("Agent", style="green")
    table.add_column("Tier", style="yellow")
    table.add_column("Avg Reward", style="magenta")
    table.add_column("Tasks", style="blue")
    
    # Sort by metric
    if metric == "tasks":
        agents.sort(key=lambda a: a['total_tasks'], reverse=True)
    elif metric == "tier":
        tier_order = {'principal': 3, 'senior': 2, 'junior': 1}
        agents.sort(key=lambda a: (tier_order.get(a['tier'], 0), a['rolling_avg_reward']), reverse=True)
    
    for i, agent in enumerate(agents):
        table.add_row(
            str(i + 1),
            agent['name'],
            agent['tier'],
            f"{agent['rolling_avg_reward']:.2f}",
            str(agent['total_tasks'])
        )
    
    console.print(table)
    console.print(f"\n[dim]Last updated: {data['updated_at']}[/dim]")

@app.command()
def scores(
    agent: str = typer.Argument(..., help="Agent name"),
    last: int = typer.Option(10, help="Number of recent scores to show")
):
    """Show recent scores for an agent"""
    
    rewards = []
    scoreboard_file = SCOREBOARD_DIR / "rlvr.jsonl"
    
    if not scoreboard_file.exists():
        console.print("[red]No scoreboard data found[/red]")
        raise typer.Exit(1)
    
    with open(scoreboard_file) as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get('agent_name') == agent or entry.get('agent_name') == f"agent-{agent}":
                    rewards.append(entry)
            except:
                continue
    
    if not rewards:
        console.print(f"[yellow]No scores found for agent {agent}[/yellow]")
        raise typer.Exit(1)
    
    # Show recent rewards
    recent = rewards[-last:]
    
    table = Table(title=f"Recent Scores for {agent}")
    table.add_column("Timestamp", style="cyan")
    table.add_column("Task ID", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Reward", style="magenta")
    
    for entry in recent:
        table.add_row(
            entry['timestamp'][:19],  # Truncate timestamp
            entry['task_id'],
            entry['task_status'],
            f"{entry['reward']:.2f}"
        )
    
    console.print(table)
    
    # Show average
    avg_reward = sum(e['reward'] for e in recent) / len(recent)
    console.print(f"\n[bold]Average reward (last {len(recent)}): {avg_reward:.2f}[/bold]")

@app.command()
def logs(
    tail: bool = typer.Option(False, "--tail", help="Follow log output"),
    task: str = typer.Option(None, help="Filter by task ID"),
    agent: str = typer.Option(None, help="Filter by agent name"),
    event: str = typer.Option(None, help="Filter by event type")
):
    """View system logs"""
    
    events_file = SCOREBOARD_DIR / "events.jsonl"
    
    if not events_file.exists():
        console.print("[yellow]No events logged yet[/yellow]")
        raise typer.Exit(1)
    
    def print_event(event_data):
        timestamp = event_data.get('timestamp', 'unknown')[:19]
        event_type = event_data.get('event', 'unknown')
        
        if event_type == 'task_assigned':
            console.print(f"[cyan]{timestamp}[/cyan] [green]ASSIGNED[/green] {event_data.get('task_id')} to {event_data.get('agent_name')}")
        elif event_type == 'task_completed':
            console.print(f"[cyan]{timestamp}[/cyan] [blue]COMPLETED[/blue] {event_data.get('task_id')} - reward: {event_data.get('reward', 0):.2f}")
        elif event_type == 'tier_change':
            console.print(f"[cyan]{timestamp}[/cyan] [yellow]TIER CHANGE[/yellow] {event_data.get('agent_name')}: {event_data.get('from_tier')} → {event_data.get('to_tier')}")
        else:
            console.print(f"[cyan]{timestamp}[/cyan] [dim]{event_type}[/dim] {json.dumps(event_data)}")
    
    if tail:
        # Follow mode
        import time
        with open(events_file) as f:
            # Go to end of file
            f.seek(0, 2)
            
            console.print("[bold]Following events... (Ctrl+C to stop)[/bold]\n")
            
            try:
                while True:
                    line = f.readline()
                    if line:
                        try:
                            event_data = json.loads(line)
                            
                            # Apply filters
                            if task and event_data.get('task_id') != task:
                                continue
                            if agent and event_data.get('agent_name') != agent:
                                continue
                            if event and event_data.get('event') != event:
                                continue
                            
                            print_event(event_data)
                        except:
                            pass
                    else:
                        time.sleep(0.5)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped following logs[/yellow]")
    else:
        # Show recent events
        events = []
        with open(events_file) as f:
            for line in f:
                try:
                    event_data = json.loads(line)
                    
                    # Apply filters
                    if task and event_data.get('task_id') != task:
                        continue
                    if agent and event_data.get('agent_name') != agent:
                        continue
                    if event and event_data.get('event') != event:
                        continue
                    
                    events.append(event_data)
                except:
                    pass
        
        # Show last 20 events
        for event_data in events[-20:]:
            print_event(event_data)

@app.command()
def update_tiers(
    dry_run: bool = typer.Option(False, help="Show what would change without updating")
):
    """Manually trigger tier update"""
    
    console.print("[bold]Running tier update...[/bold]\n")
    
    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]\n")
    
    # Run tier updater
    import subprocess
    result = subprocess.run([
        'python', str(CLAUDE_DIR / 'scripts' / 'tier-updater.py')
    ], capture_output=True, text=True)
    
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]")
    
    if result.returncode == 0:
        console.print("\n[green]Tier update completed successfully[/green]")
    else:
        console.print("\n[red]Tier update failed[/red]")

@app.command()
def init():
    """Initialize Doom-RLVR directories and files"""
    
    console.print("[bold]Initializing Doom-RLVR...[/bold]\n")
    
    # Create directories
    directories = [
        CLAUDE_DIR / "hooks",
        CLAUDE_DIR / "agents", 
        CLAUDE_DIR / "scripts",
        CLAUDE_DIR / "scoreboard",
        CLAUDE_DIR / "config",
        CLAUDE_DIR / "tasks",
        CLAUDE_DIR / "tasks" / "archive"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Created {dir_path}")
    
    # Create default config
    config_file = CLAUDE_DIR / "config" / "settings.json"
    if not config_file.exists():
        default_config = {
            "coordinator": {
                "max_concurrent_agents": 10,
                "task_timeout_default_ms": 300000
            },
            "evaluator": {
                "weights": {
                    "test_coverage_delta": 0.3,
                    "lint_score": 0.2,
                    "security_scan_score": 0.2,
                    "code_complexity_delta": 0.1,
                    "ci_pipeline_status": 0.1,
                    "review_feedback_score": 0.1
                }
            },
            "tiers": {
                "promotion_threshold": 4.0,
                "demotion_threshold": 2.0,
                "suspension_threshold": 0.0,
                "evaluation_window": 10
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        console.print(f"[green]✓[/green] Created default configuration")
    
    # Initialize empty scoreboard files
    for filename in ["rlvr.jsonl", "events.jsonl", "tier_changes.jsonl", "tool_usage.jsonl"]:
        filepath = SCOREBOARD_DIR / filename
        if not filepath.exists():
            filepath.touch()
            console.print(f"[green]✓[/green] Created {filename}")
    
    console.print("\n[bold green]Doom-RLVR initialized successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Create task.yml and run a command to test")
    console.print("2. Check agent status with: doom agents")
    console.print("3. View task status with: doom status")

if __name__ == "__main__":
    app()