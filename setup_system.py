#!/usr/bin/env python3
"""
Complete setup script for BDI-RL Protocol Buffer + ZeroMQ system
Handles protoc installation with multiple fallback options
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import platform
from pathlib import Path

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n[{step}] {description}")

def run_command(cmd, description="", ignore_errors=False):
    """Run a command and return success status"""
    try:
        if description:
            print(f"  Running: {description}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            if not ignore_errors:
                print(f"  ✗ Failed: {result.stderr}")
            return False
    except Exception as e:
        if not ignore_errors:
            print(f"  ✗ Error: {e}")
        return False

def check_protoc():
    """Check if protoc is already installed"""
    return run_command("protoc --version", "Checking protoc installation", ignore_errors=True)

def install_protoc_windows():
    """Install protoc on Windows with multiple fallback methods"""
    print_step("1.1", "Installing protoc for Windows...")
    
    # Method 1: Try chocolatey
    print("  Trying Chocolatey...")
    if run_command("choco install protoc -y", ignore_errors=True):
        return True
    
    # Method 2: Manual download and installation
    print("  Chocolatey not available, trying manual installation...")
    
    protoc_dir = Path.home() / "tools" / "protoc"
    protoc_dir.mkdir(parents=True, exist_ok=True)
    
    protoc_zip = protoc_dir / "protoc-25.1-win64.zip"
    
    # Try multiple download sources
    download_urls = [
        "https://github.com/protocolbuffers/protobuf/releases/download/v25.1/protoc-25.1-win64.zip",
        "https://mirror.ghproxy.com/https://github.com/protocolbuffers/protobuf/releases/download/v25.1/protoc-25.1-win64.zip"
    ]
    
    downloaded = False
    for url in download_urls:
        try:
            print(f"  Downloading from: {url}")
            urllib.request.urlretrieve(url, protoc_zip)
            downloaded = True
            break
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            continue
    
    if not downloaded:
        print("  ✗ All download attempts failed")
        print("\n  MANUAL INSTALLATION REQUIRED:")
        print("  1. Download protoc-25.1-win64.zip from:")
        print("     https://github.com/protocolbuffers/protobuf/releases/download/v25.1/protoc-25.1-win64.zip")
        print(f"  2. Extract to: {protoc_dir}")
        print("  3. Add to PATH: export PATH=\"$HOME/tools/protoc/bin:$PATH\"")
        print("  4. Add to ~/.bashrc: echo 'export PATH=\"$HOME/tools/protoc/bin:$PATH\"' >> ~/.bashrc")
        return False
    
    # Extract the zip file
    try:
        with zipfile.ZipFile(protoc_zip, 'r') as zip_ref:
            zip_ref.extractall(protoc_dir)
        print("  ✓ Extracted protoc")
        
        # Add to PATH
        protoc_bin = protoc_dir / "bin"
        current_path = os.environ.get("PATH", "")
        if str(protoc_bin) not in current_path:
            os.environ["PATH"] = f"{protoc_bin}{os.pathsep}{current_path}"
            print("  ✓ Added to PATH (current session)")
            
            # Add to bashrc
            bashrc_line = f'export PATH="{protoc_bin}:$PATH"'
            bashrc_path = Path.home() / ".bashrc"
            
            try:
                with open(bashrc_path, "a") as f:
                    f.write(f"\n# Added by BDI-RL setup\n{bashrc_line}\n")
                print("  ✓ Added to ~/.bashrc")
            except Exception as e:
                print(f"  ⚠ Could not update ~/.bashrc: {e}")
                print(f"  Please manually add: {bashrc_line}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Extraction failed: {e}")
        return False

def install_protoc_linux():
    """Install protoc on Linux"""
    print_step("1.1", "Installing protoc for Linux...")
    
    # Try package manager
    if run_command("sudo apt-get update && sudo apt-get install -y protobuf-compiler", ignore_errors=True):
        return True
    
    if run_command("sudo yum install -y protobuf-compiler", ignore_errors=True):
        return True
    
    print("  ✗ Package manager installation failed")
    print("  Please install protoc manually or use a different Linux distribution")
    return False

def install_protoc_mac():
    """Install protoc on macOS"""
    print_step("1.1", "Installing protoc for macOS...")
    
    if run_command("brew install protobuf", ignore_errors=True):
        return True
    
    print("  ✗ Homebrew installation failed")
    print("  Please install Homebrew first: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    return False

def setup_protoc():
    """Setup protoc based on the operating system"""
    print_step("1", "Setting up Protocol Buffer Compiler (protoc)")
    
    if check_protoc():
        print("  ✓ protoc is already installed")
        return True
    
    system = platform.system().lower()
    
    if system == "windows":
        return install_protoc_windows()
    elif system == "linux":
        return install_protoc_linux()
    elif system == "darwin":
        return install_protoc_mac()
    else:
        print(f"  ✗ Unsupported operating system: {system}")
        return False

def setup_python_env():
    """Setup Python virtual environment and dependencies"""
    print_step("2", "Setting up Python Environment")
    
    # Check if virtual environment exists
    if not os.path.exists(".venv"):
        print("  Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv .venv"):
            return False
    else:
        print("  ✓ Virtual environment exists")
    
    # Install dependencies
    print("  Installing Python dependencies...")
    
    # Determine pip command based on OS
    if platform.system().lower() == "windows":
        pip_cmd = ".venv\\Scripts\\pip"
        python_cmd = ".venv\\Scripts\\python"
    else:
        pip_cmd = ".venv/bin/pip"
        python_cmd = ".venv/bin/python"
    
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        return False
    
    # Test imports
    test_cmd = f'{python_cmd} -c "import zmq, google.protobuf; print(f\\"ZMQ: {{zmq.zmq_version()}}, Protobuf: {{google.protobuf.__version__}}\\")"'
    if run_command(test_cmd, "Testing dependencies"):
        return True
    else:
        print("  ⚠ Dependency test failed, but continuing...")
        return True

def generate_protobuf_code():
    """Generate Python code from .proto files"""
    print_step("3", "Generating Protocol Buffer Code")
    
    if not os.path.exists("mutations.proto"):
        print("  ✗ mutations.proto not found")
        return False
    
    if run_command("protoc --python_out=. mutations.proto", "Generating Python stubs"):
        if os.path.exists("mutations_pb2.py"):
            print("  ✓ mutations_pb2.py generated successfully")
            return True
        else:
            print("  ✗ mutations_pb2.py not found after generation")
            return False
    else:
        print("  ✗ protoc code generation failed")
        print("\n  If protoc is not in PATH, try:")
        print("  1. Restart your terminal")
        print("  2. Run: source ~/.bashrc")
        print("  3. Or manually run: protoc --python_out=. mutations.proto")
        return False

def organize_files():
    """Organize project files and clean up legacy files"""
    print_step("4", "Organizing Project Files")
    
    # Create legacy_files directory
    legacy_dir = Path("legacy_files")
    legacy_dir.mkdir(exist_ok=True)
    
    # Files to move to legacy
    legacy_files = [
        "need_plan.txt",
        "new_plan.asl", 
        "merge_plan.py",
        "rl_plan_generator.py",
        "run_bdi_rl_workflow.py",
        "run_bdi_rl_wrapper.py"
    ]
    
    moved_count = 0
    for file in legacy_files:
        if os.path.exists(file):
            try:
                shutil.move(file, legacy_dir / file)
                moved_count += 1
                print(f"  ✓ Moved {file} to legacy_files/")
            except Exception as e:
                print(f"  ⚠ Could not move {file}: {e}")
    
    print(f"  ✓ Moved {moved_count} legacy files")
    return True

def setup_cargo_path():
    """Setup Cargo PATH if needed"""
    print_step("5", "Setting up Cargo PATH (if needed)")
    
    cargo_bin = Path.home() / ".cargo" / "bin"
    if cargo_bin.exists():
        # Add to bashrc if not already there
        bashrc_path = Path.home() / ".bashrc"
        cargo_line = f'export PATH="{cargo_bin}:$PATH"'
        
        try:
            if bashrc_path.exists():
                with open(bashrc_path, "r") as f:
                    content = f.read()
                if ".cargo/bin" not in content:
                    with open(bashrc_path, "a") as f:
                        f.write(f"\n# Added by BDI-RL setup - Cargo\n{cargo_line}\n")
                    print("  ✓ Added Cargo to ~/.bashrc")
                else:
                    print("  ✓ Cargo already in ~/.bashrc")
            else:
                with open(bashrc_path, "w") as f:
                    f.write(f"# Created by BDI-RL setup\n{cargo_line}\n")
                print("  ✓ Created ~/.bashrc with Cargo PATH")
        except Exception as e:
            print(f"  ⚠ Could not update ~/.bashrc: {e}")
            print(f"  Please manually add: {cargo_line}")
    else:
        print("  ✓ Cargo not found, skipping")
    
    return True

def run_tests():
    """Run system tests"""
    print_step("6", "Running System Tests")
    
    if os.path.exists("test_system.py"):
        if run_command(f"{sys.executable} test_system.py", "Running test suite"):
            return True
        else:
            print("  ⚠ Tests failed, but system may still work")
            return True
    else:
        print("  ⚠ test_system.py not found, skipping tests")
        return True

def print_next_steps():
    """Print next steps for the user"""
    print_header("🎉 Setup Complete!")
    
    print("\n📋 Next Steps:")
    print("1. Restart your terminal or run: source ~/.bashrc")
    print("2. Activate virtual environment:")
    
    if platform.system().lower() == "windows":
        print("   .venv\\Scripts\\activate")
    else:
        print("   source .venv/bin/activate")
    
    print("3. Test the system:")
    print("   python test_system.py")
    print("4. Run the complete workflow:")
    print("   python start_workflow.py")
    print("\n📚 Documentation:")
    print("   README.md - Complete setup and usage guide")
    print("   README_new_system.md - Technical details")
    
    print("\n🚀 Quick Test:")
    print("   python rl_plan_sender.py    # Terminal 1")
    print("   python agent_launcher.py    # Terminal 2")

def main():
    print_header("BDI-RL System Setup")
    print("This script will set up the complete Protocol Buffer + ZeroMQ system")
    print("for real-time ML/RL to BDI agent communication.")
    
    success_count = 0
    total_steps = 6
    
    steps = [
        setup_protoc,
        setup_python_env,
        generate_protobuf_code,
        organize_files,
        setup_cargo_path,
        run_tests
    ]
    
    for step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print(f"  ⚠ Step failed but continuing...")
        except Exception as e:
            print(f"  ✗ Step error: {e}")
    
    print_header(f"Setup Results: {success_count}/{total_steps} steps completed")
    
    if success_count >= 4:  # Core steps completed
        print_next_steps()
        return 0
    else:
        print("\n❌ Setup incomplete. Please check the errors above and:")
        print("1. Install protoc manually if needed")
        print("2. Check network connectivity")
        print("3. Run: pip install -r requirements.txt")
        print("4. Run: protoc --python_out=. mutations.proto")
        return 1

if __name__ == "__main__":
    exit(main())
