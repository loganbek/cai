"""
Nuclei web vulnerability scanner tool.
"""
import subprocess
import json
from typing import List, Dict, Optional

def run_nuclei_scan(
    target_urls: List[str],
    templates: Optional[List[str]] = None,
    options: Optional[List[str]] = None
) -> Dict:
    """
    Runs a Nuclei scan against the specified target URLs with given templates and options.

    Args:
        target_urls: A list of URLs to scan.
        templates: Optional list of specific template names, paths, tags, or keywords.
                   (e.g., ["cves", "technologies/nginx.yaml", "critical"]).
                   If None, Nuclei's default/automatic behavior for template selection will be used.
        options: Optional list of other Nuclei command-line options 
                 (e.g., ["-severity", "high,critical"], ["-etags", "intrusive"]).
                 The -jsonl flag is added automatically.

    Returns:
        A dictionary containing a list of findings or an error message.
        Each finding is a dictionary parsed from Nuclei's JSONL output.
    """
    if not target_urls:
        return {"error": "No target URLs specified for Nuclei scan."}

    command = ["nuclei"]

    for url in target_urls:
        command.extend(["-u", url]) # Or -list if providing a file of URLs

    if templates:
        command.extend(["-t", ",".join(templates)]) # -t can take comma-separated templates/paths/tags

    if options:
        # Filter out any user-supplied json output options to avoid conflict
        safe_options = [opt for opt in options if not opt.lower().startswith(("-json", "-jsonl"))]
        command.extend(safe_options)
    
    command.append("-jsonl") # Output in JSONL format

    try:
        print(f"Running Nuclei command: {' '.join(command)}")
        process = subprocess.run(command, capture_output=True, text=True, check=False)

        findings = []
        # Nuclei outputs one JSON object per line for each finding.
        # stderr might contain progress, info, or errors from Nuclei itself.
        
        if process.stdout:
            for line in process.stdout.strip().split('\n'):
                if line:
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse Nuclei JSON line: {line} - Error: {e}")
                        # Optionally, add this malformed line or error to a separate part of the result
        
        result = {"findings": findings}

        if process.returncode != 0:
            error_message = f"Nuclei process exited with error code {process.returncode}."
            if process.stderr:
                error_message += f" Stderr: {process.stderr.strip()}"
            result["warning"] = error_message # Add as warning because some findings might still be present
        elif process.stderr: # Even with success, stderr might have useful info/warnings from Nuclei
            result["info"] = process.stderr.strip()
            
        if not findings and "warning" in result: # If no findings and there was an error
             return {"error": result["warning"], "stderr": process.stderr.strip() if process.stderr else ""}


        return result

    except FileNotFoundError:
        return {"error": "Nuclei command not found. Please ensure Nuclei is installed and in your system PATH."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while running Nuclei: {str(e)}"}

if __name__ == '__main__':
    # Example Usage (requires Nuclei to be installed and a host to scan)
    # Replace 'http://scanme.nmap.org' or 'http://example.com' with a target you are authorized to scan.
    # Using a publicly available, safe test site is recommended.
    # ProjectDiscovery provides http://honey.scanme.sh for safe testing of Nuclei.
    print("Starting Nuclei tool example...")
    
    # Test with a single target known for having some informational findings
    # test_target_urls = ["http://scanme.nmap.org"] 
    test_target_urls = ["http://honey.scanme.sh"] # Official test site from ProjectDiscovery
    
    # Example 1: Basic scan with default templates
    print(f"\nScanning target(s): {test_target_urls} (default templates)")
    results_default = run_nuclei_scan(test_target_urls)
    print("Nuclei Scan Results (Default):")
    print(json.dumps(results_default, indent=2))

    # Example 2: Scan with specific templates (e.g., common exposures, technologies)
    # Ensure these templates/tags exist in your Nuclei template installation
    # test_templates = ["exposures/tokens/generic/plaintext-credentials-in-response.yaml", "technologies"]
    test_templates = ["dns/caa-fingerprint.yaml", "http/technologies/tech-detect.yaml"] # some basic, non-intrusive templates
    print(f"\nScanning target(s): {test_target_urls} with templates: {test_templates}")
    results_specific_templates = run_nuclei_scan(test_target_urls, templates=test_templates)
    print("Nuclei Scan Results (Specific Templates):")
    print(json.dumps(results_specific_templates, indent=2))

    # Example 3: Scan with options (e.g., severity)
    test_options = ["-severity", "info,low"] # Filter by severity
    print(f"\nScanning target(s): {test_target_urls} with options: {test_options}")
    results_with_options = run_nuclei_scan(test_target_urls, options=test_options)
    print("Nuclei Scan Results (With Options):")
    print(json.dumps(results_with_options, indent=2))
    
    # Example 4: Scan multiple targets
    # multi_targets = ["http://honey.scanme.sh", "http://example.com"] # example.com is very basic
    # print(f"\nScanning multiple targets: {multi_targets}")
    # results_multi = run_nuclei_scan(multi_targets, templates=["http/technologies/tech-detect.yaml"])
    # print("Nuclei Scan Results (Multiple Targets):")
    # print(json.dumps(results_multi, indent=2))

    # Example 5: Non-existent target / error handling
    # print(f"\nScanning non_existent_target: http://thisshouldnotexist12345abc.com")
    # error_results = run_nuclei_scan(["http://thisshouldnotexist12345abc.com"], templates=["http/technologies/tech-detect.yaml"])
    # print("Nuclei Scan Results (Error Case):")
    # print(json.dumps(error_results, indent=2))
