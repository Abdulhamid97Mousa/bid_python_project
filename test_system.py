#!/usr/bin/env python3
"""
Simple test script to verify the Protocol Buffers + ZeroMQ system works
"""

import time
import asyncio
from mutations_pb2 import PlanMutation, BeliefMutation

def test_protobuf_serialization():
    """Test that Protocol Buffer serialization works"""
    print("Testing Protocol Buffer serialization...")
    
    # Test PlanMutation
    plan = PlanMutation(
        op=PlanMutation.ADD,
        prio=1,
        plan='+!test_goal : context(test) <- .print("Test successful").'
    )
    
    # Serialize and deserialize
    serialized = plan.SerializeToString()
    
    plan2 = PlanMutation()
    plan2.ParseFromString(serialized)
    
    assert plan2.op == PlanMutation.ADD
    assert plan2.prio == 1
    assert "test_goal" in plan2.plan
    
    print("✓ PlanMutation serialization works")
    
    # Test BeliefMutation
    belief = BeliefMutation(
        op=BeliefMutation.ADD,
        predicate="test_belief",
        args=["arg1", "arg2"]
    )
    
    serialized = belief.SerializeToString()
    belief2 = BeliefMutation()
    belief2.ParseFromString(serialized)
    
    assert belief2.op == BeliefMutation.ADD
    assert belief2.predicate == "test_belief"
    assert belief2.args == ["arg1", "arg2"]
    
    print("✓ BeliefMutation serialization works")

def test_zmq_availability():
    """Test that ZeroMQ is available"""
    print("Testing ZeroMQ availability...")
    
    try:
        import zmq
        print(f"✓ ZeroMQ version: {zmq.zmq_version()}")
        print(f"✓ PyZMQ version: {zmq.pyzmq_version()}")
        
        # Test basic socket creation
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.close()
        context.term()
        
        print("✓ ZeroMQ socket creation works")
        
    except ImportError:
        print("✗ ZeroMQ not available - run: pip install pyzmq")
        return False
    except Exception as e:
        print(f"✗ ZeroMQ error: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        "mutations.proto",
        "mutations_pb2.py", 
        "rl_plan_sender.py",
        "mutate_behaviour.py",
        "agent_launcher.py",
        "start_workflow.py",
        "requirements.txt",
        "agent.asl"
    ]
    
    missing_files = []
    for file in required_files:
        try:
            with open(file, 'r') as f:
                pass
            print(f"✓ {file}")
        except FileNotFoundError:
            missing_files.append(file)
            print(f"✗ {file} - missing")
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    
    return True

def main():
    print("=" * 50)
    print("BDI-RL System Test Suite")
    print("=" * 50)
    print()
    
    all_tests_passed = True
    
    try:
        # Test 1: File structure
        if not test_file_structure():
            all_tests_passed = False
        print()
        
        # Test 2: Protocol Buffers
        test_protobuf_serialization()
        print()
        
        # Test 3: ZeroMQ
        if not test_zmq_availability():
            all_tests_passed = False
        print()
        
        if all_tests_passed:
            print("🎉 All tests passed!")
            print()
            print("System is ready to run:")
            print("  python start_workflow.py")
            print()
            print("Or run components separately:")
            print("  Terminal 1: python rl_plan_sender.py")
            print("  Terminal 2: python agent_launcher.py")
        else:
            print("❌ Some tests failed. Please fix the issues above.")
            
    except Exception as e:
        print(f"❌ Test suite error: {e}")
        all_tests_passed = False
    
    return 0 if all_tests_passed else 1

if __name__ == "__main__":
    exit(main())
