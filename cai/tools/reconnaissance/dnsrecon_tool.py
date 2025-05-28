"""
DNSRecon tool for DNS enumeration and reconnaissance.
"""
import subprocess
import json
from typing import List, Dict, Optional


def run_dnsrecon_scan(
    domain: str,
    scan_type: str = "std",
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs dnsrecon against the specified domain for DNS enumeration.

    Args:
        domain: The target domain to enumerate (e.g., "example.com").
        scan_type: Type of scan to perform (std, brt, srv, axfr, rvl, snoop, tld, zonewalk).
        options: Optional list of dnsrecon command-line options.

    Returns:
        A dictionary containing DNS enumeration results or an error message.
    """
    if not domain:
        return {"error": "No domain specified for dnsrecon scan."}

    command = ["dnsrecon", "-d", domain, "-t", scan_type]

    if options:
        command.extend(options)

    # Add JSON output for better parsing
    if "-j" not in command and "--json" not in command:
        command.extend(["-j", "/tmp/dnsrecon_output.json"])

    try:
        print(f"Running DNSRecon command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        results = {"dns_records": [], "scan_type": scan_type, "domain": domain}

        # Try to read JSON output file first
        try:
            with open("/tmp/dnsrecon_output.json", "r") as f:
                json_data = json.load(f)
                if isinstance(json_data, list):
                    results["dns_records"] = json_data
                elif isinstance(json_data, dict):
                    results.update(json_data)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fall back to parsing stdout
            if process.stdout:
                for line in process.stdout.strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('['):
                        # Parse different types of DNS records
                        if any(record_type in line for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT']):
                            parts = line.split()
                            if len(parts) >= 3:
                                record_type = parts[0] if parts[0] in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'SOA', 'TXT'] else 'Unknown'
                                name = parts[1] if len(parts) > 1 else ''
                                value = ' '.join(parts[2:]) if len(parts) > 2 else ''
                                
                                results["dns_records"].append({
                                    "type": record_type,
                                    "name": name,
                                    "value": value,
                                    "raw": line
                                })

        if process.returncode != 0:
            error_message = f"DNSRecon process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            
            if not results["dns_records"]:
                return {"error": error_message}
            else:
                results["warning"] = error_message

        # Clean up output file
        try:
            subprocess.run(["rm", "/tmp/dnsrecon_output.json"], check=False)
        except:
            pass

        return results

    except FileNotFoundError:
        return {"error": "DNSRecon command not found. Please ensure dnsrecon is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running dnsrecon: {str(e)}"}


def dnsrecon_standard_scan(domain: str) -> str:
    """
    Performs a standard DNS enumeration scan.

    Args:
        domain: The target domain to scan

    Returns:
        JSON string containing scan results
    """
    result = run_dnsrecon_scan(domain, "std")
    return json.dumps(result, indent=2)


def dnsrecon_bruteforce_scan(
    domain: str,
    wordlist: str = "/usr/share/wordlists/dnsrecon.txt"
) -> str:
    """
    Performs a DNS brute force scan for subdomains.

    Args:
        domain: The target domain to scan
        wordlist: Path to wordlist file for brute forcing

    Returns:
        JSON string containing scan results
    """
    options = ["-D", wordlist] if wordlist else []
    result = run_dnsrecon_scan(domain, "brt", options)
    return json.dumps(result, indent=2)


def dnsrecon_axfr_scan(domain: str) -> str:
    """
    Attempts a DNS zone transfer (AXFR).

    Args:
        domain: The target domain to scan

    Returns:
        JSON string containing scan results
    """
    result = run_dnsrecon_scan(domain, "axfr")
    return json.dumps(result, indent=2)


def dnsrecon_reverse_lookup(ip_range: str) -> str:
    """
    Performs reverse DNS lookups on an IP range.

    Args:
        ip_range: IP range to perform reverse lookup on (e.g., "192.168.1.0/24")

    Returns:
        JSON string containing scan results
    """
    options = ["-r", ip_range]
    result = run_dnsrecon_scan("", "rvl", options)
    return json.dumps(result, indent=2)


def dnsrecon_srv_scan(domain: str) -> str:
    """
    Enumerates SRV records for common services.

    Args:
        domain: The target domain to scan

    Returns:
        JSON string containing scan results
    """
    result = run_dnsrecon_scan(domain, "srv")
    return json.dumps(result, indent=2)


def dnsrecon_comprehensive_scan(domain: str) -> str:
    """
    Performs a comprehensive DNS enumeration including multiple scan types.

    Args:
        domain: The target domain to scan

    Returns:
        JSON string containing combined scan results
    """
    results = {
        "domain": domain,
        "scans": {}
    }
    
    # Standard enumeration
    std_result = run_dnsrecon_scan(domain, "std")
    results["scans"]["standard"] = std_result
    
    # Zone transfer attempt
    axfr_result = run_dnsrecon_scan(domain, "axfr")
    results["scans"]["zone_transfer"] = axfr_result
    
    # SRV records
    srv_result = run_dnsrecon_scan(domain, "srv")
    results["scans"]["srv_records"] = srv_result
    
    return json.dumps(results, indent=2)


if __name__ == '__main__':
    # Example usage
    print("Testing DNSRecon tool...")
    
    # Test standard scan
    test_domain = "google.com"
    print(f"\nTesting standard DNS scan on {test_domain}")
    std_results = dnsrecon_standard_scan(test_domain)
    print("Standard scan results:")
    print(std_results)
    
    # Test zone transfer
    print(f"\nTesting zone transfer on {test_domain}")
    axfr_results = dnsrecon_axfr_scan(test_domain)
    print("Zone transfer results:")
    print(axfr_results)
    
    # Test SRV scan
    print(f"\nTesting SRV scan on {test_domain}")
    srv_results = dnsrecon_srv_scan(test_domain)
    print("SRV scan results:")
    print(srv_results)