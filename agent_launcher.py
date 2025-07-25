# agent_launcher.py 
# C:\Users\Hamid\Desktop\Transformer\bid_python_project\agent_launcher.py

import asyncio
import time
from mutate_behaviour import MutableBDIAgent

async def launch_agent(agent_id="agent01", domain="localhost"):
    """
    Launch a single BDI agent with mutation capabilities
    """
    jid = f"{agent_id}@{domain}"
    password = "password"  # In production, use proper authentication
    
    agent = MutableBDIAgent(jid, password)
    
    # Load initial beliefs and plans from agent.asl
    await load_initial_state(agent)
    
    print(f"Starting agent {jid}...")
    await agent.start()
    
    return agent

async def load_initial_state(agent):
    """
    Load initial beliefs and plans from agent.asl file
    This replaces the static file loading from the old workflow
    """
    try:
        with open("agent.asl", "r") as f:
            content = f.read()
        
        print(f"Loading initial state for agent {agent.jid}...")
        
        # Parse beliefs and goals from agent.asl
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//'):
                if line.startswith('!'):
                    # Initial goal
                    print(f"  Initial goal: {line}")
                elif line.endswith('.') and not line.startswith('+!') and not line.startswith('-!'):
                    # Initial belief
                    print(f"  Initial belief: {line}")
                elif line.startswith('+!'):
                    # Plan definition
                    print(f"  Initial plan: {line[:50]}...")
        
        # Store initial content for reference
        agent.initial_asl = content
        
    except FileNotFoundError:
        print(f"Warning: agent.asl not found, agent {agent.jid} will start with no initial state")
    except Exception as e:
        print(f"Error loading initial state for agent {agent.jid}: {e}")

async def launch_multiple_agents(num_agents=1):
    """
    Launch multiple agents for testing scalability
    """
    agents = []
    
    for i in range(num_agents):
        agent_id = f"agent{i:02d}"
        agent = await launch_agent(agent_id)
        agents.append(agent)
        
        # Small delay between agent startups
        await asyncio.sleep(0.5)
    
    print(f"\nAll {num_agents} agents started successfully!")
    print("Agents are now listening for RL plan mutations on ZeroMQ...")
    print("Press Ctrl+C to stop all agents")
    
    return agents

async def monitor_agents(agents):
    """
    Monitor running agents and their received mutations
    """
    while True:
        try:
            await asyncio.sleep(5)  # Check every 5 seconds
            
            print("\n=== Agent Status ===")
            for agent in agents:
                runtime_plans = agent.get_runtime_plans()
                print(f"Agent {agent.jid}: {len(runtime_plans)} runtime plans received")
                
        except KeyboardInterrupt:
            print("\nShutting down agents...")
            break

async def main():
    """
    Main launcher function
    """
    print("=== BDI-RL Agent Launcher ===")
    print("This replaces the old file-based workflow with ZeroMQ messaging")
    print()
    
    # Launch agents (you can change this number)
    num_agents = 1
    agents = await launch_multiple_agents(num_agents)
    
    try:
        # Monitor agents until interrupted
        await monitor_agents(agents)
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    
    finally:
        # Clean shutdown
        print("Stopping all agents...")
        for agent in agents:
            await agent.stop()
        print("All agents stopped")

if __name__ == "__main__":
    print("Starting BDI-RL Agent Launcher...")
    print("Make sure to start rl_plan_sender.py in another terminal!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
