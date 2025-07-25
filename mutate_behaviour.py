# # agent_launcher.py
# C:\Users\Hamid\Desktop\Transformer\bid_python_project\mutate_behaviour.py
import zmq
import asyncio
import re
import logging
from spade.behaviour import CyclicBehaviour
from spade_bdi.bdi import BDIAgent
from mutations_pb2 import PlanMutation, BeliefMutation

# Basic plan syntax validation
PLAN_OK = re.compile(r'^[+!@\w].*<-.*\.$', re.MULTILINE | re.DOTALL)

class MutateBehaviour(CyclicBehaviour):
    """
    Cyclic behavior that subscribes to ZeroMQ messages and applies 
    runtime mutations to the agent's plan library
    """
    
    async def on_start(self):
        """Initialize ZeroMQ subscriber"""
        self.context = zmq.Context.instance()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5555")
        self.subscriber.setsockopt(zmq.SUBSCRIBE, b"")  # Subscribe to all messages
        self.subscriber.setsockopt(zmq.RCVTIMEO, 100)  # 100ms timeout
        
        # Handle ZeroMQ slow-joiner syndrome - wait for connection to establish
        await asyncio.sleep(0.5)
        
        print(f"Agent {self.agent.jid} - MutateBehaviour started, listening for mutations...")
    
    async def run(self):
        """Main behavior loop - check for incoming mutations"""
        try:
            # Non-blocking receive with timeout
            raw_data = await asyncio.get_event_loop().run_in_executor(
                None, self._receive_message
            )
            
            if raw_data:
                await self._process_mutation(raw_data)
                
        except Exception as e:
            print(f"Agent {self.agent.jid} - Error in MutateBehaviour: {e}")
            await asyncio.sleep(0.1)  # Brief pause on error
    
    def _receive_message(self):
        """Receive ZeroMQ message (blocking call for executor)"""
        try:
            return self.subscriber.recv(zmq.NOBLOCK)
        except zmq.Again:
            return None  # No message available
    
    async def _process_mutation(self, raw_data):
        """Process incoming mutation message"""
        try:
            # Try to parse as PlanMutation first
            plan_mutation = PlanMutation()
            plan_mutation.ParseFromString(raw_data)
            
            if hasattr(plan_mutation, 'plan') and plan_mutation.plan:
                await self._apply_plan_mutation(plan_mutation)
                return
                
        except Exception:
            # If PlanMutation fails, try BeliefMutation
            try:
                belief_mutation = BeliefMutation()
                belief_mutation.ParseFromString(raw_data)
                await self._apply_belief_mutation(belief_mutation)
            except Exception as e:
                print(f"Agent {self.agent.jid} - Failed to parse mutation: {e}")
    
    async def _apply_plan_mutation(self, mutation):
        """Apply plan mutation to agent's BDI system"""
        if mutation.op == PlanMutation.ADD:
            # Validate plan syntax
            if not PLAN_OK.match(mutation.plan.strip()):
                print(f"Agent {self.agent.jid} - Invalid plan syntax: {mutation.plan[:50]}...")
                return
            
            try:
                # Add plan to agent's plan library
                # Note: This is a simplified approach - in real SPADE-BDI, 
                # you would use the proper BDI API methods
                print(f"Agent {self.agent.jid} - Adding new plan:")
                print(f"  Priority: {mutation.prio}")
                print(f"  Plan: {mutation.plan}")
                
                # Store the plan (in a real implementation, this would integrate with SPADE-BDI)
                if not hasattr(self.agent, 'runtime_plans'):
                    self.agent.runtime_plans = []
                self.agent.runtime_plans.append(mutation.plan)
                
                print(f"Agent {self.agent.jid} - Plan added successfully")
                
            except Exception as e:
                print(f"Agent {self.agent.jid} - Failed to add plan: {e}")
                
        elif mutation.op == PlanMutation.REMOVE:
            print(f"Agent {self.agent.jid} - Plan removal not implemented yet")
    
    async def _apply_belief_mutation(self, mutation):
        """Apply belief mutation to agent's BDI system"""
        if mutation.op == BeliefMutation.ADD:
            belief_str = f"{mutation.predicate}({', '.join(mutation.args)})"
            print(f"Agent {self.agent.jid} - Adding belief: {belief_str}")
            # In real SPADE-BDI: self.agent.bdi.set_belief(mutation.predicate, *mutation.args)
            
        elif mutation.op == BeliefMutation.REMOVE:
            belief_str = f"{mutation.predicate}({', '.join(mutation.args)})"
            print(f"Agent {self.agent.jid} - Removing belief: {belief_str}")
            # In real SPADE-BDI: self.agent.bdi.remove_belief(mutation.predicate, *mutation.args)
    
    async def on_end(self):
        """Cleanup on behavior termination"""
        if hasattr(self, 'subscriber'):
            self.subscriber.close()
        print(f"Agent {self.agent.jid} - MutateBehaviour stopped")


class MutableBDIAgent(BDIAgent):
    """
    BDI Agent that can receive runtime plan/belief mutations via ZeroMQ
    """
    
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.runtime_plans = []
    
    async def setup(self):
        """Setup the agent with mutation behavior"""
        print(f"Agent {self.jid} starting up...")
        
        # Add the mutation behavior
        mutate_behaviour = MutateBehaviour()
        self.add_behaviour(mutate_behaviour)
        
        print(f"Agent {self.jid} setup complete")
    
    def get_runtime_plans(self):
        """Get all runtime-added plans"""
        return getattr(self, 'runtime_plans', [])
