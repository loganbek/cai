"""
Gobuster tool for directory/file brute forcing and DNS subdomain enumeration.
"""
import subprocess
import json
from typing import List, Dict, Optional


def run_gobuster_dir(
    target_url: str,
    wordlist: str = "/usr/share/wordlists/dirb/common.txt",
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs gobuster in directory brute force mode against the specified target URL.

    Args:
        target_url: The target URL to scan (e.g., "http://example.com").
        wordlist: Path to the wordlist file for brute forcing.
        options: Optional list of gobuster command-line options
                 (e.g., ["-x", "php,html,txt"], ["-t", "50"]).

    Returns:
        A dictionary containing discovered directories/files or an error message.
    """
    if not target_url:
        return {"error": "No target URL specified for gobuster directory scan."}

    command = ["gobuster", "dir", "-u", target_url, "-w", wordlist]

    if options:
        command.extend(options)

    # Add quiet mode and format options for better parsing
    if "-q" not in command:
        command.append("-q")
    if "-o" not in command and "--output" not in command:
        command.extend(["-o", "/tmp/gobuster_output.txt"])

    try:
        print(f"Running Gobuster command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        results = {"discovered_paths": []}

        # Parse output from stdout
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line and not line.startswith('='):
                    # Gobuster output format: /path (Status: 200) [Size: 1234]
                    parts = line.split()
                    if len(parts) >= 3:
                        path = parts[0]
                        status = None
                        size = None
                        
                        # Extract status code
                        for part in parts:
                            if part.startswith("Status:"):
                                status = part.replace("Status:", "").rstrip(")")
                            elif part.startswith("[Size:"):
                                size = part.replace("[Size:", "").rstrip("]")
                        
                        results["discovered_paths"].append({
                            "path": path,
                            "status": status,
                            "size": size,
                            "full_url": target_url.rstrip('/') + path
                        })

        # Also try to read from output file if it was created
        try:
            with open("/tmp/gobuster_output.txt", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('='):
                        parts = line.split()
                        if len(parts) >= 3:
                            path = parts[0]
                            status = None
                            size = None
                            
                            for part in parts:
                                if part.startswith("Status:"):
                                    status = part.replace("Status:", "").rstrip(")")
                                elif part.startswith("[Size:"):
                                    size = part.replace("[Size:", "").rstrip("]")
                            
                            # Avoid duplicates
                            if not any(p["path"] == path for p in results["discovered_paths"]):
                                results["discovered_paths"].append({
                                    "path": path,
                                    "status": status,
                                    "size": size,
                                    "full_url": target_url.rstrip('/') + path
                                })
        except FileNotFoundError:
            pass

        if process.returncode != 0:
            error_message = f"Gobuster process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            
            if not results["discovered_paths"]:
                return {"error": error_message}
            else:
                results["warning"] = error_message

        # Clean up output file
        try:
            subprocess.run(["rm", "/tmp/gobuster_output.txt"], check=False)
        except:
            pass

        return results

    except FileNotFoundError:
        return {"error": "Gobuster command not found. Please ensure gobuster is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running gobuster: {str(e)}"}


def run_gobuster_dns(
    domain: str,
    wordlist: str = "/usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt",
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs gobuster in DNS subdomain enumeration mode against the specified domain.

    Args:
        domain: The target domain to enumerate subdomains for (e.g., "example.com").
        wordlist: Path to the wordlist file for subdomain enumeration.
        options: Optional list of gobuster command-line options.

    Returns:
        A dictionary containing discovered subdomains or an error message.
    """
    if not domain:
        return {"error": "No domain specified for gobuster DNS enumeration."}

    command = ["gobuster", "dns", "-d", domain, "-w", wordlist]

    if options:
        command.extend(options)

    # Add quiet mode for better parsing
    if "-q" not in command:
        command.append("-q")

    try:
        print(f"Running Gobuster DNS command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        results = {"discovered_subdomains": []}

        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line and "Found:" in line:
                    # Gobuster DNS output format: Found: subdomain.example.com
                    subdomain = line.replace("Found:", "").strip()
                    results["discovered_subdomains"].append({
                        "subdomain": subdomain,
                        "domain": domain
                    })

        if process.returncode != 0:
            error_message = f"Gobuster DNS process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            
            if not results["discovered_subdomains"]:
                return {"error": error_message}
            else:
                results["warning"] = error_message

        return results

    except FileNotFoundError:
        return {"error": "Gobuster command not found. Please ensure gobuster is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running gobuster DNS: {str(e)}"}


def gobuster_dir_scan(
    target_url: str,
    wordlist: str = "/usr/share/wordlists/dirb/common.txt",
    extensions: str = "",
    threads: int = 10,
    status_codes: str = "200,204,301,302,307,403,500"
) -> str:
    """
    Main gobuster directory scanning function for CAI integration.

    Args:
        target_url: The target URL to scan
        wordlist: Path to wordlist file
        extensions: File extensions to search for (comma-separated)
        threads: Number of concurrent threads
        status_codes: HTTP status codes to consider as positive (comma-separated)

    Returns:
        JSON string containing scan results
    """
    options = ["-t", str(threads), "-s", status_codes]
    
    if extensions:
        options.extend(["-x", extensions])

    result = run_gobuster_dir(target_url, wordlist, options)
    return json.dumps(result, indent=2)


def gobuster_dns_scan(
    domain: str,
    wordlist: str = "/usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt",
    threads: int = 10
) -> str:
    """
    Main gobuster DNS scanning function for CAI integration.

    Args:
        domain: The target domain to enumerate
        wordlist: Path to subdomain wordlist file
        threads: Number of concurrent threads

    Returns:
        JSON string containing scan results
    """
    options = ["-t", str(threads)]
    result = run_gobuster_dns(domain, wordlist, options)
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    # Example usage
    print("Testing Gobuster tool...")
    
    # Test directory scanning
    test_url = "http://testphp.vulnweb.com"
    print(f"\nTesting directory scan on {test_url}")
    dir_results = gobuster_dir_scan(test_url, extensions="php,html,txt")
    print("Directory scan results:")
    print(dir_results)
    
    # Test DNS enumeration
    test_domain = "google.com"
    print(f"\nTesting DNS enumeration on {test_domain}")
    dns_results = gobuster_dns_scan(test_domain)
    print("DNS enumeration results:")
    print(dns_results)