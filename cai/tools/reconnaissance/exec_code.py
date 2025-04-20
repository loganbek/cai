"""
Tool for executing code via LLM tool calls.
"""
# Standard library imports
import os
import subprocess
from typing import Optional

# Local imports
from cai.tools.common import run_command, _get_workspace_dir, _get_container_workspace_path  # pylint: disable=import-error
def execute_code(code: str = "", language: str = "python",
                filename: str = "exploit", timeout: int = 100, ctf=None) -> str:
    """
    Create a file with code, store it and execute it, or execute an existing file.

    This tool allows for executing code provided in different
    programming languages. It creates a permanent file with the provided code
    and executes it using the appropriate interpreter. You can exec this
    code as many times as you want using `generic_linux_command` tool.

    If only a filename is provided (without code), the tool will execute
    the existing file with that name.

    Priorize: Python and Perl

    Args:
        code: The code snippet to execute. If empty, will execute an existing file.
        language: Programming language to use (default: python)
        filename: Base name for the file without extension (default: exploit)
        timeout: Timeout for the execution (default: 100 seconds)
                Use high timeout for long running code 
                Use low timeout for short running code
    Returns:
        Command output or error message from execution
    """

    # Map file extensions
    extensions = {
        "python": "py",
        "php": "php",
        "bash": "sh",
        "ruby": "rb",
        "perl": "pl",
        "golang": "go",
        "javascript": "js",
        "typescript": "ts",
        "rust": "rs",
        "csharp": "cs",
        "java": "java",
        "kotlin": "kt",
        "solidity": "sol"
    }
    ext = extensions.get(language.lower(), "txt")
    full_filename = f"{filename}.{ext}"

    # Check if running in a Docker container
    active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")
    
    # Determine the correct workspace path (host or container)
    if active_container:
        # Running in a container environment
        workspace_path = _get_container_workspace_path()
    else:
        # Running on the host system
        workspace_path = _get_workspace_dir()

    # Construct the full path for the code file
    code_file_path = os.path.join(workspace_path, full_filename)

    # If code is provided, create a new file
    if code:
        try:
            # Create directory if it doesn't exist
            os.makedirs(workspace_path, exist_ok=True)
            
            # Write code directly to file using Python's file operations
            # This avoids shell escaping issues
            with open(code_file_path, 'w', encoding='utf-8') as f:
                f.write(code)
                
            result = "File created successfully"
        except Exception as e:
            return f"Failed to create code file '{code_file_path}': {str(e)}"
    else:
        # If no code is provided, check if the file exists
        file_exists = run_command(f"[ -f '{code_file_path}' ] && echo 'exists' || echo 'not found'", ctf=ctf).strip()
        if file_exists != "exists":
            return f"No code provided and file '{code_file_path}' does not exist."

    # Determine command to execute based on language, using workspace_path
    if language.lower() == "python":
        exec_cmd = f"python3 '{code_file_path}'"
    elif language.lower() == "php":
        exec_cmd = f"php '{code_file_path}'"
    elif language.lower() in ["bash", "sh"]:
        # Ensure the script is executable first
        run_command(f"chmod +x '{code_file_path}'", ctf=ctf)
        exec_cmd = f"bash '{code_file_path}'"
    elif language.lower() == "ruby":
        exec_cmd = f"ruby '{code_file_path}'"
    elif language.lower() == "perl":
        exec_cmd = f"perl '{code_file_path}'"
    elif language.lower() == "golang" or language.lower() == "go":
        temp_dir = f"/tmp/go_exec_{filename}"
        run_command(f"mkdir -p {temp_dir}", ctf=ctf)
        # Copy the file using its full path
        run_command(f"cp '{code_file_path}' {temp_dir}/main.go", ctf=ctf)
        run_command(f"cd {temp_dir} && go mod init temp", ctf=ctf)
        exec_cmd = f"cd {temp_dir} && go run main.go"
    elif language.lower() == "javascript":
        exec_cmd = f"node '{code_file_path}'"
    elif language.lower() == "typescript":
        # Ensure ts-node is installed (best effort warning)
        # print("[Warning] Ensure 'ts-node' and 'typescript' are installed in the execution environment.")
        exec_cmd = f"ts-node '{code_file_path}'"
    elif language.lower() == "rust":
        # For Rust, we need to compile first
        # Compile in the workspace directory
        compile_cmd = f"rustc '{code_file_path}' -o '{os.path.join(workspace_path, filename)}'"
        compile_result = run_command(compile_cmd, ctf=ctf)
        if "error" in compile_result.lower():
            return f"Rust compilation failed: {compile_result}"
        exec_cmd = f"'{os.path.join(workspace_path, filename)}'" # Execute the compiled binary from workspace
    elif language.lower() == "csharp":
        # For C#, compile with dotnet
        # This assumes a project structure might be needed. A simple script might fail.
        # For simplicity, let's try running directly if possible, else build/run
        # This might require a .csproj file in the workspace.
        # Trying run directly first:
        exec_cmd = f"dotnet run --project '{workspace_path}' '{code_file_path}'" # Specify project context
        # Fallback or more complex build logic might be needed here.
        # print("[Warning] C# execution might require a .csproj file in the workspace.")
    elif language.lower() == "java":
        # For Java, compile first
        compile_cmd = f"javac '{code_file_path}'"
        compile_result = run_command(compile_cmd, ctf=ctf)
        if "error" in compile_result.lower():
            return f"Java compilation failed: {compile_result}"
        # Execute using the class name (filename) within the workspace context
        exec_cmd = f"java -cp '{workspace_path}' {filename}"
    elif language.lower() == "kotlin":
        # For Kotlin, compile first
        jar_path = os.path.join(workspace_path, f"{filename}.jar")
        compile_cmd = f"kotlinc '{code_file_path}' -include-runtime -d '{jar_path}'"
        compile_result = run_command(compile_cmd, ctf=ctf)
        if "error" in compile_result.lower():
            return f"Kotlin compilation failed: {compile_result}"
        exec_cmd = f"java -jar '{jar_path}'"
    elif language.lower() == "solidity":
        # For Solidity, compile with solc
        build_dir = os.path.join(workspace_path, f"{filename}_build")
        run_command(f"mkdir -p '{build_dir}'", ctf=ctf)
        # Ensure npx and solc are available
        exec_cmd = f"npx solc --bin --abi --optimize -o '{build_dir}' '{code_file_path}'"
    else:
        return f"Unsupported language: {language}"

    # Execute the command and return output
    output = run_command(exec_cmd, ctf=ctf, timeout=timeout)

    return output
