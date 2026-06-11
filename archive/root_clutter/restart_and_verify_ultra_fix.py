#!/usr/bin/env python3
"""
SYSTEM3 RESTART AND VERIFICATION SCRIPT
Automates the restart process and verifies Ultra Model fix activation
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime
import psutil

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def find_python_processes(exclude_current=False):
    """Find all running Python processes related to System3
    
    Args:
        exclude_current: If True, exclude the current process
    """
    processes = []
    current_pid = os.getpid() if exclude_current else None
    current_script = os.path.basename(__file__) if exclude_current else None
    
    # Target scripts to look for (actual System3 processes)
    target_scripts = [
        'system3_autorun_master.py',
        'system3_watchdog.py',
        'system3_production_pipeline_clean.py',
        'run_system3.py'
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmdline_str = ' '.join(cmdline).lower()
                    
                    # Check if it's a target System3 process
                    is_target = any(script.lower() in cmdline_str 
                                  for script in target_scripts)
                    
                    if is_target:
                        # Skip current process if requested
                        if exclude_current and proc.info['pid'] == current_pid:
                            continue
                        # Skip this restart script
                        if exclude_current and current_script and current_script.lower() in cmdline_str:
                            continue
                        
                        processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': ' '.join(cmdline) if cmdline else 'N/A'
                        })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return processes

def stop_autorun():
    """Stop currently running System3 autorun processes"""
    print_header("STEP 1: STOPPING CURRENT AUTORUN")
    
    # Find processes excluding this script
    processes = find_python_processes(exclude_current=True)
    
    if not processes:
        print_info("No other System3 processes found running")
        return True
    
    print_info(f"Found {len(processes)} other System3 process(es):")
    for proc in processes:
        print(f"  PID {proc['pid']}: {proc['cmdline'][:80]}...")
    
    print("\nAttempting graceful shutdown...")
    for proc in processes:
        try:
            p = psutil.Process(proc['pid'])
            p.terminate()
            print_info(f"Sent termination signal to PID {proc['pid']}")
        except Exception as e:
            print_warning(f"Could not terminate PID {proc['pid']}: {e}")
    
    # Wait for processes to stop
    print("Waiting for processes to stop (max 10 seconds)...")
    for i in range(10):
        time.sleep(1)
        remaining = find_python_processes(exclude_current=True)
        if not remaining:
            print_success("All processes stopped gracefully")
            return True
        print(f"  {len(remaining)} process(es) still running...")
    
    # Force kill if still running
    remaining = find_python_processes(exclude_current=True)
    if remaining:
        print_warning("Some processes did not stop gracefully. Force killing...")
        for proc in remaining:
            try:
                p = psutil.Process(proc['pid'])
                p.kill()
                print_info(f"Force killed PID {proc['pid']}")
            except Exception as e:
                print_error(f"Could not kill PID {proc['pid']}: {e}")
        time.sleep(2)
    
    final_check = find_python_processes(exclude_current=True)
    if final_check:
        print_error(f"{len(final_check)} process(es) could not be stopped")
        return False
    
    print_success("All other System3 processes stopped")
    return True

def verify_environment():
    """Verify Python environment and dependencies"""
    print_header("STEP 2: ENVIRONMENT VERIFICATION")
    
    # Check virtual environment
    venv_path = Path("venv/Scripts/python.exe")
    if not venv_path.exists():
        print_error(f"Virtual environment not found at {venv_path}")
        return False
    print_success(f"Virtual environment found: {venv_path}")
    
    # Check Python version
    try:
        result = subprocess.run(
            [str(venv_path), "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print_success(f"Python version: {result.stdout.strip()}")
    except Exception as e:
        print_error(f"Could not verify Python version: {e}")
        return False
    
    # Check critical dependencies
    critical_deps = ['pandas', 'numpy', 'psutil']
    print("\nChecking critical dependencies...")
    for dep in critical_deps:
        try:
            subprocess.run(
                [str(venv_path), "-c", f"import {dep}"],
                capture_output=True,
                timeout=5,
                check=True
            )
            print_success(f"  {dep} installed")
        except subprocess.CalledProcessError:
            print_error(f"  {dep} NOT installed")
            return False
    
    return True

def check_ultra_fix_files():
    """Check if Ultra Model fix files exist"""
    print_header("STEP 3: ULTRA MODEL FIX VERIFICATION")
    
    fix_files = [
        'fix_ultra_model_feature_mismatch.py',
        'verify_ultra_features.py',
        'check_fix_status.py'
    ]
    
    all_exist = True
    for file in fix_files:
        if Path(file).exists():
            print_success(f"Found: {file}")
        else:
            print_warning(f"Missing: {file}")
            all_exist = False
    
    if not all_exist:
        print_warning("Some fix files are missing, but this may be okay")
    
    return True

def start_autorun():
    """Start System3 autorun"""
    print_header("STEP 4: STARTING SYSTEM3 AUTORUN")
    
    venv_python = Path("venv/Scripts/python.exe")
    autorun_script = Path("system3_autorun_master.py")
    
    if not autorun_script.exists():
        print_error(f"Autorun script not found: {autorun_script}")
        return False
    
    print_info("Starting autorun in background...")
    print_info("Command: python system3_autorun_master.py")
    
    try:
        # Start process in background
        if sys.platform == 'win32':
            # Windows: use CREATE_NEW_CONSOLE to run in new window
            subprocess.Popen(
                [str(venv_python), str(autorun_script)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=os.getcwd()
            )
        else:
            # Unix: use nohup
            subprocess.Popen(
                [str(venv_python), str(autorun_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
        
        print_success("Autorun started successfully")
        print_info("Waiting 5 seconds for startup...")
        time.sleep(5)
        
        # Verify process started (exclude this script)
        processes = find_python_processes(exclude_current=True)
        if processes:
            print_success(f"Autorun process running (PID: {processes[0]['pid']})")
            return True
        else:
            print_warning("Could not verify autorun process started")
            return False
            
    except Exception as e:
        print_error(f"Failed to start autorun: {e}")
        return False

def wait_for_signal_cycle():
    """Wait for next signal cycle"""
    print_header("STEP 5: WAITING FOR SIGNAL CYCLE")
    
    now = datetime.now()
    current_minute = now.minute
    
    # Signal cycles at :15 and :45
    if current_minute < 15:
        next_cycle = 15
    elif current_minute < 45:
        next_cycle = 45
    else:
        next_cycle = 15  # Next hour
    
    wait_minutes = (next_cycle - current_minute) % 60
    
    print_info(f"Current time: {now.strftime('%H:%M:%S')}")
    print_info(f"Next signal cycle: {now.hour}:{next_cycle:02d}")
    print_info(f"Wait time: ~{wait_minutes} minutes")
    
    if wait_minutes > 30:
        print_warning("Next cycle is far away. You may want to run verification manually later.")
        return False
    
    print("\nWaiting for signal cycle...")
    print("(You can press Ctrl+C to skip and verify manually later)")
    
    try:
        for i in range(wait_minutes * 60):
            time.sleep(1)
            if i % 60 == 0:
                remaining = wait_minutes - (i // 60)
                print(f"  {remaining} minute(s) remaining...")
    except KeyboardInterrupt:
        print_warning("\nWait interrupted by user")
        return False
    
    print_success("Signal cycle time reached!")
    print_info("Waiting additional 2 minutes for cycle to complete...")
    time.sleep(120)
    
    return True

def verify_ultra_fix():
    """Verify Ultra Model fix is loaded"""
    print_header("STEP 6: VERIFYING ULTRA MODEL FIX")
    
    venv_python = Path("venv/Scripts/python.exe")
    check_script = Path("check_fix_status.py")
    
    if not check_script.exists():
        print_warning(f"Verification script not found: {check_script}")
        print_info("Manual verification required:")
        print("  1. Check logs for 'USING_ULTRA_MODEL' messages")
        print("  2. Verify signal CSV has 114 columns (not 74)")
        print("  3. Check HOLD % is below 60% (was 79%)")
        return False
    
    print_info("Running verification script...")
    try:
        result = subprocess.run(
            [str(venv_python), str(check_script)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("\n" + "="*80)
        print(result.stdout)
        print("="*80 + "\n")
        
        if result.returncode == 0:
            print_success("Verification script completed successfully")
            return True
        else:
            print_warning("Verification script returned warnings")
            if result.stderr:
                print(f"Errors: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Could not run verification script: {e}")
        return False

def main():
    """Main execution flow"""
    print_header("SYSTEM3 RESTART & ULTRA FIX VERIFICATION")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Stop current autorun
    if not stop_autorun():
        print_error("Failed to stop current processes")
        print_info("Please manually stop System3 processes and try again")
        return 1
    
    # Step 2: Verify environment
    if not verify_environment():
        print_error("Environment verification failed")
        return 1
    
    # Step 3: Check fix files
    check_ultra_fix_files()
    
    # Step 4: Start autorun
    if not start_autorun():
        print_error("Failed to start autorun")
        print_info("Try running manually: SYSTEM3_DAILY_START.bat")
        return 1
    
    # Step 5: Wait for signal cycle (optional)
    print("\n" + "="*80)
    response = input("Wait for next signal cycle to verify fix? (y/n): ").lower()
    if response == 'y':
        if wait_for_signal_cycle():
            # Step 6: Verify fix
            verify_ultra_fix()
        else:
            print_info("\nSkipped automatic verification")
            print_info("Run manually later: python check_fix_status.py")
    else:
        print_info("\nSkipped automatic verification")
        print_info("Run manually after next signal cycle: python check_fix_status.py")
    
    # Summary
    print_header("RESTART COMPLETE")
    print_success("System3 has been restarted successfully")
    print("\nNext Steps:")
    print("  1. Monitor logs for 'USING_ULTRA_MODEL' messages")
    print("  2. After next signal cycle, run: python check_fix_status.py")
    print("  3. Verify HOLD % drops below 60% (was 79%)")
    print("  4. Check for 114 columns in signals CSV (was 74)")
    print("\nFor detailed guide, see: SYSTEM3_RESTART_ULTRA_FIX_GUIDE.md")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\n\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
