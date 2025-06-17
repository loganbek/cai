"""
Data recorder
"""

import os  # pylint: disable=import-error
from datetime import datetime
import json
import socket
import urllib.request
import getpass
import platform
from urllib.error import URLError
import pytz  # pylint: disable=import-error
import uuid  # Add uuid import
from cai.util import get_active_time, get_idle_time
import time
import requests
import atexit

# Global recorder instance for session-wide logging
_session_recorder = None


def get_session_recorder(workspace_name=None):
    """
    Get the global session recorder instance.
    If one doesn't exist, it will be created.

    Args:
        workspace_name (str | None): Optional workspace name.

    Returns:
        DataRecorder: The session recorder instance.
    """
    global _session_recorder
    
    # Check if session recording is disabled (e.g., during replay)
    if os.environ.get("CAI_DISABLE_SESSION_RECORDING", "").lower() == "true":
        return None
    
    if _session_recorder is None:
        _session_recorder = DataRecorder(workspace_name)
    return _session_recorder


class DataRecorder:  # pylint: disable=too-few-public-methods
    """
    Records training data from litellm.completion
    calls in OpenAI-like JSON format.

    Stores both input messages and completion
    responses during execution in a single JSONL file.
    """

    def __init__(self, workspace_name: str | None = None):
        """
        Initializes the DataRecorder.

        Args:
            workspace_name (str | None): The name of the current workspace.
        """
        # Generate a session ID that will be used for the entire session
        self.session_id = str(uuid.uuid4())

        # Track the last message to ensure it's logged
        self.last_assistant_message = None
        self.last_assistant_tool_calls = None
        self._last_message_logged = False
        self._session_end_logged = False

        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        # Get current username
        try:
            username = getpass.getuser()
        except Exception:  # pylint: disable=broad-except
            username = "unknown"

        # Get operating system and version information
        try:
            os_name = platform.system().lower()
            os_version = platform.release()
            os_info = f"{os_name}_{os_version}"
        except Exception:  # pylint: disable=broad-except
            os_info = "unknown_os"

        # Check internet connection and get public IP
        public_ip = "127.0.0.1"
        try:
            # Quick connection check with minimal traffic
            socket.create_connection(("1.1.1.1", 53), timeout=1)

            # If connected, try to get public IP
            try:
                # Using a simple and lightweight service
                with urllib.request.urlopen(  # nosec: B310
                    "https://api.ipify.org",
                    timeout=2
                ) as response:
                    public_ip = response.read().decode('utf-8')
            except (URLError, socket.timeout):
                # Fallback to another service if the first one fails
                try:
                    with urllib.request.urlopen(  # nosec: B310
                        "https://ifconfig.me",
                        timeout=2
                    ) as response:
                        public_ip = response.read().decode('utf-8')
                except (URLError, socket.timeout):
                    # If both services fail, keep the default value
                    pass
        except (OSError, socket.timeout, socket.gaierror):
            # No internet connection, keep the default value
            pass

        # Create filename with username, OS info, and IP
        timestamp = datetime.now().astimezone(
            pytz.timezone("Europe/Madrid")).strftime("%Y%m%d_%H%M%S")
        base_filename = f'cai_{self.session_id}_{timestamp}_{username}_{os_info}_{public_ip.replace(".", "_")}.jsonl'

        if workspace_name:
            self.filename = os.path.join(
                log_dir, f'{workspace_name}_{base_filename}'
            )
        else:
            self.filename = os.path.join(log_dir, base_filename)

        # Inicializar el coste total acumulado
        self.total_cost = 0.0

        # Log the session start
        with open(self.filename, 'a', encoding='utf-8') as f:
            session_start = {
                "event": "session_start",
                "timestamp": datetime.now().astimezone(
                    pytz.timezone("Europe/Madrid")).isoformat(),
                "session_id": self.session_id
            }
            json.dump(session_start, f)
            f.write('\n')

    def rec_training_data(self, create_params, msg, total_cost=None) -> None:
        """
        Records a single training data entry to the JSONL file

        Args:
            create_params: Parameters used for the LLM call
            msg: Response from the LLM
            total_cost: Optional total accumulated cost from CAI instance
        """
        request_data = {
            "model": create_params["model"],
            "messages": create_params["messages"],
            "stream": create_params["stream"]
        }
        if "tools" in create_params:
            request_data.update({
                "tools": create_params["tools"],
                "tool_choice": create_params["tool_choice"],
            })

        # Obtener el coste de la interacción
        interaction_cost = 0.0
        if hasattr(msg, "cost"):
            interaction_cost = float(msg.cost) if msg.cost is not None else 0.0

        # Usar el total_cost proporcionado o actualizar el interno
        if total_cost is not None:
            self.total_cost = float(total_cost)
        else:
            self.total_cost += interaction_cost

        # Get timing metrics (without units, just numeric values)
        active_time_str = get_active_time()
        idle_time_str = get_idle_time()

        # Convert string time to seconds for storage
        def time_str_to_seconds(time_str):
            if "h" in time_str:
                parts = time_str.split()
                hours = float(parts[0].replace("h", ""))
                minutes = float(parts[1].replace("m", ""))
                seconds = float(parts[2].replace("s", ""))
                return hours * 3600 + minutes * 60 + seconds
            if "m" in time_str:
                parts = time_str.split()
                minutes = float(parts[0].replace("m", ""))
                seconds = float(parts[1].replace("s", ""))
                return minutes * 60 + seconds
            return float(time_str.replace("s", ""))

        active_time_seconds = time_str_to_seconds(active_time_str)
        idle_time_seconds = time_str_to_seconds(idle_time_str)

        # Get token usage from the usage object - handle both field names
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        
        if hasattr(msg, "usage"):
            # Try input_tokens first (ResponseUsage)
            if hasattr(msg.usage, "input_tokens"):
                prompt_tokens = msg.usage.input_tokens
            # Fall back to prompt_tokens (ChatCompletion)
            elif hasattr(msg.usage, "prompt_tokens"):
                prompt_tokens = msg.usage.prompt_tokens
                
            # Try output_tokens first (ResponseUsage)
            if hasattr(msg.usage, "output_tokens"):
                completion_tokens = msg.usage.output_tokens
            # Fall back to completion_tokens (ChatCompletion)
            elif hasattr(msg.usage, "completion_tokens"):
                completion_tokens = msg.usage.completion_tokens
                
            # Get total tokens - calculate if not available
            if hasattr(msg.usage, "total_tokens"):
                total_tokens = msg.usage.total_tokens
            else:
                total_tokens = prompt_tokens + completion_tokens

        completion_data = {
            "id": msg.id,
            "object": "chat.completion",
            "created": int(datetime.now().timestamp()),
            "model": msg.model,
            "messages": [
                {
                    "role": m.role,
                    "content": m.content,
                    "tool_calls": [t.model_dump() for t in (m.tool_calls or [])]  # pylint: disable=line-too-long  # noqa: E501
                }
                for m in msg.messages
            ] if hasattr(msg, "messages") else [],
            "choices": [{
                "index": 0,
                "message": {
                    "role": msg.choices[0].message.role if hasattr(msg, "choices") and msg.choices else "assistant",
                    "content": msg.choices[0].message.content if hasattr(msg, "choices") and msg.choices else None,
                    "tool_calls": [t.model_dump() for t in (msg.choices[0].message.tool_calls or [])] if hasattr(msg, "choices") and msg.choices else []  # pylint: disable=line-too-long  # noqa: E501
                },
                "finish_reason": msg.choices[0].finish_reason if hasattr(msg, "choices") and msg.choices else "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            },
            "cost": {
                "interaction_cost": interaction_cost,
                "total_cost": self.total_cost
            },
            "timing": {
                "active_seconds": active_time_seconds,
                "idle_seconds": idle_time_seconds
            },
            "timestamp_iso": datetime.now().astimezone(
                pytz.timezone("Europe/Madrid")).isoformat()
        }

        # Append both request and completion to the instance's jsonl file
        with open(self.filename, 'a', encoding='utf-8') as f:
            json.dump(request_data, f)
            f.write('\n')
            json.dump(completion_data, f)
            f.write('\n')

    def log_user_message(self, user_message):
        """
        Logs a user message to the JSONL file.
        
        Args:
            user_message: The message from the user to log
        """
        with open(self.filename, 'a', encoding='utf-8') as f:
            user_data = {
                "event": "user_message",
                "timestamp": datetime.now().astimezone(
                    pytz.timezone("Europe/Madrid")).isoformat(),
                "content": user_message
            }
            json.dump(user_data, f)
            f.write('\n')
    
    def log_assistant_message(self, assistant_message, tool_calls=None):
        """
        Logs an assistant message to the JSONL file.
        
        Args:
            assistant_message: The message from the assistant to log
            tool_calls: Optional tool calls included in the assistant message
        """
        # Store the last message in case we need to log it at exit
        self.last_assistant_message = assistant_message
        self.last_assistant_tool_calls = tool_calls
        
        with open(self.filename, 'a', encoding='utf-8') as f:
            assistant_data = {
                "event": "assistant_message",
                "timestamp": datetime.now().astimezone(
                    pytz.timezone("Europe/Madrid")).isoformat(),
                "content": assistant_message
            }
            if tool_calls:
                assistant_data["tool_calls"] = tool_calls
            json.dump(assistant_data, f)
            f.write('\n')
            
        # Mark that the message has been logged
        self._last_message_logged = True
    
    def log_session_end(self):
        """
        Logs the end of the session to the JSONL file.
        Includes timing metrics from active/idle time tracking.
        """
        # Set a flag to indicate we've already logged the session end
        self._session_end_logged = True
        
        try:
            from cai.util import get_active_time_seconds, get_idle_time_seconds, COST_TRACKER
            active_time = get_active_time_seconds()
            idle_time = get_idle_time_seconds()
            # Get the global session cost from COST_TRACKER
            session_cost = COST_TRACKER.session_total_cost
        except ImportError:
            active_time = 0.0
            idle_time = 0.0
            session_cost = self.total_cost
            
        with open(self.filename, 'a', encoding='utf-8') as f:
            session_end = {
                "event": "session_end",
                "timestamp": datetime.now().astimezone(
                    pytz.timezone("Europe/Madrid")).isoformat(),
                "session_id": self.session_id,
                "timing_metrics": {
                    "active_time_seconds": active_time,
                    "idle_time_seconds": idle_time,
                    "total_time_seconds": active_time + idle_time,
                    "active_percentage": round((active_time / (active_time + idle_time)) * 100, 2) if (active_time + idle_time) > 0 else 0.0
                },
                "cost": {
                    "total_cost": session_cost  # Use the global session cost
                }
            }
            json.dump(session_end, f)
            f.write('\n')


def load_history_from_jsonl(file_path):
    """
    Load conversation history from a JSONL file and
    return it as a list of messages.

    Args:
        file_path (str): The path to the JSONL file.
            NOTE: file_path assumes it's either relative to the
            current directory or absolute.

    Returns:
        list: A list of messages extracted from the JSONL file.
    """
    messages = []
    last_assistant_message = None
    tool_outputs = {}  # Map tool_call_id to output content
    
    try:
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except Exception:  # pylint: disable=broad-except
                    print(f"Error loading line: {line}")
                    continue

                # Collect tool outputs from tool_message events
                if record.get("event") == "tool_message":
                    tool_call_id = record.get("tool_call_id", "")
                    content = record.get("content", "")
                    if tool_call_id and content:
                        tool_outputs[tool_call_id] = content

                # process assistant messages and keep the last one
                # for additing it manually at the end
                if record.get("event") == "assistant_message":
                    last_assistant_message = record.get("content")

                # Extract messages from model record
                if "model" in record and "messages" in record and isinstance(record["messages"], list):
                    # Store only complete conversation message objects
                    for msg in record["messages"]:
                        if "role" in msg:
                            # Skip system messages
                            if msg.get("role") == "system":
                                continue

                            # Add this message if we haven't seen it already
                            if not any(m.get("role") == msg.get("role") and 
                                       m.get("content") == msg.get("content") and
                                       m.get("tool_call_id") == msg.get("tool_call_id") for m in messages):
                                messages.append(msg)

                # Extract assistant messages and tool responses from model record choices
                elif "choices" in record and isinstance(record["choices"], list) and record["choices"]:
                    choice = record["choices"][0]
                    if "message" in choice and "role" in choice["message"]:
                        msg = choice["message"]
                        if not any(m.get("role") == msg.get("role") and 
                                  m.get("content") == msg.get("content") and
                                  m.get("tool_call_id") == msg.get("tool_call_id") for m in messages):
                            messages.append(msg)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error loading history from {file_path}: {e}")

    # Clean up duplicates and reorder
    unique_messages = []
    for msg in messages:
        if not any(m.get("role") == msg.get("role") and 
                  m.get("content") == msg.get("content") and
                  m.get("tool_call_id", "") == msg.get("tool_call_id", "") and
                  m.get("tool_calls") == msg.get("tool_calls") for m in unique_messages):
            unique_messages.append(msg)

    # Now add tool result messages for any tool calls that have outputs
    final_messages = []
    for msg in unique_messages:
        final_messages.append(msg)
        
        # If this is an assistant message with tool_calls, add corresponding tool results
        if (msg.get("role") == "assistant" and 
            msg.get("tool_calls") and 
            isinstance(msg.get("tool_calls"), list)):
            
            for tool_call in msg.get("tool_calls", []):
                tool_call_id = tool_call.get("id")
                if tool_call_id and tool_call_id in tool_outputs:
                    # Add the tool result message immediately after the assistant message
                    tool_result_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_outputs[tool_call_id]
                    }
                    final_messages.append(tool_result_msg)

    # Add last message to the end of the list if it exists and isn't already there
    if last_assistant_message:
        # Check if this message is already in the list
        if not any(m.get("role") == "assistant" and 
                  m.get("content") == last_assistant_message for m in final_messages):
            final_messages.append({
                "role": "assistant",
                "content": last_assistant_message
            })
    
    return final_messages


def get_token_stats(file_path):
    """
    Get token usage statistics from a JSONL file.

    Args:
        file_path (str): Path to the JSONL file

    Returns:
        tuple: (model_name, total_prompt_tokens, total_completion_tokens,
                total_cost, active_time, idle_time)
    """
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cost = 0.0
    model_name = None
    last_total_cost = 0.0
    last_active_time = 0.0
    last_idle_time = 0.0

    with open(file_path, encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if "usage" in record:
                    total_prompt_tokens += record["usage"]["prompt_tokens"]
                    total_completion_tokens += (
                        record["usage"]["completion_tokens"]
                    )
                if "cost" in record:
                    if isinstance(record["cost"], dict):
                        # Si cost es un diccionario, obtener total_cost
                        last_total_cost = record["cost"].get("total_cost", 0.0)
                    else:
                        # Si cost es un valor directo
                        last_total_cost = float(record["cost"])
                if "timing_metrics" in record:
                    if isinstance(record["timing_metrics"], dict):
                        last_active_time = record["timing_metrics"].get(
                            "active_time_seconds", 0.0)
                        last_idle_time = record["timing_metrics"].get(
                            "idle_time_seconds", 0.0)
                if "model" in record:
                    model_name = record["model"]
                # Keep track of the last record for session_end event
                if record.get("event") == "session_end":
                    if "timing_metrics" in record and isinstance(record["timing_metrics"], dict):
                        last_active_time = record["timing_metrics"].get(
                            "active_time_seconds", 0.0)
                        last_idle_time = record["timing_metrics"].get(
                            "idle_time_seconds", 0.0)
                    if "cost" in record and isinstance(record["cost"], dict):
                        last_total_cost = record["cost"].get("total_cost", 0.0)
            except Exception as e:  # pylint: disable=broad-except
                print(f"Error loading line: {line}: {e}")
                continue

    # Usar el último total_cost encontrado como el total
    total_cost = last_total_cost

    return (model_name, total_prompt_tokens, total_completion_tokens,
            total_cost, last_active_time, last_idle_time)

def atexit_handler():
    """
    Ensure session_end is logged when the program exits.
    Only logs if a session recorder exists and session_end hasn't already been logged.
    """
    global _session_recorder
    if _session_recorder is None:
        return
    
    # Check if we have an unlogged assistant message and log it
    if hasattr(_session_recorder, 'last_assistant_message') and not getattr(_session_recorder, '_last_message_logged', False):
        if _session_recorder.last_assistant_message or _session_recorder.last_assistant_tool_calls:
            _session_recorder.log_assistant_message(
                _session_recorder.last_assistant_message,
                _session_recorder.last_assistant_tool_calls
            )
    
    # Check if we've already logged the session end (via KeyboardInterrupt)
    if getattr(_session_recorder, '_session_end_logged', False):
        return
    
    # Log the session end
    _session_recorder.log_session_end()

# Register the exit handler
atexit.register(atexit_handler)