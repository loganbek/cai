"""
Feroxbuster tool for fast content discovery written in Rust.
"""
import subprocess
import json
from typing import List, Dict, Optional


def run_feroxbuster_scan(
    target_url: str,
    wordlist: str = "/usr/share/wordlists/dirb/common.txt",
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs feroxbuster against the specified target URL for content discovery.

    Args:
        target_url: The target URL to scan (e.g., "http://example.com").
        wordlist: Path to the wordlist file for brute forcing.
        options: Optional list of feroxbuster command-line options
                 (e.g., ["-x", "php,html,txt"], ["-t", "50"]).

    Returns:
        A dictionary containing discovered content or an error message.
    """
    if not target_url:
        return {"error": "No target URL specified for feroxbuster scan."}

    command = ["feroxbuster", "-u", target_url, "-w", wordlist]

    if options:
        command.extend(options)

    # Add JSON output and quiet mode for better parsing
    if "--json" not in command and "-j" not in command:
        command.append("--json")
    if "--quiet" not in command and "-q" not in command:
        command.append("--quiet")

    try:
        print(f"Running Feroxbuster command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        results = {"discovered_content": []}

        # Parse JSON output from stdout
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        if data.get("type") == "response":
                            results["discovered_content"].append({
                                "url": data.get("url"),
                                "status": data.get("status"),
                                "content_length": data.get("content_length"),
                                "line_count": data.get("line_count"),
                                "word_count": data.get("word_count"),
                                "method": data.get("method"),
                                "wildcard": data.get("wildcard", False)
                            })
                    except json.JSONDecodeError:
                        # If not JSON, try to parse as text output
                        if " " in line and any(code in line for code in ["200", "301", "302", "403", "404", "500"]):
                            parts = line.split()
                            if len(parts) >= 3:
                                status = parts[0]
                                size = parts[1] if parts[1].isdigit() else None
                                url = parts[-1]
                                results["discovered_content"].append({
                                    "url": url,
                                    "status": status,
                                    "content_length": size,
                                    "method": "GET",
                                    "wildcard": False
                                })

        if process.returncode != 0:
            error_message = f"Feroxbuster process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            
            if not results["discovered_content"]:
                return {"error": error_message}
            else:
                results["warning"] = error_message

        return results

    except FileNotFoundError:
        return {"error": "Feroxbuster command not found. Please ensure feroxbuster is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running feroxbuster: {str(e)}"}


def feroxbuster_scan(
    target_url: str,
    wordlist: str = "/usr/share/wordlists/dirb/common.txt",
    extensions: str = "",
    threads: int = 50,
    depth: int = 4,
    status_codes: str = "200,204,301,302,307,308,401,403,405,500"
) -> str:
    """
    Main feroxbuster scanning function for CAI integration.

    Args:
        target_url: The target URL to scan
        wordlist: Path to wordlist file
        extensions: File extensions to search for (comma-separated)
        threads: Number of concurrent threads
        depth: Maximum recursion depth
        status_codes: HTTP status codes to include (comma-separated)

    Returns:
        JSON string containing scan results
    """
    options = ["-t", str(threads), "-d", str(depth), "-s", status_codes]
    
    if extensions:
        options.extend(["-x", extensions])

    # Add some useful default options
    options.extend([
        "--auto-tune",      # Automatically tune scan speed
        "--auto-bail",      # Stop scanning after certain amount of errors
        "--smart"           # Smart filtering based on content length
    ])

    result = run_feroxbuster_scan(target_url, wordlist, options)
    return json.dumps(result, indent=2)


def feroxbuster_recursive_scan(
    target_url: str,
    wordlist: str = "/usr/share/wordlists/dirb/common.txt",
    extensions: str = "php,html,txt,js,css",
    max_depth: int = 3
) -> str:
    """
    Feroxbuster recursive scanning with common web extensions.

    Args:
        target_url: The target URL to scan
        wordlist: Path to wordlist file
        extensions: File extensions to search for (comma-separated)
        max_depth: Maximum recursion depth

    Returns:
        JSON string containing scan results
    """
    options = [
        "-t", "100",                    # High thread count for faster scanning
        "-d", str(max_depth),           # Recursion depth
        "-x", extensions,               # File extensions
        "--auto-tune",                  # Auto-tune performance
        "--smart",                      # Smart filtering
        "-s", "200,204,301,302,307,308,401,403,405,500",  # Status codes
        "-C", "404"                     # Filter out 404s
    ]

    result = run_feroxbuster_scan(target_url, wordlist, options)
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    # Example usage
    print("Testing Feroxbuster tool...")
    
    # Test basic scanning
    test_url = "http://testphp.vulnweb.com"
    print(f"\nTesting feroxbuster scan on {test_url}")
    results = feroxbuster_scan(test_url, extensions="php,html,txt")
    print("Feroxbuster scan results:")
    print(results)
    
    # Test recursive scanning
    print(f"\nTesting recursive feroxbuster scan on {test_url}")
    recursive_results = feroxbuster_recursive_scan(test_url)
    print("Recursive scan results:")
    print(recursive_results)