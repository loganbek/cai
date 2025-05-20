"""
Command completer for CAI REPL.
This module provides a fuzzy command completer with autocompletion menu and
command shadowing.
"""
# Standard library imports
import datetime
import threading
import time
from functools import lru_cache
from typing import (
    List,
    Optional,
    Dict,
    Any
)
import json
import subprocess

# Third-party imports
import requests  # pylint: disable=import-error,unused-import,line-too-long # noqa: E501
from prompt_toolkit.completion import (  # pylint: disable=import-error
    Completer,
    Completion
)
from prompt_toolkit.formatted_text import HTML  # pylint: disable=import-error
from prompt_toolkit.styles import Style  # pylint: disable=import-error
from rich.console import Console  # pylint: disable=import-error

from cai.core import get_ollama_api_base
from cai.repl.commands.base import (
    COMMANDS,
    COMMAND_ALIASES
)

console = Console()

# Global cache for command descriptions and subcommands
COMMAND_DESCRIPTIONS_CACHE = None
SUBCOMMAND_DESCRIPTIONS_CACHE = None
ALL_COMMANDS_CACHE = None


class FuzzyCommandCompleter(Completer):
    """Command completer with fuzzy matching for the REPL.

    This advanced completer provides intelligent suggestions for commands,
    subcommands, and arguments based on what the user is typing.
    It supports fuzzy matching to find commands even with typos.

    Features:
    - Fuzzy matching for commands and subcommands
    - Autocompletion menu with descriptions
    - Command shadowing (showing hints for previously used commands)
    - Model completion for the /model command
    - Virtualization completion for Docker containers and images
    """

    # Class-level cache for models
    _cached_models = []
    _cached_model_numbers = {}
    _last_model_fetch = datetime.datetime.now() - datetime.timedelta(minutes=10)
    _fetch_lock = threading.Lock()

    # Class-level cache for Docker images
    _cached_docker_images = []
    _last_docker_fetch = datetime.datetime.now() - datetime.timedelta(minutes=10)
    _docker_fetch_lock = threading.Lock()

    def __init__(self):
        """Initialize the command completer with cached model information."""
        super().__init__()
        self.command_history = {}  # Store command usage frequency
        
        # Fetch models in background thread to avoid blocking
        threading.Thread(
            target=self._background_fetch_models,
            daemon=True
        ).start()

        # Styling for the completion menu
        self.completion_style = Style.from_dict({
            'completion-menu': 'bg:#2b2b2b #ffffff',
            'completion-menu.completion': 'bg:#2b2b2b #ffffff',
            'completion-menu.completion.current': 'bg:#004b6b #ffffff',
            'scrollbar.background': 'bg:#2b2b2b',
            'scrollbar.button': 'bg:#004b6b',
        })
    
    def _background_fetch_models(self):
        """Fetch models in background to avoid blocking the UI."""
        try:
            self.fetch_ollama_models()
        except Exception:  # pylint: disable=broad-except
            pass

    def fetch_ollama_models(self):  # pylint: disable=too-many-branches,too-many-statements,inconsistent-return-statements,line-too-long # noqa: E501
        """
        Fetches and caches the list of available models from the Ollama API and standard model presets.
        
        If the Ollama API is available, retrieves the list of models from the running instance, otherwise falls back to a predefined set of standard models. Updates internal caches for model names and their corresponding numeric indices. Limits fetch frequency to once per 60 seconds to reduce API calls. Silently ignores errors if the Ollama API is unreachable.
        """
        # Only fetch every 60 seconds to avoid excessive API calls
        now = datetime.datetime.now()
        
        # Use a lock to prevent multiple threads from fetching simultaneously
        with self._fetch_lock:
            if (now - self._last_model_fetch).total_seconds() < 60:
                return
            
            self._last_model_fetch = now
            ollama_models = []

            try:
                # Get Ollama models with a short timeout to prevent hanging
                api_base = get_ollama_api_base()
                response = requests.get(
                    f"{api_base.replace('/v1', '')}/api/tags", timeout=0.5)

                if response.status_code == 200:
                    data = response.json()
                    if 'models' in data:
                        models = data['models']
                    else:
                        # Fallback for older Ollama versions
                        models = data.get('items', [])

                    ollama_models = [(model.get('name', ''), []) for model in models]
            except Exception:  # pylint: disable=broad-except
                # Silently fail if Ollama is not available
                pass

            # Standard models always available
            standard_models = [
                # Claude 3.7 models
                "claude-3-7-sonnet-20250219",

                # Claude 3.5 models
                "claude-3-5-sonnet-20240620",
                "claude-3-5-20241122",

                # Claude 3 models
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",

                # OpenAI O-series models
                "o1",
                "o1-mini",
                "o3-mini",                # OpenAI GPT models
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo",

                # Google Gemini models
                "gemini/gemini-2.5-pro-exp-03-25",

                # DeepSeek models
                "deepseek/deepseek-chat",
                "deepseek/deepseek-reasoner"
            ]

            # Combine standard models with Ollama models
            self._cached_models = standard_models + ollama_models

            # Create number mappings for models (1-based indexing)
            self._cached_model_numbers = {}
            for i, model in enumerate(self._cached_models, 1):
                self._cached_model_numbers[str(i)] = model

    def record_command_usage(self, command: str):
        """Record command usage for command shadowing.

        Args:
            command: The command that was used
        """
        if command.startswith('/'):
            # Extract the main command
            parts = command.split()
            main_command = parts[0]

            # Update usage count
            if main_command in self.command_history:
                self.command_history[main_command] += 1
            else:
                self.command_history[main_command] = 1

    @lru_cache(maxsize=1)
    def get_command_descriptions(self):
        """Get descriptions for all commands.

        Returns:
            A dictionary mapping command names to descriptions
        """
        global COMMAND_DESCRIPTIONS_CACHE
        if COMMAND_DESCRIPTIONS_CACHE is None:
            COMMAND_DESCRIPTIONS_CACHE = {cmd.name: cmd.description for cmd in COMMANDS.values()}
        return COMMAND_DESCRIPTIONS_CACHE

    @lru_cache(maxsize=1)
    def get_subcommand_descriptions(self):
        """Get descriptions for all subcommands.

        Returns:
            A dictionary mapping command paths to descriptions
        """
        global SUBCOMMAND_DESCRIPTIONS_CACHE
        if SUBCOMMAND_DESCRIPTIONS_CACHE is None:
            descriptions = {}
            for cmd in COMMANDS.values():
                for subcmd in cmd.get_subcommands():
                    key = f"{cmd.name} {subcmd}"
                    descriptions[key] = cmd.get_subcommand_description(subcmd)
            SUBCOMMAND_DESCRIPTIONS_CACHE = descriptions
        return SUBCOMMAND_DESCRIPTIONS_CACHE

    @lru_cache(maxsize=1)
    def get_all_commands(self):
        """Get all commands and their subcommands.

        Returns:
            A dictionary mapping command names to lists of subcommand names
        """
        global ALL_COMMANDS_CACHE
        if ALL_COMMANDS_CACHE is None:
            ALL_COMMANDS_CACHE = {cmd.name: cmd.get_subcommands() for cmd in COMMANDS.values()}
        return ALL_COMMANDS_CACHE

    # Cache for command suggestions to avoid recalculating
    _command_suggestions_cache = {}
    _command_suggestions_last_update = 0
    _command_suggestions_update_interval = 1.0  # Update every second

    def get_command_suggestions(self, current_word: str) -> List[Completion]:
        """Get command suggestions with fuzzy matching.

        Args:
            current_word: The current word being typed

        Returns:
            A list of completions for commands
        """
        # Check cache first
        current_time = time.time()
        cache_key = current_word
        
        if (cache_key in self._command_suggestions_cache and
                current_time - self._command_suggestions_last_update < 
                self._command_suggestions_update_interval):
            return self._command_suggestions_cache[cache_key]
        
        suggestions = []

        # Get command descriptions
        command_descriptions = self.get_command_descriptions()

        # Sort commands by usage frequency (for command shadowing)
        sorted_commands = sorted(
            command_descriptions.items(),
            key=lambda x: self.command_history.get(x[0], 0),
            reverse=True
        )

        # Add command completions
        for cmd, description in sorted_commands:
            # Exact prefix match
            if cmd.startswith(current_word):
                suggestions.append(Completion(
                    cmd,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansicyan><b>{cmd:<15}</b></ansicyan> "
                        f"{description}"),
                    style="fg:ansicyan bold"
                ))
            # Fuzzy match (contains the substring)
            elif current_word in cmd and not cmd.startswith(current_word):
                suggestions.append(Completion(
                    cmd,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansicyan>{cmd:<15}</ansicyan> {description}"),
                    style="fg:ansicyan"
                ))

        # Add alias completions
        for alias, cmd in sorted(COMMAND_ALIASES.items()):
            cmd_description = command_descriptions.get(cmd, "")
            if alias.startswith(current_word):
                suggestions.append(Completion(
                    alias,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansigreen><b>{alias:<15}</b></ansigreen> "
                        f"{cmd} - {cmd_description}"),
                    style="fg:ansigreen bold"
                ))
            elif current_word in alias and not alias.startswith(current_word):
                suggestions.append(Completion(
                    alias,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansigreen>{alias:<15}</ansigreen> "
                        f"{cmd} - {cmd_description}"),
                    style="fg:ansigreen"
                ))
        
        # Update cache
        self._command_suggestions_cache[cache_key] = suggestions
        self._command_suggestions_last_update = current_time
        
        return suggestions

    # Cache for command shadow
    _command_shadow_cache = {}
    _command_shadow_last_update = 0
    _command_shadow_update_interval = 0.2  # Update every 200ms

    @lru_cache(maxsize=100)
    def _get_command_shadow_cached(self, text: str) -> Optional[str]:
        """Cached version of command shadow lookup."""
        if not text or not text.startswith('/'):
            return None

        # Find commands that start with the current input
        matching_commands = []
        for cmd, count in self.command_history.items():
            if cmd.startswith(text) and cmd != text:
                matching_commands.append((cmd, count))

        # Sort by usage count (descending)
        matching_commands.sort(key=lambda x: x[1], reverse=True)

        # Return the most frequently used command
        if matching_commands:
            return matching_commands[0][0]

        return None

    def get_command_shadow(self, text: str) -> Optional[str]:
        """Get a command shadow suggestion based on command history.

        This method returns a suggestion for command shadowing based on
        the current input and command usage history.

        Args:
            text: The current input text

        Returns:
            A suggested command completion or None if no suggestion
        """
        # Check cache first
        current_time = time.time()
        
        if (text in self._command_shadow_cache and
                current_time - self._command_shadow_last_update < 
                self._command_shadow_update_interval):
            return self._command_shadow_cache[text]
        
        # Get shadow from cached function
        result = self._get_command_shadow_cached(text)
        
        # Update cache
        self._command_shadow_cache[text] = result
        self._command_shadow_last_update = current_time
        
        return result

    # Cache for subcommand suggestions
    _subcommand_suggestions_cache = {}
    _subcommand_suggestions_last_update = 0
    _subcommand_suggestions_update_interval = 1.0  # Update every second
    
    def get_subcommand_suggestions(
            self, cmd: str, current_word: str) -> List[Completion]:
        """Get subcommand suggestions with fuzzy matching.

        Args:
            cmd: The main command
            current_word: The current word being typed

        Returns:
            A list of completions for subcommands
        """
        # Check cache first
        current_time = time.time()
        cache_key = f"{cmd}:{current_word}"
        
        if (cache_key in self._subcommand_suggestions_cache and
                current_time - self._subcommand_suggestions_last_update < 
                self._subcommand_suggestions_update_interval):
            return self._subcommand_suggestions_cache[cache_key]
            
        suggestions = []

        # If using an alias, get the real command
        cmd = COMMAND_ALIASES.get(cmd, cmd)

        all_commands = self.get_all_commands()
        subcommand_descriptions = self.get_subcommand_descriptions()

        if cmd in all_commands:
            for subcmd in sorted(all_commands[cmd]):
                # Get description for this subcommand if available
                subcmd_description = subcommand_descriptions.get(
                    f"{cmd} {subcmd}", "")

                # Exact prefix match
                if subcmd.startswith(current_word):
                    suggestions.append(Completion(
                        subcmd,
                        start_position=-len(current_word),
                        display=HTML(
                            f"<ansiyellow><b>{subcmd:<15}</b></ansiyellow> "
                            f"{subcmd_description}"),
                        style="fg:ansiyellow bold"
                    ))
                # Fuzzy match
                elif (current_word in subcmd and
                      not subcmd.startswith(current_word)):
                    suggestions.append(Completion(
                        subcmd,
                        start_position=-len(current_word),
                        display=HTML(
                            f"<ansiyellow>{subcmd:<15}</ansiyellow> "
                            f"{subcmd_description}"),
                        style="fg:ansiyellow"
                    ))
        
        # Update cache
        self._subcommand_suggestions_cache[cache_key] = suggestions
        self._subcommand_suggestions_last_update = current_time
        
        return suggestions

    def get_model_suggestions(self, current_word: str) -> List[Completion]:
        """Get model suggestions for the /model command.

        Args:
            current_word: The current word being typed

        Returns:
            A list of completions for models
        """
        suggestions = []

        # First try to complete model numbers
        for num, model_name in self._cached_model_numbers.items():
            if num.startswith(current_word):
                suggestions.append(Completion(
                    num,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansiwhite><b>{num:<3}</b></ansiwhite> "
                        f"{model_name}"),
                    style="fg:ansiwhite bold"
                ))

        # Then try to complete model names
        for model in self._cached_models:
            model_name = model[0] if isinstance(model, tuple) else model            
            if model_name.startswith(current_word):
                suggestions.append(Completion(
                    model_name,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansimagenta><b>{model_name}</b></ansimagenta>"),
                    style="fg:ansimagenta bold"
                ))
            elif (current_word.lower() in model_name.lower() and
                  not model_name.startswith(current_word)):
                suggestions.append(Completion(
                    model_name,
                    start_position=-len(current_word),
                    display=HTML(f"<ansimagenta>{model_name}</ansimagenta>"),
                    style="fg:ansimagenta"
                ))

        return suggestions

    def get_docker_suggestions(self, current_word: str) -> List[Completion]:
        """Get Docker image and container suggestions for virtualization.

        Args:
            current_word: The current word being typed

        Returns:
            A list of completions for Docker images and containers
        """
        suggestions = []
        
        # Default suggestions
        default_images = [
            ("cai-container", "Recommended environment used for usage", "sec1"),
            ("kalilinux/kali-rolling", "Kali Linux with security tools", "pen1")
        ]
        
        # Add more images with IDs
        try:
            # Attempt to import from virtualization command to get all images
            from cai.repl.commands.virtualization import DEFAULT_IMAGES
            default_images = []
            for name, info in DEFAULT_IMAGES.items():
                image_id = info.get("id", "")
                desc = info.get("description", "")
                default_images.append((name, desc, image_id))
        except ImportError:
            # Continue with the basic list if import fails
            pass

        # Try to get actually available Docker containers
        try:
            # Check for running containers using our default images
            running_containers = []
            
            # Check if Docker is available
            result = subprocess.run(
                ["docker", "ps", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Process the output to find containers with our default images
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container = json.loads(line)
                            image = container.get("Image", "")
                            container_id = container.get("ID", "")[:12]
                            
                            # Check if this is one of our default images
                            for name, _, _ in default_images:
                                if image == name:
                                    running_containers.append((container_id, image))
                                    break
                        except json.JSONDecodeError:
                            pass
            
            # Add running containers to suggestions
            for container_id, image in running_containers:
                if (container_id.startswith(current_word) or 
                        image.startswith(current_word)):
                    suggestions.append(Completion(
                        container_id,
                        start_position=-len(current_word),
                        display=HTML(
                            f"<ansigreen><b>{container_id}</b></ansigreen> "
                            f"(running {image})"),
                        style="fg:ansigreen bold"
                    ))
        except Exception:  # pylint: disable=broad-except
            # Silently fail if we can't get Docker info
            pass
        
        # Add ID suggestions
        for _, _, image_id in default_images:
            if image_id and image_id.startswith(current_word):
                # Find the corresponding image name and description
                image_name = ""
                description = ""
                for name, desc, id_check in default_images:
                    if id_check == image_id:
                        image_name = name
                        description = desc
                        break
                    
                suggestions.append(Completion(
                    image_id,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansiyellow><b>{image_id}</b></ansiyellow> "
                        f"({image_name}: {description})"),
                    style="fg:ansiyellow bold"
                ))
        
        # Add default image suggestions
        for image, description, _ in default_images:
            if image.startswith(current_word):
                suggestions.append(Completion(
                    image,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansiblue><b>{image:<25}</b></ansiblue> "
                        f"{description}"),
                    style="fg:ansiblue bold"
                ))
            elif current_word in image and not image.startswith(current_word):
                suggestions.append(Completion(
                    image,
                    start_position=-len(current_word),
                    display=HTML(
                        f"<ansiblue>{image:<25}</ansiblue> "
                        f"{description}"),
                    style="fg:ansiblue"
                ))
                
        return suggestions

    # pylint: disable=unused-argument
    def get_completions(self, document, complete_event):
        """Get completions for the current document
        with fuzzy matching support.

        Args:
            document: The document to complete
            complete_event: The completion event

        Returns:
            A generator of completions
        """
        text = document.text_before_cursor.strip()
        words = text.split()

        # Refresh Ollama models periodically
        self.fetch_ollama_models()

        if not text:
            # Show all main commands with descriptions
            command_descriptions = self.get_command_descriptions()

            # Sort commands by usage frequency (for command shadowing)
            sorted_commands = sorted(
                command_descriptions.items(),
                key=lambda x: self.command_history.get(x[0], 0),
                reverse=True
            )

            for cmd, description in sorted_commands:
                yield Completion(
                    cmd,
                    start_position=0,
                    display=HTML(
                        f"<ansicyan><b>{cmd:<15}</b></ansicyan> "
                        f"{description}"),
                    style="fg:ansicyan bold"
                )
            return

        if text.startswith('/'):
            current_word = words[-1]

            # Main command completion (first word)
            if len(words) == 1:
                # Get command suggestions
                yield from self.get_command_suggestions(current_word)

            # Subcommand completion (second word)
            elif len(words) == 2:
                cmd = words[0]

                # Special handling for model command
                if cmd in ["/model", "/mod"]:
                    yield from self.get_model_suggestions(current_word)
                # Special handling for virtualization command
                elif cmd in ["/virtualization", "/virt"]:
                    yield from self.get_docker_suggestions(current_word)
                else:
                    # Get subcommand suggestions
                    yield from self.get_subcommand_suggestions(
                        cmd, current_word)
