"""
This is used to create a generic linux command.
"""
import os
import time
import uuid
import subprocess
import sys
from cai.tools.common import (run_command,
                              list_shell_sessions,
                              get_session_output,
                              terminate_session)  # pylint: disable=import-error # noqa E501
from cai.sdk.agents import function_tool
from wasabi import color  # pylint: disable=import-error


@function_tool
def generic_linux_command(command: str = "",
                          interactive: bool = False,
                          session_id: str = None) -> str:
    """
    Execute commands with session management.

    Use this tool to run any command. The system automatically detects and handles:
    - Regular commands (ls, cat, grep, etc.)
    - Interactive commands that need persistent sessions (ssh, nc, python, etc.)
    - Session management and output capture
    - CTF environments (automatically detected and used when available)
    - Container environments (automatically detected and used when available)
    - SSH environments (automatically detected and used when available)

    Args:
        command: The complete command to execute (e.g., "ls -la", "ssh user@host", "cat file.txt")
        interactive: Set to True for commands that need persistent sessions (ssh, nc, python, ftp etc.)
                    Leave False for regular commands
        session_id: Use existing session ID to send commands to running interactive sessions.
                   Get session IDs from previous interactive command outputs.

    Examples:
        - Regular command: generic_linux_command("ls -la")
        - Interactive command: generic_linux_command("ssh user@host", interactive=True)
        - Send to session: generic_linux_command("pwd", session_id="abc12345")
        - List sessions: generic_linux_command("session list")
        - Kill session: generic_linux_command("session kill abc12345")
        - Environment info: generic_linux_command("env info")

    Environment Detection:
        The system automatically detects and uses the appropriate execution environment:
        - CTF: Commands run in the CTF challenge environment when available
        - Container: Commands run in Docker containers when CAI_ACTIVE_CONTAINER is set
        - SSH: Commands run via SSH when SSH_USER and SSH_HOST are configured
        - Local: Commands run on the local system as fallback

    Returns:
        Command output, session ID for interactive commands, or status message
    """
    # Handle special session management commands
    if command.startswith("session "):
        parts = command.split(" ", 2)
        if len(parts) < 2:
            return "Usage: session list|output|kill [session_id]"
        
        action = parts[1]
        
        if action == "list":
            sessions = list_shell_sessions()
            if not sessions:
                return "No active sessions"

            result = "Active sessions:\n"
            for session in sessions:
                result += (f"ID: {session['session_id']} | "
                           f"Command: {session['command']} | "
                           f"Last activity: {session['last_activity']}\n")
            return result

        elif action == "output" and len(parts) >= 3:
            target_session_id = parts[2]
            output = get_session_output(target_session_id, clear=False, stdout=True)
            return output

        elif action == "kill" and len(parts) >= 3:
            target_session_id = parts[2]
            return terminate_session(target_session_id)

        return "Usage: session list|output <id>|kill <id>"

    # Handle environment information command
    if command.strip() == "env info" or command.strip() == "environment info":
        env_info = []
        
        # Check CTF environment
        try:
            from cai.cli import ctf_global
            if ctf_global and hasattr(ctf_global, 'get_shell'):
                env_info.append("🎯 CTF Environment: Active")
            else:
                env_info.append("🎯 CTF Environment: Not available")
        except:
            env_info.append("🎯 CTF Environment: Not available")
        
        # Check Container environment
        active_container = os.getenv("CAI_ACTIVE_CONTAINER", "")
        if active_container:
            env_info.append(f"🐳 Container: {active_container[:12]}")
        else:
            env_info.append("🐳 Container: Not active")
        
        # Check SSH environment
        ssh_user = os.getenv('SSH_USER')
        ssh_host = os.getenv('SSH_HOST')
        if ssh_user and ssh_host:
            env_info.append(f"🔗 SSH: {ssh_user}@{ssh_host}")
        else:
            env_info.append("🔗 SSH: Not configured")
        
        # Check workspace
        try:
            from cai.tools.common import _get_workspace_dir
            workspace = _get_workspace_dir()
            env_info.append(f"📁 Workspace: {workspace}")
        except:
            env_info.append("📁 Workspace: Unknown")
        
        return "Current Environment:\n" + "\n".join(env_info)

    if not command.strip():
        return "Error: No command provided"

    # For SSH sessions or interactive commands, use different timeout
    if session_id:
        timeout = 10
    else:
        timeout = 100
        
    # Command streaming should be independent of LLM streaming
    stream = True  # Always enable streaming for commands
    
    # Generate a call_id for streaming
    call_id = str(uuid.uuid4())[:8]

    # Run the command with the appropriate parameters
    result = run_command(command, ctf=None,
                       async_mode=interactive, session_id=session_id,
                       timeout=timeout, stream=stream, call_id=call_id,
                       tool_name="generic_linux_command")
    
    return result

@function_tool
def null_tool() -> str:
    """
    This is a null tool that does nothing.
    NEVER USE THIS TOOL
    """
    return "Null tool"