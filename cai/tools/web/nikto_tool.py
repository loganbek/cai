"""
Nikto web server scanner tool.
"""
import subprocess
import json
from typing import List, Dict, Optional
import tempfile
import os

def run_nikto_scan(
    target_url: str, 
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs a Nikto scan against the specified target URL.

    Args:
        target_url: The target URL to scan (e.g., "http://example.com" or "https://example.com:443").
                    Nikto typically requires the protocol.
        options: Optional list of other Nikto command-line options
                 (e.g., ["-Tuning", "x 6"], ["-mutate", "1"]).
                 The -Format json and -o (output file) flags are handled by this function.

    Returns:
        A dictionary containing the parsed Nikto scan results or an error message.
    """
    if not target_url:
        return {"error": "No target URL specified for Nikto scan."}

    # Validate target_url format (basic check)
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        return {"error": "Invalid target URL format. Nikto requires protocol (http:// or https://)."}
    
    # Nikto requires -h (host) or -url. We'll use -url for clarity with full URLs.
    # However, some versions/setups prefer -h and -p for SSL. Let's try to be robust.
    # A common way is to specify the host with -h and optionally -ssl if https.
    # For simplicity and modern Nikto, -h <full_url_including_protocol> often works.
    # Let's use -h <host_or_ip> and -port <port> and -ssl if https for better compatibility.
    
    from urllib.parse import urlparse
    parsed_url = urlparse(target_url)
    host = parsed_url.hostname
    port = str(parsed_url.port if parsed_url.port else (443 if parsed_url.scheme == 'https' else 80))

    if not host:
        return {"error": "Could not parse hostname from target URL."}

    command = ["nikto", "-h", host, "-p", port]

    if parsed_url.scheme == 'https':
        command.append("-ssl")

    # Use a temporary file for JSON output as Nikto's direct stdout for JSON can be tricky
    # or mixed with other informational messages.
    temp_output_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") # Changed to w for text mode
    temp_output_filename = temp_output_file.name
    temp_output_file.close() # Close it so Nikto can write to it

    command.extend(["-Format", "json", "-o", temp_output_filename])

    if options:
        # Filter out any user-supplied format or output options to avoid conflict
        safe_options = [opt for opt in options if not opt.lower().startswith( (
            "-f", "-format", "-o", "-output"
        ) )]
        command.extend(safe_options)
    
    # Nikto can take a while, consider adding a timeout option if this function is called in a blocking way.
    # For now, no explicit timeout in subprocess.run

    try:
        print(f"Running Nikto command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)
        
        scan_results = {}
        # Read the JSON output from the temporary file
        if os.path.exists(temp_output_filename):
            with open(temp_output_filename, 'r', encoding='utf-8') as f:
                try:
                    # Nikto JSON output is typically a single JSON object (or array for multiple hosts)
                    # For single target, it should be a dictionary.
                    scan_results = json.load(f)
                except json.JSONDecodeError as e:
                    # If JSON is empty or malformed, provide context
                    file_content_sample = ""
                    try:
                        with open(temp_output_filename, 'r', encoding='utf-8') as f_err:
                            file_content_sample = f_err.read(500) # Read a sample for debugging
                    except Exception as read_err:
                        file_content_sample = f"(Could not read temp file: {read_err})"
                    return {
                        "error": f"Failed to parse Nikto JSON output from {temp_output_filename}. Error: {e}",
                        "nikto_stderr": process.stderr.strip() if process.stderr else "",
                        "nikto_stdout_raw": process.stdout.strip() if process.stdout else "", # Nikto might print summary to stdout
                        "file_content_sample": file_content_sample
                    }
        else:
            return {"error": f"Nikto output file {temp_output_filename} not found.", 
                    "nikto_stderr": process.stderr.strip() if process.stderr else "",
                    "nikto_stdout_raw": process.stdout.strip() if process.stdout else ""}

        if process.returncode != 0:
            # Nikto might exit non-zero even if some results are found (e.g. if scan is interrupted or some checks fail)
            # We already tried to parse the JSON, so add a warning.
            warning_message = f"Nikto process exited with error code {process.returncode}."
            if process.stderr:
                warning_message += f" Stderr: {process.stderr.strip()}"
            if isinstance(scan_results, dict): # if we have a dict, add warning to it
                scan_results["warning_nikto_execution"] = warning_message
            else: # if scan_results is not a dict (e.g. parsing failed and returned an error dict)
                return {"error": warning_message, "parsed_output": scan_results} 

        # Include raw stdout from Nikto as it might contain summary info not in JSON
        if process.stdout and isinstance(scan_results, dict):
            scan_results["nikto_stdout_summary"] = process.stdout.strip()

        return scan_results

    except FileNotFoundError:
        return {"error": "Nikto command not found. Please ensure Nikto is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running Nikto: {str(e)}"}
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_output_filename):
            try:
                os.remove(temp_output_filename)
            except Exception as e_remove:
                print(f"Warning: Could not remove temporary Nikto output file {temp_output_filename}: {e_remove}")

if __name__ == '__main__':
    # Example Usage (requires Nikto to be installed)
    # Replace with a target you are authorized to scan.
    # Nikto's own test CGI scripts are often at http://cirt.net/nikto/nikto-current/support/test/mutillidae/ (if available)
    # Or use a locally hosted test environment.
    # For a very basic, non-intrusive test against a public site (use with caution and ensure authorization):
    # test_target = "http://example.com" # Very basic, likely few findings
    # A more interesting target for Nikto might be a deliberately vulnerable app, or a complex web server.
    # Using scanme.nmap.org for Nikto is less ideal as it's more for Nmap, but can show basic server info.
    
    print("Starting Nikto tool example...")
    # It's better to test Nikto against a server you control or have explicit permission for.
    # For this example, let's assume you have a local web server for testing, e.g., http://localhost
    # If not, this example might not yield many interesting results or could be slow.
    test_target = "http://localhost" # Replace if you have a better test target
    # test_target = "http://scanme.nmap.org" # Use with caution, check scanme.nmap.org policies

    print(f"\nScanning target: {test_target} with Nikto")
    # Nikto can be verbose on stdout even when outputting to a file, subprocess.PIPE captures this.
    results = run_nikto_scan(test_target)
    print("Nikto Scan Results:")
    print(json.dumps(results, indent=2))

    # Example with options (e.g., specific tuning)
    # Tuning options: https://cirt.net/nikto2-docs/options.html#-tuning
    # 0 File Upload
    # 1 Interesting File / Seen in logs
    # 2 Misconfiguration / Default File
    # 3 Information Disclosure
    # 4 Injection (XSS/Script/HTML)
    # 5 Remote File Retrieval - Inside Web Root
    # 6 Denial of Service
    # 7 Remote File Retrieval - Server Wide
    # 8 Command Execution / Remote Shell
    # 9 SQL Injection
    # a Authentication Bypass
    # b Software Identification
    # c Remote Source Inclusion
    # x Reverse Tuning Options (i.e., 01236ab will test for all except XSS, RFI and RCE)
    # test_options = ["-Tuning", "x 6"] # Example: Run all checks except DoS
    # print(f"\nScanning target: {test_target} with Nikto options: {test_options}")
    # results_options = run_nikto_scan(test_target, options=test_options)
    # print("Nikto Scan Results (with options):")
    # print(json.dumps(results_options, indent=2))

    # Test with an HTTPS target if you have one available for testing
    # test_target_https = "https://your-test-https-site.com"
    # if test_target_https != "https://your-test-https-site.com": # Basic check if it was changed
    #     print(f"\nScanning HTTPS target: {test_target_https} with Nikto")
    #     results_https = run_nikto_scan(test_target_https)
    #     print("Nikto Scan Results (HTTPS):")
    #     print(json.dumps(results_https, indent=2))
    # else:
    #     print("\nSkipping HTTPS test, please set a valid test_target_https if desired.")
