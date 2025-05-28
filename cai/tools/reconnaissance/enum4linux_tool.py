"""
Enum4linux tool for SMB and Windows enumeration.
"""
import subprocess
import json
from typing import List, Dict, Optional


def run_enum4linux_scan(
    target: str,
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs enum4linux against the specified target for SMB/Windows enumeration.

    Args:
        target: The target IP address or hostname to enumerate.
        options: Optional list of enum4linux command-line options.

    Returns:
        A dictionary containing enumeration results or an error message.
    """
    if not target:
        return {"error": "No target specified for enum4linux scan."}

    command = ["enum4linux"]

    if options:
        command.extend(options)
    
    command.append(target)

    try:
        print(f"Running Enum4linux command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=300)

        results = {
            "target": target,
            "workgroup_domain": None,
            "os_info": None,
            "users": [],
            "groups": [],
            "shares": [],
            "policies": [],
            "printers": [],
            "raw_output": process.stdout
        }

        if process.stdout:
            lines = process.stdout.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                # Parse workgroup/domain info
                if "Domain Name:" in line:
                    results["workgroup_domain"] = line.split("Domain Name:")[-1].strip()
                elif "Workgroup:" in line:
                    if not results["workgroup_domain"]:
                        results["workgroup_domain"] = line.split("Workgroup:")[-1].strip()
                
                # Parse OS information
                if "OS name:" in line or "OS version:" in line:
                    if not results["os_info"]:
                        results["os_info"] = {}
                    if "OS name:" in line:
                        results["os_info"]["name"] = line.split("OS name:")[-1].strip()
                    elif "OS version:" in line:
                        results["os_info"]["version"] = line.split("OS version:")[-1].strip()
                
                # Identify sections
                if "Getting the global users list" in line:
                    current_section = "users"
                elif "Getting the group list" in line:
                    current_section = "groups"
                elif "Getting the available shares" in line:
                    current_section = "shares"
                elif "Getting the password policy" in line:
                    current_section = "policies"
                elif "Getting the printer list" in line:
                    current_section = "printers"
                
                # Parse users
                if current_section == "users" and line.startswith("user:"):
                    user_info = line.replace("user:", "").strip()
                    if user_info:
                        results["users"].append(user_info)
                
                # Parse groups
                if current_section == "groups" and line.startswith("group:"):
                    group_info = line.replace("group:", "").strip()
                    if group_info:
                        results["groups"].append(group_info)
                
                # Parse shares
                if current_section == "shares" and "\t" in line and not line.startswith("index"):
                    parts = [part.strip() for part in line.split('\t') if part.strip()]
                    if len(parts) >= 2:
                        share_name = parts[0]
                        share_type = parts[1] if len(parts) > 1 else "Unknown"
                        comment = parts[2] if len(parts) > 2 else ""
                        results["shares"].append({
                            "name": share_name,
                            "type": share_type,
                            "comment": comment
                        })

        if process.returncode != 0:
            error_message = f"Enum4linux process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            
            if not any([results["users"], results["groups"], results["shares"]]):
                return {"error": error_message}
            else:
                results["warning"] = error_message

        return results

    except subprocess.TimeoutExpired:
        return {"error": "Enum4linux scan timed out after 5 minutes."}
    except FileNotFoundError:
        return {"error": "Enum4linux command not found. Please ensure enum4linux is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running enum4linux: {str(e)}"}


def enum4linux_basic_scan(target: str) -> str:
    """
    Performs a basic enum4linux scan.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing scan results
    """
    options = ["-a"]  # All simple enumeration
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_user_enumeration(target: str) -> str:
    """
    Focuses on user enumeration.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing user enumeration results
    """
    options = ["-U"]  # User enumeration
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_share_enumeration(target: str) -> str:
    """
    Focuses on share enumeration.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing share enumeration results
    """
    options = ["-S"]  # Share enumeration
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_group_enumeration(target: str) -> str:
    """
    Focuses on group enumeration.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing group enumeration results
    """
    options = ["-G"]  # Group enumeration
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_policy_enumeration(target: str) -> str:
    """
    Focuses on password policy enumeration.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing policy enumeration results
    """
    options = ["-P"]  # Password policy enumeration
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_comprehensive_scan(target: str) -> str:
    """
    Performs a comprehensive enum4linux scan with all options.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing comprehensive scan results
    """
    options = ["-a", "-v"]  # All enumeration with verbose output
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


def enum4linux_null_session_scan(target: str) -> str:
    """
    Attempts enumeration using null sessions.

    Args:
        target: The target IP address or hostname to scan

    Returns:
        JSON string containing scan results
    """
    options = ["-a", "-u", "", "-p", ""]  # Null session attempt
    result = run_enum4linux_scan(target, options)
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    # Example usage
    print("Testing Enum4linux tool...")
    
    # Test basic scan (using a known Windows test target or localhost)
    test_target = "127.0.0.1"  # Replace with actual target for testing
    print(f"\nTesting basic enum4linux scan on {test_target}")
    basic_results = enum4linux_basic_scan(test_target)
    print("Basic scan results:")
    print(basic_results)
    
    # Test user enumeration
    print(f"\nTesting user enumeration on {test_target}")
    user_results = enum4linux_user_enumeration(test_target)
    print("User enumeration results:")
    print(user_results)
    
    # Test share enumeration
    print(f"\nTesting share enumeration on {test_target}")
    share_results = enum4linux_share_enumeration(test_target)
    print("Share enumeration results:")
    print(share_results)