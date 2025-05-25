"""
LinPEAS (Linux Privilege Escalation Awesome Script) execution tool.
"""
import subprocess
from typing import List, Dict, Optional
import os

def run_linpeas(
    script_path: str, 
    options: Optional[List[str]] = None, 
    output_file_path: Optional[str] = None
) -> Dict:
    """
    Runs a LinPEAS script and captures its output.

    Args:
        script_path: Absolute path to the LinPEAS script (e.g., linpeas.sh).
        options: Optional list of command-line options for LinPEAS.
        output_file_path: Optional path to save the raw output of LinPEAS.

    Returns:
        A dictionary containing:
            - "status": "success" or "error"
            - "raw_output": The raw stdout from LinPEAS (can be very large).
            - "error_message": Error details if status is "error".
            - "output_saved_to": Path to the saved output file, if provided.
    """
    if not os.path.exists(script_path) or not os.access(script_path, os.X_OK):
        return {
            "status": "error", 
            "error_message": f"LinPEAS script not found at {script_path} or not executable."
        }

    command = [script_path]
    if options:
        command.extend(options)

    try:
        print(f"Running LinPEAS command: {' '.join(command)}")
        # LinPEAS can produce a very large amount of output.
        # Consider implications for memory if capturing all to raw_output directly without streaming.
        process = subprocess.run(command, capture_output=True, text=True, check=False, encoding='utf-8', errors='replace')

        raw_output = process.stdout
        stderr_output = process.stderr

        result = {
            "status": "success",
            "raw_output": raw_output # Potentially very large
        }

        if output_file_path:
            try:
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(raw_output)
                result["output_saved_to"] = output_file_path
            except Exception as e:
                result["save_error"] = f"Failed to save LinPEAS output to {output_file_path}: {str(e)}"

        if process.returncode != 0:
            # LinPEAS might not always exit with 0 even on successful enumeration
            result["warning_linpeas_execution"] = f"LinPEAS process exited with code {process.returncode}."
            if stderr_output:
                 result["warning_linpeas_execution"] += f" Stderr: {stderr_output.strip()}"
        
        if stderr_output and not result.get("warning_linpeas_execution"):
            result["stderr_info"] = stderr_output.strip()

        return result

    except FileNotFoundError:
        return {"status": "error", "error_message": f"Script {script_path} not found. Ensure it's a valid path."}
    except Exception as e:
        return {"status": "error", "error_message": f"An unexpected error occurred while running LinPEAS: {str(e)}"}

if __name__ == '__main__':
    print("Starting LinPEAS tool example...")
    # This example assumes linpeas.sh is available and executable at the specified path.
    # You need to download linpeas.sh from https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS
    # and place it in a known location.
    # For testing, you might run it on a test Linux VM.
    # Replace '/path/to/linpeas.sh' with the actual path to your linpeas.sh script.
    linpeas_script_location = "/tmp/linpeas.sh" # EXAMPLE PATH - REPLACE THIS
    
    if not os.path.exists(linpeas_script_location):
        print(f"LinPEAS script not found at {linpeas_script_location}. Download it and update the path to run this example.")
    else:
        print(f"Attempting to run LinPEAS from: {linpeas_script_location}")
        # Basic run, saving output to a file
        results = run_linpeas(linpeas_script_location, output_file_path="/tmp/linpeas_output.txt")
        print("LinPEAS Scan Results:")
        if results["status"] == "success":
            print(f"LinPEAS ran successfully.")
            if "output_saved_to" in results:
                print(f"Output saved to: {results['output_saved_to']}")
            # print("First 1000 chars of output:")
            # print(results["raw_output"][:1000]) # Print only a snippet as it can be huge
        else:
            print(f"LinPEAS failed: {results['error_message']}")
