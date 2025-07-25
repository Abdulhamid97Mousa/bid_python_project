#!/usr/bin/env python3
# C:\Users\Hamid\Desktop\Transformer\bid_python_project\start_workflow.py
# start_workflow.py
"""
Startup script for the new Protocol Buffers + ZeroMQ BDI-RL workflow
This replaces the old file-based polling system
"""

import subprocess
import sys
import time
import signal
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import zmq
        import google.protobuf
        print("✓ ZeroMQ and Protocol Buffers are available")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_rl_sender():
    """Start the RL plan sender in background"""
    print("Starting RL Plan Sender...")
    return subprocess.Popen([
        sys.executable, "rl_plan_sender.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def start_agents():
    """Start the BDI agents"""
    print("Starting BDI Agents...")
    return subprocess.Popen([
        sys.executable, "agent_launcher.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def main():
    print("=" * 50)
    print("BDI-RL Protocol Buffer + ZeroMQ Workflow")
    print("=" * 50)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if mutations_pb2.py exists
    if not os.path.exists("mutations_pb2.py"):
        print("✗ mutations_pb2.py not found")
        print("Generating Protocol Buffer stubs...")
        try:
            subprocess.run(["protoc", "--python_out=.", "mutations.proto"], check=True)
            print("✓ Protocol Buffer stubs generated")
        except subprocess.CalledProcessError:
            print("✗ Failed to generate Protocol Buffer stubs")
            print("Make sure 'protoc' is installed and in your PATH")
            sys.exit(1)
    
    processes = []
    
    try:
        # Start RL sender
        rl_process = start_rl_sender()
        processes.append(rl_process)
        time.sleep(2)  # Give it time to bind to port
        
        # Start agents
        agent_process = start_agents()
        processes.append(agent_process)
        
        print()
        print("🚀 Workflow started successfully!")
        print("✓ RL Plan Sender running on tcp://localhost:5555")
        print("✓ BDI Agents listening for plan mutations")
        print()
        print("Press Ctrl+C to stop all processes...")
        
        # Wait for processes or keyboard interrupt
        while True:
            time.sleep(1)
            
            # Check if any process died unexpectedly
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    print(f"⚠ Process {i} exited unexpectedly")
                    break
    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal, shutting down...")
    
    finally:
        # Clean shutdown
        print("Stopping all processes...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        print("✓ All processes stopped")
        print("Goodbye!")

if __name__ == "__main__":
    main()
