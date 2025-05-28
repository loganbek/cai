"""
Tools for pillaging and extracting sensitive information from various sources.
"""
import re

def extract_ip_addresses(text: str) -> list[str]:
    """
    Extracts IPv4 addresses from a given text.

    Args:
        text: The text to search for IP addresses.

    Returns:
        A list of unique IP addresses found.
    """
    # Regex for IPv4 addresses
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(ip_pattern, text)
    # Filter out invalid IPs like 0.0.0.0 or 255.255.255.255 if necessary,
    # and ensure they are actual valid IPs.
    # For simplicity, this example returns all matches.
    return list(set(ips))

def extract_software_versions(text: str) -> dict[str, str]:
    """
    Extracts software names and their versions from text.
    This is a basic implementation and might need to be expanded
    for more complex versioning schemes.

    Args:
        text: The text to search for software versions.

    Returns:
        A dictionary where keys are software names and values are their versions.
    """
    versions = {}
    # Common patterns: "SoftwareName/Version", "SoftwareName Version", "Version: x.y.z"
    # This regex is a starting point and can be quite broad.
    # Example: Apache/2.4.52, nginx/1.21.6, OpenSSH_8.2p1, vsftpd 3.0.3
    # More specific regexes might be needed for different output formats.
    patterns = [
        r'([a-zA-Z0-9\._-]+)/([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:[a-zA-Z0-9\.-]+)?)',  # Apache/2.4.52, nginx/1.21.6
        r'([a-zA-Z0-9\._-]+)\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:[a-zA-Z0-9\.-]+)?)', # vsftpd 3.0.3
        r'([Oo]penSSH)[_-]([0-9]+\.[0-9]+[a-zA-Z0-9\._-]*)', # OpenSSH_8.2p1, openssh-8.2
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                software_name = match[0].strip().rstrip('_')
                version_number = match[1].strip()
                # Avoid overwriting if a more specific version was already found (e.g. patch version)
                if software_name not in versions or len(version_number) > len(versions[software_name]):
                    versions[software_name] = version_number
    return versions

def extract_pii(text: str) -> dict:
    """
    Extracts personally identifiable information from text.
    This searches for patterns like email addresses, phone numbers, 
    credit card numbers, and other common PII patterns.

    Args:
        text: The text to search for PII.

    Returns:
        A dictionary containing found PII, categorized by type.
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
        r'\b\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',  # US format
        r'\b\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}\b'  # International
    ]
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    pii_data["phone_numbers"] = list(set(phone_numbers))
    
    # Credit card numbers (basic pattern, 13-19 digits)
    cc_pattern = r'\b(?:[0-9]{4}[-\s]?){3,4}[0-9]{1,4}\b'
    potential_ccs = re.findall(cc_pattern, text)
    # Filter out obvious non-credit cards (like repeated digits or IPs)
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
    This searches for username/password pairs, API keys, tokens, and other sensitive data.
    Care should be taken due to the sensitivity of this data.

    Args:
        text: The text to search for credentials.

    Returns:
        A list of dictionaries, each representing a found credential.
    """
    credentials = []
    
    # Username:password patterns
    user_pass_patterns = [
        r'([a-zA-Z0-9._-]+):([a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+)',  # Basic user:pass
        r'user[name]*\s*[:=]\s*([^\s]+).*?pass[word]*\s*[:=]\s*([^\s]+)',  # user= pass=
        r'login\s*[:=]\s*([^\s]+).*?password\s*[:=]\s*([^\s]+)',  # login= password=
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
    Note: This requires CrackMapExec to be installed on the system.

    Args:
        target: The target specification for CrackMapExec (e.g., IP, range, CIDR).
        options: Additional options for CrackMapExec.

    Returns:
        A dictionary containing parsed results from CrackMapExec.
    """
    import subprocess
    import json
    import os
    
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
            # Split options safely 
            cmd.extend(options.split())
        
        # Add JSON output if not already specified
        if "--json" not in options and "-j" not in options:
            cmd.append("--json")
        
        # Run the command with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False
        )
        
        parsed_results = {
            "status": "completed",
            "target": target,
            "return_code": result.returncode,
            "hosts": [],
            "services": [],
            "vulnerabilities": [],
            "raw_output": result.stdout,
            "errors": result.stderr
        }
        
        # Parse the output
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Try to parse as JSON first
                try:
                    json_data = json.loads(line)
                    if "host" in json_data:
                        parsed_results["hosts"].append(json_data)
                    continue
                except json.JSONDecodeError:
                    pass
                
                # Parse text output for key information
                if "SMB" in line and "445" in line:
                    # SMB service detection
                    parts = line.split()
                    if len(parts) >= 3:
                        parsed_results["services"].append({
                            "host": parts[0] if parts[0] != "SMB" else "unknown",
                            "port": "445",
                            "service": "SMB",
                            "details": line
                        })
                
                elif "VULNERABLE" in line.upper() or "SUCCESS" in line:
                    # Potential vulnerability or successful exploit
                    parsed_results["vulnerabilities"].append({
                        "description": line,
                        "severity": "high" if "VULNERABLE" in line.upper() else "info"
                    })
                
                elif ":" in line and any(port in line for port in ["445", "139", "22", "3389"]):
                    # General service detection
                    try:
                        host_port = line.split()[0]
                        if ":" in host_port:
                            host, port = host_port.split(":", 1)
                            parsed_results["services"].append({
                                "host": host,
                                "port": port,
                                "details": line
                            })
                    except (IndexError, ValueError):
                        pass
        
        return parsed_results
        
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

# Example usage (for testing purposes, typically not part of the library code)
if __name__ == '__main__':
    sample_text_ips = """
    Server A is at 192.168.1.10.
    Server B is at 10.0.0.5 and 172.16.0.1.
    Invalid IP: 999.999.999.999. Gateway: 0.0.0.0
    My public IP is 8.8.8.8.
    """
    print(f"IPs found: {extract_ip_addresses(sample_text_ips)}")

    sample_text_versions = """
    Running Apache/2.4.53 (Unix) OpenSSL/1.1.1k PHP/7.4.28.
    Server: nginx/1.20.1
    SSH server version: OpenSSH_8.2p1 Ubuntu-4ubuntu0.3
    FTP Server: vsftpd 3.0.3
    Microsoft-IIS/10.0
    Another service version 1.2.3-beta
    """
    print(f"Software versions found: {extract_software_versions(sample_text_versions)}")
    
    # Test PII extraction
    sample_text_pii = """
    Contact us at support@example.com or admin@test.org
    Call us at +1-555-123-4567 or (555) 987-6543
    Visit our website at https://www.example.com
    Credit card: 4111-1111-1111-1111
    SSN: 123-45-6789
    """
    print(f"PII found: {extract_pii(sample_text_pii)}")
    
    # Test credential extraction  
    sample_text_creds = """
    Database config:
    username:admin
    password:secret123
    api_key = "sk-1234567890abcdef1234567890abcdef"
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    mysql://user:pass@localhost/db
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    """
    print(f"Credentials found: {extract_credentials(sample_text_creds)}")
    
    # Test CrackMapExec (will show not available message in most environments)
    print(f"CrackMapExec test: {run_crackmapexec_and_parse('127.0.0.1', '--timeout 5')}")
