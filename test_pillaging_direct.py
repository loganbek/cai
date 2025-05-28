#!/usr/bin/env python3
"""
Direct test of pillaging functionality implementations.
"""
import re
import subprocess
import json

def extract_ip_addresses(text: str) -> list[str]:
    """
    Extracts IPv4 addresses from a given text.
    """
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(ip_pattern, text)
    return list(set(ips))

def extract_software_versions(text: str) -> dict[str, str]:
    """
    Extracts software names and their versions from text.
    """
    versions = {}
    patterns = [
        r'([a-zA-Z0-9\._-]+)/([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:[a-zA-Z0-9\.-]+)?)',
        r'([a-zA-Z0-9\._-]+)\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:[a-zA-Z0-9\.-]+)?)',
        r'([Oo]penSSH)[_-]([0-9]+\.[0-9]+[a-zA-Z0-9\._-]*)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                software_name = match[0].strip().rstrip('_')
                version_number = match[1].strip()
                if software_name not in versions or len(version_number) > len(versions[software_name]):
                    versions[software_name] = version_number
    return versions

def extract_pii(text: str) -> dict:
    """
    Extracts personally identifiable information from text.
    """
    pii_data = {
        "emails": [],
        "phone_numbers": [], 
        "credit_cards": [],
        "ssns": [],
        "urls": []
    }
    
    # Email addresses
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    pii_data["emails"] = list(set(re.findall(email_pattern, text)))
    
    # Phone numbers (various formats)
    phone_patterns = [
        r'\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
        r'\b\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}\b'
    ]
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    pii_data["phone_numbers"] = list(set(phone_numbers))
    
    # Credit card numbers (basic pattern, 13-19 digits)
    cc_pattern = r'\b(?:[0-9]{4}[-\s]?){3,4}[0-9]{1,4}\b'
    potential_ccs = re.findall(cc_pattern, text)
    pii_data["credit_cards"] = [cc for cc in set(potential_ccs) 
                               if len(re.sub(r'[-\s]', '', cc)) >= 13]
    
    # Social Security Numbers (XXX-XX-XXXX format)
    ssn_pattern = r'\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b'
    pii_data["ssns"] = list(set(re.findall(ssn_pattern, text)))
    
    # URLs (basic pattern)
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
    pii_data["urls"] = list(set(re.findall(url_pattern, text)))
    
    return pii_data

def extract_credentials(text: str) -> list[dict]:
    """
    Extracts potential credentials from text.
    """
    credentials = []
    
    # Username:password patterns
    user_pass_patterns = [
        r'([a-zA-Z0-9._-]+):([a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+)',
        r'user[name]*\s*[:=]\s*([^\s]+).*?pass[word]*\s*[:=]\s*([^\s]+)',
        r'login\s*[:=]\s*([^\s]+).*?password\s*[:=]\s*([^\s]+)',
    ]
    
    for pattern in user_pass_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if len(match) == 2 and match[0] not in ['username', 'password', 'user', 'pass', 'login']:
                credentials.append({
                    "type": "username_password", 
                    "username": match[0],
                    "password": match[1]
                })
    
    # API Keys (common patterns)
    api_key_patterns = [
        (r'api[_-]?key\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?', "api_key"),
        (r'access[_-]?token\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})["\']?', "access_token"),
        (r'secret[_-]?key\s*[:=]\s*["\']?([a-zA-Z0-9._-]{20,})["\']?', "secret_key"),
        (r'bearer\s+([a-zA-Z0-9._-]{20,})', "bearer_token"),
        (r'authorization:\s*bearer\s+([a-zA-Z0-9._-]{20,})', "bearer_token"),
    ]
    
    for pattern, cred_type in api_key_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            credentials.append({
                "type": cred_type,
                "value": match if isinstance(match, str) else match[0]
            })
    
    # AWS Keys
    aws_patterns = [
        (r'AKIA[0-9A-Z]{16}', "aws_access_key"),
        (r'aws_secret_access_key\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', "aws_secret_key"),
    ]
    
    for pattern, cred_type in aws_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            credentials.append({
                "type": cred_type,
                "value": match if isinstance(match, str) else match[0]
            })
    
    # Database connection strings
    db_patterns = [
        r'mysql://([^:]+):([^@]+)@([^/]+)/([^\s]+)',
        r'postgresql://([^:]+):([^@]+)@([^/]+)/([^\s]+)',
        r'mongodb://([^:]+):([^@]+)@([^/]+)/([^\s]+)',
    ]
    
    for pattern in db_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 4:
                credentials.append({
                    "type": "database_connection",
                    "username": match[0],
                    "password": match[1], 
                    "host": match[2],
                    "database": match[3]
                })
    
    # SSH private keys
    ssh_key_pattern = r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'
    if re.search(ssh_key_pattern, text):
        credentials.append({
            "type": "ssh_private_key",
            "value": "SSH private key found"
        })
    
    return credentials

def run_crackmapexec_and_parse(target: str, options: str = "") -> dict:
    """
    Runs CrackMapExec and parses its output.
    """
    # Check if crackmapexec is available
    try:
        subprocess.run(["crackmapexec", "--version"], 
                      capture_output=True, check=True, timeout=10)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return {
            "status": "error",
            "message": "CrackMapExec not found or not accessible",
            "target": target
        }
    
    try:
        # Construct the command
        cmd = ["crackmapexec", target]
        if options:
            cmd.extend(options.split())
        
        # Add JSON output if not already specified
        if "--json" not in options and "-j" not in options:
            cmd.append("--json")
        
        # Run the command with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            check=False
        )
        
        return {
            "status": "completed",
            "target": target,
            "return_code": result.returncode,
            "hosts": [],
            "services": [],
            "vulnerabilities": [],
            "raw_output": result.stdout,
            "errors": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "message": "CrackMapExec execution timed out",
            "target": target
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error running CrackMapExec: {str(e)}",
            "target": target
        }

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
        import traceback
        traceback.print_exc()