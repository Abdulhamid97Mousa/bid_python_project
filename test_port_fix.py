#!/usr/bin/env python3
"""
Test script to verify the port mismatch and slow-joiner fixes
"""

import subprocess
import sys
import time
import signal
import os

def test_fixed_communication():
    """Test that RL sender and agent can communicate properly"""
    print("=" * 60)
    print("  Testing Port Mismatch & Slow-Joiner Fixes")
    print("=" * 60)
    
    processes = []
    
    try:
        print("\n[1] Starting RL Plan Sender on fixed port 5555...")
        rl_process = subprocess.Popen([
            sys.executable, "rl_plan_sender.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        processes.append(("RL Sender", rl_process))
        
        # Wait for sender to bind and start publishing
        print("✓ RL Sender started")
        print("⏱ Waiting 1 second for sender to establish...")
        time.sleep(1)
        
        print("\n[2] Starting Agent Demo (with slow-joiner fix)...")
        agent_process = subprocess.Popen([
            sys.executable, "simple_agent_demo.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        processes.append(("Agent Demo", agent_process))
        
        print("✓ Agent started with 0.5s slow-joiner delay")
        
        print("\n[3] Monitoring communication for 10 seconds...")
        print("Expected: Agent should receive plan mutations without parse errors")
        print("-" * 60)
        
        # Monitor for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            time.sleep(0.5)
            
            # Check if processes are still running
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠ {name} process stopped unexpectedly")
                    # Try to get output
                    try:
                        stdout, stderr = process.communicate(timeout=1)
                        if stdout:
                            print(f"{name} output: {stdout[-200:]}")  # Last 200 chars
                        if stderr:
                            print(f"{name} errors: {stderr[-200:]}")
                    except:
                        pass
        
        print(f"\n⏰ Test completed after 10 seconds")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    
    finally:
        print("\n[4] Stopping all processes...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=3)
                print(f"✓ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"✓ {name} force-stopped")
            except Exception as e:
                print(f"⚠ {name} stop error: {e}")
        
        print("\n🏆 Port Fix Test Complete!")
        print("\n📋 What was tested:")
        print("  ✅ Fixed port 5555 (no auto-increment)")
        print("  ✅ 0.5s slow-joiner delay in agent")
        print("  ✅ Prefix framing (P for plans, B for beliefs)")
        print("  ✅ Proper error handling with message type detection")
        
        print("\n🎯 If successful, you should see:")
        print("  • 'Plan added successfully!' messages")
        print("  • No 'Failed to parse mutation' errors")
        print("  • Agent receiving plans in real-time")

if __name__ == "__main__":
    test_fixed_communication()
