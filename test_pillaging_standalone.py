#!/usr/bin/env python3
"""
Simple test script for pillaging functionality without framework dependencies.
"""
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import just the functions we need
from cai.tools.pillaging import (
    extract_ip_addresses,
    extract_software_versions,
    extract_pii,
    extract_credentials,
    run_crackmapexec_and_parse
)

def test_extract_ip_addresses():
    print("Testing IP address extraction...")
    text = "Server is at 192.168.1.1 and backup at 10.0.0.1"
    ips = extract_ip_addresses(text)
    assert "192.168.1.1" in ips
    assert "10.0.0.1" in ips
    print("✓ IP extraction works")

def test_extract_software_versions():
    print("Testing software version extraction...")
    text = "Running Apache/2.4.53 nginx/1.20.1"
    versions = extract_software_versions(text)
    assert "Apache" in versions
    assert "nginx" in versions
    assert versions["Apache"] == "2.4.53"
    print("✓ Software version extraction works")

def test_extract_pii():
    print("Testing PII extraction...")
    text = """
    Contact us at support@example.com
    Call us at +1-555-123-4567
    Visit https://www.example.com
    """
    pii = extract_pii(text)
    assert "support@example.com" in pii["emails"]
    assert len(pii["phone_numbers"]) > 0
    assert len(pii["urls"]) > 0
    print("✓ PII extraction works")

def test_extract_credentials():
    print("Testing credential extraction...")
    text = """
    api_key = "sk-1234567890abcdef1234567890abcdef"
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    mysql://user:pass@localhost/db
    """
    creds = extract_credentials(text)
    api_keys = [c for c in creds if c["type"] == "api_key"]
    bearer_tokens = [c for c in creds if c["type"] == "bearer_token"]
    db_creds = [c for c in creds if c["type"] == "database_connection"]
    
    assert len(api_keys) > 0
    assert len(bearer_tokens) > 0
    assert len(db_creds) > 0
    print("✓ Credential extraction works")

def test_run_crackmapexec():
    print("Testing CrackMapExec functionality...")
    # This should return an error since crackmapexec likely isn't installed
    result = run_crackmapexec_and_parse("127.0.0.1", "--timeout 5")
    assert result["status"] == "error"
    assert "not found" in result["message"].lower()
    print("✓ CrackMapExec error handling works")

if __name__ == "__main__":
    print("Running pillaging functionality tests...\n")
    
    try:
        test_extract_ip_addresses()
        test_extract_software_versions()
        test_extract_pii()
        test_extract_credentials()
        test_run_crackmapexec()
        
        print("\n🎉 All tests passed! Pillaging functionality is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)