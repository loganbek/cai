"""
Hashcat tool for password cracking and hash analysis.
"""
import subprocess
import json
import os
from typing import List, Dict, Optional


def run_hashcat_crack(
    hash_file: str,
    wordlist: str,
    hash_type: str = "0",
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs hashcat for password cracking.

    Args:
        hash_file: Path to file containing hashes to crack.
        wordlist: Path to wordlist file for cracking.
        hash_type: Hashcat hash type number (e.g., "0" for MD5, "1000" for NTLM).
        options: Optional list of hashcat command-line options.

    Returns:
        A dictionary containing cracking results or an error message.
    """
    if not hash_file or not os.path.exists(hash_file):
        return {"error": f"Hash file not found: {hash_file}"}
    
    if not wordlist or not os.path.exists(wordlist):
        return {"error": f"Wordlist file not found: {wordlist}"}

    command = ["hashcat", "-m", hash_type, "-a", "0", hash_file, wordlist]

    if options:
        command.extend(options)

    # Add useful default options for non-interactive mode
    default_options = [
        "--potfile-disable",     # Don't use potfile to avoid conflicts
        "--quiet",               # Reduce output
        "--status",              # Show status
        "--status-timer=30"      # Status update interval
    ]
    
    for opt in default_options:
        if opt not in command:
            command.append(opt)

    try:
        print(f"Running Hashcat command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=600)

        results = {
            "hash_type": hash_type,
            "hash_file": hash_file,
            "wordlist": wordlist,
            "cracked_hashes": [],
            "status": "completed"
        }

        # Parse cracked hashes from output
        if process.stdout:
            for line in process.stdout.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('[') and not line.startswith('Session'):
                    # Format: hash:password
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        results["cracked_hashes"].append({
                            "hash": parts[0],
                            "password": parts[1]
                        })

        # Check if hashcat found the potfile and extract results
        try:
            # Also check for results in current directory
            for filename in os.listdir('.'):
                if filename.endswith('.potfile') or filename == 'hashcat.potfile':
                    with open(filename, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if ':' in line:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    # Avoid duplicates
                                    if not any(h["hash"] == parts[0] for h in results["cracked_hashes"]):
                                        results["cracked_hashes"].append({
                                            "hash": parts[0],
                                            "password": parts[1]
                                        })
        except:
            pass

        if process.returncode != 0:
            if process.returncode == 1:
                results["status"] = "exhausted"  # Wordlist exhausted
            else:
                error_message = f"Hashcat process exited with error code {process.returncode}."
                if process.stderr:
                    error_message += f" Stderr: {process.stderr.strip()}"
                
                if not results["cracked_hashes"]:
                    return {"error": error_message}
                else:
                    results["warning"] = error_message

        return results

    except subprocess.TimeoutExpired:
        return {"error": "Hashcat process timed out after 10 minutes."}
    except FileNotFoundError:
        return {"error": "Hashcat command not found. Please ensure hashcat is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running hashcat: {str(e)}"}


def hashcat_identify_hash(hash_value: str) -> str:
    """
    Attempts to identify the hash type using hashcat's hash identification.

    Args:
        hash_value: The hash to identify

    Returns:
        JSON string containing possible hash types
    """
    # Create temporary file with hash
    temp_file = "/tmp/temp_hash.txt"
    try:
        with open(temp_file, 'w') as f:
            f.write(hash_value)
        
        # Try common hash types
        common_hash_types = {
            "0": "MD5",
            "100": "SHA1",
            "1000": "NTLM",
            "1400": "SHA256",
            "1700": "SHA512",
            "3200": "bcrypt",
            "1800": "sha512crypt",
            "500": "md5crypt"
        }
        
        results = {
            "hash": hash_value,
            "possible_types": [],
            "length": len(hash_value)
        }
        
        # Basic identification based on length and format
        hash_len = len(hash_value)
        if hash_len == 32 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
            results["possible_types"].append({"type": "0", "name": "MD5"})
        elif hash_len == 40 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
            results["possible_types"].append({"type": "100", "name": "SHA1"})
        elif hash_len == 64 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
            results["possible_types"].append({"type": "1400", "name": "SHA256"})
        elif hash_len == 128 and all(c in '0123456789abcdefABCDEF' for c in hash_value):
            results["possible_types"].append({"type": "1700", "name": "SHA512"})
        elif hash_len == 32 and ':' not in hash_value:
            results["possible_types"].append({"type": "1000", "name": "NTLM"})
        
        return json.dumps(results, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Error identifying hash: {str(e)}"}, indent=2)
    finally:
        try:
            os.remove(temp_file)
        except:
            pass


def hashcat_crack_md5(hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
    """
    Cracks MD5 hashes using hashcat.

    Args:
        hash_file: Path to file containing MD5 hashes
        wordlist: Path to wordlist file

    Returns:
        JSON string containing cracking results
    """
    result = run_hashcat_crack(hash_file, wordlist, "0")
    return json.dumps(result, indent=2)


def hashcat_crack_ntlm(hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
    """
    Cracks NTLM hashes using hashcat.

    Args:
        hash_file: Path to file containing NTLM hashes
        wordlist: Path to wordlist file

    Returns:
        JSON string containing cracking results
    """
    result = run_hashcat_crack(hash_file, wordlist, "1000")
    return json.dumps(result, indent=2)


def hashcat_crack_sha256(hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
    """
    Cracks SHA256 hashes using hashcat.

    Args:
        hash_file: Path to file containing SHA256 hashes
        wordlist: Path to wordlist file

    Returns:
        JSON string containing cracking results
    """
    result = run_hashcat_crack(hash_file, wordlist, "1400")
    return json.dumps(result, indent=2)


def hashcat_crack_sha1(hash_file: str, wordlist: str = "/usr/share/wordlists/rockyou.txt") -> str:
    """
    Cracks SHA1 hashes using hashcat.

    Args:
        hash_file: Path to file containing SHA1 hashes
        wordlist: Path to wordlist file

    Returns:
        JSON string containing cracking results
    """
    result = run_hashcat_crack(hash_file, wordlist, "100")
    return json.dumps(result, indent=2)


def hashcat_benchmark() -> str:
    """
    Runs hashcat benchmark to test performance.

    Returns:
        JSON string containing benchmark results
    """
    try:
        command = ["hashcat", "-b", "--quiet"]
        process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=120)
        
        results = {
            "benchmark_completed": process.returncode == 0,
            "output": process.stdout,
            "error": process.stderr if process.stderr else None
        }
        
        return json.dumps(results, indent=2)
        
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Hashcat benchmark timed out"}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error running benchmark: {str(e)}"}, indent=2)


if __name__ == '__main__':
    # Example usage
    print("Testing Hashcat tool...")
    
    # Test hash identification
    test_hash = "5d41402abc4b2a76b9719d911017c592"  # MD5 of "hello"
    print(f"\nTesting hash identification for: {test_hash}")
    id_results = hashcat_identify_hash(test_hash)
    print("Hash identification results:")
    print(id_results)
    
    # Test benchmark
    print("\nTesting hashcat benchmark...")
    benchmark_results = hashcat_benchmark()
    print("Benchmark results:")
    print(benchmark_results)