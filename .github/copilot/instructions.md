# GitHub Copilot Repository Instructions

## Repository information

- **Project**: Cybersecurity AI (CAI)
- **Purpose**: A lightweight, ergonomic framework for building bug bounty-ready Cybersecurity AIs

## Project Architecture

CAI focuses on cybersecurity agent coordination and execution, built upon 7 pillars:

- **Agents**: AI components that interact with environments through sensors/actuators
- **Tools**: Functions that enable agents to perform security tasks (reconnaissance, exploitation, etc.)
- **Handoffs**: Mechanisms for agents to delegate tasks to other specialized agents
- **Patterns**: Structured design paradigms for agent interaction (Swarm, Hierarchical, Chain-of-Thought, etc.)
- **Turns**: Conversational flow control mechanisms
- **Tracing**: Detailed logging and observability
- **HITL**: Human-in-the-loop mechanisms

## Coding Standards

1. **Python Styling**:
   - Follow PEP 8 guidelines
   - Use pylint for code quality (see existing pylint directives)
   - Keep functions focused and maintainable

2. **Security Considerations**:
   - All exploitation tools must include appropriate warnings and documentation
   - API keys should never be hardcoded
   - Follow responsible disclosure practices in tool implementations

3. **Documentation**:
   - New tools should have clear docstrings
   - Complex functions need detailed parameter documentation
   - Examples should be provided where helpful

4. **Type Hints**:
   - Use type hints for all new functions
   - Include proper return type annotations

5. **Error Handling**:
   - Implement appropriate error handling, especially for external API calls
   - Provide clear error messages

## File Organization

- `cai/agents/`: Agent implementations
- `cai/tools/`: Tool implementations organized by security kill chain categories
- `cai/prompts/`: System prompts for different agent types
- `examples/`: Example scripts demonstrating usage
- `tests/`: Test infrastructure

## Recent Features

- Bug bounty platform integration (HackerOne and Bugcrowd APIs)
- Extended tools for web security testing
- Support for multiple LLM providers via LiteLLM

## Dependencies and APIs

- LiteLLM for model access
- Phoenix for tracing and logging
- Support for OpenAI, Anthropic, DeepSeek, and Ollama models

## Ethical Guidelines

This project emphasizes ethical use of AI for security:

- Only test systems where you have explicit permission
- Follow responsible disclosure practices
- Document findings professionally
- Focus on security improvement, not exploitation
