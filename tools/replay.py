#!/usr/bin/env python3
"""
Tool to convert JSONL files to a replay format that simulates the CLI output.
This allows reviewing conversations in a more readable format.

Usage:
    JSONL_FILE_PATH="path/to/file.jsonl" REPLAY_DELAY="0.5" python3 tools/replay.py

    # Or using positional arguments:
    python3 tools/replay.py path/to/file.jsonl 0.5
    cai-replay path/to/file.jsonl 0.5

    # Or using command line arguments:
    python3 tools/replay.py --jsonl-file-path path/to/file.jsonl --replay-delay 0.5

Usage with asciinema rec, generating a .cast file and then converting it to a gif:
    asciinema rec --command="python3 tools/replay.py path/to/file.jsonl 0.5" --overwrite

Or alternatively:
    asciinema rec --command="JSONL_FILE_PATH='caiextensions-memory/caiextensions/memory/it/pentestperf/hackableii/hackableII_autonomo.jsonl' REPLAY_DELAY='0.05' cai-replay"

Then convert the .cast file to a gif:
    agg /tmp/tmp6c4dxoac-ascii.cast demo.gif

Environment Variables:
    JSONL_FILE_PATH: Path to the JSONL file containing conversation history (required)
    REPLAY_DELAY: Time in seconds to wait between actions (default: 0.5)
"""
import json
import os
import sys
import time
import argparse
from typing import Dict, List, Tuple

# Disable session recording for replay tool
os.environ["CAI_DISABLE_SESSION_RECORDING"] = "true"

# Add the parent directory to the path to import cai modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.text import Text
from rich.console import Group

from cai.util import (
    cli_print_agent_messages,
    cli_print_tool_output,
    color
)
from cai.sdk.agents.run_to_jsonl import get_token_stats, load_history_from_jsonl
from cai.repl.ui.banner import display_banner

# Initialize console object for rich printing
console = Console()


# Create our own display_execution_time function that uses our local console
def display_execution_time(metrics=None):
    """Display the total execution time with our local console."""
    if metrics is None:
        return

    # Create a panel for the execution time
    content = []
    content.append(f"Session Time: {metrics['session_time']}")
    content.append(f"Active Time: {metrics['active_time']}")
    content.append(f"Idle Time: {metrics['idle_time']}")

    if metrics.get('llm_time') and metrics['llm_time'] != "0.0s":
        content.append(
            f"LLM Processing Time: [bold yellow]{metrics['llm_time']}[/bold yellow] "
            f"[dim]({metrics['llm_percentage']:.1f}% of session)[/dim]"
        )

    time_panel = Panel(
        Group(*[Text(line) for line in content]),
        border_style="blue",
        box=ROUNDED,
        padding=(0, 1),
        title="[bold]Session Statistics[/bold]",
        title_align="left"
    )
    console.print(time_panel)


def load_jsonl(file_path: str) -> List[Dict]:
    """Load a JSONL file and return its contents as a list of dictionaries."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line: {line[:50]}...")
    return data

def replay_conversation(messages: List[Dict], replay_delay: float = 0.5, usage: Tuple = None) -> None:
    """
    Replay a conversation from a list of messages, printing in real-time.

    Args:
        messages: List of message dictionaries
        replay_delay: Time in seconds to wait between actions
        usage: Tuple containing (model_name, total_input_tokens, total_output_tokens,
               total_cost, active_time, idle_time)
    """
    turn_counter = 0
    interaction_counter = 0
    debug = 0  # Always set debug to 2

    if not messages:
        print(color("No valid messages found in the JSONL file", fg="yellow"))
        return

    print(color(f"Replaying conversation with {len(messages)} messages...",
                fg="green"))

    # Extract the usage stats from the usage tuple
    # Handle both old format (4 elements) and new format (6 elements with timing)
    file_model = usage[0]
    total_input_tokens = usage[1]
    total_output_tokens = usage[2]
    total_cost = usage[3]

    # Check if timing information is available
    active_time = usage[4] if len(usage) > 4 else 0
    idle_time = usage[5] if len(usage) > 5 else 0

    # Display timing information if available
    if active_time > 0 or idle_time > 0:
        print(color(f"Active time: {active_time:.2f}s", fg="cyan"))
        print(color(f"Idle time: {idle_time:.2f}s", fg="cyan"))

    print(color(f"Total cost: ${total_cost:.6f}", fg="cyan"))

    # First pass: Process all tool outputs
    tool_outputs = {}
    for idx, message in enumerate(messages):
        if message.get("role") == "tool" and message.get("tool_call_id"):
            tool_id = message.get("tool_call_id")
            content = message.get("content", "")
            tool_outputs[tool_id] = content

    # Process assistant messages to match tool calls with outputs
    for message in messages:
        if message.get("role") == "assistant" and message.get("tool_calls"):
            for tool_call in message.get("tool_calls", []):
                call_id = tool_call.get("id", "")
                if call_id in tool_outputs:
                    # Add this output to the tool_outputs of the assistant message
                    if "tool_outputs" not in message:
                        message["tool_outputs"] = {}
                    message["tool_outputs"][call_id] = tool_outputs[call_id]

    for i, message in enumerate(messages):
        try:
            # Add delay between actions
            if i > 0:
                time.sleep(replay_delay)

            role = message.get("role", "")
            content = message.get("content")
            content = str(content).strip() if content is not None else ""
            sender = message.get("sender", role)
            model = message.get("model", file_model)

            # Skip system messages
            if role == "system":
                continue

            # Handle user messages
            if role == "user":
                print(color(f"CAI> ", fg="cyan") + f"{content}")
                turn_counter += 1
                interaction_counter = 0
            
            # Handle assistant messages
            elif role == "assistant":
                # Check if there are tool calls
                tool_calls = message.get("tool_calls", [])
                tool_outputs = message.get("tool_outputs", {})

                if tool_calls:
                    # Print the assistant message with tool calls
                    cli_print_agent_messages(
                        sender,
                        content or "",
                        interaction_counter,
                        model,
                        debug,
                        interaction_input_tokens=message.get("input_tokens", 0),
                        interaction_output_tokens=message.get("output_tokens", 0),
                        interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                        total_input_tokens=total_input_tokens,
                        total_output_tokens=total_output_tokens,
                        total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                        interaction_cost=message.get("interaction_cost", 0.0),
                        total_cost=total_cost
                    )

                    # Print each tool call with its output
                    for tool_call in tool_calls:
                        function = tool_call.get("function", {})
                        name = function.get("name", "")
                        arguments = function.get("arguments", "{}")
                        call_id = tool_call.get("id", "")

                        # Get the tool output if available
                        tool_output = ""
                        if call_id and call_id in tool_outputs:
                            tool_output = tool_outputs[call_id]

                        # Skip empty tool calls
                        if not name:
                            continue

                        try:
                            # Try to parse arguments as JSON
                            if arguments and isinstance(arguments, str) and arguments.strip().startswith("{"):
                                args_obj = json.loads(arguments)
                            else:
                                args_obj = arguments
                        except json.JSONDecodeError:
                            args_obj = arguments

                        # Print the tool call and output
                        cli_print_tool_output(
                            tool_name=name,
                            args=args_obj,
                            output=tool_output,  # Use the matched tool output
                            call_id=call_id,
                            token_info={
                                "interaction_input_tokens": message.get("input_tokens", 0),
                                "interaction_output_tokens": message.get("output_tokens", 0),
                                "interaction_reasoning_tokens": message.get("reasoning_tokens", 0),
                                "total_input_tokens": total_input_tokens,
                                "total_output_tokens": total_output_tokens,
                                "total_reasoning_tokens": message.get("total_reasoning_tokens", 0),
                                "model": model,
                                "interaction_cost": message.get("interaction_cost", 0.0),
                                "total_cost": total_cost
                            }
                        )
                else:
                    # Print regular assistant message
                    cli_print_agent_messages(
                        sender,
                        content or "",
                        interaction_counter,
                        model,
                        debug,
                        interaction_input_tokens=message.get("input_tokens", 0),
                        interaction_output_tokens=message.get("output_tokens", 0),
                        interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                        total_input_tokens=total_input_tokens,
                        total_output_tokens=total_output_tokens,
                        total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                        interaction_cost=message.get("interaction_cost", 0.0),
                        total_cost=total_cost
                    )
                interaction_counter += 1  # iterate the interaction counter

            # Handle tool messages - only those not already displayed with assistant messages
            elif role == "tool":
                # Check if we've already displayed this tool output with an assistant message
                tool_call_id = message.get("tool_call_id", "")

                # Skip tool messages that have been displayed with an assistant message
                is_already_displayed = False
                for prev_msg in messages[:i]:
                    if prev_msg.get("role") == "assistant" and tool_call_id in prev_msg.get("tool_outputs", {}):
                        is_already_displayed = True
                        break

                if not is_already_displayed and content:  # Only show if there's actual content
                    tool_name = message.get("name", message.get("tool_call_id", "unknown"))
                    cli_print_tool_output(
                        tool_name=tool_name,
                        args="",
                        output=content,
                        token_info={
                            "interaction_input_tokens": message.get("input_tokens", 0),
                            "interaction_output_tokens": message.get("output_tokens", 0),
                            "interaction_reasoning_tokens": message.get("reasoning_tokens", 0),
                            "total_input_tokens": total_input_tokens,
                            "total_output_tokens": total_output_tokens,
                            "total_reasoning_tokens": message.get("total_reasoning_tokens", 0),
                            "model": model,
                            "interaction_cost": message.get("interaction_cost", 0.0),
                            "total_cost": total_cost
                        }
                    )

            # Handle any other message types
            else:
                if content:  # Only display if there's actual content
                    cli_print_agent_messages(
                        sender or role,
                        content,
                        interaction_counter,
                        model,
                        debug,
                        interaction_input_tokens=message.get("input_tokens", 0),
                        interaction_output_tokens=message.get("output_tokens", 0),
                        interaction_reasoning_tokens=message.get("reasoning_tokens", 0),
                        total_input_tokens=total_input_tokens,
                        total_output_tokens=total_output_tokens,
                        total_reasoning_tokens=message.get("total_reasoning_tokens", 0),
                        interaction_cost=message.get("interaction_cost", 0.0),
                        total_cost=total_cost
                    )

            # Force flush stdout to ensure immediate printing
            sys.stdout.flush()

        except Exception as e:
            # Handle any errors during message processing
            print(color(f"Warning: Error processing message {i+1}: {str(e)}", fg="yellow"))
            print(color("Continuing with next message...", fg="yellow"))
            continue


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tool to convert JSONL files to a replay format that simulates the CLI output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variables:
  JSONL_FILE_PATH="path/to/file.jsonl" REPLAY_DELAY="0.5" python3 tools/replay.py

  # Using positional arguments:
  python3 tools/replay.py path/to/file.jsonl 0.5
  cai-replay path/to/file.jsonl 0.5

  # Using command line arguments:
  python3 tools/replay.py --jsonl-file-path path/to/file.jsonl --replay-delay 0.5

  # Using positional argument for file only:
  python3 tools/replay.py path/to/file.jsonl --replay-delay 0.5

  # With asciinema:
  asciinema rec --command="python3 tools/replay.py path/to/file.jsonl 0.5" --overwrite
"""
    )

    parser.add_argument(
        "jsonl_file",
        nargs="?",
        default=None,
        help="Path to the JSONL file containing conversation history"
    )

    parser.add_argument(
        "replay_delay_pos",
        nargs="?",
        type=float,
        default=None,
        help="Time in seconds to wait between actions (positional argument)"
    )

    parser.add_argument(
        "--jsonl-file-path",
        type=str,
        help="Path to the JSONL file containing conversation history"
    )

    parser.add_argument(
        "--replay-delay",
        type=float,
        default=0.5,
        help="Time in seconds to wait between actions (default: 0.5)"
    )

    return parser.parse_args()


def main():
    """Main function to process JSONL files and generate replay output."""
    # Display banner
    display_banner(console)
    print("\n")

    # Parse command line arguments
    args = parse_arguments()

    # Get environment variables or command line arguments
    # First check for --jsonl-file-path, then positional argument, then environment variable
    jsonl_file_path = args.jsonl_file_path or args.jsonl_file or os.environ.get("JSONL_FILE_PATH")

    # For replay delay, prioritize: positional arg > --replay-delay > environment variable > default
    if args.replay_delay_pos is not None:
        replay_delay = args.replay_delay_pos
    elif args.replay_delay != 0.5:  # Check if --replay-delay was explicitly set
        replay_delay = args.replay_delay
    else:
        replay_delay = float(os.environ.get("REPLAY_DELAY", "0.5"))

    # Validate required parameters
    if not jsonl_file_path:
        print(color("Error: JSONL file path is required. Use a positional argument, --jsonl-file-path option, or set JSONL_FILE_PATH environment variable.",
                    fg="red"))
        sys.exit(1)

    print(color(f"Loading JSONL file: {jsonl_file_path}", fg="blue"))

    try:
        # Load the full JSONL file to extract tool outputs
        full_data = load_jsonl(jsonl_file_path)

        # Extract tool outputs from events and find last assistant message
        tool_outputs = {}

        # Load the JSONL file for messages
        messages = load_history_from_jsonl(jsonl_file_path)

        # Attach tool outputs to messages
        for message in messages:
            if message.get("role") == "assistant" and message.get("tool_calls"):
                if "tool_outputs" not in message:
                    message["tool_outputs"] = {}

                for tool_call in message.get("tool_calls", []):
                    call_id = tool_call.get("id", "")
                    if call_id in tool_outputs:
                        message["tool_outputs"][call_id] = tool_outputs[call_id]

        print(color(f"Loaded {len(messages)} messages from JSONL file", fg="blue"))

        # Get token stats and cost from the JSONL file
        usage = get_token_stats(jsonl_file_path)

        # Display timing information if available (new format)
        if len(usage) > 4:
            print(color(f"Active time: {usage[4]:.2f}s", fg="blue"))
            print(color(f"Idle time: {usage[5]:.2f}s", fg="blue"))

        # Generate the replay with live printing
        replay_conversation(messages, replay_delay, usage)
        print(color("Replay completed successfully", fg="green"))

        # Display the total cost
        active_time = usage[4] if len(usage) > 4 else 0
        idle_time = usage[5] if len(usage) > 5 else 0
        total_time = active_time + idle_time

        # Format time values as strings with units
        def format_time(seconds):
            """Format time in seconds to a human-readable string."""
            if seconds < 60:
                return f"{seconds:.1f}s"
            else:
                # Convert seconds to hours, minutes, seconds
                hours, remainder = divmod(seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                if hours > 0:
                    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
                else:
                    return f"{int(minutes)}m {int(seconds)}s"

        metrics = {
            'session_time': format_time(total_time),
            'llm_time': "0.0s",
            'llm_percentage': 0,
            'active_time': format_time(active_time),
            'idle_time': format_time(idle_time)
        }
        display_execution_time(metrics)

    except FileNotFoundError:
        print(color(f"Error: File {jsonl_file_path} not found", fg="red"))
        sys.exit(1)
    except json.JSONDecodeError:
        print(color(f"Error: Invalid JSON in {jsonl_file_path}", fg="red"))
        sys.exit(1)
    except Exception as e:
        print(color(f"Error: {str(e)}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
