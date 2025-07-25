#!/usr/bin/env python3
"""
Simplified BDI Agent Demo for testing the ZeroMQ Protocol Buffer system
This doesn't require SPADE-BDI or XMPP server, just demonstrates the messaging
"""

import zmq
import time
import asyncio
import re
from mutations_pb2 import PlanMutation, BeliefMutation

# Basic plan syntax validation
PLAN_OK = re.compile(r'^[+!@\w].*<-.*\.$', re.MULTILINE | re.DOTALL)

class SimpleBDIAgent:
    """
    Simplified BDI agent that demonstrates receiving mutations via ZeroMQ
    """
    
    def __init__(self, agent_id="demo_agent"):
        self.agent_id = agent_id
        self.beliefs = []
        self.plans = []
        self.runtime_plans = []
        self.context = zmq.Context()
        self.subscriber = None
        self.running = False
        
    def setup_zmq_connection(self, port=5555):
        """Setup ZeroMQ subscriber"""
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://localhost:{port}")
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")  # Subscribe to all messages
        self.subscriber.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
        
        # Handle ZeroMQ slow-joiner syndrome - wait for connection to establish
        time.sleep(0.5)
        
        print(f"Agent {self.agent_id} connected to ZeroMQ on port {port}")
    
    def load_initial_state(self):
        """Load initial beliefs and plans from agent.asl"""
        try:
            with open("agent.asl", "r") as f:
                content = f.read()
            
            print(f"Loading initial state for agent {self.agent_id}...")
            
            # Parse beliefs and goals from agent.asl
            for line in content.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    if line.startswith('!'):
                        print(f"  Initial goal: {line}")
                    elif line.endswith('.') and not line.startswith('+!') and not line.startswith('-!'):
                        self.beliefs.append(line)
                        print(f"  Initial belief: {line}")
                    elif line.startswith('+!'):
                        self.plans.append(line)
                        print(f"  Initial plan: {line[:50]}...")
                        
        except FileNotFoundError:
            print(f"Warning: agent.asl not found, agent {self.agent_id} will start with no initial state")
        except Exception as e:
            print(f"Error loading initial state: {e}")
    
    def process_mutation(self, raw_data):
        """Process incoming mutation message with prefix framing"""
        if len(raw_data) < 1:
            print(f"Agent {self.agent_id} - Received empty message")
            return
            
        # Check message type prefix
        message_type = raw_data[:1]
        message_data = raw_data[1:]
        
        try:
            if message_type == b"P":
                # PlanMutation
                plan_mutation = PlanMutation()
                plan_mutation.ParseFromString(message_data)
                self.apply_plan_mutation(plan_mutation)
                
            elif message_type == b"B":
                # BeliefMutation
                belief_mutation = BeliefMutation()
                belief_mutation.ParseFromString(message_data)
                self.apply_belief_mutation(belief_mutation)
                
            else:
                print(f"Agent {self.agent_id} - Unknown message type: {message_type}")
                
        except Exception as e:
            print(f"Agent {self.agent_id} - Failed to parse {message_type.decode('utf-8', errors='ignore')} mutation: {e}")
    
    def apply_plan_mutation(self, mutation):
        """Apply plan mutation to agent"""
        if mutation.op == PlanMutation.ADD:
            # Validate plan syntax
            if not PLAN_OK.match(mutation.plan.strip()):
                print(f"Agent {self.agent_id} - Invalid plan syntax: {mutation.plan[:50]}...")
                return
            
            print(f"Agent {self.agent_id} - Received new plan:")
            print(f"  Priority: {mutation.prio}")
            print(f"  Plan: {mutation.plan}")
            
            # Store the plan
            self.runtime_plans.append(mutation.plan)
            print(f"Agent {self.agent_id} - Plan added successfully! Total runtime plans: {len(self.runtime_plans)}")
            
        elif mutation.op == PlanMutation.REMOVE:
            print(f"Agent {self.agent_id} - Plan removal received (not implemented)")
    
    def apply_belief_mutation(self, mutation):
        """Apply belief mutation to agent"""
        if mutation.op == BeliefMutation.ADD:
            belief_str = f"{mutation.predicate}({', '.join(mutation.args)})"
            print(f"Agent {self.agent_id} - Adding belief: {belief_str}")
            self.beliefs.append(belief_str)
            
        elif mutation.op == BeliefMutation.REMOVE:
            belief_str = f"{mutation.predicate}({', '.join(mutation.args)})"
            print(f"Agent {self.agent_id} - Removing belief: {belief_str}")
            if belief_str in self.beliefs:
                self.beliefs.remove(belief_str)
    
    def run(self):
        """Main agent loop - listen for mutations"""
        self.running = True
        print(f"Agent {self.agent_id} started, listening for mutations...")
        
        while self.running:
            try:
                # Check for incoming messages
                raw_data = self.subscriber.recv(zmq.NOBLOCK)
                self.process_mutation(raw_data)
                
            except zmq.Again:
                # No message available, continue
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print(f"Agent {self.agent_id} - Received interrupt signal")
                break
                
            except Exception as e:
                print(f"Agent {self.agent_id} - Error: {e}")
                time.sleep(0.1)
    
    def stop(self):
        """Stop the agent"""
        self.running = False
        if self.subscriber:
            self.subscriber.close()
        self.context.term()
        print(f"Agent {self.agent_id} stopped")
    
    def get_status(self):
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'beliefs': len(self.beliefs),
            'initial_plans': len(self.plans),
            'runtime_plans': len(self.runtime_plans)
        }

def main():
    """Main function to run the simple agent demo"""
    print("=" * 60)
    print("  Simple BDI Agent Demo - ZeroMQ Protocol Buffer Testing")
    print("=" * 60)
    print()
    print("This demo agent will:")
    print("  1. Load initial state from agent.asl")
    print("  2. Connect to ZeroMQ on localhost:5555")
    print("  3. Listen for plan/belief mutations")
    print("  4. Display received mutations in real-time")
    print()
    print("Make sure rl_plan_sender.py is running in another terminal!")
    print()
    
    # Create and configure agent
    agent = SimpleBDIAgent("demo_agent_01")
    
    try:
        # Setup
        agent.load_initial_state()
        agent.setup_zmq_connection()
        
        print(f"Agent ready! Status: {agent.get_status()}")
        print("Press Ctrl+C to stop the agent")
        print("-" * 60)
        
        # Run the agent
        agent.run()
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal, stopping agent...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        agent.stop()
        print("Demo complete!")

if __name__ == "__main__":
    main()
