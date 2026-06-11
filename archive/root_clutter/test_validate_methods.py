#!/usr/bin/env python3
"""
Test script to verify the validate() methods in continuous_validators.py
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.monitoring.continuous_validators import TimestampValidator, MergeKeyValidator, VenvLockMode

def test_timestamp_validator():
    """Test TimestampValidator.validate()"""
    print("Testing TimestampValidator.validate()...")
    validator = TimestampValidator()
    result = validator.validate()
    print(f"Result: {result}")
    print(f"Passed: {result.get('passed', False)}")
    print()

def test_merge_key_validator():
    """Test MergeKeyValidator.validate()"""
    print("Testing MergeKeyValidator.validate()...")
    validator = MergeKeyValidator()
    result = validator.validate()
    print(f"Result: {result}")
    print(f"Passed: {result.get('passed', False)}")
    print()

def test_venv_lock_mode():
    """Test VenvLockMode.validate()"""
    print("Testing VenvLockMode.validate()...")
    validator = VenvLockMode()
    result = validator.validate()
    print(f"Result: {result}")
    print(f"Passed: {result.get('passed', False)}")
    print()

if __name__ == "__main__":
    print("Running validate() method tests...\n")

    try:
        test_timestamp_validator()
        test_merge_key_validator()
        test_venv_lock_mode()

        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
